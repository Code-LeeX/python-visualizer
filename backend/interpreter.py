"""
自定义Python解释器 - 执行AST并生成可视化数据
"""
import ast
import copy
import time
from typing import Dict, List, Any, Optional, Union
from ast_parser import ExecutionHook

class PythonObject:
    """自定义对象类，用于表示Python对象"""
    def __init__(self, class_name: str, attributes: Dict = None):
        self.class_name = class_name
        self.attributes = attributes or {}

class ExecutionError(Exception):
    """执行时错误"""
    pass

class PythonInterpreter:
    """自定义Python解释器"""

    def __init__(self, execution_hook: ExecutionHook, execution_delay: float = 0.3):
        self.hook = execution_hook
        self.execution_delay = execution_delay  # 执行延迟（秒）
        self.execution_manager = None  # 将被设置为ExecutionManager的引用
        self.global_scope = {
            # 内置函数
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'range': range,
            'print': self._builtin_print,
            'abs': abs,
            'max': max,
            'min': min,
        }
        self.local_scopes = []  # 函数调用栈的局部作用域
        self.return_value = None
        self.break_flag = False
        self.continue_flag = False
        self.output_buffer = []
        self.step_mode = False  # 单步模式标志
        self.should_stop = False  # 停止执行标志

    def _builtin_print(self, *args, **kwargs):
        """自定义print函数"""
        output = ' '.join(str(arg) for arg in args)
        self.output_buffer.append(output)
        return output

    def get_current_scope(self) -> Dict:
        """获取当前作用域"""
        if self.local_scopes:
            return self.local_scopes[-1]
        return self.global_scope

    def set_variable(self, name: str, value: Any):
        """设置变量"""
        scope = self.get_current_scope()
        scope[name] = value

    def get_variable(self, name: str) -> Any:
        """获取变量"""
        # 首先检查局部作用域
        for scope in reversed(self.local_scopes):
            if name in scope:
                return scope[name]

        # 然后检查全局作用域
        if name in self.global_scope:
            return self.global_scope[name]

        raise NameError(f"name '{name}' is not defined")

    def execute(self, node: ast.AST) -> Any:
        """执行AST节点"""
        # 检查是否应该停止执行
        if self.should_stop:
            print("Execution stopped by flag")
            raise ExecutionError("Execution stopped")

        # 对所有节点都检查暂停状态，确保暂停功能及时响应
        self._check_pause_state()

        method_name = f'execute_{type(node).__name__}'
        method = getattr(self, method_name, self.execute_generic)

        # 只在重要的节点记录执行步骤和添加延迟
        should_track = hasattr(node, 'lineno') and type(node).__name__ in [
            'Assign', 'AnnAssign', 'If', 'For', 'While', 'FunctionDef', 'ClassDef',
            'Return', 'Expr', 'Call'
        ]

        if should_track:
            # 再次检查停止标志（在延迟前）
            if self.should_stop:
                raise ExecutionError("Execution stopped")

            self.hook.current_line = node.lineno
            self.hook.record_step(
                type(node).__name__,
                node.lineno,
                f"Executing line {node.lineno}: {type(node).__name__}",
                self.get_all_variables(),
                self.hook.call_stack
            )

            # 添加延迟以便用户看到可视化效果（分成小段，便于中断和暂停）
            if self.execution_delay > 0:
                print(f"Applying execution delay: {self.execution_delay:.2f}s at line {node.lineno}")
                self._sleep_with_pause_check(self.execution_delay)

        return method(node)

    def _check_pause_state(self):
        """检查暂停状态，如果暂停则等待恢复"""
        if self.execution_manager and self.execution_manager.is_paused:
            print("Execution paused - waiting for resume...")
            print(f"Manager state: is_paused={self.execution_manager.is_paused}, is_running={self.execution_manager.is_running}")

            while self.execution_manager.is_paused:
                # 在等待时检查是否被停止
                if self.should_stop:
                    print("Execution stopped while paused")
                    raise ExecutionError("Execution stopped while paused")
                time.sleep(0.1)  # 短暂等待，避免忙等待

            print("Execution resumed from pause")
            print(f"Manager state after resume: is_paused={self.execution_manager.is_paused}, is_running={self.execution_manager.is_running}")

    def _sleep_with_pause_check(self, delay_seconds):
        """带暂停检查的延迟函数"""
        # 将延迟分解为小段，每段检查暂停和停止状态
        delay_segments = int(delay_seconds * 10)  # 100ms 段
        for i in range(delay_segments):
            if self.should_stop:
                raise ExecutionError("Execution stopped during delay")

            # 检查暂停状态
            self._check_pause_state()

            time.sleep(0.1)

        # 处理剩余的小数部分
        remaining = delay_seconds - (delay_segments * 0.1)
        if remaining > 0:
            if self.should_stop:
                raise ExecutionError("Execution stopped")
            self._check_pause_state()
            time.sleep(remaining)

    def execute_generic(self, node: ast.AST) -> Any:
        """通用执行方法"""
        raise NotImplementedError(f"Execution of {type(node).__name__} not implemented")

    def execute_Module(self, node: ast.Module) -> Any:
        """执行模块"""
        result = None
        for stmt in node.body:
            result = self.execute(stmt)
            if self.return_value is not None:
                break
        return result

    def execute_FunctionDef(self, node: ast.FunctionDef) -> None:
        """执行函数定义"""
        def user_function(*args, **kwargs):
            # 创建新的局部作用域
            local_scope = {}

            # 绑定参数
            for i, arg in enumerate(node.args.args):
                if i < len(args):
                    local_scope[arg.arg] = args[i]

            for key, value in kwargs.items():
                local_scope[key] = value

            # 进入函数作用域
            self.local_scopes.append(local_scope)
            self.hook.call_stack.append(f"{node.name}()")

            try:
                # 执行函数体
                result = None
                for stmt in node.body:
                    result = self.execute(stmt)
                    if self.return_value is not None:
                        result = self.return_value
                        self.return_value = None
                        break

                return result
            finally:
                # 退出函数作用域
                self.local_scopes.pop()
                self.hook.call_stack.pop()

        # 将函数添加到当前作用域
        self.set_variable(node.name, user_function)

    def execute_ClassDef(self, node: ast.ClassDef) -> None:
        """执行类定义"""
        class_dict = {}

        # 创建类的命名空间
        old_scopes = self.local_scopes[:]
        self.local_scopes = [class_dict]

        try:
            # 执行类体
            for stmt in node.body:
                self.execute(stmt)
        finally:
            self.local_scopes = old_scopes

        # 创建类对象
        def class_constructor(*args, **kwargs):
            obj = PythonObject(node.name)
            # 如果有__init__方法，调用它
            if '__init__' in class_dict:
                class_dict['__init__'](obj, *args, **kwargs)
            return obj

        self.set_variable(node.name, class_constructor)

    def execute_Assign(self, node: ast.Assign) -> None:
        """执行赋值语句"""
        # 检测动画操作（在执行赋值前）
        animation_data = self._detect_assignment_animation(node)

        value = self.execute(node.value)

        for target in node.targets:
            if isinstance(target, ast.Name):
                self.set_variable(target.id, value)
            elif isinstance(target, ast.Subscript):
                obj = self.execute(target.value)
                key = self.execute(target.slice)
                obj[key] = value
            elif isinstance(target, ast.Attribute):
                obj = self.execute(target.value)
                setattr(obj, target.attr, value)

        # 如果检测到动画操作，记录动画信息
        if animation_data:
            animation_data['completed'] = True
            self.hook.record_animation_step(animation_data)

    def execute_AnnAssign(self, node: ast.AnnAssign) -> None:
        """执行带注解的赋值"""
        if node.value:
            value = self.execute(node.value)
            if isinstance(node.target, ast.Name):
                self.set_variable(node.target.id, value)

    def execute_Return(self, node: ast.Return) -> None:
        """执行return语句"""
        if node.value:
            self.return_value = self.execute(node.value)
        else:
            self.return_value = None

    def execute_If(self, node: ast.If) -> Any:
        """执行if语句"""
        condition = self.execute(node.test)

        if condition:
            for stmt in node.body:
                self.execute(stmt)
        else:
            for stmt in node.orelse:
                self.execute(stmt)

    def execute_While(self, node: ast.While) -> Any:
        """执行while循环"""
        while True:
            condition = self.execute(node.test)
            if not condition:
                break

            for stmt in node.body:
                self.execute(stmt)
                if self.break_flag:
                    self.break_flag = False
                    return
                if self.continue_flag:
                    self.continue_flag = False
                    break
                if self.return_value is not None:
                    return

    def execute_For(self, node: ast.For) -> Any:
        """执行for循环"""
        iterable = self.execute(node.iter)

        for item in iterable:
            if isinstance(node.target, ast.Name):
                self.set_variable(node.target.id, item)

            for stmt in node.body:
                self.execute(stmt)
                if self.break_flag:
                    self.break_flag = False
                    return
                if self.continue_flag:
                    self.continue_flag = False
                    break
                if self.return_value is not None:
                    return

    def execute_Break(self, node: ast.Break) -> None:
        """执行break语句"""
        self.break_flag = True

    def execute_Continue(self, node: ast.Continue) -> None:
        """执行continue语句"""
        self.continue_flag = True

    def execute_Expr(self, node: ast.Expr) -> Any:
        """执行表达式语句"""
        return self.execute(node.value)

    def execute_Name(self, node: ast.Name) -> Any:
        """执行名称节点"""
        return self.get_variable(node.id)

    def execute_Constant(self, node: ast.Constant) -> Any:
        """执行常量节点"""
        return node.value

    def execute_Num(self, node: ast.Num) -> Union[int, float]:
        """执行数字节点（Python < 3.8 兼容性）"""
        return node.n

    def execute_Str(self, node: ast.Str) -> str:
        """执行字符串节点（Python < 3.8 兼容性）"""
        return node.s

    def execute_JoinedStr(self, node: ast.JoinedStr) -> str:
        """执行f-string节点"""
        result = ""
        for value in node.values:
            if isinstance(value, ast.Constant):
                result += str(value.value)
            elif isinstance(value, ast.Str):
                result += value.s
            elif isinstance(value, ast.FormattedValue):
                # 执行表达式并格式化
                expr_result = self.execute(value.value)
                if value.format_spec:
                    # 简化处理，忽略复杂的格式化规范
                    result += str(expr_result)
                else:
                    result += str(expr_result)
            else:
                result += str(self.execute(value))
        return result

    def execute_FormattedValue(self, node: ast.FormattedValue) -> str:
        """执行格式化值节点"""
        return str(self.execute(node.value))

    def execute_List(self, node: ast.List) -> List:
        """执行列表节点"""
        return [self.execute(elt) for elt in node.elts]

    def execute_Dict(self, node: ast.Dict) -> Dict:
        """执行字典节点"""
        result = {}
        for key, value in zip(node.keys, node.values):
            result[self.execute(key)] = self.execute(value)
        return result

    def execute_Subscript(self, node: ast.Subscript) -> Any:
        """执行下标访问"""
        obj = self.execute(node.value)
        key = self.execute(node.slice)
        return obj[key]

    def execute_Attribute(self, node: ast.Attribute) -> Any:
        """执行属性访问"""
        obj = self.execute(node.value)
        return getattr(obj, node.attr)

    def execute_Call(self, node: ast.Call) -> Any:
        """执行函数调用"""
        # 检测动画操作（在执行前）
        animation_data = self._detect_animation_operation(node)

        func = self.execute(node.func)
        args = [self.execute(arg) for arg in node.args]
        kwargs = {kw.arg: self.execute(kw.value) for kw in node.keywords}

        result = func(*args, **kwargs)

        # 如果检测到动画操作，记录动画信息
        if animation_data:
            animation_data['completed'] = True
            self.hook.record_animation_step(animation_data)

        return result

    def execute_BinOp(self, node: ast.BinOp) -> Any:
        """执行二元运算"""
        left = self.execute(node.left)
        right = self.execute(node.right)

        op_map = {
            ast.Add: lambda x, y: x + y,
            ast.Sub: lambda x, y: x - y,
            ast.Mult: lambda x, y: x * y,
            ast.Div: lambda x, y: x / y,
            ast.FloorDiv: lambda x, y: x // y,
            ast.Mod: lambda x, y: x % y,
            ast.Pow: lambda x, y: x ** y,
        }

        op_func = op_map.get(type(node.op))
        if op_func:
            return op_func(left, right)

        raise NotImplementedError(f"Binary operator {type(node.op).__name__} not implemented")

    def execute_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """执行一元运算"""
        operand = self.execute(node.operand)

        op_map = {
            ast.UAdd: lambda x: +x,
            ast.USub: lambda x: -x,
            ast.Not: lambda x: not x,
        }

        op_func = op_map.get(type(node.op))
        if op_func:
            return op_func(operand)

        raise NotImplementedError(f"Unary operator {type(node.op).__name__} not implemented")

    def execute_Compare(self, node: ast.Compare) -> bool:
        """执行比较运算"""
        left = self.execute(node.left)

        op_map = {
            ast.Eq: lambda x, y: x == y,
            ast.NotEq: lambda x, y: x != y,
            ast.Lt: lambda x, y: x < y,
            ast.LtE: lambda x, y: x <= y,
            ast.Gt: lambda x, y: x > y,
            ast.GtE: lambda x, y: x >= y,
            ast.Is: lambda x, y: x is y,
            ast.IsNot: lambda x, y: x is not y,
            ast.In: lambda x, y: x in y,
            ast.NotIn: lambda x, y: x not in y,
        }

        for op, right_node in zip(node.ops, node.comparators):
            right = self.execute(right_node)
            op_func = op_map.get(type(op))
            if not op_func:
                raise NotImplementedError(f"Comparison operator {type(op).__name__} not implemented")

            if not op_func(left, right):
                return False
            left = right  # Chain comparisons

        return True

    def execute_BoolOp(self, node: ast.BoolOp) -> bool:
        """执行布尔运算"""
        if isinstance(node.op, ast.And):
            for value in node.values:
                if not self.execute(value):
                    return False
            return True
        elif isinstance(node.op, ast.Or):
            for value in node.values:
                if self.execute(value):
                    return True
            return False

    def get_all_variables(self) -> Dict[str, Any]:
        """获取所有变量（用于可视化）"""
        variables = {
            'global': {},
            'local': {}
        }

        # 添加全局变量
        for name, value in self.global_scope.items():
            if not name.startswith('__') and not callable(value):
                variables['global'][name] = self._serialize_value(value)

        # 添加当前局部变量（最新的作用域）
        if self.local_scopes:
            current_scope = self.local_scopes[-1]
            for name, value in current_scope.items():
                if not name.startswith('__') and not callable(value):
                    variables['local'][name] = self._serialize_value(value)

        return variables

    def _serialize_value(self, value: Any) -> Dict[str, Any]:
        """序列化值用于JSON传输"""
        if isinstance(value, (int, float, str, bool)) or value is None:
            return {
                'type': type(value).__name__ if value is not None else 'NoneType',
                'value': value,
                'display': str(value)
            }
        elif isinstance(value, list):
            return {
                'type': 'list',
                'value': [self._serialize_value(item)['value'] for item in value[:10]],  # 限制长度
                'display': f"[{', '.join(str(item) for item in value[:3])}{'...' if len(value) > 3 else ''}]",
                'length': len(value)
            }
        elif isinstance(value, dict):
            return {
                'type': 'dict',
                'value': {str(k): self._serialize_value(v)['value'] for k, v in list(value.items())[:5]},
                'display': f"{{{', '.join(f'{k}: {v}' for k, v in list(value.items())[:2])}{('...' if len(value) > 2 else '')}}}",
                'length': len(value)
            }
        elif isinstance(value, PythonObject):
            return {
                'type': value.class_name,
                'value': value.attributes,
                'display': f"<{value.class_name} object>"
            }
        else:
            return {
                'type': type(value).__name__,
                'value': None,
                'display': str(value)
            }

    def _detect_assignment_animation(self, node: ast.Assign) -> Optional[Dict[str, Any]]:
        """检测赋值操作中的动画，如 dict[key] = variable"""
        try:
            # 检查是否是从变量赋值
            if isinstance(node.value, ast.Name):
                source_var = node.value.id
                try:
                    source_value = self.get_variable(source_var)
                except NameError:
                    return None

                # 检查目标是否是下标赋值 (obj[key] = var)
                for target in node.targets:
                    if isinstance(target, ast.Subscript):
                        target_obj = self._get_variable_name_from_node(target.value)
                        if target_obj:
                            return {
                                'type': 'value_transfer',
                                'operation': 'assignment',
                                'source_variable': source_var,
                                'source_value': source_value,
                                'target_variable': target_obj,
                                'line': node.lineno,
                                'animation_type': 'assignment_operation'
                            }

            return None
        except Exception as e:
            print(f"Assignment animation detection error: {e}")
            return None

    def _detect_animation_operation(self, node: ast.Call) -> Optional[Dict[str, Any]]:
        """检测动画操作，如 list.append(variable), dict[key] = variable 等"""
        try:
            # 检测方法调用，如 list.append(var)
            if isinstance(node.func, ast.Attribute):
                attr_name = node.func.attr

                # 检测 list/array 操作
                if attr_name in ['append', 'insert', 'extend'] and len(node.args) > 0:
                    # 获取目标对象名（如 list_name）
                    target_obj = self._get_variable_name_from_node(node.func.value)
                    if target_obj:
                        # 获取源变量名（传入的参数）
                        source_var = None
                        source_value = None

                        for arg in node.args:
                            if isinstance(arg, ast.Name):
                                source_var = arg.id
                                try:
                                    source_value = self.get_variable(arg.id)
                                except NameError:
                                    continue
                                break
                            elif isinstance(arg, ast.Constant):
                                source_value = arg.value
                                break

                        if source_var or source_value is not None:
                            return {
                                'type': 'value_transfer',
                                'operation': attr_name,
                                'source_variable': source_var,
                                'source_value': source_value,
                                'target_variable': target_obj,
                                'line': node.lineno,
                                'animation_type': 'list_operation'
                            }

                # 检测字典操作等其他方法调用
                elif attr_name in ['update', 'setdefault']:
                    target_obj = self._get_variable_name_from_node(node.func.value)
                    if target_obj and len(node.args) > 0:
                        return {
                            'type': 'value_transfer',
                            'operation': attr_name,
                            'target_variable': target_obj,
                            'line': node.lineno,
                            'animation_type': 'dict_operation'
                        }

            return None
        except Exception as e:
            # 如果检测失败，不影响正常执行
            print(f"Animation detection error: {e}")
            return None

    def _get_variable_name_from_node(self, node: ast.AST) -> Optional[str]:
        """从AST节点中提取变量名"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # 对于类似 obj.attr 的情况，返回 obj
            base_name = self._get_variable_name_from_node(node.value)
            if base_name:
                return f"{base_name}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            # 对于类似 obj[key] 的情况，返回 obj
            return self._get_variable_name_from_node(node.value)

        return None
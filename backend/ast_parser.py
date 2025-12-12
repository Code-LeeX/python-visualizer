"""
AST解析器 - 将Python代码解析为抽象语法树并提供执行钩子
"""
import ast
from typing import Dict, List, Any, Optional
import json

class ExecutionHook:
    """执行钩子类，用于在AST节点执行时记录状态"""

    def __init__(self):
        self.steps = []
        self.current_line = 1
        self.variables = {}
        self.call_stack = []
        self.step_count = 0
        self.emit_callback = None  # 用于实时发送步骤的回调函数
        self.sent_animations = set()  # 用于追踪已发送的动画，防止重复
        self.loop_contexts = []  # 循环上下文栈，用于追踪嵌套循环
        self.iteration_stack = []  # 遍历状态栈，支持嵌套循环 [{container: str, index: int, iterator_var: str}]

    def record_step(self, node_type: str, line_number: int, description: str,
                   variables: Dict = None, call_stack: List = None):
        """记录执行步骤"""
        step = {
            'step': self.step_count,
            'line': line_number,
            'node_type': node_type,
            'description': description,
            'variables': dict(variables) if variables else dict(self.variables),
            'call_stack': list(call_stack) if call_stack else list(self.call_stack),
            'timestamp': self.step_count  # 简化的时间戳
        }
        self.steps.append(step)
        self.step_count += 1

        # 如果设置了回调函数，实时发送步骤
        if self.emit_callback:
            self.emit_callback(step)

        return step

    def record_animation_step(self, animation_data: dict):
        """记录动画步骤"""
        # 创建动画的唯一标识符，防止重复发送相同的动画
        # 包含步骤计数确保即使是相同的操作在不同时刻也被认为是不同的
        animation_key = (
            animation_data.get('line'),
            animation_data.get('operation'),
            animation_data.get('source_variable'),
            animation_data.get('target_variable'),
            str(animation_data.get('source_value')),
            animation_data.get('step_count', self.step_count)  # 添加步骤计数确保唯一性
        )

        print(f"🎬 [Debug] Animation key: {animation_key}")
        print(f"🎬 [Debug] Sent animations count: {len(self.sent_animations)}")

        # 检查是否已经发送过相同的动画
        if animation_key in self.sent_animations:
            print(f"🎬 [Animation] Skipping duplicate animation: {animation_data.get('operation')} (key exists)")
            return

        # 记录已发送的动画
        self.sent_animations.add(animation_key)
        print(f"🎬 [Animation] Added to sent_animations, new count: {len(self.sent_animations)}")

        # 将动画数据添加到当前步骤中
        if self.steps:
            # 添加到最近的步骤
            self.steps[-1]['animation'] = animation_data
            print(f"🎬 [Animation] Recorded animation for {animation_data.get('operation')}: {animation_data.get('source_variable')} -> {animation_data.get('target_variable')}")

            # 如果设置了回调函数，实时发送动画步骤
            if self.emit_callback:
                # 创建专门的动画事件
                animation_event = {
                    'step': self.step_count,
                    'line': animation_data.get('line'),
                    'node_type': 'Animation',
                    'description': f"Animation: {animation_data.get('operation')}",
                    'variables': dict(self.variables),
                    'call_stack': list(self.call_stack),
                    'animation': animation_data,
                    'timestamp': self.step_count
                }
                self.emit_callback(animation_event)

    def push_iteration_context(self, container_name: str, iterator_var: str, line: int, pattern: str = 'simple'):
        """开始新的循环上下文"""
        context = {
            'container': container_name,
            'iterator_var': iterator_var,
            'line': line,
            'current_index': -1,  # 还没开始遍历
            'level': len(self.iteration_stack),  # 嵌套级别
            'pattern': pattern,  # 'simple' 或 'dual_pointer'
            'multi_indices': {}  # 用于存储多个索引访问 {container_name: [indices]}
        }
        self.iteration_stack.append(context)
        print(f"🔄 [Loop Start] Pushed loop context: {iterator_var} in {container_name} (level {context['level']}, pattern: {pattern})")

    def update_iteration_index(self, iterator_var: str, current_index: int):
        """更新当前循环的索引"""
        # 找到匹配的循环上下文并更新索引
        for context in reversed(self.iteration_stack):
            if context['iterator_var'] == iterator_var:
                context['current_index'] = current_index
                print(f"🔄 [Iteration] Updated {iterator_var}[{current_index}] in {context['container']} (level {context['level']})")

                # 发送更新的遍历状态
                if self.emit_callback:
                    iteration_event = {
                        'step': self.step_count,
                        'line': self.current_line,
                        'node_type': 'Iteration',
                        'description': f"Iterating {iterator_var} in {context['container']}[{current_index}]",
                        'variables': {},  # 将在interpreter中填充
                        'call_stack': list(self.call_stack),
                        'iteration_stack': [ctx.copy() for ctx in self.iteration_stack],  # 发送整个栈
                        'timestamp': self.step_count
                    }
                    self.emit_callback(iteration_event)
                break

    def record_multi_index_access(self, container_name: str, indices: List[int], index_vars: List[str]):
        """记录同一容器的多个索引访问（双指针模式）"""
        if not self.iteration_stack:
            return

        # 找到当前最顶层的上下文并记录多索引访问
        current_context = self.iteration_stack[-1]
        current_context['multi_indices'][container_name] = {
            'indices': indices.copy(),
            'index_vars': index_vars.copy(),
            'type': 'multi_index'
        }

        print(f"🔄 [Multi-Index] Recording {container_name} indices: {dict(zip(index_vars, indices))}")

        # 发送多索引访问事件
        if self.emit_callback:
            multi_index_event = {
                'step': self.step_count,
                'line': self.current_line,
                'node_type': 'MultiIndex',
                'description': f"Multi-index access: {container_name}{indices}",
                'variables': {},  # 将在interpreter中填充
                'call_stack': list(self.call_stack),
                'iteration_stack': [ctx.copy() for ctx in self.iteration_stack],
                'timestamp': self.step_count
            }
            self.emit_callback(multi_index_event)

    def record_slice_access(self, container_name: str, start_idx: int, end_idx: int, start_var: str, end_var: str):
        """记录切片范围访问（slice模式）"""
        if not self.iteration_stack:
            return

        # 找到当前最顶层的上下文并记录切片访问
        current_context = self.iteration_stack[-1]
        current_context['multi_indices'][container_name] = {
            'start_index': start_idx,
            'end_index': end_idx,
            'start_var': start_var,
            'end_var': end_var,
            'type': 'slice_range'
        }

        print(f"🔄 [Slice] Recording {container_name}[{start_idx}:{end_idx}] range: {start_var}={start_idx}, {end_var}={end_idx}")

        # 发送切片访问事件
        if self.emit_callback:
            slice_event = {
                'step': self.step_count,
                'line': self.current_line,
                'node_type': 'SliceRange',
                'description': f"Slice range access: {container_name}[{start_idx}:{end_idx}]",
                'variables': {},  # 将在interpreter中填充
                'call_stack': list(self.call_stack),
                'iteration_stack': [ctx.copy() for ctx in self.iteration_stack],
                'timestamp': self.step_count
            }
            self.emit_callback(slice_event)

    def pop_iteration_context(self, iterator_var: str):
        """结束循环上下文"""
        # 从栈顶开始查找匹配的上下文
        for i in range(len(self.iteration_stack) - 1, -1, -1):
            if self.iteration_stack[i]['iterator_var'] == iterator_var:
                removed_context = self.iteration_stack.pop(i)
                print(f"🔄 [Loop End] Popped loop context: {iterator_var} (level {removed_context['level']})")

                # 发送循环结束事件
                if self.emit_callback:
                    end_event = {
                        'step': self.step_count,
                        'line': self.current_line,
                        'node_type': 'IterationEnd',
                        'description': f"Loop ended: {iterator_var}",
                        'variables': {},
                        'call_stack': list(self.call_stack),
                        'iteration_stack': [ctx.copy() for ctx in self.iteration_stack],  # 发送剩余的栈
                        'timestamp': self.step_count
                    }
                    self.emit_callback(end_event)
                break

    def get_iteration_stack(self):
        """获取当前迭代栈的副本"""
        return [ctx.copy() for ctx in self.iteration_stack]

    def clear_all_iteration_contexts(self):
        """清除所有循环上下文（用于重置）"""
        self.iteration_stack.clear()
        print("🔄 [Reset] Cleared all iteration contexts")

class IndexAccessAnalyzer(ast.NodeVisitor):
    """分析循环体内的索引访问模式"""

    def __init__(self, index_var_name: str):
        self.index_var_name = index_var_name
        self.container_accesses = []  # 存储 container[index] 的访问

    def visit_Subscript(self, node):
        """检测 container[index] 和 container[start:end] 访问模式"""
        container_name = None
        if isinstance(node.value, ast.Name):
            container_name = node.value.id

        # 1. 检查单个索引访问：container[index]
        if (isinstance(node.slice, ast.Name) and
            node.slice.id == self.index_var_name and
            container_name):

            self.container_accesses.append({
                'container': container_name,
                'line': node.lineno,
                'access_type': 'single_index'
            })
            print(f"🔍 [IndexAccess] Found {container_name}[{self.index_var_name}] at line {node.lineno}")

        # 2. 检查切片访问：container[start:end]
        elif (isinstance(node.slice, ast.Slice) and container_name):
            slice_vars = []

            # 检查切片的起始位置
            if isinstance(node.slice.lower, ast.Name):
                slice_vars.append(node.slice.lower.id)

            # 检查切片的结束位置
            if isinstance(node.slice.upper, ast.Name):
                slice_vars.append(node.slice.upper.id)

            # 如果切片使用了我们关注的索引变量
            if self.index_var_name in slice_vars:
                self.container_accesses.append({
                    'container': container_name,
                    'line': node.lineno,
                    'access_type': 'slice',
                    'slice_vars': slice_vars
                })
                print(f"🔍 [SliceAccess] Found {container_name}[{':'.join(slice_vars)}] at line {node.lineno}")

        self.generic_visit(node)

class CodeAnalyzer(ast.NodeVisitor):
    """代码分析器 - 分析AST结构并提取信息"""

    def __init__(self):
        self.functions = {}
        self.classes = {}
        self.variables = set()
        self.line_map = {}  # 行号到节点的映射
        self.control_flow = []  # 控制流信息

    def visit_FunctionDef(self, node):
        """访问函数定义"""
        self.functions[node.name] = {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'line': node.lineno,
            'docstring': ast.get_docstring(node)
        }
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """访问类定义"""
        self.classes[node.name] = {
            'name': node.name,
            'line': node.lineno,
            'methods': [],
            'docstring': ast.get_docstring(node)
        }
        self.generic_visit(node)

    def visit_Assign(self, node):
        """访问赋值语句"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
        self.line_map[node.lineno] = node
        self.generic_visit(node)

    def visit_If(self, node):
        """访问if语句"""
        self.control_flow.append({
            'type': 'if',
            'line': node.lineno,
            'condition': ast.unparse(node.test) if hasattr(ast, 'unparse') else 'condition'
        })
        self.line_map[node.lineno] = node
        self.generic_visit(node)

    def visit_While(self, node):
        """访问while循环"""
        self.control_flow.append({
            'type': 'while',
            'line': node.lineno,
            'condition': ast.unparse(node.test) if hasattr(ast, 'unparse') else 'condition'
        })
        self.line_map[node.lineno] = node
        self.generic_visit(node)

    def visit_For(self, node):
        """访问for循环"""
        self.control_flow.append({
            'type': 'for',
            'line': node.lineno,
            'target': node.target.id if isinstance(node.target, ast.Name) else 'target',
            'iter': ast.unparse(node.iter) if hasattr(ast, 'unparse') else 'iterable'
        })
        self.line_map[node.lineno] = node
        self.generic_visit(node)

class ASTParser:
    """主要的AST解析器类"""

    def __init__(self):
        self.tree = None
        self.analyzer = None
        self.source_lines = []

    def parse(self, source_code: str) -> Dict[str, Any]:
        """解析Python源代码"""
        try:
            # 解析为AST
            self.tree = ast.parse(source_code)

            # 保存源代码行
            self.source_lines = source_code.splitlines()

            # 分析AST结构
            self.analyzer = CodeAnalyzer()
            self.analyzer.visit(self.tree)

            # 返回分析结果
            return {
                'success': True,
                'ast': self.tree,
                'functions': self.analyzer.functions,
                'classes': self.analyzer.classes,
                'variables': list(self.analyzer.variables),
                'control_flow': self.analyzer.control_flow,
                'line_count': len(self.source_lines),
                'source_lines': self.source_lines
            }

        except SyntaxError as e:
            return {
                'success': False,
                'error': 'SyntaxError',
                'message': str(e),
                'line': getattr(e, 'lineno', 0),
                'offset': getattr(e, 'offset', 0)
            }
        except Exception as e:
            return {
                'success': False,
                'error': type(e).__name__,
                'message': str(e)
            }

    def get_line_info(self, line_number: int) -> Optional[Dict]:
        """获取指定行的信息"""
        if not self.analyzer or line_number not in self.analyzer.line_map:
            return None

        node = self.analyzer.line_map[line_number]
        return {
            'line': line_number,
            'node_type': type(node).__name__,
            'content': self.source_lines[line_number - 1] if line_number <= len(self.source_lines) else ''
        }

    def get_ast_dump(self) -> str:
        """获取AST的文本表示"""
        if not self.tree:
            return ''
        return ast.dump(self.tree, indent=2)
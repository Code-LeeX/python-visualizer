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
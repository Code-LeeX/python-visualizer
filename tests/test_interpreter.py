"""
测试Python解释器功能
"""
import sys
import os

# 添加后端目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ast_parser import ASTParser, ExecutionHook
from interpreter import PythonInterpreter

def test_basic_operations():
    """测试基本操作"""
    print("Testing basic operations...")

    code = """
x = 5
y = 3
result = x + y
print(f"Result: {result}")
"""

    # 解析代码
    parser = ASTParser()
    parse_result = parser.parse(code)

    if not parse_result['success']:
        print(f"Parse error: {parse_result['message']}")
        return False

    # 执行代码
    hook = ExecutionHook()
    interpreter = PythonInterpreter(hook)

    try:
        interpreter.execute(parse_result['ast'])
        print("Basic operations test: PASSED")
        return True
    except Exception as e:
        print(f"Basic operations test: FAILED - {e}")
        return False

def test_conditional_logic():
    """测试条件逻辑"""
    print("Testing conditional logic...")

    code = """
age = 20
if age >= 18:
    status = "adult"
else:
    status = "minor"
print(f"Status: {status}")
"""

    parser = ASTParser()
    parse_result = parser.parse(code)

    if not parse_result['success']:
        print(f"Parse error: {parse_result['message']}")
        return False

    hook = ExecutionHook()
    interpreter = PythonInterpreter(hook)

    try:
        interpreter.execute(parse_result['ast'])

        # 检查变量值
        variables = interpreter.get_all_variables()
        status_var = None
        for name, value in variables.items():
            if 'status' in name:
                status_var = value
                break

        if status_var and status_var.get('value') == 'adult':
            print("Conditional logic test: PASSED")
            return True
        else:
            print(f"Conditional logic test: FAILED - Expected 'adult', got {status_var}")
            return False

    except Exception as e:
        print(f"Conditional logic test: FAILED - {e}")
        return False

def test_loops():
    """测试循环"""
    print("Testing loops...")

    code = """
numbers = []
for i in range(3):
    numbers.append(i)
print(f"Numbers: {numbers}")
"""

    parser = ASTParser()
    parse_result = parser.parse(code)

    if not parse_result['success']:
        print(f"Parse error: {parse_result['message']}")
        return False

    hook = ExecutionHook()
    interpreter = PythonInterpreter(hook)

    try:
        interpreter.execute(parse_result['ast'])

        # 检查变量值
        variables = interpreter.get_all_variables()
        numbers_var = None
        for name, value in variables.items():
            if 'numbers' in name:
                numbers_var = value
                break

        expected = [0, 1, 2]
        if numbers_var and numbers_var.get('value') == expected:
            print("Loops test: PASSED")
            return True
        else:
            print(f"Loops test: FAILED - Expected {expected}, got {numbers_var}")
            return False

    except Exception as e:
        print(f"Loops test: FAILED - {e}")
        return False

def test_functions():
    """测试函数"""
    print("Testing functions...")

    code = """
def add(x, y):
    return x + y

result = add(5, 3)
print(f"Function result: {result}")
"""

    parser = ASTParser()
    parse_result = parser.parse(code)

    if not parse_result['success']:
        print(f"Parse error: {parse_result['message']}")
        return False

    hook = ExecutionHook()
    interpreter = PythonInterpreter(hook)

    try:
        interpreter.execute(parse_result['ast'])

        # 检查变量值
        variables = interpreter.get_all_variables()
        result_var = None
        for name, value in variables.items():
            if 'result' in name:
                result_var = value
                break

        if result_var and result_var.get('value') == 8:
            print("Functions test: PASSED")
            return True
        else:
            print(f"Functions test: FAILED - Expected 8, got {result_var}")
            return False

    except Exception as e:
        print(f"Functions test: FAILED - {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("Running Python Visualizer Tests...\n")

    tests = [
        test_basic_operations,
        test_conditional_logic,
        test_loops,
        test_functions
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests PASSED! ✅")
        return True
    else:
        print("Some tests FAILED! ❌")
        return False

if __name__ == "__main__":
    run_all_tests()
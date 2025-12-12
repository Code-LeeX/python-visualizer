"""
Python代码示例 - 用于测试变量可视化效果
"""

examples = [
    {
        "id": "basic_variables",
        "title": "🔢 基础变量类型",
        "code": """# 基础变量类型演示
mystr = "hello"
for i in range(len(mystr)):
    for j in range(i+1, len(mystr)):
        c = mystr[i:j]
        print(c)
""",
        "inputs": ""
    },
    {
        "id": "list_operations",
        "title": "📋 列表操作",
        "code": """# 列表操作演示
numbers = [1, 2, 3]
print("初始列表:", numbers)

# 添加元素
numbers.append(4)
numbers.append(5)
numbers.extend([6, 7, 8, 9, 10])

# 创建更多列表
fruits = ["苹果", "香蕉", "橙子"]
colors = ["红色", "蓝色", "绿色", "黄色", "紫色"]
mixed = [1, "hello", True, 3.14]

print("数字列表:", numbers)
print("水果列表:", fruits)
print("颜色列表:", colors)
print("混合列表:", mixed)
""",
        "inputs": ""
    },
    {
        "id": "dict_operations",
        "title": "📖 字典操作",
        "code": """# 字典操作演示
person = {"name": "张三", "age": 25}
person["city"] = "北京"
person["job"] = "程序员"
person["salary"] = 15000

# 嵌套字典
company = {
    "name": "科技公司",
    "employees": 100,
    "address": {
        "city": "上海",
        "district": "浦东"
    }
}

# 字典列表
students = [
    {"name": "小明", "grade": 85},
    {"name": "小红", "grade": 92},
    {"name": "小刚", "grade": 78}
]

print("个人信息:", person)
print("公司信息:", company)
print("学生成绩:", students)
""",
        "inputs": ""
    },
    {
        "id": "loops_conditions",
        "title": "🔄 循环与条件",
        "code": """# 循环与条件演示
# for循环处理列表
scores = [85, 92, 78, 96, 67]
total = 0
count = 0

for score in scores:
    total += score
    count += 1
    if score >= 90:
        grade = "优秀"
    elif score >= 80:
        grade = "良好"
    else:
        grade = "及格"
    print(f"分数: {score}, 等级: {grade}")

average = total / count
print(f"平均分: {average:.2f}")

# while循环
countdown = 5
while countdown > 0:
    print(f"倒计时: {countdown}")
    countdown -= 1

print("发射!")
""",
        "inputs": ""
    },
    {
        "id": "functions",
        "title": "⚡ 函数定义与调用",
        "code": """# 函数演示
def calculate_area(length, width):
    area = length * width
    return area

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def process_list(data):
    result = []
    for item in data:
        processed = item * 2 + 1
        result.append(processed)
    return result

# 函数调用
room_area = calculate_area(5, 3)
fib_result = fibonacci(6)
numbers = [1, 2, 3, 4, 5]
processed_numbers = process_list(numbers)

print(f"房间面积: {room_area}")
print(f"斐波那契数列第6项: {fib_result}")
print(f"处理后的数字: {processed_numbers}")
""",
        "inputs": ""
    },
    {
        "id": "comprehensive",
        "title": "🌟 综合测试",
        "code": """# 综合功能测试
def analyze_data():
    # 学生数据
    students = [
        {"name": "张三", "scores": [85, 90, 78]},
        {"name": "李四", "scores": [92, 88, 95]},
        {"name": "王五", "scores": [76, 82, 79]}
    ]

    # 统计数据
    statistics = {}
    all_scores = []

    for student in students:
        name = student["name"]
        scores = student["scores"]
        average = sum(scores) / len(scores)

        statistics[name] = {
            "average": round(average, 2),
            "max": max(scores),
            "min": min(scores)
        }

        all_scores.extend(scores)

    # 全班统计
    class_stats = {
        "total_students": len(students),
        "class_average": round(sum(all_scores) / len(all_scores), 2),
        "highest_score": max(all_scores),
        "lowest_score": min(all_scores)
    }

    return students, statistics, class_stats

# 执行分析
student_data, individual_stats, class_statistics = analyze_data()

print("学生数据:", student_data)
print("个人统计:", individual_stats)
print("全班统计:", class_statistics)
""",
        "inputs": ""
    },
    {
        "id": "animation_test",
        "title": "🎬 动画效果测试",
        "code": """# 动画效果测试
# 创建初始变量
a = 3
b = "hello"
c = 42

# 创建容器
my_list = [1, 2]
my_dict = {"x": 10}

# 测试list.append动画 - 值从变量a飞到列表
my_list.append(a)

# 测试字典赋值动画 - 值从变量b飞到字典
my_dict["greeting"] = b

# 测试更多list操作
my_list.append(c)
my_list.extend([4, 5])

# 打印结果
print("列表内容:", my_list)
print("字典内容:", my_dict)
""",
        "inputs": ""
    }
]

def get_examples():
    """获取所有示例"""
    return examples

def get_example_by_index(index):
    """根据索引获取示例"""
    if 0 <= index < len(examples):
        return examples[index]
    return None
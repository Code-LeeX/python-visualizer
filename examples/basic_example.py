# Basic Python Example for Visualization

def greet(name):
    """A simple greeting function"""
    message = "Hello, " + name + "!"
    print(message)
    return message

# Variables
user_name = "Alice"
age = 25
is_student = True

# Function call
greeting = greet(user_name)

# Conditional logic
if age >= 18:
    status = "adult"
else:
    status = "minor"

print(f"{user_name} is {age} years old and is an {status}")

# List operations
numbers = [1, 2, 3, 4, 5]
squares = []

for num in numbers:
    square = num ** 2
    squares.append(square)
    print(f"Square of {num} is {square}")

print(f"Original numbers: {numbers}")
print(f"Squared numbers: {squares}")

# Dictionary example
person = {
    "name": user_name,
    "age": age,
    "is_student": is_student,
    "grades": [85, 90, 78, 92]
}

print(f"Person data: {person}")

# Calculate average grade
total = 0
count = 0
for grade in person["grades"]:
    total += grade
    count += 1

average = total / count
print(f"Average grade: {average}")

# Class example
class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, value):
        self.result += value
        return self.result

    def multiply(self, value):
        self.result *= value
        return self.result

# Using the class
calc = Calculator()
calc.add(10)
calc.multiply(2)
final_result = calc.result

print(f"Calculator result: {final_result}")
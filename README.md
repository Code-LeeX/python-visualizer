# Python Code Execution Visualizer

一个功能完整的Python代码执行过程可视化工具，基于AST解析和自定义解释器实现，提供直观的代码执行动画和状态追踪。

## ✨ 功能特性

- 🔍 **实时代码执行可视化** - 逐行高亮显示当前执行位置
- 📊 **变量状态动态追踪** - 实时显示变量值的变化过程
- 🎯 **执行流程步进控制** - 支持单步调试和速度控制
- 📚 **调用栈可视化** - 清晰展示函数调用层次结构
- 🎨 **数据结构动画展示** - 列表、字典等数据结构的可视化操作
- 💻 **现代化Web界面** - 响应式设计，支持多种交互方式
- ⚡ **实时WebSocket通信** - 流畅的执行状态同步
- 🎮 **丰富的交互功能** - 键盘快捷键、拖拽、上下文菜单等

## 🐍 支持的Python语法

### 基础语法
- ✅ 变量赋值和基础数据类型（int, float, string, boolean, None）
- ✅ 算术运算符（+, -, *, /, //, %, **）
- ✅ 比较运算符（==, !=, <, <=, >, >=, is, in）
- ✅ 逻辑运算符（and, or, not）
- ✅ F-string格式化字符串

### 控制结构
- ✅ 条件判断（if/elif/else）
- ✅ 循环结构（for/while）
- ✅ 循环控制（break/continue）

### 数据结构
- ✅ 列表操作（创建、索引、切片、append、extend、remove、pop）
- ✅ 字典操作（创建、键值访问、更新、迭代）
- ✅ 列表推导式

### 函数和类
- ✅ 函数定义和调用
- ✅ 参数传递（位置参数、关键字参数）
- ✅ 返回值处理
- ✅ 类定义和实例化
- ✅ 方法调用

### 内置函数
- ✅ print(), len(), str(), int(), float(), bool()
- ✅ list(), dict(), range()
- ✅ abs(), max(), min()

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# 克隆或下载项目后，直接运行启动脚本
./start.sh
```

启动脚本会自动：
1. 创建Python虚拟环境
2. 安装所需依赖
3. 运行测试验证功能
4. 启动Web服务器

### 方法二：手动启动

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
python3 tests/test_interpreter.py

# 5. 启动服务器
python backend/app.py
```

### 访问应用

打开浏览器访问：http://localhost:3001

## 🎮 使用说明

### 界面布局

1. **左侧面板** - 代码编辑器
   - 支持语法高亮的Python代码编辑
   - 内置示例代码选择器
   - 输入变量定义区域

2. **中央面板** - 可视化执行区域
   - 实时代码执行高亮
   - 执行控制按钮组
   - 控制台输出显示

3. **右侧面板** - 状态监控
   - 变量状态实时显示
   - 函数调用栈跟踪
   - 执行统计信息

### 执行控制

- **运行 (Ctrl+Enter/F5)** - 完整执行代码
- **步进 (Ctrl+./F10)** - 单步执行每行代码
- **暂停** - 暂停当前执行
- **停止 (Escape)** - 停止执行
- **重置 (Ctrl+Shift+R)** - 重置执行环境

### 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Enter` | 运行代码 |
| `F5` | 运行代码 |
| `F10` | 单步执行 |
| `Ctrl+.` | 单步执行 |
| `Escape` | 停止执行 |
| `Ctrl+Shift+R` | 重置 |
| `Ctrl+Shift+P` | 解析代码 |

### 示例代码

应用内置了多个示例代码，包括：
- Hello World 基础示例
- 斐波那契数列递归计算
- 列表操作演示
- 字典操作演示
- 类和对象示例
- 循环结构示例

## 🏗️ 项目结构

```
python_visualizer/
├── 📁 backend/                    # 后端代码
│   ├── 🐍 app.py                 # Flask应用主文件
│   ├── 🔍 ast_parser.py          # AST解析器
│   ├── ⚙️ interpreter.py          # 自定义Python解释器
│   └── 🔌 websocket_handler.py    # WebSocket处理器
├── 📁 frontend/                   # 前端代码
│   ├── 📁 templates/              # HTML模板
│   │   └── 🌐 index.html         # 主页面
│   └── 📁 static/                 # 静态资源
│       ├── 📁 css/                # 样式文件
│       └── 📁 js/                 # JavaScript文件
├── 📁 examples/                   # 示例代码
│   └── 🐍 basic_example.py       # 基础示例
├── 📁 tests/                      # 测试文件
│   └── 🧪 test_interpreter.py     # 解释器测试
├── 🚀 start.sh                   # 启动脚本
├── 📋 requirements.txt           # Python依赖
└── 📖 README.md                  # 项目说明
```

## 🧪 测试

项目包含完整的测试套件：

```bash
# 运行所有测试
python3 tests/test_interpreter.py

# 测试内容包括：
# - 基础运算和变量操作
# - 条件逻辑执行
# - 循环结构处理
# - 函数定义和调用
```

## 🔧 技术架构

### 后端技术栈
- **Flask** - Web框架
- **Flask-SocketIO** - WebSocket实时通信
- **AST** - Python抽象语法树解析
- **自定义解释器** - 逐步执行和状态追踪

### 前端技术栈
- **HTML5/CSS3** - 现代Web标准
- **JavaScript ES6+** - 交互逻辑
- **CodeMirror** - 代码编辑器
- **Canvas API** - 数据结构可视化
- **WebSocket** - 实时通信

### 核心设计
1. **AST解析器** - 将Python代码转换为抽象语法树
2. **执行钩子** - 在每个执行步骤记录状态信息
3. **可视化引擎** - 实时渲染执行状态和变量变化
4. **WebSocket通信** - 保持前后端状态同步

## 🚧 已知限制

当前版本不支持：
- 复杂的Python库导入（如numpy, pandas等）
- 多线程和异步操作
- 文件I/O操作
- 复杂的异常处理
- 装饰器和元类
- 生成器和迭代器协议

## 🔮 未来计划

- [ ] 添加更多Python语法支持
- [ ] 实现断点调试功能
- [ ] 添加代码性能分析
- [ ] 支持代码分享和保存
- [ ] 移动端适配优化
- [ ] 多语言界面支持

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

感谢所有开源项目和社区的贡献，特别是：
- Flask 和 Flask-SocketIO 团队
- CodeMirror 编辑器
- Python AST 模块

---

**享受Python代码可视化的乐趣！** 🎉
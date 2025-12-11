#!/bin/bash

# Python代码执行可视化工具启动脚本

echo "🚀 启动Python代码执行可视化工具..."

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv

    echo "📥 安装依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 运行测试
echo "🧪 运行测试..."
python3 tests/test_interpreter.py

if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过！"
    echo ""
    echo "🌐 启动Web服务器..."
    echo "📍 服务将运行在: http://localhost:5000"
    echo "⏹️  按 Ctrl+C 停止服务器"
    echo ""

    # 启动服务器
    python backend/app.py
else
    echo "❌ 测试失败，请检查代码"
    exit 1
fi
"""
Python代码执行可视化工具 - Flask API服务器
"""
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from websocket_handler import setup_websocket_handlers, execution_manager
from examples import get_examples as get_example_list

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'python_visualizer_secret_key_2024'

# 启用CORS支持React前端
CORS(app, origins=["http://localhost:3001"])

# 创建SocketIO实例，允许React前端连接
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3001"])

# 设置WebSocket处理器
setup_websocket_handlers(socketio)

@app.route('/api/examples')
def get_examples():
    """获取示例代码"""
    # 使用新的动画演示示例
    examples = get_example_list()
    return jsonify(examples)

@app.route('/api/parse', methods=['POST'])
def parse_code():
    """解析代码API端点"""
    data = request.json
    source_code = data.get('source_code', '')
    inputs = data.get('inputs', '')

    print(f"Parsing code: {len(source_code)} characters")
    result = execution_manager.parse_code(source_code, inputs)
    print(f"Parse result: success={result.get('success')}")

    # 如果解析成功，自动开始执行
    if result.get('success'):
        print("Code parsed successfully, starting execution automatically...")
        execution_result = execution_manager.start_execution(step_mode=False)
        print(f"Execution start result: {execution_result}")
        result['execution_started'] = execution_result.get('success', False)

    return jsonify(result)

@app.route('/api/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'Python Code Visualizer',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Python Code Visualizer...")
    print("Server will be available at: http://localhost:3002")

    # 检查端口是否可用
    port = 3002
    host = '0.0.0.0'

    # 启动服务器
    socketio.run(app,
                host=host,
                port=port,
                debug=True,
                allow_unsafe_werkzeug=True)
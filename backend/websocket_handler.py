"""
WebSocket处理器 - 处理实时通信和执行控制
"""
from flask_socketio import SocketIO, emit
import threading
import time
from ast_parser import ASTParser, ExecutionHook
from interpreter import PythonInterpreter

class ExecutionManager:
    """执行管理器 - 管理代码执行过程"""

    def __init__(self):
        self.current_execution = None
        self.is_running = False
        self.is_paused = False
        self.step_mode = False
        self.execution_thread = None
        self.socketio = None
        self.default_execution_delay = 0.3  # Default delay in seconds
        self.step_iterator = None  # For step-by-step execution

    def set_socketio(self, socketio: SocketIO):
        """设置SocketIO实例"""
        self.socketio = socketio

    def parse_code(self, source_code: str, inputs: str = ""):
        """解析代码"""
        parser = ASTParser()
        result = parser.parse(source_code)

        if result['success']:
            # 创建执行环境
            hook = ExecutionHook()
            interpreter = PythonInterpreter(hook, execution_delay=self.default_execution_delay)
            # 设置解释器的执行管理器引用，让它能检查暂停状态
            interpreter.execution_manager = self

            # 处理输入参数
            if inputs.strip():
                try:
                    # 简单的输入解析
                    input_vars = {}
                    for line in inputs.strip().split('\n'):
                        if '=' in line:
                            name, value = line.split('=', 1)
                            name = name.strip()
                            value = value.strip()
                            # 尝试解析值
                            try:
                                input_vars[name] = eval(value)
                            except:
                                input_vars[name] = value

                    # 将输入变量添加到解释器
                    for name, value in input_vars.items():
                        interpreter.set_variable(name, value)

                except Exception as e:
                    return {
                        'success': False,
                        'error': 'InputError',
                        'message': f'Error parsing inputs: {str(e)}'
                    }

            self.current_execution = {
                'ast_tree': result['ast'],
                'interpreter': interpreter,
                'hook': hook,
                'parser_info': result
            }

            return {
                'success': True,
                'functions': result['functions'],
                'classes': result['classes'],
                'variables': result['variables'],
                'control_flow': result['control_flow'],
                'line_count': result['line_count']
            }
        else:
            return result

    def start_execution(self, step_mode: bool = False):
        """开始执行"""
        print(f"⚡ [ExecutionManager] start_execution called with step_mode={step_mode}")
        if not self.current_execution:
            print("⚡ [ExecutionManager] No current execution context")
            return {'success': False, 'message': 'No code to execute'}

        self.is_running = True
        self.is_paused = False
        self.step_mode = step_mode
        print(f"⚡ [ExecutionManager] Set step_mode={self.step_mode}, is_running={self.is_running}")

        if step_mode:
            # 步进模式：初始化步进迭代器并开始执行（会在第一步暂停）
            print("⚡ [ExecutionManager] Creating step iterator for step mode...")
            try:
                self.step_iterator = self._create_step_iterator()
                print("⚡ [ExecutionManager] Step iterator created, starting execution...")
                self.step_iterator.start_execution()
                print("⚡ [ExecutionManager] Step iterator start_execution called")
                self._emit_execution_start()
                print("⚡ [ExecutionManager] Step mode started successfully")
                return {'success': True, 'message': 'Step mode started - click Step to continue'}
            except Exception as e:
                print(f"⚡ [ExecutionManager] ERROR creating step iterator: {e}")
                print(f"⚡ [ExecutionManager] Exception type: {type(e).__name__}")
                import traceback
                print(f"⚡ [ExecutionManager] Traceback: {traceback.format_exc()}")
                self.is_running = False
                self.step_mode = False
                return {'success': False, 'message': f'Failed to start step mode: {str(e)}'}
        else:
            # 正常模式：在新线程中连续执行
            print("⚡ [ExecutionManager] Starting continuous execution thread...")
            self.execution_thread = threading.Thread(target=self._execute_code)
            self.execution_thread.start()
            return {'success': True, 'message': 'Continuous execution started'}

    def _execute_code(self):
        """执行代码的内部方法"""
        try:
            interpreter = self.current_execution['interpreter']
            ast_tree = self.current_execution['ast_tree']
            hook = self.current_execution['hook']

            # 设置hook的回调函数，让它可以发送实时更新
            hook.emit_callback = self._emit_execution_step

            # 开始执行
            self._emit_execution_start()

            # 执行AST
            result = interpreter.execute(ast_tree)

            # 检查是否被停止
            if interpreter.should_stop:
                print("Execution was stopped")
                if self.socketio:
                    self.socketio.emit('execution_control', {
                        'success': True,
                        'message': 'Execution stopped by user'
                    })
            else:
                # 正常执行完成
                self._emit_execution_complete(result, interpreter.output_buffer)

        except Exception as e:
            error_msg = str(e)
            print(f"Execution error: {error_msg}")

            # 区分停止和错误
            if "Execution stopped" in error_msg:
                if self.socketio:
                    self.socketio.emit('execution_control', {
                        'success': True,
                        'message': 'Execution stopped by user'
                    })
            else:
                self._emit_execution_error(error_msg)
        finally:
            print("Cleaning up execution state...")
            self.is_running = False
            self.is_paused = False
            if self.current_execution:
                self.current_execution['interpreter'].should_stop = False  # 重置标志

    def _emit_execution_start(self):
        """发送执行开始事件"""
        if self.socketio:
            self.socketio.emit('execution_started', {
                'message': 'Code execution started'
            })

    def _emit_execution_step(self, step_data):
        """发送执行步骤事件"""
        print(f"Emitting execution step: line {step_data.get('line')}, variables: {len(step_data.get('variables', {}))}")
        if self.socketio:
            self.socketio.emit('execution_step', step_data)

    def _emit_execution_complete(self, result, output):
        """发送执行完成事件"""
        if self.socketio:
            self.socketio.emit('execution_completed', {
                'result': result,
                'output': output,
                'steps': self.current_execution['hook'].steps
            })

    def _emit_execution_error(self, error_message):
        """发送执行错误事件"""
        if self.socketio:
            self.socketio.emit('execution_error', {
                'error': error_message
            })

    def pause_execution(self):
        """暂停执行"""
        if not self.is_running:
            print("Cannot pause: No execution in progress")
            return {'success': False, 'message': 'No execution in progress to pause'}

        if self.is_paused:
            print("Execution is already paused")
            return {'success': False, 'message': 'Execution is already paused'}

        print("Pausing execution...")
        self.is_paused = True
        print(f"Pause state set: is_paused={self.is_paused}, is_running={self.is_running}")
        return {'success': True, 'message': 'Execution paused'}

    def resume_execution(self):
        """恢复执行"""
        if not self.is_running:
            print("Cannot resume: No execution in progress")
            return {'success': False, 'message': 'No execution in progress to resume'}

        if not self.is_paused:
            print("Execution is not paused, cannot resume")
            return {'success': False, 'message': 'Execution is not paused'}

        print("Resuming execution...")
        self.is_paused = False
        print(f"Resume state set: is_paused={self.is_paused}, is_running={self.is_running}")
        return {'success': True, 'message': 'Execution resumed'}

    def stop_execution(self):
        """停止执行"""
        print("Stopping execution...")
        self.is_running = False
        self.is_paused = False

        # 强制终止执行线程
        if self.execution_thread and self.execution_thread.is_alive():
            print("Terminating execution thread...")
            # 设置停止标志
            if hasattr(self, 'step_wait_event'):
                self.step_wait_event.set()  # 唤醒可能在等待的步进模式

        # 清理当前执行状态
        if self.current_execution:
            interpreter = self.current_execution['interpreter']
            interpreter.should_stop = True  # 设置解释器停止标志

        return {'success': True, 'message': 'Execution stopped'}

    def _create_step_iterator(self):
        """创建单步执行迭代器"""
        print("🔄 [ExecutionManager] _create_step_iterator method entered")
        interpreter = self.current_execution['interpreter']
        ast_tree = self.current_execution['ast_tree']
        hook = self.current_execution['hook']
        print(f"🔄 [ExecutionManager] Got interpreter: {bool(interpreter)}, ast_tree: {bool(ast_tree)}, hook: {bool(hook)}")

        # 首先设置hook的正常回调函数（如果还没设置的话）
        if not hasattr(hook, 'emit_callback') or hook.emit_callback is None:
            print("🔄 [ExecutionManager] Setting hook emit_callback to _emit_execution_step")
            hook.emit_callback = self._emit_execution_step

        # 设置hook的回调函数，让它在每步后等待
        original_callback = hook.emit_callback
        print(f"🔄 [ExecutionManager] original_callback is: {original_callback}")
        self.step_wait_event = threading.Event()

        # 跟踪是否是第一步
        self.is_first_step = True

        def step_callback(step_data):
            print(f"🔄 [StepIterator] step_callback called with step_data line: {step_data.get('line', 'N/A')}")
            if original_callback:
                print("🔄 [StepIterator] Calling original callback")
                original_callback(step_data)

            # 如果是第一步，直接显示不等待；后续步骤需要等待用户输入
            if self.step_mode and self.is_running:
                if self.is_first_step:
                    print("🔄 [StepIterator] First step - displaying immediately without waiting")
                    self.is_first_step = False
                else:
                    print(f"🔄 [StepIterator] Step mode active, waiting for step_next... (step_mode={self.step_mode}, is_running={self.is_running})")
                    self.step_wait_event.wait()  # 等待step_next调用
                    print("🔄 [StepIterator] Received step_next signal, continuing...")
                    self.step_wait_event.clear()  # 重置事件
            else:
                print(f"🔄 [StepIterator] Not waiting - step_mode={self.step_mode}, is_running={self.is_running}")

        hook.emit_callback = step_callback

        class StepIterator:
            def __init__(self, manager, interp, tree):
                self.manager = manager
                self.interpreter = interp
                self.ast_tree = tree
                self.completed = False
                self.thread = None

            def start_execution(self):
                """开始执行（在线程中）"""
                print("🔄 [StepIterator] start_execution called")
                if not self.completed:
                    print("🔄 [StepIterator] Creating execution thread...")
                    self.thread = threading.Thread(target=self._execute_all)
                    self.thread.start()
                    print("🔄 [StepIterator] Execution thread started")
                else:
                    print("🔄 [StepIterator] Already completed, not starting")

            def _execute_all(self):
                """执行所有步骤（但会在每步后暂停）"""
                print("🔄 [StepIterator] _execute_all thread started")
                try:
                    print("🔄 [StepIterator] Starting interpreter execution...")
                    result = self.interpreter.execute(self.ast_tree)
                    print("🔄 [StepIterator] Interpreter execution completed")
                    self.completed = True

                    # 检查是否被停止
                    if self.interpreter.should_stop:
                        print("Step execution was stopped")
                        if self.manager.socketio:
                            self.manager.socketio.emit('execution_control', {
                                'success': True,
                                'message': 'Step execution stopped by user'
                            })
                    else:
                        # 发送完成事件
                        print("🔄 [StepIterator] Emitting execution complete")
                        self.manager._emit_execution_complete(result, self.interpreter.output_buffer)

                except Exception as e:
                    self.completed = True
                    error_msg = str(e)
                    print(f"🔄 [StepIterator] Step execution error: {error_msg}")

                    # 区分停止和错误
                    if "Execution stopped" in error_msg:
                        if self.manager.socketio:
                            self.manager.socketio.emit('execution_control', {
                                'success': True,
                                'message': 'Step execution stopped by user'
                            })
                    else:
                        print("🔄 [StepIterator] Emitting error")
                        self.manager._emit_execution_error(error_msg)
                finally:
                    print("🔄 [StepIterator] Cleaning up step execution...")
                    self.manager.is_running = False
                    if self.interpreter:
                        self.interpreter.should_stop = False  # 重置标志

        print("🔄 [ExecutionManager] Creating StepIterator instance...")
        step_iterator = StepIterator(self, interpreter, ast_tree)
        print("🔄 [ExecutionManager] StepIterator instance created, returning...")
        return step_iterator

    def step_next(self):
        """单步执行下一步"""
        print(f"🔄 [ExecutionManager] step_next called - current_execution: {bool(self.current_execution)}, step_mode: {self.step_mode}, is_running: {self.is_running}")

        if not self.current_execution or not self.step_mode:
            print("🔄 [ExecutionManager] Not in step mode")
            return {'success': False, 'message': 'Not in step mode'}

        if not self.is_running:
            print("🔄 [ExecutionManager] No execution in progress")
            return {'success': False, 'message': 'No execution in progress'}

        # 触发继续执行下一步
        if hasattr(self, 'step_wait_event'):
            print("🔄 [ExecutionManager] Triggering step_wait_event")
            self.step_wait_event.set()
            return {'success': True, 'message': 'Continuing to next step'}
        else:
            print("🔄 [ExecutionManager] Step mechanism not available")
            return {'success': False, 'message': 'Step mechanism not available'}

    def get_current_state(self):
        """获取当前执行状态"""
        if not self.current_execution:
            return {'success': False, 'message': 'No execution context'}

        interpreter = self.current_execution['interpreter']
        hook = self.current_execution['hook']

        return {
            'success': True,
            'current_line': hook.current_line,
            'variables': interpreter.get_all_variables(),
            'call_stack': hook.call_stack,
            'step_count': hook.step_count,
            'is_running': self.is_running,
            'is_paused': self.is_paused
        }

    def set_execution_speed(self, delay: float):
        """设置执行速度"""
        print(f"Setting execution delay to {delay:.2f} seconds")

        if self.current_execution:
            interpreter = self.current_execution['interpreter']
            interpreter.execution_delay = delay
            print(f"Updated current interpreter delay to {delay:.2f}s")
            return {'success': True, 'message': f'Execution speed set to {delay:.2f}s per step'}
        else:
            # Store for future executions
            self.default_execution_delay = delay
            print(f"Stored default delay for future executions: {delay:.2f}s")
            return {'success': True, 'message': f'Execution speed set to {delay:.2f}s per step (will apply to next execution)'}

# 创建全局执行管理器实例
execution_manager = ExecutionManager()

def setup_websocket_handlers(socketio: SocketIO):
    """设置WebSocket事件处理器"""
    execution_manager.set_socketio(socketio)

    @socketio.on('connect')
    def handle_connect():
        """客户端连接"""
        print('🔌 [WebSocket] Client connected - debug mode active - LATEST VERSION')
        emit('connected', {'message': 'Connected to Python Visualizer'})

    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接"""
        print('Client disconnected - stopping any running execution')

        # 立即停止任何正在运行的执行
        if execution_manager.is_running:
            print('Stopping execution due to client disconnect')
            execution_manager.stop_execution()

        # 清理执行环境
        execution_manager.current_execution = None
        execution_manager.step_iterator = None

    @socketio.on('parse_code')
    def handle_parse_code(data):
        """解析代码"""
        print('🔧 [WebSocket] Received parse_code request via WebSocket')
        source_code = data.get('source_code', '')
        inputs = data.get('inputs', '')
        step_mode = data.get('step_mode', False)
        print(f'🔧 [WebSocket] Code length: {len(source_code)}, Inputs: {inputs}, Step mode: {step_mode}')

        result = execution_manager.parse_code(source_code, inputs)
        print(f'🔧 [WebSocket] Parse result: success={result.get("success")}')

        if result.get('success'):
            # 如果解析成功，根据模式开始执行
            if step_mode:
                print("🔧 [WebSocket] Starting step mode execution...")
                execution_result = execution_manager.start_execution(step_mode=True)
                print(f"🔧 [WebSocket] Step mode start result: {execution_result}")
            emit('code_parsed', {**result, 'step_mode': step_mode})
        else:
            emit('code_parsed', result)

    @socketio.on('start_execution')
    def handle_start_execution(data):
        """开始执行"""
        step_mode = data.get('step_mode', False)
        result = execution_manager.start_execution(step_mode)
        emit('execution_control', result)

    @socketio.on('pause_execution')
    def handle_pause_execution():
        """暂停执行"""
        result = execution_manager.pause_execution()
        emit('execution_control', result)

    @socketio.on('resume_execution')
    def handle_resume_execution():
        """恢复执行"""
        result = execution_manager.resume_execution()
        emit('execution_control', result)

    @socketio.on('stop_execution')
    def handle_stop_execution():
        """停止执行"""
        result = execution_manager.stop_execution()
        emit('execution_control', result)

    @socketio.on('step_next')
    def handle_step_next():
        """单步执行"""
        print('🔧 [WebSocket] Received step_next request')
        result = execution_manager.step_next()
        print(f'🔧 [WebSocket] Step next result: {result}')
        emit('execution_control', result)

    @socketio.on('get_state')
    def handle_get_state():
        """获取当前状态"""
        result = execution_manager.get_current_state()
        emit('current_state', result)

    @socketio.on('reset')
    def handle_reset():
        """重置执行环境"""
        execution_manager.stop_execution()
        execution_manager.current_execution = None
        emit('execution_control', {
            'success': True,
            'message': 'Execution environment reset'
        })

    @socketio.on('set_execution_speed')
    def handle_set_execution_speed(data):
        """设置执行速度"""
        delay = data.get('delay', 0.3)  # Default to 0.3 seconds
        result = execution_manager.set_execution_speed(delay)
        emit('execution_control', result)
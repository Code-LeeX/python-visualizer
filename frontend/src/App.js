import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

import CodeEditor from './components/CodeEditor';
import VariableViewer from './components/VariableViewer';
import ExecutionControls from './components/ExecutionControls';
import ValueAnimationOverlay from './components/ValueAnimationOverlay';

const API_BASE = 'http://localhost:3002';

function App() {
  const [code, setCode] = useState('');
  const [variables, setVariables] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState(null);
  const [executionState, setExecutionState] = useState('idle'); // idle, running, paused, error
  const [isStepMode, setIsStepMode] = useState(false); // 跟踪是否在步进模式
  const [currentLine, setCurrentLine] = useState(null); // 当前执行行号
  const [variablePositions, setVariablePositions] = useState({}); // 变量位置信息
  const [animationData, setAnimationData] = useState(null); // 当前动画数据
  const [iterationStack, setIterationStack] = useState([]); // 遍历状态栈，支持嵌套循环

  useEffect(() => {
    // 建立WebSocket连接
    const socketConnection = io(API_BASE);

    socketConnection.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to server');
    });

    socketConnection.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    });

    // 监听代码解析事件
    socketConnection.on('code_parsed', (data) => {
      console.log('Code parsed via WebSocket:', data);
      if (!data.success) {
        setExecutionState('error');
        console.error('Parse error:', data.error);
      }
      // 如果是步进模式，状态已经在 handleStepCode 中设置为 'paused'
    });

    // 监听执行开始事件
    socketConnection.on('execution_started', (data) => {
      console.log('Execution started:', data.message);
      // 通过检查当前状态来判断是否在步进模式
      setExecutionState(current => {
        console.log('execution_started: current state:', current);
        // 如果当前已经是paused（用户点击了单步执行），保持paused状态
        if (current === 'paused') {
          return 'paused';
        }
        return 'running';
      });
    });

    // 监听执行步骤事件（实时变量更新）
    socketConnection.on('execution_step', (data) => {
      console.log('Execution step:', data);
      setVariables(data.variables || {});

      // 检查是否包含动画数据
      if (data.animation) {
        console.log('🎬 [Frontend] Received animation data:', data.animation);
        // 触发动画效果
        setAnimationData(data.animation);
      }

      // 检查是否包含遍历状态数据
      if (data.iteration_stack !== undefined) {
        console.log('🔄 [Frontend] Received iteration stack:', data.iteration_stack);
        setIterationStack(data.iteration_stack || []);
      }

      // 更新当前执行行号（只有当行号真正变化时才更新）
      if (data.line) {
        setCurrentLine(prevLine => {
          if (prevLine !== data.line) {
            console.log('Current execution line updated from', prevLine, 'to:', data.line);
            return data.line;
          } else {
            console.log('Same line execution (different AST node):', data.line, 'node_type:', data.node_type);
            return prevLine; // 保持原来的行号，不触发重新渲染
          }
        });
      }
      // 通过检查当前状态来判断模式
      setExecutionState(current => {
        console.log('execution_step: current state:', current);
        // 如果之前是paused状态（步进模式），保持paused
        // 如果是running状态（连续模式），保持running
        if (current === 'paused') {
          return 'paused'; // 步进模式下每步后都暂停等待用户输入
        }
        return 'running'; // 连续模式保持运行
      });
    });

    // 监听执行完成事件
    socketConnection.on('execution_completed', (data) => {
      console.log('Execution completed:', data);
      setVariables(data.result?.variables || {});
      setExecutionState('idle');
      setIsStepMode(false);
      setCurrentLine(null); // 清除当前行号高亮
    });

    // 监听执行错误事件
    socketConnection.on('execution_error', (data) => {
      console.error('Execution error:', data.error);
      setExecutionState('error');
      setIsStepMode(false);
      setCurrentLine(null); // 清除当前行号高亮
    });

    // 监听执行控制事件（暂停、恢复、停止等）
    socketConnection.on('execution_control', (data) => {
      console.log('Execution control:', data);
      if (data.success) {
        console.log(data.message);
      }
    });

    // 兼容旧的事件名称（如果后端还在使用）
    socketConnection.on('execution_update', (data) => {
      setVariables(data.variables || {});
      setExecutionState(data.status || 'idle');
    });

    socketConnection.on('execution_complete', (data) => {
      setVariables(data.variables || {});
      setExecutionState('idle');
    });

    setSocket(socketConnection);

    return () => {
      socketConnection.disconnect();
    };
  }, []);

  const handleRunCode = async () => {
    if (!code.trim()) return;

    setExecutionState('running');
    setIsStepMode(false); // 连续执行模式

    try {
      const response = await axios.post(`${API_BASE}/api/parse`, {
        source_code: code,
        inputs: ''
      });

      if (response.data.success) {
        console.log('Code parsed and execution started automatically');
        // 执行会通过WebSocket事件更新状态
      } else {
        setExecutionState('error');
        console.error('Parse error:', response.data.error);
      }
    } catch (error) {
      setExecutionState('error');
      console.error('Request failed:', error);
    }
  };

  const handleStepCode = () => {
    console.log('🎯 [Frontend] handleStepCode called, current state:', executionState, 'isStepMode:', isStepMode, 'socket:', !!socket, 'currentLine:', currentLine);
    if (!code.trim()) {
      console.log('🎯 [Frontend] No code to execute');
      return;
    }
    if (!socket) {
      console.log('🎯 [Frontend] No socket connection');
      return;
    }

    // 如果还没开始执行，通过 WebSocket 解析并开始步进模式
    if (executionState === 'idle') {
      console.log('🎯 [Frontend] Starting step mode via WebSocket...');
      setExecutionState('paused'); // 设置为暂停状态，等待第一步
      setIsStepMode(true); // 启用步进模式

      const payload = {
        source_code: code,
        inputs: '',
        step_mode: true
      };
      console.log('🎯 [Frontend] Emitting parse_code event with payload:', payload);
      socket.emit('parse_code', payload);
    } else if (executionState === 'paused') {
      // 如果已经在步进模式中，继续下一步
      console.log('🎯 [Frontend] Continuing to next step via step_next...');
      socket.emit('step_next');
      console.log('🎯 [Frontend] step_next event emitted');
    } else {
      console.log('🎯 [Frontend] Cannot step - execution state is:', executionState);
    }
  };

  const handleResetCode = () => {
    setVariables({});
    setExecutionState('idle');
    setIsStepMode(false); // 重置步进模式
    setCurrentLine(null); // 清除当前行号高亮
    if (socket) {
      socket.emit('reset');
    }
  };

  const handleVariablePositionsUpdate = (positions) => {
    setVariablePositions(positions);
    console.log('📍 [App] Variable positions updated:', positions);
  };

  const handleAnimationComplete = (animationId) => {
    console.log('🎬 [App] Animation completed:', animationId);
    // 清除动画数据，防止重复动画
    setAnimationData(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        {/* <h1>🐍 Python代码执行可视化工具</h1> */}
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          <span>{isConnected ? '已连接' : '未连接'}</span>
        </div>
      </header>

      <main className="App-main" style={{ position: 'relative' }}>
        <div className="left-panel">
          <CodeEditor
            value={code}
            onChange={setCode}
            disabled={executionState === 'running'}
            currentLine={currentLine}
          />

          <ExecutionControls
            onRun={handleRunCode}
            onStep={handleStepCode}
            onReset={handleResetCode}
            executionState={executionState}
          />
        </div>

        <div className="right-panel">
          <VariableViewer
            variables={variables}
            onVariablePositionsUpdate={handleVariablePositionsUpdate}
            iterationStack={iterationStack}
          />
        </div>

        {/* 动画覆盖层 */}
        <ValueAnimationOverlay
          animationData={animationData}
          variablePositions={variablePositions}
          onAnimationComplete={handleAnimationComplete}
        />
      </main>
    </div>
  );
}

export default App;

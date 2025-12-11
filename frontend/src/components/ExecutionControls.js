import React from 'react';
import './ExecutionControls.css';

const ExecutionControls = ({ onRun, onStep, onReset, executionState }) => {
  return (
    <div className="execution-controls">
      <h3>🎮 执行控制</h3>

      <div className="controls-buttons">
        <button
          className="control-btn run-btn"
          onClick={onRun}
          disabled={executionState === 'running'}
        >
          ▶️ 运行代码
        </button>

        <button
          className="control-btn step-btn"
          onClick={onStep}
          disabled={executionState === 'running'}
        >
          ⏭️ 单步执行
        </button>

        <button
          className="control-btn reset-btn"
          onClick={onReset}
          disabled={executionState === 'running'}
        >
          🔄 重置
        </button>
      </div>

      <div className="execution-status">
        <div className={`status-indicator ${executionState}`}>
          <span className="status-text">
            {executionState === 'idle' && '⚪ 等待执行'}
            {executionState === 'running' && '🟢 正在执行'}
            {executionState === 'paused' && '🟡 单步模式 - 点击单步继续'}
            {executionState === 'error' && '🔴 执行错误'}
          </span>
        </div>
      </div>

      <div className="keyboard-shortcuts">
        <small>
          快捷键: Ctrl+Enter 运行 | Ctrl+. 单步 | Ctrl+R 重置
        </small>
      </div>
    </div>
  );
};

export default ExecutionControls;
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CodeEditor.css';

const CodeEditor = ({ value, onChange, disabled, currentLine }) => {
  const [examples, setExamples] = useState([]);
  const [selectedExample, setSelectedExample] = useState('');

  useEffect(() => {
    // 获取示例代码
    const fetchExamples = async () => {
      try {
        const response = await axios.get('http://localhost:3002/api/examples');
        setExamples(response.data);
      } catch (error) {
        console.error('Failed to fetch examples:', error);
      }
    };

    fetchExamples();
  }, []);

  const handleExampleChange = (e) => {
    const exampleId = e.target.value;
    setSelectedExample(exampleId);

    const example = examples.find(ex => ex.id === exampleId);
    if (example && onChange) {
      onChange(example.code);
    }
  };

  // 将代码分行处理
  const codeLines = value.split('\n');

  return (
    <div className="code-editor">
      <div className="editor-header">
        <h3>📝 Python代码编辑器</h3>
        <div className="example-selector">
          <label>示例代码:</label>
          <select
            value={selectedExample}
            onChange={handleExampleChange}
            disabled={disabled}
          >
            <option value="">请选择示例...</option>
            {examples.map(example => (
              <option key={example.id} value={example.id}>
                {example.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="code-editor-container">
        {/* 带行号的代码显示区域 */}
        <div className="code-display">
          <div className="line-numbers">
            {codeLines.map((_, index) => (
              <div
                key={index}
                className={`line-number ${currentLine === index + 1 ? 'highlight' : ''}`}
              >
                {index + 1}
              </div>
            ))}
          </div>
          <div className="code-lines">
            {codeLines.map((line, index) => (
              <div
                key={index}
                className={`code-line ${currentLine === index + 1 ? 'highlight' : ''}`}
              >
                {line || '\u00A0'}
              </div>
            ))}
          </div>
        </div>

        {/* 编辑用的textarea（透明覆盖） */}
        <textarea
          className="code-textarea-overlay"
          value={value}
          onChange={(e) => onChange && onChange(e.target.value)}
          disabled={disabled}
          placeholder="在这里输入Python代码..."
          rows={15}
        />
      </div>

      <div className="editor-footer">
        <small>支持基础Python语法：变量、循环、条件、函数等</small>
      </div>
    </div>
  );
};

export default CodeEditor;
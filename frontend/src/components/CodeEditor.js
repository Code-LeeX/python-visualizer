import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CodeEditor.css';

const CodeEditor = ({ value, onChange, disabled }) => {
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

      <textarea
        className="code-textarea"
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        disabled={disabled}
        placeholder="在这里输入Python代码..."
        rows={15}
      />

      <div className="editor-footer">
        <small>支持基础Python语法：变量、循环、条件、函数等</small>
      </div>
    </div>
  );
};

export default CodeEditor;
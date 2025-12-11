import React from 'react';
import './VariableViewer.css';

const VariableViewer = ({ variables }) => {
  const renderVariableValue = (value, type) => {
    if (Array.isArray(value)) {
      return (
        <div className="array-visualization">
          <div className="array-header">
            <span className="array-type">数组</span>
            <span className="array-length">[{value.length}]</span>
          </div>
          <div className="array-elements">
            {value.map((item, index) => (
              <div key={index} className="array-element">
                <div className="element-index">{index}</div>
                <div className="element-value">{JSON.stringify(item)}</div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (type === 'dict' || (typeof value === 'object' && value !== null)) {
      return (
        <div className="dict-visualization">
          <div className="dict-header">
            <span className="dict-type">字典</span>
            <span className="dict-count">{Object.keys(value).length} keys</span>
          </div>
          <div className="dict-entries">
            {Object.entries(value).map(([key, val]) => (
              <div key={key} className="dict-entry">
                <div className="dict-key">"{key}":</div>
                <div className="dict-value">{JSON.stringify(val)}</div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // 基础类型
    return (
      <div className={`basic-value ${type}`}>
        {JSON.stringify(value)}
      </div>
    );
  };

  const getVariableTypeIcon = (type) => {
    const icons = {
      'int': '🔢',
      'float': '📊',
      'str': '📝',
      'bool': '☑️',
      'list': '📋',
      'dict': '📖',
      'function': '⚡'
    };
    return icons[type] || '❓';
  };

  return (
    <div className="variable-viewer">
      <h3>🔍 变量监控</h3>

      {Object.keys(variables).length === 0 ? (
        <div className="no-variables">
          <p>暂无变量数据</p>
          <small>运行代码后变量状态将显示在这里</small>
        </div>
      ) : (
        <div className="variables-list">
          {Object.entries(variables).map(([scope, scopeVars]) => (
            <div key={scope} className="scope-section">
              <h4 className="scope-title">
                {scope === 'global' ? '🌍 全局变量' : '🏠 局部变量'}
              </h4>

              {Object.keys(scopeVars).length === 0 ? (
                <div className="no-scope-vars">
                  <small>该作用域暂无变量</small>
                </div>
              ) : (
                <div className="scope-variables">
                  {Object.entries(scopeVars).map(([varName, varData]) => {
                    // 安全检查：确保 varData 不为 null 且有必要的属性
                    if (!varData || typeof varData !== 'object') {
                      return (
                        <div key={varName} className="variable-item">
                          <div className="variable-header">
                            <span className="variable-icon">❓</span>
                            <span className="variable-name">{varName}</span>
                            <span className="variable-type">unknown</span>
                          </div>
                          <div className="variable-content">
                            <div className="basic-value">
                              {JSON.stringify(varData)}
                            </div>
                          </div>
                        </div>
                      );
                    }

                    const safeType = varData.type || 'unknown';
                    const safeValue = varData.value !== undefined ? varData.value : varData;

                    return (
                      <div key={varName} className="variable-item">
                        <div className="variable-header">
                          <span className="variable-icon">
                            {getVariableTypeIcon(safeType)}
                          </span>
                          <span className="variable-name">{varName}</span>
                          <span className="variable-type">{safeType}</span>
                        </div>

                        <div className="variable-content">
                          {renderVariableValue(safeValue, safeType)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="viewer-footer">
        <small>实时更新变量状态 - 无动画干扰</small>
      </div>
    </div>
  );
};

export default VariableViewer;
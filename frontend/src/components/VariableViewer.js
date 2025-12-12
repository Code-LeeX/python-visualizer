import React, { useRef, useEffect, useState } from 'react';
import './VariableViewer.css';

const VariableViewer = ({ variables, onVariablePositionsUpdate, iterationStack }) => {
  const variableRefs = useRef({});
  const containerRef = useRef(null);
  const [variablePositions, setVariablePositions] = useState({});
  const [hiddenVariables, setHiddenVariables] = useState(new Set()); // 隐藏的变量集合
  const [showHiddenVariables, setShowHiddenVariables] = useState(false); // 是否显示隐藏变量

  // 计算变量位置的效果钩子
  useEffect(() => {
    const updatePositions = () => {
      const newPositions = {};
      const containerRect = containerRef.current?.getBoundingClientRect();

      if (containerRect) {
        Object.entries(variableRefs.current).forEach(([varId, ref]) => {
          if (ref && ref.current) {
            const rect = ref.current.getBoundingClientRect();
            const relativePosition = {
              top: rect.top - containerRect.top,
              left: rect.left - containerRect.left,
              width: rect.width,
              height: rect.height,
              centerX: rect.left - containerRect.left + rect.width / 2,
              centerY: rect.top - containerRect.top + rect.height / 2,
              absoluteX: rect.left,
              absoluteY: rect.top
            };
            newPositions[varId] = relativePosition;
            console.log(`📍 [VariableViewer] Position for ${varId}:`, relativePosition);
          }
        });

        setVariablePositions(newPositions);

        // 通知父组件位置更新
        if (onVariablePositionsUpdate) {
          onVariablePositionsUpdate(newPositions);
        }
      }
    };

    // 延迟计算以确保DOM更新完成
    const timer = setTimeout(updatePositions, 100);

    // 窗口大小变化时重新计算
    window.addEventListener('resize', updatePositions);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', updatePositions);
    };
  }, [variables, onVariablePositionsUpdate]);

  // 隐藏变量
  const hideVariable = (scope, varName) => {
    const varId = `${scope}.${varName}`;
    setHiddenVariables(prev => new Set([...prev, varId]));
  };

  // 恢复显示变量
  const showVariable = (scope, varName) => {
    const varId = `${scope}.${varName}`;
    setHiddenVariables(prev => {
      const newSet = new Set(prev);
      newSet.delete(varId);
      return newSet;
    });
  };

  // 切换显示隐藏变量
  const toggleShowHiddenVariables = () => {
    setShowHiddenVariables(prev => !prev);
  };

  const renderVariableValue = (value, type, varName) => {
    // 调试信息
    if (iterationStack && iterationStack.length > 0 && console.log) {
      console.log('🔄 [VariableViewer] Rendering', varName, 'with iteration stack:', iterationStack);
    }

    if (Array.isArray(value)) {
      return (
        <div className="array-visualization">
          <div className="array-header">
            <span className="array-type">数组</span>
            <span className="array-length">[{value.length}]</span>
          </div>
          <div className="array-elements">
            {value.map((item, index) => {
              // 检查是否是当前遍历的元素，支持多层嵌套、双指针和切片范围
              let iterationInfo = null;
              let multiIndexInfo = null;
              let sliceRangeInfo = null;

              if (iterationStack && iterationStack.length > 0) {
                // 查找匹配的迭代上下文（单指针）
                iterationInfo = iterationStack.find(context =>
                  context.container === varName &&
                  context.current_index === index &&
                  context.current_index >= 0  // 确保已开始遍历
                );

                // 查找多指针访问
                for (let context of iterationStack) {
                  if (context.multi_indices && context.multi_indices[varName]) {
                    const multiIndices = context.multi_indices[varName];

                    // 检查是否是多指针模式
                    if (multiIndices.type === 'multi_index') {
                      const pointerIndex = multiIndices.indices.indexOf(index);
                      if (pointerIndex !== -1) {
                        multiIndexInfo = {
                          level: context.level,
                          pointerType: pointerIndex, // 0=第一个指针, 1=第二个指针
                          pointerVar: multiIndices.index_vars[pointerIndex],
                          totalPointers: multiIndices.indices.length
                        };
                        break;
                      }
                    }

                    // 检查是否是切片范围模式
                    else if (multiIndices.type === 'slice_range') {
                      const startIdx = multiIndices.start_index;
                      const endIdx = multiIndices.end_index;
                      if (index >= startIdx && index < endIdx) {
                        sliceRangeInfo = {
                          level: context.level,
                          startVar: multiIndices.start_var,
                          endVar: multiIndices.end_var,
                          startIndex: startIdx,
                          endIndex: endIdx,
                          isStartBoundary: index === startIdx,
                          isEndBoundary: index === endIdx - 1
                        };
                        break;
                      }
                    }
                  }
                }
              }

              const isCurrentIteration = !!(iterationInfo || multiIndexInfo);
              const isSliceRange = !!sliceRangeInfo;
              const iterationLevel = iterationInfo ? iterationInfo.level : (multiIndexInfo ? multiIndexInfo.level : (sliceRangeInfo ? sliceRangeInfo.level : 0));
              const pointerType = multiIndexInfo ? multiIndexInfo.pointerType : 0;

              // 构建CSS类名
              let cssClasses = ['array-element'];

              if (isCurrentIteration) {
                cssClasses.push('current-iteration', `level-${iterationLevel}`);
              }

              if (multiIndexInfo) {
                cssClasses.push(`pointer-${pointerType}`);
              }

              if (isSliceRange) {
                cssClasses.push('slice-range');
                if (sliceRangeInfo.isStartBoundary) cssClasses.push('slice-start');
                if (sliceRangeInfo.isEndBoundary) cssClasses.push('slice-end');
              }

              // 构建title信息
              let title = '';
              if (multiIndexInfo) {
                title = `Pointer: ${multiIndexInfo.pointerVar}`;
              } else if (sliceRangeInfo) {
                title = `Slice: ${sliceRangeInfo.startVar}[${sliceRangeInfo.startIndex}] to ${sliceRangeInfo.endVar}[${sliceRangeInfo.endIndex}]`;
              }

              return (
                <div
                  key={index}
                  className={cssClasses.join(' ')}
                  data-iteration-level={iterationLevel}
                  data-pointer-type={pointerType}
                  title={title}
                >
                  <div className="element-index">{index}</div>
                  <div className="element-value">{JSON.stringify(item)}</div>
                </div>
              );
            })}
          </div>
        </div>
      );
    }

    // 字符串可视化 - 支持字符级别的索引遍历
    if (type === 'str' || typeof value === 'string') {
      // 将字符串转换为字符数组进行处理
      const chars = Array.from(value);

      return (
        <div className="string-visualization">
          <div className="string-header">
            <span className="string-type">字符串</span>
            <span className="string-length">[{chars.length}]</span>
          </div>
          <div className="string-characters">
            {chars.map((char, index) => {
              // 检查是否是当前遍历的字符，支持多层嵌套、双指针和切片范围
              let iterationInfo = null;
              let multiIndexInfo = null;
              let sliceRangeInfo = null;

              if (iterationStack && iterationStack.length > 0) {
                // 查找匹配的迭代上下文（单指针）
                iterationInfo = iterationStack.find(context =>
                  context.container === varName &&
                  context.current_index === index &&
                  context.current_index >= 0  // 确保已开始遍历
                );

                // 查找多指针访问
                for (let context of iterationStack) {
                  if (context.multi_indices && context.multi_indices[varName]) {
                    const multiIndices = context.multi_indices[varName];

                    // 检查是否是多指针模式
                    if (multiIndices.type === 'multi_index') {
                      const pointerIndex = multiIndices.indices.indexOf(index);
                      if (pointerIndex !== -1) {
                        multiIndexInfo = {
                          level: context.level,
                          pointerType: pointerIndex, // 0=第一个指针, 1=第二个指针
                          pointerVar: multiIndices.index_vars[pointerIndex],
                          totalPointers: multiIndices.indices.length
                        };
                        break;
                      }
                    }

                    // 检查是否是切片范围模式
                    else if (multiIndices.type === 'slice_range') {
                      const startIdx = multiIndices.start_index;
                      const endIdx = multiIndices.end_index;
                      if (index >= startIdx && index < endIdx) {
                        sliceRangeInfo = {
                          level: context.level,
                          startVar: multiIndices.start_var,
                          endVar: multiIndices.end_var,
                          startIndex: startIdx,
                          endIndex: endIdx,
                          isStartBoundary: index === startIdx,
                          isEndBoundary: index === endIdx - 1
                        };
                        break;
                      }
                    }
                  }
                }
              }

              const isCurrentIteration = !!(iterationInfo || multiIndexInfo);
              const isSliceRange = !!sliceRangeInfo;
              const iterationLevel = iterationInfo ? iterationInfo.level : (multiIndexInfo ? multiIndexInfo.level : (sliceRangeInfo ? sliceRangeInfo.level : 0));
              const pointerType = multiIndexInfo ? multiIndexInfo.pointerType : 0;

              // 构建CSS类名
              let cssClasses = ['string-character'];

              if (isCurrentIteration) {
                cssClasses.push('current-iteration', `level-${iterationLevel}`);
              }

              if (multiIndexInfo) {
                cssClasses.push(`pointer-${pointerType}`);
              }

              if (isSliceRange) {
                cssClasses.push('slice-range');
                if (sliceRangeInfo.isStartBoundary) cssClasses.push('slice-start');
                if (sliceRangeInfo.isEndBoundary) cssClasses.push('slice-end');
              }

              // 构建title信息
              let title = '';
              if (multiIndexInfo) {
                title = `Pointer: ${multiIndexInfo.pointerVar}`;
              } else if (sliceRangeInfo) {
                title = `Slice: ${sliceRangeInfo.startVar}[${sliceRangeInfo.startIndex}] to ${sliceRangeInfo.endVar}[${sliceRangeInfo.endIndex}]`;
              }

              return (
                <div
                  key={index}
                  className={cssClasses.join(' ')}
                  data-iteration-level={iterationLevel}
                  data-pointer-type={pointerType}
                  title={title}
                >
                  <div className="char-index">{index}</div>
                  <div className="char-value">{char === ' ' ? '␣' : char}</div>
                </div>
              );
            })}
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
      'string': '📝',  // 支持 string 类型别名
      'bool': '☑️',
      'list': '📋',
      'dict': '📖',
      'function': '⚡'
    };
    return icons[type] || '❓';
  };

  return (
    <div className="variable-viewer" ref={containerRef}>
      <div className="variable-viewer-header">
        <h3>🔍 变量监控</h3>
        {hiddenVariables.size > 0 && (
          <button
            className="toggle-hidden-btn"
            onClick={toggleShowHiddenVariables}
            title={showHiddenVariables ? "隐藏已隐藏的变量" : "显示已隐藏的变量"}
          >
            {showHiddenVariables ? "👁️" : "👁️‍🗨️"} {hiddenVariables.size}
          </button>
        )}
      </div>

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
                    // 创建变量的唯一ID（包含作用域信息）
                    const varId = `${scope}.${varName}`;
                    const isHidden = hiddenVariables.has(varId);

                    // 如果变量被隐藏且不显示隐藏变量，则跳过
                    if (isHidden && !showHiddenVariables) {
                      return null;
                    }

                    // 安全检查：确保 varData 不为 null 且有必要的属性
                    if (!varData || typeof varData !== 'object') {
                      return (
                        <div key={varName} className={`variable-item ${isHidden ? 'hidden-variable' : ''}`}>
                          <div className="variable-header">
                            <div className="variable-info">
                              <span className="variable-icon">❓</span>
                              <span className="variable-name">{varName}</span>
                              <span className="variable-type">unknown</span>
                            </div>
                            <div className="variable-controls">
                              {isHidden ? (
                                <button
                                  className="show-variable-btn"
                                  onClick={() => showVariable(scope, varName)}
                                  title="显示变量"
                                >
                                  👁️
                                </button>
                              ) : (
                                <button
                                  className="hide-variable-btn"
                                  onClick={() => hideVariable(scope, varName)}
                                  title="隐藏变量"
                                >
                                  👁️‍🗨️
                                </button>
                              )}
                            </div>
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

                    // 确保为该变量创建ref
                    if (!variableRefs.current[varId]) {
                      variableRefs.current[varId] = React.createRef();
                    }

                    return (
                      <div
                        key={varName}
                        className={`variable-item ${isHidden ? 'hidden-variable' : ''}`}
                        ref={variableRefs.current[varId]}
                        data-variable-id={varId}
                      >
                        <div className="variable-header">
                          <div className="variable-info">
                            <span className="variable-icon">
                              {getVariableTypeIcon(safeType)}
                            </span>
                            <span className="variable-name">{varName}</span>
                            <span className="variable-type">{safeType}</span>
                          </div>
                          <div className="variable-controls">
                            {isHidden ? (
                              <button
                                className="show-variable-btn"
                                onClick={() => showVariable(scope, varName)}
                                title="显示变量"
                              >
                                👁️
                              </button>
                            ) : (
                              <button
                                className="hide-variable-btn"
                                onClick={() => hideVariable(scope, varName)}
                                title="隐藏变量"
                              >
                                👁️‍🗨️
                              </button>
                            )}
                          </div>
                        </div>

                        <div className="variable-content">
                          {renderVariableValue(safeValue, safeType, varName)}
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
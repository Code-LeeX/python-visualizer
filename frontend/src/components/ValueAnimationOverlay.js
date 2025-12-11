import React, { useState, useEffect, useRef } from 'react';
import './ValueAnimationOverlay.css';

const ValueAnimationOverlay = ({ animationData, variablePositions, onAnimationComplete }) => {
  const [activeAnimations, setActiveAnimations] = useState([]);
  const containerRef = useRef(null);
  const animationIdRef = useRef(0);

  useEffect(() => {
    if (animationData && variablePositions) {
      console.log('🎬 [ValueAnimationOverlay] Starting animation:', animationData);
      console.log('🎬 [ValueAnimationOverlay] Variable positions:', variablePositions);

      const sourceVarId = `global.${animationData.source_variable}`;
      const targetVarId = `global.${animationData.target_variable}`;

      const sourcePos = variablePositions[sourceVarId];
      const targetPos = variablePositions[targetVarId];

      if (sourcePos && targetPos) {
        const animationId = animationIdRef.current++;
        const newAnimation = {
          id: animationId,
          value: animationData.source_value,
          startX: sourcePos.centerX,
          startY: sourcePos.centerY,
          endX: targetPos.centerX,
          endY: targetPos.centerY,
          operation: animationData.operation,
          animationType: animationData.animation_type,
          timestamp: Date.now()
        };

        console.log('🎬 [ValueAnimationOverlay] Animation coordinates:', newAnimation);

        setActiveAnimations(prev => [...prev, newAnimation]);

        // 动画持续时间
        const animationDuration = 1200; // 1.2秒

        setTimeout(() => {
          setActiveAnimations(prev => prev.filter(anim => anim.id !== animationId));
          if (onAnimationComplete) {
            onAnimationComplete(animationId);
          }
        }, animationDuration);

      } else {
        console.warn('🎬 [ValueAnimationOverlay] Missing position data for variables:', {
          sourceVarId,
          targetVarId,
          sourcePos,
          targetPos
        });
      }
    }
  }, [animationData, variablePositions, onAnimationComplete]);

  const renderFlyingValue = (animation) => {
    const { id, value, startX, startY, endX, endY, operation } = animation;

    // 计算动画样式
    const animationStyle = {
      '--start-x': `${startX}px`,
      '--start-y': `${startY}px`,
      '--end-x': `${endX}px`,
      '--end-y': `${endY}px`
    };

    return (
      <div
        key={id}
        className={`flying-value flying-value-${operation}`}
        style={animationStyle}
      >
        <div className="flying-value-content">
          <span className="flying-value-text">{JSON.stringify(value)}</span>
          <div className="flying-value-trail"></div>
        </div>
      </div>
    );
  };

  return (
    <div className="value-animation-overlay" ref={containerRef}>
      {activeAnimations.map(renderFlyingValue)}

      {/* 调试信息 */}
      {process.env.NODE_ENV === 'development' && (
        <div className="animation-debug">
          <div>活跃动画数量: {activeAnimations.length}</div>
          <div>变量位置数量: {Object.keys(variablePositions).length}</div>
        </div>
      )}
    </div>
  );
};

export default ValueAnimationOverlay;
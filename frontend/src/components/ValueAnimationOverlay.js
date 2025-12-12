import React, { useState, useEffect, useRef } from 'react';
import './ValueAnimationOverlay.css';

const ValueAnimationOverlay = ({ animationData, variablePositions, onAnimationComplete }) => {
  const [activeAnimations, setActiveAnimations] = useState([]);
  const containerRef = useRef(null);
  const animationIdRef = useRef(0);
  const processedAnimations = useRef(new Set()); // 防止重复动画

  useEffect(() => {
    // 如果animationData为null，清空处理记录（用于重置）
    if (!animationData) {
      processedAnimations.current.clear();
      console.log('🎬 [ValueAnimationOverlay] Cleared processed animations');
      return;
    }

    if (animationData && variablePositions) {
      console.log('🎬 [ValueAnimationOverlay] Starting animation:', animationData);
      console.log('🎬 [ValueAnimationOverlay] Variable positions:', variablePositions);

      // 创建动画的唯一标识符，防止重复动画
      const animationKey = JSON.stringify({
        line: animationData.line,
        operation: animationData.operation,
        source_variable: animationData.source_variable,
        target_variable: animationData.target_variable,
        source_value: animationData.source_value,
        step_count: animationData.step_count
      });

      console.log('🎬 [ValueAnimationOverlay] Animation key:', animationKey);
      console.log('🎬 [ValueAnimationOverlay] Processed animations count:', processedAnimations.current.size);

      // 检查是否已经处理过相同的动画
      if (processedAnimations.current.has(animationKey)) {
        console.log('🎬 [ValueAnimationOverlay] Skipping duplicate animation');
        return;
      }

      // 记录已处理的动画
      processedAnimations.current.add(animationKey);
      console.log('🎬 [ValueAnimationOverlay] Added to processed animations, new count:', processedAnimations.current.size);

      const sourceVarId = `global.${animationData.source_variable}`;
      const targetVarId = `global.${animationData.target_variable}`;

      const sourcePos = variablePositions[sourceVarId];
      const targetPos = variablePositions[targetVarId];

      if (sourcePos && targetPos) {
        const animationId = animationIdRef.current++;

        // Use absolute coordinates instead of relative coordinates
        // since the animation overlay is positioned absolutely over the page
        const startX = sourcePos.absoluteX + sourcePos.width / 2;
        const startY = sourcePos.absoluteY + sourcePos.height / 2;
        const endX = targetPos.absoluteX + targetPos.width / 2;
        const endY = targetPos.absoluteY + targetPos.height / 2;

        const newAnimation = {
          id: animationId,
          value: animationData.source_value,
          startX: startX,
          startY: startY,
          endX: endX,
          endY: endY,
          operation: animationData.operation,
          animationType: animationData.animation_type,
          timestamp: Date.now()
        };

        console.log('🎬 [ValueAnimationOverlay] Creating animation with coordinates:', newAnimation);

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
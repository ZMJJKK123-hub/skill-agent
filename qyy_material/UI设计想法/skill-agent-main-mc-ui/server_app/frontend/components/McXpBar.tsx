"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import clsx from "clsx";

interface McXpBarProps {
  level: number;
  finished: boolean;
  running: boolean;
  onMaxLevel?: () => void;
  phaseLabels?: string[];
  activePhase?: number;
}

/** 播放MC原版经验升级音效（叮~） */
function playLevelUpSound() {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const now = ctx.currentTime;
    // 经典的双音叮叮声
    const notes = [1200, 1600];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, now + i * 0.08);
      gain.gain.setValueAtTime(0.25, now + i * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.08 + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.08);
      osc.stop(now + i * 0.08 + 0.25);
    });
    // 关闭音频上下文
    setTimeout(() => ctx.close(), 1000);
  } catch (_) {}
}

export default function McXpBar({
  level,
  finished,
  running,
  onMaxLevel,
  phaseLabels = ["思考", "执行", "生成", "附魔完成!"],
  activePhase = -1,
}: McXpBarProps) {
  const [displayLevel, setDisplayLevel] = useState(0);
  const [xpGlow, setXpGlow] = useState(false);
  const [showLevelUp, setShowLevelUp] = useState(false);
  const maxLevel = 30;
  const animFrame = useRef<number>(0);
  const prevLevel = useRef(0);
  const hasTriggeredMax = useRef(false);

  useEffect(() => {
    const target = Math.min(level, maxLevel);
    const animate = () => {
      setDisplayLevel((prev) => {
        if (prev >= target) { cancelAnimationFrame(animFrame.current); return target; }
        animFrame.current = requestAnimationFrame(animate);
        return Math.min(prev + 0.35, target);
      });
    };
    cancelAnimationFrame(animFrame.current);
    animFrame.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animFrame.current);
  }, [level, maxLevel]);

  useEffect(() => {
    const floored = Math.floor(displayLevel);
    if (floored > prevLevel.current && floored > 0) {
      setXpGlow(true);
      setShowLevelUp(true);
      playLevelUpSound();
      setTimeout(() => setXpGlow(false), 300);
      setTimeout(() => setShowLevelUp(false), 1500);
    }
    prevLevel.current = floored;
  }, [displayLevel]);

  // 达到30级时触发
  useEffect(() => {
    if (displayLevel >= maxLevel - 0.05 && !hasTriggeredMax.current && onMaxLevel) {
      hasTriggeredMax.current = true;
      onMaxLevel();
    }
  }, [displayLevel, maxLevel, onMaxLevel]);

  const fillPercent = Math.min((displayLevel / maxLevel) * 100, 100);
  const flooredLevel = Math.floor(displayLevel);
  const segments = 30;
  const filledSegments = Math.floor((displayLevel / maxLevel) * segments);
  // MC原版阶段图标：书、镐、齿轮、附魔书
  const icons = ["📖", "⛏️", "🔧", "📚"];

  // 经验值颜色：MC原版绿色系
  const xpGreen = "#55FF55";
  const xpGreenBright = "#80FF00";
  const xpGreenComplete = "#00FF00";

  return (
    <div className="relative space-y-3">
      {/* 经验条本体 */}
      <div className="relative">
        {/* 标签行：经验值 / 等级数字 */}
        <div className="mb-1.5 flex items-center justify-between">
          <span className="text-xs tracking-wider text-zinc-400"
            style={{ fontFamily: "'Minecraft', 'Courier New', monospace" }}>
            经验值
          </span>
          <div className="flex items-center gap-1.5">
            {/* 等级数字 - MC原版绿色像素风格 */}
            <span
              className={clsx(
                "text-lg font-bold tabular-nums transition-colors duration-300",
                "drop-shadow-[0_2px_0_rgba(0,0,0,0.8)]",
                finished
                  ? "text-[#00FF00] drop-shadow-[0_0_10px_rgba(0,255,0,0.7)]"
                  : xpGlow
                    ? "text-[#80FF00] drop-shadow-[0_0_8px_rgba(128,255,0,0.6)]"
                    : running
                      ? "text-[#55FF55]"
                      : "text-zinc-600"
              )}
              style={{ fontFamily: "'Minecraft', 'Courier New', monospace" }}
            >
              {flooredLevel}
            </span>
            <span
              className="text-xs text-zinc-600"
              style={{ fontFamily: "'Minecraft', 'Courier New', monospace" }}
            >
              / {maxLevel}
            </span>
          </div>
        </div>

        {/* 经验条填充区域 - MC原版黑色背景+绿色进度 */}
        <div
          className="relative h-4 overflow-hidden border-2 border-[#2a2a2a] bg-[#0d0d0d]"
          style={{
            borderImage: "linear-gradient(180deg, #373737 0%, #1a1a1a 50%, #373737 100%) 2",
            borderImageSlice: 2,
            imageRendering: "pixelated",
          }}
        >
          {/* 背景纹理：暗色条纹 */}
          <div className="absolute inset-0 bg-[repeating-linear-gradient(90deg,transparent,transparent_3px,rgba(0,0,0,0.25)_3px,rgba(0,0,0,0.25)_4px)]" />

          {/* 经验填充 - MC原版绿色渐变 */}
          <div
            className={clsx(
              "relative h-full transition-all duration-500 ease-out",
              finished
                ? "bg-gradient-to-b from-[#00FF00] via-[#33FF33] to-[#00CC00]"
                : "bg-gradient-to-b from-[#3CB043] via-[#50C878] to-[#2E8B57]"
            )}
            style={{ width: fillPercent + "%" }}
          >
            {/* 高光条纹 */}
            <div className="absolute inset-0 bg-[repeating-linear-gradient(90deg,transparent,transparent_2px,rgba(255,255,255,0.12)_2px,rgba(255,255,255,0.12)_3px)]" />
            {/* 顶部高光 */}
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-white/20" />
            {/* 分段线 */}
            {Array.from({ length: segments - 1 }).map((_, i) => (
              <div
                key={i}
                className={clsx(
                  "absolute top-0 h-full w-px transition-opacity duration-300",
                  i < filledSegments ? "opacity-100 bg-black/20" : "opacity-0"
                )}
                style={{ left: ((i + 1) / segments) * 100 + "%" }}
              />
            ))}
            {/* 闪光划过效果 */}
            {running && (
              <div className="absolute inset-0 animate-[xpShine_2s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-white/25 to-transparent" />
            )}
            {/* 完成时脉冲 */}
            {finished && (
              <div className="absolute inset-0 animate-[enchantGlow_0.5s_ease-in-out_infinite] bg-white/8" />
            )}
          </div>

          {/* 升级闪烁 */}
          {xpGlow && (
            <div className="absolute inset-0 animate-[levelUpFlash_0.3s_ease-out] bg-white/30" />
          )}
        </div>

        {/* 升级飘字 */}
        {showLevelUp && !finished && (
          <div className="absolute -top-7 right-0 pointer-events-none">
            <span
              className="text-xs font-bold animate-[fadeUp_0.3s_ease,floatAway_1.5s_ease-out_forwards]"
              style={{
                fontFamily: "'Minecraft', 'Courier New', monospace",
                color: xpGreenBright,
                textShadow: "0 0 8px rgba(128,255,0,0.8), 0 2px 0 rgba(0,0,0,0.8)",
              }}
            >
              {flooredLevel}级!
            </span>
          </div>
        )}
      </div>

      {/* 阶段指示器 */}
      <div className="flex gap-2 pt-1">
        {phaseLabels.map((label, i) => {
          const phaseDone = (finished && i <= 3) || (running && i < Math.min(activePhase + 1, 4));
          const phaseActive = running && i === activePhase;
          return (
            <div key={i} className="flex-1 text-center">
              <div
                className={clsx(
                  "mx-auto flex h-8 w-8 items-center justify-center rounded-sm text-base transition-all duration-300",
                  "border",
                  phaseActive
                    ? "scale-110 bg-[#1a3a1a] border-[#55FF55]/50 shadow-[0_0_12px_rgba(85,255,85,0.4)]"
                    : phaseDone
                      ? "bg-[#0a2a0a] border-[#2a5a2a]/30"
                      : "bg-[#111] border-[#1a1a1a] opacity-40 grayscale"
                )}
                style={{ imageRendering: "pixelated" }}
              >
                {icons[i]}
              </div>
              <span
                className={clsx(
                  "mt-1 block text-[10px] transition-colors duration-300 font-bold",
                  phaseActive
                    ? "text-[#55FF55] drop-shadow-[0_0_4px_rgba(85,255,85,0.5)]"
                    : phaseDone
                      ? "text-[#3a7a3a]"
                      : "text-zinc-700"
                )}
                style={{ fontFamily: "'Minecraft', 'Courier New', monospace" }}
              >
                {phaseDone ? "§a✓" : phaseActive ? "§e⚡" : "§7○"} {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

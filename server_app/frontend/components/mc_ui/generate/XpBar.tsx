/**
 * XpBar —— MC 原版经验条板块。
 * 轨道 #262846 + 4px 暗条纹 + 渐变填充 + 29 分段线 + 闪光 + 升级闪烁/飘字。
 * 经验值跨整数时由父组件调用 playMcLevelUp（本组件只负责视觉闪光与飘字）。
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { MC, MAX_XP } from "./mcTheme";

interface XpBarProps {
  /** 当前经验值（0-30，浮点小数表示进度） */
  level: number;
  /** 是否已完成（完成态绿光更强） */
  finished: boolean;
  /** 是否运行中（运行中显示闪光） */
  running: boolean;
}

const SEGMENTS = Array.from({ length: MAX_XP - 1 }, (_, i) => i + 1);

function formatSegLeft(i: number): string {
  return `${(i / MAX_XP) * 100}%`;
}

export default function XpBar({ level, finished, running }: XpBarProps) {
  const [flash, setFlash] = useState(false);
  const [pop, setPop] = useState<string | null>(null);
  const prevFloor = useRef(0);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  useEffect(() => {
    const floor = Math.floor(level);
    if (floor > prevFloor.current && floor > 0) {
      // 升级：白闪 + 飘字
      setFlash(true);
      setPop(`${floor}级!`);
      timers.current.push(
        setTimeout(() => setFlash(false), 350),
        setTimeout(() => setPop(null), 1400)
      );
    }
    prevFloor.current = floor;
  }, [level]);

  useEffect(() => {
    return () => timers.current.forEach(clearTimeout);
  }, []);

  const pct = Math.min((level / MAX_XP) * 100, 100);
  const floor = Math.floor(level);

  return (
    <div
      className="relative flex flex-col gap-1.5 p-2.5"
      style={{ background: "rgba(0,0,0,0.6)", border: "2px solid #373737" }}
    >
      {/* 标签行：经验值 + 等级 */}
      <div className="flex items-center justify-between">
        <span style={{ fontSize: 11, color: "#A0A0A0", textShadow: "0 1px 0 rgba(0,0,0,0.9)" }}>
          经验值
        </span>
        <div className="flex items-baseline gap-1">
          <span
            className={finished ? "mc-xp-finished" : undefined}
            style={{
              fontSize: 20,
              fontWeight: 700,
              color: MC.XP_TOP,
              textShadow: finished
                ? "0 2px 0 #000, 0 0 10px rgba(126,252,32,.8), 0 0 20px rgba(126,252,32,.4)"
                : "0 2px 0 #000, 0 0 3px #3A7A0A",
              transition: "color .3s",
            }}
          >
            {floor}
          </span>
          <span style={{ fontSize: 12, color: "#606060" }}>/ {MAX_XP}</span>
        </div>
      </div>

      {/* 轨道 */}
      <div
        className="relative h-4 overflow-hidden"
        style={{ background: MC.XP_TRACK, border: `2px solid ${MC.XP_TRACK_BORDER}` }}
      >
        {/* 4px 暗条纹背景 */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            backgroundImage:
              "repeating-linear-gradient(90deg, transparent 0px, transparent 3px, rgba(0,0,0,0.35) 3px, rgba(0,0,0,0.35) 4px)",
          }}
        />
        {/* 填充 */}
        <div
          className="relative h-full transition-[width] duration-500 ease-out"
          style={{
            width: `${pct}%`,
            background: finished
              ? "linear-gradient(180deg,#7EFC20 0%,#7EFC20 15%,#6FD81A 40%,#4C9813 65%,#3A7A0A 100%)"
              : "linear-gradient(180deg,#7EFC20 0%,#7EFC20 18%,#62C419 30%,#4C9813 55%,#436924 80%,#223D22 100%)",
            boxShadow: finished ? "0 0 10px rgba(126,252,32,0.3)" : undefined,
          }}
        >
          {/* 顶部高光 */}
          <div
            className="pointer-events-none absolute left-0 right-0 top-0 h-[3px]"
            style={{ background: "rgba(255,255,255,0.18)" }}
          />
        </div>
        {/* 闪光 */}
        {running && !finished && (
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 35%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.08) 65%, transparent 100%)",
              animation: "mcXpShine 2.5s ease-in-out infinite",
            }}
          />
        )}
        {/* 分段线 */}
        {SEGMENTS.map((i) => (
          <span
            key={i}
            className="pointer-events-none absolute top-0 h-full w-px"
            style={{ left: formatSegLeft(i), background: "rgba(0,0,0,0.25)" }}
          />
        ))}
        {/* 升级白闪 */}
        {flash && (
          <div
            className="pointer-events-none absolute inset-0"
            style={{ background: "rgba(255,255,255,0.4)", animation: "mcFlashOut 0.35s ease-out forwards" }}
          />
        )}
      </div>

      {/* 升级飘字 */}
      {pop && (
        <div
          className="pointer-events-none absolute -top-7 right-0"
          style={{ animation: "mcPopUp 1.4s ease-out forwards" }}
        >
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: MC.XP_TOP,
              textShadow: "0 2px 0 #000, 0 0 8px rgba(126,252,32,0.8)",
            }}
          >
            {pop}
          </span>
        </div>
      )}
    </div>
  );
}
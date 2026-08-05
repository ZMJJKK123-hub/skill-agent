/**
 * PhaseIndicator —— MC 原版四阶段指示器。
 * 思考📖 → 执行⛏️ → 生成🔧 → 附魔完成📚，active/done 状态着色。
 */
"use client";

import { PHASES, MC } from "./mcTheme";

interface PhaseIndicatorProps {
  /** 当前活动阶段索引（0-3）；<= index 且已完成时显示 done */
  active: number;
  /** 是否运行中（-1 = 未开始） */
  running: boolean;
  /** 是否已完成（全部阶段点亮 done） */
  finished: boolean;
}

export default function PhaseIndicator({ active, running, finished }: PhaseIndicatorProps) {
  return (
    <div className="flex gap-1.5">
      {PHASES.map((p, i) => {
        const done = finished || (running && i < active);
        const isActive = !finished && running && i === active;
        const style: React.CSSProperties = {
          flex: 1,
          textAlign: "center",
          padding: "8px 4px",
          border: "2px solid #1A1C33",
          background: "#262846",
          transition: "all .3s",
        };
        if (isActive) {
          style.borderColor = MC.XP_TOP;
          style.background = "#1A2A10";
          style.boxShadow = "0 0 6px rgba(126,252,32,0.3)";
        } else if (done) {
          style.borderColor = "#2A4A1A";
          style.background = "#0F1F0A";
        }
        return (
          <div key={i} style={style}>
            <span style={{ fontSize: 24, display: "block" }}>
              {isActive ? "⚡" : done ? "✓" : "○"}
            </span>
            <span
              style={{
                fontSize: 12,
                fontWeight: 700,
                marginTop: 4,
                display: "block",
                color: isActive ? MC.XP_TOP : done ? "#4A8A2A" : "#606060",
              }}
            >
              {p.icon} {p.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
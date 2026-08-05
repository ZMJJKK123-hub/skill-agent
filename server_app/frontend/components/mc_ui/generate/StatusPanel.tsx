/**
 * StatusPanel —— 左面板统计板块。
 * MC 原版 stat-card：状态 / 已用时间 / 产物统计 + MC 3D 凸起按钮（下载/重新生成）。
 */
"use client";

import { MC } from "./mcTheme";

interface StatusPanelProps {
  statusText: string;
  elapsedText: string;
  fileSummary: string;
  finished: boolean;
  onDownload: () => void;
  onRegenerate: () => void;
}

/** MC 3D 凸起按钮样式（border-image 渐变模拟原版按钮） */
const btnBase: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 4,
  padding: "5px 14px",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 11,
  fontWeight: 700,
  border: "2px solid #000",
  borderBottom: "3px solid #000",
  textShadow: "0 1px 0 rgba(255,255,255,0.3)",
  transition: "0.05s",
  imageRendering: "pixelated",
};

function StatCard({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ padding: "6px 8px", background: MC.CARD_BG, border: `2px solid ${MC.CARD_BORDER}` }}>
      <div style={{ fontSize: 9, color: MC.LABEL }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 700, color: MC.XP_TOP, marginTop: 2 }}>{children}</div>
    </div>
  );
}

export default function StatusPanel({
  statusText,
  elapsedText,
  fileSummary,
  finished,
  onDownload,
  onRegenerate,
}: StatusPanelProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {/* 双列 stat-card：状态 / 已用时间 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
        <StatCard label="状态">{statusText}</StatCard>
        <StatCard label="已用时间">{elapsedText}</StatCard>
      </div>

      {/* 产物统计 */}
      <div style={{ padding: "6px 8px", background: MC.CARD_BG, border: `2px solid ${MC.CARD_BORDER}` }}>
        <div style={{ fontSize: 9, color: MC.LABEL }}>产物统计</div>
        <div style={{ fontSize: 11, color: MC.TEXT, marginTop: 2 }}>{fileSummary}</div>
      </div>

      {/* 操作按钮 */}
      <div style={{ display: "flex", gap: 6 }}>
        <button
          onClick={onDownload}
          disabled={!finished}
          style={{
            ...btnBase,
            background: MC.BTN_LIGHT,
            color: "#3F3F3F",
            borderImage: MC.BTN_BORDER,
            opacity: finished ? 1 : 0.4,
            cursor: finished ? "pointer" : "default",
          }}
        >
          ⬇ 下载mod
        </button>
        <button
          onClick={onRegenerate}
          style={{
            ...btnBase,
            background: MC.BTN_DARK,
            color: MC.TEXT,
            borderImage: MC.BTN_BORDER,
            textShadow: "0 1px 0 rgba(0,0,0,0.8)",
          }}
        >
          🔄 重新生成
        </button>
      </div>
    </div>
  );
}
/**
 * StatusPanel —— 左面板统计板块。
 * MC 原版 stat-card：状态 / 已用时间 / 产物统计 + MC 3D 凸起按钮（下载/重新生成）。
 */
"use client";

import { useState } from "react";
import { MC } from "./mcTheme";

interface StatusPanelProps {
  statusText: string;
  elapsedText: string;
  fileSummary: string;
  finished: boolean;
  /** 是否已打包出 jar（服务端检测） */
  hasJar: boolean;
  onDownload: () => void;
  onDownloadJar: () => void;
  onRegenerate: () => void;
}

/** MC 3D 凸起按钮样式（border-image 渐变模拟原版按钮） */
const btnBase: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 6,
  padding: "8px 16px",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 700,
  border: "2px solid #000",
  borderBottom: "3px solid #000",
  textShadow: "0 1px 0 rgba(255,255,255,0.3)",
  transition: "0.05s",
  imageRendering: "pixelated",
};

function StatCard({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ padding: "8px 10px", background: MC.CARD_BG, border: `2px solid ${MC.CARD_BORDER}` }}>
      <div style={{ fontSize: 11, color: MC.LABEL }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700, color: MC.XP_TOP, marginTop: 4 }}>{children}</div>
    </div>
  );
}

export default function StatusPanel({
  statusText,
  elapsedText,
  fileSummary,
  finished,
  hasJar,
  onDownload,
  onDownloadJar,
  onRegenerate,
}: StatusPanelProps) {
  // jar 打包状态文本（finished 前视为进行中）
  const jarStatus = !finished ? "打包中..." : hasJar ? "✓ 已打包" : "未打包";
  const jarColor = !finished ? "#A0A0A0" : hasJar ? MC.XP_TOP : "#A0A0A0";
  // 下载进行中标记：防止用户长时间无反馈而重复点击（后端首次打包 11MB 需数秒）
  const [busy, setBusy] = useState<null | "zip" | "jar">(null);

  const handleZip = async () => {
    if (busy) return;
    setBusy("zip");
    try {
      await onDownload();
    } finally {
      setBusy(null);
    }
  };
  const handleJar = async () => {
    if (busy) return;
    setBusy("jar");
    try {
      await onDownloadJar();
    } finally {
      setBusy(null);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {/* 双列 stat-card：状态 / 已用时间 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        <StatCard label="状态">{statusText}</StatCard>
        <StatCard label="已用时间">{elapsedText}</StatCard>
      </div>

      {/* 产物统计 */}
      <div style={{ padding: "8px 10px", background: MC.CARD_BG, border: `2px solid ${MC.CARD_BORDER}` }}>
        <div style={{ fontSize: 11, color: MC.LABEL }}>产物统计</div>
        <div style={{ fontSize: 14, color: MC.TEXT, marginTop: 4 }}>{fileSummary}</div>
      </div>

      {/* jar 打包状态 */}
      <div style={{ padding: "8px 10px", background: MC.CARD_BG, border: `2px solid ${MC.CARD_BORDER}` }}>
        <div style={{ fontSize: 11, color: MC.LABEL }}>jar 打包</div>
        <div style={{ fontSize: 14, fontWeight: 700, color: jarColor, marginTop: 4 }}>
          {jarStatus}
        </div>
      </div>

      {/* 操作按钮：源码 zip + jar + 重新生成 */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          onClick={handleZip}
          disabled={!finished || busy !== null}
          title={
            finished
              ? "源码工程（Java + Gradle 配置 + 资源）。可自行修改后用 gradlew build 重新构建。本包不包含已编译的 jar，需自行构建。"
              : "生成完成后可下载源码工程"
          }
          style={{
            ...btnBase,
            background: MC.BTN_LIGHT,
            color: "#3F3F3F",
            borderImage: MC.BTN_BORDER,
            opacity: finished && busy === null ? 1 : 0.4,
            cursor: finished && busy === null ? "pointer" : "default",
          }}
        >
          {busy === "zip" ? "打包中…" : "⬇ 源码 zip"}
        </button>
        <button
          onClick={handleJar}
          disabled={!finished || !hasJar || busy !== null}
          title={
            finished && hasJar
              ? "已编译打包的可安装模组。直接放入游戏的 mods 文件夹即可使用，无需构建。"
              : finished
                ? "尚未打包出 jar（构建失败或未构建）"
                : "生成并打包完成后可下载"
          }
          style={{
            ...btnBase,
            background: MC.BTN_LIGHT,
            color: "#3F3F3F",
            borderImage: MC.BTN_BORDER,
            opacity: finished && hasJar && busy === null ? 1 : 0.4,
            cursor: finished && hasJar && busy === null ? "pointer" : "default",
          }}
        >
          {busy === "jar" ? "下载中…" : "⬇ 下载 jar"}
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
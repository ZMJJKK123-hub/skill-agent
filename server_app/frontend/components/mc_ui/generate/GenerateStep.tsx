/**
 * GenerateStep —— MC 原版复古像素风任务生成页容器。
 *
 * 组装：左面板（XpBar 经验条 + PhaseIndicator 阶段 + StatusPanel 统计）
 *       + 右终端（McTerminal 智能体工作台）+ 附魔完成遮罩（EnchantOverlay）+ 产物浏览器。
 *
 * 数据接入：真实轮询事件 / 会话状态 / 文件统计；
 *   - 经验值 = 事件数映射 0→29.5（实时进度），finished 升满 30
 *   - 升级跨整数 → playMcLevelUp；running→finished 自然完成 → 附魔动画 + 附魔音效
 *   - 复用历史会话（hydrate 的 finished）不自动播放附魔
 */
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { MC_ANIMATION_CSS } from "./mcTheme";
import { playMcLevelUp, primeAudio } from "./mcSfx";
import XpBar from "./XpBar";
import PhaseIndicator from "./PhaseIndicator";
import StatusPanel from "./StatusPanel";
import McTerminal from "./McTerminal";
import EnchantOverlay from "./EnchantOverlay";
import ArtifactExplorer from "../../common_ui/ArtifactExplorer";
import { downloadSession } from "../../../lib/api";
import type { AgentEvent, SessionStats } from "../../../lib/types";

interface GenerateStepProps {
  sessionId: string;
  game: string;
  prompt: string;
  events: AgentEvent[];
  status: SessionStats | null;
  running: boolean;
  finished: boolean;
  onHome: () => void;
  onRegenerate: () => void;
}

function formatDuration(totalSeconds: number | null | undefined): string {
  const s = Math.max(0, Math.floor(totalSeconds || 0));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}

function formatBytes(n: number | null | undefined): string {
  if (n == null) return "-";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

/**
 * 由事件流推导当前阶段（0 思考 / 1 执行 / 2 生成 / 3 完成）。
 * 有 thinking → 0；有 tool_call → 1；事件数超过"足够多" → 2。
 */
function derivePhase(events: AgentEvent[], finished: boolean): number {
  if (finished) return 3;
  const hasTool = events.some((e) => e.type === "tool_call");
  if (!hasTool) return 0;
  if (events.length > 12) return 2;
  return 1;
}

export default function GenerateStep({
  sessionId,
  game,
  prompt,
  events,
  status,
  running,
  finished,
  onHome,
  onRegenerate,
}: GenerateStepProps) {
  /** 经验值（0-30，浮点表示进度） */
  const [xpLevel, setXpLevel] = useState(0);
  /** 附魔遮罩显示开关（仅本次自然完成触发） */
  const [enchantOpen, setEnchantOpen] = useState(false);
  const prevFinished = useRef(false);
  const prevFloor = useRef(0);

  // 经验值推进：事件增长 → 进度增长；完成 → 升满 30
  useEffect(() => {
    if (finished) {
      setXpLevel((v) => (v >= 30 ? 30 : Math.min(30, v + 0.5)));
      return;
    }
    const target = Math.min(events.length / 3, 29.5);
    // 平滑逼近 target（每 800ms 轮询一次，逐步靠拢）
    setXpLevel((v) => {
      const d = target - v;
      if (Math.abs(d) < 0.05) return target;
      return v + Math.sign(d) * 0.6;
    });
  }, [events.length, finished]);

  // 升级音效：跨整数
  useEffect(() => {
    const floor = Math.floor(xpLevel);
    if (floor > prevFloor.current && floor > 0) {
      playMcLevelUp();
    }
    prevFloor.current = floor;
  }, [xpLevel]);

  // 附魔动画：仅本次自然完成（running→finished）触发
  useEffect(() => {
    if (finished && !prevFinished.current) {
      const t = setTimeout(() => setEnchantOpen(true), 500);
      return () => clearTimeout(t);
    }
    prevFinished.current = finished;
  }, [finished]);

  // 首次交互预热音频（解锁 AudioContext）
  const handleDownload = useCallback(() => {
    primeAudio();
    if (!finished) return;
    downloadSession(sessionId).catch(() => undefined);
  }, [finished, sessionId]);

  const handleRegenerateClick = useCallback(() => {
    primeAudio();
    setEnchantOpen(false);
    onRegenerate();
  }, [onRegenerate]);

  const phase = derivePhase(events, finished);
  const statusText = finished ? "已完成" : running ? "生成中" : "等待中";
  const elapsedText = formatDuration(status?.elapsed);
  const fileSummary =
    status?.file_count != null && status.file_count > 0
      ? `${status.file_count} 个文件 · ${formatBytes(status.total_bytes)}`
      : "尚无文件";

  return (
    <div
      className="relative font-mono"
      style={{ background: "#0D0D0D", color: "#BFBFBF", imageRendering: "pixelated" }}
    >
      {/* 注入 MC 复杂 3D / 关键帧动画（Tailwind 盲区解决方案） */}
      <style>{MC_ANIMATION_CSS}</style>

      {/* 附魔完成遮罩 */}
      {enchantOpen && (
        <EnchantOverlay prompt={prompt || "(无需求记录)"} onComplete={() => setEnchantOpen(false)} />
      )}

      {/* 控制条：返回首页 + 会话 ID */}
      <div
        className="mb-3.5 flex items-center gap-2.5 px-3 py-2"
        style={{ background: "#262846", border: "2px solid #1A1C33" }}
      >
        <button
          onClick={onHome}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            padding: "5px 14px",
            cursor: "pointer",
            fontFamily: "inherit",
            fontSize: 11,
            fontWeight: 700,
            background: "#7EFC20",
            color: "#000",
            border: "2px solid #4A9810",
            textShadow: "0 1px 0 rgba(255,255,255,0.2)",
            transition: "0.05s",
          }}
        >
          ◀ 返回首页
        </button>
        <span className="ml-auto" style={{ fontSize: 10, color: "#808090" }}>
          {game} · {sessionId}
        </span>
      </div>

      {/* 双栏：左面板 / 右终端 */}
      <div className="grid gap-3.5" style={{ gridTemplateColumns: "340px 1fr" }}>
        {/* 左面板 */}
        <div style={{ background: "rgba(0,0,0,0.75)", border: "2px solid #373737" }}>
          <div
            className="flex items-center px-2.5 py-1.5"
            style={{ background: "rgba(0,0,0,0.5)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}
          >
            <span style={{ fontSize: 12, fontWeight: 700 }}>生成状态</span>
            <span className="ml-auto" style={{ fontSize: 9, color: "#808090" }}>
              {game}
            </span>
          </div>
          <div className="flex flex-col gap-2 p-2.5">
            <XpBar level={xpLevel} finished={finished} running={running} />
            <PhaseIndicator active={phase} running={running} finished={finished} />
            <StatusPanel
              statusText={statusText}
              elapsedText={elapsedText}
              fileSummary={fileSummary}
              finished={finished}
              onDownload={handleDownload}
              onRegenerate={handleRegenerateClick}
            />
          </div>
        </div>

        {/* 右终端 */}
        <McTerminal events={events} loading={running} />
      </div>

      {/* 产物浏览器（完成后展示） */}
      {finished && <div className="mt-3.5">{/* 复用现有 ArtifactExplorer 保留 VS Code 文件树能力 */}
        <ArtifactExplorer sessionId={sessionId} />
      </div>}
    </div>
  );
}
/**
 * GenerateStep —— MC 原版复古像素风任务生成页容器。
 *
 * 组装：左面板（XpBar 经验条 + PhaseIndicator 阶段 + StatusPanel 统计）
 *       + 右终端（McTerminal 智能体工作台）+ 附魔完成遮罩（EnchantOverlay）+ 产物浏览器。
 *
 * 数据接入：真实轮询事件 / 会话状态 / 文件统计；
 *   - 经验值：running 固定速率增长 0→29.5，自然完成补满 30，复用历史会话直接满条
 *   - 升级到 5 的倍数（精确每 5 级）→ playMcLevelUp 升级音效
 *   - 附魔/旋转动画已停用（任务完成不再播特殊动画，2026-08-06，见下方注释）
 */
"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { MC_ANIMATION_CSS } from "./mcTheme";
import { playMcLevelUp, playMcCompleteSound, primeAudio } from "./mcSfx";
import XpBar from "./XpBar";
import PhaseIndicator from "./PhaseIndicator";
import StatusPanel from "./StatusPanel";
import McTerminal from "./McTerminal";
import EnchantOverlay from "./EnchantOverlay";
import ArtifactExplorer from "../../common_ui/ArtifactExplorer";
import { downloadSession, downloadJar } from "../../../lib/api";
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
  /** 是否曾见过 running 状态：历史已完成会话复用（从未 running）不触发附魔 */
  const sawRunning = useRef(false);
  /** 升级音效许可：仅真正自然运行（running）期间开启，复用/回放绝不响 */
  const xpSoundEnabled = useRef(false);

  // 经验值推进：
  //   - running（生成中）：固定速率平滑增长（800ms +0.3，封顶 29.5），与事件数无关
  //   - finished 且本次自然完成过（sawRunning）：补满到 30
  //   - finished 但从未 running（复用历史已完成会话）：直接满条 30，不再从 0 重爬
  useEffect(() => {
    if (running) {
      sawRunning.current = true;
      xpSoundEnabled.current = true;
    }

    if (finished && !sawRunning.current) {
      // 复用历史已完成会话：静默满条，不触发升级音效
      setXpLevel(30);
      return;
    }
    if (running && !finished) {
      const id = setInterval(() => {
        setXpLevel((v) => (v >= 29.5 ? 29.5 : v + 0.3));
      }, 800);
      return () => clearInterval(id);
    }
    if (finished) {
      setXpLevel((v) => (v >= 30 ? 30 : Math.min(30, v + 0.5)));
      return;
    }
  }, [running, finished]);

  // 升级音效：仅自然运行期间（xpSoundEnabled）跨到 5 的倍数等级时触发（精确每 5 级一响）；
  // 复用历史会话 / 从历史回工作台（从未 running）绝不响
  useEffect(() => {
    const floor = Math.floor(xpLevel);
    if (
      xpSoundEnabled.current &&
      floor > prevFloor.current &&
      floor > 0 &&
      floor % 5 === 0
    ) {
      playMcLevelUp();
    }
    prevFloor.current = floor;
  }, [xpLevel]);

  // ── 附魔/旋转动画：已按需求停用（2026-08-06）──
  // 任务完成成功后不再弹出附魔书等特殊动画，直接静态展示产物。
  // 如需恢复，取消注释下面 useEffect 与 JSX 中的 <EnchantOverlay> 即可：
  // useEffect(() => {
  //   if (finished && !prevFinished.current) {
  //     if (sawRunning.current) {
  //       const t = setTimeout(() => setEnchantOpen(true), 500);
  //       return () => clearTimeout(t);
  //     }
  //   }
  //   prevFinished.current = finished;
  // }, [finished]);

  // 任务完成音效：本次自然生成完成（running→finished）时播放一次 mc_complete.mp3；
  // 复用历史已完成会话（从未 running）不播；prevFinished 保证只响一次
  useEffect(() => {
    if (finished && !prevFinished.current && sawRunning.current) {
      playMcCompleteSound();
    }
    prevFinished.current = finished;
  }, [finished]);

  // 首次交互预热音频（解锁 AudioContext）
  const handleDownload = useCallback(() => {
    primeAudio();
    if (!finished) return;
    downloadSession(sessionId).catch(() => undefined);
  }, [finished, sessionId]);

  const handleDownloadJar = useCallback(() => {
    primeAudio();
    downloadJar(sessionId).catch(() => undefined);
  }, [sessionId]);

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

      {/* 附魔完成遮罩（已停用，见上方 useEffect 注释说明） */}
      {/* {enchantOpen && (
        <EnchantOverlay prompt={prompt || "(无需求记录)"} onComplete={() => setEnchantOpen(false)} />
      )} */}

      {/* 控制条：返回首页 + 会话 ID */}
      <div
        className="mb-4 flex items-center gap-3 px-3 py-2.5"
        style={{ background: "#262846", border: "2px solid #1A1C33" }}
      >
        <button
          onClick={onHome}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            padding: "8px 16px",
            cursor: "pointer",
            fontFamily: "inherit",
            fontSize: 14,
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
        <span className="ml-auto" style={{ fontSize: 13, color: "#808090" }}>
          {game} · {sessionId}
        </span>
      </div>

      {/* 双栏：左面板 / 右终端 */}
      <div className="grid gap-4" style={{ gridTemplateColumns: "440px 1fr" }}>
        {/* 左面板 */}
        <div style={{ background: "rgba(0,0,0,0.75)", border: "2px solid #373737" }}>
          <div
            className="flex items-center px-3 py-2"
            style={{ background: "rgba(0,0,0,0.5)", borderBottom: "1px solid rgba(255,255,255,0.05)" }}
          >
            <span style={{ fontSize: 15, fontWeight: 700 }}>生成状态</span>
            <span className="ml-auto" style={{ fontSize: 12, color: "#808090" }}>
              {game}
            </span>
          </div>
          <div className="flex flex-col gap-2.5 p-3">
            <XpBar level={xpLevel} finished={finished} running={running} />
            <PhaseIndicator active={phase} running={running} finished={finished} />
            <StatusPanel
              statusText={statusText}
              elapsedText={elapsedText}
              fileSummary={fileSummary}
              finished={finished}
              hasJar={status?.has_jar ?? false}
              onDownload={handleDownload}
              onDownloadJar={handleDownloadJar}
              onRegenerate={handleRegenerateClick}
            />
          </div>
        </div>

        {/* 右终端 */}
        <McTerminal events={events} loading={running} />
      </div>

      {/* 产物浏览器（完成后展示） */}
      {finished && <div className="mt-4">{/* 复用现有 ArtifactExplorer 保留 VS Code 文件树能力 */}
        <ArtifactExplorer sessionId={sessionId} />
      </div>}
    </div>
  );
}
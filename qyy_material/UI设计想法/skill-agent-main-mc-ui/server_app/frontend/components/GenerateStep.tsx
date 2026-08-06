"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Download, Home, RefreshCcw } from "lucide-react";
import clsx from "clsx";
import EventTimeline from "./EventTimeline";
import ArtifactExplorer from "./ArtifactExplorer";
import McXpBar from "./McXpBar";
import McEnchantAnimation from "./McEnchantAnimation";
import { downloadSession } from "../lib/api";
import type { AgentEvent, SessionStats } from "../lib/types";

interface GenerateStepProps {
  sessionId: string;
  game: string;
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

/** 根据事件类型推断当前阶段 */
function detectActivePhase(events: AgentEvent[]): number {
  if (events.length === 0) return 0;
  const last = events[events.length - 1];
  switch (last.type) {
    case "thinking":
      return 0;
    case "tool_call":
      return 1;
    case "todo":
    case "round":
      return 2;
    default:
      return 2;
  }
}

/** 根据事件流计算经验等级(0-30) */
function calcXpLevel(
  events: AgentEvent[],
  elapsed: number | null,
  finished: boolean,
  fileCount: number | null
): number {
  if (finished) return 30;
  if (!events || events.length === 0) return 0;

  // 综合考虑事件数量、耗时和文件数
  const eventScore = Math.min(events.length / 80, 0.8); // 最多80个事件占80%权重
  const timeScore = elapsed ? Math.min(elapsed / 300, 0.15) : 0; // 5分钟占15%
  const fileScore = fileCount ? Math.min(fileCount / 50, 0.05) : 0; // 50个文件占5%

  const rawLevel = (eventScore * 0.65 + timeScore * 0.25 + fileScore * 0.1) * 30;
  return Math.min(Math.floor(rawLevel * 10) / 10, 29.5);
}

export default function GenerateStep({
  sessionId,
  game,
  events,
  status,
  running,
  finished,
  onHome,
  onRegenerate,
}: GenerateStepProps) {
  const elapsed =
    status?.elapsed ??
    (status?.started_at
      ? Math.floor((Date.now() - status.started_at * 1000) / 1000)
      : null);

  // 附魔动画状态
  const [showEnchant, setShowEnchant] = useState(false);
  const [enchantDone, setEnchantDone] = useState(false);
  const [promptForBook, setPromptForBook] = useState("");

  // 获取提示词（从第一个thinking事件中提取）
  const lastPromptRef = useRef("");
  useEffect(() => {
    const thinkingEvents = events.filter((e) => e.type === "thinking");
    if (thinkingEvents.length > 0) {
      const content = thinkingEvents[0].content || "";
      if (content && content !== lastPromptRef.current) {
        lastPromptRef.current = content;
        setPromptForBook(content.slice(0, 80));
      }
    }
  }, [events]);

  // 计算当前经验等级
  const xpLevel = calcXpLevel(events, elapsed, finished, status?.file_count ?? null);
  const activePhase = detectActivePhase(events);

  // 达到30级触发附魔动画
  const handleMaxLevel = useCallback(() => {
    if (!finished && running) {
      setShowEnchant(true);
    }
  }, [finished, running]);

  const handleEnchantComplete = useCallback(() => {
    setEnchantDone(true);
    setShowEnchant(false);
  }, []);

  const phaseLabels = ["思考", "执行", "生成", "附魔完成!"];
  const mcFont = { fontFamily: "'Minecraft', 'Courier New', monospace" };

  return (
    <div className="space-y-5">
      {/* 附魔动画遮罩 */}
      <McEnchantAnimation
        trigger={showEnchant && !enchantDone}
        onComplete={handleEnchantComplete}
        promptText={promptForBook || "请帮我生成一个Mod..."}
      />

      {/* 返回首页 */}
      <div className="flex items-center justify-between">
        <button onClick={onHome} className="btn-ghost !py-1.5">
          <Home size={14} />
          返回首页
        </button>
        <span className="font-mono text-xs text-zinc-600">{sessionId}</span>
      </div>

      {/* IDE 分屏 */}
      <div className="grid gap-5 lg:grid-cols-[340px_1fr]">
        {/* 左：MC风格仪表盘 */}
        <div className="glass overflow-hidden">
          {/* 标题栏 - MC风格 */}
          <div
            className="flex items-center gap-2 border-b border-white/5 px-4 py-2.5"
            style={{ background: "rgba(0,0,0,0.3)" }}
          >
            <span className="text-sm font-bold text-[#BFBFBF]" style={mcFont}>
              生成状态
            </span>
            <span className="ml-auto text-xs text-zinc-500" style={mcFont}>
              {game}
            </span>
          </div>
          <div className="space-y-4 p-4">
            {/* MC经验条 */}
            <McXpBar
              level={xpLevel}
              finished={finished}
              running={running}
              onMaxLevel={handleMaxLevel}
              phaseLabels={phaseLabels}
              activePhase={activePhase}
            />

            {/* 分隔线 */}
            <div className="h-px bg-white/5" />

            {/* 状态与时间 */}
            <div className="grid grid-cols-2 gap-3">
              <div
                className="rounded border border-[#373737] p-3"
                style={{ background: "rgba(0,0,0,0.4)", imageRendering: "pixelated" }}
              >
                <div className="text-[10px] tracking-wider text-zinc-500" style={mcFont}>
                  状态
                </div>
                <div
                  className={clsx(
                    "mt-1 text-lg font-bold",
                    finished
                      ? "text-[#00FF00] drop-shadow-[0_0_6px_rgba(0,255,0,0.5)]"
                      : running
                        ? "animate-pulseSoft text-[#55FF55]"
                        : "text-zinc-400"
                  )}
                  style={mcFont}
                >
                  {finished ? "已完成" : running ? "生成中" : "等待中"}
                </div>
              </div>
              <div
                className="rounded border border-[#373737] p-3"
                style={{ background: "rgba(0,0,0,0.4)", imageRendering: "pixelated" }}
              >
                <div className="text-[10px] tracking-wider text-zinc-500" style={mcFont}>
                  已用时间
                </div>
                <div className="mt-1 text-lg font-bold text-[#55FF55]" style={mcFont}>
                  {formatDuration(elapsed)}
                </div>
              </div>
            </div>

            {/* 产物统计 */}
            <div
              className="rounded border border-[#373737] p-3"
              style={{ background: "rgba(0,0,0,0.4)", imageRendering: "pixelated" }}
            >
              <div className="text-[10px] tracking-wider text-zinc-500" style={mcFont}>
                产物统计
              </div>
              <div className="mt-1 text-sm text-zinc-300" style={mcFont}>
                {status?.file_count != null
                  ? `${status.file_count} 个文件 · ${formatBytes(status.total_bytes)}`
                  : "尚无文件"}
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-2 pt-1">
              <button
                onClick={() => {
                  if (!finished) return;
                  downloadSession(sessionId).catch(() => undefined);
                }}
                className={clsx(
                  "btn-primary flex-1",
                  !finished && "pointer-events-none opacity-40"
                )}
                style={mcFont}
              >
                <Download size={15} />
                下载 mod.zip
              </button>
              <button onClick={onRegenerate} className="btn-ghost" style={mcFont}>
                <RefreshCcw size={14} />
                重新生成
              </button>
            </div>
          </div>
        </div>

        {/* 右：MC风格终端工作台 */}
        <div
          className="overflow-hidden rounded-xl border border-white/10"
          style={{ background: "#0d0d0d" }}
        >
          <div
            className="flex items-center gap-3 border-b border-white/5 px-4 py-2.5"
            style={{ background: "#151515" }}
          >
            <span className="text-sm font-bold text-[#BFBFBF]" style={mcFont}>
              智能体工作台
            </span>
            <span className="ml-auto text-[11px] text-zinc-600" style={mcFont}>
              {events.length} 事件
            </span>
          </div>
          <div className="terminal-scroll max-h-[520px] overflow-y-auto">
            <EventTimeline events={events} loading={running} />
          </div>
        </div>
      </div>

      {/* 产物浏览器 */}
      {finished && <ArtifactExplorer sessionId={sessionId} />}
    </div>
  );
}

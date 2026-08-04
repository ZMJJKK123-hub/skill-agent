"use client";

import { Download, Home, RefreshCcw } from "lucide-react";
import clsx from "clsx";
import EventTimeline from "./EventTimeline";
import ArtifactExplorer from "./ArtifactExplorer";
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

/** macOS 风格终端红绿灯 */
function TrafficLights() {
  return (
    <div className="flex gap-1.5">
      <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
      <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
      <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
    </div>
  );
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

  return (
    <div className="space-y-5">
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
        {/* 左：仪表盘 */}
        <div className="glass overflow-hidden">
          <div className="flex items-center gap-2 border-b border-white/5 px-4 py-2.5">
            <span className="text-sm font-semibold text-zinc-200">生成状态</span>
            <span className="ml-auto text-xs text-zinc-500">{game}</span>
          </div>
          <div className="space-y-4 p-4">
            {/* 状态与时间两个数码管卡片 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-white/5 bg-ink-950/60 p-3">
                <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                  状态
                </div>
                <div
                  className={clsx(
                    "mt-1 font-mono text-xl font-bold",
                    finished
                      ? "text-forge-emerald"
                      : running
                        ? "animate-pulseSoft text-forge-cyan"
                        : "text-zinc-400"
                  )}
                >
                  {finished ? "已完成" : running ? "生成中" : "等待中"}
                </div>
              </div>
              <div className="rounded-xl border border-white/5 bg-ink-950/60 p-3">
                <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                  已用时间
                </div>
                <div className="mt-1 font-mono text-xl font-bold text-forge-cyan">
                  {formatDuration(elapsed)}
                </div>
              </div>
            </div>

            {/* 进度条（全局 glowPulse 动画替代 style-jsx） */}
            <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
              <div
                className={clsx(
                  "h-full rounded-full transition-all duration-500",
                  finished
                    ? "w-full bg-forge-emerald"
                    : running
                      ? "w-3/5 animate-[glowPulse_2s_ease_infinite] bg-gradient-to-r from-forge-cyan to-forge-emerald"
                      : "w-0"
                )}
              />
            </div>

            {/* 四阶段呼吸灯 */}
            <div className="flex gap-2">
              {["思考", "执行", "生成", "完成"].map((phase, i) => {
                const phaseDone = finished && i === 3;
                const phaseActive = running && i === 2;
                return (
                  <div key={phase} className="flex-1 text-center">
                    <span
                      className={clsx(
                        "mx-auto block h-2 w-2 rounded-full",
                        phaseDone
                          ? "bg-forge-emerald shadow-[0_0_8px_rgba(52,211,153,0.6)]"
                          : phaseActive
                            ? "animate-breathe bg-forge-cyan"
                            : "bg-white/10"
                      )}
                    />
                    <span
                      className={clsx(
                        "mt-1 block text-[10px]",
                        phaseDone ? "text-forge-emerald" : "text-zinc-600"
                      )}
                    >
                      {phase}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* 产物统计 */}
            <div className="rounded-xl border border-white/5 bg-ink-950/60 p-3">
              <div className="text-[10px] uppercase tracking-wider text-zinc-500">
                产物统计
              </div>
              <div className="mt-1 font-mono text-sm text-zinc-300">
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
              >
                <Download size={15} />
                下载 mod.zip
              </button>
              <button onClick={onRegenerate} className="btn-ghost">
                <RefreshCcw size={14} />
                重新生成
              </button>
            </div>
          </div>
        </div>

        {/* 右：macOS 终端式智能体工作台 */}
        <div className="overflow-hidden rounded-xl border border-white/10 bg-[#0d0d0d]">
          <div className="flex items-center gap-3 border-b border-white/5 bg-[#151515] px-4 py-2.5">
            <TrafficLights />
            <span className="mono-label">智能体工作台</span>
            <span className="ml-auto font-mono text-[11px] text-zinc-600">
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
"use client";

import { Download, Play, Trash2 } from "lucide-react";
import { loadHistory, clearHistory } from "../lib/history";
import { downloadUrl } from "../lib/api";
import type { HistoryEntry } from "../lib/types";

interface HistoryViewProps {
  onResume: (sessionId: string) => void;
  onClear: () => void;
}

function formatDuration(totalSeconds: number | null | undefined): string {
  const s = Math.max(0, Math.floor(totalSeconds || 0));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}

export default function HistoryView({ onResume, onClear }: HistoryViewProps) {
  const history: HistoryEntry[] = loadHistory();

  const handleClear = () => {
    clearHistory();
    onClear();
  };

  if (history.length === 0) {
    return (
      <div className="glass mx-auto max-w-2xl p-10 text-center">
        <p className="text-sm text-zinc-500">
          还没有历史记录。完成一次生成后，会话会出现在这里。
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-zinc-100">历史记录</h2>
        <button onClick={handleClear} className="btn-ghost !py-1.5">
          <Trash2 size={14} />
          清空
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {history.map((h) => (
          <div
            key={h.sessionId}
            className="glass group flex flex-col p-4 transition-all duration-200 hover:border-white/15 hover:shadow-glow"
          >
            {/* 顶部：游戏 + 时间 */}
            <div className="flex items-center justify-between">
              <span className="rounded-full bg-forge-purple/15 px-2 py-0.5 text-xs font-medium text-forge-purple">
                {h.game || "minecraft"}
              </span>
              <span className="mono-label">{h.date || ""}</span>
            </div>

            {/* 摘要 */}
            <p className="mt-3 line-clamp-2 min-h-[44px] flex-1 text-sm text-zinc-300">
              {h.prompt || "(无需求记录)"}
            </p>

            {/* 底部：统计 + 操作 */}
            <div className="mt-4 flex items-center justify-between">
              <div className="flex gap-3 font-mono text-[11px] text-zinc-500">
                <span>{h.elapsed != null ? formatDuration(h.elapsed) : "—"}</span>
                <span>{h.fileCount != null ? `${h.fileCount} 文件` : ""}</span>
              </div>
              <div className="flex gap-1.5">
                <a
                  href={downloadUrl(h.sessionId)}
                  target="_blank"
                  rel="noreferrer"
                  className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-zinc-400 transition-all duration-150 hover:border-forge-cyan/40 hover:text-forge-cyan"
                  title="下载"
                >
                  <Download size={14} />
                </a>
                <button
                  onClick={() => onResume(h.sessionId)}
                  className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-zinc-400 transition-all duration-150 hover:border-forge-emerald/40 hover:text-forge-emerald"
                  title="复用会话"
                >
                  <Play size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
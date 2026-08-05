"use client";

import { useEffect, useState } from "react";
import { Download, Play, Trash2 } from "lucide-react";
import { loadHistory, clearHistory } from "../../lib/history";
import { downloadSession } from "../../lib/api";
import type { HistoryEntry } from "../../lib/types";

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
  const [history, setHistory] = useState<HistoryEntry[] | null>(null);

  // 进入页面时拉取当前用户的历史（服务端）
  useEffect(() => {
    let active = true;
    loadHistory().then((list) => {
      if (active) setHistory(list);
    });
    return () => {
      active = false;
    };
  }, []);

  const handleClear = async () => {
    await clearHistory();
    setHistory([]);
    onClear();
  };

  const handleDownload = async (sessionId: string) => {
    try {
      await downloadSession(sessionId);
    } catch (err) {
      alert(err instanceof Error ? err.message : "下载失败");
    }
  };

  if (history === null) {
    return (
      <div className="glass mx-auto max-w-2xl p-10 text-center">
        <div className="flex items-center justify-center gap-2 font-mono text-sm text-zinc-600">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/10 border-t-forge-cyan" />
          加载历史记录...
        </div>
      </div>
    );
  }

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
            className="glass group flex flex-col p-4 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-500/30 hover:shadow-[0_0_15px_rgba(16,185,129,0.1)]"
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
                <button
                  onClick={() => handleDownload(h.sessionId)}
                  className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-zinc-400 transition-all duration-150 hover:border-forge-cyan/40 hover:text-forge-cyan"
                  title="下载"
                >
                  <Download size={14} />
                </button>
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
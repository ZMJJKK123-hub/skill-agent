/**
 * HistoryView —— 历史记录列表。
 * 支持：单条删除 / 批量删除（勾选模式）/ 全部删除，均弹「不可恢复」确认框；
 * 删除同步清理后端 data/sessions/{id}/ 会话目录与产物。
 */
"use client";

import { useEffect, useState } from "react";
import {
  CheckSquare,
  Download,
  Play,
  Square,
  Trash2,
  X,
} from "lucide-react";
import {
  loadHistory,
  clearHistory,
  removeHistoryItem,
  removeHistoryItems,
} from "../../lib/history";
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

/** 不可恢复删除确认弹窗 */
function ConfirmModal({
  title,
  message,
  onCancel,
  onConfirm,
}: {
  title: string;
  message: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm"
      onClick={onCancel}
    >
      <div
        className="glass relative w-full max-w-sm p-6 !bg-ink-900/80"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-400">
            <Trash2 size={16} />
          </span>
          <h3 className="text-base font-bold text-zinc-100">{title}</h3>
        </div>
        <p className="mt-3 text-sm leading-relaxed text-zinc-400">{message}</p>
        <div className="mt-6 flex justify-end gap-2">
          <button onClick={onCancel} className="btn-ghost">
            取消
          </button>
          <button
            onClick={onConfirm}
            className="inline-flex items-center gap-1.5 rounded-lg border border-rose-600/50 bg-rose-600/20 px-4 py-2 text-sm font-medium text-rose-300 transition-colors duration-200 hover:bg-rose-600/30"
          >
            <Trash2 size={14} />
            确认删除
          </button>
        </div>
      </div>
    </div>
  );
}

export default function HistoryView({ onResume, onClear }: HistoryViewProps) {
  const [history, setHistory] = useState<HistoryEntry[] | null>(null);
  /** 批量删除：勾选模式开关 */
  const [selectMode, setSelectMode] = useState(false);
  /** 勾选的 sessionId 集合 */
  const [selected, setSelected] = useState<Set<string>>(new Set());
  /** 确认弹窗状态 */
  const [confirm, setConfirm] = useState<{
    title: string;
    message: string;
    action: () => void;
  } | null>(null);

  useEffect(() => {
    let active = true;
    loadHistory().then((list) => {
      if (active) setHistory(list);
    });
    return () => {
      active = false;
    };
  }, []);

  /** 刷新列表并退出勾选模式 */
  const refresh = (list: HistoryEntry[]) => {
    setHistory(list);
    setSelected(new Set());
    setSelectMode(false);
  };

  const toggleSelect = (sessionId: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(sessionId)) next.delete(sessionId);
      else next.add(sessionId);
      return next;
    });
  };

  const toggleSelectAll = () => {
    setSelected((prev) => {
      if (prev.size === (history?.length || 0)) return new Set();
      return new Set((history || []).map((h) => h.sessionId));
    });
  };

  /** 单条删除 */
  const handleDeleteOne = (sessionId: string) => {
    setConfirm({
      title: "删除这条记录？",
      message:
        "删除后将同时移除本会话的服务端产物文件（mod.zip / 生成的代码），此操作不可恢复。",
      action: async () => {
        const list = await removeHistoryItem(sessionId);
        refresh(list);
      },
    });
  };

  /** 批量删除 */
  const handleDeleteSelected = () => {
    setConfirm({
      title: `删除选中的 ${selected.size} 条记录？`,
      message:
        "删除后将同时移除这些会话的服务端产物文件（mod.zip / 生成的代码），此操作不可恢复。",
      action: async () => {
        const list = await removeHistoryItems(Array.from(selected));
        refresh(list);
      },
    });
  };

  /** 全部删除 */
  const handleClearAll = () => {
    setConfirm({
      title: "删除全部历史记录？",
      message:
        "将删除全部会话及其服务端产物文件（mod.zip / 生成的代码），此操作不可恢复。",
      action: async () => {
        const list = await clearHistory();
        refresh(list);
        onClear();
      },
    });
  };

  const handleDownload = async (sessionId: string) => {
    try {
      await downloadSession(sessionId);
    } catch (err) {
      alert(err instanceof Error ? err.message : "下载失败");
    }
  };

  const allSelected = history
    ? history.length > 0 && selected.size === history.length
    : false;

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
      {/* 顶部操作条 */}
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-lg font-bold text-zinc-100">历史记录</h2>
        <div className="flex items-center gap-2">
          {!selectMode ? (
            <>
              <button
                onClick={() => setSelectMode(true)}
                className="btn-ghost !py-1.5"
              >
                <CheckSquare size={14} />
                批量删除
              </button>
              <button onClick={handleClearAll} className="btn-ghost !py-1.5">
                <Trash2 size={14} />
                全部删除
              </button>
            </>
          ) : (
            <>
              <button onClick={toggleSelectAll} className="btn-ghost !py-1.5">
                {allSelected ? (
                  <CheckSquare size={14} />
                ) : (
                  <Square size={14} />
                )}
                {allSelected ? "取消全选" : "全选"}
              </button>
              <button
                onClick={handleDeleteSelected}
                disabled={selected.size === 0}
                className="inline-flex items-center gap-1.5 rounded-lg border border-rose-600/50 bg-rose-600/20 px-3 py-1.5 text-sm font-medium text-rose-300 transition-colors duration-200 hover:bg-rose-600/30 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Trash2 size={14} />
                删除选中（{selected.size}）
              </button>
              <button
                onClick={() => {
                  setSelectMode(false);
                  setSelected(new Set());
                }}
                className="btn-ghost !py-1.5"
              >
                <X size={14} />
                取消
              </button>
            </>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {history.map((h) => {
          const isSelected = selected.has(h.sessionId);
          return (
            <div
              key={h.sessionId}
              className={`glass group relative flex flex-col p-4 transition-all duration-300 ${
                isSelected
                  ? "border-rose-500/40 shadow-[0_0_15px_rgba(244,63,94,0.15)]"
                  : "hover:-translate-y-1 hover:border-emerald-500/30 hover:shadow-[0_0_15px_rgba(16,185,129,0.1)]"
              }`}
            >
              {/* 勾选模式下显示选择框 */}
              {selectMode && (
                <button
                  onClick={() => toggleSelect(h.sessionId)}
                  className="absolute left-3 top-3 z-10 grid h-6 w-6 place-items-center rounded border border-zinc-700 bg-zinc-900/80 text-zinc-300 transition-colors hover:border-forge-emerald/50 hover:text-forge-emerald"
                  title={isSelected ? "取消选择" : "选择"}
                >
                  {isSelected ? <CheckSquare size={14} /> : <Square size={14} />}
                </button>
              )}

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
                  <button
                    onClick={() => handleDeleteOne(h.sessionId)}
                    className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-zinc-400 transition-all duration-150 hover:border-rose-500/40 hover:text-rose-400"
                    title="删除"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 确认弹窗（不可恢复警告） */}
      {confirm && (
        <ConfirmModal
          title={confirm.title}
          message={confirm.message}
          onCancel={() => setConfirm(null)}
          onConfirm={() => {
            confirm.action();
            setConfirm(null);
          }}
        />
      )}
    </div>
  );
}
/**
 * 历史记录管理（localStorage 持久化）
 *
 * 核心修复：按 sessionId 去重。
 *  - 已存在的会话 → 合并更新耗时/文件数/时间，但【保留首次记录的 prompt】
 *  - 不存在的会话 → 插入到最前
 */

import type { HistoryEntry } from "./types";

const KEY = "modforge_history_v2";
const MAX = 20;

export function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? (list as HistoryEntry[]) : [];
  } catch {
    return [];
  }
}

export function saveHistory(entry: HistoryEntry): HistoryEntry[] {
  const list = loadHistory();
  const idx = list.findIndex((h) => h.sessionId === entry.sessionId);
  if (idx >= 0) {
    // 已存在：仅更新耗时/文件数/时间，保留首次 prompt
    const old = list[idx];
    list[idx] = {
      ...old,
      elapsed: entry.elapsed ?? old.elapsed,
      fileCount: entry.fileCount ?? old.fileCount,
      date: entry.date || old.date,
    };
  } else {
    list.unshift({
      sessionId: entry.sessionId,
      game: entry.game || "minecraft",
      prompt: entry.prompt || "",
      elapsed: entry.elapsed ?? null,
      fileCount: entry.fileCount ?? null,
      date:
        entry.date ||
        new Date().toLocaleString("zh-CN", { hour12: false }),
    });
  }
  const trimmed = list.slice(0, MAX);
  try {
    localStorage.setItem(KEY, JSON.stringify(trimmed));
  } catch {
    /* 存储失败忽略 */
  }
  return trimmed;
}

export function clearHistory(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* noop */
  }
}
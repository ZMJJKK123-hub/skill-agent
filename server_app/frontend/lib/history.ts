/**
 * 历史记录管理（服务端存储，按登录用户隔离）
 *
 * 所有读写都走后端 /api/history（带 Authorization 头），
 * 不再使用 localStorage——不同用户之间的历史完全隔离。
 */

import type { HistoryEntry } from "./types";
import {
  fetchHistory,
  saveHistoryToServer,
  clearHistoryOnServer,
  deleteHistoryItem,
  deleteHistoryItems,
} from "./api";

export async function loadHistory(): Promise<HistoryEntry[]> {
  try {
    return await fetchHistory();
  } catch {
    return [];
  }
}

export async function saveHistory(entry: HistoryEntry): Promise<void> {
  try {
    await saveHistoryToServer(entry);
  } catch {
    /* 网络/鉴权失败静默忽略，避免阻塞生成流程 */
  }
}

export async function clearHistory(): Promise<HistoryEntry[]> {
  try {
    return await clearHistoryOnServer();
  } catch {
    return [];
  }
}

/** 单条删除历史（后端同步删除会话目录与产物） */
export async function removeHistoryItem(sessionId: string): Promise<HistoryEntry[]> {
  try {
    return await deleteHistoryItem(sessionId);
  } catch {
    return [];
  }
}

/** 批量删除历史（后端同步删除会话目录与产物） */
export async function removeHistoryItems(sessionIds: string[]): Promise<HistoryEntry[]> {
  try {
    return await deleteHistoryItems(sessionIds);
  } catch {
    return [];
  }
}
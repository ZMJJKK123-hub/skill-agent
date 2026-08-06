/** API 封装层：对后端 FastAPI 的唯一 fetch 出口（TypeScript + AbortSignal + 自动鉴权） */

import type { EventStream, FilePreview, FileTree, Game, HistoryEntry, SessionStats } from "./types";
import { getToken } from "./auth";

/** 自动附加 Authorization: Bearer <token>（未登录时为空头） */
function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...authHeaders(),
    ...(options.headers as Record<string, string> | undefined),
  };
  if (options.body) headers["Content-Type"] = "application/json";

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    let msg = res.statusText || `HTTP ${res.status}`;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data?.detail) msg = data.detail;
    } catch {
      /* 非 JSON 响应 */
    }
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

export interface CreateSessionResult {
  session_id: string;
  mod_dir: string;
}

export interface StartTaskResult {
  session_id: string;
  status: string;
}

export function createSession(
  apiKey: string,
  game: string,
  loader = "",
  version = ""
): Promise<CreateSessionResult> {
  return request<CreateSessionResult>("/api/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, game, loader, version }),
  });
}

export function resetSession(sessionId: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(
    `/api/session/reset?session_id=${encodeURIComponent(sessionId)}`,
    { method: "POST" }
  );
}

export function deleteSession(sessionId: string): Promise<{ ok: boolean }> {
  return request<{ ok: boolean }>(
    `/api/session?session_id=${encodeURIComponent(sessionId)}`,
    { method: "DELETE" }
  );
}

export function startTask(sessionId: string, prompt: string): Promise<StartTaskResult> {
  return request<StartTaskResult>("/api/task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, prompt }),
  });
}

export function getSession(sessionId: string, signal?: AbortSignal): Promise<SessionStats> {
  return request<SessionStats>(
    `/api/session?session_id=${encodeURIComponent(sessionId)}`,
    { signal }
  );
}

export function getStatus(sessionId: string, signal?: AbortSignal): Promise<SessionStats> {
  return request<SessionStats>(
    `/api/status?session_id=${encodeURIComponent(sessionId)}`,
    { signal }
  );
}

export function getEvents(
  sessionId: string,
  cursor: { run: number; agent: number } | null = null,
  signal?: AbortSignal
): Promise<EventStream> {
  const params = new URLSearchParams({ session_id: sessionId });
  if (cursor) params.set("cursor", JSON.stringify(cursor));
  return request<EventStream>(`/api/events?${params.toString()}`, { signal });
}

export function getFiles(
  sessionId: string,
  path = "",
  signal?: AbortSignal
): Promise<FileTree | FilePreview> {
  const params = new URLSearchParams({ session_id: sessionId });
  if (path) params.set("path", path);
  return request<FileTree | FilePreview>(`/api/files?${params.toString()}`, { signal });
}

export function getLog(sessionId: string, offset = 0): Promise<{ content: string; offset: number }> {
  return request<{ content: string; offset: number }>(
    `/api/log?session_id=${encodeURIComponent(sessionId)}&offset=${offset}`
  );
}

export function getGames(): Promise<{ games: Game[] }> {
  return request<{ games: Game[] }>("/api/games");
}

/** 下载 mod.zip 源码包（带登录头，<a> 无法携带自定义头所以用 fetch 流式下载） */
export async function downloadSession(sessionId: string): Promise<void> {
  const res = await fetch(`/api/download?session_id=${encodeURIComponent(sessionId)}`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    let msg = res.statusText || `HTTP ${res.status}`;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data?.detail) msg = data.detail;
    } catch {
      /* 非 JSON 响应 */
    }
    throw new Error(msg);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `mod-${sessionId}-src.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** 下载打包好的 mod jar（带登录头；无 jar 时后端返回 400） */
export async function downloadJar(sessionId: string): Promise<void> {
  const res = await fetch(`/api/download/jar?session_id=${encodeURIComponent(sessionId)}`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    let msg = res.statusText || `HTTP ${res.status}`;
    try {
      const data = (await res.json()) as { detail?: string };
      if (data?.detail) msg = data.detail;
    } catch {
      /* 非 JSON 响应 */
    }
    throw new Error(msg);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `mod-${sessionId}.jar`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ===== 服务端历史记录（按用户隔离） =====

export async function fetchHistory(): Promise<HistoryEntry[]> {
  const data = await request<{ history: HistoryEntry[] }>("/api/history");
  return data.history || [];
}

export async function saveHistoryToServer(entry: HistoryEntry): Promise<HistoryEntry[]> {
  const data = await request<{ history: HistoryEntry[] }>("/api/history", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entry),
  });
  return data.history || [];
}

export async function clearHistoryOnServer(): Promise<HistoryEntry[]> {
  const data = await request<{ history: HistoryEntry[] }>("/api/history", { method: "DELETE" });
  return data.history || [];
}

/** 单条删除历史（同步删除会话目录与产物文件） */
export async function deleteHistoryItem(sessionId: string): Promise<HistoryEntry[]> {
  const data = await request<{ history: HistoryEntry[] }>(
    `/api/history?session_id=${encodeURIComponent(sessionId)}`,
    { method: "DELETE" }
  );
  return data.history || [];
}

/** 批量删除历史（同步删除会话目录与产物文件） */
export async function deleteHistoryItems(sessionIds: string[]): Promise<HistoryEntry[]> {
  const data = await request<{ history: HistoryEntry[] }>("/api/history/batch", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_ids: sessionIds }),
  });
  return data.history || [];
}

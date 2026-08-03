/** API 封装层：对后端 FastAPI 的唯一 fetch 出口（TypeScript + AbortSignal） */

import type { EventStream, FilePreview, FileTree, Game, SessionStats } from "./types";

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(url, options);
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

export function createSession(apiKey: string, game: string): Promise<CreateSessionResult> {
  return request<CreateSessionResult>("/api/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, game }),
  });
}

export function startTask(sessionId: string, prompt: string): Promise<StartTaskResult> {
  return request<StartTaskResult>("/api/task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, prompt }),
  });
}

export function getSession(sessionId: string, signal?: AbortSignal): Promise<SessionStats> {
  return request<SessionStats>(`/api/session?session_id=${encodeURIComponent(sessionId)}`, { signal });
}

export function getStatus(sessionId: string, signal?: AbortSignal): Promise<SessionStats> {
  return request<SessionStats>(`/api/status?session_id=${encodeURIComponent(sessionId)}`, { signal });
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

export function getFiles(sessionId: string, path = "", signal?: AbortSignal): Promise<FileTree | FilePreview> {
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

export const downloadUrl = (sessionId: string): string =>
  `/api/download?session_id=${encodeURIComponent(sessionId)}`;
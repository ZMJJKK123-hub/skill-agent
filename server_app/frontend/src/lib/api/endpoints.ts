/**
 * 全部后端端点封装（由 lib/api.ts 原样迁出，按域分组）。
 */
import { api, downloadBlob } from './client'
import type { ConversationMessage, EventsResponse, GameInfo, HistoryEntry, Question, StatusResponse } from './types'

// ── 会话 ──

export function createSession(
  apiKey: string,
  game: string,
  loader: string,
  version: string,
  model = '',
  baseUrl = '',
  sandbox = 'full-access',
  visionEnabled = false,
  visionApiKey = '',
  visionBaseUrl = '',
  visionModel = '',
  autoMode = false,
  searchApiKey = '',
) {
  return api<{ session_id: string; mod_dir: string }>('/api/session', {
    method: 'POST',
    body: JSON.stringify({
      api_key: apiKey, game, loader, version, model, base_url: baseUrl, sandbox,
      vision_enabled: visionEnabled,
      vision_api_key: visionApiKey,
      vision_base_url: visionBaseUrl,
      vision_model: visionModel,
      auto_mode: autoMode,
      search_api_key: searchApiKey,
    }),
  })
}

export function resetSession(sessionId: string) {
  return api<{ session_id: string; status: string }>('/api/session/reset', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  })
}

export function deleteSession(sessionId: string) {
  return api(`/api/session?session_id=${sessionId}`, { method: 'DELETE' })
}

// 准备 mod 工作区：复制模板+MC 源码到 <session>/mod/（/mod 触发，幂等）
export function prepareModWorkspace(sessionId: string) {
  return api<{ session_id: string; mod_ready: boolean; already: boolean }>('/api/session/mod?session_id=' + encodeURIComponent(sessionId), {
    method: 'POST',
  })
}

// 会话对话历史（多轮 user/assistant 消息对）+ 模式推断
export function getConversation(sessionId: string) {
  return api<{ session_id: string; messages: ConversationMessage[]; mode: 'chat' | 'mod' | null }>(
    `/api/conversation?session_id=${encodeURIComponent(sessionId)}`,
  )
}

// 历史消息里图片附件的取回地址（文件名由后端落盘 .chat/uploads）
export function sessionImageUrl(sessionId: string, name: string) {
  return `/api/session/image?session_id=${encodeURIComponent(sessionId)}&name=${encodeURIComponent(name)}`
}

// ── 任务 ──

export function startTask(
  sessionId: string,
  prompt: string,
  mode = 'chat',
  resume = false,
  apiKey = '',
  model = '',
  baseUrl = '',
  visionEnabled?: boolean,
  visionApiKey?: string,
  visionBaseUrl?: string,
  visionModel?: string,
  autoMode?: boolean,
  searchApiKey?: string,
  images?: string[],
  forceMode?: boolean,
) {
  const body: Record<string, unknown> = { session_id: sessionId, prompt, mode, resume, model, base_url: baseUrl }
  if (apiKey) body.api_key = apiKey
  if (visionEnabled !== undefined) body.vision_enabled = visionEnabled
  if (visionApiKey !== undefined) body.vision_api_key = visionApiKey
  if (visionBaseUrl !== undefined) body.vision_base_url = visionBaseUrl
  if (visionModel !== undefined) body.vision_model = visionModel
  if (autoMode !== undefined) body.auto_mode = autoMode
  if (searchApiKey !== undefined) body.search_api_key = searchApiKey
  // 用户上传的图片（data URL，最多 4 张）：后端落盘 .chat/uploads 后传给 agent
  if (images && images.length > 0) body.images = images
  // 显式模式覆盖（/chat 命令）：server 不沿用会话记忆的 mod 模式
  if (forceMode) body.force_mode = true
  return api<{ session_id: string; status: string; mode: string; resume?: boolean }>('/api/task', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

// 暂停当前运行的 agent（kill 子进程，断点保留在 .chat/working.jsonl）
export function pauseTask(sessionId: string) {
  return api<{ session_id: string; status: string }>('/api/task/pause?session_id=' + encodeURIComponent(sessionId), {
    method: 'POST',
  })
}

// ── 状态 / 事件 ──

export function getStatus(sessionId: string, apiKey = '') {
  // apiKey 可选：服务重启后恢复的旧会话内存 key 为空，轮询带上 key 让后端回填
  const q = apiKey ? `&api_key=${encodeURIComponent(apiKey)}` : ''
  return api<StatusResponse>(`/api/status?session_id=${sessionId}${q}`)
}

export function getResult(sessionId: string) {
  return api<{ status: string; result: string | null }>(`/api/result?session_id=${sessionId}`)
}

export function getEvents(sessionId: string, cursor?: { run: number; agent: number }) {
  const q = cursor ? `&cursor=${encodeURIComponent(JSON.stringify(cursor))}` : ''
  return api<EventsResponse>(`/api/events?session_id=${sessionId}${q}`)
}

// ── 历史 ──

export function getHistory() {
  return api<{ history: HistoryEntry[] }>('/api/history')
}

// 按 owner 派生的会话列表（data/sessions/*/owner.txt），历史与会话双向一致
export function getSessions() {
  return api<{ sessions: HistoryEntry[] }>('/api/sessions')
}

// ── 问答 ──

export function getQuestion(sessionId: string) {
  return api<Question>(`/api/question?session_id=${sessionId}`)
}

export function answerQuestion(sessionId: string, answer: string) {
  return api(`/api/answer`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, answer }),
  })
}

// 多题确认提交：answers = [{question, answer}, ...]
export function answerQuestions(sessionId: string, answers: { question: string; answer: string }[]) {
  return api(`/api/answer`, {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, answers }),
  })
}

// ── 游戏模板 ──

export function getGames() {
  return api<{ games: GameInfo[] }>('/api/games')
}

// ── 下载 ──

export function downloadJar(sessionId: string) {
  return downloadBlob(`/api/download/jar?session_id=${sessionId}`, `mod-${sessionId}.jar`)
}

export function downloadSourceZip(sessionId: string) {
  return downloadBlob(`/api/download?session_id=${sessionId}`, `mod-${sessionId}-src.zip`)
}

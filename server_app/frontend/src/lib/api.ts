// 后端 API 封装：token 注入 + 所有接口 + 类型定义
// 后端 = server_app/server.py（FastAPI，无需改动）

import JSZip from 'jszip'

export interface SessionStats {
  session_id: string
  state: 'pending' | 'running' | 'finished'
  running: boolean
  finished: boolean
  started_at: number | null
  finished_at: number | null
  elapsed: number | null
  file_count: number
  total_bytes: number
  has_jar: boolean
}

export interface StatusResponse extends SessionStats {
  log_tail: string
  paused?: boolean
  pending?: number
}

export interface EventItem {
  id: string
  ts: number
  type: string // thinking | tool_call | todo | log | round | system | background | protocol | worktree | tool_result
  source: string
  content: string
  tool?: string
  peer?: string   // teammate | subagent | supervisor
  status?: string // tool_result: success | failed
}

export interface EventsResponse {
  session_id: string
  events: EventItem[]
  cursor: { run: number; agent: number }
}

export interface HistoryEntry {
  sessionId: string
  owner: string
  has_jar: boolean
  date: string
  title?: string
}

export interface GameInfo {
  id: string
  name: string
  description: string
}

const TOKEN_KEY = 'modforge_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

async function api<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (options.body && typeof options.body === 'string') headers['Content-Type'] = 'application/json'

  const res = await fetch(path, { ...options, headers })
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const j = await res.json()
      if (j && j.detail) detail = j.detail
    } catch {
      /* ignore non-JSON error body */
    }
    throw new Error(detail)
  }
  // 空响应体返回 undefined
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return (await res.json()) as T
  return undefined as T
}

// ── 认证 ──
export function register(username: string, password: string) {
  return api<{ username: string; token: string }>('/api/register', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function login(username: string, password: string) {
  return api<{ username: string; token: string }>('/api/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function me() {
  return api<{ username: string }>('/api/me')
}

export function logout() {
  return api('/api/logout', { method: 'POST' })
}

// ── 会话 / 任务 ──
export function createSession(
  apiKey: string,
  game: string,
  loader: string,
  version: string,
  model = 'deepseek-v4-flash',
  baseUrl = 'https://api.deepseek.com/v1',
  sandbox = 'full-access',
  visionEnabled = false,
  visionApiKey = '',
  visionBaseUrl = '',
  visionModel = '',
) {
  return api<{ session_id: string; mod_dir: string }>('/api/session', {
    method: 'POST',
    body: JSON.stringify({
      api_key: apiKey, game, loader, version, model, base_url: baseUrl, sandbox,
      vision_enabled: visionEnabled,
      vision_api_key: visionApiKey,
      vision_base_url: visionBaseUrl,
      vision_model: visionModel,
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

export function startTask(
  sessionId: string,
  prompt: string,
  mode = 'chat',
  resume = false,
  model = '',
  baseUrl = '',
  visionEnabled?: boolean,
  visionApiKey?: string,
  visionBaseUrl?: string,
  visionModel?: string,
) {
  const body: Record<string, unknown> = { session_id: sessionId, prompt, mode, resume, model, base_url: baseUrl }
  if (visionEnabled !== undefined) body.vision_enabled = visionEnabled
  if (visionApiKey !== undefined) body.vision_api_key = visionApiKey
  if (visionBaseUrl !== undefined) body.vision_base_url = visionBaseUrl
  if (visionModel !== undefined) body.vision_model = visionModel
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

// 准备 mod 工作区：复制模板+MC 源码到 <session>/mod/（/mod 触发，幂等）
export function prepareModWorkspace(sessionId: string) {
  return api<{ session_id: string; mod_ready: boolean; already: boolean }>('/api/session/mod?session_id=' + encodeURIComponent(sessionId), {
    method: 'POST',
  })
}

// 会话对话历史（多轮聊天的 user/assistant 消息对）+ 模式推断
export function getConversation(sessionId: string) {
  return api<{ session_id: string; messages: { role: string; content: string }[]; mode: 'chat' | 'mod' | null }>(
    `/api/conversation?session_id=${encodeURIComponent(sessionId)}`,
  )
}

// ── 状态 / 事件 ──
export function getStatus(sessionId: string) {
  return api<StatusResponse>(`/api/status?session_id=${sessionId}`)
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

export interface QuestionItem {
  question: string
  options?: string[]
}

export interface Question {
  status: string
  question?: string       // legacy 单题
  options?: string[]      // legacy 单题
  questions?: QuestionItem[]  // 多题
}

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

// ── 下载（需 token，用 fetch + blob 触发浏览器下载）──
export async function downloadJar(sessionId: string) {
  const token = getToken()
  const res = await fetch(`/api/download/jar?session_id=${sessionId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) throw new Error(`下载失败: ${res.status}`)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mod-${sessionId}.jar`
  a.click()
  URL.revokeObjectURL(url)
}

export async function downloadSourceZip(sessionId: string) {
  const token = getToken()
  const res = await fetch(`/api/download?session_id=${sessionId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) throw new Error(`下载失败: ${res.status}`)
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `mod-${sessionId}-src.zip`
  a.click()
  URL.revokeObjectURL(url)
}

// ============================================================================
// 【导入文件夹功能 - 已临时禁用】
// 说明：导入后 bug 较多，暂时注释停用；代码保留，后续扩展时恢复。
// ============================================================================
// // 导入已有 mod 文件夹：客户端打包 zip → 上传 → 后端解压成新会话工作区
// export interface ImportFile {
//   path: string
//   data: Uint8Array
// }
//
// export async function importSession(
//   files: ImportFile[],
//   settings: { apiKey: string; game: string; loader: string; version: string; model: string; baseUrl: string; sandbox: string },
// ) {
//   const zip = new JSZip()
//   for (const f of files) zip.file(f.path, f.data)
//   const blob = await zip.generateAsync({ type: 'blob' })
//
//   const qs = `game=${encodeURIComponent(settings.game)}&loader=${encodeURIComponent(settings.loader)}&version=${encodeURIComponent(settings.version)}&model=${encodeURIComponent(settings.model)}&base_url=${encodeURIComponent(settings.baseUrl)}&sandbox=${encodeURIComponent(settings.sandbox)}`
//   const token = getToken()
//   const res = await fetch(`/api/import?${qs}`, {
//     method: 'POST',
//     body: blob,
//     headers: {
//       ...(token ? { Authorization: `Bearer ${token}` } : {}),
//       'X-API-Key': settings.apiKey,
//       'Content-Type': 'application/zip',
//     },
//   })
//   if (!res.ok) {
//     let detail = `${res.status}`
//     try {
//       const j = await res.json()
//       if (j && j.detail) detail = j.detail
//     } catch {
//       /* ignore */
//     }
//     throw new Error(detail)
//   }
//   return res.json() as Promise<{ session_id: string; mod_dir: string }>
// }
// ============================================================================

/**
 * 后端 API 响应类型定义（由 lib/api.ts 迁出）。
 */

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
  crashed?: boolean  // 子进程异常退出（服务端 _crashed 判定）
  paused?: boolean
  pending?: number
}

export interface EventItem {
  id: string
  ts: number
  type: string // thinking | thinking_delta | tool_call | todo | log | round | system | background | protocol | worktree | tool_result
  source: string
  content: string
  tool?: string
  peer?: string   // teammate | subagent | supervisor
  status?: string // tool_result: success | failed
  batch?: number  // 同一次轮询到达的批次（渲染时逐行错峰渐入）
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

export interface ConversationMessage {
  role: string
  content: string
  images?: string[]
}

export interface QuestionItem {
  question: string
  options?: string[]
}

export interface Question {
  status: string
  question?: string           // legacy 单题
  options?: string[]          // legacy 单题
  questions?: QuestionItem[]  // 多题
}

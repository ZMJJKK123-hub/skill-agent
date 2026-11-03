// 会话状态只依赖通用状态契约；不依赖 React。
import type { DownloadPort, Logger, StateStore, TimerPort } from '../../../assets/js/contracts.ts'
// 会话策略参数由组合根注入。
import type { FrontendConfig } from '../../../assets/js/config.ts'
export type SessionMode = 'chat' | 'mod'
export type SessionPhase = 'idle' | 'creating' | 'running' | 'paused' | 'finished' | 'error'
export interface ChatMessage { role: 'user' | 'assistant'; content: string }
export interface EventCursor { run: number; agent: number }
export interface EventItem { id: string; ts: number; type: string; source: string; content: string; tool?: string; peer?: string; status?: string }
export interface HistoryEntry { sessionId: string; owner: string; has_jar: boolean; date: string; title?: string }
export interface GenSettings {
  apiKey: string; game: string; loader: string; version: string; model: string; baseUrl: string; sandbox: string
  visionEnabled: boolean; visionApiKey: string; visionBaseUrl: string; visionModel: string; autoMode: boolean; searchApiKey: string
}
export interface SessionRequestDTO {
  api_key: string; game: string; loader: string; version: string; model: string; base_url: string; sandbox: string
  vision_enabled: boolean; vision_api_key: string; vision_base_url: string; vision_model: string
  auto_mode: boolean; search_api_key: string
}
export interface StatusResponse {
  session_id: string; state: 'pending' | 'running' | 'finished'; running: boolean; finished: boolean
  started_at: number | null; finished_at: number | null; elapsed: number | null
  file_count: number; total_bytes: number; has_jar: boolean; log_tail: string; paused?: boolean; pending?: number
}
export interface EventsResponse { session_id: string; events: EventItem[]; cursor: EventCursor }
export interface QuestionItem { question: string; options?: string[] }
export interface QuestionResponse { status: string; question?: string; options?: string[]; questions?: QuestionItem[] }
export interface QuestionAnswer { question: string; answer: string }
export interface TaskInput { sessionId: string; prompt: string; mode: SessionMode; resume: boolean; settings?: GenSettings }
export interface ConversationResponse { session_id: string; messages: ChatMessage[]; mode: SessionMode | null }
export interface SessionRepository {
  create(settings: GenSettings): Promise<{ session_id: string; mod_dir: string }>
  prepare(sessionId: string): Promise<void>
  start(input: TaskInput): Promise<void>
  pause(sessionId: string): Promise<void>
  reset(sessionId: string): Promise<void>
  remove(sessionId: string): Promise<void>
  list(): Promise<{ sessions: HistoryEntry[] }>
  conversation(sessionId: string): Promise<ConversationResponse>
  events(sessionId: string, cursor?: EventCursor): Promise<EventsResponse>
  status(sessionId: string): Promise<StatusResponse>
  question(sessionId: string): Promise<QuestionResponse>
  answer(sessionId: string, answer: string, answers?: QuestionAnswer[]): Promise<void>
  download(sessionId: string, kind: 'jar' | 'source'): Promise<Blob>
}
export interface SessionState {
  sessionId: string | null; phase: SessionPhase; error: string | null; title: string | null
  question: { question: string; options: string[] } | null
  questions: { question: string; options: string[] }[] | null
  prompts: string[]; events: EventItem[]; cursor: EventCursor | null; logTail: string
  elapsed: number | null; hasJar: boolean; history: HistoryEntry[]; mode: SessionMode | null
  chatMessages: ChatMessage[]; paused: boolean; pending: number; stoppedNotice: boolean
}
export type SessionStore = StateStore<SessionState>
export interface SessionController {
  loadHistory(): Promise<void>
  sendPrompt(prompt: string, settings: GenSettings, mode?: SessionMode): Promise<void>
  pauseTask(): Promise<void>
  resumeTask(): Promise<void>
  poll(): Promise<void>
  answerQuestion(answer: string, answers?: QuestionAnswer[]): Promise<void>
  startPolling(intervalMs?: number): void
  stopPolling(): void
  newConversation(): Promise<void>
  openHistorySession(sessionId: string): Promise<void>
  regenerate(): Promise<void>
  deleteSession(sessionId: string): Promise<void>
  downloadJar(sessionId: string): Promise<void>
  downloadSourceZip(sessionId: string): Promise<void>
  clearAccount(): void
  dispose(): void
}
export interface SessionDependencies {
  repository: SessionRepository
  store: SessionStore
  timer: TimerPort
  downloads: DownloadPort
  config: FrontendConfig
  logger: Logger
  getSettings(): GenSettings
}

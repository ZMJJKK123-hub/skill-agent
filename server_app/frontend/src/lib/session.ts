import { useSyncExternalStore } from 'react'
import * as api from './api'
import type { EventItem, HistoryEntry, ImportFile } from './api'

// 会话/生成编排：一个对话 = 一个工作区文件夹（后端 /api/session 创建）
export interface GenSettings {
  apiKey: string
  game: string
  loader: string
  version: string
  model: string
  baseUrl: string
  sandbox: string
}

export interface SessionState {
  sessionId: string | null
  phase: 'idle' | 'creating' | 'running' | 'finished' | 'error'
  error: string | null
  title: string | null
  question: { question: string; options: string[] } | null
  prompts: string[]
  events: EventItem[]
  cursor: { run: number; agent: number } | null
  logTail: string
  elapsed: number | null
  hasJar: boolean
  history: HistoryEntry[]
  // 多轮对话支持：
  mode: 'chat' | 'mod' | null        // 当前会话运行模式（null=未开始）
  chatMessages: { role: string; content: string }[]  // 聊天气泡历史（chat 模式）
}

let state: SessionState = {
  sessionId: null,
  phase: 'idle',
  error: null,
  title: null,
  question: null,
  prompts: [],
  events: [],
  cursor: null,
  logTail: '',
  elapsed: null,
  hasJar: false,
  history: [],
  mode: null,
  chatMessages: [],
}

const listeners = new Set<() => void>()
function emit() {
  listeners.forEach((l) => l())
}
function subscribe(l: () => void) {
  listeners.add(l)
  return () => listeners.delete(l)
}
function getState() {
  return state
}
function setState(patch: Partial<SessionState>) {
  state = { ...state, ...patch }
  emit()
}

export function useSession(): SessionState {
  return useSyncExternalStore(subscribe, getState)
}

// ── 动作 ──

export async function loadHistory() {
  try {
    const { sessions } = await api.getSessions()
    setState({ history: sessions })
  } catch {
    /* 未登录时忽略 */
  }
}

// 发起对话 → 建新工作区文件夹 → 启动生成 → 开始轮询
// mode: 'chat'（通用对话，不复制模板）| 'mod'（MOD 制作，需先 prepareModWorkspace）
export async function sendPrompt(prompt: string, settings: GenSettings, mode: 'chat' | 'mod' = 'chat') {
  if (state.phase === 'creating' || state.phase === 'running') return
  setState({
    phase: 'creating',
    error: null,
    events: [],
    cursor: null,
    hasJar: false,
    elapsed: null,
    logTail: '',
    mode,
  })
  try {
    // 若已有会话（如导入文件夹后），复用；否则建新会话（从零生成）
    let sid = state.sessionId
    if (!sid) {
      const { session_id } = await api.createSession(
        settings.apiKey,
        settings.game,
        settings.loader,
        settings.version,
        settings.model,
        settings.baseUrl,
        settings.sandbox,
      )
      sid = session_id
      setState({ sessionId: session_id })
    }
    // mod 模式：先准备 mod 工作区（复制模板+源码，幂等）
    if (mode === 'mod') {
      await api.prepareModWorkspace(sid)
    }
    const prompts = [...state.prompts, prompt]
    // 标题：已有（文件夹名）优先，否则用首条输入截断
    const title = state.title ?? (prompt.length > 24 ? prompt.slice(0, 24) + '…' : prompt)
    // chat 模式：把用户消息加入聊天气泡
    const chatMessages = mode === 'chat'
      ? [...state.chatMessages, { role: 'user' as const, content: prompt }]
      : state.chatMessages
    setState({ prompts, phase: 'running', title, chatMessages })
    await api.startTask(sid, prompt, mode)
    void poll()
    void loadHistory()
  } catch (e) {
    setState({ phase: 'error', error: String((e as Error)?.message || e) })
  }
}

export async function poll() {
  const sid = state.sessionId
  if (!sid) return
  try {
    const ev = await api.getEvents(sid, state.cursor ?? undefined)
    if (ev.events.length > 0) {
      setState({ events: [...state.events, ...ev.events], cursor: ev.cursor })
    }
    const st = await api.getStatus(sid)
    setState({
      elapsed: st.elapsed,
      hasJar: st.has_jar,
      logTail: st.log_tail,
      phase: st.finished ? 'finished' : 'running',
    })
    // chat 模式：任务结束且还没记录 assistant 回复 → 从 logTail 提取最终回复
    if (st.finished && state.mode === 'chat') {
      const last = state.chatMessages[state.chatMessages.length - 1]
      if (last?.role !== 'assistant') {
        const reply = extractFinalReply(st.log_tail)
        if (reply) {
          setState({ chatMessages: [...state.chatMessages, { role: 'assistant', content: reply }] })
        }
      }
    }
    const q = await api.getQuestion(sid)
    if (q.status === 'pending' && q.question) {
      setState({ question: { question: q.question, options: q.options ?? [] } })
    } else if (state.question) {
      setState({ question: null })
    }
  } catch {
    /* 轮询瞬时失败忽略，下一轮重试 */
  }
}

// 从 run.log 尾部提取最终回复：取 "最终回复:" 之后的内容；没有则取末尾非噪音行
function extractFinalReply(logTail: string): string | null {
  if (!logTail) return null
  const marker = '最终回复:'
  const idx = logTail.lastIndexOf(marker)
  if (idx >= 0) {
    const after = logTail.slice(idx + marker.length).trim()
    if (after) return after
  }
  // 兜底：取最后一行（跳过 [run_task]/[思考] 前缀行）
  const lines = logTail.split(/\r?\n/).filter((l) => l.trim())
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim()
    if (line && !line.startsWith('[run_task]') && !line.startsWith('[思考]') && !line.startsWith('[todo]')) {
      return line
    }
  }
  return null
}

// 打开历史会话时：加载该会话的对话历史（.chat/conversation.jsonl）
export async function loadConversation(sessionId: string) {
  try {
    const { messages } = await api.getConversation(sessionId)
    setState({ chatMessages: messages })
  } catch {
    /* 未登录/无历史时忽略 */
  }
}

export async function answerQuestion(answer: string) {
  const sid = state.sessionId
  if (!sid) return
  try {
    await api.answerQuestion(sid, answer)
  } catch {
    /* 提交失败也本地清掉，避免卡死界面 */
  }
  setState({ question: null })
}

let pollTimer: number | null = null
export function startPolling(intervalMs = 2000) {
  if (pollTimer !== null) return
  pollTimer = window.setInterval(() => void poll(), intervalMs)
}
export function stopPolling() {
  if (pollTimer !== null) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

// 新建对话：回到从零生成的空态（不删历史，只清当前状态）
export async function newConversation() {
  stopPolling()
  setState({
    sessionId: null,
    phase: 'idle',
    events: [],
    cursor: null,
    prompts: [],
    title: null,
    question: null,
    error: null,
    hasJar: false,
    elapsed: null,
    logTail: '',
    mode: null,
    chatMessages: [],
  })
  void loadHistory()
}

// 从历史打开一个会话（查看产物/下载/继续对话，不重新生成）
export function openHistorySession(id: string) {
  setState({ sessionId: id, phase: 'finished', events: [], cursor: null, prompts: [], title: null, error: null, mode: null, chatMessages: [] })
  void loadConversation(id)
  void poll()
}

// 重新生成：重置当前会话骨架，回到可再发需求的空态
export async function regenerate() {
  const sid = state.sessionId
  if (!sid) return
  try {
    await api.resetSession(sid)
    setState({ phase: 'idle', events: [], cursor: null, prompts: [], error: null, hasJar: false, elapsed: null, logTail: '', mode: null, chatMessages: [] })
  } catch (e) {
    setState({ error: String((e as Error)?.message || e) })
  }
}

// 导入已有 mod 文件夹：上传 zip → 后端解压成新会话工作区 → 回到可对话态
export async function importWorkspace(files: ImportFile[], settings: GenSettings, title?: string) {
  setState({ phase: 'creating', error: null, events: [], cursor: null, prompts: [], hasJar: false, elapsed: null, logTail: '', title: title ?? null })
  try {
    const { session_id } = await api.importSession(files, settings)
    setState({ sessionId: session_id, phase: 'idle', title: title ?? null })
    void loadHistory()
  } catch (e) {
    setState({ phase: 'error', error: String((e as Error)?.message || e) })
  }
}

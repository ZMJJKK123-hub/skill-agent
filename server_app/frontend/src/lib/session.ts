import { useSyncExternalStore } from 'react'
import * as api from './api'
import type { EventItem, HistoryEntry, ImportFile } from './api'

// 会话/生成编排：一个对话 = 一个工作区文件夹（后端 /api/session 创建）
export interface GenSettings {
  apiKey: string
  game: string
  loader: string
  version: string
}

export interface SessionState {
  sessionId: string | null
  phase: 'idle' | 'creating' | 'running' | 'finished' | 'error'
  error: string | null
  prompts: string[]
  events: EventItem[]
  cursor: { run: number; agent: number } | null
  logTail: string
  elapsed: number | null
  hasJar: boolean
  history: HistoryEntry[]
}

let state: SessionState = {
  sessionId: null,
  phase: 'idle',
  error: null,
  prompts: [],
  events: [],
  cursor: null,
  logTail: '',
  elapsed: null,
  hasJar: false,
  history: [],
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
export async function sendPrompt(prompt: string, settings: GenSettings) {
  if (state.phase === 'creating' || state.phase === 'running') return
  setState({
    phase: 'creating',
    error: null,
    events: [],
    cursor: null,
    hasJar: false,
    prompts: [],
    elapsed: null,
    logTail: '',
  })
  try {
    const { session_id } = await api.createSession(
      settings.apiKey,
      settings.game,
      settings.loader,
      settings.version,
    )
    setState({ sessionId: session_id })
    const prompts = [...state.prompts, prompt]
    setState({ prompts, phase: 'running' })
    await api.startTask(session_id, prompt)
    void poll()
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
  } catch {
    /* 轮询瞬时失败忽略，下一轮重试 */
  }
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
export function newConversation() {
  stopPolling()
  setState({
    sessionId: null,
    phase: 'idle',
    events: [],
    cursor: null,
    prompts: [],
    error: null,
    hasJar: false,
    elapsed: null,
    logTail: '',
  })
}

// 从历史打开一个会话（查看产物/下载，不重新生成）
export function openHistorySession(id: string) {
  setState({ sessionId: id, phase: 'finished', events: [], cursor: null, prompts: [], error: null })
  void poll()
}

// 重新生成：重置当前会话骨架，回到可再发需求的空态
export async function regenerate() {
  const sid = state.sessionId
  if (!sid) return
  try {
    await api.resetSession(sid)
    setState({ phase: 'idle', events: [], cursor: null, prompts: [], error: null, hasJar: false, elapsed: null, logTail: '' })
  } catch (e) {
    setState({ error: String((e as Error)?.message || e) })
  }
}

// 导入已有 mod 文件夹：上传 zip → 后端解压成新会话工作区 → 回到可对话态
export async function importWorkspace(files: ImportFile[], settings: GenSettings) {
  setState({ phase: 'creating', error: null, events: [], cursor: null, prompts: [], hasJar: false, elapsed: null, logTail: '' })
  try {
    const { session_id } = await api.importSession(files, settings)
    setState({ sessionId: session_id, phase: 'idle' })
  } catch (e) {
    setState({ phase: 'error', error: String((e as Error)?.message || e) })
  }
}

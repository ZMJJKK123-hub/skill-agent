/**
 * 会话状态存储（由 lib/session.ts 原样迁出）。
 *
 * useSyncExternalStore 外部存储模式：state + listeners + setState。
 */
import { useSyncExternalStore } from 'react'
import type { EventItem, HistoryEntry } from '../api'

/** 生成配置（sendPrompt 入参） */
export interface GenSettings {
  apiKey: string
  game: string
  loader: string
  version: string
  model: string
  baseUrl: string
  sandbox: string
  visionEnabled: boolean
  visionApiKey: string
  visionBaseUrl: string
  visionModel: string
  autoMode: boolean
  searchApiKey: string
}

/** 会话全量状态 */
export interface SessionState {
  sessionId: string | null
  phase: 'idle' | 'creating' | 'running' | 'paused' | 'finished' | 'error'
  error: string | null
  title: string | null
  question: { question: string; options: string[] } | null
  // 多题提问（agent 一次问多个，前端草稿式确认）
  questions: { question: string; options: string[] }[] | null
  prompts: string[]
  events: EventItem[]
  cursor: { run: number; agent: number } | null
  logTail: string
  elapsed: number | null
  hasJar: boolean
  history: HistoryEntry[]
  mode: 'chat' | 'mod' | null        // 当前会话运行模式（null=未开始）
  chatMessages: { role: string; content: string; images?: string[] }[]  // 聊天气泡历史
  paused: boolean            // 已暂停（可继续）
  pending: number            // 运行中排队消息数（>0 自动续跑）
  lastSendAt: number | null  // 最近一次本地发送时间（抑制"排队"闪烁）
  stoppedNotice: boolean     // 是否显示"您已终止该对话"横线
}

/** 初始空态 */
export function initialState(): SessionState {
  return {
    sessionId: null,
    phase: 'idle',
    error: null,
    title: null,
    question: null,
    questions: null,
    prompts: [],
    events: [],
    cursor: null,
    logTail: '',
    elapsed: null,
    hasJar: false,
    history: [],
    mode: null,
    chatMessages: [],
    paused: false,
    pending: 0,
    lastSendAt: null,
    stoppedNotice: false,
  }
}

export let state: SessionState = initialState()

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
export function setState(patch: Partial<SessionState>) {
  state = { ...state, ...patch }
  emit()
}

export function useSession(): SessionState {
  return useSyncExternalStore(subscribe, getState)
}

// 当前活动会话指针（sessionStorage：刷新保留、关标签页即失效）。
// 刷新后据此自动恢复会话视图，运行状态由轮询接管（实测缺陷修复）。
export const ACTIVE_SID_KEY = 'modforge_active_sid'
export function rememberActiveSid(sid: string | null) {
  try {
    if (sid) sessionStorage.setItem(ACTIVE_SID_KEY, sid)
    else sessionStorage.removeItem(ACTIVE_SID_KEY)
  } catch {
    /* sessionStorage 不可用时静默 */
  }
}

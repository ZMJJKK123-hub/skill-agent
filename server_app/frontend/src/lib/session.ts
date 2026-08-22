import { useSyncExternalStore } from 'react'
import * as api from './api'
import type { EventItem, HistoryEntry } from './api'

// 会话/生成编排：一个对话 = 一个工作区文件夹（后端 /api/session 创建）
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

export interface SessionState {
  sessionId: string | null
  phase: 'idle' | 'creating' | 'running' | 'paused' | 'finished' | 'error'
  error: string | null
  title: string | null
  question: { question: string; options: string[] } | null
  // 多题提问（agent 一次问多个，前端草稿式确认）：
  questions: { question: string; options: string[] }[] | null
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
  paused: boolean            // 已暂停（可继续）
  pending: number            // 运行中排队消息数（>0 时当前轮结束后自动续跑）
  stoppedNotice: boolean     // 是否显示"您已终止该对话"横线
}

let state: SessionState = {
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
  stoppedNotice: false,
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
  // 运行中（creating/running）：消息排队（后端 pending），当前轮结束后自动续跑
  if (state.phase === 'creating' || state.phase === 'running') {
    if (state.sessionId) {
      try {
        await api.startTask(state.sessionId, prompt, mode, false, settings.model, settings.baseUrl,
          settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
          settings.autoMode, settings.searchApiKey)
        // 本地乐观显示排队消息（chat 模式）
        setState({
          chatMessages: [...state.chatMessages, { role: 'user', content: prompt }],
          pending: state.pending + 1,
        })
      } catch (e) {
        setState({ error: String((e as Error)?.message || e) })
      }
    }
    return
  }
  // 已暂停：发送 = 恢复运行 + 消息强注入
  // 后端 resume=true + 带 prompt 时：先 enqueue（写 pending+历史），
  // 再从断点恢复；恢复的 agent 第一轮 drain 到该消息作为 user 强行注入。
  if (state.paused && state.sessionId) {
    try {
      setState({ phase: 'running', paused: false, stoppedNotice: false, chatMessages: [...state.chatMessages, { role: 'user', content: prompt }] })
      await api.startTask(state.sessionId, prompt, state.mode ?? 'chat', true, settings.model, settings.baseUrl,
        settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
        settings.autoMode, settings.searchApiKey)
      void poll()
      startPolling(2000)
    } catch (e) {
      setState({ phase: 'paused', error: String((e as Error)?.message || e) })
    }
    return
  }
  setState({
    phase: 'creating',
    error: null,
    events: [],
    cursor: null,
    hasJar: false,
    elapsed: null,
    logTail: '',
    mode,
    paused: false,
    stoppedNotice: false,
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
        settings.visionEnabled,
        settings.visionApiKey,
        settings.visionBaseUrl,
        settings.visionModel,
        settings.autoMode,
        settings.searchApiKey,
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
    await api.startTask(sid, prompt, mode, false, settings.model, settings.baseUrl,
      settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
      settings.autoMode, settings.searchApiKey)
    void poll()
    void loadHistory()
  } catch (e) {
    setState({ phase: 'error', error: String((e as Error)?.message || e) })
  }
}

// 暂停当前运行的 agent（类似 sleep）：kill 子进程，断点已在磁盘
export async function pauseTask() {
  const sid = state.sessionId
  if (!sid) return
  try {
    await api.pauseTask(sid)
    setState({ phase: 'paused', paused: true, stoppedNotice: true })
    stopPolling()
  } catch (e) {
    setState({ error: String((e as Error)?.message || e) })
  }
}

// 继续：从断点恢复 agent 运行（新子进程加载 working.jsonl）
export async function resumeTask() {
  const sid = state.sessionId
  if (!sid) return
  setState({ phase: 'running', paused: false, stoppedNotice: false })
  try {
    await api.startTask(sid, '', state.mode ?? 'chat', true)
    void poll()
    startPolling(2000)
  } catch (e) {
    setState({ phase: 'paused', error: String((e as Error)?.message || e) })
  }
}

export async function poll() {
  const sid = state.sessionId
  if (!sid) return
  // 重入保护：poll 里有 3+ 个串行请求，慢网络下单次可能超过 2s 轮询间隔；
  // 不加保护时两次 poll 用同一个旧 cursor → 事件重复追加、自动续跑重复触发。
  if (pollInFlight) return
  pollInFlight = true
  try {
    await _pollOnce(sid)
  } finally {
    pollInFlight = false
  }
}

let pollInFlight = false

async function _pollOnce(sid: string) {
  try {
    const ev = await api.getEvents(sid, state.cursor ?? undefined)
    if (state.sessionId !== sid) return
    if (ev.events.length > 0) {
      setState({ events: [...state.events, ...ev.events], cursor: ev.cursor })
    }
    const st = await api.getStatus(sid)
    if (state.sessionId !== sid) return
    setState({
      elapsed: st.elapsed,
      hasJar: st.has_jar,
      logTail: st.log_tail,
      paused: st.paused,
      pending: st.pending ?? 0,
      phase: st.finished ? 'finished' : st.paused ? 'paused' : 'running',
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
    // 当前轮正常跑完 + 有排队消息 → 自动续跑处理排队消息
    if (st.finished && !st.paused && (st.pending ?? 0) > 0) {
      try {
        await api.startTask(sid, '', state.mode ?? 'chat', true)
        if (state.sessionId !== sid) return
        const prompts = [...state.prompts, `（自动续跑：处理 ${st.pending} 条排队消息）`]
        setState({ prompts, phase: 'running', pending: 0 })
        void loadHistory()
      } catch (e) {
        if (state.sessionId !== sid) return
        setState({ phase: 'finished', error: String((e as Error)?.message || e) })
      }
    }
    const q = await api.getQuestion(sid)
    if (state.sessionId !== sid) return
    if (q.status === 'pending' && q.questions && q.questions.length > 0) {
      // 多题：agent 一次问多个
      const qs = q.questions.map((it) => ({ question: it.question, options: it.options ?? [] }))
      setState({ questions: qs, question: null })
    } else if (q.status === 'pending' && q.question) {
      // 兼容单题
      setState({ question: { question: q.question, options: q.options ?? [] }, questions: null })
    } else if (state.question || state.questions) {
      setState({ question: null, questions: null })
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
  // 兜底：取最后一行（跳过各种 [前缀] 噪音行——工具/思考/待办/队友输出等）
  const noisePrefixes = ['[run_task]', '[思考]', '[todo]', '[reply]', '[tool]', '[tool-result]', '[teammate', '[subagent', '[supervisor']
  const lines = logTail.split(/\r?\n/).filter((l) => l.trim())
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim()
    if (line && !noisePrefixes.some((p) => line.startsWith(p))) {
      return line
    }
  }
  return null
}

// 打开历史会话时：加载该会话的对话历史（.chat/conversation.jsonl）+ 恢复模式
export async function loadConversation(sessionId: string) {
  try {
    const { messages, mode } = await api.getConversation(sessionId)
    setState({ chatMessages: messages, mode: mode ?? state.mode })
  } catch {
    /* 未登录/无历史时忽略 */
  }
}

// 提交回答：单题（legacy）或多题确认（answers 数组）
export async function answerQuestion(answer: string, answers?: { question: string; answer: string }[]) {
  const sid = state.sessionId
  if (!sid) return
  try {
    if (answers && answers.length > 0) {
      await api.answerQuestions(sid, answers)
    } else {
      await api.answerQuestion(sid, answer)
    }
  } catch {
    /* 提交失败也本地清掉，避免卡死界面 */
  }
  setState({ question: null, questions: null })
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
    questions: null,
    error: null,
    hasJar: false,
    elapsed: null,
    logTail: '',
    mode: null,
    chatMessages: [],
    paused: false,
    pending: 0,
    stoppedNotice: false,
  })
  void loadHistory()
}

// 从历史打开一个会话（查看产物/下载/继续对话，不重新生成）
// 关键：先停掉旧轮询，再恢复历史与模式——否则旧进程的 running 状态
// 会覆盖新会话的显示（实测：记录消失/屏幕空白/状态打架）。
export async function openHistorySession(id: string) {
  stopPolling()
  setState({ sessionId: id, phase: 'idle', events: [], cursor: null, prompts: [], title: null, error: null, mode: null, chatMessages: [], paused: false, pending: 0, stoppedNotice: false, question: null, questions: null })
  await loadConversation(id)
  // 单次探测状态：若该会话仍在运行则恢复轮询显示进行中
  void poll()
}

// 重新生成：重置当前会话骨架，回到可再发需求的空态
export async function regenerate() {
  const sid = state.sessionId
  if (!sid) return
  try {
    await api.resetSession(sid)
    setState({ phase: 'idle', events: [], cursor: null, prompts: [], error: null, hasJar: false, elapsed: null, logTail: '', mode: null, chatMessages: [], paused: false, pending: 0, stoppedNotice: false, question: null, questions: null })
  } catch (e) {
    setState({ error: String((e as Error)?.message || e) })
  }
}

// ============================================================================
// 【导入文件夹功能 - 已临时禁用】
// 说明：导入后 bug 较多，暂时注释停用；代码保留，后续扩展时恢复。
// ============================================================================
// // 导入已有 mod 文件夹：上传 zip → 后端解压成新会话工作区 → 回到可对话态
// export async function importWorkspace(files: ImportFile[], settings: GenSettings, title?: string) {
//   setState({ phase: 'creating', error: null, events: [], cursor: null, prompts: [], hasJar: false, elapsed: null, logTail: '', title: title ?? null })
//   try {
//     const { session_id } = await api.importSession(files, settings)
//     setState({ sessionId: session_id, phase: 'idle', title: title ?? null })
//     void loadHistory()
//   } catch (e) {
//     setState({ phase: 'error', error: String((e as Error)?.message || e) })
//   }
// }
// ============================================================================

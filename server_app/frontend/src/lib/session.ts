import { useSyncExternalStore } from 'react'
import * as api from './api'
import type { EventItem, HistoryEntry } from './api'
import { getUi } from './store'

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
  chatMessages: { role: string; content: string; images?: string[] }[]  // 聊天气泡历史（chat 模式；images=上传图片，本地为 data URL、历史加载为文件名）
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

// 当前活动会话指针（sessionStorage：刷新保留、关标签页即失效）。
// 此前刷新页面回到空白首页——正在跑的任务仍在后台正常执行，但界面上
// 完全看不到（运行中刷新是常见操作，实测缺陷）。刷新后据此自动恢复
// 会话视图，运行状态由轮询自动接管。
const ACTIVE_SID_KEY = 'modforge_active_sid'
function _rememberActiveSid(sid: string | null) {
  try {
    if (sid) sessionStorage.setItem(ACTIVE_SID_KEY, sid)
    else sessionStorage.removeItem(ACTIVE_SID_KEY)
  } catch {
    /* sessionStorage 不可用时静默 */
  }
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
// images: 用户随消息上传的图片（data URL），后端落盘后随消息传给视觉模型
export async function sendPrompt(prompt: string, settings: GenSettings, mode: 'chat' | 'mod' = 'chat', images: string[] = []) {
  // 运行中（creating/running）：消息排队（后端 pending），当前轮结束后自动续跑
  if (state.phase === 'creating' || state.phase === 'running') {
    if (state.sessionId) {
      try {
        await api.startTask(state.sessionId, prompt, mode, false, settings.apiKey, settings.model, settings.baseUrl,
          settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
          settings.autoMode, settings.searchApiKey, images)
        // 本地乐观显示排队消息：chat 模式走 chatMessages 气泡；
        // mod 模式只渲染 prompts，也要 push 进去（否则插话后界面无反馈）
        setState({
          prompts: [...state.prompts, prompt],
          chatMessages: [...state.chatMessages, { role: 'user', content: prompt, ...(images.length ? { images } : {}) }],
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
      // 暂停后发送 = 恢复 + 强注入。mod 模式也要把新消息加入 prompts，
      // 否则用户消息不会显示在左侧（mod 模式只渲染 prompts）。
      const prompts = state.mode === 'mod' ? [...state.prompts, prompt] : state.prompts
      setState({
        phase: 'running', paused: false, stoppedNotice: false,
        chatMessages: [...state.chatMessages, { role: 'user', content: prompt, ...(images.length ? { images } : {}) }],
        prompts,
      })
      await api.startTask(state.sessionId, prompt, state.mode ?? 'chat', true, settings.apiKey, settings.model, settings.baseUrl,
        settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
        settings.autoMode, settings.searchApiKey, images)
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
      _rememberActiveSid(session_id)
    }
    // mod 模式：先准备 mod 工作区（复制模板+源码，幂等）
    if (mode === 'mod') {
      await api.prepareModWorkspace(sid)
    }
    const prompts = [...state.prompts, prompt]
    // 标题：已有（文件夹名）优先，否则用首条输入截断；纯图片消息用固定占位
    const titleText = prompt.trim() || '图片消息'
    const title = state.title ?? (titleText.length > 24 ? titleText.slice(0, 24) + '…' : titleText)
    // 用户消息加入聊天气泡（chat 与 mod 都写：mod 模式的用户气泡也
    // 从 chatMessages 渲染，图片附件才能在运行中/历史里回显）
    const chatMessages = [
      ...state.chatMessages,
      { role: 'user' as const, content: prompt, ...(images.length ? { images } : {}) },
    ]
    setState({ prompts, phase: 'running', title, chatMessages })
    await api.startTask(sid, prompt, mode, false, settings.apiKey, settings.model, settings.baseUrl,
      settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
      settings.autoMode, settings.searchApiKey, images)
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
    const st = await api.getStatus(sid, getUi().apiKey)
    if (state.sessionId !== sid) return
    setState({
      elapsed: st.elapsed,
      hasJar: st.has_jar,
      logTail: st.log_tail,
      paused: st.paused,
      pending: st.pending ?? 0,
      phase: st.finished ? 'finished' : st.paused ? 'paused' : 'running',
    })
    // chat 模式：排队全部消化完的完成态重载磁盘对话历史（权威穿插顺序）。
    // 此前回复只留在事件流里、渲染在全部用户消息之后——连续多发时界面
    // 变成"问题一堆、回复一堆"。磁盘 conversation.jsonl 按"处理顺序"
    // 严格 u/a 交替（排队消息消费时才落盘），完成时以它为准覆盖本地。
    // 排队未消化完（pending>0）不覆盖：磁盘还没写到那些消息，覆盖会把
    // 本地乐观显示的排队气泡冲掉；等全部跑完再统一加载。
    if (st.finished && state.mode === 'chat' && (st.pending ?? 0) === 0) {
      void loadConversation(sid)
    }
    // mod 模式：完成时从后端拉对话历史，取最终总结渲染成气泡
    // （run_task 收尾把 agent 最终回复写入 conversation.jsonl；运行中不轮询它）
    if (st.finished && state.mode === 'mod') {
      const last = state.chatMessages[state.chatMessages.length - 1]
      if (!last || last.role !== 'assistant') {
        void loadConversation(sid)
      }
      // 完成时刷新侧栏：新会话标题在服务端落盘后这里才拿得到正确值
      // （此前发起瞬间 loadHistory 拿到的是裸 ID 前缀且不再更新）
      void loadHistory()
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
        const msg = String((e as Error)?.message || e)
        // daemon 自己 0.5s 就会消费排队消息：这里撞上它刚转 working 的
        // 409 属正常竞态（任务实际在跑），不算错误
        if (/409|already running|运行中/i.test(msg)) return
        setState({ phase: 'finished', error: msg })
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
// 返回是否成功（会话已被删除等场景返回 false，调用方据此回空态）
export async function loadConversation(sessionId: string): Promise<boolean> {
  try {
    const { messages, mode } = await api.getConversation(sessionId)
    // mod 模式：从历史恢复用户 prompt 气泡——此前 prompts 被清空后无人恢复，
    // 打开历史只见工具流水、看不到当时的 MOD 需求（实测缺陷）
    const userPrompts = mode === 'mod'
      ? messages.filter((m) => m.role === 'user').map((m) => m.content)
      : []
    setState({
      chatMessages: messages,
      mode: mode ?? state.mode,
      prompts: userPrompts.length > 0 ? userPrompts : state.prompts,
    })
    return true
  } catch {
    /* 会话不存在/网络失败 */
    return false
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
  _rememberActiveSid(null)
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
  _rememberActiveSid(id)
  const ok = await loadConversation(id)
  if (!ok) {
    // 会话已不存在（如已在别处删除而列表未刷新）：清指针回空态，
    // 避免刷新后永远恢复一个 404 会话
    _rememberActiveSid(null)
    void newConversation()
    return
  }
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

// 刷新恢复：模块加载时若本标签页 remembers 一个活动会话，自动恢复其视图
// （运行中的任务由 poll 探测接管，显示"进行中"；已删除的会话回空态）。
// 放在文件末尾：openHistorySession 已定义。
try {
  const _sid = sessionStorage.getItem(ACTIVE_SID_KEY)
  if (_sid) void openHistorySession(_sid)
} catch {
  /* sessionStorage 不可用时忽略 */
}

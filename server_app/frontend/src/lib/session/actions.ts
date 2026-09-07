/**
 * 会话动作（由 lib/session.ts 原样迁出）。
 *
 * sendPrompt 三分支：运行中排队 / 暂停恢复+强注入 / 新建或续发。
 */
import * as api from '../api'
import { state, setState, rememberActiveSid, type GenSettings } from './store'
import { poll, startPolling, stopPolling } from './polling'

export async function loadHistory() {
  try {
    const { sessions } = await api.getSessions()
    setState({ history: sessions })
  } catch {
    /* 服务不可达时忽略 */
  }
}

// 发起对话 → 建新工作区文件夹 → 启动生成 → 开始轮询
// mode: 'chat' | 'mod'；images: data URL 图片；forceMode: /chat 显式覆盖
export async function sendPrompt(prompt: string, settings: GenSettings, mode: 'chat' | 'mod' = 'chat', images: string[] = [], forceMode = false) {
  // 运行中：消息排队（后端 pending），当前轮结束后自动续跑
  if (state.phase === 'creating' || state.phase === 'running') {
    if (state.sessionId) {
      try {
        await api.startTask(state.sessionId, prompt, mode, false, settings.apiKey, settings.model, settings.baseUrl,
          settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
          settings.autoMode, settings.searchApiKey, images, forceMode)
        // 本地乐观显示排队消息（chat 走气泡；mod 也要 push 否则无反馈）
        setState({
          prompts: [...state.prompts, prompt],
          chatMessages: [...state.chatMessages, { role: 'user', content: prompt, ...(images.length ? { images } : {}) }],
          pending: state.pending + 1,
          lastSendAt: Date.now(),
        })
      } catch (e) {
        setState({ error: String((e as Error)?.message || e) })
      }
    }
    return
  }
  // 已暂停：发送 = 恢复运行 + 消息强注入（resume 后首轮 drain 该消息）
  if (state.paused && state.sessionId) {
    try {
      const prompts = state.mode === 'mod' && !forceMode ? [...state.prompts, prompt] : state.prompts
      // /chat（forceMode）以 chat 恢复：mode.txt 已在 server 端更新
      const resumeMode = forceMode ? mode : (state.mode ?? 'chat')
      setState({
        phase: 'running', paused: false, stoppedNotice: false, elapsed: null, lastSendAt: Date.now(),
        // 暂停后 /chat 切回必须同步本地 mode，否则 UI 按 mod 渲染（实测修复）
        mode: resumeMode,
        chatMessages: [...state.chatMessages, { role: 'user', content: prompt, ...(images.length ? { images } : {}) }],
        prompts,
      })
      await api.startTask(state.sessionId, prompt, resumeMode, true, settings.apiKey, settings.model, settings.baseUrl,
        settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
        settings.autoMode, settings.searchApiKey, images, forceMode)
      void poll()
      startPolling(2000)
    } catch (e) {
      setState({ phase: 'paused', error: String((e as Error)?.message || e) })
    }
    return
  }
  // 事件流只在开全新会话时清空：已有会话发下一轮保留——事件 id 稳定，
  // 思考/工具行组件不重挂载，手动展开状态不丢（实测缺陷）
  const freshSession = !state.sessionId
  setState({
    phase: 'creating',
    error: null,
    ...(freshSession ? { events: [], cursor: null } : {}),
    hasJar: false,
    elapsed: null,
    logTail: '',
    mode,
    paused: false,
    stoppedNotice: false,
    lastSendAt: Date.now(),
  })
  try {
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
      rememberActiveSid(session_id)
    }
    const prompts = [...state.prompts, prompt]
    // 标题：已有优先，否则首条输入截断；纯图片消息固定占位
    const titleText = prompt.trim() || '图片消息'
    const title = state.title ?? (titleText.length > 24 ? titleText.slice(0, 24) + '…' : titleText)
    // 用户消息加入聊天气泡（chat 与 mod 都写：图片附件才能回显）
    const chatMessages = [
      ...state.chatMessages,
      { role: 'user' as const, content: prompt, ...(images.length ? { images } : {}) },
    ]
    // 先上屏用户气泡与 running 态，再复制模板：prepareModWorkspace 耗时数秒，
    // 若等它完成才切 phase，确认条关闭后会短暂回退空态首页
    setState({ prompts, phase: 'running', title, chatMessages })
    // mod 模式：准备 mod 工作区（复制模板+源码，幂等）
    if (mode === 'mod') {
      await api.prepareModWorkspace(sid)
    }
    await api.startTask(sid, prompt, mode, false, settings.apiKey, settings.model, settings.baseUrl,
      settings.visionEnabled, settings.visionApiKey, settings.visionBaseUrl, settings.visionModel,
      settings.autoMode, settings.searchApiKey, images, forceMode)
    void poll()
    void loadHistory()
  } catch (e) {
    setState({ phase: 'error', error: String((e as Error)?.message || e) })
  }
}

// 暂停当前运行的 agent：kill 子进程，断点已在磁盘
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
  // elapsed 归零：恢复 = 新一轮计时
  setState({ phase: 'running', paused: false, stoppedNotice: false, elapsed: null })
  try {
    await api.startTask(sid, '', state.mode ?? 'chat', true)
    void poll()
    startPolling(2000)
  } catch (e) {
    setState({ phase: 'paused', error: String((e as Error)?.message || e) })
  }
}

// 打开历史会话：加载对话历史 + 恢复模式；返回是否成功（已删除等返回 false）
export async function loadConversation(sessionId: string): Promise<boolean> {
  try {
    const { messages, mode } = await api.getConversation(sessionId)
    // mod 模式：恢复用户 prompt 气泡（否则只见工具流水，实测缺陷）
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

// 新建对话：回到从零生成的空态（不删历史，只清当前状态）
export async function newConversation() {
  stopPolling()
  rememberActiveSid(null)
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

// 从历史打开会话（查看/继续，不重新生成）。先停旧轮询再恢复——否则旧
// 进程的 running 状态覆盖新会话显示（实测：记录消失/状态打架）。
export async function openHistorySession(id: string) {
  stopPolling()
  setState({ sessionId: id, phase: 'idle', events: [], cursor: null, prompts: [], title: null, error: null, mode: null, chatMessages: [], paused: false, pending: 0, stoppedNotice: false, question: null, questions: null, elapsed: null })
  rememberActiveSid(id)
  const ok = await loadConversation(id)
  if (!ok) {
    // 会话已不存在：清指针回空态，避免刷新后永远恢复 404 会话
    rememberActiveSid(null)
    void newConversation()
    return
  }
  // 单次探测状态：仍在运行则恢复轮询显示进行中
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

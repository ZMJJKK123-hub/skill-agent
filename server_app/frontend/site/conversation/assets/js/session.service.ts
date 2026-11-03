// 契约将会话业务与 HTTP、React、存储及浏览器计时器解耦。
import type { GenSettings, QuestionAnswer, SessionController, SessionDependencies, SessionMode, SessionState } from './session.types.ts'
// 纯模型负责初始状态、事件去重、提问归一化与旧日志回退。
import { appendEvents, emptySession, extractFinalReply, pendingQuestions, phaseFromStatus } from './session.model.ts'
// 异常在业务边界转为界面文本；统一日志器提取分类和脱敏调用帧。
import { errorMessage, errorType, FrontendError } from '../../../assets/js/errors.ts'

/** 创建一份会话控制器。
 * Args: 仓储、状态、计时器、下载端口、配置、日志和当前设置均由组合根注入。
 * Returns: SessionController；可恢复失败写入 state.error，下载失败向调用者传播。
 * 新建/切换/暂停/重置/退出账户都会隔离旧异步结果，dispose 清理轮询。
 * Globals Used: None。Dependencies: SessionRepository、纯模型、注入端口。
 */
export function createSessionService(deps: SessionDependencies): SessionController {
  const { repository: repo, store, timer, downloads, config, logger } = deps
  let revision = 0
  let accountRevision = 0
  let pollTimer: number | null = null
  let inFlight: { revision: number; promise: Promise<void> } | null = null
  let disposed = false
  const snapshot = (): SessionState => store.getSnapshot()
  const current = (id: string, version: number): boolean => !disposed && revision === version && snapshot().sessionId === id

  /** 只在当前操作仍拥有会话时展示失败；日志不含提示词、会话 ID 或响应正文。 */
  function fail(operation: string, error: unknown, version: number, phase?: SessionState['phase']): void {
    logger.write('error', 'session.operation_failed', { operation, errorType: errorType(error) }, error)
    if (!disposed && revision === version) store.set({ error: errorMessage(error), ...(phase ? { phase } : {}) })
  }

  /** 停止后续定时触发；已发请求通过 revision 校验决定是否还能更新状态。 */
  function stopPolling(): void {
    if (pollTimer !== null) timer.clearInterval(pollTimer)
    pollTimer = null
  }

  /** 账户变化后丢弃旧列表结果；未登录/网络失败不会清空已有列表。 */
  async function loadHistory(): Promise<void> {
    const version = accountRevision
    try {
      const result = await repo.list()
      if (!disposed && accountRevision === version) store.set({ history: result.sessions })
    } catch (error: unknown) {
      logger.write('warning', 'history.load_failed', { errorType: errorType(error) })
    }
  }

  /** 单次轮询依次读取事件、状态和问题；每次 await 后重新校验所属会话。 */
  async function pollOnce(id: string, version: number): Promise<void> {
    try {
      const events = await repo.events(id, snapshot().cursor ?? undefined)
      if (!current(id, version)) return
      store.set({ events: appendEvents(snapshot().events, events.events), cursor: events.cursor })
      const status = await repo.status(id)
      if (!current(id, version)) return
      store.set({ elapsed: status.elapsed, hasJar: status.has_jar, logTail: status.log_tail,
        paused: status.paused ?? false, pending: status.pending ?? 0, phase: phaseFromStatus(status) })
      if (status.finished && snapshot().mode === 'chat' && !snapshot().events.some((event): boolean => event.type === 'reply')) {
        const messages = snapshot().chatMessages
        const reply = extractFinalReply(status.log_tail)
        if (messages[messages.length - 1]?.role !== 'assistant' && reply) store.set({ chatMessages: [...messages, { role: 'assistant', content: reply }] })
      }
      if (status.finished && !status.paused && (status.pending ?? 0) > 0) {
        await repo.start({ sessionId: id, prompt: '', mode: snapshot().mode ?? 'chat', resume: true, settings: deps.getSettings() })
        if (!current(id, version)) return
        store.set({ phase: 'running', pending: 0 })
      }
      const question = await repo.question(id)
      if (!current(id, version)) return
      store.set({ questions: pendingQuestions(question), question: null })
    } catch (error: unknown) {
      logger.write('warning', 'session.poll_failed', { errorType: errorType(error) })
      if (current(id, version) && error instanceof FrontendError && error.status === 401) {
        stopPolling()
        store.set({ error: '登录已失效，请重新登录', phase: 'error' })
      }
    }
  }

  /** 同一轮询世代只有一个请求链；切换会话可立即发起新世代请求，不等待旧网络。 */
  async function poll(): Promise<void> {
    const id = snapshot().sessionId
    if (!id || disposed) return
    if (inFlight?.revision === revision) return inFlight.promise
    const token = { revision, promise: pollOnce(id, revision) }
    inFlight = token
    try { await token.promise } finally { if (inFlight === token) inFlight = null }
  }

  /** 幂等启动轮询；非正数时间回退配置值，重复调用不创建第二个计时器。 */
  function startPolling(intervalMs = config.pollingIntervalMs): void {
    if (pollTimer !== null || disposed) return
    pollTimer = timer.setInterval((): void => { void poll() }, intervalMs > 0 ? intervalMs : config.pollingIntervalMs)
  }

  /** 新建仅清理当前展示，不删除服务器历史；旧请求不能写回新对话。 */
  async function newConversation(): Promise<void> {
    revision += 1
    stopPolling()
    store.set(emptySession(snapshot().history))
    void loadHistory()
  }

  /** 发送时按空闲/运行中/暂停分支编排既有接口；不创建任何后端新协议。 */
  async function sendPrompt(prompt: string, settings: GenSettings, mode: SessionMode = 'chat'): Promise<void> {
    if (!prompt.trim() || disposed) return
    const version = revision
    const initial = snapshot()
    if (!settings.apiKey.trim()) { store.set({ error: '请先在设置中填写 API Key' }); return }
    // 既有后端 daemon 的运行模式在启动时固定，显式 /mod 转换必须新建会话。
    if (mode === 'mod' && initial.mode === 'chat') {
      await newConversation()
      return sendPrompt(prompt, settings, 'mod')
    }
    if (initial.phase === 'creating' && !initial.sessionId) {
      store.set({ error: '工作区正在创建，请稍候再发送' })
      return
    }
    if ((initial.phase === 'creating' || initial.phase === 'running') && initial.sessionId) {
      try {
        await repo.start({ sessionId: initial.sessionId, prompt, mode: initial.mode ?? mode, resume: false, settings })
        if (!current(initial.sessionId, version)) return
        store.set({ prompts: [...snapshot().prompts, prompt], chatMessages: [...snapshot().chatMessages, { role: 'user', content: prompt }], pending: snapshot().pending + 1, error: null })
      } catch (error: unknown) { fail('queue', error, version) }
      return
    }
    const resume = initial.paused && initial.sessionId !== null
    const effectiveMode = initial.mode ?? mode
    store.set({ phase: resume ? 'running' : 'creating', error: null, paused: false, stoppedNotice: false,
      ...(resume ? {} : { events: [], cursor: null, hasJar: false, elapsed: null, logTail: '', mode: effectiveMode }) })
    try {
      let id = initial.sessionId
      if (!id) {
        const created = await repo.create(settings)
        if (disposed || version !== revision) return
        id = created.session_id
        store.set({ sessionId: id })
      }
      if (effectiveMode === 'mod' && !resume) {
        await repo.prepare(id)
        if (!current(id, version)) return
      }
      store.set({ prompts: [...snapshot().prompts, prompt], phase: 'running', mode: effectiveMode,
        title: initial.title ?? (prompt.length > config.titleLimit ? `${prompt.slice(0, config.titleLimit)}…` : prompt),
        chatMessages: effectiveMode === 'chat' || resume ? [...snapshot().chatMessages, { role: 'user', content: prompt }] : snapshot().chatMessages })
      await repo.start({ sessionId: id, prompt, mode: effectiveMode, resume, settings })
      if (!current(id, version)) return
      void poll()
      startPolling()
      void loadHistory()
    } catch (error: unknown) {
      fail('send', error, version, resume ? 'paused' : 'error')
      if (resume && version === revision) store.set({ paused: true })
    }
  }

  /** 暂停前隔离旧轮询；失败恢复运行展示与轮询，成功保留断点会话。 */
  async function pauseTask(): Promise<void> {
    const id = snapshot().sessionId
    if (!id) return
    const version = ++revision
    stopPolling()
    try {
      await repo.pause(id)
      if (current(id, version)) store.set({ phase: 'paused', paused: true, stoppedNotice: true, error: null })
    } catch (error: unknown) { fail('pause', error, version); if (current(id, version)) startPolling() }
  }

  /** 使用当前用户设置恢复已有会话；失败保留暂停状态供重试。 */
  async function resumeTask(): Promise<void> {
    const id = snapshot().sessionId
    if (!id) return
    const version = revision
    store.set({ phase: 'running', paused: false, stoppedNotice: false, error: null })
    try {
      await repo.start({ sessionId: id, prompt: '', mode: snapshot().mode ?? 'chat', resume: true, settings: deps.getSettings() })
      if (!current(id, version)) return
      void poll()
      startPolling()
    } catch (error: unknown) { fail('resume', error, version, 'paused'); if (current(id, version)) store.set({ paused: true }) }
  }

  /** 历史打开后只读恢复消息及运行状态；旧会话的加载结果不得覆盖新选择。 */
  async function openHistorySession(id: string): Promise<void> {
    const version = ++revision
    stopPolling()
    store.set({ ...emptySession(snapshot().history), sessionId: id })
    try {
      const conversation = await repo.conversation(id)
      if (!current(id, version)) return
      store.set({ chatMessages: conversation.messages, mode: conversation.mode })
      await poll()
      if (current(id, version) && snapshot().phase === 'running') startPolling()
    } catch (error: unknown) { fail('open_history', error, version, 'error') }
  }

  /** 回答写入成功才清问题；失败保留问题及界面草稿，允许用户重试。 */
  async function answerQuestion(answer: string, answers?: QuestionAnswer[]): Promise<void> {
    const id = snapshot().sessionId
    if (!id) return
    const version = revision
    try {
      await repo.answer(id, answer, answers)
      if (current(id, version)) store.set({ question: null, questions: null, error: null })
    } catch (error: unknown) { fail('answer', error, version) }
  }

  /** reset 仅调用现有后端；失败保留当前信息，成功清理展示并保留会话 ID。 */
  async function regenerate(): Promise<void> {
    const id = snapshot().sessionId
    if (!id) return
    const mode = snapshot().mode
    const version = ++revision
    stopPolling()
    try {
      await repo.reset(id)
      if (current(id, version)) store.set({ ...emptySession(snapshot().history), sessionId: id, mode })
    } catch (error: unknown) { fail('reset', error, version); if (current(id, version) && snapshot().phase === 'running') startPolling() }
  }

  /** 删除成功后刷新列表；删除当前会话同时清理展示，失败保持历史并展示错误。 */
  async function deleteSession(id: string): Promise<void> {
    const version = revision
    try {
      await repo.remove(id)
      if (current(id, version)) { revision += 1; stopPolling(); store.set(emptySession(snapshot().history)) }
      if (!disposed) await loadHistory()
    } catch (error: unknown) { fail('delete', error, version) }
  }

  /** 下载前只请求原有产物路由；保存失败和 HTTP 失败均传播给组件显示。 */
  async function download(id: string, kind: 'jar' | 'source'): Promise<void> {
    const blob = await repo.download(id, kind)
    downloads.save(blob, kind === 'jar' ? `mod-${id}.jar` : `mod-${id}-src.zip`)
  }

  /** 用户退出/切换时隔离正在返回的请求，同时清空列表，防止跨账户展示。 */
  function clearAccount(): void {
    revision += 1
    accountRevision += 1
    stopPolling()
    store.set(emptySession())
  }

  return {
    loadHistory, sendPrompt, pauseTask, resumeTask, poll, answerQuestion, startPolling, stopPolling,
    newConversation, openHistorySession, regenerate, deleteSession, clearAccount,
    downloadJar: (id: string): Promise<void> => download(id, 'jar'),
    downloadSourceZip: (id: string): Promise<void> => download(id, 'source'),
    dispose(): void { disposed = true; revision += 1; accountRevision += 1; stopPolling() },
  }
}

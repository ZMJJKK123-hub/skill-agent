// 内置测试覆盖业务状态和延迟响应，不启动真实模型或后端。
import { test } from 'node:test'
// 断言针对用户可见状态、请求顺序和生命周期。
import assert from 'node:assert/strict'
// 正式服务、状态及纯计算模型接受内存替身。
import { createSessionService } from '../site/conversation/assets/js/session.service.ts'
// 每份测试拥有独立快照。
import { createSessionStore } from '../site/conversation/assets/js/session.store.ts'
// 模型检查不包含网络 I/O。
import { appendEvents, extractFinalReply, pendingQuestions, phaseFromStatus } from '../site/conversation/assets/js/session.model.ts'
// 共用实际配置避免测试建立第二套路由定义。
import { DEFAULT_CONFIG } from '../site/assets/js/config.ts'
// 测试不把请求正文发送到控制台。
import { createLogger } from '../site/assets/js/logger.ts'
// 所有替身满足正式仓储契约。
import type { ConversationResponse, EventItem, EventsResponse, GenSettings, SessionRepository, StatusResponse, TaskInput } from '../site/conversation/assets/js/session.types.ts'

/** 非敏感测试设置，不对应真实服务凭据。 */
const settings: GenSettings = { apiKey: 'fixture', game: 'minecraft', loader: 'forge', version: '1.21.11', model: 'fixture', baseUrl: 'https://fixture.invalid', sandbox: 'workspace-write', visionEnabled: false, visionApiKey: '', visionBaseUrl: '', visionModel: '', autoMode: false, searchApiKey: '' }
/** 运行中响应由测试按分支覆盖。 */
const running: StatusResponse = { session_id: 'one', state: 'running', running: true, finished: false, started_at: null, finished_at: null, elapsed: 2, file_count: 0, total_bytes: 0, has_jar: false, log_tail: '' }

/** 延迟请求用于复现会话切换竞态；由测试显式 resolve，无计时等待。 */
function deferred<T>(): { promise: Promise<T>; resolve(value: T): void } {
  let done!: (value: T) => void
  const promise = new Promise<T>((resolve): void => { done = resolve })
  return { promise, resolve: done }
}

/** 创建独立服务及可观察请求/计时器；未覆盖接口返回合法空响应。 */
function harness(overrides: Partial<SessionRepository> = {}) {
  const calls: string[] = []; const tasks: TaskInput[] = []; const saved: string[] = []
  const timers = new Map<number, () => void>(); let nextTimer = 0
  const store = createSessionStore()
  const repository: SessionRepository = {
    create: async () => { calls.push('create'); return { session_id: 'one', mod_dir: 'unused' } },
    prepare: async (): Promise<void> => { calls.push('prepare') },
    start: async (input): Promise<void> => { calls.push('start'); tasks.push(input) },
    pause: async (): Promise<void> => { calls.push('pause') }, reset: async (): Promise<void> => { calls.push('reset') },
    remove: async (): Promise<void> => { calls.push('remove') }, list: async () => ({ sessions: [] }),
    conversation: async (id) => ({ session_id: id, messages: [], mode: 'chat' }),
    events: async (id) => ({ session_id: id, events: [], cursor: { run: 10, agent: 0 } }),
    status: async () => running, question: async () => ({ status: 'none' }), answer: async (): Promise<void> => undefined,
    download: async () => new Blob(['fixture']), ...overrides,
  }
  const service = createSessionService({ repository, store, config: DEFAULT_CONFIG, logger: createLogger(), getSettings: (): GenSettings => settings,
    timer: { setInterval(callback): number { const id = ++nextTimer; timers.set(id, callback); return id }, clearInterval(id): void { timers.delete(id) } },
    downloads: { save(_blob, filename): void { saved.push(filename) } },
  })
  return { service, store, calls, tasks, timers, saved }
}

test('send: chat creates once, mod prepares template before task, empty key does not send', async (): Promise<void> => {
  const chat = harness(); await chat.service.sendPrompt('hello', settings); await chat.service.poll()
  assert.deepEqual(chat.calls, ['create', 'start']); assert.equal(chat.store.getSnapshot().chatMessages[0].content, 'hello'); chat.service.dispose()
  const mod = harness(); await mod.service.sendPrompt('sword', settings, 'mod'); await mod.service.poll()
  assert.deepEqual(mod.calls, ['create', 'prepare', 'start']); assert.equal(mod.tasks[0].mode, 'mod'); mod.service.dispose()
  const invalid = harness(); await invalid.service.sendPrompt('hello', { ...settings, apiKey: '' }); assert.equal(invalid.calls.length, 0)
})

test('send: running messages queue; paused messages resume with the current mode/settings', async (): Promise<void> => {
  const h = harness(); h.store.set({ sessionId: 'one', phase: 'running', mode: 'mod' })
  await h.service.sendPrompt('add food', settings)
  assert.equal(h.store.getSnapshot().pending, 1); assert.equal(h.tasks[0].mode, 'mod'); assert.equal(h.tasks[0].resume, false)
  h.store.set({ phase: 'paused', paused: true }); await h.service.sendPrompt('continue', settings); await h.service.poll()
  assert.equal(h.tasks[1].resume, true); assert.equal(h.tasks[1].settings?.apiKey, settings.apiKey); h.service.dispose()
})

test('mode compatibility: explicit mod starts a new session; follow-up text keeps mod mode', async (): Promise<void> => {
  const h = harness({ create: async () => ({ session_id: 'new_mod', mod_dir: 'unused' }) })
  h.store.set({ sessionId: 'old_chat', mode: 'chat', phase: 'finished' })
  await h.service.sendPrompt('sword', settings, 'mod'); await h.service.poll()
  assert.equal(h.tasks[0].sessionId, 'new_mod'); assert.equal(h.tasks[0].mode, 'mod')
  h.store.set({ phase: 'finished' }); await h.service.sendPrompt('add a recipe', settings); await h.service.poll()
  assert.equal(h.tasks[1].sessionId, 'new_mod'); assert.equal(h.tasks[1].mode, 'mod'); h.service.dispose()
})

test('failures: create, queued send, reset and pause keep actionable UI states', async (): Promise<void> => {
  const broken = async (): Promise<never> => { throw new Error('offline') }
  const create = harness({ create: broken }); await create.service.sendPrompt('hello', settings); assert.equal(create.store.getSnapshot().phase, 'error')
  const queue = harness({ start: broken }); queue.store.set({ sessionId: 'one', phase: 'running' }); await queue.service.sendPrompt('hello', settings); assert.equal(queue.store.getSnapshot().pending, 0); assert.ok(queue.store.getSnapshot().error)
  const reset = harness({ reset: broken }); reset.store.set({ sessionId: 'one', prompts: ['keep'] }); await reset.service.regenerate(); assert.deepEqual(reset.store.getSnapshot().prompts, ['keep'])
  const pause = harness({ pause: broken }); pause.store.set({ sessionId: 'one', phase: 'running' }); await pause.service.pauseTask(); assert.equal(pause.store.getSnapshot().phase, 'running'); assert.equal(pause.timers.size, 1); pause.service.dispose()
})

test('pause/resume: stops timers, retains session, and restores current configuration', async (): Promise<void> => {
  const h = harness(); h.store.set({ sessionId: 'one', phase: 'running', mode: 'mod' }); h.service.startPolling(); h.service.startPolling()
  assert.equal(h.timers.size, 1); await h.service.pauseTask(); assert.equal(h.timers.size, 0); assert.equal(h.store.getSnapshot().paused, true)
  await h.service.resumeTask(); await h.service.poll(); assert.equal(h.tasks[0].resume, true); assert.equal(h.timers.size, 1); h.service.dispose(); assert.equal(h.timers.size, 0)
})

test('poll: failed answer retains question; successful answer clears it', async (): Promise<void> => {
  let reject = true
  const h = harness({ answer: async (): Promise<void> => { if (reject) throw new Error('offline') } })
  h.store.set({ sessionId: 'one', questions: [{ question: 'color?', options: ['blue'] }] })
  await h.service.answerQuestion('blue'); assert.equal(h.store.getSnapshot().questions?.[0].question, 'color?'); assert.ok(h.store.getSnapshot().error)
  reject = false; await h.service.answerQuestion('blue'); assert.equal(h.store.getSnapshot().questions, null)
})

test('poll: late event response cannot overwrite a new conversation', async (): Promise<void> => {
  const response = deferred<EventsResponse>()
  const h = harness({ events: () => response.promise }); h.store.set({ sessionId: 'one', phase: 'running' })
  const request = h.service.poll(); await h.service.newConversation()
  response.resolve({ session_id: 'one', events: [{ id: 'old', ts: 0, type: 'reply', source: 'run', content: 'old' }], cursor: { run: 1, agent: 1 } }); await request
  assert.equal(h.store.getSnapshot().sessionId, null); assert.equal(h.store.getSnapshot().events.length, 0)
})

test('history: slow old selection cannot overwrite a later selected conversation', async (): Promise<void> => {
  const first = deferred<ConversationResponse>()
  const h = harness({ conversation: (id) => id === 'first' ? first.promise : Promise.resolve({ session_id: id, messages: [{ role: 'user', content: 'second' }], mode: 'chat' }) })
  const request = h.service.openHistorySession('first'); await h.service.openHistorySession('second')
  first.resolve({ session_id: 'first', messages: [{ role: 'user', content: 'first' }], mode: 'chat' }); await request
  assert.equal(h.store.getSnapshot().sessionId, 'second'); assert.equal(h.store.getSnapshot().chatMessages[0].content, 'second'); h.service.dispose()
})

test('poll: reentry shares one request and empty event response still advances cursor', async (): Promise<void> => {
  let calls = 0; const events = deferred<EventsResponse>()
  const h = harness({ events: () => { calls += 1; return events.promise } }); h.store.set({ sessionId: 'one' })
  const first = h.service.poll(); const second = h.service.poll(); assert.equal(calls, 1)
  events.resolve({ session_id: 'one', events: [], cursor: { run: 9, agent: 2 } }); await Promise.all([first, second])
  assert.deepEqual(h.store.getSnapshot().cursor, { run: 9, agent: 2 })
})

test('account: old history response is discarded after logout', async (): Promise<void> => {
  const history = deferred<Awaited<ReturnType<SessionRepository['list']>>>()
  const h = harness({ list: () => history.promise }); const request = h.service.loadHistory(); h.service.clearAccount()
  history.resolve({ sessions: [{ sessionId: 'old', owner: 'other', has_jar: false, date: '' }] }); await request
  assert.equal(h.store.getSnapshot().history.length, 0)
})

test('reset/delete/download: preserves ID on reset, clears deleted selection, passes binary to download port', async (): Promise<void> => {
  const h = harness(); h.store.set({ sessionId: 'one', phase: 'finished', mode: 'mod', prompts: ['old'] })
  await h.service.regenerate(); assert.equal(h.store.getSnapshot().sessionId, 'one'); assert.equal(h.store.getSnapshot().mode, 'mod'); assert.deepEqual(h.store.getSnapshot().prompts, [])
  await h.service.downloadJar('one'); await h.service.downloadSourceZip('one'); assert.deepEqual(h.saved, ['mod-one.jar', 'mod-one-src.zip'])
  await h.service.deleteSession('one'); assert.equal(h.store.getSnapshot().sessionId, null)
})

test('models: paused status wins, events deduplicate, legacy questions and log fallback stay compatible', (): void => {
  assert.equal(phaseFromStatus({ ...running, finished: true, paused: true }), 'paused')
  const event: EventItem = { id: 'a', ts: 0, type: 'reply', source: 'run', content: 'ok' }
  assert.equal(appendEvents([event], [event]).length, 1)
  assert.deepEqual(pendingQuestions({ status: 'pending', question: 'one?' }), [{ question: 'one?', options: [] }])
  assert.equal(pendingQuestions({ status: 'none' }), null)
  assert.equal(extractFinalReply('[run_task] 最终回复:\nhello'), 'hello'); assert.equal(extractFinalReply('[tool] noise'), null)
})

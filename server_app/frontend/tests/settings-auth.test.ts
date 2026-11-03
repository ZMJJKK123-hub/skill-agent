// Node 内置测试与断言用于可离线运行的前端契约检查。
import { test } from 'node:test'
// 断言只检查可观测行为，不依赖 React 渲染实现。
import assert from 'node:assert/strict'
// 默认配置与测试配置使用同一契约。
import { DEFAULT_CONFIG } from '../site/assets/js/config.ts'
// 纯计算边界覆盖损坏持久化和模型回退。
import { defaultUiState, restoreUiState, resolveModelConfig } from '../site/settings/assets/js/settings.model.ts'
// 存储、状态和日志用内存端口注入。
import { createSettingsRepository } from '../site/settings/assets/js/settings.repository.ts'
// 通用容器便于验证隔离状态。
import { createStateStore } from '../site/assets/js/state-store.ts'
// 认证服务与令牌仓储分别验证。
import { createAuthService } from '../site/user_auth/assets/js/auth.service.ts'
// 令牌存储需要覆盖浏览器存储不可用的回退。
import { createTokenStore } from '../site/user_auth/assets/js/auth.repository.ts'
// 标准异常用于明确区分网络失败和过期。
import { FrontendError } from '../site/assets/js/errors.ts'
// 日志收集器只接收安全元数据。
import { createLogger } from '../site/assets/js/logger.ts'
// 类型约束让测试替身与实际业务接口一致。
import type { AuthRepository, TokenStore } from '../site/user_auth/assets/js/auth.types.ts'
// 只替代认证层使用的会话清理接口。
import type { SessionController } from '../site/conversation/assets/js/session.types.ts'
// 内存存储与日志实体契约。
import type { LogEntry, StoragePort } from '../site/assets/js/contracts.ts'
// 设置状态类型不重复定义在测试中。
import type { UiStore } from '../site/settings/assets/js/settings.types.ts'

/** 创建无磁盘副作用的认证夹具；失败由调用方提供的 me 控制。 */
function authHarness(me: AuthRepository['me']): {
  auth: ReturnType<typeof createAuthService>; tokens: TokenStore
  ui: UiStore; logs: LogEntry[]; cleared: () => number
} {
  const data = new Map<string, string>()
  const storage: StoragePort = { getItem: (key: string): string | null => data.get(key) ?? null,
    setItem: (key: string, value: string): void => { data.set(key, value) }, removeItem: (key: string): void => { data.delete(key) } }
  const logs: LogEntry[] = []
  const logger = createLogger((entry: LogEntry): void => { logs.push(entry) })
  const tokens = createTokenStore(storage, 'test-token', logger)
  const ui = createStateStore(defaultUiState(DEFAULT_CONFIG))
  let clears = 0
  const session = { clearAccount: (): void => { clears += 1 } } as Pick<SessionController, 'clearAccount'>
  const repository: AuthRepository = { me, login: async () => ({ username: 'alice', token: 'fixture-token' }),
    register: async () => ({ username: 'alice', token: 'fixture-token' }), logout: async (): Promise<void> => undefined }
  const auth = createAuthService(repository, tokens, ui, session, logger)
  return { auth, tokens, ui, logs, cleared: (): number => clears }
}

test('settings: invalid fields fall back independently and runtime/account state is ignored', (): void => {
  const state = restoreUiState({ locale: 'bad', theme: 'light', providers: [null, {}], disabledPlugins: ['modforge-settings', 'modforge-games', 12], user: { username: 'other' }, autoMode: true }, DEFAULT_CONFIG)
  assert.equal(state.locale, 'zh'); assert.equal(state.theme, 'light'); assert.equal(state.user, null)
  assert.deepEqual(state.providers, []); assert.deepEqual(state.disabledPlugins, ['modforge-games']); assert.equal(state.autoMode, true)
})

test('settings: custom model resolves to its provider; unknown model falls back', (): void => {
  const state = defaultUiState(DEFAULT_CONFIG)
  state.providers = [{ id: 'p', name: 'fixture', baseUrl: 'https://fixture.invalid', apiKey: 'not-a-secret', model: 'one, two', protocol: 'openai' }]
  state.model = 'two'
  assert.equal(resolveModelConfig(state, DEFAULT_CONFIG).baseUrl, 'https://fixture.invalid')
  state.model = 'missing'; assert.equal(resolveModelConfig(state, DEFAULT_CONFIG).model, DEFAULT_CONFIG.officialModel)
})

test('settings: malformed JSON and unavailable storage emit safe diagnostics', (): void => {
  const logs: LogEntry[] = []
  const storage: StoragePort = { getItem: (): string => '{', setItem: (): never => { throw new Error('sensitive-value') }, removeItem: (): void => undefined }
  const repo = createSettingsRepository(storage, 'test', createLogger((entry: LogEntry): void => { logs.push(entry) }))
  assert.equal(repo.load(), null)
  const { settingsOpen: _a, user: _b, activeWorkspace: _c, viewMode: _d, toast: _e, ...settings } = defaultUiState(DEFAULT_CONFIG)
  repo.save(settings)
  assert.equal(logs.length, 2); assert.ok(!JSON.stringify(logs).includes('sensitive-value'))
})

test('auth: network failure preserves token; explicit expiration clears account', async (): Promise<void> => {
  const network = authHarness(async (): Promise<never> => { throw new FrontendError('NetworkError', 'offline') })
  network.tokens.set('fixture-token'); await network.auth.restore()
  assert.equal(network.tokens.get(), 'fixture-token'); assert.equal(network.cleared(), 0)
  const expired = authHarness(async (): Promise<never> => { throw new FrontendError('HttpError', 'expired', 401) })
  expired.tokens.set('fixture-token'); await expired.auth.restore()
  assert.equal(expired.tokens.get(), null); assert.equal(expired.cleared(), 1)
})

test('auth: login updates user only after success and logout clears session', async (): Promise<void> => {
  const harness = authHarness(async () => ({ username: 'alice' }))
  await harness.auth.login('alice', 'fixture-password')
  assert.equal(harness.ui.getSnapshot().user?.username, 'alice'); assert.equal(harness.cleared(), 1)
  await harness.auth.logout()
  assert.equal(harness.ui.getSnapshot().user, null); assert.equal(harness.tokens.get(), null); assert.equal(harness.cleared(), 2)
})

test('auth: late restore cannot reintroduce a logged-out user', async (): Promise<void> => {
  let resolve!: (value: { username: string }) => void
  const harness = authHarness(() => new Promise((done): void => { resolve = done }))
  harness.tokens.set('fixture-token'); const request = harness.auth.restore()
  await harness.auth.logout(); resolve({ username: 'alice' }); await request
  assert.equal(harness.ui.getSnapshot().user, null)
})

test('token store: blocked browser storage supports current-page login and revoke', (): void => {
  const storage: StoragePort = { getItem: (): never => { throw new Error('blocked') }, setItem: (): never => { throw new Error('blocked') }, removeItem: (): never => { throw new Error('blocked') } }
  const tokens = createTokenStore(storage, 'test', createLogger())
  assert.equal(tokens.get(), null); tokens.set('fixture'); assert.equal(tokens.get(), 'fixture'); tokens.clear(); assert.equal(tokens.get(), null)
})

// 测试组合根与槽位系统，确保实例、订阅和 UI 生命周期可独立验证。
import { test } from 'node:test'
// 只检查可观察边界，不启动浏览器。
import assert from 'node:assert/strict'
// 组合根不允许在导入时创建共享实例。
import { createApplication } from '../site/assets/js/application.ts'
// 注册表独立于 React 运行时。
import { createSlotRegistry } from '../site/assets/js/slots.ts'
// 统一配置和日志接口。
import { DEFAULT_CONFIG } from '../site/assets/js/config.ts'
// 内存诊断不会泄露认证内容。
import { createLogger } from '../site/assets/js/logger.ts'
// 桩端口使用实际存储契约。
import type { LogEntry, StoragePort } from '../site/assets/js/contracts.ts'

/** 内存存储按测试实例隔离，键和值不写入磁盘。 */
function memoryStorage(): StoragePort {
  const values = new Map<string, string>()
  return { getItem: (key: string): string | null => values.get(key) ?? null,
    setItem(key: string, value: string): void { values.set(key, value) }, removeItem(key: string): void { values.delete(key) } }
}

test('application: explicit composition is isolated and sends no requests until an action', (): void => {
  let requests = 0; const themes: string[] = []
  const create = (): ReturnType<typeof createApplication> => createApplication({ storage: memoryStorage(), config: DEFAULT_CONFIG,
    logger: createLogger(), fetcher: async (): Promise<Response> => { requests += 1; return Response.json({}) },
    timer: { setInterval: (): number => 1, clearInterval: (): void => undefined },
    downloads: { save: (): void => undefined }, theme: { apply(value): void { themes.push(value) }, dispose: (): void => undefined },
  })
  const first = create(); const second = create()
  assert.equal(requests, 0); first.ui.set({ apiKey: 'fixture', disabledPlugins: ['modforge-settings', 'modforge-games'] })
  assert.equal(second.ui.getSnapshot().apiKey, ''); assert.deepEqual(first.ui.getSnapshot().disabledPlugins, ['modforge-games'])
  first.ui.set({ theme: 'light' }); assert.equal(themes[themes.length - 1], 'light')
  first.dispose(); second.dispose()
})

test('state subscriptions: unsubscribe stops notifications and does not mutate previous snapshot', (): void => {
  const app = createApplication({ storage: memoryStorage(), config: DEFAULT_CONFIG, logger: createLogger(),
    fetcher: async (): Promise<Response> => Response.json({}), timer: { setInterval: (): number => 1, clearInterval: (): void => undefined },
    downloads: { save: (): void => undefined }, theme: { apply: (): void => undefined, dispose: (): void => undefined } })
  let updates = 0; const before = app.ui.getSnapshot(); const stop = app.ui.subscribe((): void => { updates += 1 })
  app.ui.set({ locale: 'en' }); stop(); app.ui.set({ locale: 'zh' })
  assert.equal(updates, 1); assert.equal(before.locale, 'zh'); assert.notEqual(before, app.ui.getSnapshot()); app.dispose()
})

test('slots: duplicate ownership fails and disposal retains subsequently registered entries', (): void => {
  const registry = createSlotRegistry(); const owner = registry.scope('one'); const other = registry.scope('two')
  const view = (): null => null
  const remove = owner.inject('details', 'first', view, 10)
  other.inject('details', 'second', view, 5)
  assert.deepEqual(registry.entries('details').map((entry): string => entry.id), ['second', 'first'])
  assert.throws(() => owner.inject('details', 'first', view), /分区重复注册/)
  remove(); assert.deepEqual(registry.entries('details').map((entry): string => entry.id), ['second'])
})

test('logger: full call frames exclude exception text and URL credentials and debug is opt-in', (): void => {
  const entries: LogEntry[] = []
  const logger = createLogger((entry): void => { entries.push(entry) }, 'fixture-trace')
  const error = new Error('private fixture message')
  error.stack = 'Error: private fixture message\nprivate multiline message\n    at send (https://user:password@example.test/assets/app.js?token=private#fragment:2:3)\n    at service (https://example.test/assets/service.js:4:5)\npoll@https://example.test/assets/poll.js:6:7'
  logger.write('debug', 'fixture.debug')
  logger.write('error', 'fixture.failed', { operation: 'send', errorType: 'FixtureError' }, error)
  assert.equal(entries.length, 1)
  assert.equal(entries[0]?.traceId, 'fixture-trace')
  assert.equal(entries[0]?.stack?.split('\n').length, 3)
  assert.match(entries[0]?.stack ?? '', /app\.js:2:3/)
  assert.match(entries[0]?.stack ?? '', /service\.js:4:5/)
  assert.doesNotMatch(JSON.stringify(entries), /private|password|user:|token=|fragment/)
  logger.write('warning', 'fixture.unknown', {}, 'not an Error')
  assert.equal(entries[1]?.stack, undefined)
})

// 内置测试和断言验证真实前端 HTTP 适配器。
import { test } from 'node:test'
// 不请求外部服务或修改真实用户数据。
import assert from 'node:assert/strict'
// 配置使用与生产相同的路由表。
import { DEFAULT_CONFIG } from '../site/assets/js/config.ts'
// HTTP 客户端接受可观察的 fetch 替身。
import { createHttpClient } from '../site/assets/js/http-client.ts'
// 会话仓储负责后端字段映射。
import { createSessionRepository } from '../site/conversation/assets/js/session.repository.ts'
// 认证仓储保持现有登录/注册路由。
import { createAuthRepository } from '../site/user_auth/assets/js/auth.repository.ts'
// 测试日志不用控制台输出业务载荷。
import { createLogger } from '../site/assets/js/logger.ts'
// 配置、事件与异常均使用正式契约。
import type { GenSettings } from '../site/conversation/assets/js/session.types.ts'
// 网络异常按业务类型断言，不匹配实现字符串。
import { FrontendError } from '../site/assets/js/errors.ts'

/** 只用于测试的非敏感配置。 */
const settings: GenSettings = { apiKey: 'fixture-key', game: 'minecraft', loader: 'forge', version: '1.21.11', model: 'fixture-model', baseUrl: 'https://fixture.invalid', sandbox: 'workspace-write', visionEnabled: false, visionApiKey: '', visionBaseUrl: '', visionModel: '', autoMode: true, searchApiKey: '' }

test('HTTP contract: reset ID is a query argument and bearer token is a header', async (): Promise<void> => {
  const calls: { url: string; options?: RequestInit }[] = []
  const fetcher: typeof fetch = async (url, options): Promise<Response> => { calls.push({ url: String(url), options }); return Response.json({ ok: true }) }
  const repo = createSessionRepository(createHttpClient(fetcher, (): string => 'fixture-token', DEFAULT_CONFIG, createLogger()), DEFAULT_CONFIG)
  await repo.reset('one two')
  assert.equal(calls[0].url, '/api/session/reset?session_id=one%20two')
  assert.equal(calls[0].options?.body, undefined); assert.equal(new Headers(calls[0].options?.headers).get('Authorization'), 'Bearer fixture-token')
})

test('HTTP contract: create/start map current settings to existing snake_case fields', async (): Promise<void> => {
  const requests: { path: string; body: Record<string, unknown> }[] = []
  const fetcher: typeof fetch = async (path, options): Promise<Response> => { requests.push({ path: String(path), body: JSON.parse(String(options?.body)) as Record<string, unknown> }); return Response.json({ session_id: 'one', mod_dir: 'unused' }) }
  const repo = createSessionRepository(createHttpClient(fetcher, (): null => null, DEFAULT_CONFIG, createLogger()), DEFAULT_CONFIG)
  await repo.create(settings); await repo.start({ sessionId: 'one', prompt: 'fixture', mode: 'mod', resume: true, settings })
  assert.equal(requests[0].path, '/api/session'); assert.equal(requests[0].body.api_key, settings.apiKey)
  assert.equal(requests[1].path, '/api/task'); assert.equal(requests[1].body.session_id, 'one'); assert.equal(requests[1].body.resume, true)
  assert.equal(requests[1].body.auto_mode, true); assert.equal(requests[1].body.vision_enabled, false)
  assert.equal(requests[1].body.base_url, settings.baseUrl)
})

test('HTTP contract: multi-question answer remains one /api/answer JSON request', async (): Promise<void> => {
  let body: unknown = null
  const fetcher: typeof fetch = async (_path, options): Promise<Response> => { body = JSON.parse(String(options?.body)); return Response.json({ ok: true }) }
  const repo = createSessionRepository(createHttpClient(fetcher, (): null => null, DEFAULT_CONFIG, createLogger()), DEFAULT_CONFIG)
  await repo.answer('one', '', [{ question: 'color?', answer: 'blue' }])
  assert.deepEqual(body, { session_id: 'one', answers: [{ question: 'color?', answer: 'blue' }] })
})

test('HTTP: backend detail, non-JSON error, invalid JSON, network and timeout stay distinct', async (): Promise<void> => {
  const client = (fetcher: typeof fetch) => createHttpClient(fetcher, (): null => null, { ...DEFAULT_CONFIG, requestTimeoutMs: 5 }, createLogger())
  await assert.rejects(client(async (): Promise<Response> => Response.json({ detail: 'denied' }, { status: 403 })).request('/api/me'), (error: unknown): boolean => error instanceof FrontendError && error.status === 403 && error.message === 'denied')
  await assert.rejects(client(async (): Promise<Response> => new Response('unavailable', { status: 503 })).request('/api/me'), (error: unknown): boolean => error instanceof FrontendError && error.status === 503)
  await assert.rejects(client(async (): Promise<Response> => new Response('{', { headers: { 'content-type': 'application/json' } })).request('/api/me'), (error: unknown): boolean => error instanceof FrontendError && error.code === 'InvalidResponse')
  await assert.rejects(client(async (): Promise<never> => { throw new Error('offline') }).request('/api/me'), (error: unknown): boolean => error instanceof FrontendError && error.code === 'NetworkError')
  const pending: typeof fetch = (_url, options) => new Promise((_resolve, reject): void => { options?.signal?.addEventListener('abort', (): void => reject(new Error('aborted')), { once: true }) })
  await assert.rejects(client(pending).request('/api/me'), (error: unknown): boolean => error instanceof FrontendError && error.code === 'RequestTimeout')
})

test('HTTP: logout accepts empty response and downloads preserve binary payload', async (): Promise<void> => {
  const empty = createAuthRepository(createHttpClient(async (): Promise<Response> => new Response(null, { status: 204 }), (): null => null, DEFAULT_CONFIG, createLogger()), DEFAULT_CONFIG)
  await empty.logout()
  const repo = createSessionRepository(createHttpClient(async (): Promise<Response> => new Response(new Uint8Array([80, 75, 3, 4])), (): null => null, DEFAULT_CONFIG, createLogger()), DEFAULT_CONFIG)
  assert.deepEqual([...new Uint8Array(await (await repo.download('one', 'jar')).arrayBuffer())], [80, 75, 3, 4])
})

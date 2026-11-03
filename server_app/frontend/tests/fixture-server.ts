// 仅供前端浏览器回归的内存 HTTP 替身；不导入或修改 Python 后端。
import { createServer, type IncomingMessage, type ServerResponse } from 'node:http'
// /debug 测试只读取已有前端静态资源，不执行服务端代码。
import { readFile } from 'node:fs/promises'
// 静态目录通过真实路径边界校验。
import { resolve, extname, sep } from 'node:path'
// 模块位置独立于启动 shell 的 cwd。
import { fileURLToPath } from 'node:url'
// 测试服务日志也通过统一日志器发出。
import { createLogger } from '../site/assets/js/logger.ts'

interface FixtureSession { id: string; mode: 'chat' | 'mod'; prompt: string; started: boolean; paused: boolean; question: boolean; events: number }
/** 测试只在回环地址提供非持久化内存数据。 */
const host = '127.0.0.1'
/** 可通过命令行提供隔离端口，默认 8765。 */
const port = Number(process.argv[2] ?? '8765')
/** 夹具状态不接触 data/、真实 Key 或真实模型。 */
const sessions = new Map<string, FixtureSession>([['history_fixture', { id: 'history_fixture', mode: 'chat', prompt: '历史会话示例', started: false, paused: false, question: false, events: 0 }]])
/** 每个新会话使用可区分 ID，验证切换与历史隔离。 */
let sequence = 0
/** 日志输出仅包含元数据。 */
const logger = createLogger((entry): void => { process.stdout.write(`${JSON.stringify(entry)}\n`) })
/** 只能读取此目录中的调试页面，不能通过 URL 读取仓库其他文件。 */
const debugRoot = resolve(fileURLToPath(new URL('../../debug/', import.meta.url)))

/** 返回 JSON 并设置 MIME；夹具错误返回可供前端展示的 detail。 */
function json(response: ServerResponse, value: unknown, status = 200): void {
  response.writeHead(status, { 'Content-Type': 'application/json' }); response.end(JSON.stringify(value))
}

/** 收集测试 JSON；无正文使用空对象，损坏输入由外层统一转换为 400。 */
async function body(request: IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = []
  for await (const chunk of request) chunks.push(Buffer.from(chunk))
  const text = Buffer.concat(chunks).toString('utf8')
  const parsed: unknown = text ? JSON.parse(text) : {}
  return parsed && typeof parsed === 'object' ? parsed as Record<string, unknown> : {}
}

/** 处理已知夹具路由；未知端点失败，不向真实后端回退。 */
async function handle(request: IncomingMessage, response: ServerResponse): Promise<void> {
  const url = new URL(request.url ?? '/', `http://${host}:${port}`)
  const path = url.pathname
  if (path.startsWith('/debug/')) {
    const file = resolve(debugRoot, decodeURIComponent(path.slice('/debug/'.length)))
    if (!file.startsWith(debugRoot + sep)) { json(response, { detail: 'invalid path' }, 400); return }
    try {
      const data = await readFile(file)
      const mime: Record<string, string> = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.wav': 'audio/wav' }
      response.writeHead(200, { 'Content-Type': mime[extname(file)] ?? 'application/octet-stream' }); response.end(data)
    } catch { json(response, { detail: 'fixture asset missing' }, 404) }
    return
  }
  const data = request.method === 'POST' ? await body(request) : {}
  if (path === '/api/login' || path === '/api/register') { json(response, { username: 'frontend_fixture', token: 'frontend-fixture-only-token' }); return }
  if (path === '/api/me') { json(response, { username: 'frontend_fixture' }); return }
  if (path === '/api/logout') { json(response, { ok: true }); return }
  if (path === '/api/session' && request.method === 'POST') {
    const id = `fixture_${++sequence}`
    sessions.set(id, { id, mode: 'chat', prompt: '', started: false, paused: false, question: false, events: 0 })
    json(response, { session_id: id, mod_dir: 'fixture-memory-only' }); return
  }
  if (path === '/api/sessions') {
    json(response, { sessions: [...sessions.values()].map((session) => ({ sessionId: session.id, owner: 'frontend_fixture', has_jar: session.mode === 'mod', date: 'fixture', title: session.prompt || '空白会话' })) }); return
  }
  const id = String(data.session_id ?? url.searchParams.get('session_id') ?? '')
  const session = sessions.get(id)
  if (!session) { json(response, { detail: 'fixture session not found' }, 404); return }
  if (path === '/api/session' && request.method === 'DELETE') { sessions.delete(id); json(response, { ok: true }); return }
  if (path === '/api/session/mod') { session.mode = 'mod'; json(response, { session_id: id, mod_ready: true, already: false }); return }
  if (path === '/api/session/reset') { session.started = false; session.prompt = ''; session.events = 0; session.question = false; json(response, { session_id: id, status: 'reset' }); return }
  if (path === '/api/task') {
    session.mode = data.mode === 'mod' ? 'mod' : 'chat'; session.prompt = String(data.prompt || session.prompt)
    session.started = true; session.paused = false; session.question = session.prompt.includes('question'); session.events = 0
    json(response, { session_id: id, status: 'started', mode: session.mode }); return
  }
  if (path === '/api/task/pause') { session.paused = true; json(response, { session_id: id, status: 'paused' }); return }
  if (path === '/api/conversation') { json(response, { session_id: id, mode: session.mode, messages: session.prompt ? [{ role: 'user', content: session.prompt }, { role: 'assistant', content: '这是隔离的前端回归夹具会话。' }] : [] }); return }
  if (path === '/api/status') {
    const running = session.started && !session.paused && (session.prompt.includes('hold') || session.question)
    json(response, { session_id: id, state: running ? 'running' : 'finished', running, finished: !running, paused: session.paused,
      started_at: null, finished_at: null, elapsed: 3, file_count: 1, total_bytes: 10, has_jar: session.mode === 'mod', pending: 0,
      log_tail: '[run_task] 最终回复:\n前端架构重构回归通过。' }); return
  }
  if (path === '/api/events') {
    const events = session.started && session.events++ === 0 ? [{ id: `reply-${id}`, ts: 0, type: 'reply', source: 'run', content: '**前端回归成功**：请求已通过原有接口契约。' }] : []
    json(response, { session_id: id, events, cursor: { run: session.events, agent: 0 } }); return
  }
  if (path === '/api/question') { json(response, session.question ? { status: 'pending', questions: [{ question: '选择颜色', options: ['蓝色', '绿色'] }, { question: '选择数量', options: ['1', '2'] }] } : { status: 'none' }); return }
  if (path === '/api/answer') { session.question = false; json(response, { ok: true }); return }
  if (path === '/api/download' || path === '/api/download/jar') { response.writeHead(200, { 'Content-Type': 'application/octet-stream' }); response.end(new Uint8Array([80, 75, 3, 4])); return }
  json(response, { detail: 'fixture route not found' }, 404)
}

/** 捕获夹具输入/资产错误，不留下未处理的 Promise。 */
const server = createServer((request, response): void => { void handle(request, response).catch((): void => json(response, { detail: 'invalid fixture input' }, 400)) })
server.listen(port, host, (): void => logger.write('info', 'fixture.ready', { status: port }))

// 注入的 HTTP/日志接口允许仓储在浏览器和离线测试中使用相同行为。
import type { HttpClient, Logger } from './contracts.ts'
// 地址和超时统一由组合根配置。
import type { FrontendConfig } from './config.ts'
// 标准异常只包含用户可见消息和错误分类。
import { FrontendError } from './errors.ts'

/** 创建既有后端的 HTTP 适配器。
 * Args: fetcher 为浏览器 fetch；getToken 在每次请求时读取当前令牌；config/logger 显式注入。
 * Returns: JSON/Blob 接口。非 2xx 抛 HttpError，网络与超时分别分类；不记录请求正文。
 * Globals Used: None。Dependencies: Headers、AbortController、注入的 fetch/token/logger。
 */
export function createHttpClient(
  fetcher: typeof fetch, getToken: () => string | null, config: FrontendConfig, logger: Logger,
): HttpClient {
  /** 发送请求并在 finally 清理定时器；错误响应不是 JSON 时使用状态码回退。 */
  async function send(path: string, options: RequestInit = {}): Promise<Response> {
    const controller = new AbortController()
    const startedAt = Date.now()
    const timer = setTimeout((): void => controller.abort(), config.requestTimeoutMs)
    const headers = new Headers(options.headers)
    const token = getToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
    if (typeof options.body === 'string') headers.set('Content-Type', 'application/json')
    try {
      const response = await fetcher(`${config.apiBase}${path}`, { ...options, headers, signal: controller.signal })
      if (!response.ok) {
        let detail = `请求失败（${response.status}）`
        try {
          const payload: unknown = await response.json()
          if (payload && typeof payload === 'object' && 'detail' in payload && typeof payload.detail === 'string') detail = payload.detail
        } catch { /* 非 JSON 响应使用状态码；该失败会在下方统一记录。 */ }
        throw new FrontendError('HttpError', detail, response.status)
      }
      return response
    } catch (error: unknown) {
      const failure = error instanceof FrontendError ? error
        : new FrontendError(controller.signal.aborted ? 'RequestTimeout' : 'NetworkError',
          controller.signal.aborted ? '请求超时，请重试' : '后端暂时无法连接，请稍后重试')
      logger.write('warning', 'http.request_failed', { errorType: failure.code, status: failure.status, durationMs: Date.now() - startedAt })
      throw failure
    } finally { clearTimeout(timer) }
  }
  return {
    async request<T>(path: string, options?: RequestInit): Promise<T> {
      const response = await send(path, options)
      if (response.status === 204 || !response.headers.get('content-type')?.includes('application/json')) return undefined as T
      try { return await response.json() as T }
      catch { throw new FrontendError('InvalidResponse', '服务器返回的数据格式无效') }
    },
    async download(path: string): Promise<Blob> { return (await send(path)).blob() },
  }
}

/** HTTP 和业务边界异常；只保存分类和可展示消息，不保存请求载荷。 */
export class FrontendError extends Error {
  /** 分类用于日志和状态分支，status 仅 HTTP 失败时提供。 */
  readonly code: string
  readonly status: number | undefined

  /** 构造可由界面展示的异常；不会记录或发送任何日志。 */
  constructor(code: string, message: string, status?: number) {
    super(message)
    this.name = 'FrontendError'
    this.code = code
    this.status = status
  }
}

/** 将未知异常转为界面文本；空异常使用调用方的回退文案，无全局依赖。 */
export function errorMessage(error: unknown, fallback: string = '操作失败，请重试'): string {
  return error instanceof Error && error.message ? error.message : fallback
}

/** 日志只保留错误类别，禁止附带可能包含 Key 或响应正文的 message。 */
export function errorType(error: unknown): string {
  return error instanceof FrontendError ? error.code : error instanceof Error ? error.name : 'UnknownError'
}

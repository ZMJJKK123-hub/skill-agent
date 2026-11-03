/** 跨分区基础契约；业务实体由各功能分区声明。 */
export type Unsubscribe = () => void
export type StateListener = () => void
export interface StateStore<T> {
  getSnapshot(): T
  set(patch: Partial<T>): void
  subscribe(listener: StateListener): Unsubscribe
}
export interface StoragePort {
  getItem(key: string): string | null
  setItem(key: string, value: string): void
  removeItem(key: string): void
}
export type LogLevel = 'debug' | 'info' | 'warning' | 'error'
export interface LogContext {
  operation?: string
  scope?: string
  status?: number
  errorType?: string
  durationMs?: number
}
export interface LogEntry {
  level: LogLevel
  event: string
  context: LogContext
  timestamp: string
  traceId: string
  /** 完整调用帧；移除异常正文以及 URL 中的认证、查询和片段。 */
  stack?: string
}
export interface Logger {
  write(level: LogLevel, event: string, context?: LogContext, error?: unknown): void
}
export interface HttpClient {
  request<T>(path: string, options?: RequestInit): Promise<T>
  download(path: string): Promise<Blob>
}
export interface TimerPort {
  setInterval(callback: () => void, milliseconds: number): number
  clearInterval(handle: number): void
}
export interface ThemePort {
  apply(theme: 'system' | 'light' | 'dark'): void
  dispose(): void
}
export interface DownloadPort { save(blob: Blob, filename: string): void }

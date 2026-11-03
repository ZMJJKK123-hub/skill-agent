// 日志契约隔离界面与输出方式，防止业务代码直接调用控制台。
import type { LogEntry, Logger } from './contracts.ts'

/** 从异常中提取调用帧，保留帧顺序而排除可能包含业务正文的消息行。
 * Args: error 为被边界捕获的未知异常。Returns: 脱敏堆栈；无标准调用帧时返回 undefined。
 * 浏览器/Node 的 at 帧与 Firefox 的 URL 帧均保留；URL 认证信息、查询参数和片段移除。
 * Globals Used: None。Dependencies: Error、URL；不访问存储或发送请求。
 */
function safeStack(error: unknown): string | undefined {
  if (!(error instanceof Error) || !error.stack) return undefined
  const frames = error.stack.split('\n').filter((line): boolean => /^\s*at\s/.test(line) || /^[^\s]*@(?:https?|file):\/\//.test(line))
  const stack = frames.map((frame): string => frame.replace(/(?:https?|file):\/\/[^\s)]+/g, (location): string => {
    try {
      const position = location.match(/:\d+:\d+$/)?.[0] ?? ''
      const url = new URL(position ? location.slice(0, -position.length) : location)
      url.username = ''; url.password = ''; url.search = ''; url.hash = ''
      return url.toString() + position
    } catch { return '[source]' }
  })).join('\n')
  return stack || undefined
}

/** 创建结构化日志器。
 * Args: sink 接收不含凭据和业务正文的记录；由组合根选择浏览器事件或测试收集器。
 * traceId 关联一次页面生命周期；debug 为 false 时过滤调试记录。
 * Returns: write(level,event,context,error?) 接口；异常仅提供脱敏调用帧，默认无输出。
 * Globals Used: None。Dependencies: sink、Date、safeStack。
 */
export function createLogger(sink: (entry: LogEntry) => void = () => undefined, traceId: string = 'frontend', debug: boolean = false): Logger {
  return {
    write(level, event, context = {}, error?: unknown): void {
      if (level === 'debug' && !debug) return
      sink({ level, event, context: { operation: context.operation, scope: context.scope, status: context.status,
        errorType: context.errorType, durationMs: context.durationMs }, timestamp: new Date().toISOString(), traceId,
        ...(error === undefined ? {} : { stack: safeStack(error) }) })
    },
  }
}

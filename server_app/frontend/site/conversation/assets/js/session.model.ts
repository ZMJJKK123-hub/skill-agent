// 纯计算只依赖会话契约，便于覆盖暂停、恢复和日志回退分支。
import type { EventItem, QuestionResponse, SessionPhase, SessionState, StatusResponse } from './session.types.ts'

/** 创建新会话快照；历史可由调用方保留。无全局状态或 I/O。 */
export function emptySession(history: SessionState['history'] = []): SessionState {
  return { sessionId: null, phase: 'idle', error: null, title: null, question: null, questions: null,
    prompts: [], events: [], cursor: null, logTail: '', elapsed: null, hasJar: false, history, mode: null,
    chatMessages: [], paused: false, pending: 0, stoppedNotice: false }
}

/** 后端暂停标记优先于进程退出；未运行也未完成的会话恢复为空闲。 */
export function phaseFromStatus(status: StatusResponse): SessionPhase {
  return status.paused ? 'paused' : status.finished ? 'finished' : status.running ? 'running' : 'idle'
}

/** 按事件 ID 去重增量结果，保留原顺序；相同游标重试不会重复展示。 */
export function appendEvents(current: EventItem[], incoming: EventItem[]): EventItem[] {
  const seen = new Set(current.map((event: EventItem): string => event.id))
  return [...current, ...incoming.filter((event: EventItem): boolean => {
    if (seen.has(event.id)) return false
    seen.add(event.id)
    return true
  })]
}

/** 将新旧提问协议归一化；没有 pending 提问时返回 null。 */
export function pendingQuestions(response: QuestionResponse): SessionState['questions'] {
  if (response.status !== 'pending') return null
  const items = response.questions?.length ? response.questions : response.question ? [{ question: response.question, options: response.options }] : []
  return items.length ? items.map((item): { question: string; options: string[] } => ({ question: item.question, options: item.options ?? [] })) : null
}

/** 从旧后端日志提取最终文本；没有可用文本返回 null，绝不请求网络。
 * 有最终回复标记取其后内容；否则跳过工具/思考日志取末行。Globals Used: None。
 */
export function extractFinalReply(logTail: string): string | null {
  const marker = '最终回复:'
  const index = logTail.lastIndexOf(marker)
  if (index >= 0 && logTail.slice(index + marker.length).trim()) return logTail.slice(index + marker.length).trim()
  const noise = ['[run_task]', '[思考]', '[todo]', '[reply]', '[tool]', '[tool-result]', '[teammate', '[subagent', '[supervisor']
  return logTail.split(/\r?\n/).map((line: string): string => line.trim()).reverse()
    .find((line: string): boolean => Boolean(line) && !noise.some((prefix: string): boolean => line.startsWith(prefix))) ?? null
}

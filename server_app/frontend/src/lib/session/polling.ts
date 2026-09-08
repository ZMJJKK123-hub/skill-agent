/**
 * 会话轮询（由 lib/session.ts 原样迁出）。
 *
 * 单次 poll = 事件流增量 + 状态汇总 + 完成收尾（历史/对话加载/自动续跑）
 * + 待答问题同步。重入保护防慢网络下旧 cursor 重复追加。
 */
import * as api from '../api'
import { getUi, resolveModelConfig } from '../store'
import { state, setState } from './store'
import { loadConversation, loadHistory } from './actions'

let pollInFlight = false
// 事件批次序号：每次轮询追加的事件递增（渲染层错峰渐入用）
let eventBatchSeq = 0
let pollTimer: number | null = null

export async function poll() {
  const sid = state.sessionId
  if (!sid) return
  // 重入保护：慢网络下单次可能超过轮询间隔，两次 poll 用同一旧 cursor
  // 会事件重复追加、自动续跑重复触发
  if (pollInFlight) return
  pollInFlight = true
  try {
    await _pollOnce(sid)
  } finally {
    pollInFlight = false
  }
}

async function _pollOnce(sid: string) {
  try {
    const ev = await api.getEvents(sid, state.cursor ?? undefined)
    if (state.sessionId !== sid) return
    if (ev.events.length > 0) {
      // 批次标：同一次轮询到达的事件共用批次号，渲染层按批内序号错峰渐入
      eventBatchSeq += 1
      const tagged = ev.events.map((e) => ({ ...e, batch: eventBatchSeq }))
      setState({ events: [...state.events, ...tagged], cursor: ev.cursor })
    }
    // apiKey 用当前选中 provider 的 key：服务重启恢复的旧会话内存 key 为
    // 空，轮询带上 key 让后端回填（否则刷新后继续旧会话会 400，实测缺陷）
    const st = await api.getStatus(sid, resolveModelConfig(getUi()).apiKey)
    if (state.sessionId !== sid) return
    setState({
      elapsed: st.elapsed,
      hasJar: st.has_jar,
      logTail: st.log_tail,
      paused: st.paused,
      pending: st.pending ?? 0,
      phase: st.finished ? 'finished' : st.paused ? 'paused' : 'running',
      crashed: !!st.crashed,
    })
    // 任务完成：刷新侧栏（标题在运行期间才落盘，创建瞬间的首次拉取拿不到）
    if (st.finished) {
      void loadHistory()
    }
    // chat 模式：排队全部消化完的完成态重载磁盘对话历史（权威穿插顺序——
    // 磁盘按"处理顺序"严格 u/a 交替；pending>0 不覆盖，等全部跑完再加载）
    if (st.finished && state.mode === 'chat' && (st.pending ?? 0) === 0) {
      void loadConversation(sid)
    }
    // mod 模式：完成时拉对话历史取最终总结渲染成气泡
    if (st.finished && state.mode === 'mod') {
      const last = state.chatMessages[state.chatMessages.length - 1]
      if (!last || last.role !== 'assistant') {
        void loadConversation(sid)
      }
      void loadHistory()
    }
    // 当前轮正常跑完 + 有排队消息 → 自动续跑
    if (st.finished && !st.paused && (st.pending ?? 0) > 0) {
      try {
        await api.startTask(sid, '', state.mode ?? 'chat', true)
        if (state.sessionId !== sid) return
        const prompts = [...state.prompts, `（自动续跑：处理 ${st.pending} 条排队消息）`]
        // elapsed 归零：续跑是新一轮
        setState({ prompts, phase: 'running', pending: 0, elapsed: null })
        void loadHistory()
      } catch (e) {
        if (state.sessionId !== sid) return
        const msg = String((e as Error)?.message || e)
        // daemon 0.5s 就会消费排队消息：撞上它刚转 working 的 409 属正常竞态
        if (/409|already running|运行中/i.test(msg)) return
        setState({ phase: 'finished', error: msg })
      }
    }
    const q = await api.getQuestion(sid)
    if (state.sessionId !== sid) return
    if (q.status === 'pending' && q.questions && q.questions.length > 0) {
      const qs = q.questions.map((it) => ({ question: it.question, options: it.options ?? [] }))
      setState({ questions: qs, question: null })
    } else if (q.status === 'pending' && q.question) {
      setState({ question: { question: q.question, options: q.options ?? [] }, questions: null })
    } else if (state.question || state.questions) {
      setState({ question: null, questions: null })
    }
  } catch {
    /* 轮询瞬时失败忽略，下一轮重试 */
  }
}

export function startPolling(intervalMs = 2000) {
  if (pollTimer !== null) return
  pollTimer = window.setInterval(() => void poll(), intervalMs)
}

export function stopPolling() {
  if (pollTimer !== null) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

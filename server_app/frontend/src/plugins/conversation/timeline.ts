/**
 * 时间线聚合纯逻辑（无 React 依赖，便于单测与复用）。
 *
 * 输入事件流 → 交织时间线（思考段/工具行/回复组按真实发生顺序），
 * 再与磁盘历史气泡按轮对齐（前缀匹配，单调游标）。
 * 逻辑由 conversation.tsx 原样迁出，行为不变。
 */
import type { EventItem } from '../../lib/api'

/** 思考段：相邻 thinking/thinking_delta 事件聚合的产物 */
export interface ThinkingSeg {
  id: string
  content: string
  streaming: boolean // 段仍在增长（事件流末尾、尚未出现后续动作）
}

/** 合成后的工具条目：调用 + 就近配对的结果 */
export interface ToolEntry {
  id: string
  tool: string
  params: string
  result?: string
  status: 'success' | 'failed' | 'running'
  batch: number
  peer?: string // teammate | subagent：队友/子代理执行，行上标来源
}

/** 时间线条目（tagged union） */
export type TimelineItem =
  | { kind: 'think'; key: string; seg: ThinkingSeg; hidden?: boolean }
  | { kind: 'tool'; key: string; entry: ToolEntry; batchIdx: number; hidden?: boolean }
  | { kind: 'reply'; key: string; events: EventItem[]; hidden?: boolean }

/** 按轮交织后的渲染视图条目 */
export type RoundView =
  | { kind: 'bubble'; key: string; msg: { role: string; content: string; images?: string[] } }
  | { kind: 'item'; key: string; item: TimelineItem }

/**
 * 事件源过滤：剔除 supervisor 噪音与 agent.log 重复 tool_call；
 * 按"实质事件"（非思考增量）计 20000 条保尾部（delta 占满名额会把
 * 工具/回复挤出时间线）。
 */
export function filterShownEvents(events: EventItem[]): EventItem[] {
  const kept = events.filter(
    (e) => e.peer !== 'supervisor' && !(e.source === 'agent' && e.type === 'tool_call'),
  )
  let count = 0
  let start = 0
  for (let i = kept.length - 1; i >= 0; i--) {
    if (kept[i].type !== 'thinking_delta') {
      count++
      if (count > 20000) {
        start = i + 1
        break
      }
    }
  }
  return kept.slice(start)
}

/**
 * 一次遍历产出交织时间线：相邻 thinking/delta 聚一段、tool_call 与其
 * 后紧邻 result 顺序配对（后端成对打印）、连续 reply 合并一组；
 * 队友/子代理日志是"参数=… output=…"合一行，拆开后视为已完成。
 * 末段 streaming 判定 + 同批工具错峰序号 + 回复组去重打标。
 */
export function buildTimeline(
  shownEvents: EventItem[],
  assistantPrefixes: Set<string>,
  hasAssistantBubbles: boolean,
  sessPending: number,
): TimelineItem[] {
  const out: TimelineItem[] = []
  let curSeg: ThinkingSeg | null = null
  let curReply: EventItem[] | null = null
  for (const e of shownEvents) {
    if (e.type === 'thinking_delta' || e.type === 'thinking') {
      curReply = null
      if (!curSeg) {
        curSeg = { id: e.id, content: '', streaming: false }
        out.push({ kind: 'think', key: e.id, seg: curSeg })
      }
      // 旧整段事件与增量混排时加换行防粘连
      if (e.type === 'thinking' && curSeg.content) curSeg.content += '\n'
      curSeg.content += e.content
      continue
    }
    curSeg = null
    if (e.type === 'reply') {
      if (curReply) {
        curReply.push(e)
      } else {
        curReply = [e]
        out.push({ kind: 'reply', key: e.id, events: curReply, hidden: false })
      }
      continue
    }
    curReply = null
    if (e.type === 'tool_call') {
      // 队友/子代理的日志是"参数=… output=…"合在一行（区别于主 agent
      // 的 [tool]/[tool-result] 成对打印）：拆开后直接视为已完成，
      // 不拆会让它永远显示"运行中"（实测误导）且摘要混入 output
      if (e.peer === 'teammate' || e.peer === 'subagent') {
        const split = e.content.split(' output=')
        const params = split[0].replace(/^参数=\s*/, '')
        const result = split.length > 1 ? split.slice(1).join(' output=') : undefined
        out.push({
          kind: 'tool',
          key: e.id,
          entry: {
            id: e.id, tool: e.tool ?? 'tool', params,
            result, status: 'success', batch: e.batch ?? 0, peer: e.peer,
          },
          batchIdx: 0,
        })
        continue
      }
      out.push({
        kind: 'tool',
        key: e.id,
        entry: { id: e.id, tool: e.tool ?? 'tool', params: e.content, status: 'running', batch: e.batch ?? 0 },
        batchIdx: 0,
      })
    } else if (e.type === 'tool_result') {
      const lines = e.content.split('\n')
      const body = (lines.slice(1).join('\n').trim() || (lines[0] ?? '')).trim()
      // 就近配对：倒序找最近一个未完成的工具
      for (let i = out.length - 1; i >= 0; i--) {
        const it = out[i]
        if (it.kind === 'tool' && it.entry.status === 'running') {
          it.entry.result = body
          it.entry.status = e.status === 'failed' ? 'failed' : 'success'
          break
        }
      }
    }
    // 其余类型（round 分界/log 等）只切断回复组，不产出成员
  }
  // 末段 streaming 判定：倒序找最近的实质动作，尾部噪音日志不算
  let streaming = false
  for (let i = shownEvents.length - 1; i >= 0; i--) {
    const t = shownEvents[i].type
    if (t === 'thinking_delta') {
      streaming = true
      break
    }
    if (t === 'tool_call' || t === 'tool_result' || t === 'reply' || t === 'round') break
  }
  if (streaming) {
    for (let i = out.length - 1; i >= 0; i--) {
      const it = out[i]
      if (it.kind === 'think') {
        it.seg.streaming = true
        break
      }
    }
  }
  // 同批工具错峰序号（同一次轮询到达的行 70ms 递增渐入）
  const batchCount = new Map<number, number>()
  for (const it of out) {
    if (it.kind !== 'tool') continue
    const b = it.entry.batch
    if (b > 0) {
      const n = batchCount.get(b) ?? 0
      it.batchIdx = n
      batchCount.set(b, n + 1)
    }
  }
  // 回复组去重打标（不删除成员——reply 组是轮次分界锚点）。最后一个组
  // （= 当前流式轮）在 pending=0 时豁免隐藏（防重放；pending>0 的窗口里
  // 它仍是上一轮已落盘回复，见 conversation.tsx 原注释）。
  let lastReplyKey: string | null = null
  for (let i = out.length - 1; i >= 0; i--) {
    if (out[i].kind === 'reply') {
      lastReplyKey = out[i].key
      break
    }
  }
  const exemptLast = !(sessPending > 0)
  return out.map((it) => {
    if (it.kind !== 'reply') return it
    if (it.key === lastReplyKey && exemptLast) return { ...it, hidden: false }
    const merged = it.events.map((e) => e.content).join('\n\n')
    const hidden = hasAssistantBubbles || assistantPrefixes.has(merged.slice(0, 50))
    return { ...it, hidden }
  })
}

/**
 * 按轮交织：磁盘历史气泡与时间线 reply 组前缀匹配对齐（单调游标 k，
 * 局部指针搜索；未命中不动 k——中途回复组不能把后续 assistant 烧掉）。
 * 匹配到的轮：[用户气泡 → 该轮思考/工具 → 回复气泡]；未匹配组按原序
 * 落尾部（当前流式轮/纯实时首轮，气泡在前+时间线在后，同构不重挂载）。
 */

// 按轮交织视图（buildRoundsView）拆至 rounds.ts；再导出供 Messages 使用
export { buildRoundsView } from './rounds'

export function collectAssistantPrefixes(
  chatMessages: Array<{ role: string; content: string }>,
): Set<string> {
  const s = new Set<string>()
  chatMessages.forEach((m) => {
    if (m.role === 'assistant' && m.content) s.add(m.content.slice(0, 50))
  })
  return s
}

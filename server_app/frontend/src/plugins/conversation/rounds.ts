/**
 * 按轮交织视图构建（由 timeline.ts 拆出）：chat 气泡与 mod 过程行
 * 统一按轮归位——对齐成功按轮归位，失败时气泡在前+时间线在后。
 */
import type { EventItem } from '../../lib/api'
import type { RoundView, TimelineItem } from './timeline'

/** 聊天/历史消息（buildRoundsView 入参） */
export interface ConversationMessage {
  role: string
  content: string
  images?: string[]
}

export function buildRoundsView(
  chatMessages: Array<{ role: string; content: string; images?: string[] }>,
  timeline: TimelineItem[],
): RoundView[] {
  const view: RoundView[] = []
  const replyGroups = timeline.filter((it) => it.kind === 'reply') as Extract<
    TimelineItem, { kind: 'reply' }
  >[]
  const diskAssistants = chatMessages.filter((m) => m.role === 'assistant')

  const assign: number[] = replyGroups.map(() => -1)
  {
    let k = 0
    for (let j = 0; j < replyGroups.length; j++) {
      const p = replyGroups[j].events.map((e) => e.content).join('\n\n').slice(0, 50)
      if (!p) continue
      for (let t = k; t < diskAssistants.length; t++) {
        const a = diskAssistants[t].content
        if (a.startsWith(p) || p.startsWith(a.slice(0, 50))) {
          assign[j] = t
          k = t + 1
          break
        }
      }
    }
  }

  // timeline 按 reply 组切段：segs[j] = 第 j 组之前的过程成员
  const segs: Array<TimelineItem[]> = []
  let cur: TimelineItem[] = []
  for (const it of timeline) {
    if (it.kind === 'reply') {
      segs.push(cur)
      cur = []
    } else {
      cur.push(it)
    }
  }
  const tailMembers = cur

  let lastConsumed = -1
  let ai = 0
  let msgIdx = 0
  for (const m of chatMessages) {
    if (m.role === 'assistant') {
      const j0 = assign.indexOf(ai)
      if (j0 !== -1) {
        for (let j = lastConsumed + 1; j <= j0; j++) {
          for (const it of segs[j] ?? []) {
            view.push({ kind: 'item', key: it.key, item: it })
          }
        }
        lastConsumed = j0
      }
      ai++
    }
    view.push({ kind: 'bubble', key: `m${msgIdx}`, msg: m })
    msgIdx++
  }
  for (let j = lastConsumed + 1; j < replyGroups.length; j++) {
    for (const it of segs[j] ?? []) {
      view.push({ kind: 'item', key: it.key, item: it })
    }
    view.push({ kind: 'item', key: replyGroups[j].key, item: replyGroups[j] })
  }
  for (const it of tailMembers) {
    view.push({ kind: 'item', key: it.key, item: it })
  }
  return view
}

/** 历史 assistant 前缀集合（reply 去重用） */

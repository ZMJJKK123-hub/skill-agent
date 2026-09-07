/**
 * 事件分派渲染组件：回复气泡 / 流式打字机回复 / 普通日志行。
 * 由 conversation.tsx 原样迁出，行为不变。
 */
import type { EventItem } from '../../../lib/api'
import { ChatBubble } from './ChatBubble'
import { useTypewriter } from './Thinking'

/** 每轮回复大框：与最终回复同款气泡样式，多轮循环中每轮一个 */
export function ReplyRow({ ev }: { ev: EventItem }) {
  return <ChatBubble role="assistant" content={ev.content} />
}

/** 流式回复：当前活跃的回复组用打字机逐字吐出（与思考一致的节奏） */
export function TypingReply({ content }: { content: string }) {
  const shown = useTypewriter(content, true)
  return <ChatBubble role="assistant" content={shown} />
}

/** 普通日志（todo/background/protocol/worktree/log/system）：左侧小字 */
export function LogRow({ ev }: { ev: EventItem }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] whitespace-pre-wrap break-all font-mono text-[10px] leading-relaxed text-faint">
        {ev.content}
      </div>
    </div>
  )
}

/** DSH 风格事件渲染器：按类型分派（thinking/tool/round 由聚合处理不渲染） */
export function EventView({ ev }: { ev: EventItem }) {
  switch (ev.type) {
    case 'reply':
      return <ReplyRow ev={ev} />
    default:
      return <LogRow ev={ev} />
  }
}

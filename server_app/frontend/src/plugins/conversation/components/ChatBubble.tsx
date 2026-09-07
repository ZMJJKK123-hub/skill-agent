/**
 * 聊天气泡组件族：图片缩略 / 复制按钮 / 双角色气泡。
 * 由 conversation.tsx 原样迁出，行为不变。
 */
import { useState } from 'react'
import { useT } from '../../../lib/i18n'
import { Markdown } from '../../../lib/markdown'
import { sessionImageUrl } from '../../../lib/api'

/** 消息内图片缩略图：本地乐观消息是 data URL 直接显示；
 *  历史加载的是 uploads 文件名，经 /api/session/image 取回 */
export function MessageImages({ images, sessionId, alignEnd }: { images: string[]; sessionId?: string | null; alignEnd?: boolean }) {
  return (
    <div className={`mb-1.5 flex flex-wrap gap-1.5 ${alignEnd ? 'justify-end' : ''}`}>
      {images.map((img, i) => (
        <img
          key={i}
          src={img.startsWith('data:') ? img : sessionId ? sessionImageUrl(sessionId, img) : ''}
          className="max-h-40 max-w-[220px] rounded-lg object-cover"
          alt={`附件图片 ${i + 1}`}
        />
      ))}
    </div>
  )
}

/** 一键复制小按钮（无 emoji，SVG 图标），点击后短暂变为"已复制" */
export function CopyButton({ getText, className = '' }: { getText: () => string; className?: string }) {
  const t = useT()
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(getText())
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    } catch {
      /* 剪贴板不可用（非安全上下文等）静默 */
    }
  }
  return (
    <button
      onClick={() => void copy()}
      className={`flex items-center gap-1 rounded px-1.5 py-0.5 text-[11px] text-faint hoverable hover:text-main ${className}`}
    >
      {copied ? (
        <>
          {/* 对勾 */}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
          已复制
        </>
      ) : (
        <>
          {/* 双矩形：复制 */}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          复制
        </>
      )}
    </button>
  )
}

/** AI 回复气泡：主题令牌配色（此前硬编码深蓝底，浅色主题下是一块黑），
 *  右下角带一键复制全文 */
export function ChatBubble({ role, content, images, sessionId }: { role: 'user' | 'assistant'; content: string; images?: string[]; sessionId?: string | null }) {
  const isUser = role === 'user'
  if (isUser) {
    return (
      <div className="fade-in-up flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-md bg-forge-500 px-4 py-2.5 text-sm text-ink-950">
          {images && images.length > 0 && <MessageImages images={images} sessionId={sessionId} alignEnd />}
          {content && <div className="whitespace-pre-wrap break-words">{content}</div>}
        </div>
      </div>
    )
  }
  return (
    <div className="fade-in-up group flex justify-start">
      <div className="relative max-w-[88%] rounded-xl border border-line bg-panel px-4 py-3 text-sm leading-relaxed">
        <Markdown content={content} />
        {/* 悬停显示的复制全文按钮（group-hover） */}
        <div className="absolute -bottom-2 right-2 hidden group-hover:block">
          <div className="rounded-md border border-line bg-panel px-1">
            <CopyButton getText={() => content} />
          </div>
        </div>
      </div>
    </div>
  )
}

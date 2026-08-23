import { useMemo } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

// GFM + 软换行：AI 回复中的单个换行也渲染为 <br>，更接近聊天流式输出观感。
marked.setOptions({
  gfm: true,
  breaks: true,
})

export function Markdown({ content, className = '' }: { content: string; className?: string }) {
  const html = useMemo(() => {
    const raw = marked.parse(content ?? '') as string
    return DOMPurify.sanitize(raw)
  }, [content])

  return (
    <div
      className={`markdown-body ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

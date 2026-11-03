// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// React hooks 用于组件状态、订阅和生命周期。
import { useMemo } from 'react'
// 显式导入当前模块使用的基础设施依赖。
import { marked } from 'marked'
// 显式导入当前模块使用的基础设施依赖。
import DOMPurify from 'dompurify'

// GFM + 软换行：AI 回复中的单个换行也渲染为 <br>，更接近聊天流式输出观感。
marked.setOptions({
  gfm: true,
  breaks: true,
})

/** 把文本解析为 Markdown 并经 DOMPurify 清洗；空文本生成空内容，禁止原始 HTML 直接注入。
 * Args: 原始 Markdown 正文与可选 CSS 类名。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: marked.parse、DOMPurify.sanitize、useMemo。
 */
export function Markdown({ content, className = '' }: { content: string; className?: string }): ReactElement {
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

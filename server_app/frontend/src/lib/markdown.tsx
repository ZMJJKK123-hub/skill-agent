import { useEffect, useMemo, useRef } from 'react'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

// GFM + 软换行：AI 回复中的单个换行也渲染为 <br>，更接近聊天流式输出观感。
marked.setOptions({
  gfm: true,
  breaks: true,
})

// 回复内的链接一律新窗口打开：同窗跳转会把整个应用带走（输入草稿、
// 滚动位置全丢，实测）。在净化钩子里统一补 target/rel。
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A') {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener noreferrer')
  }
})

export function Markdown({ content, className = '' }: { content: string; className?: string }) {
  const html = useMemo(() => {
    const raw = marked.parse(content ?? '') as string
    return DOMPurify.sanitize(raw)
  }, [content])

  // 代码块复制按钮：内容是 dangerouslySetInnerHTML，无法放 React 组件，
  // 在渲染后用 DOM 注入（幂等：先查 .md-copy 防重复）。
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const root = ref.current
    if (!root) return
    root.querySelectorAll('pre').forEach((pre) => {
      if (pre.querySelector('.md-copy')) return
      const btn = document.createElement('button')
      btn.className = 'md-copy'
      btn.type = 'button'
      btn.textContent = '复制'
      btn.addEventListener('click', () => {
        const text = pre.querySelector('code')?.innerText ?? pre.innerText
        void navigator.clipboard.writeText(text).then(() => {
          btn.textContent = '已复制'
          btn.classList.add('md-copy-done')
          window.setTimeout(() => {
            btn.textContent = '复制'
            btn.classList.remove('md-copy-done')
          }, 1500)
        }).catch(() => { /* 剪贴板不可用静默 */ })
      })
      pre.appendChild(btn)
    })
  }, [html])

  return (
    <div
      ref={ref}
      className={`markdown-body ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}

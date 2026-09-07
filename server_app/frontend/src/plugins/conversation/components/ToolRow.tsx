/**
 * 工具调用行组件：工具名（状态色）+ 参数首行摘要 + 展开箭头。
 * 由 conversation.tsx 原样迁出，行为不变。
 */
import { useState } from 'react'
import type { ToolEntry } from '../timeline'

/** 工具调用行：结果收进展开（用户反馈：参数摘要保留在行上，只收
 *  result）。同批错峰渐入。 */
export function ToolRow({ entry, delayMs }: { entry: ToolEntry; delayMs: number }) {
  const [open, setOpen] = useState(false)
  const color =
    entry.status === 'success' ? 'text-emerald-500'
    : entry.status === 'failed' ? 'text-red-500'
    : 'text-muted animate-pulse'
  const oneLine = entry.params.replace(/\s+/g, ' ').trim().slice(0, 100)
  const peerLabel = entry.peer === 'teammate' ? '队友 · '
    : entry.peer === 'subagent' ? '子代理 · ' : ''
  return (
    <div className="fade-in-up" style={{ animationDelay: `${delayMs}ms` }}>
      <button
        onClick={() => setOpen((v) => !v)}
        className={`flex w-full items-center gap-1.5 py-0.5 text-left text-[13px] transition ${color} hover:opacity-80`}
      >
        {/* 展开箭头（SVG 三角，非 emoji） */}
        <svg width="10" height="10" viewBox="0 0 12 12" fill="currentColor" className={`shrink-0 transition-transform ${open ? 'rotate-90' : ''}`}>
          <path d="M3 1.5L9.5 6L3 10.5V1.5z" />
        </svg>
        {peerLabel && <span className="shrink-0 text-[11px] opacity-70">{peerLabel}</span>}
        <span className="shrink-0 font-mono">{entry.tool}</span>
        <span className="min-w-0 flex-1 truncate font-mono text-[12px] opacity-60">{oneLine}</span>
        {entry.status === 'running' && <span className="shrink-0 text-[11px] text-faint">运行中</span>}
      </button>
      {open && (
        <div className="ml-4 mt-0.5 max-h-52 space-y-1.5 overflow-auto">
          {entry.params && (
            <div>
              <div className="text-[10px] text-faint">参数</div>
              <pre className="whitespace-pre-wrap break-all font-mono text-[11px] leading-relaxed text-muted">{entry.params}</pre>
            </div>
          )}
          {entry.result != null && (
            <div>
              <div className="text-[10px] text-faint">结果</div>
              <pre className="whitespace-pre-wrap break-all font-mono text-[11px] leading-relaxed text-muted">{entry.result}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * 思考段组件：打字机 hook + 时间线思考行。
 * 由 conversation.tsx 原样迁出，行为不变。
 */
import { useEffect, useRef, useState } from 'react'
import type { ThinkingSeg } from '../timeline'

/** 打字机：active 时把 target 逐字吐出，非 active 直接显示全文。
 *  节奏自适应：真实流式（积压小）逐字吐保持手感；一轮 poll 到达的
 *  历史回复组积压大（一次挂载几百字），固定 6 字/28ms 要追十几秒——
 *  回复还在"补播"、下面的工具行早已推进（实测 4 个打字机并行、
 *  8 秒并存窗口）。改为：大积压直接对齐到尾部 40 字内渐显，任何
 *  时刻显示滞后 < ~1.2s，打字机观感保留。
 *  挂载一律从 0 字起步：streaming 判定可能闪断（首批事件尾部混有
 *  日志行），若按初始 active 初始化进度到"全文"，此后永远直接显示
 *  全量、不再吐字（实测：2315 字瞬间全出，无逐字效果）。 */
export function useTypewriter(target: string, active: boolean): string {
  const [shownLen, setShownLen] = useState(0)
  const posRef = useRef(0)
  useEffect(() => {
    if (!active) {
      // 结束/非流式：未吐完的部分瞬间补齐
      if (posRef.current < target.length) {
        posRef.current = target.length
        setShownLen(target.length)
      }
      return
    }
    if (posRef.current > target.length) posRef.current = target.length
    const timer = window.setInterval(() => {
      const cur = posRef.current
      if (cur >= target.length) return
      // 小积压 1-4 字/tick（流式手感）；大积压对齐到只剩 40 字渐显
      const backlog = target.length - cur
      const step = backlog > 400 ? backlog - 40 : backlog > 60 ? 12 : backlog > 24 ? 4 : 1
      posRef.current = cur + step
      setShownLen(cur + step)
    }, 28)
    return () => window.clearInterval(timer)
  }, [target, active])
  return active ? target.slice(0, shownLen) : target
}

/** 思考段视图：streaming 段用打字机逐字吐出 */
function ThinkingSegView({ seg }: { seg: ThinkingSeg }) {
  const shown = useTypewriter(seg.content, seg.streaming)
  return (
    <div className="text-[12px] leading-relaxed text-muted">
      <div className="mt-0.5 whitespace-pre-wrap break-words">
        {shown}
        {seg.streaming && shown.length < seg.content.length + 1 && <span className="animate-pulse"> …</span>}
      </div>
    </div>
  )
}

/** 时间线里的单个思考段：思考中自动展开（打字机），完成后收成一行，
 *  随时手动展开。与工具行按真实发生顺序交织。 */
export function ThinkingSegRow({ seg }: { seg: ThinkingSeg }) {
  const [open, setOpen] = useState(false)
  useEffect(() => {
    if (seg.streaming) setOpen(true)
    else setOpen(false)
  }, [seg.streaming])
  const lines = seg.content.split('\n').filter((l) => l.trim()).length
  return (
    <div className="fade-in-up opacity-80">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 py-0.5 text-[13px] text-muted transition hover:text-main"
      >
        {seg.streaming ? (
          <span className="animate-pulse">思考中</span>
        ) : (
          <span>思考 · {lines} 行</span>
        )}
        <span className="text-[11px] text-faint">{open ? '收起' : '展开'}</span>
      </button>
      {open && (
        <div className="mt-1 border-l border-line pl-3">
          <ThinkingSegView seg={seg} />
        </div>
      )}
    </div>
  )
}

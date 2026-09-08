/**
 * 滚动跟随 hook（由 Messages.tsx 拆出）。
 *
 * 判定一律以"实时 DOM 位置"为准，不用缓存标志：scroll 事件派发晚于
 * 程序化修改与 effect，缓存标志存在竞态。内容增长量由 deps 触发贴底。
 * 返回 listRef（挂消息列表根）、showBackToBottom（浮钮）、scrollToBottom。
 */
import { useEffect, useRef, useState } from 'react'

export function useScrollFollow(sessionId: string | null, contentDeps: unknown[]) {
  const listRef = useRef<HTMLDivElement>(null)
  const [showBackToBottom, setShowBackToBottom] = useState(false)
  const wasAtBottomRef = useRef(true)
  const lastScrollTopRef = useRef(0)
  const measure = () => {
    const scroller = listRef.current?.closest('.overflow-y-auto') as HTMLElement | null
    if (!scroller) return null
    return {
      scroller,
      atBottom: scroller.scrollHeight - scroller.scrollTop - scroller.clientHeight < 60,
      overflow: scroller.scrollHeight - scroller.clientHeight,
    }
  }
  useEffect(() => {
    // 依赖 sessionId：空态时 listRef 未挂载，进入会话后必须重绑
    const r = measure()
    if (!r) return
    const onScroll = () => {
      const m = measure()
      if (!m) return
      wasAtBottomRef.current = m.atBottom
      lastScrollTopRef.current = m.scroller.scrollTop
      setShowBackToBottom(!m.atBottom && m.overflow > 100)
    }
    r.scroller.addEventListener('scroll', onScroll, { passive: true })
    return () => r.scroller.removeEventListener('scroll', onScroll)
  }, [sessionId])
  // 事件兜底：WebView/触摸滚动 scroll 不派发——低频轮询同步位置状态
  useEffect(() => {
    if (!sessionId) return
    const timer = window.setInterval(() => {
      const m = measure()
      if (!m) return
      wasAtBottomRef.current = m.atBottom
      lastScrollTopRef.current = m.scroller.scrollTop
      setShowBackToBottom(!m.atBottom && m.overflow > 100)
    }, 800)
    return () => window.clearInterval(timer)
  }, [sessionId])
  // 新会话：强制贴底起步
  useEffect(() => {
    const r = measure()
    if (!r) return
    r.scroller.scrollTop = r.scroller.scrollHeight
    wasAtBottomRef.current = true
    lastScrollTopRef.current = r.scroller.scrollTop
    setShowBackToBottom(false)
  }, [sessionId])
  // 内容变化：区分"用户滚动"与"内容增长把视口顶开"（见原注释的竞态说明）
  useEffect(() => {
    const r = measure()
    if (!r) return
    const { scroller } = r
    if (wasAtBottomRef.current) {
      if (Math.abs(scroller.scrollTop - lastScrollTopRef.current) < 1) {
        scroller.scrollTop = scroller.scrollHeight
        setShowBackToBottom(false)
      } else {
        wasAtBottomRef.current = r.atBottom
        setShowBackToBottom(!r.atBottom && r.overflow > 100)
      }
    } else {
      setShowBackToBottom(r.overflow > 100)
    }
    lastScrollTopRef.current = scroller.scrollTop
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, contentDeps)


  const scrollToBottom = () => {
    const r = measure()
    if (!r) return
    r.scroller.scrollTop = r.scroller.scrollHeight
    wasAtBottomRef.current = true
    lastScrollTopRef.current = r.scroller.scrollTop
    setShowBackToBottom(false)
  }
  return { listRef, showBackToBottom, scrollToBottom, measure, wasAtBottomRef, lastScrollTopRef, setShowBackToBottom }
}

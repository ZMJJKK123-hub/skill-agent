/**
 * 消息主视图：滚动跟随 + 按轮交织渲染（chat/mod 同构）。
 * 滚动竞态判定逻辑由 conversation.tsx 原样迁出；时间线聚合改为
 * 调用 timeline.ts 纯函数（行为不变）。
 */
import { useEffect, useMemo, useState } from 'react'
import { useScrollFollow } from './hooks/useScrollFollow'
import { useT } from '../../lib/i18n'
import { useSession, startPolling, stopPolling, regenerate } from '../../lib/session'
import { downloadJar, downloadSourceZip } from '../../lib/api'
import { ChatBubble } from './components/ChatBubble'
import { ThinkingSegRow } from './components/Thinking'
import { ToolRow } from './components/ToolRow'
import { TypingReply } from './components/EventView'
import { EmptyState } from './components/EmptyState'
import { buildTimeline, buildRoundsView, collectAssistantPrefixes, filterShownEvents } from './timeline'

export function errMsg(e: unknown): string {
  if (e instanceof Error) return e.message
  return String(e)
}

export function Messages() {
  const t = useT()
  const sess = useSession()
  const { phase, events, elapsed, hasJar, error, mode, chatMessages, stoppedNotice, sessionId, paused, pending: sessPending } = sess
  const [displayElapsed, setDisplayElapsed] = useState<number | null>(null)

  useEffect(() => {
    if (phase === 'running') {
      startPolling(2000)
      return () => stopPolling()
    }
  }, [phase])

  // 本地每秒跳动：后端仍 2s 拉一次，但展示秒数不再 2s 一跳
  useEffect(() => {
    if (phase === 'running' || phase === 'creating') {
      setDisplayElapsed(elapsed ?? 0)
      const timer = window.setInterval(() => {
        setDisplayElapsed((prev) => (prev ?? 0) + 1)
      }, 1000)
      return () => window.clearInterval(timer)
    }
    setDisplayElapsed(null)
  }, [phase, elapsed])

  // ── 自动滚动跟随（逻辑拆至 hooks/useScrollFollow）──
  const { listRef, showBackToBottom, scrollToBottom, measure, wasAtBottomRef, lastScrollTopRef, setShowBackToBottom } =
    useScrollFollow(sessionId, [chatMessages.length, events.length])

  // 标签页标题反映运行状态
  const runningForTitle = phase === 'running' || phase === 'creating'
  useEffect(() => {
    document.title = runningForTitle ? '进行中 · MOD Forge' : 'MOD Forge'
    return () => { document.title = 'MOD Forge' }
  }, [runningForTitle])

  // mod 完成瞬间把总结气泡滚进视口
  useEffect(() => {
    if (mode !== 'mod' || phase !== 'finished') return
    const members = listRef.current?.querySelectorAll('.fade-in-up')
    const last = members && members.length > 0 ? members[members.length - 1] : null
    last?.scrollIntoView({ block: 'end' })
  }, [phase, mode])

  // 时间线三段纯逻辑（过滤 → 聚合 → 按轮交织），见 timeline.ts
  const shownEvents = useMemo(() => filterShownEvents(events), [events])
  const assistantPrefixes = useMemo(() => collectAssistantPrefixes(chatMessages), [chatMessages])
  const hasAssistantBubbles = useMemo(
    () => chatMessages.some((m) => m.role === 'assistant'),
    [chatMessages],
  )
  const timeline = useMemo(
    () => buildTimeline(shownEvents, assistantPrefixes, hasAssistantBubbles, sessPending),
    [shownEvents, assistantPrefixes, hasAssistantBubbles, sessPending],
  )
  const roundsView = useMemo(() => buildRoundsView(chatMessages, timeline), [chatMessages, timeline])

  const running = phase === 'running' || phase === 'creating'

  if (!sessionId) {
    return <EmptyState error={sess.phase === 'error' ? error : null} />
  }

  return (
    <div ref={listRef} className="mx-auto w-full max-w-4xl space-y-3 p-4 md:p-6">
      {showBackToBottom && (
        <button
          onClick={() => {
            const members = listRef.current?.querySelectorAll('.fade-in-up')
            const last = members && members.length > 0 ? members[members.length - 1] : null
            if (last) {
              last.scrollIntoView({ block: 'end' })
            }
            // 再贴一次容器绝对底：scrollIntoView 后视口可能残留 60-80px，
            // 超过 atBottom 阈值会让轮询下一拍又把浮钮亮回来
            const scroller = listRef.current?.closest('.overflow-y-auto') as HTMLElement | null
            if (scroller) scroller.scrollTop = scroller.scrollHeight
            wasAtBottomRef.current = true
            lastScrollTopRef.current = scroller ? scroller.scrollTop : lastScrollTopRef.current
            setShowBackToBottom(false)
          }}
          className="fixed bottom-28 right-6 z-30 flex items-center gap-1.5 rounded-full border border-line bg-panel px-3 py-1.5 text-xs text-muted shadow-lg hoverable"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14M5 12l7 7 7-7" />
          </svg>
          回到底部
        </button>
      )}
      <div className="space-y-3">
        {/* 统一交织视图（chat/mod 同构）：对齐成功按轮归位；失败时气泡在前
            +时间线在后，同一棵渲染树——两态切换不重挂载 */}
        {roundsView.map((v) => {
          if (v.kind === 'bubble') {
            const m = v.msg
            return <ChatBubble key={v.key} role={m.role === 'user' ? 'user' : 'assistant'} content={m.content} images={m.images} sessionId={sessionId} />
          }
          const item = v.item
          if (item.kind === 'reply') {
            if (item.hidden) return null
            const merged = item.events.map((e) => e.content).join('\n\n')
            if (!running && assistantPrefixes.has(merged.slice(0, 50))) return null
            return running
              ? <TypingReply key={v.key} content={merged} />
              : <ChatBubble key={v.key} role="assistant" content={merged} />
          }
          if (item.kind === 'think') return <ThinkingSegRow key={v.key} seg={item.seg} />
          if (item.kind === 'tool') return <ToolRow key={v.key} entry={item.entry} delayMs={Math.min(item.batchIdx, 5) * 70} />
          return null
        })}

        {running && (
          <div className="flex items-center gap-1.5 text-xs text-faint">
            <svg className="h-3.5 w-3.5 animate-spin text-forge-400" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>
              {phase === 'creating'
                ? '正在准备工作区…'
                : `${t('conv.running')}${displayElapsed != null ? ` · ${displayElapsed}s` : ''}…`}
            </span>
          </div>
        )}

        {stoppedNotice && phase !== 'running' && (
          <div className="flex items-center gap-2 py-1 text-xs text-faint">
            <div className="h-px flex-1 bg-line" />
            <span>{t('conv.stopped')}</span>
            <div className="h-px flex-1 bg-line" />
          </div>
        )}

        {error && <div className="text-sm text-red-400">{errMsg(error)}</div>}
      </div>

      {/* 下载/重新生成按钮：条件取 mode==='mod' || hasJar（/chat 切回后
          产物仍在，按钮不能跟着模式消失） */}
      {(mode === 'mod' || hasJar) && (paused || phase === 'finished') && (
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <button
            onClick={() => sess.sessionId && downloadJar(sess.sessionId).catch((e) => alert(errMsg(e)))}
            disabled={!hasJar}
            title={hasJar ? '' : t('conv.noJar')}
            className="rounded-lg bg-forge-500 px-3 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
          >
            {t('conv.downloadJar')}
          </button>
          <button
            onClick={() => sess.sessionId && downloadSourceZip(sess.sessionId).catch((e) => alert(errMsg(e)))}
            className="hoverable rounded-lg border border-line px-3 py-1.5 text-sm"
          >
            {t('conv.downloadZip')}
          </button>
          <button onClick={() => regenerate()} className="hoverable rounded-lg border border-line px-3 py-1.5 text-sm">
            {t('conv.regenerate')}
          </button>
          {phase === 'finished' &&
            (/(任务异常终止|Traceback \(most recent call last\))/.test(sess.logTail) ? (
              <span className="flex items-center gap-1.5 rounded-full border border-red-500/40 bg-red-500/10 px-2 py-0.5 text-xs text-red-400">
                <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                ✗ {t('conv.crashed')}
              </span>
            ) : (
              <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                ✓ {t('conv.done')}
              </span>
            ))}
        </div>
      )}
    </div>
  )
}

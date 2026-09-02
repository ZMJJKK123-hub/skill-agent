import { useEffect, useMemo, useRef, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { useUi, setUi, resolveModelConfig, hasModelConfig } from '../lib/store'
import { useT } from '../lib/i18n'
import { useSession, sendPrompt, startPolling, stopPolling, regenerate, answerQuestion, pauseTask, resumeTask } from '../lib/session'
import { downloadJar, downloadSourceZip, sessionImageUrl } from '../lib/api'
import type { EventItem } from '../lib/api'
import { Markdown } from '../lib/markdown'

function errMsg(e: unknown): string {
  if (e instanceof Error) return e.message
  return String(e)
}

/** 消息内图片缩略图：本地乐观消息是 data URL 直接显示；
 *  历史加载的是 uploads 文件名，经 /api/session/image 取回 */
function MessageImages({ images, sessionId, alignEnd }: { images: string[]; sessionId?: string | null; alignEnd?: boolean }) {
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
function CopyButton({ getText, className = '' }: { getText: () => string; className?: string }) {
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
function ChatBubble({ role, content, images, sessionId }: { role: 'user' | 'assistant'; content: string; images?: string[]; sessionId?: string | null }) {
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

/** 思考段：相邻 thinking/thinking_delta 事件聚合的产物 */
interface ThinkingSeg {
  id: string
  content: string
  streaming: boolean // 段仍在增长（事件流末尾、尚未出现后续动作）
}

/** 打字机：active 时把 target 逐字吐出（每 tick 吐 1-6 字，积压越多
 *  追赶越快），非 active 直接显示全文。
 *  挂载一律从 0 字起步：streaming 判定可能闪断（首批事件尾部混有
 *  日志行），若按初始 active 初始化进度到"全文"，此后永远直接显示
 *  全量、不再吐字（实测：2315 字瞬间全出，无逐字效果）。 */
function useTypewriter(target: string, active: boolean): string {
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
      // 基础 1 字/次；积压多时加速追赶，保持连续不断顿
      const backlog = target.length - cur
      const step = backlog > 60 ? 6 : backlog > 24 ? 3 : 1
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
 *  随时手动展开。与工具行按真实发生顺序交织（此前全部思考聚合在
 *  顶部一大块、永远停在消息流开头，用户看不到"思考→工具→思考"交替）。 */
function ThinkingSegRow({ seg }: { seg: ThinkingSeg }) {
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

/** 合成后的工具条目：调用 + 就近配对的结果 */
interface ToolEntry {
  id: string
  tool: string
  params: string
  result?: string
  status: 'success' | 'failed' | 'running'
  batch: number
}

/** 工具调用行：工具名（状态色）+ 参数首行摘要 + 展开箭头；结果收进
 *  展开（用户反馈：参数摘要保留在行上，只收 result）。同批错峰渐入。 */
function ToolRow({ entry, delayMs }: { entry: ToolEntry; delayMs: number }) {
  const [open, setOpen] = useState(false)
  const color =
    entry.status === 'success' ? 'text-emerald-500'
    : entry.status === 'failed' ? 'text-red-500'
    : 'text-muted animate-pulse'
  const oneLine = entry.params.replace(/\s+/g, ' ').trim().slice(0, 100)
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

/** 每轮回复大框：与最终回复同款气泡样式，多轮循环中每轮一个 */
function ReplyRow({ ev }: { ev: EventItem }) {
  return <ChatBubble role="assistant" content={ev.content} />
}

/** 流式回复：当前活跃的回复组用打字机逐字吐出（与思考一致的节奏） */
function TypingReply({ content }: { content: string }) {
  const shown = useTypewriter(content, true)
  return <ChatBubble role="assistant" content={shown} />
}

/** 中间分界线（round / system 事件）：居中显示，不归属任何人 */
function DividerRow({ ev }: { ev: EventItem }) {
  const text = ev.type === 'round'
    ? (ev.content.replace('===', '').trim().slice(0, 30))
    : ev.content
  return (
    <div className="flex items-center gap-2 py-0.5">
      <div className="h-px flex-1 bg-line" />
      <span className="text-[10px] text-faint">{text}</span>
      <div className="h-px flex-1 bg-line" />
    </div>
  )
}

/** 普通日志（todo/background/protocol/worktree/log/system）：左侧小字 */
function LogRow({ ev }: { ev: EventItem }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] whitespace-pre-wrap break-all font-mono text-[10px] leading-relaxed text-faint">
        {ev.content}
      </div>
    </div>
  )
}

/** 用户可见的事件类型白名单：回复直接渲染；思考与工具由聚合逻辑
 *  （thinkingSegs / toolEntries）转成流式思考段和合成工具行。
 *  其余（log/round/system/protocol/worktree/background/todo 等运行日志）
 *  是给开发者看的内部流水，不进用户时间线。 */
const VISIBLE_EVENT_TYPES = new Set(['reply'])

/** DSH 风格事件渲染器：按类型分派（thinking/tool 由聚合渲染，不在此） */
function EventView({ ev }: { ev: EventItem }) {
  switch (ev.type) {
    case 'reply':
      return <ReplyRow ev={ev} />
    case 'round':
      return <DividerRow ev={ev} />
    default:
      return <LogRow ev={ev} />
  }
}

function Messages() {
  const { user } = useUi()
  const t = useT()
  const sess = useSession()
  const { phase, events, elapsed, hasJar, error, mode, chatMessages, stoppedNotice, sessionId, paused } = sess
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

  // ── 自动滚动跟随（标准聊天行为）──
  // 消息区在 AppShell 的滚动容器里（main .overflow-y-auto）。
  // 用户位于底部时新内容自动跟随；上滚回看时不打扰，并显示"回到底部"。
  // 决策一律以"实时 DOM 位置"为准，不用缓存标志：scroll 事件的派发晚于
  // 程序化 scrollTop 修改与 React effect，缓存标志存在竞态——用户刚滚到
  // 顶、scroll 事件未派发时 effect 先看到旧标志把视图拽回底部，随后
  // scroll 事件在底部触发，回看状态被吞（实测：拦截 scrollTop 赋值抓到
  // effect 在用户置顶后立刻拽底的调用栈）。
  const listRef = useRef<HTMLDivElement>(null)
  const [showBackToBottom, setShowBackToBottom] = useState(false)
  // 视窗跟随状态（见下方内容 effect 的判定说明）
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
    // 依赖 sessionId：空态时 Messages 提前 return EmptyState，listRef 未挂载
    // （依赖 [] 只在挂载时空绑一次），进入会话后必须重绑。
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
  // 新会话：强制贴底起步
  useEffect(() => {
    const r = measure()
    if (!r) return
    r.scroller.scrollTop = r.scroller.scrollHeight
    wasAtBottomRef.current = true
    lastScrollTopRef.current = r.scroller.scrollTop
    setShowBackToBottom(false)
  }, [sessionId])
  // 内容变化：区分"用户滚动"与"内容增长把视口顶开"——
  // 内容增长不触发 scroll 事件（scrollTop 不变），用户滚动必触发但事件
  // 派发可能晚于本 effect（竞态窗口）。判定：上一次记录的贴底状态 +
  // scrollTop 是否被外部改变过（与 lastScrollTopRef 对比）。
  // 此前用"实时位置"判定：内容增长瞬间视口被动离开底部 → 被误判成
  // 用户回看 → 跟随失效、浮钮误出现（实测：没碰过滚动却停在顶部）。
  useEffect(() => {
    const r = measure()
    if (!r) return
    const { scroller } = r
    if (wasAtBottomRef.current) {
      if (Math.abs(scroller.scrollTop - lastScrollTopRef.current) < 1) {
        // 位置没被用户改过 → 安全跟随新内容
        scroller.scrollTop = scroller.scrollHeight
        setShowBackToBottom(false)
      } else {
        // 用户刚滚动、scroll 事件尚未派发（竞态窗口）→ 尊重用户不拽
        wasAtBottomRef.current = r.atBottom
        setShowBackToBottom(!r.atBottom && r.overflow > 100)
      }
    } else {
      // 回看中：不拽动，仅按最新溢出量刷新浮钮
      setShowBackToBottom(r.overflow > 100)
    }
    lastScrollTopRef.current = scroller.scrollTop
  }, [chatMessages.length, events.length])

  // 标签页标题反映运行状态：多标签时一眼看到哪个在跑
  const runningForTitle = phase === 'running' || phase === 'creating'
  useEffect(() => {
    document.title = runningForTitle ? '进行中 · MOD Forge' : 'MOD Forge'
    return () => { document.title = 'MOD Forge' }
  }, [runningForTitle])

  // 事件源（含不直接渲染但参与"切断"逻辑的类型）。
  // round 事件作轮次分界：不同轮次的回复必须分成两组，否则两轮回复被拼成
  // supervisor 的动作是内部监管，对用户是噪音，不进时间线。
  // 截断按"实质事件"（非思考增量）计 500 条：一轮流式思考可产生数千条
  // thinking_delta，按总条数截断会被 delta 占满名额、把工具/回复挤出
  // 时间线（实测：2515 条 delta 占满 800 名额，11 个工具全部消失）。
  // delta 随所在段保留，聚合后体积很小。
  const shownEvents = useMemo(() => {
    const kept = events.filter((e) => e.peer !== 'supervisor')
    let count = 0
    let start = 0
    for (let i = kept.length - 1; i >= 0; i--) {
      if (kept[i].type !== 'thinking_delta') {
        count++
        if (count > 500) { start = i + 1; break }
      }
    }
    return kept.slice(start)
  }, [events])

  // chat 模式：重开会话时历史 assistant 气泡与 reply 事件是同一内容
  // （conversation.jsonl 与流式日志各存一份），按前缀匹配去重——
  // 已有气泡的 reply 不再渲染；实时轮次（尚未入历史）照常实时显示。
  const assistantPrefixes = useMemo(() => {
    const s = new Set<string>()
    if (mode === 'chat') {
      chatMessages.forEach((m) => {
        if (m.role === 'assistant' && m.content) s.add(m.content.slice(0, 50))
      })
    }
    return s
  }, [mode, chatMessages])

  // 权威气泡在场（chatMessages 里有 assistant，通常来自磁盘历史加载）时
  // 流式 reply 组整体隐藏——前缀去重对"暂停续跑重输出/中途改口"等场景
  // 会失配造成回复重复显示（实测：暂停恢复后同一条回复出现两次）。
  // 气泡不在（纯实时轮次/历史加载失败）时仍显示 reply 事件作为回复。
  const hasAssistantBubbles = useMemo(
    () => chatMessages.some((m) => m.role === 'assistant'),
    [chatMessages],
  )

  // ── 时间线：思考段 / 工具行 / 回复组 / 轮次分界 按真实发生顺序交织 ──
  // 此前思考被聚合在顶部一大块（永远停在消息流开头）、工具全部堆在其后，
  // "思考→工具→思考→回复"的交替过程被打散（用户实测反馈）。
  // 一条时间线一次遍历产出：相邻 thinking/delta 聚一段、tool_call 与其后
  // 紧邻 result 顺序配对（后端成对打印）、连续 reply 合并一组。
  const timeline = useMemo(() => {
    type Item =
      | { kind: 'think'; key: string; seg: ThinkingSeg }
      | { kind: 'tool'; key: string; entry: ToolEntry; batchIdx: number }
      | { kind: 'reply'; key: string; events: EventItem[] }
      | { kind: 'divider'; key: string; ev: EventItem }
    const out: Item[] = []
    let curSeg: ThinkingSeg | null = null
    let curReply: EventItem[] | null = null
    for (const e of shownEvents) {
      if (e.type === 'thinking_delta' || e.type === 'thinking') {
        curReply = null
        if (!curSeg) {
          curSeg = { id: e.id, content: '', streaming: false }
          out.push({ kind: 'think', key: e.id, seg: curSeg })
        }
        // 旧整段事件与增量混排时加换行防粘连
        if (e.type === 'thinking' && curSeg.content) curSeg.content += '\n'
        curSeg.content += e.content
        continue
      }
      curSeg = null
      if (e.type === 'reply') {
        if (curReply) {
          curReply.push(e)
        } else {
          curReply = [e]
          out.push({ kind: 'reply', key: e.id, events: curReply })
        }
        continue
      }
      curReply = null
      if (e.type === 'tool_call') {
        out.push({
          kind: 'tool', key: e.id,
          entry: { id: e.id, tool: e.tool ?? 'tool', params: e.content, status: 'running', batch: e.batch ?? 0 },
          batchIdx: 0,
        })
      } else if (e.type === 'tool_result') {
        const lines = e.content.split('\n')
        const body = (lines.slice(1).join('\n').trim() || (lines[0] ?? '')).trim()
        // 就近配对：倒序找最近一个未完成的工具
        for (let i = out.length - 1; i >= 0; i--) {
          const it = out[i]
          if (it.kind === 'tool' && it.entry.status === 'running') {
            it.entry.result = body
            it.entry.status = e.status === 'failed' ? 'failed' : 'success'
            break
          }
        }
      } else if (e.type === 'round') {
        out.push({ kind: 'divider', key: e.id, ev: e })
      }
      // 其余类型（log 等）只切断回复组，不产出成员
    }
    // 末段 streaming 判定：倒序找最近的实质动作，尾部噪音日志不算
    let streaming = false
    for (let i = shownEvents.length - 1; i >= 0; i--) {
      const t = shownEvents[i].type
      if (t === 'thinking_delta') { streaming = true; break }
      if (t === 'tool_call' || t === 'tool_result' || t === 'reply' || t === 'round') break
    }
    if (streaming) {
      for (let i = out.length - 1; i >= 0; i--) {
        const it = out[i]
        if (it.kind === 'think') { it.seg.streaming = true; break }
      }
    }
    // 同批工具错峰序号（同一次轮询到达的行 70ms 递增渐入）
    const batchCount = new Map<number, number>()
    for (const it of out) {
      if (it.kind !== 'tool') continue
      const b = it.entry.batch
      if (b > 0) {
        const n = batchCount.get(b) ?? 0
        it.batchIdx = n
        batchCount.set(b, n + 1)
      }
    }
    // 回复组去重：权威气泡在场时隐藏全部；否则按前缀匹配滤掉已入历史的
    return out.filter((it) => {
      if (it.kind !== 'reply') return true
      if (hasAssistantBubbles) return false
      const merged = it.events.map((e) => e.content).join('\n\n')
      return !assistantPrefixes.has(merged.slice(0, 50))
    })
  }, [shownEvents, assistantPrefixes, hasAssistantBubbles])

  // chat 模式：把“当前轮”的事件插在最后一个 assistant 回复之前，
  // 避免最终回答先于思考/工具过程出现；之前的轮次尽量保持原始顺序。
  let lastAssistantIdx = -1
  chatMessages.forEach((m, i) => {
    if (m.role === 'assistant') lastAssistantIdx = i
  })
  // 如果最后一条 assistant 后面还有消息（通常是新一轮的 user prompt），
  // 说明最后一条 assistant 不是“当前轮最终回答”，不应挪到事件流后面；
  // 此时整段历史按原顺序渲染，当前轮回复由事件流显示。
  const hasTrailingMessages = lastAssistantIdx >= 0 && lastAssistantIdx < chatMessages.length - 1
  const beforeLastAssistant =
    lastAssistantIdx < 0 || hasTrailingMessages ? chatMessages : chatMessages.slice(0, lastAssistantIdx)
  const lastAssistant =
    lastAssistantIdx < 0 || hasTrailingMessages ? [] : chatMessages.slice(lastAssistantIdx)
  const running = phase === 'running' || phase === 'creating'

  // 空态判断以"是否有会话"为准：无会话 → 引导页；
  // 有会话（含历史会话，phase=idle + chatMessages 有内容）→ 显示聊天流
  if (!sessionId) {
    return <EmptyState error={sess.phase === 'error' ? error : null} />
  }

  // ── 统一微信式聊天流：chat 模式显示气泡对话；mod 模式 DSH 风格事件流 ──
  return (
    <div ref={listRef} className="mx-auto w-full max-w-4xl space-y-3 p-4 md:p-6">
      {/* 回到底部浮钮：上滚回看历史时出现（fixed 定位于视口右下） */}
      {showBackToBottom && (
        <button
          onClick={() => {
            const scroller = listRef.current?.closest('.overflow-y-auto') as HTMLElement | null
            if (scroller) {
              scroller.scrollTop = scroller.scrollHeight
              setShowBackToBottom(false)
            }
          }}
          className="fixed bottom-28 right-6 z-30 flex items-center gap-1.5 rounded-full border border-line bg-panel px-3 py-1.5 text-xs text-muted shadow-lg hoverable"
        >
          {/* 向下箭头 */}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 5v14M5 12l7 7 7-7" />
          </svg>
          回到底部
        </button>
      )}
      <div className="space-y-3">
        {/* chat 模式：历史消息（保持原始顺序，最后一个 assistant 留到事件流之后） */}
        {mode === 'chat' && beforeLastAssistant.map((m, i) => (
          <ChatBubble key={i} role={m.role === 'user' ? 'user' : 'assistant'} content={m.content} images={m.images} sessionId={sessionId} />
        ))}

        {/* mod 模式：用户消息气泡（含上传图片）——与 chat 同源 chatMessages。
            此前用 prompts 纯文本渲染，历史图片无法回显；prompts 数组仍保留
            供排队等内部逻辑使用。 */}
        {mode === 'mod' && chatMessages.filter((m) => m.role === 'user').map((m, i) => (
          <ChatBubble key={`mu-${i}`} role="user" content={m.content} images={m.images} sessionId={sessionId} />
        ))}

        {/* 运行中提示（所有模式）：只显示状态 + 本地 1s 秒数，具体步骤看下方事件流 */}
        {running && (
          <div className="text-xs text-faint">
            {phase === 'creating'
              ? '正在准备工作区…'
              : `${t('conv.running')}${displayElapsed != null ? ` · ${displayElapsed}s` : ''}…`}
          </div>
        )}

        {/* 时间线：思考段（思考中展开+打字机，完成收一行）/ 工具行（状态色+ */}
        {/* 参数摘要+箭头展开）/ 回复气泡 / 轮次分界，按真实发生顺序交织 */}
        {timeline.map((item, idx) => {
          switch (item.kind) {
            case 'think':
              return <ThinkingSegRow key={item.key} seg={item.seg} />
            case 'tool':
              return <ToolRow key={item.key} entry={item.entry} delayMs={Math.min(item.batchIdx, 5) * 70} />
            case 'reply': {
              const content = item.events.map((e) => e.content).join('\n\n')
              // 运行中且是时间线末尾的回复组 = 当前活跃回复 → 打字机逐字输出
              const isActive = running && idx === timeline.length - 1
              return isActive
                ? <TypingReply key={item.key} content={content} />
                : <ChatBubble key={item.key} role="assistant" content={content} />
            }
            case 'divider':
              return <EventView key={item.key} ev={item.ev} />
          }
        })}

        {/* chat 模式：当前轮最终回答放在事件流之后 */}
        {mode === 'chat' && lastAssistant.map((m, i) => (
          <ChatBubble key={i} role={m.role === 'user' ? 'user' : 'assistant'} content={m.content} images={m.images} sessionId={sessionId} />
        ))}

        {/* mod 模式：完成后渲染最终总结气泡（conversation.jsonl 的最后一条 assistant）。
            此前 mod 模式只渲染事件流，完成时界面没有任何回复（718d315bec0b 实测：
            显示"完成 ✓"却没有说明文字）。 */}
        {mode === 'mod' && (phase === 'finished' || paused) && (() => {
          const lastA = [...chatMessages].reverse().find((m) => m.role === 'assistant' && m.content)
          return lastA ? <ChatBubble role="assistant" content={lastA.content} /> : null
        })()}

        {/* 已暂停：横线提示"您已终止该对话" */}
        {stoppedNotice && phase !== 'running' && (
          <div className="flex items-center gap-2 py-1 text-xs text-faint">
            <div className="h-px flex-1 bg-line" />
            <span>{t('conv.stopped')}</span>
            <div className="h-px flex-1 bg-line" />
          </div>
        )}

        {error && <div className="text-sm text-red-400">{errMsg(error)}</div>}
      </div>

      {/* mod 模式：下载/重新生成按钮 —— 运行中隐藏，暂停/完成后显示 */}
      {mode === 'mod' && (paused || phase === 'finished') && (
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
              <span className="text-xs text-red-400">✗ {t('conv.crashed')}</span>
            ) : (
              <span className="text-xs text-emerald-400">{t('conv.done')}</span>
            ))}
        </div>
      )}
    </div>
  )
}

function EmptyState({ error }: { error?: string | null }) {
  const t = useT()
  // 快捷示例：点击填入输入框（经自定义事件，Composer 监听后 setText + 聚焦）。
  // i18n 里这三个键早就存在但从未渲染——用户第一眼就有可点的示例。
  const quickPicks = [t('conv.quickSword'), t('conv.quickFood'), t('conv.quickBlock')]
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-forge-500 text-3xl font-bold text-ink-950">
        M
      </div>
      <div className="text-lg font-semibold">{t('conv.title')}</div>
      <div className="max-w-md text-sm text-muted">{t('conv.desc')}</div>
      <div className="mt-2 flex max-w-lg flex-wrap justify-center gap-2">
        {quickPicks.map((q) => (
          <button
            key={q}
            onClick={() => window.dispatchEvent(new CustomEvent('modforge:prefill', { detail: q }))}
            className="rounded-full border border-line px-3 py-1.5 text-xs text-muted hoverable hover:text-main"
          >
            {q}
          </button>
        ))}
      </div>
      {/* 发起失败（服务失联/404/断网等）在空态也要可见——此前 error 只在
          running 视图渲染，sessionId=null 时点发送毫无反馈（实测静默失败缺陷） */}
      {error && (
        <div className="max-w-md rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
          <div className="font-medium">发起失败：{error}</div>
          {/404|Not Found/i.test(error) && (
            <div className="mt-1 text-xs text-red-300/80">服务连接异常（404）：服务可能已更新或重启，请刷新页面后重试。</div>
          )}
        </div>
      )}
      {/* 作者联系方式：放空态空白处，方便用户咨询 */}
      <div className="mt-6 max-w-sm rounded-xl border border-line bg-panel/60 p-3 text-xs text-muted">
        <div className="mb-1 font-medium text-forge-300">联系作者</div>
        <div>
          使用遇到问题、想提需求或反馈 bug？加作者微信交流：
          <span
            className="cursor-pointer select-all rounded bg-field px-1.5 py-0.5 font-mono text-forge-300"
            title="点击全选复制"
            onClick={(e) => {
              const range = document.createRange()
              range.selectNodeContents(e.currentTarget)
              const sel = window.getSelection()
              sel?.removeAllRanges()
              sel?.addRange(range)
            }}
          >
            lyx525100
          </span>
        </div>
      </div>
    </div>
  )
}

function QuestionCard() {
  const sess = useSession()
  const t = useT()
  // 支持多题：questions（数组）优先；兼容单题 question
  const qs = sess.questions ?? (sess.question ? [sess.question] : null)
  // 每题的草稿答案（index → string）；null = 未作答
  const [drafts, setDrafts] = useState<Record<number, string>>({})
  const [customText, setCustomText] = useState<Record<number, string>>({})

  if (!qs || qs.length === 0) return null

  // 点选项：暂存为该题答案（不提交！可随时改）
  const pick = (idx: number, opt: string) => {
    setDrafts((d) => ({ ...d, [idx]: opt }))
    setCustomText((c) => ({ ...c, [idx]: '' }))
  }
  // 自由填写：输入即暂存（不提交）
  const type = (idx: number, v: string) => {
    setCustomText((c) => ({ ...c, [idx]: v }))
    if (v.trim()) setDrafts((d) => ({ ...d, [idx]: v.trim() }))
  }
  // 确认：一次性提交所有题目的答案
  const confirmAll = () => {
    const answers = qs.map((q, i) => ({
      question: q.question,
      answer: drafts[i] ?? customText[i]?.trim() ?? '',
    }))
    answerQuestion('', answers)
    setDrafts({})
    setCustomText({})
  }
  const answeredCount = qs.filter((_, i) => (drafts[i] ?? '').trim()).length
  const allAnswered = answeredCount === qs.length

  return (
    <div className="mb-2 rounded-xl border border-forge-500/40 bg-forge-500/10 p-3">
      <div className="mb-1 text-xs text-faint">
        {t('conv.questionTitle')}（{answeredCount}/{qs.length}）
      </div>
      <div className="space-y-3">
        {qs.map((q, i) => (
          <div key={i} className="rounded-lg border border-line bg-panel/50 p-2">
            <div className="mb-1.5 text-sm font-medium text-forge-300">
              {i + 1}. {q.question}
            </div>
            {q.options.length > 0 && (
              <div className="mb-1.5 flex flex-wrap gap-1.5">
                {q.options.map((o) => (
                  <button
                    key={o}
                    onClick={() => pick(i, o)}
                    className={`rounded-md border px-2.5 py-1 text-xs transition ${
                      drafts[i] === o
                        ? 'border-forge-500 bg-forge-500/20 text-forge-300'
                        : 'border-forge-500/30 text-forge-400 hover:bg-forge-500/10'
                    }`}
                  >
                    {o}
                  </button>
                ))}
              </div>
            )}
            <input
              value={customText[i] ?? ''}
              onChange={(e) => type(i, e.target.value)}
              placeholder={drafts[i] && drafts[i] !== customText[i] ? `已选「${drafts[i]}」，可在此修改或自填…` : '也可自行填写…'}
              className="w-full rounded-md border border-line bg-field px-2 py-1 text-xs outline-none placeholder:text-faint focus:border-forge-500"
            />
            {drafts[i] && (
              <div className="mt-1 text-[11px] text-faint">
                当前答案：{drafts[i]}
                <button
                  onClick={() => {
                    setDrafts((d) => { const n = { ...d }; delete n[i]; return n })
                    setCustomText((c) => { const n = { ...c }; delete n[i]; return n })
                  }}
                  className="ml-2 text-red-400 hoverable"
                >
                  ✕ 清除
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-2 flex items-center gap-2">
        <button
          onClick={confirmAll}
          disabled={!allAnswered}
          className="rounded-md bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
        >
          {t('conv.questionConfirm')} {allAnswered ? '' : `（还差 ${qs.length - answeredCount} 题）`}
        </button>
        {!allAnswered && <span className="text-xs text-faint">全部回答后即可确认，可随时修改</span>}
      </div>
    </div>
  )
}

/** 每条消息最多携带的图片数（与后端 /api/task 的 images 上限一致） */
const MAX_IMAGES_PER_MESSAGE = 4

/** 图片文件 → data URL：小图（≤600KB）原样返回；
 *  大图 canvas 缩放到 1280 内并转 JPEG 0.85，控制上传与 token 体积 */
async function fileToDataUrl(file: File): Promise<string> {
  const raw = await new Promise<string>((resolve, reject) => {
    const r = new FileReader()
    r.onload = () => resolve(String(r.result))
    r.onerror = () => reject(new Error('读取图片失败'))
    r.readAsDataURL(file)
  })
  if (file.size <= 600 * 1024) return raw
  try {
    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const im = new Image()
      im.onload = () => resolve(im)
      im.onerror = () => reject(new Error('解析图片失败'))
      im.src = raw
    })
    const scale = Math.min(1, 1280 / Math.max(img.width, img.height))
    if (scale >= 1) return raw
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(img.width * scale)
    canvas.height = Math.round(img.height * scale)
    const ctx = canvas.getContext('2d')
    if (!ctx) return raw
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    return canvas.toDataURL('image/jpeg', 0.85)
  } catch {
    return raw
  }
}

function Composer() {
  const { user, model, providers, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey, settingsOpen } = useUi()
  const t = useT()
  const sess = useSession()
  const [text, setText] = useState('')
  // 随消息上传的图片（data URL，发送时压缩为附件传给后端落盘）
  const [images, setImages] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  // /mod 应用内确认：不再用 window.confirm——原生对话框在"禁止此页再弹窗"
  // 或自动化环境里会被自动接受，确认形同虚设（实测缺陷）。改为状态驱动浮层。
  const [modConfirm, setModConfirm] = useState<string | null>(null)
  const [modImages, setModImages] = useState<string[]>([])
  const running = sess.phase === 'running' || sess.phase === 'creating'
  const paused = sess.phase === 'paused' || sess.paused

  // 空态快捷示例点击 → 填入输入框并聚焦
  useEffect(() => {
    const onPrefill = (e: Event) => {
      const detail = (e as CustomEvent<string>).detail || ''
      setText(detail)
      ;(document.querySelector('main textarea') as HTMLTextAreaElement | null)?.focus()
    }
    window.addEventListener('modforge:prefill', onPrefill)
    return () => window.removeEventListener('modforge:prefill', onPrefill)
  }, [])

  // 拖拽图片进输入区（第三条上传路径：点选/粘贴/拖拽）
  const [dragOver, setDragOver] = useState(false)

  const addImageFiles = async (files: File[]) => {
    const pics = files.filter((f) => f.type.startsWith('image/'))
    if (pics.length === 0) return
    const room = MAX_IMAGES_PER_MESSAGE - images.length
    if (pics.length > room) alert(t('conv.tooManyImages'))
    if (room <= 0) return
    const encoded: string[] = []
    for (const f of pics.slice(0, room)) {
      try {
        encoded.push(await fileToDataUrl(f))
      } catch {
        /* 单张解析失败跳过 */
      }
    }
    if (encoded.length > 0) setImages((prev) => [...prev, ...encoded])
  }

  const send = () => {
    const prompt = text.trim()
    if (!prompt && images.length === 0) return
    const r = resolveModelConfig({ model, providers })
    const settings = { apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game: 'minecraft', loader: 'forge', version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey }

    // /mod 拦截：固定格式触发 mod 制作模式（大小写不敏感——/MOD /Mod 同样生效；
    // 此前只认小写，大写会静默按 chat 发出烧 token，实测 bug #10）
    if (/^\/mod(\s|$)/i.test(prompt)) {
      const modPrompt = prompt.slice(4).trim()
      if (!modPrompt) {
        alert('用法：/mod <你的 MOD 需求描述>，例如：/mod 做一把钻石剑')
        return
      }
      setModConfirm(modPrompt) // 弹应用内确认条，等用户点"确认开始"
      setModImages(images)
      return
    }

    // 普通消息：mod 会话（含打开的历史 mod 会话）沿用 mod 模式——否则
    // 完成后的迭代需求会被降级成只读咨询（P1 实测缺陷：daemon 以 chat 重启
    // 后整个会话锁死只读）。新建/纯 chat 会话仍是 chat；server 端还有
    // mode.txt 记忆 + /mod 前缀强制双保险。
    void sendPrompt(prompt, settings, sess.mode === 'mod' ? 'mod' : 'chat', images)
    setText('')
    setImages([])
  }

  const confirmMod = () => {
    if (!modConfirm) return
    const r = resolveModelConfig({ model, providers })
    const settings = { apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game: 'minecraft', loader: 'forge', version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey }
    void sendPrompt(modConfirm, settings, 'mod', modImages)
    setModConfirm(null)
    setModImages([])
    setText('')
    setImages([])
  }

  // 可发送 = 已配置可用模型（v1.0.2：官方默认已移除，完全由用户提供）。
  // 未配置时不显示任何提示框——只在发送按钮悬停（title）时给出指引。
  const canChat = hasModelConfig({ model, providers })
  const notReadyReason = canChat ? '' : t('conv.noModel')

  // 运行中：红方块停止按钮；暂停后：绿箭头继续按钮；空闲：发送按钮
  const actionButton = running ? (
    <button
      onClick={() => pauseTask()}
      title={t('conv.pause')}
      className="flex h-9 w-9 items-center justify-center rounded-full border border-red-500/50 text-red-400 hover:bg-red-500/10"
    >
      {/* 停止：圆圈内红色方块 */}
      <span className="block h-3.5 w-3.5 rounded-[3px] bg-red-500" />
    </button>
  ) : paused ? (
    <button
      onClick={() => resumeTask()}
      title={t('conv.resume')}
      className="flex h-9 w-9 items-center justify-center rounded-full border border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10"
    >
      {/* 继续：绿色三角箭头 */}
      <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
        <path d="M4 2l10 6-10 6V2z" />
      </svg>
    </button>
  ) : (
    <button
      onClick={send}
      disabled={(!text.trim() && images.length === 0) || !canChat}
      title={canChat ? '' : notReadyReason}
      className="rounded-lg bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
    >
      {t('conv.send')}
    </button>
  )

  return (
    <div className="mx-auto w-full max-w-4xl">
      <QuestionCard />
      {modConfirm && (
        <div className="mb-2 rounded-xl border border-forge-500/40 bg-forge-500/10 p-3">
          <div className="mb-1 text-xs font-medium text-forge-300">即将开始 MOD 制作</div>
          <div className="mb-2 text-sm text-main">
            将复制 MOD 模板与 MC 源码，开始制作：“{modConfirm.slice(0, 80)}{modConfirm.length > 80 ? '…' : ''}”
          </div>
          <div className="flex gap-2">
            <button
              onClick={confirmMod}
              className="rounded-md bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400"
            >
              ✓ 确认开始
            </button>
            <button
              onClick={() => setModConfirm(null)}
              className="hoverable rounded-md border border-line px-4 py-1.5 text-sm"
            >
              取消
            </button>
          </div>
        </div>
      )}
      {/* 未配置时不显示提示框（用户要求）：提示只在发送按钮悬停 title 出现 */}
      <div
        className={`rounded-xl border bg-panel p-3 transition-colors ${dragOver ? 'border-forge-500' : 'border-line'}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith('image/'))
          if (files.length > 0) void addImageFiles(files)
        }}
      >
        {/* 待上传图片缩略图（选择/粘贴/拖拽后、发送前）+ 数量计数 */}
        {images.length > 0 && (
          <div className="mb-2 flex flex-wrap items-start gap-2">
            {images.map((src, i) => (
              <div key={i} className="relative">
                <img src={src} alt={`待上传 ${i + 1}`} className="h-20 w-20 rounded-lg border border-line object-cover" />
                <button
                  onClick={() => setImages((prev) => prev.filter((_, j) => j !== i))}
                  title="移除图片"
                  className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full border border-line bg-panel text-[10px] text-faint hoverable hover:text-red-400"
                >
                  ✕
                </button>
              </div>
            ))}
            <span className="self-end text-[11px] text-faint">{images.length}/{MAX_IMAGES_PER_MESSAGE}</span>
          </div>
        )}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onPaste={(e) => {
            // 粘贴图片：剪贴板里有图片文件时直接加入待上传列表
            const files = Array.from(e.clipboardData.files).filter((f) => f.type.startsWith('image/'))
            if (files.length > 0) {
              e.preventDefault()
              void addImageFiles(files)
            }
          }}
          onKeyDown={(e) => {
            // 输入法组合中的 Enter 是"选候选词"，不是发送——此前未检查
            // isComposing，中文用户每次选词都会误发（实测缺陷）
            if (e.nativeEvent.isComposing) return
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              if (running || paused) {
                // 运行中/暂停后回车：排队发送
                if (text.trim() || images.length > 0) send()
              } else if (text.trim() || images.length > 0) {
                send()
              }
            }
          }}
          rows={3}
          disabled={!canChat}
          placeholder={canChat ? t('conv.placeholder') : t('conv.configureFirst')}
          className="w-full resize-none bg-transparent text-sm outline-none placeholder:text-faint disabled:opacity-60"
        />
          <div className="mt-2 flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => {
                void addImageFiles(Array.from(e.target.files ?? []))
                e.target.value = '' // 允许重复选择同一张
              }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={!canChat}
              title={t('conv.attach')}
              className="flex h-7 w-7 items-center justify-center rounded-md border border-line text-muted hoverable disabled:opacity-50"
            >
              {/* 回形针：上传图片附件 */}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
            </button>
            <select
              value={model}
              onChange={(e) => setUi({ model: e.target.value })}
              disabled={!canChat}
              title={canChat ? '' : t('conv.noModel')}
              className="rounded-md border border-line bg-field px-2 py-1 text-xs text-muted outline-none disabled:opacity-50"
            >
              {canChat ? (
                providers.map((p) => (
                  <optgroup key={p.id} label={p.name}>
                    {p.model.split(',').map((m) => m.trim()).filter(Boolean).map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </optgroup>
                ))
              ) : (
                <option value="">{t('conv.noModelShort')}</option>
              )}
            </select>
            <div className="flex-1" />
            {running && sess.pending > 0 && (
              <span className="text-xs text-faint">{sess.pending} 条排队…</span>
            )}
            {actionButton}
          </div>
        </div>
    </div>
  )
}

export const conversationPlugin: PluginManifest = {
  id: 'modforge-conversation',
  name: '对话',
  apply(ctx) {
    ctx.slots.inject(SLOTS.conversationMessages, 'messages', () => <Messages />)
    ctx.slots.inject(SLOTS.conversationComposer, 'composer', () => <Composer />)
  },
}

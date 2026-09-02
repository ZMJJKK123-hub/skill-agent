import { useEffect, useMemo, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { useUi, setUi, resolveModelConfig, hasModelConfig } from '../lib/store'
import { useT } from '../lib/i18n'
import { useSession, sendPrompt, startPolling, stopPolling, regenerate, answerQuestion, pauseTask, resumeTask } from '../lib/session'
import { downloadJar, downloadSourceZip } from '../lib/api'
import type { EventItem } from '../lib/api'
import { Markdown } from '../lib/markdown'

function errMsg(e: unknown): string {
  if (e instanceof Error) return e.message
  return String(e)
}

/** 思考气泡的显示名：peer 映射（supervisor/teammate/subagent），无 peer 是主 agent */
function thinkingName(ev: EventItem, t: (k: string) => string): string {
  switch (ev.peer) {
    case 'supervisor': return '🛡 Supervisor'
    case 'teammate': return '👥 Teammate'
    case 'subagent': return '🔬 Subagent'
    default: return t('conv.agent')
  }
}

/** AI 回复气泡：深海蓝半透明 + 暗金边框 + 毛玻璃，无头像 */
function ChatBubble({ role, content }: { role: 'user' | 'assistant'; content: string }) {
  const isUser = role === 'user'
  if (isUser) {
    return (
      <div className="fade-in-up flex justify-end">
        <div className="max-w-[80%] rounded-2xl rounded-br-md bg-forge-500 px-4 py-2.5 text-sm text-ink-950">
          <div className="whitespace-pre-wrap break-words">{content}</div>
        </div>
      </div>
    )
  }
  return (
    <div className="fade-in-up flex justify-start">
      <div
        className="max-w-[88%] rounded-xl px-4 py-3 text-sm leading-relaxed backdrop-blur-sm"
        style={{
          background: 'rgba(20, 25, 40, 0.7)',
          border: '1px solid rgba(200, 180, 150, 0.4)',
          borderRadius: '12px',
        }}
      >
        <Markdown content={content} />
      </div>
    </div>
  )
}

/** 思考过程：极简内联，不用框，点击展开 */
function ThinkingGroup({ events, t }: { events: EventItem[]; t: (k: string) => string }) {
  const [open, setOpen] = useState(false)
  if (events.length === 0) return null
  const totalLines = events.reduce(
    (n, ev) => n + ev.content.split('\n').filter((l) => l.trim()).length, 0)
  return (
    <div className="fade-in-up opacity-70">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 py-0.5 text-[13px] text-blue-100/60 transition hover:text-blue-100/90"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
          <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
        </svg>
        <span>Agent thinking · {events.length} 段 / {totalLines} 行</span>
        <span className="text-[11px] text-faint">{open ? '收起' : '展开'}</span>
      </button>
      {open && (
        <div className="mt-1 space-y-2 pl-5">
          {events.map((ev, i) => (
            <div key={ev.id} className="text-[12px] leading-relaxed text-blue-100/50">
              <span className="text-blue-200/40">#{i + 1} {thinkingName(ev, t)}</span>
              <div className="mt-0.5 whitespace-pre-wrap break-words">{ev.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/** 工具调用：极简单行，✨ 图标，无边框无背景 */
function ToolCallRow({ ev }: { ev: EventItem }) {
  const [open, setOpen] = useState(false)
  const tool = ev.tool ?? 'tool'
  const oneLine = ev.content.replace(/\s+/g, ' ').trim().slice(0, 120)
  return (
    <div className="fade-in-up opacity-70">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-1.5 py-0.5 text-left text-[13px] text-blue-100/60 transition hover:text-blue-100/90"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0 text-white/50">
          <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
        </svg>
        <span className="shrink-0">Tool call · <span className="text-blue-200/80">{tool}</span> · </span>
        <span className="min-w-0 flex-1 truncate font-mono text-[12px] text-slate-400">{oneLine}</span>
      </button>
      {open && (
        <div className="ml-5 mt-0.5 max-h-48 overflow-auto whitespace-pre-wrap break-all font-mono text-[11px] text-slate-400/80">
          {ev.content}
        </div>
      )}
    </div>
  )
}

/** 工具结果：极简，✓/✗ + 截断内容，点击展开 */
function ToolResultRow({ ev }: { ev: EventItem }) {
  const [open, setOpen] = useState(false)
  const ok = ev.status !== 'failed'
  const lines = ev.content.split('\n')
  const body = (lines.slice(1).join('\n').trim() || (lines[0] ?? '')).trim()
  return (
    <div className="fade-in-up opacity-70">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-1.5 py-0.5 text-left text-[13px] transition"
        style={{ color: ok ? 'rgba(134, 239, 172, 0.6)' : 'rgba(248, 113, 113, 0.6)' }}
      >
        <span className="shrink-0">{ok ? '✓' : '✗'}</span>
        <span className="shrink-0">{ok ? 'Result' : 'Failed'}</span>
        <span className="min-w-0 flex-1 truncate font-mono text-[12px] opacity-60">{body.replace(/\s+/g, ' ').slice(0, 100)}</span>
        <span className="shrink-0 text-[11px] text-faint">{open ? '收起' : `${body.length}`}</span>
      </button>
      {open && (
        <pre className="ml-5 mt-0.5 max-h-48 overflow-auto whitespace-pre-wrap break-all font-mono text-[11px] leading-relaxed text-slate-400/70">
          {body}
        </pre>
      )}
    </div>
  )
}

/** 每轮回复大框：与最终回复同款气泡样式，多轮循环中每轮一个 */
function ReplyRow({ ev }: { ev: EventItem }) {
  return <ChatBubble role="assistant" content={ev.content} />
}

/** 中间分界线（round / system 事件）：居中显示，不归属任何人 */
function DividerRow({ ev }: { ev: EventItem }) {
  const text = ev.type === 'round'
    ? (ev.content.replace('===', '').trim().slice(0, 30))
    : ev.content
  return (
    <div className="flex items-center gap-2 py-0.5">
      <div className="h-px flex-1 bg-line" />
      <span className="text-[10px] text-faint">🔁 {text}</span>
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

/** 用户可见的事件类型白名单：只展示 思考 / 工具调用 / 工具结果 / 回复。
 *  其余（log/round/system/protocol/worktree/background/todo 等运行日志）
 *  是给开发者看的内部流水，不进用户时间线。 */
const VISIBLE_EVENT_TYPES = new Set(['thinking', 'tool_call', 'tool_result', 'reply'])

/** DSH 风格事件渲染器：按类型分派（thinking 由 ThinkingGroup 聚合渲染） */
function EventView({ ev, t }: { ev: EventItem; t: (k: string) => string }) {
  switch (ev.type) {
    case 'tool_call':
      return <ToolCallRow ev={ev} />
    case 'tool_result':
      return <ToolResultRow ev={ev} />
    case 'reply':
      return <ReplyRow ev={ev} />
    case 'round':
      return <DividerRow ev={ev} />
    case 'todo':
    case 'background':
    case 'protocol':
    case 'worktree':
    case 'system':
    case 'log':
    default:
      return <LogRow ev={ev} />
  }
}

function Messages() {
  const { user } = useUi()
  const t = useT()
  const sess = useSession()
  const { phase, prompts, events, elapsed, hasJar, error, mode, chatMessages, stoppedNotice, sessionId, paused } = sess
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

  // 先筛出用户可见的事件，再保留最近 500 条。
  // 之前直接 events.slice(-120) 会被大量 log/todo/round 等不可见事件占满名额，
  // 导致工具调用和思考过程在长任务中被挤出 UI（用户看到"只调了两个工具"）。
  // supervisor 的 tool_call/tool_result 是内部监管动作（读参考文档、试读日志），
  // 对用户是噪音（718d315bec0b：7 次 run.log 读取失败显示成一串红 ✗），不进时间线。
  const shownEvents = useMemo(() => {
    return events.filter((e) =>
      VISIBLE_EVENT_TYPES.has(e.type)
      && !(e.peer === 'supervisor' && (e.type === 'tool_call' || e.type === 'tool_result'))
    ).slice(-500)
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

  // 连续 reply 事件合并为一个助手气泡：
  // 流式过程中一次回复可能被后端按轮询切片拆成多个 reply 事件，
  // 只要中间没有 thinking/tool 等事件，就把它们拼成同一条完整回复。
  const visibleEvents = useMemo(() => {
    const out: (EventItem | EventItem[])[] = []
    let current: EventItem[] | null = null
    for (const ev of shownEvents) {
      if (ev.type === 'reply') {
        if (current) {
          current.push(ev)
        } else {
          current = [ev]
          out.push(current)
        }
        continue
      }
      // 任何非 reply 事件（即使不渲染，如 round）都切断当前回复组，
      // 避免把不同轮次的回复错误合并。
      current = null
      if (ev.type !== 'thinking' && VISIBLE_EVENT_TYPES.has(ev.type)) {
        out.push(ev)
      }
    }
    return out.filter((item) => {
      if (!Array.isArray(item)) return true
      const merged = item.map((e) => e.content).join('\n\n')
      return !assistantPrefixes.has(merged.slice(0, 50))
    })
  }, [shownEvents, assistantPrefixes])

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
    <div className="mx-auto w-full max-w-4xl space-y-3 p-4 md:p-6">
      <div className="space-y-3">
        {/* chat 模式：历史消息（保持原始顺序，最后一个 assistant 留到事件流之后） */}
        {mode === 'chat' && beforeLastAssistant.map((m, i) => (
          <ChatBubble key={i} role={m.role === 'user' ? 'user' : 'assistant'} content={m.content} />
        ))}

        {/* mod 模式：用户 prompt 气泡 */}
        {mode === 'mod' && prompts.map((p, i) => (
          <ChatBubble key={i} role="user" content={p} />
        ))}

        {/* 运行中提示（所有模式）：只显示状态 + 本地 1s 秒数，具体步骤看下方事件流 */}
        {running && (
          <div className="text-xs text-faint">
            {phase === 'creating'
              ? '⏳ 正在准备工作区…'
              : `⏳ ${t('conv.running')}${displayElapsed != null ? ` · ${displayElapsed}s` : ''}…`}
          </div>
        )}

        {/* DSH 风格事件流（白名单）：思考聚合为一个默认收起的分组，*/}
        {/* 工具调用/结果单行小框，每轮回复用大框，其余运行日志不展示 */}
        <ThinkingGroup events={shownEvents.filter((e) => e.type === 'thinking')} t={t} />
        {visibleEvents.map((item) => {
          if (Array.isArray(item)) {
            const content = item.map((e) => e.content).join('\n\n')
            return <ChatBubble key={item[0].id} role="assistant" content={content} />
          }
          return <EventView key={item.id} ev={item} t={t} />
        })}

        {/* chat 模式：当前轮最终回答放在事件流之后 */}
        {mode === 'chat' && lastAssistant.map((m, i) => (
          <ChatBubble key={i} role={m.role === 'user' ? 'user' : 'assistant'} content={m.content} />
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
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-forge-500 text-3xl font-bold text-ink-950">
        M
      </div>
      <div className="text-lg font-semibold">{t('conv.title')}</div>
      <div className="max-w-md text-sm text-muted">{t('conv.desc')}</div>
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
          （点击可全选复制）
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

function Composer() {
  const { user, model, providers, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey, settingsOpen } = useUi()
  const t = useT()
  const sess = useSession()
  const [text, setText] = useState('')
  // /mod 应用内确认：不再用 window.confirm——原生对话框在"禁止此页再弹窗"
  // 或自动化环境里会被自动接受，确认形同虚设（实测缺陷）。改为状态驱动浮层。
  const [modConfirm, setModConfirm] = useState<string | null>(null)
  const running = sess.phase === 'running' || sess.phase === 'creating'
  const paused = sess.phase === 'paused' || sess.paused

  const send = () => {
    const prompt = text.trim()
    if (!prompt) return
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
      return
    }

    // 普通消息：mod 会话（含打开的历史 mod 会话）沿用 mod 模式——否则
    // 完成后的迭代需求会被降级成只读咨询（P1 实测缺陷：daemon 以 chat 重启
    // 后整个会话锁死只读）。新建/纯 chat 会话仍是 chat；server 端还有
    // mode.txt 记忆 + /mod 前缀强制双保险。
    void sendPrompt(prompt, settings, sess.mode === 'mod' ? 'mod' : 'chat')
    setText('')
  }

  const confirmMod = () => {
    if (!modConfirm) return
    const r = resolveModelConfig({ model, providers })
    const settings = { apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game: 'minecraft', loader: 'forge', version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey }
    void sendPrompt(modConfirm, settings, 'mod')
    setModConfirm(null)
    setText('')
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
      disabled={!text.trim() || !canChat}
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
      <div className="rounded-xl border border-line bg-panel p-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              if (running || paused) {
                // 运行中/暂停后回车：排队发送
                if (text.trim()) send()
              } else if (text.trim()) {
                send()
              }
            }
          }}
          rows={3}
          disabled={!canChat}
          placeholder={canChat ? t('conv.placeholder') : t('conv.noModelShort')}
          className="w-full resize-none bg-transparent text-sm outline-none placeholder:text-faint disabled:opacity-60"
        />
          <div className="mt-2 flex items-center gap-2">
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

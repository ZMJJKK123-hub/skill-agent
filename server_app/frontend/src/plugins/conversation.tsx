import { useEffect, useMemo, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { useUi, setUi, resolveModelConfig } from '../lib/store'
import { useT } from '../lib/i18n'
import { useSession, sendPrompt, startPolling, stopPolling, regenerate, answerQuestion, pauseTask, resumeTask } from '../lib/session'
import { downloadJar, downloadSourceZip } from '../lib/api'
import type { EventItem } from '../lib/api'

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

/** DSH 风格思考行：默认折叠只显示第一行，点击展开全部 */
function ThinkingRow({ ev, t }: { ev: EventItem; t: (k: string) => string }) {
  const [open, setOpen] = useState(false)
  const lines = ev.content.split('\n').filter((l) => l.trim())
  const first = lines[0] ?? ''
  return (
    <div className="flex justify-start">
      <div className="max-w-[85%]">
        <div className="mb-0.5 text-[11px] text-violet-400/80">{thinkingName(ev, t)}</div>
        <button
          onClick={() => setOpen((v) => !v)}
          className="w-full rounded-2xl rounded-bl-sm border border-violet-500/20 bg-violet-500/5 px-3 py-1.5 text-left text-xs leading-relaxed text-violet-200/80 hover:bg-violet-500/10"
        >
          <div className="whitespace-pre-wrap break-all">{open ? ev.content : first}</div>
          {!open && lines.length > 1 && (
            <div className="mt-1 text-[10px] text-faint">… 思考中（点击展开 {lines.length - 1} 行）</div>
          )}
          {open && lines.length > 1 && (
            <div className="mt-1 text-[10px] text-faint">▲ 收起</div>
          )}
        </button>
      </div>
    </div>
  )
}

/** 工具调用行：特殊颜色标注 工具名 + 参数/命令 */
function ToolCallRow({ ev }: { ev: EventItem }) {
  const tool = ev.tool ?? 'tool'
  const peerLabel = ev.peer === 'supervisor' ? '🛡 ' : ev.peer === 'teammate' ? '👥 ' : ev.peer === 'subagent' ? '🔬 ' : ''
  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] rounded-lg border border-amber-500/25 bg-amber-500/5 px-3 py-1.5">
        <div className="flex items-center gap-1.5 text-xs">
          <span className="font-semibold text-amber-400">🔧 {peerLabel}{tool}</span>
          <span className="text-faint">调用</span>
        </div>
        <div className="mt-0.5 whitespace-pre-wrap break-all font-mono text-[11px] text-amber-100/70">{ev.content}</div>
      </div>
    </div>
  )
}

/** 工具结果：代码块样式（成功绿边 / 失败红边），可折叠 */
function ToolResultRow({ ev }: { ev: EventItem }) {
  const [open, setOpen] = useState(true)
  const ok = ev.status !== 'failed'
  // 去掉首行 "success|failed" 标记，只显示输出内容
  const lines = ev.content.split('\n')
  const body = (lines.slice(1).join('\n').trim() || (lines[0] ?? '')).trim()
  const preview = body.split('\n').slice(0, 6).join('\n')
  return (
    <div className="flex justify-start">
      <div className={`w-full max-w-[90%] overflow-hidden rounded-lg border ${ok ? 'border-emerald-500/25' : 'border-red-500/30'}`}>
        <button
          onClick={() => setOpen((v) => !v)}
          className={`flex w-full items-center gap-1.5 px-2 py-1 text-[10px] font-medium ${ok ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}
        >
          <span>{ok ? '✓' : '✗'}</span>
          <span>{ok ? '执行成功' : '执行失败'}</span>
          <span className="flex-1" />
          <span>{open ? '▲ 收起' : `▼ 展开（${body.length} 字符）`}</span>
        </button>
        {open && (
          <pre className="max-h-64 overflow-auto whitespace-pre-wrap break-all bg-black/30 px-2 py-1.5 font-mono text-[11px] leading-relaxed text-muted">
            {open ? body : preview}
          </pre>
        )}
      </div>
    </div>
  )
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

/** DSH 风格事件渲染器：按类型分派 */
function EventView({ ev, t }: { ev: EventItem; t: (k: string) => string }) {
  switch (ev.type) {
    case 'thinking':
      return <ThinkingRow ev={ev} t={t} />
    case 'tool_call':
      return <ToolCallRow ev={ev} />
    case 'tool_result':
      return <ToolResultRow ev={ev} />
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
  const { user, apiKey } = useUi()
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

  const shownEvents = useMemo(() => events.slice(-120), [events])

  // chat 模式：把“当前轮”的事件插在最后一个 assistant 回复之前，
  // 避免最终回答先于思考/工具过程出现；之前的轮次尽量保持原始顺序。
  let lastAssistantIdx = -1
  chatMessages.forEach((m, i) => {
    if (m.role === 'assistant') lastAssistantIdx = i
  })
  const beforeLastAssistant = lastAssistantIdx >= 0 ? chatMessages.slice(0, lastAssistantIdx) : chatMessages
  const lastAssistant = lastAssistantIdx >= 0 ? chatMessages.slice(lastAssistantIdx) : []
  const running = phase === 'running' || phase === 'creating'

  // 空态判断以"是否有会话"为准：无会话 → 引导页；
  // 有会话（含历史会话，phase=idle + chatMessages 有内容）→ 显示聊天流
  if (!sessionId) {
    return <EmptyState loggedIn={!!user} configured={!!apiKey} />
  }

  // ── 统一微信式聊天流：chat 模式显示气泡对话；mod 模式 DSH 风格事件流 ──
  return (
    <div className="mx-auto max-w-3xl space-y-3 p-4">
      <div className="space-y-2">
        {/* chat 模式：历史消息（保持原始顺序，最后一个 assistant 留到事件流之后） */}
        {mode === 'chat' && beforeLastAssistant.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
            <div
              className={
                m.role === 'user'
                  ? 'max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-forge-500 px-4 py-2 text-sm text-ink-950'
                  : 'max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-bl-sm border border-line bg-panel px-4 py-2 text-sm'
              }
            >
              {m.content}
            </div>
          </div>
        ))}

        {/* mod 模式：用户 prompt 气泡 */}
        {mode === 'mod' && prompts.map((p, i) => (
          <div key={i} className="flex justify-end">
            <div className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-sm bg-forge-500 px-4 py-2 text-sm text-ink-950">
              {p}
            </div>
          </div>
        ))}

        {/* 运行中提示（所有模式）：只显示状态 + 本地 1s 秒数，具体步骤看下方事件流 */}
        {running && (
          <div className="text-xs text-faint">
            {phase === 'creating'
              ? '⏳ 正在准备工作区…'
              : `⏳ ${t('conv.running')}${displayElapsed != null ? ` · ${displayElapsed}s` : ''}…`}
          </div>
        )}

        {/* DSH 风格事件流：chat / mod 都实时展示 agent 的思考、工具调用、结果与日志 */}
        {shownEvents.map((ev) => (
          <EventView key={ev.id} ev={ev} t={t} />
        ))}

        {/* chat 模式：当前轮最终回答放在事件流之后 */}
        {mode === 'chat' && lastAssistant.map((m, i) => (
          <div key={i} className="flex justify-start">
            <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-bl-sm border border-line bg-panel px-4 py-2 text-sm">
              {m.content}
            </div>
          </div>
        ))}

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
            ⬇ {t('conv.downloadJar')}
          </button>
          <button
            onClick={() => sess.sessionId && downloadSourceZip(sess.sessionId).catch((e) => alert(errMsg(e)))}
            className="hoverable rounded-lg border border-line px-3 py-1.5 text-sm"
          >
            ⬇ {t('conv.downloadZip')}
          </button>
          <button onClick={() => regenerate()} className="hoverable rounded-lg border border-line px-3 py-1.5 text-sm">
            🔄 {t('conv.regenerate')}
          </button>
          {phase === 'finished' && <span className="text-xs text-emerald-400">{t('conv.done')}</span>}
        </div>
      )}
    </div>
  )
}

function EmptyState({ loggedIn, configured }: { loggedIn: boolean; configured: boolean }) {
  const t = useT()
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-forge-500 text-3xl font-bold text-ink-950">
        M
      </div>
      <div className="text-lg font-semibold">{t('conv.title')}</div>
      <div className="max-w-md text-sm text-muted">{t('conv.desc')}</div>
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
  const { user, apiKey, model, providers, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey } = useUi()
  const t = useT()
  const sess = useSession()
  const [text, setText] = useState('')
  const running = sess.phase === 'running' || sess.phase === 'creating'
  const paused = sess.phase === 'paused' || sess.paused

  const models = ['deepseek-v4-flash', 'deepseek-v4-pro', ...providers.map((p) => p.model)]

  const send = () => {
    const prompt = text.trim()
    if (!prompt) return
    const r = resolveModelConfig({ apiKey, model, providers })
    const settings = { apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game: 'minecraft', loader: 'forge', version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey }

    // /mod 拦截：固定格式触发 mod 制作模式
    if (prompt.startsWith('/mod')) {
      const modPrompt = prompt.slice(4).trim()
      if (!modPrompt) {
        alert('用法：/mod <你的 MOD 需求描述>，例如：/mod 做一把钻石剑')
        return
      }
      const ok = window.confirm(`即将复制 MOD 模板与 MC 源码，开始制作 MOD：\n\n“${modPrompt.slice(0, 80)}${modPrompt.length > 80 ? '…' : ''}”\n\n确认开始吗？`)
      if (!ok) return
      void sendPrompt(modPrompt, settings, 'mod')
      setText('')
      return
    }

    // 普通消息：chat 模式（通用对话，不复制模板）；运行中则排队
    void sendPrompt(prompt, settings, 'chat')
    setText('')
  }

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
      disabled={!text.trim()}
      className="rounded-lg bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
    >
      {t('conv.send')}
    </button>
  )

  return (
    <div className="mx-auto max-w-3xl">
      <QuestionCard />
      {(!user || (!apiKey && providers.length === 0)) && sess.sessionId ? (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-400">
          {!user ? t('auth.loginFirst') : t('auth.needApiKey')}
        </div>
      ) : (!user || (!apiKey && providers.length === 0)) && !sess.sessionId ? null : (
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
            placeholder={t('conv.placeholder')}
            className="w-full resize-none bg-transparent text-sm outline-none placeholder:text-faint"
          />
          <div className="mt-2 flex items-center gap-2">
            <select
              value={model}
              onChange={(e) => setUi({ model: e.target.value })}
              className="rounded-md border border-line bg-field px-2 py-1 text-xs text-muted outline-none"
            >
              <optgroup label="DeepSeek">
                <option value="deepseek-v4-flash">deepseek-v4-flash</option>
                <option value="deepseek-v4-pro">deepseek-v4-pro</option>
              </optgroup>
              {providers.map((p) => (
                <optgroup key={p.id} label={p.name}>
                  {p.model.split(',').map((m) => m.trim()).filter(Boolean).map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </optgroup>
              ))}
            </select>
            <div className="flex-1" />
            {running && sess.pending > 0 && (
              <span className="text-xs text-faint">{sess.pending} 条排队…</span>
            )}
            {actionButton}
          </div>
        </div>
      )}
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

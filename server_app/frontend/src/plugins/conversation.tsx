import { useEffect, useMemo, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { useUi, setUi, resolveModelConfig } from '../lib/store'
import { useT } from '../lib/i18n'
import { useSession, sendPrompt, startPolling, stopPolling, regenerate, answerQuestion } from '../lib/session'
import { downloadJar, downloadSourceZip } from '../lib/api'
import type { EventItem } from '../lib/api'

const EVENT_META: Record<string, { icon: string; color: string }> = {
  thinking: { icon: '🧠', color: 'text-violet-400' },
  tool_call: { icon: '🔧', color: 'text-forge-400' },
  todo: { icon: '📋', color: 'text-amber-400' },
  round: { icon: '🔁', color: 'text-faint' },
  system: { icon: '⚙️', color: 'text-faint' },
  background: { icon: '⏳', color: 'text-faint' },
  protocol: { icon: '🤝', color: 'text-emerald-400' },
  worktree: { icon: '🌲', color: 'text-emerald-400' },
  log: { icon: '📄', color: 'text-faint' },
}

function errMsg(e: unknown): string {
  if (e instanceof Error) return e.message
  return String(e)
}

function EventRow({ ev }: { ev: EventItem }) {
  const meta = EVENT_META[ev.type] ?? { icon: '·', color: 'text-faint' }
  return (
    <div className="flex gap-2 py-0.5 font-mono text-[11px] leading-relaxed">
      <span className={`shrink-0 ${meta.color}`}>{meta.icon}</span>
      <span className="whitespace-pre-wrap break-all text-muted">{ev.content}</span>
    </div>
  )
}

function Messages() {
  const { user, apiKey } = useUi()
  const t = useT()
  const sess = useSession()
  const { phase, prompts, events, elapsed, hasJar, error, mode, chatMessages } = sess

  useEffect(() => {
    if (phase === 'running') {
      startPolling(2000)
      return () => stopPolling()
    }
  }, [phase])

  const shownEvents = useMemo(() => events.slice(-80), [events])

  if (phase === 'idle' && prompts.length === 0) {
    return <EmptyState loggedIn={!!user} configured={!!apiKey} />
  }

  // chat 模式：聊天气泡展示（用户消息 + agent 回复）
  if (mode === 'chat') {
    return (
      <div className="mx-auto max-w-3xl space-y-4 p-4">
        <div className="space-y-3">
          {chatMessages.map((m, i) => (
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
          {phase === 'running' && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-sm border border-line bg-panel px-4 py-2 text-sm text-faint">
                {t('conv.running')}
                {elapsed ? ` · ${elapsed}s` : ''}…
              </div>
            </div>
          )}
          {error && <div className="text-sm text-red-400">{errMsg(error)}</div>}
        </div>
      </div>
    )
  }

  // mod 模式：原有事件流面板
  return (
    <div className="mx-auto max-w-3xl space-y-4 p-4">
      {prompts.map((p, i) => (
        <div key={i} className="flex justify-end">
          <div className="max-w-[80%] rounded-2xl rounded-br-sm bg-forge-500 px-4 py-2 text-sm text-ink-950">
            {p}
          </div>
        </div>
      ))}

      <div className="rounded-xl border border-line bg-panel">
        <div className="flex items-center gap-2 border-b border-line px-3 py-2 text-sm">
          <span className="font-medium">{t('conv.section')}</span>
          {phase === 'running' && (
            <span className="text-forge-400">
              {t('conv.running')}
              {elapsed ? ` · ${elapsed}s` : ''}…
            </span>
          )}
          {phase === 'finished' && <span className="text-emerald-400">{t('conv.done')}</span>}
          {phase === 'error' && <span className="text-red-400">{t('conv.failed')}</span>}
        </div>

        <div className="max-h-80 space-y-0.5 overflow-y-auto p-3">
          {phase === 'creating' && (
            <div className="text-sm text-faint">正在创建工作区（复制模板与 MC 源码）…</div>
          )}
          {shownEvents.length === 0 && phase === 'running' && (
            <div className="text-sm text-faint">{t('conv.starting')}</div>
          )}
          {shownEvents.map((ev) => (
            <EventRow key={ev.id} ev={ev} />
          ))}
          {error && <div className="text-sm text-red-400">{errMsg(error)}</div>}
        </div>

        {phase === 'finished' && (
          <div className="flex flex-wrap gap-2 border-t border-line p-3">
            <button
              onClick={() => sess.sessionId && downloadJar(sess.sessionId).catch((e) => alert(errMsg(e)))}
              disabled={!hasJar}
              title={hasJar ? '' : t('conv.noJar')}
              className="rounded-md bg-forge-500 px-3 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
            >
              ⬇ {t('conv.downloadJar')}
            </button>
            <button
              onClick={() => sess.sessionId && downloadSourceZip(sess.sessionId).catch((e) => alert(errMsg(e)))}
              className="hoverable rounded-md border border-line px-3 py-1.5 text-sm"
            >
              {t('conv.downloadZip')}
            </button>
            <button onClick={() => regenerate()} className="hoverable rounded-md border border-line px-3 py-1.5 text-sm">
              🔄 {t('conv.regenerate')}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

function EmptyState({ loggedIn, configured }: { loggedIn: boolean; configured: boolean }) {
  const t = useT()
  const hints: string[] = []
  if (!loggedIn) hints.push(t('auth.loginFirst'))
  if (!configured) hints.push(t('auth.needApiKey'))
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-forge-500 text-3xl font-bold text-ink-950">
        M
      </div>
      <div className="text-lg font-semibold">{t('conv.title')}</div>
      <div className="max-w-md text-sm text-muted">{t('conv.desc')}</div>
      {hints.length > 0 && (
        <div className="flex flex-col gap-1 text-xs text-amber-400">{hints.map((h) => <span key={h}>⚠ {h}</span>)}</div>
      )}
    </div>
  )
}

function QuestionCard() {
  const sess = useSession()
  const [text, setText] = useState('')
  const q = sess.question
  if (!q) return null
  const submit = (v: string) => {
    answerQuestion(v)
    setText('')
  }
  return (
    <div className="mb-2 rounded-xl border border-forge-500/40 bg-forge-500/10 p-3">
      <div className="mb-2 text-sm font-medium text-forge-300">💬 {q.question}</div>
      {q.options.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {q.options.map((o) => (
            <button
              key={o}
              onClick={() => submit(o)}
              className="rounded-md border border-forge-500/40 px-3 py-1 text-sm text-forge-400 hover:bg-forge-500/10"
            >
              {o}
            </button>
          ))}
        </div>
      )}
      <div className="flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && text.trim()) submit(text.trim())
          }}
          placeholder="输入回答…"
          className="flex-1 rounded-md border border-line bg-field px-3 py-1.5 text-sm outline-none"
        />
        <button
          onClick={() => text.trim() && submit(text.trim())}
          className="rounded-md bg-forge-500 px-3 py-1.5 text-sm text-ink-950"
        >
          回答
        </button>
      </div>
    </div>
  )
}

function Composer() {
  const { user, apiKey, model, providers, version, sandbox } = useUi()
  const t = useT()
  const sess = useSession()
  const [text, setText] = useState('')
  const busy = sess.phase === 'running' || sess.phase === 'creating'

  const models = ['deepseek-v4-flash', 'deepseek-v4-pro', ...providers.map((p) => p.model)]

  const send = () => {
    const prompt = text.trim()
    if (!prompt || busy) return
    const r = resolveModelConfig({ apiKey, model, providers })
    const settings = { apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game: 'minecraft', loader: 'forge', version, sandbox }

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

    // 普通消息：chat 模式（通用对话，不复制模板）
    sendPrompt(prompt, settings, 'chat')
    setText('')
  }

  return (
    <div className="mx-auto max-w-3xl">
      <QuestionCard />
      {!user ? (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-400">{t('auth.loginFirst')}</div>
      ) : !apiKey && providers.length === 0 ? (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-400">{t('auth.needApiKey')}</div>
      ) : (
        <div className="rounded-xl border border-line bg-panel p-3">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
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
            <button
              onClick={send}
              disabled={!text.trim() || busy}
              className="rounded-lg bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
            >
              {busy ? t('conv.generating') : t('conv.send')}
            </button>
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

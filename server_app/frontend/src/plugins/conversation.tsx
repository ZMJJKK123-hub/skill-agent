import { useEffect, useMemo, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { useUi, setUi } from '../lib/store'
import { useT } from '../lib/i18n'
import { useSession, sendPrompt, startPolling, stopPolling, regenerate } from '../lib/session'
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
  const { phase, prompts, events, elapsed, hasJar, error } = sess

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

function Composer() {
  const { user, apiKey, model, providers, version } = useUi()
  const t = useT()
  const sess = useSession()
  const [text, setText] = useState('')
  const busy = sess.phase === 'running' || sess.phase === 'creating'

  const models = ['deepseek-v4-flash', 'deepseek-v4-pro', ...providers.map((p) => p.model)]

  const send = () => {
    const prompt = text.trim()
    if (!prompt || busy) return
    sendPrompt(prompt, { apiKey, game: 'minecraft', loader: 'forge', version })
    setText('')
  }

  return (
    <div className="mx-auto max-w-3xl">
      {!user ? (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-400">{t('auth.loginFirst')}</div>
      ) : !apiKey ? (
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
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
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

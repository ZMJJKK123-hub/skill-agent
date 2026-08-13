import { PluginManifest, SLOTS } from '../shell/registry'
import { useT } from '../lib/i18n'
import { useSession, regenerate } from '../lib/session'
import { downloadJar, downloadSourceZip } from '../lib/api'

function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : String(e)
}

function GeneratePanel() {
  const t = useT()
  const sess = useSession()
  const { phase, elapsed, hasJar, sessionId } = sess

  return (
    <div className="p-4">
      <h2 className="mb-3 text-sm font-semibold">{t('conv.section')}</h2>
      <div className="space-y-2 text-sm text-muted">
        <div className="flex justify-between">
          <span>{t('nav.sessions')}</span>
          <span className={phase === 'running' ? 'text-forge-400' : phase === 'finished' ? 'text-emerald-400' : 'text-faint'}>
            {phase === 'running' ? t('conv.running') : phase === 'finished' ? t('conv.done') : '—'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>{t('conv.running')}</span>
          <span className="text-faint">{elapsed ? `${elapsed}s` : '—'}</span>
        </div>
        <div className="flex justify-between">
          <span>ID</span>
          <span className="text-faint">{sessionId ? sessionId.slice(0, 8) + '…' : '—'}</span>
        </div>
      </div>

      {phase === 'finished' && sessionId && (
        <div className="mt-4 space-y-2">
          <button
            onClick={() => downloadJar(sessionId).catch((e) => alert(errMsg(e)))}
            disabled={!hasJar}
            title={hasJar ? '' : t('conv.noJar')}
            className="w-full rounded-md bg-forge-500 py-2 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
          >
            ⬇ {t('conv.downloadJar')}
          </button>
          <button onClick={() => downloadSourceZip(sessionId).catch((e) => alert(errMsg(e)))} className="hoverable w-full rounded-md border border-line py-2 text-sm">
            {t('conv.downloadZip')}
          </button>
          <button onClick={() => regenerate()} className="hoverable w-full rounded-md border border-line py-2 text-sm">
            🔄 {t('conv.regenerate')}
          </button>
        </div>
      )}
      <p className="mt-2 text-xs text-faint">jar 由后端构建后写入 mod/dist/。</p>
    </div>
  )
}

export const generatePlugin: PluginManifest = {
  id: 'modforge-generate',
  name: '生成监控',
  apply(ctx) {
    ctx.slots.inject(SLOTS.details, 'generate', () => <GeneratePanel />)
  },
}

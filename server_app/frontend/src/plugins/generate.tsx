import { PluginManifest, SLOTS } from '../shell/registry'
import { useT } from '../lib/i18n'
import { useSession } from '../lib/session'

function GeneratePanel() {
  const t = useT()
  const sess = useSession()
  const { phase, elapsed, sessionId, mode } = sess

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
          <span>模式</span>
          <span className="text-faint">{mode === 'mod' ? 'MOD 制作' : mode === 'chat' ? '普通对话' : '—'}</span>
        </div>
        <div className="flex justify-between">
          <span>ID</span>
          <span className="text-faint">{sessionId ? sessionId.slice(0, 8) + '…' : '—'}</span>
        </div>
      </div>
      <p className="mt-2 text-xs text-faint">jar 由后端构建后写入 mod/dist/；下载按钮在对话底部（mod 模式）。</p>
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

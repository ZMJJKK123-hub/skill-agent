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
          <span className={`flex items-center gap-1.5 ${phase === 'running' ? 'text-forge-400' : phase === 'finished' ? 'text-emerald-400' : 'text-faint'}`}>
            {phase === 'running' ? (
              <>
                <svg className="h-3 w-3 animate-spin text-forge-400" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                {t('conv.running')}
              </>
            ) : phase === 'finished' ? (
              <>
                <span className={`h-1.5 w-1.5 rounded-full ${/任务异常终止|Traceback \(most recent call last\)/.test(sess.logTail) ? 'bg-red-500' : 'bg-emerald-500'}`} />
                {t('conv.done')}
              </>
            ) : '—'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>耗时</span>
          {/* P2 修复：elapsed 只在 running 态展示——已完成会话的 elapsed 是从
              文件时间推断的残留值，与"完成 ✓"并排显示"进行中 60s"自相矛盾（实测） */}
          <span className="text-faint">{phase === 'running' && elapsed ? `${elapsed}s` : '—'}</span>
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

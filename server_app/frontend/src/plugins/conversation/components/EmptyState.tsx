/**
 * 空态引导页：快捷示例 + 发起失败提示 + 作者联系卡。
 * 由 conversation.tsx 原样迁出，行为不变。
 */
import { useT } from '../../../lib/i18n'

export function EmptyState({ error }: { error?: string | null }) {
  const t = useT()
  // 快捷示例：点击填入输入框（经自定义事件，Composer 监听后 setText + 聚焦）。
  const quickPicks = [t('conv.quickSword'), t('conv.quickFood'), t('conv.quickBlock')]
  // 错峰入场：logo → 标题 → 描述 → chips → 联系卡依次淡入
  const step = (i: number) => ({ animationDelay: `${i * 90}ms` })
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div style={step(0)} className="fade-in-up flex h-14 w-14 items-center justify-center rounded-2xl bg-forge-500 text-3xl font-bold text-ink-950">
        M
      </div>
      <div style={step(1)} className="fade-in-up text-lg font-semibold">{t('conv.title')}</div>
      <div style={step(2)} className="fade-in-up max-w-md text-sm text-muted">{t('conv.desc')}</div>
      <div style={step(3)} className="fade-in-up mt-2 flex max-w-lg flex-wrap justify-center gap-2">
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
      {/* 发起失败（服务失联/404/断网等）在空态也要可见 */}
      {error && (
        <div className="max-w-md rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
          <div className="font-medium">发起失败：{error}</div>
          {/404|Not Found/i.test(error) && (
            <div className="mt-1 text-xs text-red-300/80">服务连接异常（404）：服务可能已更新或重启，请刷新页面后重试。</div>
          )}
        </div>
      )}
      {/* 作者联系方式：放空态空白处，方便用户咨询 */}
      <div style={step(4)} className="fade-in-up mt-6 max-w-sm rounded-xl border border-line bg-panel/60 p-3 text-xs text-muted">
        <div className="mb-1 font-medium text-forge-300">{t('contact.title')}</div>
        <div>
          {t('contact.desc')}
          <span
            className="cursor-pointer select-all rounded bg-field px-1.5 py-0.5 font-mono text-forge-300"
            title={t('contact.copyTitle')}
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

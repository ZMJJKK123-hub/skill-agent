/**
 * 输入区右侧动作按钮三态：运行中=停止、暂停=继续、空闲=发送。
 * 由 Composer 原样迁出，行为不变。
 */
import { useT } from '../../../lib/i18n'

export function SendControls({ running, paused, disabled, title, onSend, onPause, onResume }: {
  running: boolean
  paused: boolean
  disabled: boolean
  title: string
  onSend: () => void
  onPause: () => void
  onResume: () => void
}) {
  const t = useT()
  if (running) {
    return (
      <button
        onClick={onPause}
        title={t('conv.pause')}
        className="flex h-9 w-9 items-center justify-center rounded-full border border-red-500/50 text-red-400 hover:bg-red-500/10"
      >
        {/* 停止：圆圈内红色方块 */}
        <span className="block h-3.5 w-3.5 rounded-[3px] bg-red-500" />
      </button>
    )
  }
  if (paused) {
    return (
      <button
        onClick={onResume}
        title={t('conv.resume')}
        className="flex h-9 w-9 items-center justify-center rounded-full border border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10"
      >
        {/* 继续：绿色三角箭头 */}
        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
          <path d="M4 2l10 6-10 6V2z" />
        </svg>
      </button>
    )
  }
  return (
    <button
      onClick={onSend}
      disabled={disabled}
      title={title}
      className="rounded-lg bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
    >
      {t('conv.send')}
    </button>
  )
}

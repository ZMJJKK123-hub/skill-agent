/**
 * /mod 应用内确认条（替代原生 confirm——原生对话框在"禁止此页再弹窗"
 * 或自动化环境里会被自动接受，确认形同虚设）。原样迁出。
 */
export function ModConfirmBar({ prompt, onConfirm, onCancel }: { prompt: string; onConfirm: () => void; onCancel: () => void }) {
  return (
    <div className="mb-2 rounded-xl border border-forge-500/40 bg-forge-500/10 p-3">
      <div className="mb-1 text-xs font-medium text-forge-300">即将开始 MOD 制作</div>
      <div className="mb-2 text-sm text-main">
        将复制 MOD 模板与 MC 源码，开始制作：“{prompt.slice(0, 80)}{prompt.length > 80 ? '…' : ''}”
      </div>
      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          className="rounded-md bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400"
        >
          ✓ 确认开始
        </button>
        <button
          onClick={onCancel}
          className="hoverable rounded-md border border-line px-4 py-1.5 text-sm"
        >
          取消
        </button>
      </div>
    </div>
  )
}

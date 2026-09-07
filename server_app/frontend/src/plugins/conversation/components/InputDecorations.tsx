/**
 * 输入区装饰组件：待上传图片缩略图条 + textarea 键盘事件处理。
 * 由 Composer 原样迁出，行为不变。
 */

/** 待上传图片缩略图（选择/粘贴/拖拽后、发送前）+ 数量计数 + 移除按钮 */
export function UploadThumbStrip({ images, onRemove }: {
  images: string[]
  onRemove: (i: number) => void
}) {
  if (images.length === 0) return null
  return (
    <div className="mb-2 flex flex-wrap items-start gap-2">
      {images.map((src, i) => (
        <div key={i} className="relative">
          <img src={src} alt={`待上传 ${i + 1}`} className="h-20 w-20 rounded-lg border border-line object-cover" />
          <button
            onClick={() => onRemove(i)}
            title="移除图片"
            className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full border border-line bg-panel text-[10px] text-faint hoverable hover:text-red-400"
          >
            ✕
          </button>
        </div>
      ))}
      <span className="self-end text-[11px] text-faint">{images.length}/4</span>
    </div>
  )
}

/** textarea 键盘处理：命令面板导航（↑↓/Tab/Enter/Esc）+ 回车发送。
 *  输入法组合中的 Enter 是"选候选词"，不是发送（isComposing 检查）。 */
export function handleTextareaKey(e: React.KeyboardEvent<HTMLTextAreaElement>, ctx: {
  cmdOpen: boolean
  cmdCount: number
  onCmdIndex: (fn: (i: number) => number) => void
  onApplyCmd: () => void
  onCloseCmd: () => void
  onSend: () => void
  canSend: boolean
}): void {
  if (e.nativeEvent.isComposing) return
  const { cmdOpen, cmdCount, onCmdIndex, onApplyCmd, onCloseCmd, onSend, canSend } = ctx
  if (cmdOpen && cmdCount > 0) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Tab') {
      e.preventDefault()
      const dir = e.key === 'ArrowUp' ? -1 : 1
      onCmdIndex((i) => (i + dir + cmdCount) % cmdCount)
      return
    }
    if (e.key === 'Enter') {
      e.preventDefault()
      onApplyCmd()
      return
    }
    if (e.key === 'Escape') {
      e.preventDefault()
      onCloseCmd()
      return
    }
  }
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (canSend) onSend()
  }
}

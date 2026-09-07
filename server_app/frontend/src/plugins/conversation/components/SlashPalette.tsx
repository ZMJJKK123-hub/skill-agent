/**
 * "/" 命令面板：输入以 / 开头时弹出，↑↓/Tab 移动高亮，Enter 选中，
 * Esc 关闭（键盘处理在 Composer 的 onKeyDown 里，此处只渲染）。
 */
export interface SlashCommand {
  cmd: string
  desc: string
}

export function SlashPalette({ commands, index, onApply, onHover }: {
  commands: SlashCommand[]
  index: number
  onApply: (cmd: string) => void
  onHover: (i: number) => void
}) {
  return (
    <div className="absolute bottom-full left-0 right-0 z-30 mb-2 overflow-hidden rounded-xl border border-line bg-panel shadow-lg">
      <div className="border-b border-line px-3 py-1.5 text-[10px] text-faint">命令</div>
      {commands.map((c, i) => (
        <button
          key={c.cmd}
          // onMouseDown 先于 blur 触发，保证点击能选中
          onMouseDown={(e) => {
            e.preventDefault()
            onApply(c.cmd)
          }}
          onMouseEnter={() => onHover(i)}
          className={`flex w-full items-baseline gap-2 px-3 py-2 text-left text-[13px] transition ${i === index ? 'bg-subtle' : ''}`}
        >
          <span className="shrink-0 font-mono font-medium text-forge-400">{c.cmd}</span>
          <span className="min-w-0 flex-1 truncate text-muted">{c.desc}</span>
        </button>
      ))}
    </div>
  )
}

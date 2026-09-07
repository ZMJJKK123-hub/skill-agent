/**
 * 设置面板公共 UI 原子（由 settings.tsx 迁出）。
 */
import type { ReactNode } from 'react'

/** 表单字段容器：标签 + 控件 */
export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="mb-3">
      <div className="mb-1 text-sm text-muted">{label}</div>
      {children}
    </div>
  )
}

/** 开关按钮（设置面板通用样式；on 决定滑块位置与配色） */
export function Toggle({ on, onClick, size = 'md' }: {
  on: boolean
  onClick: () => void
  size?: 'md' | 'sm'
}) {
  const dims = size === 'md'
    ? { track: 'h-6 w-11', knob: 'h-5 w-5', on: 'left-[22px]' }
    : { track: 'h-5 w-9', knob: 'h-4 w-4', on: 'left-[18px]' }
  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative ${dims.track} rounded-full transition ${on ? 'bg-forge-500' : 'bg-slate-600'}`}
    >
      <span className={`absolute top-0.5 ${dims.knob} rounded-full bg-white transition ${on ? dims.on : 'left-0.5'}`} />
    </button>
  )
}

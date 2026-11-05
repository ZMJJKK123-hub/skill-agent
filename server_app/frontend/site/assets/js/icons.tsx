// React 类型约束图标节点和返回值，不引入第三方图标运行时。
import type { ReactElement, ReactNode } from 'react'
// 名称和展示参数独立于图形实现，供各分区使用。
import type { IconName, IconProps } from './icons.types.ts'

/** 共享描边图标，无 I/O 或注册副作用。 */
const shapes: Record<IconName, ReactNode> = {
  cube: <><path d="m12 3 9 5v8l-9 5-9-5V8l9-5Z" /><path d="m3 8 9 5 9-5M12 13v8M7.5 5.5l9 5" /></>,
  plus: <path d="M12 5v14M5 12h14" />,
  chat: <path d="M20 15a3 3 0 0 1-3 3H8l-5 3V6a3 3 0 0 1 3-3h11a3 3 0 0 1 3 3v9ZM7 8h9M7 12h6" />,
  settings: <><path d="m9 4 1-2h4l1 2 3 2 2 .5 2 3-1 2v3l1 2-2 3-2 .5-3 2-1 2h-4l-1-2-3-2-2-.5-2-3 1-2v-3l-1-2 2-3 2-.5 3-2Z" transform="translate(2 1) scale(.83)" /><circle cx="12" cy="12" r="3" /></>,
  sidebar: <><rect x="3" y="4" width="18" height="16" rx="3" /><path d="M9 4v16M5.5 8h1M5.5 12h1" /></>,
  details: <><rect x="3" y="4" width="18" height="16" rx="3" /><path d="M15 4v16M18 8h.5M18 12h.5" /></>,
  arrow: <path d="M5 19 19 5M5 5h14v14" />,
  send: <path d="M12 19V5m-6 6 6-6 6 6" />,
  sparkles: <><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3ZM20 2v4M18 4h4" /></>,
  close: <path d="m6 6 12 12M6 18 18 6" />,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  leaf: <path d="M20 3c-9 0-16 2-16 10a6 6 0 0 0 6 6c8 0 10-7 10-16ZM3 21l12-12M8 16v-5M8 16h5" />,
  sword: <path d="M14 3h7v7L10 18l-4-4L14 3ZM4 12l8 8M3 21l5-5M15 9l3-3" />,
  gamepad: <><path d="M7 7h10a4 4 0 0 1 4 3l1 7a2 2 0 0 1-3 2l-3-3H8l-3 3a2 2 0 0 1-3-2l1-7a4 4 0 0 1 4-3Z" /><path d="M7 10v5M4.5 12.5h5M16 11h.1M19 14h.1" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  login: <><path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4M3 12h12m-4-4 4 4-4 4" /></>,
  layers: <path d="m12 3 10 6-10 6L2 9l10-6ZM2 13l10 6 10-6M2 17l10 6 10-6" />,
  globe: <><circle cx="12" cy="12" r="9" /><ellipse cx="12" cy="12" rx="4" ry="9" /><path d="M3 12h18" /></>,
  eye: <><path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" /></>,
  sliders: <><path d="M4 7h5m4 0h7M4 17h9m4 0h3" /><circle cx="11" cy="7" r="2" /><circle cx="15" cy="17" r="2" /></>,
  sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5" /></>,
}

/** 渲染装饰图标，控件名称由外层按钮或标签负责。
 * Args: name 为受约束的图形；size 默认 18 像素；className 用于分区样式。
 * Returns: 不接收焦点的 SVG，无网络、存储或失败分支。
 * Globals Used: shapes。Dependencies: React SVG 渲染。
 */
export function Icon({ name, size = 18, className }: IconProps): ReactElement {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true" focusable="false">{shapes[name]}</svg>
}

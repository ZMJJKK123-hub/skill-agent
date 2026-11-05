/** 只包含已使用的图标名称，禁止未知图形字符串。 */
export type IconName = 'cube' | 'plus' | 'chat' | 'settings' | 'sidebar' | 'details' | 'arrow' | 'send' | 'sparkles' | 'close' | 'clock' | 'leaf' | 'sword' | 'gamepad' | 'check' | 'login' | 'layers' | 'globe' | 'eye' | 'sliders' | 'sun'

/** 图标由父控件提供可访问名称，尺寸单位为 CSS 像素。 */
export interface IconProps { name: IconName; size?: number; className?: string }

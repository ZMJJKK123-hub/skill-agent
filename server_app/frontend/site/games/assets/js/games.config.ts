/** 小游戏选项、转发按键和窗口尺寸（像素）；仅由小游戏分区消费。 */
export const GAMES: readonly { id: string; label: string }[] = [
  { id: 'snake-2048', label: '🐍 Snake 2048' },
  { id: 'casino', label: '🎰 算力赌坊（梭哈）' },
]

export const FORWARD_KEYS: ReadonlySet<string> = new Set([
  'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  'w', 'a', 's', 'd', 'W', 'A', 'S', 'D', ' ',
  'r', 'R', 'Enter', 'Escape',
])

export const INIT_W: number = 600
export const INIT_H: number = 560
export const MIN_W: number = 360
export const MIN_H: number = 320

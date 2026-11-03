// 小游戏分区的选项与尺寸独立配置，不放入跨分区共享区。
import { GAMES, FORWARD_KEYS, INIT_W, INIT_H, MIN_W, MIN_H } from './games.config.ts'
// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// 本分区样式仅在当前分区模块加载时挂载。
import '../css/games.css'
// React hooks 用于组件状态、订阅和生命周期。
import { useState, useRef, useEffect, useCallback } from 'react'
// 类型契约约束分区间的数据和组件通信。
import type { PluginManifest, PluginContext } from '../../../assets/js/slots.types.ts'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 翻译 hook 为本分区提供当前语言文案。
import { useT } from '../../../assets/js/i18n.ts'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useSession } from '../../../assets/js/application-context.tsx'

// 主页小游戏浮窗：可拖拽 + 可缩放
// 游戏本体复用 debug 维护页的游戏，零重复实现。
// 当前只上线 Snake 2048；其余游戏取消注释即可复原。

/** 管理小游戏窗口、选择、重启、拖拽和尺寸；关闭时清理键盘转发。
 * Args: 无参数；本地维护窗口位置、尺寸、游戏选项及 iframe 引用。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context；浏览器界面事件/确认。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function GameWindow(): ReactElement {
  const t = useT()
  const sess = useSession()
  const [open, setOpen] = useState(false)
  const [game, setGame] = useState('snake-2048')
  const [nonce, setNonce] = useState(0)

  // 窗口位置和尺寸
  const [pos, setPos] = useState({ x: window.innerWidth - INIT_W - 20, y: 80 })
  const [size, setSize] = useState({ w: INIT_W, h: INIT_H })
  const panelRef = useRef<HTMLDivElement>(null)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // 拖拽
  const dragging = useRef(false)
  const dragOffset = useRef({ x: 0, y: 0 })

  // 缩放
  const resizing = useRef(false)
  const resizeStart = useRef({ x: 0, y: 0, w: 0, h: 0 })

  const onHeaderMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'SELECT' || (e.target as HTMLElement).tagName === 'BUTTON') return
    dragging.current = true
    dragOffset.current = { x: e.clientX - pos.x, y: e.clientY - pos.y }
    e.preventDefault()
  }, [pos])

  const onResizeMouseDown = useCallback((e: React.MouseEvent) => {
    resizing.current = true
    resizeStart.current = { x: e.clientX, y: e.clientY, w: size.w, h: size.h }
    e.preventDefault()
    e.stopPropagation()
  }, [size])

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (dragging.current) {
        setPos({
          x: Math.max(0, Math.min(e.clientX - dragOffset.current.x, window.innerWidth - 80)),
          y: Math.max(0, Math.min(e.clientY - dragOffset.current.y, window.innerHeight - 40)),
        })
      }
      if (resizing.current) {
        setSize({
          w: Math.max(MIN_W, resizeStart.current.w + (e.clientX - resizeStart.current.x)),
          h: Math.max(MIN_H, resizeStart.current.h + (e.clientY - resizeStart.current.y)),
        })
      }
    }
    const onUp = () => {
      dragging.current = false
      resizing.current = false
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [])

  // 键盘转发：游戏面板打开时，把方向键/WASD/空格/R/ESC 通过 postMessage 转发到 iframe
  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => {
      // 焦点在输入框时不拦截
      const tag = (e.target as HTMLElement)?.tagName
      if (tag === 'TEXTAREA' || tag === 'INPUT' || tag === 'SELECT') return
      if (!FORWARD_KEYS.has(e.key)) return
      const iframe = iframeRef.current
      if (!iframe?.contentWindow) return
      // 用 postMessage 转发（比 parent.addEventListener 更可靠）
      iframe.contentWindow.postMessage({ type: 'key', key: e.key }, '*')
      e.preventDefault()
    }
    window.addEventListener('keydown', handler, true)
    return () => window.removeEventListener('keydown', handler, true)
  }, [open])

  const running = sess.phase === 'running' || sess.phase === 'creating'

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        title={t('games.launch')}
        className={`fixed bottom-4 right-4 z-50 flex h-11 w-11 items-center justify-center rounded-full border border-line bg-panel text-xl shadow-xl hoverable ${
          running ? 'animate-pulse' : ''
        }`}
      >
        🎮
      </button>
    )
  }

  return (
    <div
      ref={panelRef}
      className="fixed z-50 flex flex-col overflow-hidden rounded-xl border border-strong bg-panel shadow-2xl"
      style={{ left: pos.x, top: pos.y, width: size.w, height: size.h }}
    >
      {/* 拖拽标题栏 */}
      <div
        onMouseDown={onHeaderMouseDown}
        className="flex h-9 shrink-0 cursor-move items-center gap-2 border-b border-line px-2 select-none"
      >
        <span className="text-xs font-medium text-faint">🎮 {t('games.title')}</span>
        <select
          value={game}
          onChange={(e) => setGame(e.target.value)}
          className="min-w-0 flex-1 rounded-md border border-line bg-field px-1.5 py-0.5 text-xs text-muted outline-none"
        >
          {GAMES.map((g) => (
            <option key={g.id} value={g.id}>
              {g.label}
            </option>
          ))}
        </select>
        <button
          onClick={() => setNonce((n) => n + 1)}
          title={t('games.restart')}
          className="rounded px-1.5 text-sm text-muted hoverable"
        >
          ↻
        </button>
        <button onClick={() => setOpen(false)} title={t('games.close')} className="rounded px-1.5 text-sm text-muted hoverable">
          ✕
        </button>
      </div>

      {/* 游戏区域 */}
      <iframe
        ref={iframeRef}
        key={game + ':' + nonce}
        src={`/debug/game.html?g=${encodeURIComponent(game)}&_v=${nonce}`}
        title={t('games.title')}
        className="min-h-0 w-full flex-1 border-0 bg-[#050810]"
      />

      {/* 右下角缩放手柄 */}
      <div
        onMouseDown={onResizeMouseDown}
        className="absolute bottom-0 right-0 z-10 flex h-4 w-4 cursor-nwse-resize items-center justify-center text-slate-600"
        style={{ userSelect: 'none' }}
      >
        <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor">
          <path d="M7 0L1 6h6V0z" opacity="0.5" />
        </svg>
      </div>
    </div>
  )
}

export const gamesPlugin: PluginManifest = {
  id: 'modforge-games',
  name: '小游戏',
  apply(ctx: PluginContext): void {
    ctx.slots.inject(SLOTS.overlay, 'games', () => <GameWindow />)
  },
}

import { useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { useT } from '../lib/i18n'
import { useSession } from '../lib/session'

// 主页小游戏浮窗：等待 agent 生成时挂一个游戏窗口（iframe 挂 /debug/game.html）
// 游戏本体复用 debug 维护页的 7 个游戏，零重复实现。

const GAMES = [
  { id: 'snake-2048', label: '🐍 Snake 2048' },
  { id: 'server-defense', label: '🛡️ Server Defense' },
  { id: 'traffic-breakout', label: '🧱 Traffic Breakout' },
  { id: 'dimension-parkour', label: '🏃 Dimension Parkour' },
  { id: 'bug-sorter', label: '🎵 Bug Sorter' },
  { id: 'terminal-hacker', label: '💻 Terminal Hacker' },
  { id: 'data-turing', label: '🔌 Data Turing' },
]

function GameWindow() {
  const t = useT()
  const sess = useSession()
  const [open, setOpen] = useState(false)
  const [game, setGame] = useState('snake-2048')
  const [nonce, setNonce] = useState(0)
  const running = sess.phase === 'running' || sess.phase === 'creating'

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          title={t('games.launch')}
          className={`fixed bottom-4 right-4 z-50 flex h-11 w-11 items-center justify-center rounded-full border border-line bg-panel text-xl shadow-xl hoverable ${
            running ? 'animate-pulse' : ''
          }`}
        >
          🎮
        </button>
      )}
      {open && (
        <div className="fixed bottom-4 right-4 z-50 flex h-[min(600px,78vh)] w-[min(540px,calc(100vw-2rem))] flex-col overflow-hidden rounded-xl border border-strong bg-panel shadow-2xl">
          <div className="flex h-9 shrink-0 items-center gap-2 border-b border-line px-2">
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
          <iframe
            key={game + ':' + nonce}
            src={`/debug/game.html?g=${encodeURIComponent(game)}`}
            title={t('games.title')}
            className="min-h-0 w-full flex-1 border-0 bg-[#050810]"
          />
        </div>
      )}
    </>
  )
}

export const gamesPlugin: PluginManifest = {
  id: 'modforge-games',
  name: '小游戏',
  apply(ctx) {
    ctx.slots.inject(SLOTS.overlay, 'games', () => <GameWindow />)
  },
}

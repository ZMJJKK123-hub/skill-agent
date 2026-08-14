import { useEffect } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { setUi, useUi } from '../lib/store'
import { useT } from '../lib/i18n'
import { useSession, loadHistory, openHistorySession, newConversation } from '../lib/session'
import { deleteSession } from '../lib/api'

export const sidebarPlugin: PluginManifest = {
  id: 'modforge-sidebar',
  name: '侧栏',
  apply(ctx) {
    // 顶栏 logo（占位）
    ctx.slots.inject(SLOTS.sidebarLogo, 'logo', (props: any) => (
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded bg-forge-500 text-sm font-bold text-ink-950">
          M
        </div>
        {!props?.collapsed && <span className="truncate font-semibold">MOD Forge</span>}
      </div>
    ))

    ctx.slots.inject(SLOTS.sidebarWorkspaces, 'workspaces', (props: any) => {
      const { activeWorkspace } = useUi()
      const { title } = useSession()
      const t = useT()
      const label = title ?? t('nav.newChat')
      return (
        <div className="px-2 py-3">
          <div className="mb-2 px-1 text-xs text-faint">
            {!props?.collapsed && <span>{t('nav.workspace')}</span>}
          </div>
          {!props?.collapsed && (
            <div className="space-y-1">
              <button
                onClick={() => {
                  newConversation()
                  setUi({ activeWorkspace: null })
                }}
                title={t('nav.newChat')}
                className={`block w-full truncate rounded px-2 py-1.5 text-left text-sm ${
                  activeWorkspace === null ? 'bg-subtle text-main' : 'text-muted hoverable'
                }`}
              >
                💬 {label}
              </button>
            </div>
          )}
        </div>
      )
    })

    ctx.slots.inject(SLOTS.sidebarSessions, 'sessions', (props: any) => {
      const { history } = useSession()
      const { user } = useUi()
      const t = useT()
      useEffect(() => {
        if (user) void loadHistory()
      }, [user])

      if (props?.collapsed) return <div className="px-2 py-3" />

      const remove = async (id: string) => {
        try {
          await deleteSession(id)
          await loadHistory()
        } catch {
          await loadHistory()
        }
      }

      return (
        <div className="px-2 py-3">
          <div className="mb-2 px-1 text-xs text-faint">{t('nav.sessions')}</div>
          {!user ? (
            <div className="px-2 text-xs text-faint">{t('nav.loginToSee')}</div>
          ) : history.length === 0 ? (
            <div className="px-2 text-xs text-faint">{t('nav.noSessions')}</div>
          ) : (
            <div className="space-y-1">
              {history.map((h) => (
                <div key={h.sessionId} className="group flex items-center gap-1">
                  <button
                    onClick={() => {
                      openHistorySession(h.sessionId)
                      setUi({ activeWorkspace: h.sessionId })
                    }}
                    className="flex-1 overflow-hidden rounded px-2 py-1.5 text-left text-sm text-muted hoverable"
                  >
                    <div className="truncate">{h.sessionId}</div>
                    <div className="flex items-center gap-1 text-[10px] text-faint">
                      <span>{h.date}</span>
                      {h.has_jar && <span className="text-forge-400">· jar ✓</span>}
                    </div>
                  </button>
                  <button
                    onClick={() => remove(h.sessionId)}
                    title="删除会话"
                    className="rounded px-1 text-xs text-faint opacity-0 hoverable group-hover:opacity-100"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )
    })
  },
}

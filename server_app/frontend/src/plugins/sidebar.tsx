import { useEffect, useState } from 'react'
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
        {!props?.collapsed && (
          <span className="truncate font-semibold">
            MOD Forge
            <span
              title="V0.1.0 预览版"
              className="ml-1.5 inline-block translate-y-[-1px] rounded border border-forge-500/50 bg-forge-500/10 px-1 py-px align-middle text-[9px] font-medium tracking-wide text-forge-300"
            >
              V0.1.0 预览版
            </span>
          </span>
        )}
      </div>
    ))

    ctx.slots.inject(SLOTS.sidebarWorkspaces, 'workspaces', (props: any) => {
      const { activeWorkspace } = useUi()
      const t = useT()
      // 固定显示"新对话"（不跟随当前会话 title）
      const label = t('nav.newChat')
      return (
        <div className="px-2 py-3">
          {/* 不再显示"工作区"分组标题：下面只有一个新对话按钮，
              分组名名不副实还占一行 */}
          {!props?.collapsed && (
            <div className="space-y-1">
              <button
                onClick={() => {
                  newConversation()
                  setUi({ activeWorkspace: null, toast: t('toast.newChat') })
                }}
                title={t('nav.newChat')}
                className={`block w-full truncate rounded px-2 py-1.5 text-center text-sm ${
                  activeWorkspace === null ? 'bg-subtle text-main' : 'text-muted hoverable'
                }`}
              >
                {label}
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
      const sess = useSession()
      // 应用内两步删除确认：原生 window.confirm 在禁弹窗/自动化环境下会被吞掉，
      // 删除操作静默失效（实测缺陷）。改为行内"确认删除"二次点击。
      const [confirmId, setConfirmId] = useState<string | null>(null)
      useEffect(() => {
        if (user) void loadHistory()
      }, [user])

      if (props?.collapsed) return <div className="px-2 py-3" />

      const remove = async (id: string) => {
        try {
          await deleteSession(id)
        } catch {
          /* 后端失败也刷新列表，保持与磁盘一致 */
        }
        // 删除的是当前正在查看的会话 → 回到空态。此前视图仍停留在
        // 已删除会话上，此时发消息必报 "Session not found"（实测缺陷）
        if (sess.sessionId === id) {
          await newConversation()
        }
        setConfirmId(null)
        await loadHistory()
      }

      // 侧栏标题：服务端在首条消息落盘前会回退到裸 ID 前缀（实测缺陷），
      // 当前会话用本地乐观标题覆盖；server 标题正常时以 server 为准。
      // 未取名（裸 ID/空）一律显示「新对话」占位，不用 ID 代替名称。
      const displayTitle = (h: { sessionId: string; title?: string }) => {
        const local = h.sessionId === sess.sessionId ? sess.title : null
        const serverRaw = !h.title || h.title === h.sessionId.slice(0, 8)
        if (local && serverRaw) return local
        return h.title && !serverRaw ? h.title : t('nav.newChat')
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
                    <div className="truncate">{displayTitle(h)}</div>
                    <div className="flex items-center gap-1 text-[10px] text-faint">
                      <span>{h.date}</span>
                      {h.has_jar && <span className="text-forge-400">· jar ✓</span>}
                    </div>
                  </button>
                  {confirmId === h.sessionId ? (
                    <button
                      onClick={() => remove(h.sessionId)}
                      title="再次点击确认删除"
                      className="rounded border border-red-500/50 px-1.5 py-0.5 text-[10px] text-red-400 hover:bg-red-500/10"
                    >
                      确认删除?
                    </button>
                  ) : (
                    <button
                      onClick={() => setConfirmId(h.sessionId)}
                      title="删除会话"
                      className="rounded px-1 text-xs text-faint opacity-0 hoverable group-hover:opacity-100"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )
    })
  },
}

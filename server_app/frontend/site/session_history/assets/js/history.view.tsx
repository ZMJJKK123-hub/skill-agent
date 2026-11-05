// 本分区样式仅在当前分区模块加载时挂载。
import '../css/session_history.css'
// React hooks 用于组件状态、订阅和生命周期。
import { useEffect } from 'react'
// 类型契约约束分区间的数据和组件通信。
import type { PluginManifest, PluginContext, SlotProps } from '../../../assets/js/slots.types.ts'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useUiActions, useUi, useSession, useSessionActions } from '../../../assets/js/application-context.tsx'
// 翻译 hook 为本分区提供当前语言文案。
import { useT } from '../../../assets/js/i18n.ts'
// 侧栏与其他分区使用相同的描边图标。
import { Icon } from '../../../assets/js/icons.tsx'

export const sidebarPlugin: PluginManifest = {
  id: 'modforge-sidebar',
  name: '侧栏',
  apply(ctx: PluginContext): void {
    // 顶栏 logo（占位）
    ctx.slots.inject(SLOTS.sidebarLogo, 'logo', (props: SlotProps) => (
      <div className="studio-brand">
        <div className="studio-mark">
          <Icon name="cube" size={24} />
        </div>
        {!props?.collapsed && <div><span className="studio-brand-name">MOD Forge<span className="brand-period">.</span></span><span className="studio-brand-caption">CREATIVE STUDIO</span></div>}
      </div>
    ))

    ctx.slots.inject(SLOTS.sidebarWorkspaces, 'workspaces', (props: SlotProps) => {
      const { setUi } = useUiActions()
      const { newConversation } = useSessionActions()
      const t = useT()
      // 固定显示"新对话"（不跟随当前会话 title）
      const label = t('nav.newChat')
      return (
        <div className="workspace-section" data-collapsed={props?.collapsed}>
          {!props?.collapsed && <div className="sidebar-section-label">{t('nav.workspace')}</div>}
            <div>
              <button
                onClick={() => {
                  newConversation()
                  setUi({ activeWorkspace: null, promptDraft: '', toast: t('toast.newChat') })
                }}
                title={t('nav.newChat')}
                aria-label={label}
                className="new-conversation-button"
              >
                <Icon name="plus" size={18} />{!props?.collapsed && <><span>{label}</span><span className="new-conversation-hint"><Icon name="chat" size={14} /></span></>}
              </button>
            </div>
        </div>
      )
    })

    ctx.slots.inject(SLOTS.sidebarSessions, 'sessions', (props: SlotProps) => {
      const { setUi } = useUiActions()
      const { loadHistory, openHistorySession, deleteSession } = useSessionActions()
      const { history, sessionId } = useSession()
      const { user } = useUi()
      const t = useT()
      useEffect(() => {
        if (user) void loadHistory()
      }, [user, loadHistory])

      if (props?.collapsed) return <div className="px-2 py-3" />

      const remove = async (id: string) => {
        // 删除不可恢复，先弹确认
        const ok = window.confirm('确定删除该会话吗？删除后无法恢复。')
        if (!ok) return
        await deleteSession(id)
      }

      return (
        <div className="history-section">
          <div className="sidebar-section-label">{t('nav.sessions')}<span>{user ? history.length : '—'}</span></div>
          {!user ? (
            <div className="history-empty"><Icon name="clock" size={20} /><p>{t('nav.loginToSee')}</p><span>{t('studio.historyEmpty')}</span></div>
          ) : history.length === 0 ? (
            <div className="history-empty"><Icon name="chat" size={20} /><p>{t('nav.noSessions')}</p><span>{t('studio.historyEmpty')}</span></div>
          ) : (
            <div className="space-y-1">
              {history.map((h) => (
                <div key={h.sessionId} className={`history-row group flex items-center gap-1 ${sessionId === h.sessionId ? 'is-active' : ''}`}>
                  <button
                    onClick={() => {
                      openHistorySession(h.sessionId)
                      setUi({ activeWorkspace: h.sessionId })
                    }}
                    className="history-item flex-1 overflow-hidden text-left text-sm text-muted"
                    aria-current={sessionId === h.sessionId ? 'page' : undefined}
                  >
                    <div className="history-item-title"><Icon name="chat" size={14} /><span className="truncate">{h.title || h.sessionId.slice(0, 8)}</span></div>
                    <div className="flex items-center gap-1 text-[10px] text-faint">
                      <span>{h.date}</span>
                      {h.has_jar && <span className="text-forge-400">· jar ✓</span>}
                    </div>
                  </button>
                  <button
                    onClick={() => remove(h.sessionId)}
                    title="删除会话"
                    className="history-delete icon-button text-faint opacity-0 group-hover:opacity-100 focus:opacity-100"
                  >
                    <Icon name="close" size={13} />
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="sidebar-creative-note"><Icon name="sparkles" size={19} /><strong>{t('studio.privateSpace')}</strong><p>{t('studio.spaceHint')}</p><div className="note-grid" aria-hidden="true" /></div>
        </div>
      )
    })
  },
}

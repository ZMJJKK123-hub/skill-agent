// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// React hooks 用于组件状态、订阅和生命周期。
import { useEffect, useState } from 'react'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { SlotView } from '../../../assets/js/slot-view.tsx'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useApplication, useUiActions, useUi, useSession } from '../../../assets/js/application-context.tsx'
// 共享图标替换壳层字符按钮，保持控件命名与图形独立。
import { Icon } from '../../../assets/js/icons.tsx'
// 壳层标题和状态跟随现有语言偏好。
import { useT } from '../../../assets/js/i18n.ts'
// 本分区样式仅在当前分区模块加载时挂载。
import '../css/index.css'

// 轻量 toast：全局顶部提示，2 秒自动消失（跨插件反馈用）
/** 监听通知状态并在配置时间后清除；无通知返回 null，卸载清理定时器。
 * Args: 无参数；读取当前通知和注入的超时配置。
 * Returns: React 展示元素；空数据或关闭态返回 null。
 * Globals Used: 当前应用 Context；window 定时器。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function Toast(): ReactElement | null {
  const { setUi } = useUiActions()
  const { config } = useApplication()
  const { toast } = useUi()
  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setUi({ toast: null }), config.toastDurationMs)
    return () => window.clearTimeout(timer)
  }, [toast, config.toastDurationMs, setUi])
  if (!toast) return null
  return (
    <div role="status" className="app-toast pointer-events-none fixed left-1/2 top-20 z-[60] -translate-x-1/2 rounded-xl border border-strong bg-panel px-4 py-3 text-sm shadow-xl">
      <Icon name="check" size={16} />
      {toast}
    </div>
  )
}

// 三栏壳层：侧栏 / 对话 / 详情 都是可关组件。
// 关闭某个组件时，那一整栏（连同分界线）消失，相邻栏自动拉伸填满。
/** 渲染侧栏、对话、详情与浮层；分区关闭时隐藏整栏，状态来自注入服务。
 * Args: 无参数；读取插件开关，栏位宽度与详情显隐由本组件维护。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context；window.matchMedia 初始化侧栏宽度。Calls/Dependencies: React hooks、SlotView、Icon、翻译器。
 */
export function AppShell(): ReactElement {
  const [sidebarWide, setSidebarWide] = useState((): boolean => window.matchMedia('(min-width: 900px)').matches)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const { disabledPlugins, version } = useUi()
  const session = useSession()
  const t = useT()

  const off = new Set(disabledPlugins)
  const sidebarOn = !off.has('modforge-sidebar')
  const conversationOn = !off.has('modforge-conversation')
  const detailsAvailable = !off.has('modforge-generate')

  const collapsed = !sidebarWide

  return (
    <div className="app-shell flex h-full bg-app text-main">
      {/* 左侧可伸缩栏（侧栏插件开启才渲染） */}
      {sidebarOn && (
        <aside
          data-collapsed={collapsed}
          className="app-sidebar flex shrink-0 flex-col border-r border-line"
        >
          <div className="sidebar-brand flex items-center">
            <SlotView name={SLOTS.sidebarLogo} props={{ collapsed }} />
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            <SlotView name={SLOTS.sidebarWorkspaces} props={{ collapsed }} />
            <SlotView name={SLOTS.sidebarSessions} props={{ collapsed }} />
          </div>
          <div className="sidebar-footer border-t border-line">
            <SlotView name={SLOTS.sidebarFooter} props={{ collapsed }} />
          </div>
        </aside>
      )}
      {sidebarOn && sidebarWide && <button className="sidebar-backdrop" aria-label={t('studio.close')} onClick={() => setSidebarWide(false)} />}

      {/* 中间对话区 */}
      <main className="app-main flex min-w-0 flex-1 flex-col">
        <header className="app-header flex items-center gap-2 border-b border-line">
          {sidebarOn && (
            <button
              onClick={() => setSidebarWide((v) => !v)}
              title="折叠/展开侧栏"
              aria-label="折叠/展开侧栏"
              aria-expanded={sidebarWide}
              className="icon-button"
            >
              <Icon name="sidebar" />
            </button>
          )}
          <div className="header-breadcrumb"><span>{t('studio.workspace')}</span><span className="breadcrumb-divider">/</span><span className="header-title">{session.title ?? t('studio.newIdea')}</span></div>
          <div className="flex-1" />
          <span className="version-chip"><span className="status-dot" />Minecraft {version}</span>
          {detailsAvailable && <button onClick={() => setDetailsOpen((value) => !value)} title={t('studio.sessionDetails')} aria-label={t('studio.sessionDetails')} aria-pressed={detailsOpen} className="icon-button"><Icon name="details" /></button>}
          <div className="header-separator" />
          <SlotView name={SLOTS.headerActions} />
        </header>

        {conversationOn && (
          <>
            <div className="conversation-scroll min-h-0 flex-1 overflow-y-auto">
              <SlotView name={SLOTS.conversationMessages} />
            </div>
            <div className="composer-dock">
              <SlotView name={SLOTS.conversationComposer} />
            </div>
          </>
        )}
      </main>

      {/* 右侧详情面板（详情插件开启 + 手动展开才渲染） */}
      {detailsOpen && detailsAvailable && (
        <aside className="details-panel shrink-0 overflow-y-auto border-l border-line">
          <div className="details-panel-heading"><span>{t('studio.sessionDetails')}</span><button className="icon-button" aria-label={t('studio.close')} onClick={() => setDetailsOpen(false)}><Icon name="close" size={16} /></button></div>
          <SlotView name={SLOTS.details} />
        </aside>
      )}

      {/* 全局浮层（设置面板 / 弹窗） */}
      <SlotView name={SLOTS.overlay} />
      <Toast />
    </div>
  )
}

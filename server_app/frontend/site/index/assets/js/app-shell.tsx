// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// React hooks 用于组件状态、订阅和生命周期。
import { useEffect, useState } from 'react'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { SlotView } from '../../../assets/js/slot-view.tsx'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useApplication, useUiActions, useUi } from '../../../assets/js/application-context.tsx'
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
    <div className="pointer-events-none fixed left-1/2 top-16 z-[60] -translate-x-1/2 rounded-lg border border-strong bg-panel px-4 py-2 text-sm shadow-xl">
      {toast}
    </div>
  )
}

// 三栏壳层：侧栏 / 对话 / 详情 都是可关组件。
// 关闭某个组件时，那一整栏（连同分界线）消失，相邻栏自动拉伸填满。
/** 渲染侧栏、对话、详情与浮层；分区关闭时隐藏整栏，状态来自注入服务。
 * Args: 无参数；读取插件开关，栏位宽度与详情显隐由本组件维护。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
export function AppShell(): ReactElement {
  const [sidebarWide, setSidebarWide] = useState(true)
  const [detailsOpen, setDetailsOpen] = useState(false)
  const { disabledPlugins } = useUi()

  const off = new Set(disabledPlugins)
  const sidebarOn = !off.has('modforge-sidebar')
  const conversationOn = !off.has('modforge-conversation')
  const detailsAvailable = !off.has('modforge-generate')

  const collapsed = !sidebarWide

  return (
    <div className="flex h-full bg-app text-main">
      {/* 左侧可伸缩栏（侧栏插件开启才渲染） */}
      {sidebarOn && (
        <aside
          className={`${
            sidebarWide ? 'w-64' : 'w-14'
          } flex shrink-0 flex-col border-r border-line transition-all duration-200`}
        >
          <div className="flex h-12 items-center gap-2 border-b border-line px-2">
            <SlotView name={SLOTS.sidebarLogo} props={{ collapsed }} />
          </div>
          <div className="flex-1 overflow-y-auto">
            <SlotView name={SLOTS.sidebarWorkspaces} props={{ collapsed }} />
            <SlotView name={SLOTS.sidebarSessions} props={{ collapsed }} />
          </div>
          <div className="border-t border-line p-1.5">
            <SlotView name={SLOTS.sidebarFooter} props={{ collapsed }} />
          </div>
        </aside>
      )}

      {/* 中间对话区 */}
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 items-center gap-1 border-b border-line px-2">
          {sidebarOn && (
            <button
              onClick={() => setSidebarWide((v) => !v)}
              title="折叠/展开侧栏"
              className="hoverable rounded-md px-2 py-1 text-muted"
            >
              ☰
            </button>
          )}
          {detailsAvailable && (
            <button
              onClick={() => setDetailsOpen((v) => !v)}
              title="详情面板"
              className="hoverable rounded-md px-2 py-1 text-muted"
            >
              {detailsOpen ? '»' : '«'}
            </button>
          )}
          <div className="flex-1" />
          <SlotView name={SLOTS.headerActions} />
        </header>

        {conversationOn && (
          <>
            <div className="flex-1 overflow-y-auto">
              <SlotView name={SLOTS.conversationMessages} />
            </div>
            <div className="border-t border-line p-3">
              <SlotView name={SLOTS.conversationComposer} />
            </div>
          </>
        )}
      </main>

      {/* 右侧详情面板（详情插件开启 + 手动展开才渲染） */}
      {detailsOpen && detailsAvailable && (
        <aside className="w-80 shrink-0 overflow-y-auto border-l border-line">
          <SlotView name={SLOTS.details} />
        </aside>
      )}

      {/* 全局浮层（设置面板 / 弹窗） */}
      <SlotView name={SLOTS.overlay} />
      <Toast />
    </div>
  )
}

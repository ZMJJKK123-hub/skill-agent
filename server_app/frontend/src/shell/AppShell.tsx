import { useEffect, useState } from 'react'
import { SLOTS, SlotView } from './registry'
import { setUi, useUi } from '../lib/store'

// 轻量 toast：全局顶部提示，2 秒自动消失（跨插件反馈用）
function Toast() {
  const { toast } = useUi()
  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setUi({ toast: null }), 2000)
    return () => window.clearTimeout(timer)
  }, [toast])
  if (!toast) return null
  return (
    <div className="pointer-events-none fixed left-1/2 top-16 z-[60] -translate-x-1/2 rounded-lg border border-strong bg-panel px-4 py-2 text-sm shadow-xl">
      {toast}
    </div>
  )
}

// 三栏壳层：侧栏 / 对话 / 详情 都是可关组件。
// 关闭某个组件时，那一整栏（连同分界线）消失，相邻栏自动拉伸填满。
export function AppShell() {
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

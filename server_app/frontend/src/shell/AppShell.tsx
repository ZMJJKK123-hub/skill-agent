import { useState } from 'react'
import { SLOTS, SlotView } from './registry'
import { setUi } from '../lib/store'

// 三栏可伸缩壳层（仿 dsh 布局）：
//   左：可伸缩快捷栏（256px ↔ 56px rail）· 中：对话 · 右：详情面板（可开关）
export function AppShell() {
  const [sidebarWide, setSidebarWide] = useState(true)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const collapsed = !sidebarWide

  return (
    <div className="flex h-full bg-app text-main">
      {/* 左侧可伸缩栏 */}
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

      {/* 中间对话区 */}
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 items-center gap-1 border-b border-line px-2">
          <button
            onClick={() => setSidebarWide((v) => !v)}
            title="折叠/展开侧栏"
            className="hoverable rounded-md px-2 py-1 text-muted"
          >
            ☰
          </button>
          <button
            onClick={() => setDetailsOpen((v) => !v)}
            title="详情面板"
            className="hoverable rounded-md px-2 py-1 text-muted"
          >
            {detailsOpen ? '»' : '«'}
          </button>
          <div className="flex-1" />
          <SlotView name={SLOTS.headerActions} />
          <button
            onClick={() => setUi({ settingsOpen: true })}
            title="设置"
            className="hoverable ml-1 rounded-md px-2 py-1 text-muted"
          >
            ⚙️
          </button>
        </header>

        <div className="flex-1 overflow-y-auto">
          <SlotView name={SLOTS.conversationMessages} />
        </div>

        <div className="border-t border-line p-3">
          <SlotView name={SLOTS.conversationComposer} />
        </div>
      </main>

      {/* 右侧详情面板 */}
      {detailsOpen && (
        <aside className="w-80 shrink-0 overflow-y-auto border-l border-line">
          <SlotView name={SLOTS.details} />
        </aside>
      )}

      {/* 全局浮层（设置面板 / 弹窗 / 导入对话框） */}
      <SlotView name={SLOTS.overlay} />
    </div>
  )
}

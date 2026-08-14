import { type ReactNode } from 'react'
import { useUi } from '../lib/store'

// ── 迷你槽位系统（仿 dsh 的 client Slot）────────────────────────
// 静态插件化：main.tsx 启动时按 composition 顺序 apply 所有插件，
// 插件通过 ctx.slots.register() 把 UI 注册进命名槽位；壳层用 SlotView 渲染。
// 支持运行时开关：每个槽位条目记录 pluginId，disabledPlugins 里的插件被过滤掉。

export type SlotRender = (props?: Record<string, unknown>) => ReactNode

interface SlotEntry {
  id: string
  pluginId: string
  render: SlotRender
  order: number
}

class SlotRegistry {
  currentPluginId: string | null = null
  private slots = new Map<string, SlotEntry[]>()

  register(slot: string, id: string, render: SlotRender, order = 0): () => void {
    const arr = this.slots.get(slot) ?? []
    arr.push({ id, pluginId: this.currentPluginId ?? 'unknown', render, order })
    this.slots.set(slot, arr)
    return () => this.slots.set(slot, arr.filter((e) => e.id !== id))
  }

  inject(slot: string, id: string, render: SlotRender, order = 0): () => void {
    return this.register(slot, id, render, order)
  }

  entries(slot: string): SlotEntry[] {
    return (this.slots.get(slot) ?? []).slice().sort((a, b) => a.order - b.order)
  }
}

export const registry = new SlotRegistry()

export interface PluginContext {
  slots: SlotRegistry
}

export interface PluginManifest {
  id: string
  name: string
  apply(ctx: PluginContext): void | (() => void)
}

// 槽位名常量（集中声明，避免插件里手写字符串出错）
export const SLOTS = {
  sidebarLogo: 'sidebar.logo',
  sidebarWorkspaces: 'sidebar.workspaces',
  sidebarSessions: 'sidebar.sessions',
  sidebarFooter: 'sidebar.footer',
  headerActions: 'header.actions',
  conversationMessages: 'conversation.messages',
  conversationComposer: 'conversation.composer',
  details: 'details',
  overlay: 'shell.overlay',
} as const

export function SlotView({
  name,
  props,
}: {
  name: string
  props?: Record<string, unknown>
}) {
  const { disabledPlugins } = useUi()
  const disabled = new Set(disabledPlugins)
  return (
    <>
      {registry
        .entries(name)
        .filter((e) => !disabled.has(e.pluginId) || e.pluginId === 'modforge-settings')
        .map((e) => {
          // 每个槽位渲染函数作为独立 React 组件调用，保证内部 hooks 有独立 fiber
          const Comp = e.render as any
          return <Comp key={e.id} {...(props ?? {})} />
        })}
    </>
  )
}

// 槽位渲染契约允许业务分区注册自己的 React 组件。
import type { ComponentType } from 'react'
export interface SlotProps { collapsed?: boolean }
export type SlotName = 'sidebar.logo' | 'sidebar.workspaces' | 'sidebar.sessions' | 'sidebar.footer'
  | 'header.actions' | 'conversation.messages' | 'conversation.composer' | 'details' | 'shell.overlay'
export interface SlotEntry { id: string; pluginId: string; render: ComponentType<SlotProps>; order: number }
export interface SlotWriter {
  inject(slot: SlotName, id: string, render: ComponentType<SlotProps>, order?: number): () => void
}
export interface SlotRegistryPort {
  scope(pluginId: string): SlotWriter
  entries(slot: SlotName): SlotEntry[]
}
export interface PluginContext { slots: SlotWriter }
export interface PluginManifest { id: string; name: string; apply(context: PluginContext): void | (() => void) }

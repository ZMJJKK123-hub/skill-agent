// 注册表只存组件描述，不调用 React hooks 或导入业务分区。
import type { SlotEntry, SlotName, SlotRegistryPort, SlotWriter } from './slots.types.ts'
// 重复注册显式失败，避免界面重复挂载而静默覆盖。
import { FrontendError } from './errors.ts'

/** 已有槽位名集中声明；命名与旧版保持一致。 */
export const SLOTS = {
  sidebarLogo: 'sidebar.logo', sidebarWorkspaces: 'sidebar.workspaces', sidebarSessions: 'sidebar.sessions',
  sidebarFooter: 'sidebar.footer', headerActions: 'header.actions', conversationMessages: 'conversation.messages',
  conversationComposer: 'conversation.composer', details: 'details', overlay: 'shell.overlay',
} as const

/** 创建独立注册表。
 * scope 将注册动作绑定到固定 pluginId，消除原 currentPluginId 隐藏全局状态。
 * entries 返回排序后的副本；注销只删除自己的项。Globals Used: None。Dependencies: Map。
 */
export function createSlotRegistry(): SlotRegistryPort {
  const slots = new Map<SlotName, SlotEntry[]>()
  return {
    scope(pluginId: string): SlotWriter {
      return {
        inject(slot, id, render, order = 0): () => void {
          const entries = slots.get(slot) ?? []
          if (entries.some((entry: SlotEntry): boolean => entry.id === id && entry.pluginId === pluginId)) throw new FrontendError('DuplicateSlot', '分区重复注册')
          slots.set(slot, [...entries, { id, pluginId, render, order }])
          return (): void => { slots.set(slot, (slots.get(slot) ?? []).filter((entry: SlotEntry): boolean => entry.id !== id || entry.pluginId !== pluginId)) }
        },
      }
    },
    entries(slot: SlotName): SlotEntry[] { return [...(slots.get(slot) ?? [])].sort((a: SlotEntry, b: SlotEntry): number => a.order - b.order) },
  }
}

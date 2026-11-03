// 类型契约约束分区间的数据和组件通信。
import type { PluginManifest } from '../../../assets/js/slots.types.ts'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { sidebarPlugin } from '../../../session_history/assets/js/history.view.tsx'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { authPlugin } from '../../../user_auth/assets/js/auth.view.tsx'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { conversationPlugin } from '../../../conversation/assets/js/conversation.view.tsx'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { settingsPlugin } from '../../../settings/assets/js/settings.view.tsx'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { generatePlugin } from '../../../generation/assets/js/generation.view.tsx'
// 装配已实现的功能分区，业务逻辑留在分区内部。
import { gamesPlugin } from '../../../games/assets/js/games.view.tsx'

// 组合配置（等价 dsh 的 cordis.yml）：声明启用哪些插件及装配顺序。
// 顺序即插件 apply 的顺序（先注册先渲染到槽位）。
export const composition: PluginManifest[] = [
  sidebarPlugin,
  conversationPlugin,
  authPlugin,
  settingsPlugin,
  generatePlugin,
  gamesPlugin,
]

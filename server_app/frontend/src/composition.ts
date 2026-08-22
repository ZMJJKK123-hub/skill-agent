import { PluginManifest } from './shell/registry'
import { sidebarPlugin } from './plugins/sidebar'
import { authPlugin } from './plugins/auth'
import { conversationPlugin } from './plugins/conversation'
import { settingsPlugin } from './plugins/settings'
import { workspacePlugin } from './plugins/workspace'
import { generatePlugin } from './plugins/generate'
import { gamesPlugin } from './plugins/games'

// 组合配置（等价 dsh 的 cordis.yml）：声明启用哪些插件及装配顺序。
// 顺序即插件 apply 的顺序（先注册先渲染到槽位）。
export const composition: PluginManifest[] = [
  sidebarPlugin,
  conversationPlugin,
  authPlugin,
  settingsPlugin,
  workspacePlugin,
  generatePlugin,
  gamesPlugin,
]

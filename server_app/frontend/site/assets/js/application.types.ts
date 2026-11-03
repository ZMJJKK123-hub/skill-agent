// 应用边界只组合各分区接口，不在类型文件内实例化实现。
import type { UiStore } from '../../settings/assets/js/settings.types.ts'
// 会话状态和动作分别提供给视图。
import type { SessionController, SessionStore } from '../../conversation/assets/js/session.types.ts'
// 认证服务不暴露密码或令牌仓储给组件。
import type { AuthController } from '../../user_auth/assets/js/auth.types.ts'
// 公开配置、基础端口和槽位契约。
import type { FrontendConfig } from './config.ts'
// 浏览器依赖通过组合根注入。
import type { DownloadPort, Logger, StoragePort, ThemePort, TimerPort } from './contracts.ts'
// 槽位注册只在装配时使用。
import type { SlotRegistryPort } from './slots.types.ts'
export interface ApplicationServices {
  ui: UiStore
  sessionStore: SessionStore
  session: SessionController
  auth: AuthController
  slots: SlotRegistryPort
  config: FrontendConfig
  dispose(): void
}
export interface ApplicationDependencies {
  storage: StoragePort
  fetcher: typeof fetch
  timer: TimerPort
  theme: ThemePort
  downloads: DownloadPort
  logger: Logger
  config: FrontendConfig
}

// 所有基础设施与业务实例只在显式组装时创建。
import type { ApplicationDependencies, ApplicationServices } from './application.types.ts'
// 共享基础设施适配器。
import { createHttpClient } from './http-client.ts'
// 槽位注册表不依赖业务组件。
import { createSlotRegistry } from './slots.ts'
// 设置分区拥有持久化和状态初始化。
import { createSettingsRepository } from '../../settings/assets/js/settings.repository.ts'
// 设置状态通过仓储与主题接口组装。
import { createUiStore } from '../../settings/assets/js/settings.store.ts'
// 模型解析保持纯计算，当前配置在每次恢复任务时读取。
import { resolveModelConfig } from '../../settings/assets/js/settings.model.ts'
// 认证令牌与 HTTP 请求属于认证仓储。
import { createAuthRepository, createTokenStore } from '../../user_auth/assets/js/auth.repository.ts'
// 认证服务协调账户变化和会话清理。
import { createAuthService } from '../../user_auth/assets/js/auth.service.ts'
// 会话模块分别实现 HTTP、状态和业务编排。
import { createSessionRepository } from '../../conversation/assets/js/session.repository.ts'
// 每个应用实例拥有独立会话快照。
import { createSessionStore } from '../../conversation/assets/js/session.store.ts'
// 会话控制器不读取任何模块级全局实例。
import { createSessionService } from '../../conversation/assets/js/session.service.ts'

/** 应用组合根：创建设置→令牌/HTTP→会话→认证→槽位。
 * Args: 浏览器或测试提供的依赖。Returns: 可注入 React 的服务集合和清理入口。
 * 多次调用相互隔离；导入本文件无请求/轮询/存储副作用。Globals Used: None。
 */
export function createApplication(deps: ApplicationDependencies): ApplicationServices {
  const { config, logger } = deps
  const ui = createUiStore(createSettingsRepository(deps.storage, config.settingsStorageKey, logger), config, deps.theme)
  const tokens = createTokenStore(deps.storage, config.tokenStorageKey, logger)
  const http = createHttpClient(deps.fetcher, tokens.get, config, logger)
  const sessionStore = createSessionStore()
  const session = createSessionService({ repository: createSessionRepository(http, config), store: sessionStore,
    timer: deps.timer, downloads: deps.downloads, config, logger,
    getSettings: () => {
      const state = ui.getSnapshot()
      return { ...state, ...resolveModelConfig(state, config) }
    },
  })
  const auth = createAuthService(createAuthRepository(http, config), tokens, ui, session, logger)
  return { ui, sessionStore, session, auth, config, slots: createSlotRegistry(),
    dispose(): void { session.dispose(); deps.theme.dispose() },
  }
}

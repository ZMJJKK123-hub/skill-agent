// 认证生命周期只依赖接口，HTTP 与令牌持久化在仓储层实现。
import type { AuthController, AuthRepository, TokenStore } from './auth.types.ts'
// 用户显示状态与会话清理分别注入，退出时不能遗留前一账户消息。
import type { UiStore } from '../../../settings/assets/js/settings.types.ts'
// 控制器契约避免认证层依赖具体会话实现。
import type { SessionController } from '../../../conversation/assets/js/session.types.ts'
// 日志只记录操作与错误类型。
import type { Logger } from '../../../assets/js/contracts.ts'
// 401/403 是明确失效；网络异常保留本地令牌供下一次重试。
import { FrontendError, errorType } from '../../../assets/js/errors.ts'

/** 创建认证服务。
 * Args: repository/tokens/ui/session/logger 由组合根组装。Returns: 恢复/登录/注册/退出动作。
 * 登录失败向弹窗传播；恢复网络失败保留令牌；退出请求失败仍清理本地账户。
 * Globals Used: None。Dependencies: 注入的仓储和状态接口。
 */
export function createAuthService(repository: AuthRepository, tokens: TokenStore, ui: UiStore, session: Pick<SessionController, 'clearAccount'>, logger: Logger): AuthController {
  let revision = 0
  /** 成功认证后隔离旧账户请求，再发布新登录状态。 */
  async function authenticate(mode: 'login' | 'register', username: string, password: string): Promise<void> {
    const version = ++revision
    const result = await repository[mode](username.trim(), password)
    if (version !== revision) return
    session.clearAccount()
    tokens.set(result.token)
    ui.set({ user: { username: result.username }, activeWorkspace: null })
    logger.write('info', 'auth.authenticated', { operation: mode })
  }
  return {
    async restore(): Promise<void> {
      const token = tokens.get()
      const version = revision
      if (!token) return
      try {
        const user = await repository.me()
        if (version === revision && token === tokens.get()) ui.set({ user })
      } catch (error: unknown) {
        if (version !== revision || token !== tokens.get()) return
        if (error instanceof FrontendError && (error.status === 401 || error.status === 403)) {
          tokens.clear(); session.clearAccount(); ui.set({ user: null })
        } else { ui.set({ toast: '登录状态暂时无法核验，请稍后重试' }) }
        logger.write('warning', 'auth.restore_failed', { errorType: errorType(error) })
      }
    },
    login: (username: string, password: string): Promise<void> => authenticate('login', username, password),
    register: (username: string, password: string): Promise<void> => authenticate('register', username, password),
    async logout(): Promise<void> {
      const version = ++revision
      try { await repository.logout() }
      catch (error: unknown) { logger.write('warning', 'auth.logout_failed', { errorType: errorType(error) }) }
      finally { if (version === revision) { tokens.clear(); session.clearAccount(); ui.set({ user: null, activeWorkspace: null }) } }
    },
  }
}

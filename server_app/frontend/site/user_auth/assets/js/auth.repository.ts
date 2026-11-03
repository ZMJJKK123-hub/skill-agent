// HTTP/存储/日志是基础设施接口，不在仓储内创建浏览器服务。
import type { HttpClient, Logger, StoragePort } from '../../../assets/js/contracts.ts'
// 路由与存储键来自统一配置。
import type { FrontendConfig } from '../../../assets/js/config.ts'
// 认证 DTO 与适配器契约。
import type { AuthRepository, AuthResult, TokenStore, User } from './auth.types.ts'
// 只记录异常分类，令牌本身不得进入日志。
import { errorType } from '../../../assets/js/errors.ts'

/** 创建令牌仓储；浏览器存储受限时保持当前页内存登录态，刷新后需重新登录。
 * Args: storage/key/logger 显式注入。Returns: 读/写/撤销接口。Globals Used: None。
 */
export function createTokenStore(storage: StoragePort, key: string, logger: Logger): TokenStore {
  let memory: string | null = null
  let memoryOnly = false
  return {
    get(): string | null {
      if (memoryOnly) return memory
      try { return storage.getItem(key) }
      catch (error: unknown) { memoryOnly = true; logger.write('warning', 'auth.storage_read_failed', { errorType: errorType(error) }); return memory }
    },
    set(token: string): void {
      memory = token
      try { storage.setItem(key, token); memoryOnly = false }
      catch (error: unknown) { memoryOnly = true; logger.write('warning', 'auth.storage_write_failed', { errorType: errorType(error) }) }
    },
    clear(): void {
      memory = null
      try { storage.removeItem(key); memoryOnly = false }
      catch (error: unknown) { memoryOnly = true; logger.write('warning', 'auth.storage_clear_failed', { errorType: errorType(error) }) }
    },
  }
}

/** 适配既有认证路由与字段；HTTP 异常向服务层传播，无全局依赖。 */
export function createAuthRepository(http: HttpClient, config: FrontendConfig): AuthRepository {
  return {
    login: (username: string, password: string): Promise<AuthResult> => http.request(config.paths.login, { method: 'POST', body: JSON.stringify({ username, password }) }),
    register: (username: string, password: string): Promise<AuthResult> => http.request(config.paths.register, { method: 'POST', body: JSON.stringify({ username, password }) }),
    me: (): Promise<User> => http.request(config.paths.me),
    logout: (): Promise<void> => http.request(config.paths.logout, { method: 'POST' }),
  }
}

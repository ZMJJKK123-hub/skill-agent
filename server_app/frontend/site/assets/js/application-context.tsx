// React 上下文只连接服务接口和组件，不创建服务或发送请求。
import { createContext, useContext, useSyncExternalStore, type ReactElement, type ReactNode } from 'react'
// 服务类型与实现分离。
import type { ApplicationServices } from './application.types.ts'
// hooks 使用显式类型作为分区通信契约。
import type { UiState } from '../../settings/assets/js/settings.types.ts'
// 会话快照与控制器不绑定 React。
import type { SessionController, SessionState } from '../../conversation/assets/js/session.types.ts'
// 认证界面只消费控制器。
import type { AuthController } from '../../user_auth/assets/js/auth.types.ts'
// 缺少 Provider 是装配错误，显式抛出。
import { FrontendError } from './errors.ts'

/** Context 仅存注入实例，空值用于识别缺失装配。 */
const Context = createContext<ApplicationServices | null>(null)

/** 注入应用服务；组件树外调用 hooks 会抛 MissingApplication，无网络副作用。 */
export function ApplicationProvider({ services, children }: { services: ApplicationServices; children: ReactNode }): ReactElement {
  return <Context.Provider value={services}>{children}</Context.Provider>
}

/** 获取当前树的服务集合；不存在 Provider 时显式失败，避免跨实例全局回退。 */
export function useApplication(): ApplicationServices {
  const application = useContext(Context)
  if (!application) throw new FrontendError('MissingApplication', '应用服务尚未装配')
  return application
}

/** 订阅设置与界面状态；卸载自动解绑，不在 render 中访问 localStorage。 */
export function useUi(): UiState {
  const { ui } = useApplication()
  return useSyncExternalStore(ui.subscribe, ui.getSnapshot, ui.getSnapshot)
}

/** 返回当前实例的界面状态动作；setUi 只接受 UiState 的类型化补丁。 */
export function useUiActions(): { setUi: (patch: Partial<UiState>) => void } { return { setUi: useApplication().ui.set } }

/** 订阅会话快照，视图不再直接引用模块级会话变量。 */
export function useSession(): SessionState {
  const { sessionStore } = useApplication()
  return useSyncExternalStore(sessionStore.subscribe, sessionStore.getSnapshot, sessionStore.getSnapshot)
}

/** 读取当前会话控制器；动作由服务处理异常及异步世代，不产生新实例。 */
export function useSessionActions(): SessionController { return useApplication().session }

/** 读取当前认证控制器；组件只提供输入，不接触令牌存储。 */
export function useAuthActions(): AuthController { return useApplication().auth }

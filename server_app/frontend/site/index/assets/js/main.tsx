// React 严格模式和渲染器只在首页组合根创建。
import { StrictMode } from 'react'
// 浏览器挂载与 HMR 清理由入口拥有。
import { createRoot } from 'react-dom/client'
// 共享设计令牌是跨分区样式；各面板自行导入专属样式。
import '../../../assets/css/base.css'
// 公开配置可在入口按部署环境覆盖。
import { DEFAULT_CONFIG } from '../../../assets/js/config.ts'
// 应用实例通过依赖注入组装。
import { createApplication } from '../../../assets/js/application.ts'
// React Provider 不承担实例化工作。
import { ApplicationProvider } from '../../../assets/js/application-context.tsx'
// 结构化日志只发送本地诊断事件。
import { createLogger } from '../../../assets/js/logger.ts'
// 启动错误显式报告，避免空白挂载。
import { FrontendError } from '../../../assets/js/errors.ts'
// 浏览器 API 适配器在入口注入。
import { createBrowserAdapters } from './browser-adapters.ts'
// 分区装配列表只由入口使用。
import { composition } from './composition.ts'
// 壳组件只渲染已注册的槽位。
import { AppShell } from './app-shell.tsx'

/** 浏览器入口只创建当前页使用的端口；业务模块导入不触发副作用。 */
const ports = createBrowserAdapters(window, document)
/** trace 不是凭据；兼容现有 HTTP 部署中缺少 randomUUID 的浏览器上下文。 */
const traceId = window.crypto?.randomUUID?.() ?? `frontend-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`
/** 每个页面实例拥有自己的服务与状态，不在功能模块内复用全局单例。 */
const services = createApplication({ ...ports, fetcher: window.fetch.bind(window), logger: createLogger(ports.log, traceId),
  config: { ...DEFAULT_CONFIG, apiBase: import.meta.env.VITE_API_BASE_URL ?? DEFAULT_CONFIG.apiBase },
})
/** 注册器注销动作在页面销毁/HMR 时按逆序执行。 */
const cleanups: (() => void)[] = []
for (const plugin of composition) {
  const cleanup = plugin.apply({ slots: services.slots.scope(plugin.id) })
  if (cleanup) cleanups.push(cleanup)
}
/** 根节点来自当前首页 HTML，缺失时显式失败。 */
const element = document.getElementById('root')
if (!element) throw new FrontendError('MissingRoot', '首页缺少应用挂载节点')
/** React 生命周期由首页入口拥有。 */
const root = createRoot(element)
root.render(<StrictMode><ApplicationProvider services={services}><AppShell /></ApplicationProvider></StrictMode>)

/** 页面离开或 HMR 替换时销毁订阅、轮询与组件；重复调用安全。 */
function dispose(): void {
  cleanups.splice(0).reverse().forEach((cleanup: () => void): void => cleanup())
  services.dispose()
  root.unmount()
  window.removeEventListener('pagehide', dispose)
}
window.addEventListener('pagehide', dispose, { once: true })
if (import.meta.hot) import.meta.hot.dispose(dispose)

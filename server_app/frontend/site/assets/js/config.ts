/** 已有后端路由的唯一前端定义；路径不包含凭据或用户内容。 */
export const API_PATHS = {
  register: '/api/register', login: '/api/login', me: '/api/me', logout: '/api/logout',
  session: '/api/session', prepare: '/api/session/mod', reset: '/api/session/reset',
  task: '/api/task', pause: '/api/task/pause', conversation: '/api/conversation',
  status: '/api/status', events: '/api/events', sessions: '/api/sessions',
  question: '/api/question', answer: '/api/answer',
  jar: '/api/download/jar', source: '/api/download',
} as const

/** 配置只包含公开地址、存储键和时间参数；认证信息由用户输入。 */
export interface FrontendConfig {
  apiBase: string
  requestTimeoutMs: number
  pollingIntervalMs: number
  toastDurationMs: number
  elapsedTickMs: number
  visibleEventLimit: number
  titleLimit: number
  settingsStorageKey: string
  tokenStorageKey: string
  officialModel: string
  officialModels: readonly string[]
  officialBaseUrl: string
  paths: typeof API_PATHS
}

/** 默认值沿用已有前端；组合根可为测试或部署显式覆盖。 */
export const DEFAULT_CONFIG: FrontendConfig = {
  apiBase: '', requestTimeoutMs: 30_000, pollingIntervalMs: 2_000,
  toastDurationMs: 2_000, elapsedTickMs: 1_000, visibleEventLimit: 500, titleLimit: 24,
  settingsStorageKey: 'modforge_ui', tokenStorageKey: 'modforge_token',
  officialModel: 'deepseek-v4-flash',
  officialModels: ['deepseek-v4-flash', 'deepseek-v4-pro'],
  officialBaseUrl: 'https://api.deepseek.com', paths: API_PATHS,
}

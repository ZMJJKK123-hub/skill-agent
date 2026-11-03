// HTTP 和配置从组合根注入，所有会话请求都通过同一认证/错误边界。
import type { HttpClient } from '../../../assets/js/contracts.ts'
// 后端路由表保持既有接口。
import type { FrontendConfig } from '../../../assets/js/config.ts'
// 请求和响应 DTO 独立声明，业务层不传无契约字典。
import type { GenSettings, SessionRepository, SessionRequestDTO, TaskInput } from './session.types.ts'

/** 把用户设置转换为后端创建会话的 snake_case 字段；无 I/O 或全局依赖。 */
function sessionPayload(settings: GenSettings): SessionRequestDTO {
  return {
    api_key: settings.apiKey, game: settings.game, loader: settings.loader, version: settings.version,
    model: settings.model, base_url: settings.baseUrl, sandbox: settings.sandbox,
    vision_enabled: settings.visionEnabled, vision_api_key: settings.visionApiKey,
    vision_base_url: settings.visionBaseUrl, vision_model: settings.visionModel,
    auto_mode: settings.autoMode, search_api_key: settings.searchApiKey,
  }
}

/** 创建既有会话 HTTP 适配器。
 * Args: http/config 是组合根注入的实现。Returns: SessionRepository，失败抛标准 HTTP 异常。
 * reset 使用后端要求的查询参数；其他路由和字段不改变。Globals Used: None。
 */
export function createSessionRepository(http: HttpClient, config: FrontendConfig): SessionRepository {
  const paths = config.paths
  const query = (path: string, sessionId: string): string => `${path}?session_id=${encodeURIComponent(sessionId)}`
  return {
    create: (settings: GenSettings) => http.request(paths.session, { method: 'POST', body: JSON.stringify(sessionPayload(settings)) }),
    prepare: (id: string) => http.request(query(paths.prepare, id), { method: 'POST' }),
    start(input: TaskInput): Promise<void> {
      const settings = input.settings
      return http.request(paths.task, { method: 'POST', body: JSON.stringify({
        session_id: input.sessionId, prompt: input.prompt, mode: input.mode, resume: input.resume,
        ...(settings ? {
          api_key: settings.apiKey || undefined, model: settings.model, base_url: settings.baseUrl,
          vision_enabled: settings.visionEnabled, vision_api_key: settings.visionApiKey,
          vision_base_url: settings.visionBaseUrl, vision_model: settings.visionModel,
          auto_mode: settings.autoMode, search_api_key: settings.searchApiKey,
        } : {}),
      }) })
    },
    pause: (id: string) => http.request(query(paths.pause, id), { method: 'POST' }),
    reset: (id: string) => http.request(query(paths.reset, id), { method: 'POST' }),
    remove: (id: string) => http.request(query(paths.session, id), { method: 'DELETE' }),
    list: () => http.request(paths.sessions),
    conversation: (id: string) => http.request(query(paths.conversation, id)),
    events: (id: string, cursor) => http.request(query(paths.events, id) + (cursor ? `&cursor=${encodeURIComponent(JSON.stringify(cursor))}` : '')),
    status: (id: string) => http.request(query(paths.status, id)),
    question: (id: string) => http.request(query(paths.question, id)),
    answer: (id: string, answer: string, answers) => http.request(paths.answer, {
      method: 'POST', body: JSON.stringify(answers?.length ? { session_id: id, answers } : { session_id: id, answer }),
    }),
    download: (id: string, kind) => http.download(query(kind === 'jar' ? paths.jar : paths.source, id)),
  }
}

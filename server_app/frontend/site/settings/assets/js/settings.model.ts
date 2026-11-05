// 默认值由公开配置注入；此模块只计算，不访问存储或 DOM。
import type { FrontendConfig } from '../../../assets/js/config.ts'
// 设置类型与持久化格式集中在独立契约文件。
import type { ModelConfig, Provider, SavedSettings, UiState } from './settings.types.ts'

/** 创建完整默认状态；config 只提供公开模型参数，无全局依赖或副作用。 */
export function defaultUiState(config: FrontendConfig): UiState {
  return {
    settingsOpen: false, user: null, activeWorkspace: null, viewMode: 'chat', apiKey: '',
    game: 'minecraft', loader: 'forge', version: '1.21.11', locale: 'zh', theme: 'dark',
    model: config.officialModel, sandbox: 'full-access', providers: [], disabledPlugins: [], toast: null, promptDraft: '',
    visionEnabled: false, visionApiKey: '', visionBaseUrl: '', visionModel: '', autoMode: false, searchApiKey: '',
  }
}

/** 边界判断：只接受对象，数组/null 均回退为空对象。 */
function object(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}

/** 校验单个提供方；字段缺失时丢弃，避免损坏存储让模型选择界面崩溃。 */
function provider(value: unknown): Provider | null {
  const item = object(value)
  if (!['id', 'name', 'baseUrl', 'apiKey', 'model', 'protocol'].every((key: string): boolean => typeof item[key] === 'string')) return null
  return item as unknown as Provider
}

/** 从未知存储数据恢复设置。
 * Args: raw 是仓储读取结果；config 提供模型回退。Returns: 完整 UiState，损坏字段逐项使用默认值。
 * 不恢复用户和运行状态，设置插件始终可用。Globals Used: None。Dependencies: defaultUiState、resolveModelConfig。
 */
export function restoreUiState(raw: unknown, config: FrontendConfig): UiState {
  const state = defaultUiState(config)
  const data = object(raw)
  const strings = ['apiKey', 'game', 'loader', 'version', 'model', 'visionApiKey', 'visionBaseUrl', 'visionModel', 'searchApiKey'] as const
  for (const key of strings) if (typeof data[key] === 'string') state[key] = data[key]
  if (data.locale === 'zh' || data.locale === 'en') state.locale = data.locale
  if (data.theme === 'dark' || data.theme === 'light' || data.theme === 'system') state.theme = data.theme
  if (data.sandbox === 'full-access' || data.sandbox === 'workspace-write' || data.sandbox === 'read-only') state.sandbox = data.sandbox
  for (const key of ['visionEnabled', 'autoMode'] as const) if (typeof data[key] === 'boolean') state[key] = data[key]
  if (Array.isArray(data.providers)) state.providers = data.providers.map(provider).filter((item: Provider | null): item is Provider => item !== null)
  if (Array.isArray(data.disabledPlugins)) state.disabledPlugins = data.disabledPlugins.filter((id: unknown): id is string => typeof id === 'string' && id !== 'modforge-settings' && id !== 'modforge-workspace')
  state.model = resolveModelConfig(state, config).model
  return state
}

/** 解析用户选择的模型；未知模型回退官方默认，匹配到自定义项时返回其配置，不执行请求。 */
export function resolveModelConfig(state: Pick<UiState, 'apiKey' | 'model' | 'providers'>, config: FrontendConfig): ModelConfig {
  if (config.officialModels.includes(state.model)) return { apiKey: state.apiKey, baseUrl: config.officialBaseUrl, model: state.model }
  const item = state.providers.find((entry: Provider): boolean => entry.model.split(',').map((model: string): string => model.trim()).includes(state.model))
  return item ? { apiKey: item.apiKey, baseUrl: item.baseUrl, model: state.model }
    : { apiKey: state.apiKey, baseUrl: config.officialBaseUrl, model: config.officialModel }
}

/** 只投影可持久化设置；用户、消息、弹窗、运行状态永不写入设置存储。 */
export function savedSettings(state: UiState): SavedSettings {
  const { settingsOpen: _settingsOpen, user: _user, activeWorkspace: _workspace, viewMode: _viewMode, toast: _toast, promptDraft: _promptDraft, ...settings } = state
  return settings
}

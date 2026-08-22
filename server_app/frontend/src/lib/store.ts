import { useSyncExternalStore } from 'react'

export interface Provider {
  id: string
  name: string
  baseUrl: string
  apiKey: string
  model: string
  protocol: string
}

// 把「选中的模型」解析成后端实际要用的 (apiKey, baseUrl, model)：
// 官方模型走 DeepSeek；自定义模型匹配到对应 provider 的 key/地址。
export function resolveModelConfig(state: Pick<UiState, 'apiKey' | 'model' | 'providers'>): {
  apiKey: string
  baseUrl: string
  model: string
} {
  const { apiKey, model, providers } = state
  if (model === 'DeepSeek-V4-Flash-0731') {
    return { apiKey, baseUrl: 'https://llmapi.paratera.com', model }
  }
  const p = providers.find((p) => p.model.split(',').map((s) => s.trim()).includes(model))
  if (p) return { apiKey: p.apiKey, baseUrl: p.baseUrl, model }
  return { apiKey, baseUrl: 'https://llmapi.paratera.com', model: 'DeepSeek-V4-Flash-0731' }
}

export type Locale = 'zh' | 'en'
export type ThemePref = 'system' | 'light' | 'dark'
export type ViewMode = 'chat' | 'trajectory'
export type SandboxMode = 'full-access' | 'workspace-write' | 'read-only'

export interface UiState {
  settingsOpen: boolean
  user: { username: string } | null
  activeWorkspace: string | null
  viewMode: ViewMode
  apiKey: string
  game: string
  loader: string
  version: string
  locale: Locale
  theme: ThemePref
  model: string
  sandbox: SandboxMode
  providers: Provider[]
  disabledPlugins: string[]
  toast: string | null
  visionEnabled: boolean
  visionApiKey: string
  visionBaseUrl: string
  visionModel: string
  autoMode: boolean
  searchApiKey: string
}

const STORAGE_KEY = 'modforge_ui'

function loadState(): UiState {
  const base: UiState = {
    settingsOpen: false,
    user: null,
    activeWorkspace: null,
    viewMode: 'chat',
    apiKey: '',
    game: 'minecraft',
    loader: 'forge',
    version: '1.21.11',
    locale: 'zh',
    theme: 'dark',
    model: 'DeepSeek-V4-Flash-0731',
    sandbox: 'full-access',
    providers: [],
    disabledPlugins: [],
    toast: null,
    visionEnabled: false,
    visionApiKey: '',
    visionBaseUrl: '',
    visionModel: '',
    autoMode: false,
    searchApiKey: '',
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const loaded = { ...base, ...(JSON.parse(raw) as Partial<UiState>) }
      // 设置插件永远启用：清掉历史上可能被误关的持久化状态
      loaded.disabledPlugins = (loaded.disabledPlugins || []).filter((p) => p !== 'modforge-settings')
      return loaded
    }
  } catch {
    /* 损坏的本地存储回退默认值 */
  }
  return base
}

let state = loadState()

function persist() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        apiKey: state.apiKey,
        game: state.game,
        loader: state.loader,
        version: state.version,
        locale: state.locale,
        theme: state.theme,
        model: state.model,
        sandbox: state.sandbox,
        providers: state.providers,
        disabledPlugins: state.disabledPlugins,
        visionEnabled: state.visionEnabled,
        visionApiKey: state.visionApiKey,
        visionBaseUrl: state.visionBaseUrl,
        visionModel: state.visionModel,
        autoMode: state.autoMode,
        searchApiKey: state.searchApiKey,
      }),
    )
  } catch {
    /* localStorage 不可用时静默 */
  }
}

const listeners = new Set<() => void>()

export function setUi(patch: Partial<UiState>) {
  const prevTheme = state.theme
  state = { ...state, ...patch }
  persist()
  if (patch.theme !== undefined && patch.theme !== prevTheme) applyTheme(patch.theme)
  listeners.forEach((l) => l())
}

function subscribe(l: () => void) {
  listeners.add(l)
  return () => {
    listeners.delete(l)
  }
}
export function getUi(): UiState {
  return state
}
export function useUi(): UiState {
  return useSyncExternalStore(subscribe, getUi)
}

function resolveTheme(t: ThemePref): 'light' | 'dark' {
  if (t === 'system') {
    return typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: light)').matches
      ? 'light'
      : 'dark'
  }
  return t
}

export function applyTheme(t: ThemePref) {
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = resolveTheme(t)
  }
}

// 启动即应用持久化的主题
applyTheme(state.theme)

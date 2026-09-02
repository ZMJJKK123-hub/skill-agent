import { useSyncExternalStore } from 'react'

export interface Provider {
  id: string
  name: string
  baseUrl: string
  apiKey: string
  model: string
  protocol: string
}

// v1.0.2：官方模型默认值（deepseek-v4-flash + api.deepseek.com）已移除——
// 模型/Base URL/API Key 完全由用户在设置里添加提供方，未配置即"暂无配置"。
export function resolveModelConfig(state: Pick<UiState, 'model' | 'providers'>): {
  apiKey: string
  baseUrl: string
  model: string
} {
  const { model, providers } = state
  const p = providers.find((p) => p.model.split(',').map((s) => s.trim()).includes(model))
  if (p) return { apiKey: p.apiKey, baseUrl: p.baseUrl, model }
  // 匹配不到（未配置/老数据残留）：返回空三件套，由调用方拦截并提示
  return { apiKey: '', baseUrl: '', model: '' }
}

/** 当前是否有可用模型配置（下拉与发送按钮的判定依据） */
export function hasModelConfig(state: Pick<UiState, 'model' | 'providers'>): boolean {
  return resolveModelConfig(state).model !== ''
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
    // v1.0.1 纯本地版：登录已移除，user 恒为本地用户——所有依赖
    // user 非空的判断（可发送/显示历史等）自然通过，auth.tsx 不再挂载
    user: { username: 'local' },
    activeWorkspace: null,
    viewMode: 'chat',
    apiKey: '',
    game: 'minecraft',
    loader: 'forge',
    version: '1.21.11',
    locale: 'zh',
    theme: 'dark',
    model: '',
    sandbox: 'full-access',
    providers: [],
    disabledPlugins: [],
    toast: null,
    visionEnabled: true,
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
      // 设置插件永远启用：清掉历史上可能被误关的持久化状态（sidebar 同理——
      // 禁用 sidebar 会藏掉设置入口造成自锁，实测缺陷 #9）
      loaded.disabledPlugins = (loaded.disabledPlugins || []).filter((p) => p !== 'modforge-settings' && p !== 'modforge-sidebar')
      // 模型清洗（v1.0.2）：持久化的模型名必须仍在某个 provider 里才保留；
      // 官方默认已移除，匹配不到一律回退空（= 暂无配置），不静默指向任何模型
      if (loaded.model) {
        const known = (loaded.providers || []).some((p) =>
          p.model.split(',').map((s) => s.trim()).includes(loaded.model!),
        )
        if (!known) loaded.model = ''
      }
      // 一次性迁移：识图模式改为默认开启（红宝石剑会话因旧默认 false 导致
      // analyze_image 全部失败、被迫绕远路）。只翻转一次，之后的开关尊重用户选择。
      if (!localStorage.getItem('modforge_vision_default_on')) {
        localStorage.setItem('modforge_vision_default_on', '1')
        loaded.visionEnabled = true
      }
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

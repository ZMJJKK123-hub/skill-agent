import { useSyncExternalStore } from 'react'

export interface Provider {
  id: string
  name: string
  baseUrl: string
  apiKey: string
  model: string
}

export type Locale = 'zh' | 'en'
export type ThemePref = 'system' | 'light' | 'dark'

export interface UiState {
  settingsOpen: boolean
  user: { username: string } | null
  activeWorkspace: string | null
  apiKey: string
  game: string
  loader: string
  version: string
  locale: Locale
  theme: ThemePref
  model: string
  providers: Provider[]
  disabledPlugins: string[]
}

const STORAGE_KEY = 'modforge_ui'

function loadState(): UiState {
  const base: UiState = {
    settingsOpen: false,
    user: null,
    activeWorkspace: null,
    apiKey: '',
    game: 'minecraft',
    loader: 'forge',
    version: '1.21.11',
    locale: 'zh',
    theme: 'dark',
    model: 'deepseek-v4-flash',
    providers: [],
    disabledPlugins: [],
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return { ...base, ...(JSON.parse(raw) as Partial<UiState>) }
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
        providers: state.providers,
        disabledPlugins: state.disabledPlugins,
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

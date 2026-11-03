// 状态容器只通过跨分区契约暴露，不携带浏览器存储实现。
import type { StateStore } from '../../../assets/js/contracts.ts'

export interface Provider { id: string; name: string; baseUrl: string; apiKey: string; model: string; protocol: string }
export interface ModelConfig { apiKey: string; baseUrl: string; model: string }
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
export type SavedSettings = Omit<UiState, 'settingsOpen' | 'user' | 'activeWorkspace' | 'viewMode' | 'toast'>
export interface SettingsRepository { load(): unknown; save(settings: SavedSettings): void }
export type UiStore = StateStore<UiState>
export type SectionKey = 'general' | 'models' | 'vision' | 'plugins' | 'language' | 'appearance' | 'agent'
export type SettingsDraft = Pick<UiState, 'apiKey' | 'loader' | 'version' | 'sandbox' | 'visionEnabled' | 'visionApiKey' | 'visionBaseUrl' | 'visionModel' | 'autoMode' | 'searchApiKey'>

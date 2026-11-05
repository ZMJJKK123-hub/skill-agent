// 通用状态实现与主题副作用接口分别注入设置状态层。
import { createStateStore } from '../../../assets/js/state-store.ts'
// 配置不从业务模块自行读取环境。
import type { FrontendConfig } from '../../../assets/js/config.ts'
// 主题端口隔离 DOM 副作用。
import type { ThemePort } from '../../../assets/js/contracts.ts'
// 仓储和状态的公共边界。
import type { SettingsRepository, UiState, UiStore } from './settings.types.ts'
// 恢复和持久化投影均为可单独测试的纯计算。
import { restoreUiState, savedSettings } from './settings.model.ts'

/** 组装设置状态；读取仓储并应用主题只在显式创建时发生。
 * set 发布新快照并保存设置；仅更新 promptDraft 时跳过仓储，草稿永不落盘；设置插件不可关闭。
 * Args: repository/config/theme 为组合根提供。Returns: UiStore。Globals Used: None。
 */
export function createUiStore(repository: SettingsRepository, config: FrontendConfig, theme: ThemePort): UiStore {
  const store = createStateStore(restoreUiState(repository.load(), config))
  theme.apply(store.getSnapshot().theme)
  return {
    getSnapshot: store.getSnapshot, subscribe: store.subscribe,
    set(patch: Partial<UiState>): void {
      const next = { ...patch }
      if (next.disabledPlugins) next.disabledPlugins = next.disabledPlugins.filter((id: string): boolean => id !== 'modforge-settings')
      const prior = store.getSnapshot().theme
      const state = { ...store.getSnapshot(), ...next }
      // 输入草稿不持久化；纯输入更新也不重复写入其他设置。
      if (Object.keys(patch).some((key: string): boolean => key !== 'promptDraft')) repository.save(savedSettings(state))
      if (state.theme !== prior) theme.apply(state.theme)
      store.set(next)
    },
  }
}

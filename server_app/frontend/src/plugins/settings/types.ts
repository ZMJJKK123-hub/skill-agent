/**
 * 设置面板共享类型与常量（由 settings.tsx 迁出）。
 */
import type { Provider, ThemePref, SandboxMode } from '../../lib/store'

/** 设置分区键 */
export type SectionKey = 'general' | 'models' | 'vision' | 'plugins' | 'language' | 'appearance' | 'agent'

/** 通用配置草稿：应用前不落库（providers/theme/locale 同样纳入草稿，
 *  "取消"整体丢弃——实测缺陷 #8 与主题/语言误生效的修复载体） */
export type Draft = {
  model: string
  loader: string
  version: string
  sandbox: SandboxMode
  visionEnabled: boolean
  visionApiKey: string
  visionBaseUrl: string
  visionModel: string
  autoMode: boolean
  searchApiKey: string
  providers: Provider[]
  theme: ThemePref
  locale: 'zh' | 'en'
}

/** 可选 MC 版本（模板目录存在性由后端判定） */
export const VERSIONS = ['1.21.11', '1.21.10', '1.21.9']

/** 可选加载器 */
export const LOADERS = ['forge', 'neoforge', 'fabric']

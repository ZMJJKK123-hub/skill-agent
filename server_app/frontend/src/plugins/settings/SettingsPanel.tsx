/**
 * 设置面板壳：分区导航 + 草稿管理 + 应用/取消（由 settings.tsx 原样迁出）。
 */
import { useEffect, useState } from 'react'
import { setUi, useUi } from '../../lib/store'
import { useT } from '../../lib/i18n'
import type { SectionKey, Draft } from './types'
import { GeneralSection } from './sections/General'
import { ModelsSection } from './sections/Models'
import { AgentSection, AppearanceSection, LanguageSection, PluginsSection, VisionSection } from './sections/Misc'

function SectionContent({ section, draft, setDraft }: {
  section: SectionKey
  draft: Draft
  setDraft: (d: Draft) => void
}) {
  switch (section) {
    case 'general':
      return <GeneralSection draft={draft} setDraft={setDraft} />
    case 'models':
      return <ModelsSection draft={draft} setDraft={setDraft} />
    case 'vision':
      return <VisionSection draft={draft} setDraft={setDraft} />
    case 'plugins':
      return <PluginsSection />
    case 'agent':
      return <AgentSection />
    case 'language':
      return <LanguageSection draft={draft} setDraft={setDraft} />
    case 'appearance':
      return <AppearanceSection draft={draft} setDraft={setDraft} />
  }
}

export function SettingsPanel() {
  const { settingsOpen } = useUi()
  const t = useT()
  const [section, setSection] = useState<SectionKey>('general')

  // 通用配置草稿：应用前不落库；theme/locale 同样纳入草稿（此前点选项
  // 直接写全局，"取消"后主题/语言已是新值——实测缺陷）
  const { model, loader, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey, providers, theme, locale } = useUi()
  const [draft, setDraft] = useState<Draft>({
    model, loader, version, sandbox,
    visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey,
    providers,
    theme, locale,
  })
  useEffect(() => {
    if (settingsOpen) {
      // 每次打开回到"通用"分区：重开不停留在意外位置
      setSection('general')
      setDraft({
        model, loader, version, sandbox,
        visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey,
        providers,
        theme, locale,
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen])

  if (!settingsOpen) return null

  const apply = () => {
    setUi({
      model: draft.model,
      loader: draft.loader,
      version: draft.version,
      sandbox: draft.sandbox,
      visionEnabled: draft.visionEnabled,
      visionApiKey: draft.visionApiKey.trim(),
      visionBaseUrl: draft.visionBaseUrl.trim(),
      visionModel: draft.visionModel.trim(),
      autoMode: draft.autoMode,
      searchApiKey: draft.searchApiKey.trim(),
      providers: draft.providers,
      theme: draft.theme,
      locale: draft.locale,
      settingsOpen: false,
    })
  }
  const cancel = () => setUi({ settingsOpen: false })

  const SECTIONS: { key: SectionKey; label: string }[] = [
    { key: 'general', label: t('settings.general') },
    { key: 'models', label: t('settings.models') },
    { key: 'vision', label: t('settings.vision') },
    { key: 'plugins', label: t('settings.plugins') },
    { key: 'agent', label: t('settings.agent') },
    { key: 'language', label: t('settings.language') },
    { key: 'appearance', label: t('settings.appearance') },
  ]

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/70" onClick={cancel}>
      <div
        className="flex h-[80vh] w-[760px] max-w-[92vw] flex-col overflow-hidden rounded-xl border border-strong bg-panel"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex min-h-0 flex-1">
          <nav className="w-44 shrink-0 border-r border-line p-2">
            {SECTIONS.map((s) => (
              <button
                key={s.key}
                onClick={() => setSection(s.key)}
                className={`block w-full rounded-md px-3 py-2 text-left text-sm ${
                  section === s.key ? 'bg-subtle text-main' : 'text-muted hoverable'
                }`}
              >
                {s.label}
              </button>
            ))}
          </nav>
          <div className="flex-1 overflow-y-auto p-5">
            <SectionContent section={section} draft={draft} setDraft={setDraft} />
          </div>
        </div>
        {/* 底部：取消 / 应用 */}
        <div className="flex justify-end gap-2 border-t border-line p-3">
          <button onClick={cancel} className="hoverable rounded-md border border-strong px-4 py-1.5 text-sm">
            {t('settings.cancel')}
          </button>
          <button onClick={apply} className="rounded-md bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400">
            {t('settings.apply')}
          </button>
        </div>
      </div>
    </div>
  )
}

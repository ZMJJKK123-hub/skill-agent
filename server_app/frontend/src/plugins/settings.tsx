import { useEffect, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { setUi, useUi, type Provider, type ThemePref, type SandboxMode } from '../lib/store'
import { useT } from '../lib/i18n'
import { composition } from '../composition'

type SectionKey = 'general' | 'models' | 'vision' | 'plugins' | 'language' | 'appearance' | 'agent'

type Draft = {
  apiKey: string
  loader: string
  version: string
  sandbox: SandboxMode
  visionEnabled: boolean
  visionApiKey: string
  visionBaseUrl: string
  visionModel: string
  autoMode: boolean
  searchApiKey: string
}

const VERSIONS = ['1.21.11', '1.21.10', '1.21.9']
const LOADERS = ['forge', 'neoforge', 'fabric']

function SettingsPanel() {
  const { settingsOpen } = useUi()
  const t = useT()
  const [section, setSection] = useState<SectionKey>('general')

  // 通用配置草稿：应用前不落库
  const { apiKey, loader, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey } = useUi()
  const [draft, setDraft] = useState({
    apiKey, loader, version, sandbox,
    visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey,
  })
  useEffect(() => {
    if (settingsOpen) setDraft({
      apiKey, loader, version, sandbox,
      visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey,
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen])

  if (!settingsOpen) return null

  const apply = () => {
    setUi({
      apiKey: draft.apiKey.trim(),
      loader: draft.loader,
      version: draft.version,
      sandbox: draft.sandbox,
      visionEnabled: draft.visionEnabled,
      visionApiKey: draft.visionApiKey.trim(),
      visionBaseUrl: draft.visionBaseUrl.trim(),
      visionModel: draft.visionModel.trim(),
      autoMode: draft.autoMode,
      searchApiKey: draft.searchApiKey.trim(),
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
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50" onClick={cancel}>
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

function GeneralSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('settings.general')}</h2>
      <Field label={t('general.game')}>
        <input value="Minecraft" disabled className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm opacity-60" />
      </Field>
      <Field label={t('general.loader')}>
        <select
          value={draft.loader}
          onChange={(e) => setDraft({ ...draft, loader: e.target.value })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        >
          {LOADERS.map((l) => (
            <option key={l} value={l}>
              {l === 'forge' ? 'Forge' : l === 'neoforge' ? 'NeoForge' : 'Fabric'}
            </option>
          ))}
        </select>
      </Field>
      <Field label={t('general.version')}>
        <select
          value={draft.version}
          onChange={(e) => setDraft({ ...draft, version: e.target.value })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        >
          {VERSIONS.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </Field>
      <Field label={t('general.apiKey')}>
        <input
          type="password"
          value={draft.apiKey}
          onChange={(e) => setDraft({ ...draft, apiKey: e.target.value })}
          placeholder={t('general.apiKeyHint')}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
      <Field label={t('general.sandbox')}>
        <select
          value={draft.sandbox}
          onChange={(e) => setDraft({ ...draft, sandbox: e.target.value as SandboxMode })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        >
          <option value="full-access">{t('general.sandbox.full')}</option>
          <option value="workspace-write">{t('general.sandbox.workspace')}</option>
          <option value="read-only">{t('general.sandbox.readonly')}</option>
        </select>
      </Field>
      <Field label="全自动模式">
        <button
          onClick={() => setDraft({ ...draft, autoMode: !draft.autoMode })}
          className={`relative h-6 w-11 rounded-full transition ${draft.autoMode ? 'bg-forge-500' : 'bg-slate-600'}`}
        >
          <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition ${draft.autoMode ? 'left-[22px]' : 'left-0.5'}`} />
        </button>
        <p className="mt-1 text-xs text-faint">开启后 agent 不再阻塞等待提问，会用合理默认值继续。</p>
      </Field>
      <Field label="Tavily Search API Key">
        <input
          type="password"
          value={draft.searchApiKey}
          onChange={(e) => setDraft({ ...draft, searchApiKey: e.target.value })}
          placeholder="tvly-…（留空则使用 DuckDuckGo fallback）"
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
      <p className="text-xs text-faint">{t('general.fallbackHint')}</p>
    </div>
  )
}

function ModelsSection() {
  const t = useT()
  const { providers } = useUi()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', baseUrl: '', apiKey: '', model: '', protocol: 'openai' })

  const save = () => {
    if (!form.name.trim() || !form.model.trim()) return
    const p: Provider = {
      id: 'p' + Date.now().toString(36),
      name: form.name.trim(),
      baseUrl: form.baseUrl.trim(),
      apiKey: form.apiKey.trim(),
      model: form.model.trim(),
      protocol: form.protocol,
    }
    setUi({ providers: [...providers, p] })
    setForm({ name: '', baseUrl: '', apiKey: '', model: '', protocol: 'openai' })
    setShowForm(false)
  }
  const remove = (id: string) => setUi({ providers: providers.filter((p) => p.id !== id) })

  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('models.title')}</h2>
      <div className="mb-2 rounded-md border border-forge-500/40 bg-forge-500/10 px-3 py-2 text-sm">
        <div className="font-medium text-forge-300">DeepSeek</div>
        <div className="text-xs text-faint">DeepSeek-V4-Flash-0731 · 官方</div>
      </div>
      {providers.length === 0 && <div className="mb-2 px-1 text-xs text-faint">{t('models.empty')}</div>}
      {providers.map((p) => (
        <div key={p.id} className="mb-2 flex items-center justify-between rounded-md border border-line px-3 py-2 text-sm">
          <div>
            <div className="font-medium">{p.name}</div>
            <div className="text-xs text-faint">{p.model}</div>
          </div>
          <button onClick={() => remove(p.id)} className="hoverable rounded px-2 py-1 text-xs text-muted">
            {t('models.remove')}
          </button>
        </div>
      ))}

      {showForm ? (
        <div className="mt-2 space-y-2 rounded-md border border-line p-3">
          <div>
            <div className="mb-1 text-xs text-faint">{t('models.protocol')}</div>
            <select value={form.protocol} onChange={(e) => setForm({ ...form, protocol: e.target.value })} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none">
              <option value="openai">OpenAI 兼容（含 DeepSeek）</option>
            </select>
          </div>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder={t('models.name')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none" />
          <input value={form.baseUrl} onChange={(e) => setForm({ ...form, baseUrl: e.target.value })} placeholder={t('models.baseUrl')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none" />
          <input value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} placeholder={t('models.model') + '（可逗号分隔多个）'} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none" />
          <input value={form.apiKey} onChange={(e) => setForm({ ...form, apiKey: e.target.value })} type="password" placeholder={t('models.apiKey')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none" />
          <div className="flex gap-2">
            <button onClick={save} className="rounded-md bg-forge-500 px-3 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400">
              {t('models.save')}
            </button>
            <button onClick={() => setShowForm(false)} className="hoverable rounded-md border border-line px-3 py-1.5 text-sm">
              {t('settings.cancel')}
            </button>
          </div>
        </div>
      ) : (
        <button onClick={() => setShowForm(true)} className="mt-2 rounded-md border border-forge-500/40 px-3 py-1.5 text-sm text-forge-400 hover:bg-forge-500/10">
          ＋ {t('models.add')}
        </button>
      )}
    </div>
  )
}

function VisionSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('vision.title')}</h2>
      <p className="mb-3 text-xs text-faint">{t('vision.hint')}</p>
      <Field label={t('vision.enabled')}>
        <button
          onClick={() => setDraft({ ...draft, visionEnabled: !draft.visionEnabled })}
          className={`relative h-6 w-11 rounded-full transition ${draft.visionEnabled ? 'bg-forge-500' : 'bg-slate-600'}`}
        >
          <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition ${draft.visionEnabled ? 'left-[22px]' : 'left-0.5'}`} />
        </button>
      </Field>
      <Field label={t('vision.apiKey')}>
        <input
          type="password"
          value={draft.visionApiKey}
          onChange={(e) => setDraft({ ...draft, visionApiKey: e.target.value })}
          placeholder="留空自动用 GLM-4.6V-Flash（读桌面 glm4v-vision-mcp/server/.env）"
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
      <Field label={t('vision.baseUrl')}>
        <input
          value={draft.visionBaseUrl}
          onChange={(e) => setDraft({ ...draft, visionBaseUrl: e.target.value })}
          placeholder="留空自动用 https://open.bigmodel.cn/api/paas/v4"
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
      <Field label={t('vision.model')}>
        <input
          value={draft.visionModel}
          onChange={(e) => setDraft({ ...draft, visionModel: e.target.value })}
          placeholder="留空自动用 glm-4.6v-flash"
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
    </div>
  )
}

function PluginsSection() {
  const t = useT()
  const { disabledPlugins } = useUi()
  const toggle = (id: string) => {
    setUi({
      disabledPlugins: disabledPlugins.includes(id)
        ? disabledPlugins.filter((p) => p !== id)
        : [...disabledPlugins, id],
    })
  }
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('plugins.title')}</h2>
      {composition.map((p) => {
        const disabled = disabledPlugins.includes(p.id)
        const locked = p.id === 'modforge-settings'
        return (
          <div key={p.id} className="mb-2 flex items-center justify-between rounded-md border border-line px-3 py-2 text-sm">
            <span>
              {p.name} <span className="text-faint">({p.id})</span>
            </span>
            {locked ? (
              <span className="text-xs text-faint">始终启用</span>
            ) : (
              <button
                onClick={() => toggle(p.id)}
                className={`relative h-5 w-9 rounded-full transition ${disabled ? 'bg-slate-600' : 'bg-forge-500'}`}
              >
                <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition ${disabled ? 'left-0.5' : 'left-[18px]'}`} />
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}

function AgentSection() {
  const t = useT()
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('agent.title')}</h2>
      <div className="rounded-md border border-forge-500/40 bg-forge-500/10 px-3 py-2 text-sm">
        <div className="font-medium text-forge-300">{t('agent.standard')}</div>
        <div className="text-xs text-faint">{t('agent.standardDesc')}</div>
      </div>
    </div>
  )
}

function LanguageSection() {
  const t = useT()
  const { locale } = useUi()
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('language.title')}</h2>
      <div className="space-y-2">
        {(['zh', 'en'] as const).map((id) => (
          <button
            key={id}
            onClick={() => setUi({ locale: id })}
            className={`block w-full rounded-md border px-3 py-2 text-left text-sm ${locale === id ? 'border-forge-500/40 bg-forge-500/10 text-forge-300' : 'border-line text-muted hoverable'}`}
          >
            {id === 'zh' ? t('language.zh') : t('language.en')}
          </button>
        ))}
      </div>
    </div>
  )
}

function AppearanceSection() {
  const t = useT()
  const { theme } = useUi()
  const options: { id: ThemePref; label: string }[] = [
    { id: 'light', label: t('appearance.light') },
    { id: 'dark', label: t('appearance.dark') },
    { id: 'system', label: t('appearance.system') },
  ]
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('appearance.title')}</h2>
      <div className="flex gap-2">
        {options.map((o) => (
          <button
            key={o.id}
            onClick={() => setUi({ theme: o.id })}
            className={`flex-1 rounded-md border px-3 py-2 text-sm ${theme === o.id ? 'border-forge-500/40 bg-forge-500/10 text-forge-300' : 'border-line text-muted hoverable'}`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}

function SectionContent({
  section,
  draft,
  setDraft,
}: {
  section: SectionKey
  draft: Draft
  setDraft: (d: Draft) => void
}) {
  switch (section) {
    case 'general':
      return <GeneralSection draft={draft} setDraft={setDraft} />
    case 'models':
      return <ModelsSection />
    case 'vision':
      return <VisionSection draft={draft} setDraft={setDraft} />
    case 'plugins':
      return <PluginsSection />
    case 'agent':
      return <AgentSection />
    case 'language':
      return <LanguageSection />
    case 'appearance':
      return <AppearanceSection />
  }
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <div className="mb-1 text-sm text-muted">{label}</div>
      {children}
    </div>
  )
}

function SettingsEntry({ collapsed }: { collapsed?: boolean }) {
  const t = useT()
  return (
    <button
      onClick={() => setUi({ settingsOpen: true })}
      className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm hoverable"
      title={t('nav.settings')}
    >
      <span>⚙️</span>
      {!collapsed && <span>{t('nav.settings')}</span>}
    </button>
  )
}

export const settingsPlugin: PluginManifest = {
  id: 'modforge-settings',
  name: '设置',
  apply(ctx) {
    ctx.slots.inject(SLOTS.overlay, 'settings', () => <SettingsPanel />)
    ctx.slots.inject(SLOTS.sidebarFooter, 'settings-entry', (props: any) => <SettingsEntry collapsed={props?.collapsed} />, 10)
  },
}

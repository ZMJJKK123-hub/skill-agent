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
  providers: Provider[]
}

const VERSIONS = ['1.21.11', '1.21.10', '1.21.9']
const LOADERS = ['forge', 'neoforge', 'fabric']

function SettingsPanel() {
  const { settingsOpen } = useUi()
  const t = useT()
  const [section, setSection] = useState<SectionKey>('general')

  // 通用配置草稿：应用前不落库（providers 同样纳入草稿——增删改全部
  // 只改 draft，点"应用"才生效，"取消"整体丢弃，实测缺陷 #8 的修复）
  const { apiKey, loader, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey, providers } = useUi()
  const [draft, setDraft] = useState({
    apiKey, loader, version, sandbox,
    visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey,
    providers,
  })
  useEffect(() => {
    if (settingsOpen) setDraft({
      apiKey, loader, version, sandbox,
      visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey,
      providers,
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
      providers: draft.providers,
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

function ModelsSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', baseUrl: '', apiKey: '', model: '', protocol: 'openai' })
  // 编辑态：editId = 正在编辑的 provider；模型 ID 以 chip 形式逐个增删
  const [editId, setEditId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState({ name: '', baseUrl: '', apiKey: '' })
  const [newModel, setNewModel] = useState('')

  const providers = draft.providers
  const modelsOf = (p: Provider) => p.model.split(',').map((s) => s.trim()).filter(Boolean)

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
    setDraft({ ...draft, providers: [...providers, p] })
    setForm({ name: '', baseUrl: '', apiKey: '', model: '', protocol: 'openai' })
    setShowForm(false)
  }
  const remove = (id: string) => setDraft({ ...draft, providers: providers.filter((p) => p.id !== id) })

  const startEdit = (p: Provider) => {
    setEditId(p.id)
    setEditForm({ name: p.name, baseUrl: p.baseUrl, apiKey: p.apiKey })
    setNewModel('')
  }
  const applyEdit = () => {
    if (!editId) return
    setDraft({
      ...draft,
      providers: providers.map((p) =>
        p.id === editId ? { ...p, name: editForm.name.trim(), baseUrl: editForm.baseUrl.trim(), apiKey: editForm.apiKey.trim() } : p,
      ),
    })
    setEditId(null)
  }
  const addModel = (pid: string) => {
    const mid = newModel.trim()
    if (!mid) return
    setDraft({
      ...draft,
      providers: providers.map((p) => {
        if (p.id !== pid) return p
        const ms = modelsOf(p)
        if (ms.includes(mid)) return p
        return { ...p, model: [...ms, mid].join(',') }
      }),
    })
    setNewModel('')
  }
  const removeModel = (pid: string, mid: string) => {
    setDraft({
      ...draft,
      providers: providers.map((p) => {
        if (p.id !== pid) return p
        const ms = modelsOf(p).filter((m) => m !== mid)
        if (ms.length === 0) return p // 至少保留一个模型 ID
        return { ...p, model: ms.join(',') }
      }),
    })
  }

  return (
    <div>
      <h2 className="mb-1 text-lg font-semibold">{t('models.title')}</h2>
      <p className="mb-3 text-xs text-faint">提供方的增删改与模型 ID 管理均为草稿：点右下角「应用」保存，「取消」丢弃全部改动。</p>
      <div className="mb-2 rounded-md border border-forge-500/40 bg-forge-500/10 px-3 py-2 text-sm">
        <div className="font-medium text-forge-300">DeepSeek</div>
        <div className="text-xs text-faint">deepseek-v4-flash / deepseek-v4-pro · 官方 api.deepseek.com</div>
      </div>
      {providers.length === 0 && <div className="mb-2 px-1 text-xs text-faint">{t('models.empty')}</div>}
      {providers.map((p) =>
        editId === p.id ? (
          <div key={p.id} className="mb-2 space-y-2 rounded-md border border-forge-500/40 bg-forge-500/5 p-3 text-sm">
            <div className="text-xs font-medium text-forge-300">编辑提供方</div>
            <input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} placeholder={t('models.name')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
            <input value={editForm.baseUrl} onChange={(e) => setEditForm({ ...editForm, baseUrl: e.target.value })} placeholder={t('models.baseUrl')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
            <input value={editForm.apiKey} onChange={(e) => setEditForm({ ...editForm, apiKey: e.target.value })} type="password" placeholder={t('models.apiKey')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
            <div>
              <div className="mb-1 text-xs text-faint">模型 ID（点 ✕ 移除；至少保留一个）</div>
              <div className="flex flex-wrap gap-1.5">
                {modelsOf(p).map((mid) => (
                  <span key={mid} className="flex items-center gap-1 rounded-md border border-line bg-field px-2 py-1 text-xs">
                    {mid}
                    <button onClick={() => removeModel(p.id, mid)} title="移除此模型 ID" className="text-faint hover:text-red-400">
                      ✕
                    </button>
                  </span>
                ))}
              </div>
              <div className="mt-2 flex gap-2">
                <input
                  value={newModel}
                  onChange={(e) => setNewModel(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addModel(p.id)
                    }
                  }}
                  placeholder="输入新的模型 ID 后回车，如 glm-4.7-flash"
                  className="flex-1 rounded-md border border-line bg-field px-3 py-1.5 text-xs outline-none focus:border-forge-500"
                />
                <button onClick={() => addModel(p.id)} className="rounded-md border border-forge-500/40 px-3 py-1.5 text-xs text-forge-400 hover:bg-forge-500/10">
                  ＋ 添加
                </button>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={applyEdit} className="rounded-md bg-forge-500 px-3 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400">
                保存修改
              </button>
              <button onClick={() => setEditId(null)} className="hoverable rounded-md border border-line px-3 py-1.5 text-sm">
                {t('settings.cancel')}
              </button>
            </div>
          </div>
        ) : (
          <div key={p.id} className="mb-2 flex items-center justify-between rounded-md border border-line px-3 py-2 text-sm">
            <div className="min-w-0">
              <div className="font-medium">{p.name}</div>
              <div className="truncate text-xs text-faint">{modelsOf(p).join(' / ')}</div>
            </div>
            <div className="flex shrink-0 gap-1">
              <button onClick={() => startEdit(p)} className="hoverable rounded px-2 py-1 text-xs text-muted">
                编辑
              </button>
              <button onClick={() => remove(p.id)} className="hoverable rounded px-2 py-1 text-xs text-muted">
                {t('models.remove')}
              </button>
            </div>
          </div>
        ),
      )}

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
          <input value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} placeholder={t('models.model') + '（可逗号分隔多个，保存后可在编辑里逐个增删）'} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none" />
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
        // settings 与 sidebar 均为常驻插件：禁用 sidebar 会连设置入口一起藏掉，
        // 用户没有任何 UI 路径恢复（实测自锁缺陷），与 settings 一同锁定
        const locked = p.id === 'modforge-settings' || p.id === 'modforge-sidebar'
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
      return <ModelsSection draft={draft} setDraft={setDraft} />
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

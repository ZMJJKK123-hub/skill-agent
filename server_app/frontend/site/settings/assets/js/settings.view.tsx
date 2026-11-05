// 选项属于设置分区；不在视图内散落配置常量。
import { VERSIONS, LOADERS } from './settings.config.ts'
// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// 本分区样式仅在当前分区模块加载时挂载。
import '../css/settings.css'
// React hooks 用于组件状态、订阅和生命周期。
import { useEffect, useState } from 'react'
// 类型契约约束分区间的数据和组件通信。
import type { PluginManifest, PluginContext, SlotProps } from '../../../assets/js/slots.types.ts'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useApplication, useUi, useUiActions } from '../../../assets/js/application-context.tsx'
// 类型契约约束分区间的数据和组件通信。
import type { Provider, ThemePref, SandboxMode, SectionKey, SettingsDraft as Draft } from './settings.types.ts'
// 翻译 hook 为本分区提供当前语言文案。
import { useT } from '../../../assets/js/i18n.ts'
// 共享插件元数据避免设置面板反向依赖组合根。
import { PLUGIN_CATALOG } from '../../../assets/js/plugin-catalog.ts'
// 设置导航使用共享图标，图形不承担业务状态。
import { Icon } from '../../../assets/js/icons.tsx'
// 图标名称与导航项均为显式契约。
import type { IconName } from '../../../assets/js/icons.types.ts'


/** 维护设置草稿；应用后写状态，取消不提交通用草稿，关闭时不渲染。
 * Args: 无参数；从设置状态创建表单草稿。
 * Returns: React 展示元素；空数据或关闭态返回 null。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function SettingsPanel(): ReactElement | null {
  const { setUi } = useUiActions()
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

  const SECTIONS: { key: SectionKey; label: string; icon: IconName }[] = [
    { key: 'general', label: t('settings.general'), icon: 'sliders' },
    { key: 'models', label: t('settings.models'), icon: 'layers' },
    { key: 'vision', label: t('settings.vision'), icon: 'eye' },
    { key: 'plugins', label: t('settings.plugins'), icon: 'cube' },
    { key: 'agent', label: t('settings.agent'), icon: 'sparkles' },
    { key: 'language', label: t('settings.language'), icon: 'globe' },
    { key: 'appearance', label: t('settings.appearance'), icon: 'sun' },
  ]

  return (
    <div className="modal-backdrop fixed inset-0 z-40 flex items-center justify-center" onClick={cancel}>
      <div
        role="dialog" aria-modal="true" aria-labelledby="settings-heading"
        className="settings-dialog surface-dialog flex flex-col overflow-hidden border border-strong bg-panel"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(event) => { if (event.key === 'Escape') cancel() }}
      >
        <div className="settings-dialog-heading"><div><h2 id="settings-heading">{t('studio.settingsTitle')}</h2><p>{t('studio.settingsDesc')}</p></div><button className="icon-button" aria-label={t('studio.close')} onClick={cancel}><Icon name="close" /></button></div>
        <div className="flex min-h-0 flex-1">
          <nav className="settings-nav shrink-0 border-r border-line">
            {SECTIONS.map((s) => (
              <button
                key={s.key}
                onClick={() => setSection(s.key)}
                aria-pressed={section === s.key}
                className="settings-nav-item"
              >
                <Icon name={s.icon} size={16} />{s.label}
              </button>
            ))}
          </nav>
          <div className="settings-content min-w-0 flex-1 overflow-y-auto">
            <SectionContent section={section} draft={draft} setDraft={setDraft} />
          </div>
        </div>
        {/* 底部：取消 / 应用 */}
        <div className="settings-actions flex justify-end gap-2 border-t border-line">
          <button onClick={cancel} className="hoverable rounded-md border border-strong px-4 py-1.5 text-sm">
            {t('settings.cancel')}
          </button>
          <button onClick={apply} className="primary-button px-5 py-2 text-xs">
            <Icon name="check" size={15} />{t('settings.apply')}
          </button>
        </div>
      </div>
    </div>
  )
}

/** 编辑通用草稿字段，不直接调用后端或访问浏览器存储。
 * Args: 通用设置草稿，以及接收完整新草稿的更新回调。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function GeneralSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }): ReactElement {
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

/** 管理自定义模型提供方；名称和模型为空时不保存，保存/删除立即更新设置。
 * Args: 无参数；读取提供方列表并维护新建表单。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function ModelsSection(): ReactElement {
  const { config } = useApplication()
  const { setUi } = useUiActions()
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
        <div className="text-xs text-faint">{config.officialModels.join(' / ')} · {config.officialBaseUrl}</div>
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

/** 编辑视觉配置草稿；实际请求仍由既有后端消费配置。
 * Args: 视觉设置草稿，以及接收完整新草稿的更新回调。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function VisionSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }): ReactElement {
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

/** 更新分区启用列表；设置分区始终启用，其他分区按配置隐藏。
 * Args: 无参数；读取插件元数据和禁用列表。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function PluginsSection(): ReactElement {
  const { setUi } = useUiActions()
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
      {PLUGIN_CATALOG.map((p) => {
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

/** 展示当前 Agent 预设信息，无状态写入或请求。
 * Args: 无参数；只读取预设说明文案。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function AgentSection(): ReactElement {
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

/** 选择中英语言后更新共享设置，各分区通过翻译 hook 同步。
 * Args: 无参数；读取当前语言并提供切换动作。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function LanguageSection(): ReactElement {
  const { setUi } = useUiActions()
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

/** 选择浅色/深色/系统主题，经设置状态触发主题端口。
 * Args: 无参数；读取当前主题并提供切换动作。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function AppearanceSection(): ReactElement {
  const { setUi } = useUiActions()
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

/** 按设置分区选择对应面板，类型限制为已定义分区。
 * Args: 已定义的设置分区键、完整草稿、草稿更新回调。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function SectionContent({
  section,
  draft,
  setDraft,
}: {
  section: SectionKey
  draft: Draft
  setDraft: (d: Draft) => void
}): ReactElement {
  const panels: Record<SectionKey, () => ReactElement> = {
    general: () => <GeneralSection draft={draft} setDraft={setDraft} />,
    models: () => <ModelsSection />, vision: () => <VisionSection draft={draft} setDraft={setDraft} />,
    plugins: () => <PluginsSection />, agent: () => <AgentSection />,
    language: () => <LanguageSection />, appearance: () => <AppearanceSection />,
  }
  return panels[section]()
}

/** 为表单控件提供标签和内容布局，不执行表单提交。
 * Args: 用户可见标签与表单 children。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function Field({ label, children }: { label: string; children: React.ReactNode }): ReactElement {
  return (
    <div className="mb-3">
      <div className="mb-1 text-sm text-muted">{label}</div>
      {children}
    </div>
  )
}

/** 打开设置面板；侧栏折叠时仅显示图标。
 * Args: 可选 collapsed，控制只显示图标还是同时显示文字。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function SettingsEntry({ collapsed }: { collapsed?: boolean }): ReactElement {
  const { setUi } = useUiActions()
  const t = useT()
  return (
    <button
      onClick={() => setUi({ settingsOpen: true })}
      className="settings-entry flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-xs hoverable"
      title={t('nav.settings')}
    >
      <Icon name="settings" size={17} />
      {!collapsed && <span>{t('nav.settings')}</span>}
    </button>
  )
}

export const settingsPlugin: PluginManifest = {
  id: 'modforge-settings',
  name: '设置',
  apply(ctx: PluginContext): void {
    ctx.slots.inject(SLOTS.overlay, 'settings', () => <SettingsPanel />)
    ctx.slots.inject(SLOTS.sidebarFooter, 'settings-entry', (props: SlotProps) => <SettingsEntry collapsed={props?.collapsed} />, 10)
  },
}

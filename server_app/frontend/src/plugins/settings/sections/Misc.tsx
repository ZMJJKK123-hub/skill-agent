/**
 * 其余分区：视觉 API / 插件开关 / Agent / 语言 / 外观
 * （由 settings.tsx 原样迁出，开关用公共 Toggle 等价替换）。
 */
import { useT } from '../../../lib/i18n'
import { setUi, useUi } from '../../../lib/store'
import { composition } from '../../../composition'
import { Field, Toggle } from '../ui'
import type { Draft } from '../types'

export function VisionSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('vision.title')}</h2>
      <p className="mb-3 text-xs text-faint">{t('vision.hint')}</p>
      <Field label={t('vision.enabled')}>
        <Toggle on={draft.visionEnabled} onClick={() => setDraft({ ...draft, visionEnabled: !draft.visionEnabled })} />
      </Field>
      <Field label={t('vision.apiKey')}>
        <input
          type="password"
          value={draft.visionApiKey}
          onChange={(e) => setDraft({ ...draft, visionApiKey: e.target.value })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
      <Field label={t('vision.baseUrl')}>
        <input
          value={draft.visionBaseUrl}
          onChange={(e) => setDraft({ ...draft, visionBaseUrl: e.target.value })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
      <Field label={t('vision.model')}>
        <input
          value={draft.visionModel}
          onChange={(e) => setDraft({ ...draft, visionModel: e.target.value })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
    </div>
  )
}

export function PluginsSection() {
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
        // settings 与 sidebar 均为常驻插件：禁用 sidebar 会连设置入口一起
        // 藏掉（实测自锁缺陷），与 settings 一同锁定
        const locked = p.id === 'modforge-settings' || p.id === 'modforge-sidebar'
        return (
          <div key={p.id} className="mb-2 flex items-center justify-between rounded-md border border-line px-3 py-2 text-sm">
            <span>
              {p.name} <span className="text-faint">({p.id})</span>
            </span>
            {locked ? (
              <span className="text-xs text-faint">始终启用</span>
            ) : (
              <Toggle size="sm" on={!disabled} onClick={() => toggle(p.id)} />
            )}
          </div>
        )
      })}
    </div>
  )
}

export function AgentSection() {
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

export function LanguageSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold">{t('language.title')}</h2>
      <div className="space-y-2">
        {(['zh', 'en'] as const).map((id) => (
          <button
            key={id}
            onClick={() => setDraft({ ...draft, locale: id })}
            className={`block w-full rounded-md border px-3 py-2 text-left text-sm ${draft.locale === id ? 'border-forge-500/40 bg-forge-500/10 text-forge-300' : 'border-line text-muted hoverable'}`}
          >
            {id === 'zh' ? t('language.zh') : t('language.en')}
          </button>
        ))}
      </div>
    </div>
  )
}

export function AppearanceSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  const options: { id: Draft['theme']; label: string }[] = [
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
            onClick={() => setDraft({ ...draft, theme: o.id })}
            className={`flex-1 rounded-md border px-3 py-2 text-sm ${draft.theme === o.id ? 'border-forge-500/40 bg-forge-500/10 text-forge-300' : 'border-line text-muted hoverable'}`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}

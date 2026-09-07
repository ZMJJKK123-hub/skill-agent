/**
 * 通用分区：游戏/加载器/版本/沙箱/全自动/搜索 Key（由 settings.tsx 原样迁出）。
 */
import { useT } from '../../../lib/i18n'
import { Field, Toggle } from '../ui'
import { LOADERS, VERSIONS, type Draft } from '../types'

export function GeneralSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
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
      <Field label={t('general.sandbox')}>
        <select
          value={draft.sandbox}
          onChange={(e) => setDraft({ ...draft, sandbox: e.target.value as Draft['sandbox'] })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        >
          <option value="full-access">{t('general.sandbox.full')}</option>
          <option value="workspace-write">{t('general.sandbox.workspace')}</option>
          <option value="read-only">{t('general.sandbox.readonly')}</option>
        </select>
      </Field>
      <Field label={t('general.autoMode')}>
        <Toggle on={draft.autoMode} onClick={() => setDraft({ ...draft, autoMode: !draft.autoMode })} />
        <p className="mt-1 text-xs text-faint">{t('general.autoModeDesc')}</p>
      </Field>
      <Field label="Tavily Search API Key">
        <input
          type="password"
          value={draft.searchApiKey}
          onChange={(e) => setDraft({ ...draft, searchApiKey: e.target.value })}
          className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
        />
      </Field>
    </div>
  )
}

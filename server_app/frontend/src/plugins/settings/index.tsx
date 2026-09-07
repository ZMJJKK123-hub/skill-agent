/**
 * 设置插件入口：面板挂 overlay 槽、入口按钮挂侧栏底槽。
 * 实现见 ./SettingsPanel.tsx 与 ./sections/（由 settings.tsx 拆分）。
 */
import { PluginManifest, SLOTS } from '../../shell/registry'
import { setUi } from '../../lib/store'
import { useT } from '../../lib/i18n'
import { SettingsPanel } from './SettingsPanel'

function SettingsEntry({ collapsed }: { collapsed?: boolean }) {
  const t = useT()
  // 此前渲染两个并排"设置"文本（用户实测指出），只保留一个并居中。
  return (
    <button
      onClick={() => setUi({ settingsOpen: true })}
      className="flex w-full items-center justify-center rounded px-2 py-1.5 text-sm hoverable"
      title={t('nav.settings')}
    >
      <span>{t('nav.settings')}</span>
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

// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// 本分区样式仅在当前分区模块加载时挂载。
import '../css/generation.css'
// 类型契约约束分区间的数据和组件通信。
import type { PluginManifest, PluginContext } from '../../../assets/js/slots.types.ts'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 翻译 hook 为本分区提供当前语言文案。
import { useT } from '../../../assets/js/i18n.ts'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useSession, useUi } from '../../../assets/js/application-context.tsx'
// 详情卡片与其他分区使用相同图标。
import { Icon } from '../../../assets/js/icons.tsx'

/** 展示当前生成模式、运行阶段、耗时和会话信息，无独立轮询。
 * Args: 无参数；读取当前会话阶段、模式、耗时和 ID。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function GeneratePanel(): ReactElement {
  const t = useT()
  const sess = useSession()
  const { phase, elapsed, sessionId, mode } = sess
  const { version } = useUi()
  const status = { idle: t('studio.ready'), creating: t('conv.starting'), running: t('conv.running'), paused: t('conv.pause'), finished: t('studio.finished'), error: t('conv.failed') }[phase]

  return (
    <div className="generation-details">
      <div className="generation-status-card" data-phase={phase}><span className="generation-icon"><Icon name="cube" size={24} /></span><span className="eyebrow">MOD FORGE</span><h2>{status}</h2><span className="generation-status-label"><span className="status-dot" />{mode === 'mod' ? t('studio.modMode') : t('studio.chatMode')}</span></div>
      <div className="generation-metrics text-muted">
        <div className="flex justify-between">
          <span>{t('studio.version')}</span><span>Minecraft {version}</span>
        </div>
        <div className="flex justify-between">
          <span>{t('studio.elapsed')}</span>
          <span>{elapsed !== null ? `${elapsed}s` : '—'}</span>
        </div>
        <div className="flex justify-between">
          <span>{t('studio.mode')}</span>
          <span>{mode === 'mod' ? t('studio.modMode') : mode === 'chat' ? t('studio.chatMode') : '—'}</span>
        </div>
        <div className="flex justify-between">
          <span>ID</span>
          <span>{sessionId ? sessionId.slice(0, 8) + '…' : '—'}</span>
        </div>
      </div>
      <p className="generation-hint">{t('conv.desc')}</p>
    </div>
  )
}

export const generatePlugin: PluginManifest = {
  id: 'modforge-generate',
  name: '生成监控',
  apply(ctx: PluginContext): void {
    ctx.slots.inject(SLOTS.details, 'generate', () => <GeneratePanel />)
  },
}

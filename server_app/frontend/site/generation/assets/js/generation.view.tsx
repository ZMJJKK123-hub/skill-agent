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
import { useSession } from '../../../assets/js/application-context.tsx'

/** 展示当前生成模式、运行阶段、耗时和会话信息，无独立轮询。
 * Args: 无参数；读取当前会话阶段、模式、耗时和 ID。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function GeneratePanel(): ReactElement {
  const t = useT()
  const sess = useSession()
  const { phase, elapsed, sessionId, mode } = sess

  return (
    <div className="p-4">
      <h2 className="mb-3 text-sm font-semibold">{t('conv.section')}</h2>
      <div className="space-y-2 text-sm text-muted">
        <div className="flex justify-between">
          <span>{t('nav.sessions')}</span>
          <span className={phase === 'running' ? 'text-forge-400' : phase === 'finished' ? 'text-emerald-400' : 'text-faint'}>
            {phase === 'running' ? t('conv.running') : phase === 'finished' ? t('conv.done') : '—'}
          </span>
        </div>
        <div className="flex justify-between">
          <span>{t('conv.running')}</span>
          <span className="text-faint">{elapsed ? `${elapsed}s` : '—'}</span>
        </div>
        <div className="flex justify-between">
          <span>模式</span>
          <span className="text-faint">{mode === 'mod' ? 'MOD 制作' : mode === 'chat' ? '普通对话' : '—'}</span>
        </div>
        <div className="flex justify-between">
          <span>ID</span>
          <span className="text-faint">{sessionId ? sessionId.slice(0, 8) + '…' : '—'}</span>
        </div>
      </div>
      <p className="mt-2 text-xs text-faint">模组制作完成后，可在对话底部下载模组和源码。</p>
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

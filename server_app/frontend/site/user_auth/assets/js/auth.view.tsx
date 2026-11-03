// ReactElement 显式标注组件返回契约，避免视图函数隐式返回类型。
import type { ReactElement } from 'react'
// React hooks 用于组件状态、订阅和生命周期。
import { useEffect, useState } from 'react'
// 类型契约约束分区间的数据和组件通信。
import type { PluginManifest, PluginContext } from '../../../assets/js/slots.types.ts'
// 命名槽位让本分区只注册自己使用的界面。
import { SLOTS } from '../../../assets/js/slots.ts'
// 通过当前应用 Context 获取状态和注入的控制器。
import { useUi, useAuthActions } from '../../../assets/js/application-context.tsx'
// 翻译 hook 为本分区提供当前语言文案。
import { useT } from '../../../assets/js/i18n.ts'
// 本分区样式仅在当前分区模块加载时挂载。
import '../css/user_auth.css'

/** 显示账户入口并恢复既有登录态；网络失败保留令牌，退出由认证控制器清理账户。
 * Args: 无参数；读取当前用户与认证控制器。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function AuthButton(): ReactElement {
  const auth = useAuthActions()
  const { user } = useUi()
  const t = useT()
  const [open, setOpen] = useState(false)

  useEffect(() => { void auth.restore() }, [auth])

  const onLogout = async (): Promise<void> => { await auth.logout() }

  return (
    <>
      {user ? (
        <button onClick={onLogout} title={t('auth.logout')} className="hoverable rounded-md border border-strong px-3 py-1 text-sm">
          {user.username}
        </button>
      ) : (
        <button onClick={() => setOpen(true)} className="hoverable rounded-md border border-strong px-3 py-1 text-sm">
          {t('auth.login')}
        </button>
      )}
      {open && <AuthModal onClose={() => setOpen(false)} />}
    </>
  )
}

/** 提供登录/注册表单；空输入本地报错，提交失败在弹窗显示原因，成功关闭。
 * Args: 成功或点击遮罩时调用的关闭回调。
 * Returns: React 展示元素。
 * Globals Used: 当前应用 Context（纯展示辅助函数无状态依赖）。Calls/Dependencies: 本文件显式导入的 React hooks、类型化动作和展示组件。
 */
function AuthModal({ onClose }: { onClose: () => void }): ReactElement {
  const auth = useAuthActions()
  const t = useT()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async () => {
    if (!username.trim() || !password) {
      setError(t('auth.fill'))
      return
    }
    setBusy(true)
    setError('')
    try {
      await auth[mode](username.trim(), password)
      onClose()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-80 rounded-xl border border-strong bg-panel p-5" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex gap-2">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 rounded-md py-1.5 text-sm ${mode === 'login' ? 'bg-forge-500 text-ink-950' : 'bg-subtle'}`}
          >
            {t('auth.login')}
          </button>
          <button
            onClick={() => setMode('register')}
            className={`flex-1 rounded-md py-1.5 text-sm ${mode === 'register' ? 'bg-forge-500 text-ink-950' : 'bg-subtle'}`}
          >
            {t('auth.register')}
          </button>
        </div>
        <div className="space-y-2">
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder={t('auth.username')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder={t('auth.password')}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
            className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
          />
          {error && <div className="text-xs text-red-400">{error}</div>}
          <button onClick={submit} disabled={busy} className="w-full rounded-md bg-forge-500 py-2 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-50">
            {busy ? t('auth.submitting') : mode === 'login' ? t('auth.login') : t('auth.registerLogin')}
          </button>
        </div>
      </div>
    </div>
  )
}

export const authPlugin: PluginManifest = {
  id: 'modforge-auth',
  name: '登录/注册',
  apply(ctx: PluginContext): void {
    ctx.slots.inject(SLOTS.headerActions, 'auth', () => <AuthButton />)
  },
}

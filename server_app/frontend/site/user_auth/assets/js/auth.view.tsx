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
// 登录入口和弹窗沿用共享品牌图标。
import { Icon } from '../../../assets/js/icons.tsx'

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
        <button onClick={onLogout} title={t('auth.logout')} className="auth-entry auth-account">
          <span className="account-avatar">{user.username.slice(0, 1).toUpperCase()}</span><span>{user.username}</span>
        </button>
      ) : (
        <button onClick={() => setOpen(true)} className="auth-entry">
          <Icon name="login" size={15} />{t('auth.login')}
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
    <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div role="dialog" aria-modal="true" aria-labelledby="auth-heading" className="auth-dialog surface-dialog border border-strong bg-panel" onKeyDown={(event) => { if (event.key === 'Escape') onClose() }} onClick={(e) => e.stopPropagation()}>
        <button className="auth-close icon-button" title={t('studio.close')} aria-label={t('studio.close')} onClick={onClose}><Icon name="close" size={17} /></button>
        <div className="auth-brand-mark"><Icon name="cube" size={30} /></div>
        <h2 id="auth-heading">{t('studio.authTitle')}</h2><p className="auth-description">{t('studio.authDesc')}</p>
        <div className="auth-tabs flex gap-1">
          <button
            onClick={() => setMode('login')}
            aria-pressed={mode === 'login'}
            className="flex-1 rounded-md py-2 text-sm"
          >
            {t('auth.login')}
          </button>
          <button
            onClick={() => setMode('register')}
            aria-pressed={mode === 'register'}
            className="flex-1 rounded-md py-2 text-sm"
          >
            {t('auth.register')}
          </button>
        </div>
        <div className="auth-fields">
          <label htmlFor="auth-username">{t('auth.username')}</label>
          <input id="auth-username" autoFocus autoComplete="username" value={username} onChange={(e) => setUsername(e.target.value)} placeholder={t('auth.username')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
          <label htmlFor="auth-password">{t('auth.password')}</label>
          <input
            id="auth-password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder={t('auth.password')}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
            className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500"
          />
          {error && <div role="alert" className="auth-error text-xs text-red-400">{error}</div>}
          <button onClick={submit} disabled={busy} className="auth-submit primary-button w-full py-2.5 text-sm">
            {busy ? t('auth.submitting') : mode === 'login' ? t('auth.login') : t('auth.registerLogin')}
          </button>
        </div>
        <p className="auth-footnote">{t('studio.authFootnote')}</p>
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

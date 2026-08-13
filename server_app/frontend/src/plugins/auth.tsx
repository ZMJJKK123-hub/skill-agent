import { useEffect, useState } from 'react'
import { PluginManifest, SLOTS } from '../shell/registry'
import { setUi, useUi } from '../lib/store'
import { useT } from '../lib/i18n'
import * as api from '../lib/api'

function AuthButton() {
  const { user } = useUi()
  const t = useT()
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (api.getToken()) {
      api
        .me()
        .then((r) => setUi({ user: { username: r.username } }))
        .catch(() => api.clearToken())
    }
  }, [])

  const onLogout = async () => {
    try {
      await api.logout()
    } catch {
      /* token 已失效也照常清理本地态 */
    }
    api.clearToken()
    setUi({ user: null })
  }

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

function AuthModal({ onClose }: { onClose: () => void }) {
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
      const res = mode === 'login' ? await api.login(username.trim(), password) : await api.register(username.trim(), password)
      api.setToken(res.token)
      setUi({ user: { username: res.username } })
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
  apply(ctx) {
    ctx.slots.inject(SLOTS.headerActions, 'auth', () => <AuthButton />)
  },
}

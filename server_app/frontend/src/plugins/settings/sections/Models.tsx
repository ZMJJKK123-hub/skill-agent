/**
 * 模型提供方分区：增删改 provider、模型 ID chip 增删、视觉支持开关
 * （由 settings.tsx 原样迁出，开关用公共 Toggle 等价替换）。
 */
import { useState } from 'react'
import { useT } from '../../../lib/i18n'
import type { Provider } from '../../../lib/store'
import { Toggle } from '../ui'
import type { Draft } from '../types'

const VISION_HINT = '模型支持图片输入（开启后主模型直接用于视觉识别，无需单独配视觉 API）'

export function ModelsSection({ draft, setDraft }: { draft: Draft; setDraft: (d: Draft) => void }) {
  const t = useT()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', baseUrl: '', apiKey: '', model: '', protocol: 'openai', supportsVision: false })
  // 编辑态：editId = 正在编辑的 provider；模型 ID 以 chip 形式逐个增删
  const [editId, setEditId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState({ name: '', baseUrl: '', apiKey: '', supportsVision: false })
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
      supportsVision: form.supportsVision,
    }
    // 官方默认移除后 model 无兜底：新增后若无可用选中模型，自动选中新
    // provider 的第一个模型（否则下拉停留在"暂无配置"）
    const nextProviders = [...providers, p]
    const modelKnown = nextProviders.some((x) =>
      x.model.split(',').map((s) => s.trim()).includes(draft.model),
    )
    setDraft({
      ...draft,
      providers: nextProviders,
      model: modelKnown && draft.model
        ? draft.model
        : p.model.split(',').map((s) => s.trim()).filter(Boolean)[0] || '',
    })
    setForm({ name: '', baseUrl: '', apiKey: '', model: '', protocol: 'openai', supportsVision: false })
    setShowForm(false)
  }
  const remove = (id: string) => {
    const nextProviders = providers.filter((p) => p.id !== id)
    const modelKnown = nextProviders.some((x) =>
      x.model.split(',').map((s) => s.trim()).includes(draft.model),
    )
    setDraft({
      ...draft,
      providers: nextProviders,
      // 删空/删中所选：回退剩余第一个可用模型，全空则"暂无配置"
      model: modelKnown ? draft.model : (nextProviders[0]
        ? nextProviders[0].model.split(',').map((s) => s.trim()).filter(Boolean)[0] || ''
        : ''),
    })
  }

  const startEdit = (p: Provider) => {
    setEditId(p.id)
    setEditForm({ name: p.name, baseUrl: p.baseUrl, apiKey: p.apiKey, supportsVision: !!p.supportsVision })
    setNewModel('')
  }
  const applyEdit = () => {
    if (!editId) return
    setDraft({
      ...draft,
      providers: providers.map((p) =>
        p.id === editId ? { ...p, name: editForm.name.trim(), baseUrl: editForm.baseUrl.trim(), apiKey: editForm.apiKey.trim(), supportsVision: editForm.supportsVision } : p,
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
      {providers.length === 0 && <div className="mb-2 px-1 text-xs text-faint">{t('models.empty')}</div>}
      {providers.map((p) =>
        editId === p.id ? (
          <div key={p.id} className="mb-2 space-y-2 rounded-md border border-forge-500/40 bg-forge-500/5 p-3 text-sm">
            <div className="text-xs font-medium text-forge-300">编辑提供方</div>
            <input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} placeholder={t('models.name')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
            <input value={editForm.baseUrl} onChange={(e) => setEditForm({ ...editForm, baseUrl: e.target.value })} placeholder={t('models.baseUrl')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
            <input value={editForm.apiKey} onChange={(e) => setEditForm({ ...editForm, apiKey: e.target.value })} type="password" placeholder={t('models.apiKey')} className="w-full rounded-md border border-line bg-field px-3 py-2 text-sm outline-none focus:border-forge-500" />
            <label className="flex items-center gap-2 text-xs text-muted">
              <Toggle size="sm" on={editForm.supportsVision} onClick={() => setEditForm({ ...editForm, supportsVision: !editForm.supportsVision })} />
              {VISION_HINT}
            </label>
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
              <div className="font-medium">
                {p.name}
                {p.supportsVision && (
                  <span className="ml-1.5 rounded border border-forge-500/40 bg-forge-500/10 px-1 py-px text-[10px] text-forge-300">视觉</span>
                )}
              </div>
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
          <label className="flex items-center gap-2 text-xs text-muted">
            <Toggle size="sm" on={form.supportsVision} onClick={() => setForm({ ...form, supportsVision: !form.supportsVision })} />
            {VISION_HINT}
          </label>
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

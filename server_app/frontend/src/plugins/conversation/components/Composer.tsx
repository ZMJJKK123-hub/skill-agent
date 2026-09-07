/**
 * 输入区：斜杠命令面板 + 图片附件（选/贴/拖）+ 发送/暂停/继续 +
 * /mod 应用内确认条 + 模型快切下拉。由 conversation.tsx 原样迁出。
 */
import { useEffect, useRef, useState } from 'react'
import { useUi, setUi, resolveModelConfig, hasModelConfig } from '../../../lib/store'
import { useT } from '../../../lib/i18n'
import { useSession, sendPrompt, pauseTask, resumeTask } from '../../../lib/session'
import { QuestionCard } from './QuestionCard'
import { ModConfirmBar } from './ModConfirmBar'
import { SendControls } from './SendControls'
import { UploadThumbStrip, handleTextareaKey } from './InputDecorations'
import { SlashPalette } from './SlashPalette'
import { MAX_IMAGES_PER_MESSAGE, fileToDataUrl } from '../lib/imageInput'

/** '/' 命令面板条目 */
const SLASH_COMMANDS = [
  { cmd: '/mod', desc: '进入 MOD 制作模式：发送需求后开始构建' },
  { cmd: '/chat', desc: '切换到对话模式：MOD 会话中回到纯聊天（默认）' },
]

export function Composer() {
  const { model, providers, version, sandbox, visionEnabled, visionApiKey, visionBaseUrl, visionModel, autoMode, searchApiKey } = useUi()
  const t = useT()
  const sess = useSession()
  const [text, setText] = useState('')
  const [images, setImages] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  // /mod 应用内确认：原生 confirm 在"禁止再弹窗"环境形同虚设，改状态浮层
  const [modConfirm, setModConfirm] = useState<string | null>(null)
  const [modImages, setModImages] = useState<string[]>([])
  const running = sess.phase === 'running' || sess.phase === 'creating'
  const paused = sess.phase === 'paused' || sess.paused

  useEffect(() => {
    const onPrefill = (e: Event) => {
      const detail = (e as CustomEvent<string>).detail || ''
      setText(detail)
      ;(document.querySelector('main textarea') as HTMLTextAreaElement | null)?.focus()
    }
    window.addEventListener('modforge:prefill', onPrefill)
    return () => window.removeEventListener('modforge:prefill', onPrefill)
  }, [])

  const [dragOver, setDragOver] = useState(false)

  const [cmdOpen, setCmdOpen] = useState(false)
  const [cmdIndex, setCmdIndex] = useState(0)
  const cmdFiltered = SLASH_COMMANDS.filter((c) => c.cmd.startsWith(text.trim()))
  // 面板开合由输入事件直接控制（applyCommand 后 setText('/mod ') 仍以 '/'
  // 开头，effect 会重新弹开面板——实测：选中后关不上）
  const onTextInput = (v: string) => {
    setText(v)
    const matches = SLASH_COMMANDS.filter((c) => c.cmd.startsWith(v.trim()))
    setCmdOpen(v.startsWith('/') && matches.length > 0)
    setCmdIndex(0)
  }

  const applyCommand = (cmd: string) => {
    setText(cmd + ' ')
    setCmdOpen(false)
    setCmdIndex(0)
    ;(document.querySelector('main textarea') as HTMLTextAreaElement | null)?.focus()
  }

  const addImageFiles = async (files: File[]) => {
    const pics = files.filter((f) => f.type.startsWith('image/'))
    if (pics.length === 0) return
    const room = MAX_IMAGES_PER_MESSAGE - images.length
    if (pics.length > room) alert(t('conv.tooManyImages'))
    if (room <= 0) return
    const encoded: string[] = []
    for (const f of pics.slice(0, room)) {
      try {
        encoded.push(await fileToDataUrl(f))
      } catch {
        /* 单张解析失败跳过 */
      }
    }
    if (encoded.length > 0) setImages((prev) => [...prev, ...encoded])
  }

  // 发送重入防护：第一次 send 尚未把 phase 切到 running（网络往返中）时，
  // 双击/回车+点击的第二次触发会重发同一条（实测：两个相同气泡+重复排队）
  const sendingRef = useRef(false)
  const buildSettings = () => {
    const r = resolveModelConfig({ model, providers })
    return {
      apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game: 'minecraft', loader: 'forge', version, sandbox,
      // 主模型支持图片输入时直接用作视觉模型，不强制单独视觉 API
      visionEnabled: visionEnabled || r.supportsVision,
      visionApiKey: r.supportsVision ? (visionApiKey || r.apiKey) : visionApiKey,
      visionBaseUrl: r.supportsVision ? (visionBaseUrl || r.baseUrl) : visionBaseUrl,
      visionModel: r.supportsVision ? (visionModel || r.model) : visionModel,
      autoMode, searchApiKey,
    }
  }
  const send = () => {
    if (sendingRef.current) return
    const prompt = text.trim()
    if (!prompt && images.length === 0) return
    const settings = buildSettings()
    // /chat 拦截：显式切回对话模式（force_mode 让 server 不沿用 mod 记忆）
    if (/^\/chat(\s|$)/i.test(prompt)) {
      const chatPrompt = prompt.slice(5).trim()
      if (!chatPrompt) {
        alert('用法：/chat <内容> —— 切换到对话模式并发送。MOD 会话中用它可退出制作模式回到纯聊天。')
        return
      }
      if (running) {
        alert('当前任务运行中，请等本轮完成后再用 /chat 切换模式。')
        return
      }
      setUi({ toast: '已切换到对话模式' })
      sendingRef.current = true
      void sendPrompt(chatPrompt, settings, 'chat', images, true).finally(() => { sendingRef.current = false })
      setText('')
      setImages([])
      return
    }
    // /mod 拦截（大小写不敏感——/MOD /Mod 同样生效）
    if (/^\/mod(\s|$)/i.test(prompt)) {
      const modPrompt = prompt.slice(4).trim()
      if (!modPrompt) {
        alert('用法：/mod <你的 MOD 需求描述>，例如：/mod 做一把钻石剑')
        return
      }
      setModConfirm(modPrompt)
      setModImages(images)
      return
    }
    // 普通消息：mod 会话沿用 mod 模式（防迭代需求被降级成只读咨询）
    sendingRef.current = true
    void sendPrompt(prompt, settings, sess.mode === 'mod' ? 'mod' : 'chat', images).finally(() => { sendingRef.current = false })
    setText('')
    setImages([])
  }

  const confirmMod = () => {
    if (!modConfirm || sendingRef.current) return
    sendingRef.current = true
    void sendPrompt(modConfirm, buildSettings(), 'mod', modImages).finally(() => { sendingRef.current = false })
    setModConfirm(null)
    setModImages([])
    setText('')
    setImages([])
  }

  const canChat = hasModelConfig({ model, providers })
  const notReadyReason = canChat ? '' : t('conv.noModel')

  return (
    <div className="mx-auto w-full max-w-4xl">
      <QuestionCard />
      {modConfirm && (
        <ModConfirmBar
          prompt={modConfirm}
          onConfirm={confirmMod}
          onCancel={() => setModConfirm(null)}
        />
      )}
      <div
        className={`relative rounded-xl border bg-panel p-3 transition-colors ${dragOver ? 'border-forge-500' : 'border-line'}`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith('image/'))
          if (files.length > 0) void addImageFiles(files)
        }}
      >
        {cmdOpen && (
          <SlashPalette
            commands={cmdFiltered}
            index={cmdIndex}
            onApply={applyCommand}
            onHover={setCmdIndex}
          />
        )}
        <UploadThumbStrip images={images} onRemove={(i) => setImages((prev) => prev.filter((_, j) => j !== i))} />
        <textarea
          value={text}
          onChange={(e) => onTextInput(e.target.value)}
          onPaste={(e) => {
            const files = Array.from(e.clipboardData.files).filter((f) => f.type.startsWith('image/'))
            if (files.length > 0) {
              e.preventDefault()
              void addImageFiles(files)
            }
          }}
          onKeyDown={(e) =>
            handleTextareaKey(e, {
              cmdOpen,
              cmdCount: cmdFiltered.length,
              onCmdIndex: setCmdIndex,
              onApplyCmd: () => applyCommand(cmdFiltered[cmdIndex].cmd),
              onCloseCmd: () => setCmdOpen(false),
              onSend: send,
              canSend: Boolean(text.trim()) || images.length > 0,
            })
          }
          rows={3}
          disabled={!canChat}
          placeholder={canChat ? (sess.mode === 'mod' ? t('conv.placeholderMod') : t('conv.placeholder')) : t('conv.configureFirst')}
          className="w-full resize-none bg-transparent text-sm outline-none placeholder:text-faint disabled:opacity-60"
        />
        <div className="mt-2 flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => {
              void addImageFiles(Array.from(e.target.files ?? []))
              e.target.value = '' // 允许重复选择同一张
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={!canChat}
            title={t('conv.attach')}
            className="flex h-7 w-7 items-center justify-center rounded-md border border-line text-muted hoverable disabled:opacity-50"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
            </svg>
          </button>
          <select
            value={model}
            onChange={(e) => setUi({ model: e.target.value })}
            disabled={!canChat}
            title={canChat ? '' : t('conv.noModel')}
            className="rounded-md border border-line bg-field px-2 py-1 text-xs text-muted outline-none disabled:opacity-50"
          >
            {canChat ? (
              providers.map((p) => (
                <optgroup key={p.id} label={p.name}>
                  {p.model.split(',').map((m) => m.trim()).filter(Boolean).map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </optgroup>
              ))
            ) : (
              <option value="">{t('conv.noModelShort')}</option>
            )}
          </select>
          <div className="flex-1" />
          {/* 发送后 3.5s 内不显示排队徽标（防空闲发送的 pending=1 闪现） */}
          {running && sess.pending > 0 && Date.now() - (sess.lastSendAt ?? 0) > 3500 && (
            <span className="text-xs text-faint">{sess.pending} 条排队…</span>
          )}
          <SendControls
            running={running}
            paused={paused}
            disabled={(!text.trim() && images.length === 0) || !canChat}
            title={canChat ? '' : notReadyReason}
            onSend={send}
            onPause={pauseTask}
            onResume={resumeTask}
          />
        </div>
      </div>
    </div>
  )
}

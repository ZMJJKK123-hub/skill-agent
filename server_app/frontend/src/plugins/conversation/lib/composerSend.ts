/**
 * 输入区发送分发（由 Composer.tsx 拆出）：/chat、/mod 命令拦截与
 * 普通消息三路分发 + mod 确认发送。纯逻辑，副作用通过 ctx 回调注入。
 */
import { setUi } from '../../../lib/store'
import { sendPrompt } from '../../../lib/session'

/** 分发结果：UI 状态如何变化（调用方据此清空输入/附件或弹确认条） */
export type SendOutcome =
  | { kind: 'sent'; promise: Promise<unknown> }
  | { kind: 'mod-confirm'; prompt: string }
  | { kind: 'rejected' }

export interface SendCtx {
  running: boolean
  mode: 'chat' | 'mod' | null
  buildSettings: () => Record<string, unknown>
  send: (prompt: string, settings: Record<string, unknown>, mode: 'chat' | 'mod', images: string[], forceMode?: boolean) => Promise<unknown>
}

/** 三路分发：/chat 显式切换、/mod 确认条、普通消息沿用会话模式 */
export function dispatchSend(promptRaw: string, images: string[], ctx: SendCtx): SendOutcome {
  const prompt = promptRaw.trim()
  if (!prompt && images.length === 0) return { kind: 'rejected' }
  const settings = ctx.buildSettings()
  // /chat 拦截：显式切回对话模式（force_mode 让 server 不沿用 mod 记忆）
  if (/^\/chat(\s|$)/i.test(prompt)) {
    const chatPrompt = prompt.slice(5).trim()
    if (!chatPrompt) {
      alert('用法：/chat <内容> —— 切换到对话模式并发送。MOD 会话中用它可退出制作模式回到纯聊天。')
      return { kind: 'rejected' }
    }
    if (ctx.running) {
      alert('当前任务运行中，请等本轮完成后再用 /chat 切换模式。')
      return { kind: 'rejected' }
    }
    setUi({ toast: '已切换到对话模式' })
    return { kind: 'sent', promise: Promise.resolve(ctx.send(chatPrompt, settings, 'chat', images, true)) }
  }
  // /mod 拦截（大小写不敏感——/MOD /Mod 同样生效）
  if (/^\/mod(\s|$)/i.test(prompt)) {
    const modPrompt = prompt.slice(4).trim()
    if (!modPrompt) {
      alert('用法：/mod <你的 MOD 需求描述>，例如：/mod 做一把钻石剑')
      return { kind: 'rejected' }
    }
    return { kind: 'mod-confirm', prompt: modPrompt }
  }
  // 普通消息：mod 会话沿用 mod 模式（防迭代需求被降级成只读咨询）
  return { kind: 'sent', promise: Promise.resolve(ctx.send(prompt, settings, ctx.mode === 'mod' ? 'mod' : 'chat', images)) }
}

/** mod 确认条「确认开始」：以 mod 模式发送暂存的需求 */
export function dispatchModConfirm(prompt: string, images: string[], ctx: SendCtx): Promise<unknown> | null {
  if (!prompt) return null
  return Promise.resolve(ctx.send(prompt, ctx.buildSettings(), 'mod', images))
}

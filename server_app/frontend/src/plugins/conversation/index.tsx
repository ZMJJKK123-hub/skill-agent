/**
 * 对话插件入口：装配 Messages 与 Composer 到对应槽位。
 * 组件实现见 ./Messages.tsx 与 ./components/（由 conversation.tsx 拆分）。
 */
import { PluginManifest, SLOTS } from '../../shell/registry'
import { Messages } from './Messages'
import { Composer } from './components/Composer'

export const conversationPlugin: PluginManifest = {
  id: 'modforge-conversation',
  name: '对话',
  apply(ctx) {
    ctx.slots.inject(SLOTS.conversationMessages, 'messages', () => <Messages />)
    ctx.slots.inject(SLOTS.conversationComposer, 'composer', () => <Composer />)
  },
}

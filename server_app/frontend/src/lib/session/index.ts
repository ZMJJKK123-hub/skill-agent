/**
 * 会话编排入口（由 lib/session.ts 拆分）。
 *
 * 组成：store（状态存储）/ actions（动作）/ polling（轮询）。
 * 公共 API 原样再导出——`from '../lib/session'` 的既有导入零改动。
 */
export { useSession, state, setState, type SessionState, type GenSettings } from './store'
export {
  loadHistory, sendPrompt, pauseTask, resumeTask, loadConversation,
  answerQuestion, newConversation, openHistorySession, regenerate,
} from './actions'
export { poll, startPolling, stopPolling } from './polling'
import { ACTIVE_SID_KEY } from './store'
import { openHistorySession } from './actions'

// 刷新恢复：模块加载时若本标签页 remembers 一个活动会话，自动恢复其视图
// （运行中的任务由 poll 探测接管；已删除的会话回空态）。
try {
  const _sid = sessionStorage.getItem(ACTIVE_SID_KEY)
  if (_sid) void openHistorySession(_sid)
} catch {
  /* sessionStorage 不可用时忽略 */
}

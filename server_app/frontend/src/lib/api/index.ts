/**
 * 后端 API 封装入口（由 lib/api.ts 拆分）。
 *
 * 组成：client（HTTP 基础）/ types（响应类型）/ endpoints（端点函数）。
 * 公共 API 原样再导出——`from '../lib/api'` 的既有导入零改动。
 */
export { getToken, setToken, clearToken } from './client'
export {
  createSession, resetSession, deleteSession, prepareModWorkspace,
  getConversation, sessionImageUrl, startTask, pauseTask, getStatus,
  getResult, getEvents, getHistory, getSessions, getQuestion,
  answerQuestion, answerQuestions, getGames, downloadJar, downloadSourceZip,
} from './endpoints'
export type {
  SessionStats, StatusResponse, EventItem, EventsResponse, HistoryEntry,
  GameInfo, ConversationMessage, QuestionItem, Question,
} from './types'

// 容器提供 React 无关的快照与订阅。
import { createStateStore } from '../../../assets/js/state-store.ts'
// 初始状态由纯模型创建，确保不同应用实例不会共享消息。
import { emptySession } from './session.model.ts'
// 仅暴露类型化状态边界。
import type { SessionStore } from './session.types.ts'

/** 创建独立会话状态；不读取浏览器存储、不启动轮询，无全局依赖。 */
export function createSessionStore(): SessionStore { return createStateStore(emptySession()) }

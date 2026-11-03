// 状态接口让业务控制器和 React 订阅层共用契约，不互相依赖。
import type { StateListener, StateStore } from './contracts.ts'

/** 创建独立状态容器。
 * Args: initial 是本实例初始状态。Returns: 快照、浅合并和可解绑订阅接口。
 * 每次 set 替换快照；解绑后不再通知。Globals Used: None。Dependencies: Set。
 */
export function createStateStore<T extends object>(initial: T): StateStore<T> {
  let state: T = initial
  const listeners: Set<StateListener> = new Set()
  return {
    getSnapshot: (): T => state,
    set(patch): void {
      state = { ...state, ...patch }
      listeners.forEach((listener: StateListener): void => listener())
    },
    subscribe(listener): () => void {
      listeners.add(listener)
      return (): void => { listeners.delete(listener) }
    },
  }
}

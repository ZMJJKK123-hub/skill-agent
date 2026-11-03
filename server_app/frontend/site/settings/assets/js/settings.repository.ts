// 浏览器存储与日志通过接口注入，测试可替换为内存实现。
import type { Logger, StoragePort } from '../../../assets/js/contracts.ts'
// 仓储只负责持久化；字段恢复由纯计算模型完成。
import type { SavedSettings, SettingsRepository } from './settings.types.ts'
// 错误分类禁止把存储中的 Key 或完整 JSON 输出到日志。
import { errorType } from '../../../assets/js/errors.ts'

/** 创建设置仓储；key 沿用 modforge_ui。
 * 存储不可用或 JSON 损坏时 load 返回 null，save 记录诊断后保留内存中的设置。
 * Globals Used: None。Dependencies: 注入的 storage/logger、JSON。
 */
export function createSettingsRepository(storage: StoragePort, key: string, logger: Logger): SettingsRepository {
  return {
    load(): unknown {
      try { const raw = storage.getItem(key); return raw ? JSON.parse(raw) as unknown : null }
      catch (error: unknown) { logger.write('warning', 'settings.load_failed', { errorType: errorType(error) }); return null }
    },
    save(settings: SavedSettings): void {
      try { storage.setItem(key, JSON.stringify(settings)) }
      catch (error: unknown) { logger.write('warning', 'settings.save_failed', { errorType: errorType(error) }) }
    },
  }
}

// 浏览器端口契约与业务实现解耦。
import type { DownloadPort, LogEntry, StoragePort, ThemePort, TimerPort } from '../../../assets/js/contracts.ts'

/** 适配浏览器能力；只在入口调用，不在模块导入时访问 window。
 * Args: 当前窗口与文档。Returns: 存储、计时器、下载、主题和诊断事件端口。
 * 主题订阅可销毁；下载 URL 延迟释放。Globals Used: None。Dependencies: 注入 Window/Document。
 */
export function createBrowserAdapters(browser: Window, document: Document): {
  storage: StoragePort; timer: TimerPort; downloads: DownloadPort; theme: ThemePort; log(entry: LogEntry): void
} {
  const media = browser.matchMedia('(prefers-color-scheme: light)')
  let preference: 'system' | 'light' | 'dark' = 'dark'
  const renderTheme = (): void => { document.documentElement.dataset.theme = preference === 'system' ? media.matches ? 'light' : 'dark' : preference }
  media.addEventListener('change', renderTheme)
  return {
    storage: {
      getItem: (key: string): string | null => browser.localStorage.getItem(key),
      setItem: (key: string, value: string): void => browser.localStorage.setItem(key, value),
      removeItem: (key: string): void => browser.localStorage.removeItem(key),
    },
    timer: { setInterval: (callback: () => void, milliseconds: number): number => browser.setInterval(callback, milliseconds), clearInterval: (id: number): void => browser.clearInterval(id) },
    theme: { apply(value): void { preference = value; renderTheme() }, dispose(): void { media.removeEventListener('change', renderTheme) } },
    downloads: { save(blob: Blob, filename: string): void {
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url; anchor.download = filename
      document.body.append(anchor); anchor.click(); anchor.remove()
      browser.setTimeout((): void => URL.revokeObjectURL(url), 0)
    } },
    log(entry: LogEntry): void { browser.dispatchEvent(new CustomEvent<LogEntry>('modforge:diagnostic', { detail: entry })) },
  }
}

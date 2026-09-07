/**
 * 轻量 i18n 入口（由 lib/i18n.ts 拆分：zh 为 key 源，en 对照补齐）。
 */
import { useUi } from '../store'
import { zh } from './zh'
import { en } from './en'

export type TKey = keyof typeof zh

export function useT() {
  const { locale } = useUi()
  const table = locale === 'en' ? en : zh
  return (key: TKey) => table[key] ?? zh[key] ?? key
}

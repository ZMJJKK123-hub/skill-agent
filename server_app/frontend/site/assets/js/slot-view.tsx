// JSX 返回类型与槽位 props 通过明确类型连接。
import type { ReactElement } from 'react'
// 槽位的实例与启用状态从当前应用获取。
import { useApplication, useUi } from './application-context.tsx'
// 页面只消费槽位名称与可选折叠状态。
import type { SlotName, SlotProps } from './slots.types.ts'

/** 渲染指定槽位；关闭的插件隐藏，设置插件始终可见。Globals Used: None。 */
export function SlotView({ name, props }: { name: SlotName; props?: SlotProps }): ReactElement {
  const { slots } = useApplication()
  const { disabledPlugins } = useUi()
  return <>{slots.entries(name).filter((entry): boolean => !disabledPlugins.includes(entry.pluginId) || entry.pluginId === 'modforge-settings')
    .map((entry): ReactElement => { const Component = entry.render; return <Component key={`${entry.pluginId}:${entry.id}`} {...props} /> })}</>
}

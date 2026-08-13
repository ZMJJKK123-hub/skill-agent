import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { composition } from './composition'
import { registry } from './shell/registry'
import { AppShell } from './shell/AppShell'

// 启动壳：按组合配置装配插件（等价 dsh 装载 client 插件树）
for (const plugin of composition) {
  registry.currentPluginId = plugin.id
  plugin.apply({ slots: registry })
}
registry.currentPluginId = null

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppShell />
  </React.StrictMode>,
)

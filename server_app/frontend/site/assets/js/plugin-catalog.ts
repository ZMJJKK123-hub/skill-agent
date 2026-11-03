/** 供装配入口和设置面板共用的元数据；不导入组件，避免设置↔装配循环依赖。 */
export const PLUGIN_CATALOG = [
  { id: 'modforge-sidebar', name: '侧栏' }, { id: 'modforge-conversation', name: '对话' },
  { id: 'modforge-auth', name: '登录/注册' }, { id: 'modforge-settings', name: '设置' },
  { id: 'modforge-generate', name: '生成监控' }, { id: 'modforge-games', name: '小游戏' },
] as const

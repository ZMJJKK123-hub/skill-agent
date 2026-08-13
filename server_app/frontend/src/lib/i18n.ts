import { useUi } from './store'

// 轻量 i18n：zh 为 key 源，en 对照补齐（仿 dsh 的 locales/ 字典 pair）
const zh: Record<string, string> = {
  'settings.general': '通用',
  'settings.models': '模型',
  'settings.plugins': '插件',
  'settings.agent': 'Agent 预设',
  'settings.language': '语言',
  'settings.appearance': '外观',
  'settings.apply': '应用',
  'settings.cancel': '取消',

  'general.game': '游戏',
  'general.loader': 'Mod Loader',
  'general.version': '游戏版本',
  'general.apiKey': 'DeepSeek API Key',
  'general.apiKeyHint': 'sk-…（仅存当前会话，不落盘）',
  'general.fallbackHint': 'NeoForge / Fabric 模板暂未提供，选它们会回退到空目录。',

  'models.title': '模型提供方',
  'models.add': '添加自定义提供方',
  'models.name': '名称',
  'models.baseUrl': 'Base URL',
  'models.model': '模型名',
  'models.apiKey': 'API Key',
  'models.save': '保存',
  'models.remove': '移除',
  'models.empty': '暂无自定义提供方',

  'plugins.title': '插件',
  'plugins.enabled': '已启用',
  'plugins.disabled': '已禁用',

  'agent.title': 'Agent 预设',
  'agent.standard': '标准（standard）',
  'agent.standardDesc': '完整的 MOD 生成 agent，默认启用。',

  'appearance.title': '外观',
  'appearance.light': '浅色',
  'appearance.dark': '深色',
  'appearance.system': '跟随系统',

  'language.title': '语言',
  'language.zh': '简体中文',
  'language.en': 'English',

  'nav.workspace': '工作区',
  'nav.sessions': '会话',
  'nav.settings': '设置',
  'nav.import': '导入文件夹',
  'nav.fromZero': '从零生成',
  'nav.newWorkspace': '新建工作区（从零生成）',
  'nav.noSessions': '还没有会话',
  'nav.loginToSee': '登录后显示历史',

  'auth.login': '登录',
  'auth.register': '注册',
  'auth.registerLogin': '注册并登录',
  'auth.username': '用户名',
  'auth.password': '密码',
  'auth.submitting': '提交中…',
  'auth.fill': '请填写用户名和密码',
  'auth.loginFirst': '请先点右上角「登录」/「注册」，登录后才能发起生成。',
  'auth.needApiKey': '请先在左下角「设置」里填写 DeepSeek API Key。',

  'conv.title': '开始生成你的 Minecraft MOD',
  'conv.desc': '输入需求，从零生成 mod 源码；或先在左侧导入已有的 mod 文件夹，再描述你想修改的内容。',
  'conv.placeholder': '描述你的 MOD 需求…（支持从零生成）',
  'conv.send': '发送 ⏎',
  'conv.generating': '生成中…',
  'conv.section': '生成',
  'conv.downloadJar': '下载 mod jar',
  'conv.downloadZip': '下载源码 zip',
  'conv.regenerate': '重新生成',
  'conv.running': '进行中',
  'conv.done': '完成 ✓',
  'conv.failed': '失败',
  'conv.starting': '正在启动 agent…',
  'conv.noJar': '尚无 jar（构建失败或未完成）',
  'conv.model': '模型',
  'conv.quickSword': '做一个攻击力很高的剑',
  'conv.quickFood': '做一个回血很多的食物',
  'conv.quickBlock': '做一个特殊的方块',
}

const en: Record<string, string> = {
  'settings.general': 'General',
  'settings.models': 'Models',
  'settings.plugins': 'Plugins',
  'settings.agent': 'Agent Preset',
  'settings.language': 'Language',
  'settings.appearance': 'Appearance',
  'settings.apply': 'Apply',
  'settings.cancel': 'Cancel',

  'general.game': 'Game',
  'general.loader': 'Mod Loader',
  'general.version': 'Game Version',
  'general.apiKey': 'DeepSeek API Key',
  'general.apiKeyHint': 'sk-… (session-only, never persisted)',
  'general.fallbackHint': 'NeoForge / Fabric templates are not available yet; selecting them falls back to an empty folder.',

  'models.title': 'Model Providers',
  'models.add': 'Add custom provider',
  'models.name': 'Name',
  'models.baseUrl': 'Base URL',
  'models.model': 'Model',
  'models.apiKey': 'API Key',
  'models.save': 'Save',
  'models.remove': 'Remove',
  'models.empty': 'No custom providers yet',

  'plugins.title': 'Plugins',
  'plugins.enabled': 'Enabled',
  'plugins.disabled': 'Disabled',

  'agent.title': 'Agent Preset',
  'agent.standard': 'Standard',
  'agent.standardDesc': 'The full MOD generation agent, enabled by default.',

  'appearance.title': 'Appearance',
  'appearance.light': 'Light',
  'appearance.dark': 'Dark',
  'appearance.system': 'System',

  'language.title': 'Language',
  'language.zh': '简体中文',
  'language.en': 'English',

  'nav.workspace': 'Workspace',
  'nav.sessions': 'Sessions',
  'nav.settings': 'Settings',
  'nav.import': 'Import folder',
  'nav.fromZero': 'From scratch',
  'nav.newWorkspace': 'New workspace (from scratch)',
  'nav.noSessions': 'No sessions yet',
  'nav.loginToSee': 'Login to see history',

  'auth.login': 'Sign in',
  'auth.register': 'Sign up',
  'auth.registerLogin': 'Sign up & sign in',
  'auth.username': 'Username',
  'auth.password': 'Password',
  'auth.submitting': 'Submitting…',
  'auth.fill': 'Please fill username and password',
  'auth.loginFirst': 'Please sign in / sign up (top-right) first.',
  'auth.needApiKey': 'Please fill your DeepSeek API Key in Settings (bottom-left).',

  'conv.title': 'Generate your Minecraft MOD',
  'conv.desc': 'Describe your request to generate a mod from scratch, or import an existing mod folder on the left and describe what to change.',
  'conv.placeholder': 'Describe your MOD request…',
  'conv.send': 'Send ⏎',
  'conv.generating': 'Generating…',
  'conv.section': 'Generate',
  'conv.downloadJar': 'Download mod jar',
  'conv.downloadZip': 'Download source zip',
  'conv.regenerate': 'Regenerate',
  'conv.running': 'Running',
  'conv.done': 'Done ✓',
  'conv.failed': 'Failed',
  'conv.starting': 'Starting agent…',
  'conv.noJar': 'No jar yet (build failed or unfinished)',
  'conv.model': 'Model',
  'conv.quickSword': 'Make a powerful sword',
  'conv.quickFood': 'Make a food that heals a lot',
  'conv.quickBlock': 'Make a special block',
}

export type TKey = keyof typeof zh

export function useT() {
  const { locale } = useUi()
  return (key: string): string => {
    const table = locale === 'en' ? en : zh
    return table[key] ?? zh[key] ?? key
  }
}

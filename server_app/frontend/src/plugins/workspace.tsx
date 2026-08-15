// ============================================================================
// 【导入文件夹功能 - 已临时禁用】
// 说明：导入后 bug 较多，暂时注释停用；代码保留，后续扩展时恢复。
// 恢复方法：取消本文件所有注释即可（插件会重新注入 sidebarFooter 的导入按钮）。
// ============================================================================

// import { useRef, useState } from 'react'
// import { PluginManifest, SLOTS } from '../shell/registry'
// import { useUi, resolveModelConfig } from '../lib/store'
// import { useT } from '../lib/i18n'
// import { importWorkspace } from '../lib/session'
// import type { ImportFile } from '../lib/api'

// const SKIP_DIRS = new Set([
//   '.gradle', 'build', 'run', 'out', 'dist', '.git', '.idea', '.vscode',
//   'node_modules', '.worktrees', '.team', '.tasks', '.transcripts', '__pycache__',
// ])

// async function collectFromHandle(dir: any, base = ''): Promise<ImportFile[]> {
//   const out: ImportFile[] = []
//   for await (const [name, handle] of dir.entries()) {
//     if (handle.kind === 'file') {
//       const file = await handle.getFile()
//       out.push({ path: base ? base + '/' + name : name, data: new Uint8Array(await file.arrayBuffer()) })
//     } else if (handle.kind === 'directory') {
//       if (SKIP_DIRS.has(name)) continue
//       out.push(...(await collectFromHandle(handle, base ? base + '/' + name : name)))
//     }
//   }
//   return out
// }

// function ImportButton({ collapsed }: { collapsed?: boolean }) {
//   const { user, apiKey, game, loader, version, model, providers, sandbox } = useUi()
//   const t = useT()
//   const [busy, setBusy] = useState(false)
//   const inputRef = useRef<HTMLInputElement>(null)

//   const cfg = () => {
//     const r = resolveModelConfig({ apiKey, model, providers })
//     return { apiKey: r.apiKey, baseUrl: r.baseUrl, model: r.model, game, loader, version, sandbox }
//   }

//   const doImport = async () => {
//     if (!user) {
//       alert(t('auth.loginFirst'))
//       return
//     }
//     const picker = (window as any).showDirectoryPicker
//     if (typeof picker === 'function') {
//       try {
//         const dir = await picker()
//         setBusy(true)
//         const files = await collectFromHandle(dir)
//         if (files.length === 0) {
//           alert('所选文件夹没有可导入的文件（已跳过构建缓存/依赖等目录）')
//           return
//         }
//         await importWorkspace(files, cfg(), dir.name)
//       } catch (e) {
//         if ((e as any)?.name !== 'AbortError') alert('导入失败: ' + (e instanceof Error ? e.message : String(e)))
//       } finally {
//         setBusy(false)
//       }
//     } else {
//       // 降级：非 Chromium 用 <input webkitdirectory>（Safari/部分场景）
//       inputRef.current?.click()
//     }
//   }

//   const onFallback = async (e: React.ChangeEvent<HTMLInputElement>) => {
//     const list = e.target.files
//     if (!list || list.length === 0) return
//     setBusy(true)
//     try {
//       let folder = '导入的文件夹'
//       const files: ImportFile[] = []
//       for (const f of Array.from(list)) {
//         const rel = (f as any).webkitRelativePath || f.name
//         if (folder === '导入的文件夹' && rel.includes('/')) folder = rel.split('/')[0]
//         files.push({ path: rel, data: new Uint8Array(await f.arrayBuffer()) })
//       }
//       await importWorkspace(files, cfg(), folder)
//     } catch (err) {
//       alert('导入失败: ' + (err instanceof Error ? err.message : String(err)))
//     } finally {
//       setBusy(false)
//       e.target.value = ''
//     }
//   }

//   return (
//     <>
//       <button
//         onClick={doImport}
//         disabled={busy}
//         title={t('nav.import')}
//         className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm hoverable disabled:opacity-50"
//       >
//         <span>📂</span>
//         {!collapsed && <span>{busy ? t('auth.submitting') : t('nav.import')}</span>}
//       </button>
//       {/* 非 Chromium 降级入口 */}
//       <input
//         ref={inputRef}
//         type="file"
//         multiple
//         {...({ webkitdirectory: '' } as any)}
//         onChange={onFallback}
//         className="hidden"
//       />
//     </>
//   )
// }

// export const workspacePlugin: PluginManifest = {
//   id: 'modforge-workspace',
//   name: '工作区',
//   apply(ctx) {
//     ctx.slots.inject(SLOTS.sidebarFooter, 'import', (props: any) => <ImportButton collapsed={props?.collapsed} />, 5)
//   },
// }

// ============================================================================
// 占位导出：防止 composition 引用已不存在的插件时构建报错。
// 恢复导入功能时删除此占位并恢复上方代码。
// ============================================================================
export const workspacePlugin = { id: 'modforge-workspace', name: '工作区', apply() {} }

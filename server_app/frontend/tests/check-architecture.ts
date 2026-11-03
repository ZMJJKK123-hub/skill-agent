// 结构门禁只检查前端源码，不读取用户数据或修改文件。
import { readdirSync, readFileSync, existsSync } from 'node:fs'
// 路径相对当前工具定位，避免 shell cwd 差异。
import { resolve, relative, dirname } from 'node:path'
// 当前模块地址定位前端根。
import { fileURLToPath } from 'node:url'
// TypeScript AST 检查类型逃逸、内联导入和运行时依赖环。
import ts from 'typescript'

/** 前端根目录和源码根是门禁的唯一文件范围。 */
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
/** site 分区源码必须全部通过门禁。 */
const site = resolve(root, 'site')
/** 失败列表输出文件位置和规则，不包含业务内容。 */
const failures: string[] = []

/** 递归枚举已知源码目录；不访问 node_modules、后端或运行时目录。 */
function files(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry): string[] => entry.isDirectory() ? files(resolve(directory, entry.name)) : [resolve(directory, entry.name)])
}

/** 仅解析相对源码导入；外部 npm 模块不参与应用依赖环检查。 */
function imported(from: string, specifier: string): string | null {
  if (!specifier.startsWith('.')) return null
  const path = resolve(dirname(from), specifier)
  return existsSync(path) ? path : null
}

/** 每个源码文件记录其运行时边，类型导入不构成运行时循环。 */
const graph = new Map<string, string[]>()
for (const file of files(site)) {
  const path = relative(root, file).replace(/\\/g, '/')
  if (!/^site\/(?:index\/index\.html|assets\/(?:js|css)\/[^/]+|[^/]+\/assets\/(?:js|css)\/[^/]+)$/.test(path)) failures.push(`${path}: 文件不在分区或共享资源目录`)
  if (!/\.tsx?$/.test(file)) continue
  const source = ts.createSourceFile(file, readFileSync(file, 'utf8'), ts.ScriptTarget.Latest, true, file.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS)
  const edges: string[] = []
  for (const statement of source.statements) {
    if (ts.isImportDeclaration(statement)) {
      const comment = source.text.slice(statement.getFullStart(), statement.getStart(source))
      if (!/\/\//.test(comment)) failures.push(`${path}: 导入缺少说明注释`)
      const specifier = (statement.moduleSpecifier as ts.StringLiteral).text
      if (/\/src\/|\/lib\/|\/plugins\/|\/shell\//.test(specifier)) failures.push(`${path}: 遗留目录导入`)
      if (!statement.importClause?.isTypeOnly) { const dependency = imported(file, specifier); if (dependency?.match(/\.tsx?$/)) edges.push(dependency) }
    }
    if (ts.isFunctionDeclaration(statement) && !statement.type) failures.push(`${path}: 顶层函数缺少显式返回类型`)
  }
  graph.set(file, edges)
  /** 只检查语法节点，避免注释文本产生误报。 */
  function inspect(node: ts.Node): void {
    if (node.kind === ts.SyntaxKind.AnyKeyword) failures.push(`${path}: 禁止 any`)
    if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) failures.push(`${path}: 禁止内联/延迟导入`)
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression) && node.expression.expression.getText(source) === 'console') failures.push(`${path}: 日志必须经过统一日志器`)
    if (/\.(?:service|model|store)\.ts$/.test(file) && ts.isIdentifier(node) && ['window', 'document', 'localStorage'].includes(node.text)) failures.push(`${path}: 业务层直接依赖浏览器副作用`)
    ts.forEachChild(node, inspect)
  }
  inspect(source)
}
/** DFS 路径记录用于报告实际运行时依赖环。 */
const active = new Set<string>(); const complete = new Set<string>()
function visit(file: string): void {
  if (active.has(file)) { failures.push(`${relative(root, file)}: 运行时依赖环`); return }
  if (complete.has(file)) return
  active.add(file); for (const dependency of graph.get(file) ?? []) visit(dependency)
  active.delete(file); complete.add(file)
}
for (const file of graph.keys()) visit(file)
if (existsSync(resolve(root, 'src'))) failures.push('旧 src 目录尚未移除')
if (failures.length) { process.stderr.write(`${[...new Set(failures)].join('\n')}\n`); process.exitCode = 1 }
else process.stdout.write('Frontend architecture checks passed.\n')

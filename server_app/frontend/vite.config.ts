// Vite 负责开发代理和生产静态导出；不改变 FastAPI 路由或端口。
import { defineConfig, loadEnv, type Plugin } from 'vite'
// 保留当前 React/TSX 编译能力。
import react from '@vitejs/plugin-react'
// 路径只由配置文件位置解析，不依赖启动 shell 的 cwd。
import { fileURLToPath } from 'node:url'

/** 将分区 HTML 映射为既有首页地址与产物路径，资源继续使用 Vite 哈希路径。 */
function indexEntry(): Plugin {
  return {
    name: 'modforge-index-entry', enforce: 'post',
    configureServer(server): void {
      server.middlewares.use((request, _response, next): void => {
        if (request.url === '/' || request.url?.startsWith('/?')) request.url = request.url.replace('/', '/index/index.html')
        next()
      })
    },
    generateBundle: {
      order: 'post',
      handler(_options, bundle): void {
        const page = bundle['index/index.html']
        if (page) { page.fileName = 'index.html'; bundle['index.html'] = page; delete bundle['index/index.html'] }
      },
    },
  }
}

/** 只读前端 VITE_* 环境变量；生产同源，开发默认连接既有 8000 后端。 */
export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, fileURLToPath(new URL('.', import.meta.url)), 'VITE_')
  const target = environment.VITE_DEV_API_TARGET ?? 'http://127.0.0.1:8000'
  return {
    root: fileURLToPath(new URL('./site', import.meta.url)), publicDir: false,
    plugins: [react(), indexEntry()],
    build: { outDir: fileURLToPath(new URL('../web', import.meta.url)), emptyOutDir: true,
      rollupOptions: { input: fileURLToPath(new URL('./site/index/index.html', import.meta.url)) },
    },
    server: { host: '127.0.0.1', port: 5173, proxy: {
      '/api': { target, changeOrigin: true }, '/debug': { target, changeOrigin: true },
    } },
  }
})

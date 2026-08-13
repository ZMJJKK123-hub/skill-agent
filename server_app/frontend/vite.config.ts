import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 构建产物直接输出到 server_app/web/，由 server.py 静态托管（localhost:8000）
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../web',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    proxy: {
      // 开发时 /api 转发到 FastAPI 后端
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})

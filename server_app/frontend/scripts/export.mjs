/**
 * 静态导出脚本：
 *   1. 清空 server_app/web/ 下的旧产物（index.html + _next/）
 *   2. 把 next build 生成的 out/ 拷贝到 server_app/web/
 *
 * 用法：node scripts/export.mjs   （build:all 会自动先执行 next build）
 */
import { cpSync, rmSync, existsSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDir = join(dirname(fileURLToPath(import.meta.url)), "..");
const outDir = join(frontendDir, "out");
const webDir = join(frontendDir, "..", "web");
const assetsDir = join(frontendDir, "..", "assets");

if (!existsSync(join(outDir, "index.html"))) {
  console.error("[export] out/index.html 不存在，请先执行 next build");
  process.exit(1);
}

// 清理旧产物：删除 web 下的 index.html 与 _next
for (const name of ["index.html", "_next", "favicon.ico"]) {
  rmSync(join(webDir, name), { recursive: true, force: true });
}

// 删除 React 重构前遗留的 css / js 目录（已被组件化替代）
for (const name of ["css", "js"]) {
  rmSync(join(webDir, name), { recursive: true, force: true });
}

// 拷贝 out/ 全部内容到 web/
for (const entry of readdirSync(outDir)) {
  cpSync(join(outDir, entry), join(webDir, entry), {
    recursive: true,
    force: true,
  });
}

// 拷贝 server_app/assets/（mc_icon.png 等静态素材）到 web/assets/，供前端 <img> 引用
if (existsSync(assetsDir)) {
  const dest = join(webDir, "assets");
  rmSync(dest, { recursive: true, force: true });
  cpSync(assetsDir, dest, { recursive: true, force: true });
}

console.log("[export] 前端产物已部署到 server_app/web/");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  // 静态导出到 frontend/out/，再由 scripts/export.mjs 拷贝到 server_app/web
  images: { unoptimized: true },
  reactStrictMode: true,
};

export default nextConfig;

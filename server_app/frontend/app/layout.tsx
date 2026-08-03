import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MOD Forge — AI MOD 制作器",
  description: "AI 驱动的游戏 MOD 生成器，全程可视化观察智能体的思考与决策过程。",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
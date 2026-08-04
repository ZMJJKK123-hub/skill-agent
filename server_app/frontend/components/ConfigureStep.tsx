"use client";

import { useState } from "react";
import { Eye, EyeOff, Lock, RotateCcw } from "lucide-react";
import clsx from "clsx";
import type { Game } from "../lib/types";

interface ConfigureStepProps {
  games: Game[];
  onCreateSession: (apiKey: string, game: string) => Promise<void>;
}

/** 即将支持的占位游戏（虚线锁定卡片，体现选择器阵列） */
const COMING_SOON = ["Stardew Valley", "Terraria"];

function MinecraftIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6">
      <path d="M4 10 L12 5 L20 10 L20 18 L12 22 L4 18 Z" fill="rgba(52,211,153,0.35)" />
      <path d="M4 10 L12 14 L20 10" fill="none" stroke="rgba(52,211,153,0.7)" />
    </svg>
  );
}

export default function ConfigureStep({ games, onCreateSession }: ConfigureStepProps) {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [game, setGame] = useState("minecraft");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleCreate();
  };

  async function handleCreate() {
    if (!apiKey.trim()) {
      setError("请填写 DeepSeek API Key");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await onCreateSession(apiKey.trim(), game);
      // 创建成功后立即清空，前端不再持有 API Key
      setApiKey("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建会话失败");
    } finally {
      setLoading(false);
    }
  }

  const handleReset = () => {
    setApiKey("");
    setError("");
  };

  return (
    <div className="glass mx-auto max-w-3xl p-6 md:p-8">
      {/* 标题 + 辅助说明 */}
      <div>
        <h2 className="text-lg font-bold text-zinc-100">配置生成环境</h2>
        <p className="mt-1 text-xs text-zinc-500">
          请配置您的底层大模型凭证与目标锻造环境
        </p>
      </div>

      {/* 各区大间距 */}
      <div className="mt-8 space-y-8">
        {/* API Key 区：桌面端左右分栏 */}
        <div className="grid items-start gap-4 sm:grid-cols-3 sm:gap-6">
          <div>
            <label className="block text-sm font-medium text-zinc-400">
              DeepSeek API Key
            </label>
            <p className="mt-1 hidden text-xs leading-relaxed text-zinc-600 sm:block">
              仅用于本次生成，使用后即从页面清除，不落盘、不共享
            </p>
          </div>
          <div className="sm:col-span-2">
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="sk-..."
                autoComplete="new-password"
                name="deepseek-api-key-field"
                spellCheck={false}
                className="input-forge pr-12"
                aria-label="DeepSeek API Key"
              />
              <button
                type="button"
                onClick={() => setShowKey((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 transition-colors hover:text-zinc-300"
                aria-label={showKey ? "隐藏" : "显示"}
              >
                {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
        </div>

        {/* 目标游戏区：Bento Grid 选择器 */}
        <div>
          <label className="mb-3 block text-sm font-medium text-zinc-400">
            目标游戏
          </label>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
            {games.map((g) => {
              const selected = game === g.id;
              return (
                <button
                  key={g.id}
                  onClick={() => setGame(g.id)}
                  className={clsx(
                    "group relative flex aspect-square flex-col items-center justify-center gap-2 rounded-xl border p-4 text-center transition-all duration-200",
                    selected
                      ? "border-emerald-500/30 bg-gradient-to-b from-emerald-500/10 to-transparent"
                      : "border-white/[0.05] bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.03]"
                  )}
                >
                  <span className="grid h-11 w-11 place-items-center rounded-lg bg-gradient-to-br from-green-600/30 to-green-800/30">
                    <MinecraftIcon />
                  </span>
                  <span className="block text-sm font-semibold text-zinc-100">
                    {g.name}
                  </span>
                  <span className="block font-mono text-[10px] uppercase tracking-wider text-zinc-600">
                    Engine · Fabric
                  </span>
                  {selected && (
                    <span className="absolute right-2 top-2 grid h-4 w-4 place-items-center rounded-full border border-emerald-500/40 bg-emerald-500/15 text-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.4)]">
                      <svg
                        viewBox="0 0 16 16"
                        className="h-2.5 w-2.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="3"
                      >
                        <path
                          d="M3 8.5 L6.5 12 L13 4.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </span>
                  )}
                </button>
              );
            })}

            {/* 即将支持占位卡片 */}
            {COMING_SOON.map((name) => (
              <div
                key={name}
                className="flex aspect-square flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-white/[0.06] bg-white/[0.01] p-4 text-center opacity-60"
              >
                <Lock size={16} className="text-zinc-600" />
                <span className="block text-sm font-medium text-zinc-500">
                  {name}
                </span>
                <span className="block font-mono text-[10px] uppercase tracking-wider text-zinc-700">
                  即将支持
                </span>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* 操作区：分隔线 + 右侧按钮 */}
        <div className="border-t border-zinc-800 pt-6">
          <div className="flex items-center justify-end gap-3">
            <button onClick={handleReset} className="btn-ghost" type="button">
              <RotateCcw size={14} />
              重置
            </button>
            <button
              onClick={handleCreate}
              disabled={loading}
              className="btn-primary w-auto px-6"
            >
              {loading ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-400/30 border-t-emerald-400" />
              ) : (
                "创建会话"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
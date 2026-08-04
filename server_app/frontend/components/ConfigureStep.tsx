"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import clsx from "clsx";
import type { Game } from "../lib/types";

interface ConfigureStepProps {
  games: Game[];
  onCreateSession: (apiKey: string, game: string) => Promise<void>;
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

  return (
    <div className="glass mx-auto max-w-2xl p-6 md:p-8">
      <h2 className="text-lg font-bold text-zinc-100">配置生成环境</h2>

      {/* API Key 保险箱输入框 */}
      <div className="mt-6">
        <label className="mb-2 block text-sm font-medium text-zinc-400">
          DeepSeek API Key
        </label>
        <div className="relative">
          <input
            type={showKey ? "text" : "password"}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="sk-..."
            autoComplete="off"
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

      {/* 目标游戏 */}
      <div className="mt-6">
        <label className="mb-2 block text-sm font-medium text-zinc-400">
          目标游戏
        </label>
        <div className="grid gap-3">
          {games.map((g) => {
            const selected = game === g.id;
            return (
              <button
                key={g.id}
                onClick={() => setGame(g.id)}
                className={clsx(
                  "group relative flex items-center gap-3 rounded-xl border p-4 text-left transition-all duration-200",
                  selected
                    ? "border-forge-cyan/50 bg-forge-cyan/[0.06] shadow-glow"
                    : "border-white/5 bg-ink-950/40 hover:border-white/15 hover:bg-white/[0.03]"
                )}
              >
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-green-600/30 to-green-800/30">
                  {/* 像素式草方块 */}
                  <svg viewBox="0 0 24 24" className="h-6 w-6">
                    <path
                      d="M4 10 L12 5 L20 10 L20 18 L12 22 L4 18 Z"
                      fill="rgba(52,211,153,0.35)"
                    />
                    <path
                      d="M4 10 L12 14 L20 10"
                      fill="none"
                      stroke="rgba(52,211,153,0.7)"
                    />
                  </svg>
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-semibold text-zinc-100">
                    {g.name}
                  </span>
                  <span className="block truncate text-xs text-zinc-500">
                    {g.description || "可用模板"}
                  </span>
                </span>
                {selected && (
                  <span className="ml-auto grid h-5 w-5 place-items-center rounded-full bg-forge-emerald text-ink-950">
                    <svg
                      viewBox="0 0 16 16"
                      className="h-3 w-3"
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
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="mt-6">
        <button onClick={handleCreate} disabled={loading} className="btn-primary w-full">
          {loading ? (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink-950/30 border-t-ink-950" />
          ) : (
            "创建会话"
          )}
        </button>
      </div>
    </div>
  );
}
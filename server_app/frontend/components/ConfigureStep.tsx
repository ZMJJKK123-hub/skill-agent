"use client";

import { useState } from "react";
import { Check, Eye, EyeOff, Lock, RotateCcw } from "lucide-react";
import clsx from "clsx";
import type { Game } from "../lib/types";

interface ConfigureStepProps {
  games: Game[];
  onCreateSession: (apiKey: string, game: string) => Promise<void>;
}

/** 即将支持的占位游戏 */
const COMING_SOON = ["Stardew Valley", "Terraria"];

/** 加载器选项：仅 Forge 开放，其余 WIP 禁用 */
const LOADERS = [
  { id: "forge", label: "Forge", wip: false },
  { id: "neoforge", label: "NeoForge", wip: true },
  { id: "fabric", label: "Fabric", wip: true },
];

/** 游戏版本：仅最新版开放，其余禁用 */
const VERSIONS = [
  { id: "1.21.1", label: "1.21.1（最新）", latest: true },
  { id: "1.20.1", label: "1.20.1", latest: false },
  { id: "1.19.2", label: "1.19.2", latest: false },
];

export default function ConfigureStep({ games, onCreateSession }: ConfigureStepProps) {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  /** 初始不选中：必须用户交互后才选中 */
  const [game, setGame] = useState<string | null>(null);
  const [loader, setLoader] = useState("forge");
  const [version, setVersion] = useState("1.21.1");
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
    if (!game) {
      setError("请先选择目标游戏");
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
    setGame(null);
    setLoader("forge");
    setVersion("1.21.1");
  };

  /** 面板内确认 loader/version → 自动选中 Minecraft */
  const confirmFromPanel = (nextLoader: string, nextVersion: string) => {
    setLoader(nextLoader);
    setVersion(nextVersion);
    setGame("minecraft");
  };

  return (
    <div className="glass mx-auto max-w-3xl p-6 md:p-8">
      <h2 className="text-lg font-bold text-zinc-100">配置生成环境</h2>

      {/* 各区大间距 */}
      <div className="mt-8 space-y-10">
        {/* API Key 区：桌面端左右分栏 */}
        <div className="grid items-center gap-4 sm:grid-cols-3 sm:gap-6">
          <div className="flex flex-col gap-1.5">
            <label className="block text-sm font-medium text-zinc-400">
              DeepSeek API Key
            </label>
          </div>
          <div className="sm:col-span-2">
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                onKeyDown={handleKeyPress}
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

        {/* 目标游戏区：初始不选中 + Minecraft hover 弹出双列配置面板 */}
        <div>
          <label className="mb-3 block text-sm font-medium text-zinc-400">
            目标游戏
          </label>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
            {games.map((g) => {
              const selected = game === g.id;
              return (
                <div key={g.id} className="group relative">
                  <button
                    onClick={() => setGame(g.id)}
                    className={clsx(
                      "flex aspect-[4/3] w-full flex-col items-center justify-center gap-3 rounded-xl border p-4 text-center transition-all duration-200",
                      selected
                        ? "border-emerald-500/30 bg-gradient-to-b from-emerald-500/10 to-transparent"
                        : "border-white/[0.05] bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.03]"
                    )}
                  >
                    <span className="grid h-11 w-11 place-items-center rounded-lg bg-gradient-to-br from-green-600/30 to-green-800/30">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src="/assets/mc_icon.png"
                        alt="Minecraft"
                        className="h-10 w-10 object-contain drop-shadow-[0_0_6px_rgba(52,211,153,0.35)]"
                      />
                    </span>
                    <span className="block text-sm font-semibold text-zinc-100">
                      {g.name}
                    </span>
                    {selected ? (
                      <span className="block font-mono text-[10px] tracking-widest text-emerald-400">
                        {loader.toUpperCase()} · {version}
                      </span>
                    ) : (
                      <span className="block font-mono text-[10px] tracking-widest text-zinc-500">
                        HOVER TO CONFIGURE
                      </span>
                    )}
                    {selected && (
                      <span className="absolute right-3 top-3 grid h-4 w-4 place-items-center rounded-full border border-emerald-500/40 bg-emerald-500/15 text-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.4)]">
                        <Check size={10} strokeWidth={3} />
                      </span>
                    )}
                  </button>

                  {/* 悬浮配置面板（绝对定位浮动层，不挤下方布局） */}
                  <div className="absolute left-0 top-full z-50 mt-3 w-[400px] origin-top-left rounded-xl border border-zinc-700 bg-zinc-900 p-5 opacity-0 shadow-2xl shadow-black/80 transition-all duration-200 invisible group-hover:visible group-hover:opacity-100">
                    <div className="grid grid-cols-2 gap-6">
                      {/* 左列：Mod Loader */}
                      <div>
                        <div className="mb-2 font-mono text-[10px] text-zinc-500">
                          MOD LOADER
                        </div>
                        <div className="flex flex-col gap-1.5">
                          {LOADERS.map((l) => (
                            <button
                              key={l.id}
                              disabled={l.wip}
                              onClick={() => confirmFromPanel(l.id, version)}
                              className={clsx(
                                "flex items-center justify-between rounded-lg border px-3 py-1.5 text-sm transition-colors duration-150",
                                l.wip
                                  ? "cursor-not-allowed border-white/[0.05] bg-white/[0.01] opacity-40"
                                  : loader === l.id
                                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                                    : "border-white/[0.05] bg-white/[0.02] text-zinc-300 hover:border-white/15 hover:text-zinc-100"
                              )}
                            >
                              {l.label}
                              {l.wip ? (
                                <span className="flex items-center gap-1 text-[10px] text-zinc-600">
                                  <Lock size={10} /> WIP
                                </span>
                              ) : (
                                loader === l.id && <Check size={12} />
                              )}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* 右列：Game Version */}
                      <div>
                        <div className="mb-2 font-mono text-[10px] text-zinc-500">
                          GAME VERSION
                        </div>
                        <div className="flex flex-col gap-1.5">
                          {VERSIONS.map((v) => (
                            <button
                              key={v.id}
                              disabled={!v.latest}
                              onClick={() => confirmFromPanel(loader, v.id)}
                              className={clsx(
                                "flex items-center justify-between rounded-lg border px-3 py-1.5 text-sm transition-colors duration-150",
                                !v.latest
                                  ? "cursor-not-allowed border-white/[0.05] bg-white/[0.01] opacity-40"
                                  : version === v.id
                                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                                    : "border-white/[0.05] bg-white/[0.02] text-zinc-300 hover:border-white/15 hover:text-zinc-100"
                              )}
                            >
                              {v.label}
                              {version === v.id && <Check size={12} />}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* 即将支持占位卡片 */}
            {COMING_SOON.map((name) => (
              <div
                key={name}
                className="flex aspect-[4/3] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-white/[0.06] bg-white/[0.01] p-4 text-center opacity-60"
              >
                <Lock size={16} className="text-zinc-600" />
                <span className="block text-sm font-medium text-zinc-500">
                  {name}
                </span>
                <span className="mt-1 block font-mono text-[10px] tracking-widest text-zinc-700">
                  COMING SOON
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
            <button onClick={handleReset} className="btn-ghost text-zinc-400" type="button">
              <RotateCcw size={14} />
              重置
            </button>
            <button
              onClick={handleCreate}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-emerald-600/50 bg-emerald-900/60 px-6 py-2.5 text-sm font-medium text-emerald-400 transition-all duration-300 hover:bg-emerald-800/80 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] disabled:cursor-not-allowed disabled:opacity-50"
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
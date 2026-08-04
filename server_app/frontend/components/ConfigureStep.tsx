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

/** 加载器：Forge 可用，NeoForge/Fabric WIP 禁用 */
const LOADERS = [
  { id: "forge", label: "Forge", wip: false },
  { id: "neoforge", label: "NeoForge", wip: true },
  { id: "fabric", label: "Fabric", wip: true },
];

/** 可选的游戏版本 */
const VERSIONS = ["1.21.1", "1.20.1", "1.19.2"];

export default function ConfigureStep({ games, onCreateSession }: ConfigureStepProps) {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  /** 初始全部为空：游戏 / Loader / Version 均无默认 */
  const [game, setGame] = useState<string | null>(null);
  const [loader, setLoader] = useState<string | null>(null);
  const [version, setVersion] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /** 点亮条件：三个必选项全部就绪 */
  const active = !!game && !!loader && !!version;

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleCreate();
  };

  async function handleCreate() {
    if (!active || !apiKey.trim()) return;
    setLoading(true);
    setError("");
    try {
      await onCreateSession(apiKey.trim(), game!);
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
    setLoader(null);
    setVersion(null);
    setDrawerOpen(false);
  };

  /** 点击卡片：仅切换面板展开，不点亮 */
  const toggleDrawer = () => {
    setGame("minecraft");
    setDrawerOpen((v) => !v);
  };

  /** Loader 药丸 toggle：已选再点则取消 */
  const toggleLoader = (id: string) => {
    setLoader((cur) => (cur === id ? null : id));
  };

  return (
    <div className="glass mx-auto max-w-3xl p-6 md:p-8">
      <h2 className="text-lg font-bold text-zinc-100">配置生成环境</h2>

      <div className="mt-8 space-y-10">
        {/* API Key 区 */}
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

        {/* 目标游戏区 */}
        <div>
          <label className="mb-3 block text-sm font-medium text-zinc-400">
            目标游戏
          </label>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
            {games.map((g) => {
              const isActive = active && game === g.id;
              return (
                <button
                  key={g.id}
                  onClick={toggleDrawer}
                  className={clsx(
                    "relative flex aspect-[4/3] w-full flex-col items-center justify-center gap-3 rounded-xl border p-4 text-center transition-all duration-200",
                    isActive
                      ? "border-emerald-500/50 bg-gradient-to-b from-emerald-500/10 to-transparent"
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
                  {/* 三态文案：未选 / 待选满 / 回显 */}
                  {isActive ? (
                    <span className="block font-mono text-[10px] tracking-widest text-emerald-400">
                      {loader!.toUpperCase()} · {version}
                    </span>
                  ) : drawerOpen && game === g.id ? (
                    <span className="block animate-pulse font-mono text-[10px] tracking-widest text-amber-400/80">
                      PENDING SELECTION...
                    </span>
                  ) : (
                    <span className="block font-mono text-[10px] tracking-widest text-zinc-500">
                      CLICK TO CONFIGURE
                    </span>
                  )}
                  {isActive && (
                    <span className="absolute right-3 top-3 grid h-4 w-4 place-items-center rounded-full border border-emerald-500/40 bg-emerald-500/15 text-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.4)]">
                      <Check size={10} strokeWidth={3} />
                    </span>
                  )}
                  {/* 展开指示箭头 */}
                  <span
                    className={clsx(
                      "absolute bottom-2 right-3 text-[10px] text-zinc-600 transition-transform duration-200",
                      drawerOpen && game === g.id && "rotate-180"
                    )}
                  >
                    ▾
                  </span>
                </button>
              );
            })}

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

          {/* Inline Drawer：选满前常驻提示，展开后显示配置面板 */}
          {drawerOpen && game === "minecraft" && (
            <div className="drawer-in mt-6 w-full rounded-xl border border-white/5 bg-black/40 p-5 shadow-inner shadow-black/60">
              <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
                {/* 左列：MOD LOADER */}
                <div>
                  <div className="mb-3 font-mono text-xs tracking-widest text-zinc-500">
                    MOD LOADER
                  </div>
                  <div className="flex flex-col gap-2">
                    {LOADERS.map((l) => (
                      <button
                        key={l.id}
                        disabled={l.wip}
                        onClick={() => toggleLoader(l.id)}
                        className={clsx(
                          "flex items-center justify-between rounded-lg border px-4 py-2 text-sm transition-colors duration-150",
                          l.wip
                            ? "cursor-not-allowed border border-zinc-800 text-zinc-500 opacity-40"
                            : loader === l.id
                              ? "border border-emerald-500/50 bg-emerald-900/40 text-emerald-400"
                              : "border border-zinc-800 text-zinc-300 hover:border-white/15 hover:text-zinc-100"
                        )}
                      >
                        {l.label}
                        {l.wip ? (
                          <Lock size={12} className="text-zinc-600" />
                        ) : loader === l.id ? (
                          <Check size={12} />
                        ) : null}
                      </button>
                    ))}
                  </div>
                </div>

                {/* 右列：GAME VERSION */}
                <div>
                  <div className="mb-3 font-mono text-xs tracking-widest text-zinc-500">
                    GAME VERSION
                  </div>
                  <select
                    value={version ?? ""}
                    onChange={(e) => setVersion(e.target.value || null)}
                    className={clsx(
                      "w-full rounded-lg border px-4 py-2 font-mono text-sm outline-none transition-colors duration-150",
                      version
                        ? "border border-emerald-500/50 bg-emerald-900/40 text-emerald-400"
                        : "border border-zinc-800 bg-black/40 text-zinc-300"
                    )}
                  >
                    <option value="">选择版本</option>
                    {VERSIONS.map((v) => (
                      <option key={v} value={v}>
                        {v}
                        {v === "1.21.1" ? "（最新）" : ""}
                      </option>
                    ))}
                  </select>
                  <p className="mt-2 text-xs text-zinc-600">
                    {version
                      ? "已选择，可重新下拉更换"
                      : "请选择一个版本"}
                  </p>
                </div>
              </div>

              {/* 栏内底部提示 */}
              <div className="mt-4 border-t border-white/5 pt-3 font-mono text-[10px] text-zinc-600">
                {active
                  ? `✓ ${(loader ?? "").toUpperCase()} · ${version}`
                  : "选择 LOADER 与 VERSION 后自动点亮卡片"}
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* 操作区：提交拦截 */}
        <div className="border-t border-zinc-800 pt-6">
          <div className="flex items-center justify-end gap-3">
            <button onClick={handleReset} className="btn-ghost text-zinc-400" type="button">
              <RotateCcw size={14} />
              重置
            </button>
            <button
              onClick={handleCreate}
              disabled={!active || !apiKey.trim() || loading}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-emerald-600/50 bg-emerald-900/60 px-6 py-2.5 text-sm font-medium text-emerald-400 transition-all duration-300 hover:bg-emerald-800/80 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-emerald-900/60 disabled:hover:shadow-none"
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
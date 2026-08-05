"use client";

import { useState } from "react";
import { Check, Eye, EyeOff, Lock, RotateCcw, TriangleAlert, XCircle } from "lucide-react";
import clsx from "clsx";
import type { Game } from "../../lib/types";
import { useToast } from "../common_ui/Toast";

interface ConfigureStepProps {
  games: Game[];
  onCreateSession: (apiKey: string, game: string, loader?: string, version?: string) => Promise<void>;
  /** 父级保存的已填内容：返回配置页时回显（需求 page 返回后不重输） */
  savedApiKey?: string;
  savedLoader?: string;
  savedVersion?: string;
}

/** 即将支持的占位游戏 */
const COMING_SOON = ["Stardew Valley", "Terraria"];

/** 加载器：Forge 可用，NeoForge/Fabric 锁定（下拉框内不可选，无警告） */
const LOADERS = [
  { id: "forge", label: "Forge", disabled: false },
  { id: "neoforge", label: "NeoForge", disabled: true },
  { id: "fabric", label: "Fabric", disabled: true },
];

/** 可选的游戏版本：全部可选（老版本不锁，仅给非阻塞警告） */
const VERSIONS = ["1.21.1", "1.20.1", "1.19.2"];
const LATEST_VERSION = "1.21.1";

export default function ConfigureStep({
  games,
  onCreateSession,
  savedApiKey = "",
  savedLoader = "",
  savedVersion = "",
}: ConfigureStepProps) {
  const toast = useToast();
  const [apiKey, setApiKey] = useState(savedApiKey);
  const [showKey, setShowKey] = useState(false);
  /** 游戏默认随父级选择（minecraft）；Loader/Version 用 saved 回显，无则空 */
  const [game, setGame] = useState<string | null>("minecraft");
  const [loader, setLoader] = useState<string | null>(savedLoader || null);
  const [version, setVersion] = useState<string | null>(savedVersion || null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  /** 错误标记：apiKeyError / selectError（游戏/loader/version 未满） */
  const [apiKeyError, setApiKeyError] = useState(false);
  const [selectError, setSelectError] = useState(false);
  /** shake 触发计数（改变 key 重新播放动画） */
  const [shakeTick, setShakeTick] = useState(0);

  /** 点亮条件：三个必选项全部就绪 */
  const active = !!game && !!loader && !!version;
  /** 非最新版本 → 非阻塞兼容警告 */
  const versionWarning = !!version && version !== LATEST_VERSION;

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleCreate();
  };

  async function handleCreate() {
    // 硬错误：按序校验并给出 Toast + 就地反馈
    if (!apiKey.trim()) {
      toast("请填写 DeepSeek API Key", "error");
      setApiKeyError(true);
      setShakeTick((v) => v + 1);
      return;
    }
    if (!game) {
      toast("请先选择目标游戏", "error");
      setSelectError(true);
      setShakeTick((v) => v + 1);
      return;
    }
    if (!loader || !version) {
      toast("请完成 LOADER 与 VERSION 配置", "error");
      setSelectError(true);
      setShakeTick((v) => v + 1);
      return;
    }
    setLoading(true);
    try {
      await onCreateSession(apiKey.trim(), game, loader ?? "", version ?? "");
      // 创建成功后立即清空，前端不再持有 API Key
      setApiKey("");
    } catch (err) {
      toast(err instanceof Error ? err.message : "创建会话失败", "error");
    } finally {
      setLoading(false);
    }
  }

  const handleReset = () => {
    setApiKey("");
    setShowKey(false);
    setGame(null);
    setLoader(null);
    setVersion(null);
    setDrawerOpen(false);
    setSelectError(false);
    setShowKey(false);
  };

  /** 点击卡片：仅切换面板展开，不点亮 */
  const toggleDrawer = () => {
    setGame("minecraft");
    setSelectError(false);
    setDrawerOpen((v) => !v);
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
            <div className={clsx("relative", apiKeyError && shakeTick > 0 && "shake")}>
              <input
                type={showKey ? "text" : "password"}
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setApiKeyError(false);
                }}
                onKeyDown={handleKeyPress}
                autoComplete="new-password"
                name="deepseek-api-key-field"
                spellCheck={false}
                className={clsx(
                  "input-forge pr-12",
                  apiKeyError &&
                    "!border-rose-500/50 !ring-1 !ring-rose-500/20 focus:!border-rose-500/50 focus:!ring-rose-500/20"
                )}
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
            {/* API 内联错误提示 */}
            {apiKeyError && (
              <p className="mt-1.5 flex items-center gap-1 text-xs text-rose-400">
                <XCircle size={12} className="text-rose-400" />
                请填写 DeepSeek API Key
              </p>
            )}
          </div>
        </div>

        {/* 目标游戏区 */}
        <div>
          <label className="mb-3 block text-sm font-medium text-zinc-400">
            目标游戏
          </label>
          <div className={clsx("grid grid-cols-2 gap-4 md:grid-cols-3", selectError && shakeTick > 0 && "shake rounded-xl")}>
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
                      : selectError && drawerOpen && game === g.id
                        ? "border-rose-500/50 bg-gradient-to-b from-rose-500/10 to-transparent"
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

          {/* Inline Drawer */}
          {drawerOpen && game === "minecraft" && (
            <div className="drawer-in mt-6 w-full rounded-xl border border-white/5 bg-black/40 p-5 shadow-inner shadow-black/60">
              <div className="grid grid-cols-1 gap-8 sm:grid-cols-2">
                {/* 左列：MOD LOADER（下拉框，与 GAME VERSION 同款；锁定项直接 disabled 不可选） */}
                <div>
                  <div className="mb-3 font-mono text-xs tracking-widest text-zinc-500">
                    MOD LOADER
                  </div>
                  <select
                    value={loader ?? ""}
                    onChange={(e) => {
                      setLoader(e.target.value || null);
                      setSelectError(false);
                    }}
                    className={clsx(
                      "w-full rounded-lg border px-4 py-2 font-mono text-sm outline-none transition-colors duration-150",
                      loader
                        ? "border border-emerald-500/50 bg-emerald-900/40 text-emerald-400"
                        : "border border-zinc-800 bg-black/40 text-zinc-300"
                    )}
                  >
                    <option value="">选择 Loader</option>
                    {LOADERS.map((l) => (
                      <option key={l.id} value={l.id} disabled={l.disabled}>
                        {l.label}
                        {l.disabled ? "（即将支持）" : ""}
                      </option>
                    ))}
                  </select>
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
                      </option>
                    ))}
                  </select>

                  {/* 非最新版本：非阻塞内联警告 */}
                  {versionWarning && (
                    <div className="warn-in mt-2 flex items-start gap-1.5 rounded-lg border border-amber-900/50 bg-amber-950/20 px-3 py-2">
                      <TriangleAlert size={13} className="mt-0.5 shrink-0 text-amber-500/90" />
                      <p className="text-[11px] leading-tight text-amber-500/90">
                        当前非最新版本。高版本生成的 MOD 架构可能具备一定的向下兼容性，但仍存在潜在适配风险，请谨慎测试。
                      </p>
                    </div>
                  )}
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

        {/* 操作区 */}
        <div className="border-t border-zinc-800 pt-6">
          <div className="flex items-center justify-end gap-3">
            <button onClick={handleReset} className="btn-ghost text-zinc-400" type="button">
              <RotateCcw size={14} />
              重置
            </button>
            <button
              onClick={handleCreate}
              disabled={loading}
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
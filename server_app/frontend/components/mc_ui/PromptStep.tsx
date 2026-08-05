"use client";

import { useState } from "react";
import { ArrowLeft, Copy, Sparkles } from "lucide-react";

interface PromptStepProps {
  sessionId: string;
  onBack: () => void;
  onRun: (prompt: string) => Promise<void>;
  /** 受控：MOD 需求文本（父级保存，返回/重进不清空） */
  value: string;
  onChange: (v: string) => void;
}

const TEMPLATES = [
  {
    id: "weapon",
    name: "武器",
    icon: "/assets/mc_diamondsword_icon.png",
    desc: "水晶长剑，特殊附魔与合成配方",
    prompt:
      "新增一把水晶长剑武器 MOD：拥有高攻击力与独特附魔效果，附带可合成的配方（需要水晶与铁锭），并生成对应的物品贴图资源。",
  },
  {
    id: "food",
    name: "食物",
    icon: "/assets/mc_bread_icon.png",
    desc: "魔法果实，恢复生命与速度效果",
    prompt:
      "添加一种魔法果实食物 MOD：使用后可恢复大量生命与饱食度，并赋予短暂的速度提升效果，通过稀有掉落或特定结构获取。",
  },
  {
    id: "block",
    name: "方块",
    icon: "/assets/mc_grassblock_icon.png",
    desc: "发光矿石，开采掉落稀有材料",
    prompt:
      "制作一种发光矿石方块 MOD：在特定群系自然生成，开采掉落稀有材料，可用于合成高级装备，方块本身会发光。",
  },
];

export default function PromptStep({ sessionId, onBack, onRun, value, onChange }: PromptStepProps) {
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const prompt = value;
  const setPrompt = onChange;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sessionId);
    } catch {
      /* 权限受限时忽略 */
    }
  };

  async function handleRun() {
    if (!prompt.trim()) {
      setError("请填写 MOD 需求描述");
      return;
    }
    setRunning(true);
    setError("");
    try {
      await onRun(prompt.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "启动失败");
      setRunning(false);
    }
  }

  return (
    <div className="glass mx-auto max-w-3xl p-6 md:p-8">
      {/* Header：会话 ID 药丸 与 主标题 两端对齐 */}
      <div className="flex items-end justify-between gap-3">
        <h2 className="text-lg font-semibold tracking-wide text-zinc-200">
          描述你的 MOD 需求
        </h2>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 rounded-full border border-white/[0.05] bg-white/[0.03] px-3 py-1 font-mono text-xs text-zinc-500 transition-colors duration-150 hover:bg-white/[0.06] hover:text-zinc-300"
          title="复制会话 ID"
        >
          <Copy size={12} />
          {sessionId}
        </button>
      </div>

      {/* 核心输入区（深邃凹槽） */}
      <div className="relative mt-5">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={7}
          className="w-full resize-y rounded-xl border border-white/[0.05] bg-black/40 p-4 font-mono text-sm leading-relaxed text-zinc-300 shadow-inner shadow-black/50 outline-none transition-all duration-200 placeholder:text-zinc-600 focus:border-emerald-500/40 focus:bg-black/50 focus:ring-2 focus:ring-emerald-500/10"
        />
        <span className="absolute bottom-3 right-3 font-mono text-[10px] text-zinc-600">
          {prompt.length} 字
        </span>
      </div>

      {/* 快速填充 Bento Chips（消灭虚线） */}
      <div className="mt-5">
        <label className="mb-2 flex items-center gap-1.5 text-sm font-medium text-zinc-400">
          <Sparkles size={14} className="text-zinc-500" />
          快速填充
        </label>
        <div className="grid gap-3 sm:grid-cols-3">
          {TEMPLATES.map(({ id, name, icon, desc, prompt: p }) => (
            <button
              key={id}
              onClick={() => setPrompt(p)}
              className="group rounded-xl border border-white/[0.05] bg-white/[0.02] p-4 text-left transition-all duration-300 hover:-translate-y-1 hover:border-emerald-500/30 hover:bg-zinc-800/50 hover:shadow-lg hover:shadow-emerald-900/10"
            >
              <div className="mb-1.5 flex items-center gap-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={icon}
                  alt={name}
                  className="h-7 w-7 object-contain"
                />
                <span className="text-sm font-semibold text-zinc-200 transition-colors duration-300 group-hover:text-emerald-400">
                  {name}
                </span>
              </div>
              <span className="block text-xs leading-relaxed text-zinc-500">
                {desc}
              </span>
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* 底部操作栏 */}
      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-zinc-400 transition-colors duration-200 hover:bg-white/5 hover:text-zinc-200"
        >
          <ArrowLeft size={14} />
          返回
        </button>
        <button
          onClick={handleRun}
          disabled={running}
          className="inline-flex items-center gap-2 rounded-lg border border-emerald-500/50 bg-emerald-600/80 px-6 py-2.5 text-sm font-medium text-emerald-50 transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-500 hover:shadow-[0_0_20px_rgba(16,185,129,0.3)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Sparkles size={16} className={running ? "animate-pulse" : ""} />
          {running ? "启动中..." : "开始生成"}
        </button>
      </div>
    </div>
  );
}
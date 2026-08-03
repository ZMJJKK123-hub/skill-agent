"use client";

import { useState } from "react";
import {
  ArrowLeft,
  Box,
  Cherry,
  Copy,
  Skull,
  Sparkles,
} from "lucide-react";

interface PromptStepProps {
  sessionId: string;
  onBack: () => void;
  onRun: (prompt: string) => Promise<void>;
}

const TEMPLATES = [
  {
    id: "weapon",
    name: "武器",
    icon: Skull,
    desc: "水晶长剑，特殊附魔与合成配方",
    prompt:
      "新增一把水晶长剑武器 MOD：拥有高攻击力与独特附魔效果，附带可合成的配方（需要水晶与铁锭），并生成对应的物品贴图资源。",
  },
  {
    id: "food",
    name: "食物",
    icon: Cherry,
    desc: "魔法果实，恢复生命与速度效果",
    prompt:
      "添加一种魔法果实食物 MOD：使用后可恢复大量生命与饱食度，并赋予短暂的速度提升效果，通过稀有掉落或特定结构获取。",
  },
  {
    id: "block",
    name: "方块",
    icon: Box,
    desc: "发光矿石，开采掉落稀有材料",
    prompt:
      "制作一种发光矿石方块 MOD：在特定群系自然生成，开采掉落稀有材料，可用于合成高级装备，方块本身会发光。",
  },
];

export default function PromptStep({ sessionId, onBack, onRun }: PromptStepProps) {
  const [prompt, setPrompt] = useState("");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

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
      <div className="flex items-center justify-between">
        <span className="mono-label">会话 ID: {sessionId}</span>
        <button onClick={handleCopy} className="btn-ghost !py-1.5">
          <Copy size={14} />
          复制
        </button>
      </div>

      <h2 className="mt-6 text-lg font-bold text-zinc-100">描述你的 MOD 需求</h2>

      {/* 大输入框（施法核心） */}
      <div className="mt-4">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="例：做一个能加血的工具 MOD，右键使用恢复 5 点生命，附带合成配方与对应贴图资源。"
          rows={7}
          className="input-forge !resize-y !rounded-xl !bg-ink-950/60 !shadow-inner-deep !leading-relaxed"
        />
        <div className="mt-1 text-right font-mono text-xs text-zinc-600">
          {prompt.length} 字
        </div>
      </div>

      {/* 示例模板 */}
      <div className="mt-5">
        <label className="mb-2 flex items-center gap-1.5 text-sm font-medium text-zinc-400">
          <Sparkles size={14} className="text-forge-amber" />
          快速填充
        </label>
        <div className="grid gap-3 sm:grid-cols-3">
          {TEMPLATES.map(({ id, name, icon: Icon, desc, prompt: p }) => (
            <button
              key={id}
              onClick={() => setPrompt(p)}
              className="group rounded-xl border border-dashed border-white/10 bg-ink-950/30 p-4 text-left transition-all duration-200 hover:border-forge-purple/50 hover:bg-forge-purple/[0.05]"
            >
              <Icon size={18} className="text-forge-purple" />
              <span className="mt-2 block text-sm font-semibold text-zinc-200">
                {name}
              </span>
              <span className="mt-1 block text-xs leading-relaxed text-zinc-500">
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

      <div className="mt-6 flex items-center justify-between">
        <button onClick={onBack} className="btn-ghost">
          <ArrowLeft size={14} />
          返回
        </button>
        <button onClick={handleRun} disabled={running} className="btn-primary">
          <Sparkles size={16} />
          {running ? "启动中..." : "开始生成"}
        </button>
      </div>
    </div>
  );
}
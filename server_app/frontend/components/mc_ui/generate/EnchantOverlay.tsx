/**
 * EnchantOverlay —— 附魔完成全屏遮罩。
 * 状态机：idle → appear → flip → enchanting → enchanted → done（关闭）。
 * 布局：阶段标题（上）+ 小型附魔书图片（中，3D 动画 + 旋转环）+ 描述/符文（下）。
 * 文字与书图片完全分离、零重叠；漂浮符文 / XP 球 / 底部提示保留。
 */
"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { MC } from "./mcTheme";
import { playMcEnchantSound } from "./mcSfx";

type EnchantPhase = "idle" | "appear" | "flip" | "enchanting" | "enchanted" | "done";

interface EnchantOverlayProps {
  prompt: string;
  onComplete: () => void;
}

const RUNES = "ᛃ⚡✦ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛊᛏᛒ◈⏣⬡".split("");
const COMPLETE_RUNES = "ᛟᚹᛖᚱᚠᚢᛚᛚᛟᚹᛖᚱᚠᚢᛚᛚ".split("");
const PARTICLE_COLORS = ["#A88BC4", "#7EFC20", "#FFD700", "#60A5FA", "#F472B6"];
const ORB_COLORS = ["#A88BC4", "#7EFC20", "#FFD700", "#F472B6", "#60A5FA"];

export default function EnchantOverlay({ prompt, onComplete }: EnchantOverlayProps) {
  const [phase, setPhase] = useState<EnchantPhase>("idle");
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  // 挂载即启动动画序列
  useEffect(() => {
    setPhase("appear");
    timers.current.push(
      setTimeout(() => setPhase("flip"), 750),
      setTimeout(() => {
        setPhase("enchanting");
        playMcEnchantSound(() => {
          setPhase("enchanted");
          timers.current.push(setTimeout(() => setPhase("done"), 2000));
        });
      }, 1650),
      // 兜底：8s 后强制结束，避免音效失败卡死遮罩
      setTimeout(() => setPhase("done"), 8000)
    );
    return () => timers.current.forEach(clearTimeout);
  }, []);

  // 结束回调
  useEffect(() => {
    if (phase === "done") onComplete();
  }, [phase, onComplete]);

  // 稳定随机：悬浮符文（65 个）
  const particles = useMemo(
    () =>
      Array.from({ length: 65 }, (_, i) => ({
        left: `${(i * 37) % 100}%`,
        top: `${(i * 53) % 100}%`,
        delay: `${((i * 37) % 30) / 10}s`,
        fontSize: `${14 + ((i * 17) % 32)}px`,
        color: PARTICLE_COLORS[i % PARTICLE_COLORS.length],
        char: RUNES[i % RUNES.length],
      })),
    []
  );

  // 稳定随机：XP 球（14 个）
  const orbs = useMemo(
    () =>
      Array.from({ length: 14 }, (_, i) => ({
        background: ORB_COLORS[i % ORB_COLORS.length],
        delay: `${i * 0.08}s`,
      })),
    []
  );

  if (phase === "idle" || phase === "done") return null;

  const showingRings = phase === "enchanting" || phase === "enchanted";
  const enchanted = phase === "enchanted";
  const bookClass =
    phase === "appear"
      ? "mc-a-appear"
      : phase === "flip"
        ? "mc-a-flip"
        : phase === "enchanting"
          ? "mc-a-enchanting"
          : phase === "enchanted"
            ? "mc-a-enchanted"
            : "";

  /** 阶段标题（独立显示在书图片上方，不与图片重叠） */
  const title = phase === "flip" ? "📜 翻页中..." : enchanted ? "附魔完成!" : "📖 需求之书";

  const tip =
    phase === "appear"
      ? "§a* 翻开需求之书... *"
      : phase === "flip"
        ? "§e* 书页翻动中... *"
        : phase === "enchanting"
          ? "§d✦ 奥术能量涌动！✦"
          : "§5✦ Mod已附魔成功！✦";

  return (
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center"
      style={{ background: "rgba(0,0,0,0.94)" }}
    >
      {/* 漂浮符文 */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        {particles.map((p, i) => (
          <span
            key={i}
            className="absolute font-mono"
            style={{
              left: p.left,
              top: p.top,
              fontSize: p.fontSize,
              color: p.color,
              animation: `mcRFloat 3.5s ease-in-out ${p.delay} infinite`,
            }}
          >
            {p.char}
          </span>
        ))}
      </div>

      {/* 中央内容列：标题 → 小图框 → 描述/符文 */}
      <div
        className="relative flex flex-col items-center"
        style={{ gap: 22, maxWidth: 340 }}
      >
        {/* 阶段标题（独立） */}
        <div
          style={{
            fontSize: 24,
            fontWeight: 700,
            textAlign: "center",
            color: enchanted ? MC.RUNE_UP : "#D7CCC8",
            textShadow: enchanted
              ? "0 2px 0 #000, 0 0 12px rgba(151,122,168,0.8)"
              : "0 2px 0 #000",
          }}
        >
          {title}
        </div>

        {/* 书舞台：小型附魔书图框 + 旋转环 + 3D 动画 */}
        <div className="relative" style={{ width: 200, height: 200, perspective: 800 }}>
          <div className="absolute inset-0 grid place-items-center">
            {/* 小图框（带 3D 动画，居中不依赖 transform） */}
            <div
              className={`relative ${bookClass}`}
              style={{
                width: 112,
                height: 144,
                background: "#000",
                border: `3px solid ${enchanted ? "#5A3E6A" : "#3A2508"}`,
                boxShadow: enchanted
                  ? "0 0 24px rgba(151,122,168,0.5)"
                  : "0 4px 16px rgba(0,0,0,0.7)",
              }}
            >
              {/* 旋转环（围绕小图框） */}
              {showingRings && (
                <>
                  <div
                    className="absolute rounded-full border-2 border-dashed"
                    style={{ inset: -16, borderColor: "rgba(126,252,32,0.35)", animation: "mcRingSpin 4s linear infinite" }}
                  />
                  <div
                    className="absolute rounded-full border-2 border-dashed"
                    style={{ inset: -28, borderColor: "rgba(151,122,168,0.3)", animation: "mcRingSpin 3s linear infinite reverse" }}
                  />
                  <div
                    className="absolute rounded-full border-2 border-dashed"
                    style={{ inset: -40, borderColor: "rgba(255,215,0,0.15)", animation: "mcRingSpin 5s linear infinite" }}
                  />
                </>
              )}

              {/* 真实附魔书图片 */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src="/assets/mc_enchantedbook.png"
                alt="附魔书"
                className="h-full w-full object-contain [image-rendering:pixelated]"
                style={{
                  filter: enchanted
                    ? "drop-shadow(0 0 12px rgba(151,122,168,0.7))"
                    : undefined,
                }}
              />
            </div>
          </div>

          {/* XP 球（书舞台下方） */}
          {showingRings && (
            <div className="absolute flex gap-[5px]" style={{ bottom: 6, left: "50%", transform: "translateX(-50%)" }}>
              {orbs.map((o, i) => (
                <span
                  key={i}
                  className="rounded-full"
                  style={{
                    width: 9,
                    height: 9,
                    background: o.background,
                    boxShadow: `0 0 8px ${o.background}`,
                    animation: `mcOrbFloat 1.4s ease-out ${o.delay} infinite`,
                  }}
                />
              ))}
            </div>
          )}
        </div>

        {/* 下方文字（独立，不与图片重叠）：prompt 描述卡 / 符文行 */}
        {enchanted ? (
          <div className="flex gap-1">
            {COMPLETE_RUNES.map((r, i) => (
              <span
                key={i}
                style={{
                  fontSize: 15,
                  color: MC.RUNE_UP,
                  animation: "mcEGlow 0.8s ease-in-out infinite",
                  animationDelay: `${i * 0.05}s`,
                }}
              >
                {r}
              </span>
            ))}
          </div>
        ) : phase !== "flip" ? (
          <div
            style={{
              padding: "8px 10px",
              background: "rgba(0,0,0,0.2)",
              border: "1px solid rgba(255,255,255,0.06)",
              maxWidth: 240,
            }}
          >
            <p style={{ fontSize: 11, color: "#BCAAA4", lineHeight: 1.4, maxHeight: 64, overflow: "hidden", textAlign: "center" }}>
              {prompt}
            </p>
          </div>
        ) : (
          <div style={{ fontSize: 30, opacity: 0.25 }}>📄</div>
        )}
      </div>

      {/* 底部提示 */}
      <div
        className="absolute text-center"
        style={{
          bottom: 48,
          left: "50%",
          transform: "translateX(-50%)",
          fontSize: 18,
          fontWeight: 700,
          color: MC.XP_TOP,
          textShadow: "0 2px 0 #000, 0 0 8px rgba(126,252,32,0.6)",
        }}
      >
        {tip}
      </div>
    </div>
  );
}
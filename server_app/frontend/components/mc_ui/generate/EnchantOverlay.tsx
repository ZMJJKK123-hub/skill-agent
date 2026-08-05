/**
 * EnchantOverlay —— 附魔完成全屏遮罩。
 * 状态机：idle → appear → flip → enchanting → enchanted → done（关闭）。
 * 书舞台（perspective）+ 旋转环 + 漂浮符文 + XP 球 + 底部提示；enchanting 阶段触发附魔音效。
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
  const enchanted = phase === "enchanted";

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

      {/* 书舞台 */}
      <div className="relative" style={{ width: 280, height: 360, perspective: 1000 }}>
        {/* 旋转环 */}
        {showingRings && (
          <>
            <div
              className="absolute rounded-full border-2 border-dashed"
              style={{ inset: -28, borderColor: "rgba(126,252,32,0.35)", animation: "mcRingSpin 4s linear infinite" }}
            />
            <div
              className="absolute rounded-full border-2 border-dashed"
              style={{ inset: -46, borderColor: "rgba(151,122,168,0.3)", animation: "mcRingSpin 3s linear infinite reverse" }}
            />
            <div
              className="absolute rounded-full border-2 border-dashed"
              style={{ inset: -64, borderColor: "rgba(255,215,0,0.15)", animation: "mcRingSpin 5s linear infinite" }}
            />
          </>
        )}

        {/* 附魔书 */}
        <div
          className={`relative h-full w-full ${bookClass}`}
          style={{
            background: enchanted
              ? "linear-gradient(135deg,#A88BC4,#977AA8,#6A4E7A)"
              : "linear-gradient(135deg,#7A5C1E,#654B17,#4E380E)",
            border: `3px solid ${enchanted ? "#5A3E6A" : "#3A2508"}`,
            boxShadow: enchanted
              ? "inset 0 2px 0 rgba(255,255,255,0.1), 0 0 30px rgba(151,122,168,0.6), 0 0 80px rgba(151,122,168,0.2)"
              : "inset 0 2px 0 rgba(255,255,255,0.1), 0 6px 24px rgba(0,0,0,0.7)",
            transition: "all .5s",
          }}
        >
          {/* 书脊 */}
          <div
            className="absolute left-0 top-0 h-full"
            style={{ width: 24, background: "linear-gradient(90deg,#4E380E,#654B17)", borderRight: "2px solid #2A1800" }}
          />
          {/* 封面装饰线 */}
          <div className="absolute h-px" style={{ left: 24, right: 5, top: 38, background: "rgba(255,255,255,0.08)" }} />
          <div className="absolute h-px" style={{ left: 24, right: 5, bottom: 38, background: "rgba(255,255,255,0.08)" }} />
          {/* 书内容 */}
          <div className="absolute left-[24px] right-0 top-0 flex h-full flex-col items-center justify-center p-[24px]">
            {phase === "flip" ? (
              <>
                <span style={{ fontSize: 18, color: "#D7CCC8", fontWeight: 700, textShadow: "0 2px 0 #000" }}>
                  📜 翻页中...
                </span>
                <div style={{ marginTop: 12, fontSize: 38, opacity: 0.25 }}>📄</div>
              </>
            ) : enchanted ? (
              <>
                <span style={{ fontSize: 40 }}>📚</span>
                <div style={{ marginTop: 8 }}>
                  <span
                    style={{
                      fontSize: 26,
                      fontWeight: 700,
                      color: MC.RUNE_UP,
                      textShadow: "0 2px 0 #000, 0 0 10px rgba(151,122,168,0.9), 0 0 24px rgba(151,122,168,0.5)",
                      animation: "mcEGlow 1s ease-in-out infinite",
                    }}
                  >
                    附魔完成!
                  </span>
                </div>
                <div className="mt-2 flex gap-1">
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
              </>
            ) : (
              <>
                <span style={{ fontSize: 18, color: "#D7CCC8", fontWeight: 700, textShadow: "0 2px 0 #000" }}>
                  📖 需求之书
                </span>
                <div
                  style={{
                    marginTop: 10,
                    padding: "8px 10px",
                    background: "rgba(0,0,0,0.2)",
                    border: "1px solid rgba(255,255,255,0.06)",
                    maxWidth: 190,
                  }}
                >
                  <p style={{ fontSize: 11, color: "#BCAAA4", lineHeight: 1.4, maxHeight: 64, overflow: "hidden" }}>
                    {prompt}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* XP 球 */}
        {showingRings && (
          <div className="absolute flex gap-[5px]" style={{ bottom: -44, left: "50%", transform: "translateX(-50%)" }}>
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

      {/* 底部提示 */}
      <div
        className="absolute text-center"
        style={{
          bottom: 150,
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
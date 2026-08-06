"use client";

import { useEffect, useState, useRef } from "react";
import clsx from "clsx";

interface McEnchantAnimationProps {
  trigger: boolean;
  onComplete?: () => void;
  promptText?: string;
}

/** 播放MC原版附魔音效 - 低沉的嗡声+魔法升调 */
function playEnchantSound(onDone?: () => void) {
  try {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const now = ctx.currentTime;

    // 第一阶段：低沉持续嗡声（类似附魔台的嗡嗡声）
    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain1 = ctx.createGain();
    osc1.type = "sine";
    osc2.type = "sine";
    osc1.frequency.setValueAtTime(80, now);
    osc2.frequency.setValueAtTime(120, now);
    osc1.frequency.linearRampToValueAtTime(40, now + 2.0);
    osc2.frequency.linearRampToValueAtTime(60, now + 2.0);
    gain1.gain.setValueAtTime(0.08, now);
    gain1.gain.exponentialRampToValueAtTime(0.001, now + 2.5);
    osc1.connect(gain1);
    osc2.connect(gain1);
    gain1.connect(ctx.destination);
    osc1.start(now);
    osc2.start(now);
    osc1.stop(now + 2.5);
    osc2.stop(now + 2.5);

    // 第二阶段：宇宙升调（附魔完成的高亮音）
    const notes2 = [200, 300, 400, 520, 660, 800, 1000, 1200, 1400];
    const start2 = now + 1.0;
    notes2.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, start2 + i * 0.12);
      gain.gain.setValueAtTime(0.12, start2 + i * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.001, start2 + i * 0.12 + 0.3);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(start2 + i * 0.12);
      osc.stop(start2 + i * 0.12 + 0.3);
    });

    // 第三阶段：附魔完成爆音
    const boomFreqs = [150, 300, 450, 600, 900, 1200];
    const start3 = now + 2.2;
    boomFreqs.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = i < 3 ? "square" : "sine";
      osc.frequency.setValueAtTime(freq * 2, start3);
      osc.frequency.exponentialRampToValueAtTime(freq, start3 + 0.8);
      gain.gain.setValueAtTime(0.15, start3);
      gain.gain.exponentialRampToValueAtTime(0.001, start3 + 0.8);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(start3);
      osc.stop(start3 + 0.8);
    });

    setTimeout(() => {
      ctx.close();
      onDone?.();
    }, 3200);
  } catch (_) {
    onDone?.();
  }
}

export default function McEnchantAnimation({
  trigger,
  onComplete,
  promptText = "请帮我生成一个Mod...",
}: McEnchantAnimationProps) {
  const [phase, setPhase] = useState<
    "idle" | "bookAppear" | "reading" | "flip" | "enchanting" | "enchanted" | "done"
  >("idle");
  const hasTriggered = useRef(false);

  useEffect(() => {
    if (!trigger || hasTriggered.current) return;
    hasTriggered.current = true;

    // 书籍出现动画序列
    const t1 = setTimeout(() => setPhase("bookAppear"), 100);      // 书出现
    const t2 = setTimeout(() => setPhase("reading"), 800);          // 阅读中（显示提示词）
    const t3 = setTimeout(() => setPhase("flip"), 1800);            // 开始翻页
    const t4 = setTimeout(() => {
      setPhase("enchanting");
      playEnchantSound(() => {
        setPhase("enchanted");                                      // 附魔完成
        setTimeout(() => {
          setPhase("done");
          onComplete?.();
        }, 2000);
      });
    }, 2600);

    return () => {
      [t1, t2, t3, t4].forEach(clearTimeout);
    };
  }, [trigger, onComplete]);

  if (phase === "idle" || phase === "done") return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90">
      {/* 附魔粒子背景 */}
      {(phase === "enchanting" || phase === "enchanted") && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* 银河文字粒子 */}
          {Array.from({ length: 50 }).map((_, i) => (
            <span
              key={i}
              className="absolute animate-[floatRune_3s_ease-in-out_infinite] font-mono"
              style={{
                left: Math.random() * 100 + "%",
                top: Math.random() * 100 + "%",
                animationDelay: Math.random() * 2 + "s",
                fontSize: Math.random() * 20 + 12 + "px",
                color: ["#AA00FF", "#00FFAA", "#FFD700", "#FF00FF", "#00AAFF"][Math.floor(Math.random() * 5)],
                opacity: 0.6,
              }}
            >
              {["ᛃ", "⚡", "✦", "◈", "⏣", "⬡", "ᚠ", "ᚢ", "ᚦ", "ᚨ", "ᚱ", "ᚲ", "ᚷ", "ᚹ", "ᚺ", "ᚾ", "ᛁ", "ᛊ", "ᛏ", "ᛒ"][
                Math.floor(Math.random() * 20)
              ]}
            </span>
          ))}
        </div>
      )}

      {/* 书本容器 */}
      <div
        className={clsx(
          "relative transition-all duration-700",
          phase === "bookAppear" && "animate-[bookAppear_0.6s_ease-out]",
          phase === "reading" && "scale-100",
          phase === "flip" && "animate-[bookFlip_0.8s_ease-in-out]",
          phase === "enchanting" && "scale-110",
          phase === "enchanted" && "scale-105"
        )}
        style={{ perspective: "800px" }}
      >
        {/* 附魔时的旋转光环 */}
        {(phase === "enchanting" || phase === "enchanted") && (
          <>
            <div className="absolute -inset-6 animate-spin rounded-full border-2 border-dashed border-[#AA00FF]/40 [animation-duration:4s]" />
            <div className="absolute -inset-10 animate-spin rounded-full border border-dashed border-[#00FFAA]/25 [animation-duration:3s] [animation-direction:reverse]" />
            <div className="absolute -inset-14 animate-spin rounded-full border border-dashed border-[#FFD700]/15 [animation-duration:5s]" />
          </>
        )}

        {/* 书本本体 */}
        <div
          className={clsx(
            "relative h-64 w-80 transition-all duration-500 shadow-2xl",
            phase === "enchanted"
              ? "rounded-md border-3 border-[#AA00FF] bg-gradient-to-br from-[#1a0020] to-[#0d0015] shadow-[0_0_80px_rgba(170,0,255,0.7),0_0_200px_rgba(170,0,255,0.2)]"
              : "rounded-md border-3 border-[#5D4037] bg-gradient-to-br from-[#6D4C41] to-[#3E2723] shadow-[0_0_40px_rgba(139,69,19,0.4)]"
          )}
        >
          {/* 书脊（左侧） */}
          <div className="absolute left-0 top-0 h-full w-6 rounded-l-sm bg-gradient-to-r from-[#4E342E] to-[#5D4037] border-r border-[#3E2723]/50" />

          {/* 书的内容区域 */}
          <div className="absolute left-6 right-0 top-0 h-full flex flex-col items-center justify-center p-6">
            {phase === "enchanted" ? (
              /* 附魔完成 - 紫色发光附魔书 */
              <>
                {/* 附魔书封面装饰 */}
                <div
                  className="mb-3 text-5xl animate-[enchantGlow_0.8s_ease-in-out_infinite]"
                  style={{
                    filter: "drop-shadow(0 0 20px rgba(170,0,255,0.9)) drop-shadow(0 0 40px rgba(255,0,255,0.5))",
                    imageRendering: "pixelated",
                  }}
                >
                  📚
                </div>
                <div className="animate-[enchantGlow_0.8s_ease-in-out_infinite]">
                  <span
                    className="text-3xl font-bold tracking-widest"
                    style={{
                      color: "#FF00FF",
                      fontFamily: "'Minecraft', 'Courier New', monospace",
                      textShadow: "0 0 20px rgba(255,0,255,0.9), 0 0 40px rgba(170,0,255,0.7), 0 0 80px rgba(170,0,255,0.4)",
                    }}
                  >
                    附魔完成!
                  </span>
                </div>
                {/* 银河附魔符文 */}
                <div className="mt-3 flex gap-1 opacity-70">
                  {Array.from({ length: 16 }).map((_, i) => (
                    <span
                      key={i}
                      className="text-xs animate-[enchantGlow_0.6s_ease-in-out_infinite]"
                      style={{
                        color: ["#AA00FF", "#FF00FF", "#FFD700", "#00FFAA"][i % 4],
                        animationDelay: i * 0.05 + "s",
                        textShadow: "0 0 6px currentColor",
                      }}
                    >
                      {["ᛟ", "ᚹ", "ᛖ", "ᚱ", "ᚠ", "ᚢ", "ᛚ", "ᛚ", "ᛟ", "ᚹ", "ᛖ", "ᚱ", "ᚠ", "ᚢ", "ᛚ", "ᛚ"][i]}
                    </span>
                  ))}
                </div>
              </>
            ) : (
              /* 普通书状态 - 显示提示词 */
              <>
                {/* 书本标题 */}
                <span
                  className="text-lg font-bold mb-2"
                  style={{
                    color: "#D7CCC8",
                    fontFamily: "'Minecraft', 'Courier New', monospace",
                    textShadow: "0 2px 0 rgba(0,0,0,0.5)",
                  }}
                >
                  {phase === "flip" ? "📜 翻页中..." : "📖 需求之书"}
                </span>

                {/* 提示词内容 - 书页上的文字 */}
                <div
                  className="w-full max-w-[200px] text-center px-3 py-2 rounded"
                  style={{
                    background: "rgba(0,0,0,0.15)",
                    border: "1px solid rgba(255,255,255,0.05)",
                  }}
                >
                  <p
                    className="text-xs leading-relaxed line-clamp-4"
                    style={{
                      color: "#BCAAA4",
                      fontFamily: "'Minecraft', 'Courier New', monospace",
                    }}
                  >
                    {promptText}
                  </p>
                </div>

                {/* 书页边角装饰 */}
                <div className="absolute bottom-4 right-6 h-8 w-8 rounded-sm border border-[#8D6E63]/20" />
                <div className="absolute right-6 top-4 h-3 w-3 rounded-full border border-[#8D6E63]/20" />

                {/* 翻页时的书页效果 */}
                {phase === "flip" && (
                  <div className="absolute inset-6 flex items-center justify-center pointer-events-none">
                    <div className="animate-[bookFlip_0.8s_ease-in-out] text-4xl opacity-30">📄</div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* 书封面压花装饰 */}
          <div
            className={clsx(
              "absolute right-4 bottom-4 w-12 h-12 rounded-sm border transition-colors duration-500",
              phase === "enchanted" ? "border-[#AA00FF]/40" : "border-[#8D6E63]/30"
            )}
          />
          <div
            className={clsx(
              "absolute right-4 top-4 w-5 h-5 rounded-full border transition-colors duration-500",
              phase === "enchanted" ? "border-[#AA00FF]/40" : "border-[#8D6E63]/30"
            )}
          />
        </div>

        {/* 附魔时的经验球粒子 */}
        {(phase === "enchanting" || phase === "enchanted") && (
          <div className="absolute -bottom-14 left-1/2 -translate-x-1/2 flex gap-2">
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={i}
                className="h-3 w-3 animate-[xpOrb_1.5s_ease-out_infinite] rounded-full"
                style={{
                  background: ["#AA00FF", "#00FF00", "#FFD700", "#FF00FF", "#00FFAA", "#AA00FF"][i % 6],
                  boxShadow: `0 0 12px currentColor`,
                  animationDelay: i * 0.12 + "s",
                  imageRendering: "pixelated",
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* 底部状态文字 */}
      <div className="absolute bottom-20 left-1/2 -translate-x-1/2 text-center">
        <span
          className={clsx(
            "text-lg font-bold animate-pulse",
            phase === "enchanted" ? "text-[#FF00FF]" : "text-[#00FFAA]"
          )}
          style={{
            fontFamily: "'Minecraft', 'Courier New', monospace",
            textShadow: phase === "enchanted"
              ? "0 0 12px rgba(255,0,255,0.8)"
              : "0 0 12px rgba(0,255,170,0.8)",
          }}
        >
          {phase === "bookAppear" && "§a* 翻开需求之书... *"}
          {phase === "reading" && "§7* 正在阅读提示词... *"}
          {phase === "flip" && "§e* 书页翻动中... *"}
          {phase === "enchanting" && "§d✦ 奥术能量涌动中! ✦"}
          {phase === "enchanted" && "§5✦ 附魔完成! Mod已生成! ✦"}
        </span>
      </div>
    </div>
  );
}

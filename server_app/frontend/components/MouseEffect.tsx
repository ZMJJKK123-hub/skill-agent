"use client";

import { useEffect } from "react";

/**
 * MouseEffect —— 鼠标点击粒子 + 动态光标
 *
 * 仅当 selectedGame 命中某个游戏主题时才生效（严格状态条件触发）。
 * 目前只有 minecraft 主题；其它游戏返回空渲染，且不绑定任何事件。
 *
 * 扩展方式：在 GAME_THEMES 里为其它游戏加一项，即可获得粒子色/光标样式，
 * 无需改动事件逻辑。
 */

type ThemeConfig = {
  /** 粒子颜色数组（多色随机） */
  particleColors: string[];
  /** 粒子大小范围 [min, max]（px） */
  particleSize: [number, number];
  /** 粒子寿命范围 [min, max]（ms） */
  lifetime: [number, number];
  /** 点击时粒子数 */
  count: number;
  /** 是否启用主题光标（body class） */
  customCursor: boolean;
  /** 光标 class 名（由全局 CSS 定义） */
  cursorClass: string;
};

/** 游戏主题配置字典 —— 平行扩展其它游戏只需加一项 */
const GAME_THEMES: Record<string, ThemeConfig> = {
  minecraft: {
    // 青翠绿 / 附魔紫：对应草方块与下界传送门
    particleColors: ["#34d399", "#4ade80", "#a78bfa", "#c084fc", "#fbbf24"],
    particleSize: [3, 6],
    lifetime: [450, 850],
    count: 10,
    customCursor: true,
    cursorClass: "theme-minecraft-cursor",
  },
  // 预留示例：stardew_valley: { ... 自然绿 / 阳光黄 ... }
};

function spawnParticles(e: MouseEvent, cfg: ThemeConfig) {
  for (let i = 0; i < cfg.count; i++) {
    const size =
      cfg.particleSize[0] + Math.random() * (cfg.particleSize[1] - cfg.particleSize[0]);
    const color = cfg.particleColors[
      Math.floor(Math.random() * cfg.particleColors.length)
    ] as string;
    const lifetime =
      cfg.lifetime[0] + Math.random() * (cfg.lifetime[1] - cfg.lifetime[0]);

    const el = document.createElement("span");
    el.style.cssText = [
      "position:fixed",
      "pointer-events:none",
      "z-index:9999",
      `left:${e.clientX}px`,
      `top:${e.clientY}px`,
      `width:${size}px`,
      `height:${size}px`,
      `background:${color}`,
      "border-radius:2px",
      "opacity:1",
      "transform:translate(-50%,-50%) scale(1)",
    ].join(";") + ";";

    // 用 Web Animations API 做飞出+淡出，简单可靠
    const dx = (Math.random() - 0.5) * 60;
    const dy = (Math.random() - 0.5) * 60;
    el.animate(
      [
        { transform: "translate(-50%,-50%) scale(1)", opacity: 1 },
        {
          transform: `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px)) scale(0.2)`,
          opacity: 0,
        },
      ],
      { duration: lifetime, easing: "cubic-bezier(0.2, 0.8, 0.4, 1)" }
    ).onfinish = () => el.remove();

    document.body.appendChild(el);
  }
}

interface MouseEffectProps {
  /** 当前选中的目标游戏（来自页面 state） */
  selectedGame: string;
}

export default function MouseEffect({ selectedGame }: MouseEffectProps) {
  useEffect(() => {
    const theme = GAME_THEMES[selectedGame];
    // 严格条件触发：无该游戏主题时，绝不添加监听/光标 class
    if (!theme) return;

    // 1) 光标动态切换
    if (theme.customCursor) {
      document.body.classList.add(theme.cursorClass);
    }

    // 2) 点击粒子
    const handler = (e: MouseEvent) => {
      // 提前返回：非 minecraft（或无主题）时零开销
      if (!GAME_THEMES[selectedGame]) return;
      spawnParticles(e, theme);
    };
    window.addEventListener("click", handler);

    // cleanup：离开 / 切换游戏 / 卸载时清干净
    return () => {
      window.removeEventListener("click", handler);
      if (theme.customCursor) {
        document.body.classList.remove(theme.cursorClass);
      }
    };
  }, [selectedGame]);

  // 无任何视觉元素（粒子/光标都是副作用）
  return null;
}
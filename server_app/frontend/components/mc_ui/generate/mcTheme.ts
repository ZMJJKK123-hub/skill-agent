/**
 * mcTheme —— MC 原版 UI 精确取色常量 + 复杂 3D/关键帧动画注入。
 *
 * 所有数值提取自 mod_material/mc-ui-preview-v3.html（图片精确取色版）。
 * Tailwind 盲区（复杂 @keyframes / perspective / border-image）的合法解：
 *   - 3D 附魔动画与透视：集中在此注入 <style> 标签，React 内按状态切换 className。
 *   - MC 3D 凸起按钮：MC_BTN_BORDER 内联 borderImage 常量。
 */

export const MC = {
  /* ---- 经验条（精确取色） ---- */
  XP_TOP: "#7EFC20",
  XP_MID: "#4C9813",
  XP_BOTTOM: "#223D22",
  XP_TRACK: "#262846",
  XP_TRACK_BORDER: "#1A1C33",
  XP_GLOW: "rgba(126,252,32,0.8)",

  /* ---- 面板 / 文字 ---- */
  BG: "#0D0D0D",
  TEXT: "#BFBFBF",
  PANEL_BORDER: "#373737",
  PANEL_BG: "rgba(0,0,0,0.75)",
  CARD_BG: "#262846",
  CARD_BORDER: "#1A1C33",
  LABEL: "#808090",

  /* ---- MC 3D 凸起按钮 ---- */
  BTN_LIGHT: "#C6C6C6",
  BTN_DARK: "#373737",
  BTN_BORDER: "repeating-linear-gradient(180deg, #C6C6C6, #8B8B8B 50%, #555555) 2",

  /* ---- 附魔书 ---- */
  BOOK_BROWN: "#654B17",
  BOOK_PURPLE: "#977AA8",
  RUNE_UP: "#A88BC4",
} as const;

export const PHASES = [
  { label: "思考", icon: "📖" },
  { label: "执行", icon: "⛏️" },
  { label: "生成", icon: "🔧" },
  { label: "附魔完成", icon: "📚" },
] as const;

/** 最大经验等级（0-30） */
export const MAX_XP = 30;

/** MC 复杂 3D / 关键帧动画全局样式（Tailwind 盲区解决方案） */
export const MC_ANIMATION_CSS = `
@keyframes mcBlink{0%,100%{opacity:1}50%{opacity:.2}}
@keyframes mcXpShine{0%{transform:translateX(-100%)}100%{transform:translateX(180%)}}
@keyframes mcFlashOut{0%{opacity:1}100%{opacity:0}}
@keyframes mcPopUp{0%{opacity:1;transform:translateY(0)}100%{opacity:0;transform:translateY(-18px)}}
@keyframes mcEvIn{0%{opacity:0;transform:translateY(3px)}100%{opacity:1;transform:translateY(0)}}
@keyframes mcRFloat{0%,100%{transform:translateY(40px) rotate(0);opacity:0}20%{opacity:.7}80%{opacity:.3}100%{transform:translateY(-50px) rotate(360deg);opacity:0}}
@keyframes mcRingSpin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
@keyframes mcBookAppear{0%{transform:scale(.3) rotateY(90deg);opacity:0}100%{transform:scale(1) rotateY(0);opacity:1}}
@keyframes mcBookFlip{0%{transform:rotateY(0)}50%{transform:rotateY(85deg)}100%{transform:rotateY(0)}}
@keyframes mcBookSpin{0%{transform:rotateY(0)}50%{transform:rotateY(180deg) scale(1.04)}100%{transform:rotateY(360deg) scale(1)}}
@keyframes mcOrbFloat{0%{transform:translateY(0) scale(.4);opacity:0}25%{opacity:1;transform:translateY(-6px) scale(1.2)}100%{transform:translateY(-36px) scale(.2);opacity:0}}
@keyframes mcEGlow{0%,100%{opacity:.8;filter:brightness(1)}50%{opacity:1;filter:brightness(1.3)}}
.mc-a-appear{animation:mcBookAppear .55s ease-out}
.mc-a-flip{animation:mcBookFlip .7s ease-in-out}
.mc-a-enchanting{transform:scale(1.1)}
.mc-a-enchanted{animation:mcBookSpin .9s ease-in-out}
`;
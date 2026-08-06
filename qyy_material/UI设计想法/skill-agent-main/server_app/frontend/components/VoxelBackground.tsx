/**
 * VoxelBackground —— "The Deep Dark Forge"
 *
 * 四层 Minecraft 主题深色背景：
 *   L1  Base & Pixel Grid        深黑曜石底 + 极淡像素网格
 *   L2  Landscape Silhouettes    右下角 90° 直角阶梯地形
 *   L3  Iconic Mobs              Creeper 荧光绿脸 + Enderman 紫色眼 + Pixel Pig 线框
 *   L4  Dynamic Particles        XP 方块上浮 + 下界紫色 portal 微尘
 *
 * 约束：整体装饰 opacity <= 30%，中央径向压暗保证文字可读，零外链图片。
 */

const PIXEL_GRID_URI =
  "data:image/svg+xml," +
  encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' width='48' height='48'><path d='M0 0h48v48H0z' fill='none'/><path d='M0 24h48M24 0v48' stroke='rgba(255,255,255,0.5)' stroke-width='1'/></svg>`
  );

/** 90° 直角阶梯地形（右下角，隐藏感） */
function TerrainSilhouette() {
  // 严格直角：用 rect 堆叠出块状丘陵
  const blocks = [
    { x: 60, y: 640, w: 120, h: 200 },
    { x: 180, y: 680, w: 140, h: 160 },
    { x: 320, y: 710, w: 120, h: 130 },
    { x: 440, y: 750, w: 160, h: 90 },
    { x: 600, y: 770, w: 140, h: 70 },
  ];
  return (
    <svg
      viewBox="0 0 1000 900"
      preserveAspectRatio="xMaxYMax slice"
      className="absolute bottom-0 right-0 w-full opacity-20"
      aria-hidden
    >
      {blocks.map((b, i) => (
        <rect
          key={i}
          x={b.x}
          y={b.y}
          width={b.w}
          height={b.h}
          fill="#18181b"
        />
      ))}
      {/* 块间勾缝线，强化 Voxel 感 */}
      {blocks.map((b, i) => (
        <g key={`l-${i}`} stroke="rgba(0,0,0,0.35)" strokeWidth="2">
          <line x1={b.x} y1={b.y + b.h * 0.5} x2={b.x + b.w} y2={b.y + b.h * 0.5} />
        </g>
      ))}
    </svg>
  );
}

/** Creeper 脸 —— 融入黑暗，仅眼/嘴荧光绿 */
function CreeperFace() {
  return (
    <div className="absolute right-[6%] top-[10%] opacity-25">
      <svg width="180" height="220" viewBox="0 0 180 220" aria-hidden>
        <g fill="#0a0a0a">
          <rect x="15" y="15" width="150" height="190" rx="6" />
        </g>
        {/* 荧光绿眼 */}
        <g fill="#4ade80">
          <rect x="35" y="55" width="38" height="42" style={{ filter: "drop-shadow(0 0 14px rgba(74,222,128,0.7))" }} />
          <rect x="105" y="55" width="38" height="42" style={{ filter: "drop-shadow(0 0 14px rgba(74,222,128,0.7))" }} />
        </g>
        {/* 荧光绿嘴 */}
        <g fill="#4ade80">
          <rect x="35" y="130" width="34" height="16" style={{ filter: "drop-shadow(0 0 12px rgba(74,222,128,0.6))" }} />
          <rect x="50" y="146" width="80" height="12" style={{ filter: "drop-shadow(0 0 12px rgba(74,222,128,0.5))" }} />
          <rect x="71" y="158" width="10" height="12" />
          <rect x="99" y="158" width="10" height="12" />
        </g>
      </svg>
    </div>
  );
}

/** Enderman —— 远处紫色像素眼，极慢呼吸 */
function EndermanEyes() {
  return (
    <div className="absolute left-[8%] top-[20%] opacity-20">
      <div className="flex gap-3 animate-[breathe_4s_ease-in-out_infinite]">
        <span className="block h-3 w-2.5 bg-purple-500/80 blur-[1px]" />
        <span className="block h-3 w-2.5 bg-purple-500/80 blur-[1px]" />
      </div>
    </div>
  );
}

/** Pixel Pig —— 地表线框猪 */
function PixelPig() {
  return (
    <div className="absolute bottom-[6%] left-[12%] opacity-20">
      <svg width="150" height="100" viewBox="0 0 150 100" fill="none" aria-hidden>
        {/* 身体 */}
        <rect x="35" y="30" width="80" height="45" stroke="rgba(113,113,122,0.8)" strokeWidth="2" />
        {/* 头 */}
        <rect x="105" y="40" width="32" height="30" stroke="rgba(113,113,122,0.8)" strokeWidth="2" />
        {/* 鼻 */}
        <rect x="132" y="45" width="10" height="16" stroke="rgba(161,161,170,0.7)" strokeWidth="2" />
        {/* 腿 */}
        <rect x="42" y="72" width="12" height="20" stroke="rgba(113,113,122,0.8)" strokeWidth="2" />
        <rect x="92" y="72" width="12" height="20" stroke="rgba(113,113,122,0.8)" strokeWidth="2" />
        {/* 耳朵 */}
        <rect x="105" y="30" width="10" height="10" stroke="rgba(113,113,122,0.8)" strokeWidth="2" />
        {/* 眼 */}
        <rect x="112" y="50" width="5" height="5" fill="rgba(161,161,170,0.6)" />
      </svg>
    </div>
  );
}

/** XP 方块 + 下界 portal 微尘，缓慢上浮 */
function FloatingParticles() {
  const orbs = [
    { left: "8%", delay: "0s", dur: "14s", color: "bg-lime-500/20", size: "h-2 w-2" },
    { left: "22%", delay: "3s", dur: "18s", color: "bg-yellow-400/20", size: "h-1.5 w-1.5" },
    { left: "35%", delay: "6s", dur: "16s", color: "bg-lime-500/15", size: "h-2.5 w-2.5" },
    { left: "55%", delay: "2s", dur: "20s", color: "bg-yellow-400/15", size: "h-2 w-2" },
    { left: "70%", delay: "8s", dur: "15s", color: "bg-lime-500/20", size: "h-1.5 w-1.5" },
    { left: "85%", delay: "5s", dur: "17s", color: "bg-yellow-400/15", size: "h-2 w-2" },
    { left: "15%", delay: "9s", dur: "22s", color: "bg-purple-600/25 blur-sm", size: "h-3 w-3" },
    { left: "48%", delay: "12s", dur: "19s", color: "bg-purple-600/20 blur-sm", size: "h-2 w-2" },
    { left: "78%", delay: "14s", dur: "24s", color: "bg-purple-600/20 blur-sm", size: "h-2.5 w-2.5" },
  ];
  return (
    <div className="absolute inset-0 overflow-hidden" aria-hidden>
      {orbs.map((o, i) => (
        <span
          key={i}
          className={`absolute bottom-[-20px] block rounded-[2px] ${o.color} ${o.size}`}
          style={{
            left: o.left,
            animation: `xpFloat ${o.dur} linear ${o.delay} infinite`,
          }}
        />
      ))}
    </div>
  );
}

export default function VoxelBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 z-0 overflow-hidden bg-zinc-950">
      {/* L1: 像素网格 */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `url("${PIXEL_GRID_URI}")`,
          backgroundSize: "48px 48px",
        }}
      />

      {/* L2: 地形（右下角） */}
      <TerrainSilhouette />

      {/* L3: 生物 */}
      <CreeperFace />
      <EndermanEyes />
      <PixelPig />

      {/* L4: 粒子 */}
      <FloatingParticles />

      {/* 中央径向压暗：保证卡片文字 100% 可读 */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 60% at 50% 55%, rgba(9,9,11,0.72) 0%, rgba(9,9,11,0.35) 55%, transparent 100%)",
        }}
      />
      {/* 顶部微暗，增强导航层次 */}
      <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-zinc-950/70 to-transparent" />
    </div>
  );
}
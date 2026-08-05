/** mcSfx —— MC 原版音效纯函数（Web Audio API 合成）。移植自 v3 的 sndOrb/sndEnchant。 */

/** 获取（或创建）共享 AudioContext，失败返回 null */
function getCtx(): AudioContext | null {
  try {
    const Ctx =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext?: typeof AudioContext })
        .webkitAudioContext;
    if (!Ctx) return null;
    const ctx = new Ctx();
    if (ctx.state === "suspended") void ctx.resume();
    return ctx;
  } catch {
    return null;
  }
}

/** 预热解锁 AudioContext（首次用户交互时调用） */
export function primeAudio(): boolean {
  const ctx = getCtx();
  if (!ctx) return false;
  try {
    const buf = ctx.createBuffer(1, 1, 22050);
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(ctx.destination);
    src.start(0);
    void ctx.resume();
  } catch { /* ignore */ }
  setTimeout(() => {
    try { void ctx.close(); } catch { /* ignore */ }
  }, 200);
  return true;
}

/** MC 升级音效 —— 清脆高音叮（1300/1900Hz 三角波） */
export function playMcLevelUp(): void {
  const ctx = getCtx();
  if (!ctx) return;
  try {
    const t = ctx.currentTime;
    [1300, 1900].forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "triangle";
      o.frequency.setValueAtTime(f, t + i * 0.07);
      g.gain.setValueAtTime(0.18, t + i * 0.07);
      g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.07 + 0.18);
      o.connect(g);
      g.connect(ctx.destination);
      o.start(t + i * 0.07);
      o.stop(t + i * 0.07 + 0.18);
    });
  } catch { /* 静默降级 */ }
}

/** MC 附魔音效 —— 三层合成（嗡鸣+升调+爆发），~3.2s 后回调 onComplete */
export function playMcEnchantSound(onComplete?: () => void): void {
  const ctx = getCtx();
  if (!ctx) { onComplete?.(); return; }
  try {
    const t = ctx.currentTime;

    // Layer 1: 低沉嗡鸣
    [40, 60, 80].forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "sine";
      o.frequency.setValueAtTime(f, t + i * 0.05);
      o.frequency.linearRampToValueAtTime(f * 0.3, t + 2.5);
      g.gain.setValueAtTime(0.06, t + i * 0.05);
      g.gain.exponentialRampToValueAtTime(0.001, t + 2.8);
      o.connect(g); g.connect(ctx.destination);
      o.start(t + i * 0.05); o.stop(t + 2.8);
    });

    // Layer 2: 虚幻升调
    const notes = [160, 240, 320, 450, 580, 750, 950, 1180, 1420, 1700];
    notes.forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = i % 2 ? "triangle" : "sine";
      o.frequency.setValueAtTime(f, t + 0.8 + i * 0.13);
      o.frequency.exponentialRampToValueAtTime(f * 1.1, t + 0.8 + i * 0.13 + 0.4);
      g.gain.setValueAtTime(0.09, t + 0.8 + i * 0.13);
      g.gain.exponentialRampToValueAtTime(0.001, t + 0.8 + i * 0.13 + 0.45);
      o.connect(g); g.connect(ctx.destination);
      o.start(t + 0.8 + i * 0.13); o.stop(t + 0.8 + i * 0.13 + 0.45);
    });

    // Layer 3: 爆发和弦
    [100, 200, 300, 500, 700, 1000].forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = i < 3 ? "square" : "sine";
      o.frequency.setValueAtTime(f * 2, t + 2.2 + i * 0.03);
      o.frequency.exponentialRampToValueAtTime(f, t + 3.0);
      g.gain.setValueAtTime(0.1, t + 2.2 + i * 0.03);
      g.gain.exponentialRampToValueAtTime(0.001, t + 3.0);
      o.connect(g); g.connect(ctx.destination);
      o.start(t + 2.2 + i * 0.03); o.stop(t + 3.0);
    });

    setTimeout(() => {
      try { void ctx.close(); } catch { /* ignore */ }
      onComplete?.();
    }, 3200);
  } catch { onComplete?.(); }
}
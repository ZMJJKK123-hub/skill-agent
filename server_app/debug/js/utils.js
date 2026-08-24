// utils.js — shared utilities, audio, toast
const $ = id => document.getElementById(id);
const rnd = (a, b) => Math.floor(Math.random() * (b - a + 1)) + a;
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
const lerp = (a, b, t) => a + (b - a) * t;
const dist = (x1, y1, x2, y2) => Math.hypot(x2 - x1, y2 - y1);

function toast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.classList.add('show');
  // 缩短显示时间，减少打扰（1.2s）
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 1200);
}

// Audio
let sndOn = false;
let aCtx = null;

function ensureAudio() {
  if (!aCtx) aCtx = new (window.AudioContext || window.webkitAudioContext)();
}

function beep(freq, dur, vol, type) {
  if (!sndOn) return;
  ensureAudio();
  const o = aCtx.createOscillator();
  const g = aCtx.createGain();
  o.connect(g);
  g.connect(aCtx.destination);
  o.frequency.value = freq;
  o.type = type || 'square';
  g.gain.value = vol || 0.06;
  o.start();
  g.gain.exponentialRampToValueAtTime(0.001, aCtx.currentTime + (dur || 0.1));
  o.stop(aCtx.currentTime + (dur || 0.1));
}

function sfx(name) {
  if (!sndOn) return;
  switch (name) {
    case 'hit': beep(440, 0.05, 0.05); break;
    case 'eat': beep(660, 0.08, 0.06); break;
    case 'die': beep(150, 0.4, 0.1); break;
    case 'powerup':
      beep(523, 0.06, 0.05);
      setTimeout(() => beep(880, 0.06, 0.05), 60);
      setTimeout(() => beep(1320, 0.08, 0.06), 120);
      break;
    case 'win':
      [523, 659, 784, 1047].forEach((n, i) => setTimeout(() => beep(n, 0.1, 0.06), i * 80));
      break;
    case 'lose':
      [330, 220, 110].forEach((n, i) => setTimeout(() => beep(n, 0.12, 0.08), i * 100));
      break;
    case 'click': beep(800, 0.03, 0.04); break;
    case 'combo': beep(1200, 0.04, 0.04); break;
  }
}

// BaseGame class
class BaseGame {
  constructor(container) {
    this.container = container;
    this.running = false;
    this.rafId = null;
  }
  start() { this.running = true; this.loop(); }
  stop() { this.running = false; if (this.rafId) cancelAnimationFrame(this.rafId); }
  loop() {
    if (!this.running) return;
    this.update();
    this.render();
    this.rafId = requestAnimationFrame(() => this.loop());
  }
  update() {}
  render() {}
}
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
    // 子类在构造时设置 this.intro = { title, lines: [...] } 即可获得开局玩法说明卡：
    // start() 先渲染一帧 + 弹出引导浮层，玩家点"开始"后才进入游戏循环。
  }
  start() {
    this.running = true;
    if (this.intro) {
      try { this.render && this.render(); } catch (e) { /* first frame optional */ }
      this._showIntro();
      return;
    }
    this.loop();
  }
  _showIntro() {
    var host = this.container || document.body;
    try { host.style.position = 'relative'; } catch (e) {}
    var ov = document.createElement('div');
    ov.style.cssText = 'position:absolute;inset:0;background:rgba(3,6,12,.94);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;z-index:30;padding:18px;text-align:center';
    var h = document.createElement('div');
    h.style.cssText = 'color:var(--green);font-weight:700;font-size:1em;letter-spacing:.5px;text-shadow:0 0 8px rgba(0,255,159,.4)';
    h.textContent = this.intro.title;
    ov.appendChild(h);
    var list = document.createElement('div');
    list.style.cssText = 'display:flex;flex-direction:column;gap:6px;max-width:94%';
    this.intro.lines.forEach(function (l) {
      var r = document.createElement('div');
      r.style.cssText = 'font-size:.72em;color:var(--text);line-height:1.5;text-align:left;background:rgba(0,255,159,.04);border:1px solid var(--border);border-radius:6px;padding:5px 10px';
      r.textContent = l;
      list.appendChild(r);
    });
    ov.appendChild(list);
    var btn = document.createElement('button');
    btn.textContent = '▶ 开始游戏';
    btn.style.cssText = 'margin-top:4px;padding:8px 36px;border-radius:8px;border:1px solid var(--green-d);background:rgba(0,255,159,.08);color:var(--green);cursor:pointer;font-family:inherit;font-size:.85em;font-weight:600';
    btn.onclick = function () {
      ov.remove();
      sfx('click');
      this.beginPlay();
    }.bind(this);
    ov.appendChild(btn);
    host.appendChild(ov);
    this._introOv = ov;
  }
  // 引导结束进入正式循环；子类可覆写以延迟启动计时器等
  beginPlay() {
    if (!this.running) return;
    this.loop();
  }
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
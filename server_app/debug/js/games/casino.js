// casino.js — 算力赌坊：大厅 + 共享钱包 + 子游戏注册表
// 架构铺垫：后续新增赌桌（21 点 / 骰子 / 老虎机…）只需：
//   1. 写一个新文件 class XxxTable { constructor(container, ctx) {...} update(){} destroy(){} }
//      ctx = { wallet, exit(), bot }（wallet 为共享算力钱包）
//   2. 文件末尾 Casino.register('xxx', { name, icon, desc, create: (c, ctx) => new XxxTable(c, ctx) })
//   3. game.html GAMES['casino'].files 数组与 index.html <script> 标签加上该文件
// 大厅会自动列出注册的新赌桌，无需改大厅代码。

  // ---------- 共享钱包（全赌桌通用，localStorage 持久化；纯虚拟筹码） ----------
  const CHIPS_KEY = 'casinoChips';
  const BAILOUT_AT_KEY = 'casinoBailoutAt';
  const _chipListeners = new Set();

  window.Casino = {
    wallet: {
      get() {
        var v = parseInt(localStorage.getItem(CHIPS_KEY) || '1000', 10);
        return isFinite(v) && v >= 0 ? v : 1000;
      },
      add(n) { this._save(this.get() + n); },
      sub(n) {
        if (this.get() < n) return false;
        this._save(this.get() - n);
        return true;
      },
      // 破产救济：只有筹码见底（<100）才能领，且 60 秒冷却——不能无限薅
      bailout() {
        if (this.get() >= 100) return false;
        var last = parseInt(localStorage.getItem(BAILOUT_AT_KEY) || '0', 10);
        if (Date.now() - last < 60000) return false;
        try { localStorage.setItem(BAILOUT_AT_KEY, String(Date.now())); } catch (e) {}
        this._save(this.get() + 1000);
        return true;
      },
      canBailout() { return this.get() < 100; },
      onChange(cb) {
        _chipListeners.add(cb);
        try { cb(this.get()); } catch (e) { /* listener error 不影响钱包 */ }
        return () => _chipListeners.delete(cb);
      },
      _save(v) {
        try { localStorage.setItem(CHIPS_KEY, String(v)); } catch (e) {}
        _chipListeners.forEach(function (cb) { try { cb(v); } catch (e) {} });
      }
    },

    // ---------- 音效/语音包（本地 assets/audio/*.wav，首次播放预加载） ----------
    audio: {
      _cache: {},
      play(name, vol) {
        try {
          var a = this._cache[name];
          if (a === undefined) {
            a = new Audio('assets/audio/' + name + '.wav');
            a.volume = vol === undefined ? 0.9 : vol;
            this._cache[name] = a;
          }
          if (!a) return false;
          a.volume = vol === undefined ? 0.9 : vol;
          a.currentTime = 0;
          var pr = a.play();
          if (pr && pr.catch) pr.catch(function () {});
          return true;
        } catch (e) { return false; }
      }
    },

  // ---------- 跨局战绩（localStorage 持久化，大厅页脚汇总） ----------
  stats: {
    KEY: 'casinoStats',
    _read() {
      try { return JSON.parse(localStorage.getItem(this.KEY) || '{}') || {}; } catch (e) { return {}; }
    },
    _save(s) {
      try { localStorage.setItem(this.KEY, JSON.stringify(s)); } catch (e) {}
    },
    // r: 'W' | 'L' | 'P' | 'R'（局数）
    record(tableId, r) {
      var s = this._read();
      var t = s[tableId] || (s[tableId] = { W: 0, L: 0, P: 0, R: 0 });
      t[r] = (t[r] || 0) + 1;
      this._save(s);
    },
    // 页脚汇总文案：{ list: '德州 3胜2负 · …', total: '共 …' } 或 null
    summary() {
      var s = this._read();
      var ids = ['holdem', 'blackjack', 'dice', 'slots', 'roulette', 'baccarat', 'goldenflower', 'craps', 'paigow'];
      var names = { holdem: '德州', blackjack: '21点', dice: '骰宝', slots: '老虎机', roulette: '轮盘', baccarat: '百家乐', goldenflower: '炸金花', craps: 'Craps', paigow: '牌九' };
      var parts = [], W = 0, L = 0, P = 0, any = false;
      ids.forEach(function (id) {
        var t = s[id];
        if (!t) return;
        any = true;
        W += t.W || 0; L += t.L || 0; P += t.P || 0;
        if (t.W || t.L || t.P) parts.push(names[id] + ' ' + t.W + '胜' + t.L + '负' + (t.P ? '·' + t.P + '平' : ''));
        else if (t.R) parts.push(names[id] + ' ' + t.R + '局');
      });
      if (!any) return null;
      var n = W + L;
      return { list: parts.join(' · '), total: '总计 ' + W + '胜 / ' + L + '负' + (P ? ' / ' + P + '平' : '') + (n ? ' · 胜率 ' + Math.round(W / n * 100) + '%' : '') };
    },
    reset() { this._save({}); }
  },

  // ---------- 大厅音景（WebAudio 合成低频环境音，零素材依赖；无音频环境静默降级） ----------
  ambient: {
    _ctx: null, _gain: null, _nodes: null, _timer: 0, _on: false,
    start() {
      try {
        if (this._on) return true;
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return false;
        var ctx = this._ctx || (this._ctx = new AC());
        if (ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} }
        var g = ctx.createGain();
        g.gain.value = 0;
        g.connect(ctx.destination);
        var o1 = ctx.createOscillator(), o2 = ctx.createOscillator(); // 55Hz + 82.5Hz 纯五度低音垫
        o1.frequency.value = 55; o2.frequency.value = 82.5;
        o1.type = 'sine'; o2.type = 'sine';
        var og = ctx.createGain(); og.gain.value = 0.5;
        o1.connect(og); o2.connect(og); og.connect(g);
        var lfo = ctx.createOscillator(), lg = ctx.createGain(); // 缓慢呼吸
        lfo.frequency.value = 0.08; lg.gain.value = 0.3;
        lfo.connect(lg); lg.connect(og.gain);
        o1.start(); o2.start(); lfo.start();
        this._gain = g; this._nodes = [o1, o2, lfo]; this._on = true;
        var self = this;
        this._timer = setInterval(function () {
          if (!self._gain || !self._ctx) return;
          if (self._ctx.state === 'suspended') { try { self._ctx.resume(); } catch (e) {} }
          var target = (typeof window.sndOn === 'undefined' || window.sndOn) ? 0.045 : 0;
          try { self._gain.gain.setTargetAtTime(target, self._ctx.currentTime, 0.6); } catch (e) {}
        }, 700);
        return true;
      } catch (e) { return false; }
    },
    stop() {
      try {
        if (this._timer) { clearInterval(this._timer); this._timer = 0; }
        if (this._nodes) this._nodes.forEach(function (n) { try { n.stop(); } catch (e) {} });
        if (this._gain) this._gain.disconnect();
      } catch (e) {}
      this._nodes = null; this._gain = null; this._on = false;
    },
    active() { return !!this._on; }
  },

  // ---------- 子游戏注册表 ----------
  _tables: new Map(),
  register(id, def) { this._tables.set(id, def); },
  tables() { return Array.from(this._tables.keys()); },
  get(id) { return this._tables.get(id); },

  // 语音播报：浏览器内置 speechSynthesis（零外部依赖；无语音环境静默降级返回 false）。
  // 加固：正在朗读时先 cancel 再延时播（Chrome 会吞掉紧随 cancel 的 speak）；
  // 首次调用预热音色列表；onstart/onerror 写入诊断日志。
  say(text, opts) {
    try {
      var synth = window.speechSynthesis;
      if (!synth || !window.SpeechSynthesisUtterance) return false;
      if (!this._voicesPrimed) {
        this._voicesPrimed = true;
        synth.getVoices(); // 触发音色加载
        synth.onvoiceschanged = function () { synth.getVoices(); };
      }
      var speakNow = function () {
        try {
          var u = new window.SpeechSynthesisUtterance(text);
          u.lang = (opts && opts.lang) || 'zh-CN';
          u.rate = (opts && opts.rate) || 1;
          u.pitch = (opts && opts.pitch) || 0.7;
          u.volume = 0.9;
          u.onstart = function () { window.__sayLog = { text: text, started: true }; };
          u.onerror = function (e) { window.__sayLog = { text: text, err: e && e.error }; };
          synth.speak(u);
        } catch (e) { /* ignore */ }
      };
      if (synth.speaking || synth.pending) {
        synth.cancel();
        setTimeout(speakNow, 60); // 立刻 speak 会被 cancel 吞掉
      } else {
        speakNow();
      }
      return true;
    } catch (e) { return false; }
  },

  // ---------- 场景画师（骗子酒吧风：第一人称昏暗酒馆） ----------
  // 确定性伪随机：道具/粒子位置帧间稳定
  _r(i) { var x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); },
  paint: {
    // 房间：暗木 板墙、红色霓虹招牌、琥珀吊灯、烟雾、酒瓶架（人物与桌面画在其上）
    room(c, w, h, t) {
      var _r = Casino._r;
      // 暖黑底色
      var base = c.createLinearGradient(0, 0, 0, h);
      base.addColorStop(0, '#0d0705'); base.addColorStop(0.55, '#170d08'); base.addColorStop(1, '#070302');
      c.fillStyle = base; c.fillRect(0, 0, w, h);
      // 背墙暗木板（垂直板缝，板色微差）
      var wallY = h * 0.56, planks = 15;
      for (var i = 0; i < planks; i++) {
        var px = (i / planks) * w, pw = w / planks + 1, sh = 0.8 + _r(i) * 0.4;
        c.fillStyle = 'rgb(' + Math.round(56 * sh) + ',' + Math.round(33 * sh) + ',' + Math.round(17 * sh) + ')';
        c.fillRect(px, 0, pw, wallY);
        c.fillStyle = 'rgba(0,0,0,.4)'; c.fillRect(px + pw - 2, 0, 2, wallY);
      }
      // 横梁
      c.fillStyle = 'rgba(16,8,4,.92)';
      c.fillRect(0, h * 0.045, w, h * 0.022);
      c.fillRect(0, h * 0.345, w, h * 0.016);
      // 后方吧台酒瓶架（左右两段剪影 + 瓶身高光）
      [[w * 0.045, w * 0.235], [w * 0.765, w * 0.955]].forEach(function (seg, si) {
        var by = h * 0.30, bw = seg[1] - seg[0];
        c.fillStyle = 'rgba(10,5,3,.9)';
        c.fillRect(seg[0], h * 0.175, bw, by - h * 0.175);
        for (var b = 0; b < 7; b++) {
          var bx = seg[0] + 8 + (b / 7) * (bw - 20) + _r(b * 7 + si) * 6;
          var bh = h * (0.055 + _r(b + si * 3) * 0.035);
          c.fillStyle = 'rgba(26,13,7,.95)';
          c.fillRect(bx, by - bh, 9, bh);
          c.fillRect(bx + 2.5, by - bh - 7, 4, 7);
          c.fillStyle = 'rgba(255,190,110,.16)';
          c.fillRect(bx + 2, by - bh + 4, 1.6, bh * 0.55);
        }
        c.fillStyle = 'rgba(255,190,110,.05)';
        c.fillRect(seg[0], by, bw, 3);
      });
      // 红色霓虹招牌（闪烁）
      var flick = 0.8 + 0.2 * Math.sin(t * 0.11) * Math.sin(t * 0.023 + 1.7);
      if (flick < 0.55) flick = 0.55; // 濒坏灯管的最低亮度
      c.save();
      c.globalAlpha = flick;
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.font = '700 ' + Math.max(16, w * 0.036) + 'px monospace';
      c.shadowColor = '#ff3b30'; c.shadowBlur = 26;
      c.fillStyle = '#ffb0a8';
      c.fillText('算 力 赌 坊', w / 2, h * 0.062);
      c.font = Math.max(8, w * 0.012) + 'px monospace';
      c.shadowBlur = 12;
      c.fillStyle = '#ff8a80';
      c.fillText('~  L I A R \' S   B A R  ~', w / 2, h * 0.062 + Math.max(16, w * 0.036) * 0.8);
      c.restore();
      // 中央暖光域（主吊灯的氛围光晕）
      var amb = c.createRadialGradient(w / 2, h * 0.38, 10, w / 2, h * 0.38, w * 0.72);
      amb.addColorStop(0, 'rgba(255,190,110,.30)');
      amb.addColorStop(0.4, 'rgba(190,110,50,.12)');
      amb.addColorStop(1, 'rgba(0,0,0,0)');
      c.fillStyle = amb; c.fillRect(0, 0, w, h);
      // 吊灯 ×3：中央大 + 两侧小（电线 + 灯罩 + 灯泡辉光 + 下照光锥）
      Casino.paint._lamp(c, w / 2, h * 0.155, w * 0.055, t, 0);
      Casino.paint._lamp(c, w * 0.215, h * 0.20, w * 0.038, t, 2.1);
      Casino.paint._lamp(c, w * 0.785, h * 0.20, w * 0.038, t, 4.2);
      // 烟雾（大而淡的椭圆，缓慢横移上升）
      for (var sI = 0; sI < 7; sI++) {
        var drift = (t * (0.08 + _r(sI) * 0.10) + sI * 300) % (w + 400) - 200;
        var sy = h * 0.42 - ((t * (0.10 + _r(sI + 9) * 0.15) + sI * 130) % (h * 0.5));
        c.fillStyle = 'rgba(200,170,140,' + (0.018 + 0.014 * Math.sin(t * 0.02 + sI)) + ')';
        c.beginPath();
        c.ellipse(w * 0.5 + (drift - w / 2) * (0.5 + _r(sI + 4) * 0.8), sy, w * 0.16, h * 0.05, 0, 0, Math.PI * 2);
        c.fill();
      }
      // 琥珀浮尘
      for (var d = 0; d < 22; d++) {
        var fx = (( _r(d) + t * 0.00006 * (1 + d % 3)) % 1) * w;
        var fy = h * (0.08 + _r(d + 50) * 0.5) - (t * 0.012 * (1 + d % 4)) % (h * 0.5);
        if (fy < 0) fy += h * 0.6;
        c.fillStyle = 'rgba(255,200,120,' + (0.05 + 0.09 * Math.abs(Math.sin(t * 0.03 + d))) + ')';
        c.beginPath(); c.arc(fx, fy, 1.4, 0, Math.PI * 2); c.fill();
      }
    },
    // 吊灯：电线 + 锥形灯罩 + 灯泡 + 下照光锥（亮度轻微波动）
    _lamp(c, x, y, r, t, seed) {
      var sway = Math.sin(t * 0.012 + seed) * 3;
      var bright = 0.82 + 0.18 * Math.sin(t * 0.07 + seed * 3);
      c.save();
      c.translate(sway, 0);
      // 电线
      c.strokeStyle = 'rgba(8,4,2,.9)'; c.lineWidth = 2;
      c.beginPath(); c.moveTo(x, 0); c.lineTo(x, y - r * 0.7); c.stroke();
      // 下照光锥
      var cone = c.createLinearGradient(x, y, x, y + r * 9);
      cone.addColorStop(0, 'rgba(255,200,120,' + (0.13 * bright) + ')');
      cone.addColorStop(1, 'rgba(255,200,120,0)');
      c.fillStyle = cone;
      c.beginPath();
      c.moveTo(x - r * 0.6, y); c.lineTo(x + r * 0.6, y);
      c.lineTo(x + r * 4.6, y + r * 9); c.lineTo(x - r * 4.6, y + r * 9); c.closePath(); c.fill();
      // 锥形灯罩
      var shade = c.createLinearGradient(x, y - r * 0.7, x, y + r * 0.5);
      shade.addColorStop(0, '#3a2412'); shade.addColorStop(1, '#140a05');
      c.fillStyle = shade;
      c.beginPath();
      c.moveTo(x - r * 0.28, y - r * 0.7); c.lineTo(x + r * 0.28, y - r * 0.7);
      c.lineTo(x + r, y + r * 0.45); c.lineTo(x - r, y + r * 0.45); c.closePath(); c.fill();
      c.strokeStyle = 'rgba(255,200,120,' + (0.5 * bright) + ')'; c.lineWidth = 1.2;
      c.beginPath();
      c.moveTo(x - r, y + r * 0.45); c.lineTo(x + r, y + r * 0.45); c.stroke();
      // 灯泡
      c.fillStyle = 'rgba(255,225,160,' + (0.85 * bright + 0.15) + ')';
      c.shadowColor = '#ffc87a'; c.shadowBlur = 18 * bright;
      c.beginPath(); c.arc(x, y + r * 0.55, r * 0.24, 0, Math.PI * 2); c.fill();
      c.restore();
    },
    // 扑克桌：第一人称透视——远端桌沿在画面中部，近端出血铺满底部（红棕木 + 暗红呢 + 受光亮边 + 道具）
    table(c, w, h) {
      var _r = Casino._r;
      var ty = h * 0.52;                 // 远端桌沿
      var x0 = w * 0.13, x1 = w * 0.87;  // 远端左右
      var bx0 = -w * 0.08, bx1 = w * 1.08; // 近端（出血）
      // 桌面透视梯形
      var wood = c.createLinearGradient(0, ty, 0, h);
      wood.addColorStop(0, '#8a4a1d'); wood.addColorStop(0.3, '#6e3512'); wood.addColorStop(1, '#241006');
      c.fillStyle = wood;
      c.beginPath();
      c.moveTo(x0, ty); c.lineTo(x1, ty); c.lineTo(bx1, h); c.lineTo(bx0, h); c.closePath();
      c.fill();
      // 木纹（沿透视的弧线）
      c.save();
      c.beginPath();
      c.moveTo(x0, ty); c.lineTo(x1, ty); c.lineTo(bx1, h); c.lineTo(bx0, h); c.closePath();
      c.clip();
      for (var i = 0; i < 10; i++) {
        var yy = ty + Math.pow((i + 0.5) / 10, 1.3) * (h - ty);
        c.strokeStyle = 'rgba(28,11,4,' + (0.10 + 0.12 * _r(i + 3)) + ')';
        c.lineWidth = 1 + _r(i + 41) * 2.2;
        c.beginPath(); c.moveTo(bx0, yy + 20); c.quadraticCurveTo(w / 2, yy - 16, bx1, yy + 20); c.stroke();
      }
      // 暗红呢放牌区（中央椭圆 + 金线）
      var cx = w / 2, cy = h * 0.70, rx = w * 0.315, ry = h * 0.155;
      var felt = c.createRadialGradient(cx, cy - ry * 0.3, ry * 0.15, cx, cy, rx);
      felt.addColorStop(0, '#5c1620'); felt.addColorStop(1, '#26060d');
      c.fillStyle = felt;
      c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.fill();
      c.strokeStyle = 'rgba(240,198,116,.30)'; c.lineWidth = 1.6;
      c.beginPath(); c.ellipse(cx, cy, rx * 0.93, ry * 0.88, 0, 0, Math.PI * 2); c.stroke();
      c.fillStyle = 'rgba(240,198,116,.10)';
      c.font = '700 ' + Math.max(11, w * 0.017) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText('S H O W   H A N D', cx, cy + ry * 0.02);
      c.restore();
      // 受光桌沿（远端亮边：被吊灯照亮）
      var edge = c.createLinearGradient(0, ty - 5, 0, ty + 30);
      edge.addColorStop(0, 'rgba(255,205,130,.5)'); edge.addColorStop(1, 'rgba(255,205,130,0)');
      c.fillStyle = edge;
      c.beginPath();
      c.moveTo(x0 - w * 0.012, ty - 5); c.lineTo(x1 + w * 0.012, ty - 5);
      c.lineTo(x1 + w * 0.05, ty + 30); c.lineTo(x0 - w * 0.05, ty + 30); c.closePath(); c.fill();
      c.strokeStyle = 'rgba(255,215,150,.55)'; c.lineWidth = 2;
      c.shadowColor = '#ffc87a'; c.shadowBlur = 8;
      c.beginPath(); c.moveTo(x0, ty); c.lineTo(x1, ty); c.stroke();
      c.shadowBlur = 0;
      // 道具：左轮弹壳 ×2、威士忌杯、皱纸条（确定性摆位）
      for (var g = 0; g < 2; g++) {
        var gx = w * (0.30 + g * 0.045), gy = h * (0.585 + g * 0.012);
        c.save(); c.translate(gx, gy); c.rotate(0.5 + g * 0.4);
        var casing = c.createLinearGradient(0, -2, 0, 2);
        casing.addColorStop(0, '#d9a44a'); casing.addColorStop(1, '#8a5a1d');
        c.fillStyle = casing;
        c.fillRect(-9, -2.2, 18, 4.4);
        c.fillStyle = '#6a4314'; c.fillRect(7, -2.2, 2.4, 4.4);
        c.restore();
      }
      // 威士忌杯（近右侧，琥珀酒体）
      var glx = w * 0.735, gly = h * 0.66;
      c.save();
      c.fillStyle = 'rgba(210,140,60,.55)';
      c.beginPath(); c.ellipse(glx, gly, 11, 9, 0, 0, Math.PI * 2); c.fill();
      c.strokeStyle = 'rgba(255,225,170,.5)'; c.lineWidth = 1.4;
      c.beginPath(); c.ellipse(glx, gly, 11, 9, 0, 0, Math.PI * 2); c.stroke();
      c.fillStyle = 'rgba(255,200,120,.14)';
      c.beginPath(); c.ellipse(glx, gly - 9, 9, 3, 0, 0, Math.PI * 2); c.fill();
      c.restore();
      // 皱纸条（左下）
      c.save();
      c.translate(w * 0.135, h * 0.86); c.rotate(-0.35);
      c.fillStyle = 'rgba(214,196,160,.6)';
      c.beginPath();
      c.moveTo(-22, -8); c.quadraticCurveTo(-4, -14, 20, -6);
      c.quadraticCurveTo(26, 2, 12, 8); c.quadraticCurveTo(-8, 13, -22, 6);
      c.closePath(); c.fill();
      c.strokeStyle = 'rgba(60,40,20,.5)'; c.lineWidth = 0.8;
      c.beginPath(); c.moveTo(-14, -2); c.lineTo(12, -1); c.moveTo(-12, 3); c.lineTo(8, 4); c.stroke();
      c.restore();
    },
    // 筹码堆
    chips(c, x, y, n) {
      var stacks = Math.min(6, Math.max(1, Math.ceil(n / 120)));
      var colors = ['#e05555', '#5fa8e0', '#f0c674', '#8ee08a'];
      for (var s = 0; s < stacks; s++) {
        var hgt = Math.min(8, Math.max(2, Math.floor(n / (stacks * 15))));
        for (var i = 0; i < hgt; i++) {
          c.fillStyle = colors[(s + i) % colors.length];
          c.beginPath(); c.ellipse(x + s * 16 - stacks * 8, y - i * 5, 9, 4.5, 0, 0, Math.PI * 2); c.fill();
          c.fillStyle = 'rgba(255,255,255,.25)';
          c.beginPath(); c.ellipse(x + s * 16 - stacks * 8, y - i * 5, 4, 2, 0, 0, Math.PI * 2); c.fill();
        }
      }
    },
    // 战绩点：右上角 W/L/P 圆点串（各赌桌共用）
    histDots(c, w, h, hist) {
      if (!hist || !hist.length) return;
      c.save();
      for (var i = 0; i < hist.length; i++) {
        var r = hist[i];
        c.fillStyle = r === 'W' ? '#8fce8f' : r === 'L' ? '#e08080' : '#a0c8e8';
        c.beginPath();
        c.arc(w - 18 - (hist.length - 1 - i) * 14, h * 0.125, 4.4, 0, Math.PI * 2);
        c.fill();
      }
      c.restore();
    },
    // 人物：正面朝向玩家的酒馆常客——写实向建模：
    // 皮肤色/发型按名字散列、大衣驳领+衬衫+纽扣、双臂搭桌+手部、真眼(眼白+瞳孔)、
    // 帽子按性格；lean=看牌前倾姿态；folded 垂头；active/winner 聚光。
    seat(c, x, y, t, o) {
      var s = o.scale || 1;
      var seed = 0;
      var nm = o.name || '';
      for (var ci = 0; ci < nm.length; ci++) seed = (seed * 31 + nm.charCodeAt(ci)) % 997;
      var _r = Casino._r;
      var skins = ['#e8b88a', '#d9a06f', '#c98d5c', '#b97a4e', '#8a5a3a', '#f0c8a0'];
      var skin = skins[seed % skins.length];
      var hairs = ['#1a1410', '#2c2018', '#3a2a1a', '#55402a', '#0d0a08', '#6a5236'];
      var hair = hairs[(seed + 3) % hairs.length];
      var bob = Math.sin(t * 0.035 + seed) * 2.6 * s;
      var sway = Math.sin(t * 0.02 + seed * 2) * 0.015;
      var blink = Math.sin(t * 0.017 + seed) > 0.96;
      var rim = o.winner ? '#ffd98a' : '#c88a4a';
      var alpha = o.folded ? 0.42 : 1;
      var lean = o.lean ? 1 : 0;
      c.save();
      c.translate(x, y + bob + lean * 9 * s); // 看牌：身体前倾
      if (o.folded) { c.translate(0, 30 * s); c.rotate(0.09); }
      c.rotate(sway);
      if (lean) c.scale(1 + 0.04, 1 + 0.05); // 前倾时略放大（凑近镜头）
      // 行动/赢家头顶聚光
      if (o.active || o.winner) {
        var amp = o.winner ? 0.30 : 0.15 + 0.06 * Math.sin(t * 0.12);
        var cone = c.createLinearGradient(0, -170 * s, 0, 64 * s);
        cone.addColorStop(0, 'rgba(255,200,120,' + amp + ')');
        cone.addColorStop(1, 'rgba(255,200,120,0)');
        c.fillStyle = cone;
        c.beginPath();
        c.moveTo(-18 * s, -170 * s); c.lineTo(18 * s, -170 * s);
        c.lineTo(62 * s, 64 * s); c.lineTo(-62 * s, 64 * s); c.closePath(); c.fill();
      }
      c.globalAlpha = alpha;
      // ---- 双臂（大衣袖）搭向桌面，手部贴桌 ----
      var armY = 34 * s - lean * 10 * s;
      c.strokeStyle = '#241509'; c.lineWidth = 13 * s; c.lineCap = 'round';
      c.beginPath(); c.moveTo(-30 * s, -6 * s); c.lineTo(-44 * s - lean * 8 * s, armY + 14 * s); c.stroke();
      c.beginPath(); c.moveTo(30 * s, -6 * s); c.lineTo(44 * s + lean * 8 * s, armY + 14 * s); c.stroke();
      c.fillStyle = skin;
      c.beginPath(); c.ellipse(-44 * s - lean * 8 * s, armY + 16 * s, 7.5 * s, 5.5 * s, 0, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.ellipse(44 * s + lean * 8 * s, armY + 16 * s, 7.5 * s, 5.5 * s, 0, 0, Math.PI * 2); c.fill();
      // ---- 躯干：大衣 + 驳领 + 衬衫 + 纽扣 ----
      var coat = c.createLinearGradient(0, -20 * s, 0, 64 * s);
      coat.addColorStop(0, '#33200f'); coat.addColorStop(1, '#0c0603');
      c.fillStyle = coat;
      c.beginPath();
      c.moveTo(-54 * s, 64 * s); c.lineTo(-33 * s, -16 * s);
      c.lineTo(33 * s, -16 * s); c.lineTo(54 * s, 64 * s); c.closePath(); c.fill();
      // 衬衫（领口三角）
      c.fillStyle = '#cbb596';
      c.beginPath(); c.moveTo(-9 * s, -14 * s); c.lineTo(9 * s, -14 * s); c.lineTo(0, 12 * s); c.closePath(); c.fill();
      // 驳领
      c.fillStyle = '#241508';
      c.beginPath(); c.moveTo(-9 * s, -14 * s); c.lineTo(-22 * s, 14 * s); c.lineTo(-6 * s, 6 * s); c.closePath(); c.fill();
      c.beginPath(); c.moveTo(9 * s, -14 * s); c.lineTo(22 * s, 14 * s); c.lineTo(6 * s, 6 * s); c.closePath(); c.fill();
      // 领巾（性格色）
      c.fillStyle = o.color;
      c.beginPath(); c.moveTo(-6 * s, -13 * s); c.lineTo(6 * s, -13 * s); c.lineTo(0, 2 * s); c.closePath(); c.fill();
      // 纽扣
      c.fillStyle = 'rgba(200,170,120,.75)';
      c.beginPath(); c.arc(0, 22 * s, 1.6 * s, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.arc(0, 34 * s, 1.6 * s, 0, Math.PI * 2); c.fill();
      // 肩部缘光
      c.strokeStyle = rim; c.lineWidth = 2 * s;
      c.globalAlpha = alpha * (o.winner ? 0.95 : 0.5 + (o.active ? 0.3 : 0));
      c.beginPath(); c.moveTo(-33 * s, -14 * s); c.lineTo(-53 * s, 62 * s); c.stroke();
      c.globalAlpha = alpha;
      // ---- 头：皮肤 + 耳朵 + 下颌阴影 ----
      c.fillStyle = skin;
      c.beginPath(); c.ellipse(0, -36 * s, 16 * s, 19 * s, 0, 0, Math.PI * 2); c.fill();
      // 耳朵
      c.beginPath(); c.ellipse(-15.5 * s, -35 * s, 3 * s, 4.5 * s, 0, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.ellipse(15.5 * s, -35 * s, 3 * s, 4.5 * s, 0, 0, Math.PI * 2); c.fill();
      // 下颌/颈部阴影
      c.fillStyle = 'rgba(60,30,15,.25)';
      c.beginPath(); c.ellipse(0, -24 * s, 10 * s, 6 * s, 0, 0, Math.PI * 2); c.fill();
      // 头发（帽檐下）
      c.fillStyle = hair;
      c.beginPath();
      c.ellipse(0, -44 * s, 15.5 * s, 9 * s, 0, Math.PI * 0.05, Math.PI * 0.95);
      c.fill();
      // 脸缘光
      c.strokeStyle = rim; c.lineWidth = 1.6 * s;
      c.globalAlpha = alpha * (o.winner ? 0.9 : 0.45 + (o.active ? 0.25 : 0));
      c.beginPath(); c.ellipse(0, -36 * s, 16 * s, 19 * s, 0, -Math.PI * 0.8, -Math.PI * 0.2); c.stroke();
      c.globalAlpha = alpha;
      // ---- 真实眼睛：眼白 + 瞳孔 + 眉毛 ----
      var ey = -37 * s;
      // 眼窝阴影
      c.fillStyle = 'rgba(40,20,10,.28)';
      c.beginPath(); c.ellipse(-6 * s, ey, 5.5 * s, 3.6 * s, 0, 0, Math.PI * 2); c.fill();
      c.beginPath(); c.ellipse(6 * s, ey, 5.5 * s, 3.6 * s, 0, 0, Math.PI * 2); c.fill();
      if (blink) {
        c.strokeStyle = '#2a1c12'; c.lineWidth = 1.4 * s;
        c.beginPath(); c.moveTo(-10 * s, ey); c.lineTo(-2 * s, ey); c.stroke();
        c.beginPath(); c.moveTo(2 * s, ey); c.lineTo(10 * s, ey); c.stroke();
      } else {
        c.fillStyle = '#f2ead9';
        c.beginPath(); c.ellipse(-6 * s, ey, 4.4 * s, 2.8 * s, 0, 0, Math.PI * 2); c.fill();
        c.beginPath(); c.ellipse(6 * s, ey, 4.4 * s, 2.8 * s, 0, 0, Math.PI * 2); c.fill();
        var lookX = lean ? 0 : Math.sin(t * 0.01 + seed) * 1.2 * s; // 平时视线微动，看牌时盯牌
        c.fillStyle = '#1c130c';
        c.beginPath(); c.arc(-6 * s + lookX, ey, 1.7 * s, 0, Math.PI * 2); c.fill();
        c.beginPath(); c.arc(6 * s + lookX, ey, 1.7 * s, 0, Math.PI * 2); c.fill();
      }
      // 眉毛（aggr 更斜）
      c.strokeStyle = hair; c.lineWidth = 1.8 * s;
      var browTilt = o.persona === 'aggr' ? 2.5 * s : 0.8 * s;
      c.beginPath(); c.moveTo(-10 * s, ey - 5.5 * s + browTilt); c.lineTo(-2.5 * s, ey - 6.5 * s); c.stroke();
      c.beginPath(); c.moveTo(10 * s, ey - 5.5 * s + browTilt); c.lineTo(2.5 * s, ey - 6.5 * s); c.stroke();
      // 鼻影
      c.strokeStyle = 'rgba(80,40,18,.5)'; c.lineWidth = 1.2 * s;
      c.beginPath(); c.moveTo(0, ey + 3 * s); c.lineTo(-1.5 * s, ey + 8 * s); c.stroke();
      // tight：圆眼镜
      if (o.persona === 'tight') {
        c.strokeStyle = 'rgba(200,220,255,.55)'; c.lineWidth = 1.3;
        c.beginPath(); c.arc(-6 * s, ey, 5.5 * s, 0, Math.PI * 2); c.stroke();
        c.beginPath(); c.arc(6 * s, ey, 5.5 * s, 0, Math.PI * 2); c.stroke();
        c.beginPath(); c.moveTo(-1 * s, ey); c.lineTo(1 * s, ey); c.stroke();
      }
      // ---- 帽子（按性格） ----
      if (o.persona === 'aggr') { // 宽檐牛仔帽 + 红帽带
        c.fillStyle = '#241408';
        c.beginPath(); c.ellipse(0, -50 * s, 34 * s, 8 * s, 0, 0, Math.PI * 2); c.fill();
        c.beginPath();
        c.moveTo(-15 * s, -50 * s); c.quadraticCurveTo(-17 * s, -74 * s, 0, -75 * s);
        c.quadraticCurveTo(17 * s, -74 * s, 15 * s, -50 * s); c.closePath(); c.fill();
        c.fillStyle = o.color; c.fillRect(-15 * s, -56 * s, 30 * s, 4 * s);
      } else if (o.persona === 'bluff') { // 高顶大礼帽 + 紫帽带
        c.fillStyle = '#1a1008';
        c.beginPath(); c.ellipse(0, -50 * s, 27 * s, 6.5 * s, 0, 0, Math.PI * 2); c.fill();
        c.fillRect(-14 * s, -86 * s, 28 * s, 37 * s);
        c.fillStyle = o.color; c.fillRect(-14 * s, -60 * s, 28 * s, 5 * s);
      } else if (o.persona === 'tight') { // 圆顶礼帽
        c.fillStyle = '#20130a';
        c.beginPath(); c.ellipse(0, -50 * s, 25 * s, 6 * s, 0, 0, Math.PI * 2); c.fill();
        c.beginPath(); c.arc(0, -50 * s, 14 * s, Math.PI, 0); c.fill();
        c.fillStyle = '#3a2412'; c.fillRect(-14 * s, -56 * s, 28 * s, 3 * s);
      } else { // player：棒球帽
        c.fillStyle = '#1c120a';
        c.beginPath(); c.arc(0, -50 * s, 15 * s, Math.PI, 0); c.fill();
        c.fillRect(-13 * s, -52 * s, 30 * s, 5 * s);
        c.fillStyle = o.color; c.beginPath(); c.arc(0, -50 * s, 15 * s, Math.PI, 0); c.fill();
      }
      // bluff：叼烟
      if (o.persona === 'bluff' && !o.folded) {
        c.save();
        c.strokeStyle = '#e8dfd0'; c.lineWidth = 2.6;
        c.beginPath(); c.moveTo(9 * s, -29 * s); c.lineTo(20 * s, -24 * s); c.stroke();
        c.fillStyle = '#ff5030'; c.shadowColor = '#ff5030'; c.shadowBlur = 6;
        c.beginPath(); c.arc(20 * s, -24 * s, 1.8, 0, Math.PI * 2); c.fill();
        c.shadowBlur = 0;
        for (var k = 0; k < 3; k++) {
          var puffs = (t * 0.35 + k * 14) % 42;
          c.fillStyle = 'rgba(220,210,190,' + (0.28 * (1 - puffs / 42)) + ')';
          c.beginPath();
          c.arc(21 * s + Math.sin(t * 0.05 + k * 2) * 3, -26 * s - puffs * s * 0.8, 2.2 + puffs * 0.09, 0, Math.PI * 2);
          c.fill();
        }
        c.restore();
      }
      // 行动者：桌前琥珀脉冲环 / 赢家金环
      if (o.winner) {
        c.strokeStyle = 'rgba(255,217,138,.9)'; c.lineWidth = 3;
        c.shadowColor = '#ffd98a'; c.shadowBlur = 14;
        c.beginPath(); c.ellipse(0, 64 * s, 46 * s, 12 * s, 0, 0, Math.PI * 2); c.stroke();
        c.shadowBlur = 0;
      } else if (o.active) {
        var pulse = 0.5 + 0.5 * Math.sin(t * 0.15);
        c.strokeStyle = 'rgba(255,200,120,' + (0.35 + pulse * 0.5) + ')'; c.lineWidth = 3;
        c.beginPath(); c.ellipse(0, 64 * s, (42 + pulse * 6) * s, (11 + pulse * 2) * s, 0, 0, Math.PI * 2); c.stroke();
      }
      c.restore();
      // 名牌 + 筹码
      c.save();
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 4;
      c.font = '700 ' + Math.max(11, 12 * s) + 'px monospace';
      c.fillStyle = o.folded ? 'rgba(150,120,95,.55)' : '#ecd9b8';
      c.fillText(o.name, x, y + 82 * s);
      c.font = Math.max(9, 10 * s) + 'px monospace';
      c.fillStyle = '#8fce8f';
      c.fillText((o.chipsLabel || '') + '', x, y + 96 * s);
      c.restore();
    },
    // 摊牌庆祝：金色筹码喷泉（桌心底池区域）
    confetti(c, w, h, t) {
      for (var i = 0; i < 18; i++) {
        var ang = (i / 18) * Math.PI * 2 + t * 0.02;
        var r = 26 + (t * 1.4 + i * 20) % 120;
        var px = w / 2 + Math.cos(ang) * r, py = h * 0.60 + Math.sin(ang) * r * 0.5;
        c.fillStyle = i % 2 ? '#ffc87a' : '#ffe3ad';
        c.beginPath(); c.ellipse(px, py, 5, 2.5, ang, 0, Math.PI * 2); c.fill();
      }
    },
    // 通用扑克牌绘制（各赌桌共用）：x/y 中心点，w/h 尺寸，牌 {r,s} 或 null=背面
    card(c, x, y, w, h, card, faceUp, alpha) {
      c.save();
      if (alpha !== undefined && alpha < 1) c.globalAlpha = alpha;
      c.translate(x, y);
      var r = Math.min(w, h) * 0.09;
      c.beginPath();
      c.moveTo(-w / 2 + r, -h / 2);
      c.arcTo(w / 2, -h / 2, w / 2, h / 2, r);
      c.arcTo(w / 2, h / 2, -w / 2, h / 2, r);
      c.arcTo(-w / 2, h / 2, -w / 2, -h / 2, r);
      c.arcTo(-w / 2, -h / 2, w / 2, -h / 2, r);
      c.closePath();
      if (faceUp && card) {
        var red = card.s === 1 || card.s === 3;
        c.fillStyle = 'rgba(0,0,0,.35)';
        c.save(); c.translate(2.5, 3.5); c.fill(); c.restore();
        var face = c.createLinearGradient(0, -h / 2, 0, h / 2);
        face.addColorStop(0, '#fbf6ea'); face.addColorStop(1, '#e6dcc4');
        c.fillStyle = face; c.fill();
        c.strokeStyle = 'rgba(90,50,20,.55)'; c.lineWidth = 1; c.stroke();
        var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
        var col = red ? '#c0392b' : '#2c3e50';
        c.fillStyle = col;
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.font = '700 ' + Math.round(w * 0.30) + 'px Georgia,serif';
        c.fillText(rl, -w * 0.31, -h * 0.33);
        c.font = Math.round(w * 0.24) + 'px Georgia,serif';
        c.fillText(['♠', '♥', '♣', '♦'][card.s], -w * 0.31, -h * 0.16);
        c.save();
        c.rotate(Math.PI);
        c.font = '700 ' + Math.round(w * 0.30) + 'px Georgia,serif';
        c.fillText(rl, -w * 0.31, -h * 0.33);
        c.font = Math.round(w * 0.24) + 'px Georgia,serif';
        c.fillText(['♠', '♥', '♣', '♦'][card.s], -w * 0.31, -h * 0.16);
        c.restore();
        c.globalAlpha *= 0.16;
        c.font = Math.round(w * 0.55) + 'px Georgia,serif';
        c.fillText(['♠', '♥', '♣', '♦'][card.s], 0, h * 0.04);
      } else {
        c.fillStyle = 'rgba(0,0,0,.35)';
        c.save(); c.translate(2.5, 3.5); c.fill(); c.restore();
        var back = c.createLinearGradient(0, -h / 2, 0, h / 2);
        back.addColorStop(0, '#42141c'); back.addColorStop(1, '#2a0c12');
        c.fillStyle = back; c.fill();
        c.strokeStyle = '#6a2830'; c.lineWidth = 1; c.stroke();
        c.strokeStyle = 'rgba(255,190,110,.3)';
        c.lineWidth = 1;
        c.beginPath();
        c.moveTo(-w * 0.28, -h * 0.26); c.lineTo(w * 0.28, h * 0.26);
        c.moveTo(w * 0.28, -h * 0.26); c.lineTo(-w * 0.28, h * 0.26);
        c.stroke();
        c.strokeStyle = 'rgba(255,190,110,.18)';
        c.strokeRect(-w * 0.36, -h * 0.38, w * 0.72, h * 0.76);
      }
      c.restore();
    },
    // 暗角：暖光集中桌面，四角坠入近黑（骗子酒吧的明暗对比）
    vignette(c, w, h) {
      var v = c.createRadialGradient(w / 2, h * 0.55, Math.min(w, h) * 0.36, w / 2, h * 0.55, Math.max(w, h) * 0.78);
      v.addColorStop(0, 'rgba(0,0,0,0)');
      v.addColorStop(0.62, 'rgba(0,0,0,.28)');
      v.addColorStop(1, 'rgba(5,2,1,.82)');
      c.fillStyle = v;
      c.fillRect(0, 0, w, h);
    }
  }
};

// ---------- 大厅（BaseGame：loop 只为驱动活动赌桌的 update） ----------
class CasinoHub extends BaseGame {
  constructor(c) {
    super(c);
    this.container = c;
    this.root = document.createElement('div');
    // 全屏铺满宿主容器（game.html 视口 / index 弹窗 / 主页浮窗都吃满）
    this.root.style.cssText = 'position:relative;width:100%;height:100%;min-height:540px;background:#08040d;color:#e6d9f2;font-family:inherit;overflow:hidden';
    // 场景层：canvas 铺满（第一人称酒馆），DOM 面板浮在上面
    this.scene = document.createElement('canvas');
    this.scene.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:0';
    this.root.appendChild(this.scene);
    this.sceneCtx = this.scene.getContext('2d');
    this.t = 0;
    this.panel = document.createElement('div');
    this.panel.style.cssText = 'position:absolute;inset:0;z-index:1;box-sizing:border-box';
    this.root.appendChild(this.panel);
    this.container.appendChild(this.root);
    this.state = 'lobby';
    this.table = null;
    this.tableId = null;
    // ?table=xxx（直达/自动化）：脚本全部加载完后注册表同步可用，构造即入座
    this.autoTable = new URLSearchParams(location.search).get('table') || '';
    this.bot = new URLSearchParams(location.search).get('bot') === '1';
    this._unsub = Casino.wallet.onChange(this._onChips.bind(this));
    this.renderLobby();
    if (this.autoTable && Casino.get(this.autoTable)) this.openTable(this.autoTable);
  }

  _onChips(v) {
    var el = this.panel.querySelector('.casino-balance');
    if (el) el.textContent = v.toLocaleString();
    this._syncBailBtn();
  }

  _el(tag, css, text) {
    var e = document.createElement(tag);
    if (css) e.style.cssText = css;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  renderLobby() {
    this.state = 'lobby';
    this.table = null;
    this.tableId = null;
    Casino.ambient.start(); // 大厅音景（进桌停止）
    this.panel.innerHTML = '';
    // 大厅内容整体居中（垂直+水平）
    var wrap = this._el('div', 'padding:16px 18px;box-sizing:border-box;max-width:980px;margin:0 auto;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px');
    this.panel.appendChild(wrap);
    // 顶栏：标题 + 余额 + 救济金
    var bar = this._el('div', 'display:flex;align-items:center;gap:12px;flex-wrap:wrap;justify-content:center');
    bar.appendChild(this._el('div', 'font-size:22px;font-weight:700;color:#ffc87a;text-shadow:0 2px 8px rgba(255,60,40,.35)', '🎰 算力赌坊'));
    bar.appendChild(this._el('div', 'font-size:12px;color:#a08a6a', '算力筹码'));
    var bal = this._el('div', 'casino-balance', Casino.wallet.get().toLocaleString());
    bal.style.cssText = 'font-size:20px;font-weight:700;color:#8fce8f';
    bar.appendChild(bal);
    this.bailBtn = this._el('button', 'padding:6px 14px;border-radius:8px;border:1px solid #6a4a28;background:rgba(30,16,8,.8);color:#e8c890;cursor:pointer;font-family:inherit;font-size:12px', '🎁 领救济金 +1000');
    this._syncBailBtn();
    this.bailBtn.onclick = function () {
      if (Casino.wallet.bailout()) {
        toast('救济金 +1000 算力');
        sfx('powerup');
      } else {
        toast('筹码充足或冷却中（破产 <100 可领，间隔 60 秒）');
      }
    };
    bar.appendChild(this.bailBtn);
    wrap.appendChild(bar);

    // 赌桌网格：已注册的桌自动出现（居中排布）
    var grid = this._el('div', 'display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;width:100%;max-width:860px');
    this._crowd = {}; // 桌卡在线人数氛围：id → {n, textEl, dotEl}
    Casino.tables().forEach(function (id) {
      var def = Casino.get(id);
      var card = this._el('div', 'border:1px solid #5a3a1c;border-radius:12px;padding:18px 16px;background:rgba(22,11,6,.82);cursor:pointer;transition:border-color .15s;text-align:center');
      card.onmouseenter = function () { card.style.borderColor = '#ffc87a'; };
      card.onmouseleave = function () { card.style.borderColor = '#5a3a1c'; };
      card.innerHTML = '<div style="font-size:32px">' + def.icon + '</div>' +
        '<div style="font-size:15px;font-weight:700;margin:8px 0 4px;color:#ecd9b8">' + def.name + '</div>' +
        '<div style="font-size:12px;color:#b09678;line-height:1.5">' + def.desc + '</div>';
      // 在线氛围：脉冲绿点 + 人数（按桌 id 种子，缓慢漂移）
      var crowd = this._el('div', 'margin-top:10px;font-size:11px;color:#8fce8f;display:flex;align-items:center;justify-content:center;gap:6px');
      var dot = this._el('span', 'width:7px;height:7px;border-radius:50%;background:#5fd87a;display:inline-block;box-shadow:0 0 6px #5fd87a');
      var txt = this._el('span', '', '');
      crowd.appendChild(dot);
      crowd.appendChild(txt);
      card.appendChild(crowd);
      var seed = 0;
      for (var ci = 0; ci < id.length; ci++) seed = (seed * 31 + id.charCodeAt(ci)) % 997;
      this._crowd[id] = { n: 2 + seed % 4, textEl: txt, dotEl: dot, drift: (seed % 240) + 120 };
      this._crowd[id].textEl.textContent = '👥 ' + this._crowd[id].n + ' 人在桌';
      card.onclick = function () { sfx('click'); this.openTable(id); }.bind(this);
      grid.appendChild(card);
    }, this);
    wrap.appendChild(grid);
    // 页脚战绩汇总（跨局持久化）
    var sum = Casino.stats.summary();
    if (sum) {
      var foot = this._el('div', 'max-width:860px;width:100%;text-align:center;font-size:12px;color:#b09678;line-height:1.7;border-top:1px solid #3a2412;padding-top:10px');
      foot.appendChild(this._el('div', 'font-size:13px;color:#e8c890;font-weight:700;margin-bottom:2px', '📊 战绩速览'));
      foot.appendChild(this._el('div', '', sum.list));
      foot.appendChild(this._el('div', 'color:#8fce8f', sum.total));
      var clearBtn = this._el('button', 'margin-top:6px;padding:4px 12px;border-radius:6px;border:1px solid #6a4a28;background:rgba(30,16,8,.8);color:#b09678;cursor:pointer;font-family:inherit;font-size:11px', '清空战绩');
      clearBtn.onclick = function () { Casino.stats.reset(); this.renderLobby(); }.bind(this);
      foot.appendChild(clearBtn);
      wrap.appendChild(foot);
      this.statsEl = foot;
    } else this.statsEl = null;
  }

  _syncBailBtn() {
    if (!this.bailBtn) return;
    var can = Casino.wallet.canBailout();
    this.bailBtn.disabled = !can;
    this.bailBtn.style.opacity = can ? '1' : '.45';
    this.bailBtn.style.cursor = can ? 'pointer' : 'not-allowed';
    this.bailBtn.textContent = can ? '🎁 领救济金 +1000' : '🎁 救济金（破产可领）';
  }

  openTable(id) {
    var def = Casino.get(id);
    if (!def) return;
    Casino.ambient.stop(); // 进桌停音景，让位给桌面音效
    this.state = 'table';
    this.tableId = id;
    this.panel.innerHTML = '';
    this.tableHost = this._el('div');
    this.tableHost.style.cssText = 'position:absolute;inset:0';
    this.panel.appendChild(this.tableHost);
    var self = this;
    this.table = def.create(this.tableHost, {
      wallet: Casino.wallet,
      bot: this.bot,
      exit: function () { self.renderLobby(); }
    });
  }

  update() {
    this.t++;
    if (this.state === 'lobby') this._updateCrowd();
    if (this.state === 'table' && this.table && this.table.update) this.table.update();
  }
  // 大厅在线氛围：绿点呼吸 + 人数缓慢漂移（2-5 之间，按桌错峰）
  _updateCrowd() {
    var self = this;
    Object.keys(this._crowd || {}).forEach(function (id) {
      var c = self._crowd[id];
      if (!c || !c.dotEl) return;
      c.dotEl.style.opacity = 0.45 + 0.55 * Math.abs(Math.sin(self.t * 0.06 + c.drift));
      if (self.t % c.drift === 0) {
        var delta = ((Math.sin(self.t * 0.013 + c.drift * 7) > 0) ? 1 : -1);
        var next = c.n + delta;
        if (next < 2 || next > 5) next = c.n; // 边界反弹：维持
        if (next !== c.n) {
          c.n = next;
          c.textEl.textContent = '👥 ' + c.n + ' 人在桌';
        }
      }
    });
  }
  // 每帧绘制场景背景（房间由大厅画；活动赌桌自绘桌面/人物）
  render() {
    var cv = this.scene, c = this.sceneCtx;
    if (!cv || !c) return;
    var w = cv.clientWidth || 0, h = cv.clientHeight || 0;
    if (!w || !h) return;
    if (cv.width !== w) cv.width = w;
    if (cv.height !== h) cv.height = h;
    var t = this.t;
    Casino.paint.room(c, w, h, t);
    if (this.state === 'table' && this.table && this.table.renderScene) {
      this.table.renderScene(c, w, h, t);
    }
    // 暗角收尾：光聚桌面，四角坠入近黑（盖在场景之上、DOM 之下）
    Casino.paint.vignette(c, w, h);
  }

  stop() {
    super.stop();
    if (this.table && this.table.destroy) this.table.destroy();
    if (this._unsub) this._unsub();
  }
}

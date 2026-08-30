// casino-slots.js — 算力赌坊 · 算力老虎机 Slots
// 3 轴机械老虎机：摇杆下拉 → 卷轴依次停转（过冲回弹）→ 中线判定 → 灯光追逐+金币雨。
// 全帧驱动物理：每个卷轴有位置/速度/目标，减速曲线+回弹。

// ---------- 引擎（纯函数，供测试） ----------
var SL_SYMBOLS = ['7️⃣', '💎', '🍒', '🔧', '🐍', '💾'];
var SL_SYMS = ['7', 'DIA', 'CHE', 'WRENCH', 'SNAKE', 'DISK']; // 内部标识
// 卷轴带（每轴 20 格，权重分布）
var SL_STRIP_BASE = ['7', 'DIA', 'CHE', 'CHE', 'WRENCH', 'SNAKE', 'DISK', 'CHE', 'WRENCH', 'DIA',
  'SNAKE', 'CHE', 'DISK', 'WRENCH', 'CHE', 'SNAKE', 'DIA', 'CHE', 'WRENCH', 'DISK'];
// 赔率表：3 同 ×赔率；双 7 ×3；双钻 ×2；双樱桃 ×1（回本线）
var SL_PAYTABLE = { '7': 50, 'DIA': 25, 'CHE': 15, 'WRENCH': 10, 'SNAKE': 10, 'DISK': 8 };
function __slMakeStrips() {
  // 三条独立随机带
  return [0, 1, 2].map(function () {
    var strip = SL_STRIP_BASE.slice();
    for (var i = strip.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = strip[i]; strip[i] = strip[j]; strip[j] = t;
    }
    return strip;
  });
}
// 中线判定 → {mult, desc}（mult 为下注倍数，0=未中）
function __slJudge(line) {
  var a = line[0], b = line[1], c2 = line[2];
  if (a === b && b === c2) return { mult: SL_PAYTABLE[a] || 8, desc: '三连 ' + a };
  if (a === '7' && (b === '7' || c2 === '7')) return { mult: 3, desc: '双 7' };
  var pair = (a === b) ? a : (b === c2 ? b : (a === c2 ? a : null));
  if (pair === 'DIA') return { mult: 2, desc: '双钻' };
  if (pair === 'CHE') return { mult: 1, desc: '双樱桃（回本）' };
  return { mult: 0, desc: '未中' };
}

var SLOT_BETS = [10, 50, 100];

// ---------- 老虎机桌 ----------
class CasinoSlots {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.banner = null;
    this.shake = 0;
    this._posCache = null;
    // 三轴状态：pos=带索引（浮点），vel=格/帧，target=目标索引，stopped
    this.reels = [0, 0, 0].map(function () { return { pos: Math.random() * 20, vel: 0, target: null, stopping: false, stopAt: 0 }; });
    this.strips = __slMakeStrips();
    this.lever = 0;        // 摇杆拉动进度 0..1
    this.leverPull = 0;    // 拉动动画起点
    this.lights = 0;       // 中奖灯光追逐起点
    this.betAmt = SLOT_BETS[0];
    this._buildDom(container);
    this._awaitBet();
  }

  _el(tag, css, html) {
    var e = document.createElement(tag);
    if (css) e.style.cssText = css;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  _buildDom(container) {
    var self = this;
    this.root = this._el('div', 'position:absolute;inset:0;color:#ecd9b8;pointer-events:none');
    var bar = this._el('div', 'position:absolute;top:10px;left:10px;display:flex;gap:8px;pointer-events:auto');
    var exitBtn = this._el('button', 'padding:4px 12px;border-radius:6px;border:1px solid rgba(240,120,100,.4);background:rgba(10,5,3,.45);color:#e0a090;cursor:pointer;font-family:inherit;font-size:11px', '← 离开');
    exitBtn.onclick = function () { self.destroy(); self.ctx.exit(); };
    bar.appendChild(exitBtn);
    this.root.appendChild(bar);
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:200px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px 12px;pointer-events:auto;max-width:94vw;box-sizing:border-box', '');
    this.root.appendChild(this.actEl);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }

  _awaitBet() {
    this.phase = 'bet';
    this._msg('选筹码 → 拉杆 SPIN');
    Casino.audio.play('voice-bets', 0.5);
    this._renderActions();
  }

  spin() {
    if (this.phase === 'spin') return;
    if (!this.wallet.sub(this.betAmt)) { this._msg('算力不足'); return; }
    this.phase = 'spin';
    this.leverPull = this.tick;
    this.lastWin = null;
    this.fx = [];
    // 结果先行：每轴随机停点
    var self = this;
    this.reels.forEach(function (r, i) {
      r.target = Math.floor(Math.random() * 20);
      r.stopping = false;
      r.stopped = false;          // 重置停轴标志（否则第二局秒结算不转）
      r.vel = 0.55 + i * 0.06;   // 起转速度（格/帧）
      r.stopAt = self.tick + 70 + i * 50; // 匀速转一阵后依次停（最后 26 帧减速）
    });
    this._msg('转动中…');
    Casino.audio.play('card-shuffle', 0.35);
    this._renderActions();
  }

  _finish() {
    this.phase = 'settle';
    var line = this.reels.map(function (r, i) { return this.strips[i][(Math.round(r.pos) % 20 + 20) % 20]; }, this);
    var j = __slJudge(line);
    var win = this.betAmt * j.mult;
    if (win > 0) {
      this.wallet.add(win);
      this.lights = this.tick;
      this.fx.push({ kind: 'coins', start: this.tick, dur: 110 });
      this.shake = { amp: 6, start: this.tick, dur: 16 };
      if (j.mult >= 15) Casino.audio.play('voice-jackpot', 0.95);
      else Casino.audio.play('voice-win', 0.85);
      this.banner = { text: j.mult >= 15 ? 'JACKPOT ×' + j.mult : j.desc + ' ×' + j.mult + '  +' + win, color: '#ffd98a', start: this.tick, dur: 110 };
      this._msg(j.desc + ' · 赢 ' + win + '！');
    } else {
      Casino.audio.play('voice-lose', 0.6);
      this._msg('未中 · ' + line.join(' '));
    }
    this._renderActions();
  }

  _renderActions() {
    var self = this;
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b> · 下注 <b>' + this.betAmt + '</b></span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet' || this.phase === 'settle') {
      if (this.wallet.get() < SLOT_BETS[0]) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f');
        if (!this.wallet.canBailout()) { bb.disabled = true; bb.style.opacity = .5; bb.style.cursor = 'not-allowed'; }
        self.actEl.appendChild(bb);
        return;
      }
      SLOT_BETS.forEach(function (v) {
        var b = mk('筹码 ' + v, function () { self.betAmt = v; self._renderActions(); }, self.betAmt === v ? '#ffd98a' : '#8a6a4a');
        if (self.betAmt === v) b.style.background = 'rgba(70,40,12,.95)';
        self.actEl.appendChild(b);
      });
      this.actEl.appendChild(mk('🎰 SPIN 拉杆', function () { self.spin(); }, '#e06060'));
      return;
    }
  }

  // ---------- 场景 ----------
  renderScene(c, w, h, t) {
    if (this.destroyed) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    this._posCache = { pot: [w / 2, h * 0.62], player: [w / 2, h * 0.86] };
    c.save();
    if (this.shake) {
      var sp = (this.tick - this.shake.start) / this.shake.dur;
      if (sp < 1) {
        var amp = this.shake.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      } else this.shake = 0;
    }
    P.table(c, w, h);
    // 机器主体（桌上中央偏上）
    this._cabinet(c, w, h, s, t);
    this._drawFx(c, s);
    c.restore();
    this._drawBanner(c, w, h);
  }

  _symDraw(c, sym, x, y, size) {
    var map = {
      '7': { t: '7', col: '#ff5040', font: '900 ' + size + 'px Georgia,serif' },
      'DIA': { t: '◆', col: '#7fd8ff', font: size + 'px Georgia,serif' },
      'CHE': { t: '🍒', col: '#ff8a90', font: size + 'px sans-serif' },
      'WRENCH': { t: '🔧', col: '#d8b890', font: size + 'px sans-serif' },
      'SNAKE': { t: '🐍', col: '#a0e8a0', font: size + 'px sans-serif' },
      'DISK': { t: '💾', col: '#c0c8ff', font: size + 'px sans-serif' }
    };
    var m = map[sym] || map.CHE;
    c.font = m.font;
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = m.col;
    if (sym === '7') { c.shadowColor = '#ff3020'; c.shadowBlur = 6; }
    c.fillText(m.t, x, y);
    c.shadowBlur = 0;
  }

  _cabinet(c, w, h, s, t) {
    var mw = Math.min(w * 0.62, 560 * s), mh = mw * 0.62;
    var mx = w / 2, my = h * 0.545;
    // 中奖灯光追逐（顶灯带）
    var winning = this.lights && this.tick - this.lights < 110;
    c.save();
    c.translate(mx, my);
    // 机身
    var body = c.createLinearGradient(0, -mh / 2, 0, mh / 2);
    body.addColorStop(0, '#54331a'); body.addColorStop(0.5, '#3a2010'); body.addColorStop(1, '#1c0e06');
    c.fillStyle = body;
    this._rr(c, -mw / 2, -mh / 2, mw, mh, 18 * s);
    c.fill();
    c.strokeStyle = 'rgba(255,200,120,.55)'; c.lineWidth = 2; c.stroke();
    // 顶部灯带（追逐）
    var bulbs = 9;
    for (var b = 0; b < bulbs; b++) {
      var bx = -mw / 2 + 14 * s + (b / (bulbs - 1)) * (mw - 28 * s);
      var on = winning ? (Math.floor((this.tick - this.lights) / 4) % bulbs === b) : ((b + Math.floor(this.tick * 0.03)) % 4 === 0);
      c.fillStyle = on ? '#ffd98a' : 'rgba(120,80,40,.6)';
      if (on) { c.shadowColor = '#ffc87a'; c.shadowBlur = 10; }
      c.beginPath(); c.arc(bx, -mh / 2 + 12 * s, 4.5 * s, 0, Math.PI * 2); c.fill();
      c.shadowBlur = 0;
    }
    // 顶部招牌
    c.font = '900 ' + Math.round(mw * 0.055) + 'px monospace';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillStyle = winning ? '#ffe9c0' : '#ff9f5a';
    c.shadowColor = '#ff5f30'; c.shadowBlur = winning ? 18 : 10 + 4 * Math.sin(this.tick * 0.08);
    c.fillText('S L O T S · 算 力 老虎 机', 0, -mh / 2 + 30 * s);
    c.shadowBlur = 0;
    // 赔率表（招牌下、卷轴上，赌场惯例明示）
    c.font = Math.round(mw * 0.026) + 'px monospace';
    c.fillStyle = 'rgba(255,224,170,.82)';
    c.fillText('三连：777×50 ◆×25 樱×15 🔧×10 🐍×10 💾×8', 0, -mh / 2 + 46 * s);
    c.fillStyle = 'rgba(255,224,170,.62)';
    c.fillText('两同：双7×3 · 双钻×2 · 双樱×1', 0, -mh / 2 + 60 * s);
    // 三个卷轴窗口
    var reelW = mw * 0.22, reelH = mh * 0.46;
    var gap = reelW * 1.18;
    for (var i = 0; i < 3; i++) {
      var rx = (i - 1) * gap;
      var r = this.reels[i];
      // 窗框
      c.fillStyle = '#0d0805';
      this._rr(c, rx - reelW / 2 - 4 * s, -reelH / 2 - 4 * s, reelW + 8 * s, reelH + 8 * s, 8 * s);
      c.fill();
      c.save();
      this._rr(c, rx - reelW / 2, -reelH / 2, reelW, reelH, 6 * s);
      c.clip();
      // 卷轴背景
      var rg = c.createLinearGradient(0, -reelH / 2, 0, reelH / 2);
      rg.addColorStop(0, '#241610'); rg.addColorStop(0.5, '#160c08'); rg.addColorStop(1, '#241610');
      c.fillStyle = rg;
      c.fillRect(rx - reelW / 2, -reelH / 2, reelW, reelH);
      // 符号：中心线上下各 1 格（共 3 格可见）
      var cell = reelH / 2.4;
      var base = Math.round(r.pos);
      var frac = r.pos - base;
      var fast = r.vel > 0.18; // 高速旋转：运动模糊
      for (var k2 = -1; k2 <= 1; k2++) {
        var idx = ((base + k2) % 20 + 20) % 20;
        var y = k2 * cell + frac * cell;
        var sym = this.strips[i][idx];
        if (fast) {
          // 运动模糊：拖影
          c.globalAlpha = 0.45;
          this._symDraw(c, sym, rx, y + r.vel * cell * 0.8, cell * 0.6);
          c.globalAlpha = 0.8;
          this._symDraw(c, sym, rx, y, cell * 0.6);
          c.globalAlpha = 1;
        } else {
          this._symDraw(c, sym, rx, y, cell * 0.62);
        }
      }
      // 窗口上下渐隐
      var fade = c.createLinearGradient(0, -reelH / 2, 0, reelH / 2);
      fade.addColorStop(0, 'rgba(5,3,2,.95)'); fade.addColorStop(0.22, 'rgba(5,3,2,0)');
      fade.addColorStop(0.78, 'rgba(5,3,2,0)'); fade.addColorStop(1, 'rgba(5,3,2,.95)');
      c.fillStyle = fade;
      c.fillRect(rx - reelW / 2, -reelH / 2, reelW, reelH);
      c.restore();
      // 窗框描边
      c.strokeStyle = 'rgba(255,200,120,.5)'; c.lineWidth = 1.5;
      this._rr(c, rx - reelW / 2, -reelH / 2, reelW, reelH, 6 * s);
      c.stroke();
    }
    // 中线指示（红色箭头 + 发光线）
    var lineOn = winning ? Math.sin(this.tick * 0.3) > 0 : false;
    c.strokeStyle = lineOn ? 'rgba(255,80,60,.95)' : 'rgba(255,80,60,.45)';
    c.lineWidth = lineOn ? 2.5 : 1.5;
    if (lineOn) { c.shadowColor = '#ff3020'; c.shadowBlur = 8; }
    c.beginPath(); c.moveTo(-gap - reelW / 2 - 14 * s, 0); c.lineTo(gap + reelW / 2 + 14 * s, 0); c.stroke();
    c.shadowBlur = 0;
    [-gap - reelW / 2 - 14 * s, gap + reelW / 2 + 14 * s].forEach(function (ax) {
      var dir = ax < 0 ? 1 : -1;
      c.fillStyle = lineOn ? '#ff5040' : 'rgba(255,80,60,.7)';
      c.beginPath();
      c.moveTo(ax, -6 * s); c.lineTo(ax + dir * 9 * s, 0); c.lineTo(ax, 6 * s);
      c.closePath(); c.fill();
    });
    // 摇杆（右侧）
    this._lever(c, mw / 2, s);
    c.restore();
  }
  _lever(c, attachX, s) {
    var p = this.leverPull ? Math.max(0, Math.min(1, (this.tick - this.leverPull) / 14)) : 0;
    // 拉下再回弹
    var pull = p < 0.5 ? p * 2 : (1 - p) * 2;
    var baseY = -30 * s, tipY = baseY - 52 * s + pull * 60 * s;
    c.save();
    c.strokeStyle = '#8a8f9a'; c.lineWidth = 6 * s; c.lineCap = 'round';
    c.beginPath(); c.moveTo(attachX + 16 * s, baseY); c.lineTo(attachX + 22 * s, tipY); c.stroke();
    c.fillStyle = '#e05040';
    c.shadowColor = '#ff3020'; c.shadowBlur = 8;
    c.beginPath(); c.arc(attachX + 22 * s, tipY, 10 * s, 0, Math.PI * 2); c.fill();
    c.shadowBlur = 0;
    // 底座
    c.fillStyle = '#3a2512';
    this._rr(c, attachX + 4 * s, baseY - 6 * s, 18 * s, 14 * s, 4 * s);
    c.fill();
    c.restore();
  }
  _rr(c, x, y, w2, h2, r) {
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w2, y, x + w2, y + h2, r);
    c.arcTo(x + w2, y + h2, x, y + h2, r);
    c.arcTo(x, y + h2, x, y, r);
    c.arcTo(x, y, x + w2, y, r);
    c.closePath();
  }
  _drawFx(c, s) {
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'coins') {
        // 金币雨
        for (var i = 0; i < 14; i++) {
          var cx = ((i * 137.5 + self.tick * (2 + i % 3)) % 100) / 100;
          var cy2 = ((i * 79.3 + self.tick * (3 + i % 4)) % 110) / 110;
          var x = self._posCache.pot[0] + (cx - 0.5) * 460 * s;
          var y = self._posCache.pot[1] - 60 * s + cy2 * 240 * s;
          c.fillStyle = i % 2 ? '#ffc87a' : '#ffe3ad';
          c.beginPath(); c.ellipse(x, y, 6, 3, cy2 * 6, 0, Math.PI * 2); c.fill();
        }
      }
    });
  }
  _drawBanner(c, w, h) {
    if (!this.banner) return;
    var p = Math.min(1, (this.tick - this.banner.start) / this.banner.dur);
    var inS = Math.min(1, p * 6);
    var out = p > 0.85 ? (1 - p) / 0.15 : 1;
    var scale = 0.6 + 0.4 * (1 - Math.pow(1 - inS, 2));
    c.save();
    c.translate(w / 2, h * 0.24);
    c.scale(scale, scale);
    c.globalAlpha = Math.max(0, inS * out);
    c.font = '700 ' + Math.max(20, w * 0.034) + 'px monospace';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.shadowColor = this.banner.color; c.shadowBlur = 26;
    c.fillStyle = this.banner.color;
    c.fillText(this.banner.text, 0, 0);
    c.restore();
  }

  // ---------- 帧驱动：卷轴物理 ----------
  // bot 模式自动拉杆（自动化测试/浸泡用）
  _botStep() {
    if (this.tick < 30 || this.tick % 50 !== 30) return;
    if (this.wallet.get() >= this.betAmt) this.spin();
    else this.wallet.bailout();
  }
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.phase === 'bet' && this.bot) this._botStep();
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur + 20; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.phase !== 'spin') return;
    var allStopped = true;
    this.reels.forEach(function (r, i) {
      if (r.stopped) return;
      allStopped = false;
      if (self.tick < r.stopAt - 26) {
        // 匀速转
        r.pos += r.vel;
      } else if (self.tick < r.stopAt) {
        // 减速逼近目标
        var target = r.target + Math.ceil((r.pos - r.target) / 20) * 20; // 下一个周期里的目标
        var k = (self.tick - (r.stopAt - 26)) / 26;
        var ease = 1 - Math.pow(1 - k, 3);
        r.pos = r.pos + (target - r.pos) * (0.06 + 0.2 * ease);
        r.vel = Math.max(0.05, r.vel * 0.9);
      } else {
        // 回弹停定
        if (r.vel > 0.001) {
          r.vel *= 0.6;
          r.pos += r.vel;
        } else {
          r.pos = Math.round(r.pos);
          r.vel = 0;
          r.stopped = true;
          Casino.audio.play('card-place', 0.55);
        }
      }
      r.pos = ((r.pos % 20) + 20) % 20;
    });
    if (allStopped) this._finish();
  }

  destroy() { this.destroyed = true; }
}

Casino.register('slots', {
  name: '算力老虎机 Slots',
  icon: '🍒',
  desc: '3 轴机械卷轴 · 三连 7 赔 ×50 · 拉杆 SPIN 依次停转',
  create: function (container, ctx) { return new CasinoSlots(container, ctx); }
});

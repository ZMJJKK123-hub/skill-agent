// casino-dice.js — 算力赌坊 · 骰子大小 Sic Bo
// 玩法：押 大(11-17) / 小(4-10) 赔 1:1；三骰同点（围骰）通杀。
// 动画：骰盅摇动（加速→高潮→揭盅）→ 骰子逐颗翻滚落定 → 点数横幅+语音。

// ---------- 引擎（纯函数，供测试） ----------
// 掷三骰 → {dice:[a,b,c], total, triple, big, small}
function __diceRoll(rng) {
  var r = rng || Math.random;
  var dice = [1 + Math.floor(r() * 6), 1 + Math.floor(r() * 6), 1 + Math.floor(r() * 6)];
  var total = dice[0] + dice[1] + dice[2];
  var triple = dice[0] === dice[1] && dice[1] === dice[2];
  return { dice: dice, total: total, triple: triple, big: !triple && total >= 11, small: !triple && total <= 10 };
}
// 押注判定 → 'win' | 'lose'
function __diceJudge(bet, roll) {
  if (bet === 'triple') return roll.triple ? 'win' : 'lose'; // 围骰：任意三同为中
  if (roll.triple) return 'lose';
  return (bet === 'big' && roll.big) || (bet === 'small' && roll.small) ? 'win' : 'lose';
}

var DICE_BETS = [20, 50, 100, 200];
var DICE_SHAKE_TICKS = 130; // 摇盅时长
var DICE_REVEAL_GAP = 26;   // 每颗骰子落定间隔

// ---------- 骰子大小桌 ----------
class CasinoDice {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.history = [];   // 战绩点 W/L
    this.banner = null;
    this.shakeCup = 0;
    this._posCache = null;
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
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:190px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px 12px;pointer-events:auto;max-width:94vw;box-sizing:border-box', '');
    this.root.appendChild(this.actEl);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }
  _fxChips(to, n, delay) {
    this.fx.push({ kind: 'chip', from: 'pot', to: to, start: this.tick + (delay || 0), dur: 24, n: n });
  }

  _awaitBet() {
    this.phase = 'bet';
    this.betAmt = this.betAmt || DICE_BETS[0];
    this.pendingBet = null; // 'big' | 'small' | 'triple'
    // 清上一局残留：逐骰结算标志/揭盅时刻/结果（否则第二局永不结算）
    this._d0 = this._d1 = this._d2 = false;
    this.revealT = 0;
    this.roll = null;
    this._msg('选筹码 → 押 大 / 小 / 围骰');
    Casino.audio.play('voice-bets', 0.7);
    this._renderActions();
  }

  place(bet) {
    if (this.phase !== 'bet') return;
    if (!this.wallet.sub(this.betAmt)) { this._msg('算力不足'); return; }
    this.pendingBet = bet;
    this.phase = 'shake';
    this.shakeT = this.tick;
    this.roll = __diceRoll();
    this._msg((bet === 'big' ? '押大 ' : bet === 'small' ? '押小 ' : '押围骰 ') + this.betAmt + ' · 摇盅中…');
    Casino.audio.play('coins', 0.5);
    Casino.audio.play('voice-no-more', 0.7);
    this._renderActions();
  }

  _reveal(i) {
    Casino.audio.play('card-place', 0.6);
    if (i === 2) {
      var roll = this.roll;
      var verdict = __diceJudge(this.pendingBet, roll);
      this.phase = 'settle';
      this.history.push(verdict === 'win' ? 'W' : 'L');
      if (this.history.length > 14) this.history.shift();
      var isTripleBet = this.pendingBet === 'triple';
      var winAmt = verdict === 'win' ? (isTripleBet ? this.betAmt * 31 : this.betAmt * 2) : 0; // 围骰 30 赔 1
      if (winAmt) {
        this.wallet.add(winAmt);
        for (var k = 0; k < 3; k++) this._fxChips('player', winAmt / 3, k * 5);
      }
      var txt = roll.triple
        ? '围骰 ' + roll.dice[0] + '！' + (isTripleBet ? '押中 ×30' : '通杀')
        : (roll.total >= 11 ? '大 ' + roll.total : '小 ' + roll.total);
      this._msg(txt + ' · ' + (verdict === 'win' ? '你赢了 ' + (winAmt - this.betAmt) : '输了 ' + this.betAmt));
      this.banner = {
        text: roll.triple ? '围骰 ' + roll.dice[0] + '！' + (isTripleBet ? ' ×30' : '') : (roll.total >= 11 ? '大 ' + roll.total : '小 ' + roll.total) + (verdict === 'win' ? ' · 你赢 +' + this.betAmt : ''),
        color: verdict === 'win' ? '#ffd98a' : '#e08080', start: this.tick, dur: 90
      };
      Casino.audio.play(roll.triple ? 'voice-triple' : roll.total >= 11 ? 'voice-big' : 'voice-small', 0.85);
      if (verdict === 'win') {
        Casino.audio.play(isTripleBet ? 'voice-jackpot' : 'voice-win', 0.9);
        this.shakeCup = { amp: isTripleBet ? 9 : 6, start: this.tick, dur: 12 };
      } else {
        Casino.audio.play('voice-lose', 0.7);
      }
      this._renderActions();
    }
  }

  _renderActions() {
    var self = this;
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b>' + (this.pendingBet ? ' · 押' + (this.pendingBet === 'big' ? '大' : this.pendingBet === 'small' ? '小' : '围骰') + ' <b>' + this.betAmt + '</b>' : '') + '</span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet') {
      if (this.wallet.get() < DICE_BETS[0]) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f');
        if (!this.wallet.canBailout()) { bb.disabled = true; bb.style.opacity = .5; bb.style.cursor = 'not-allowed'; }
        this.actEl.appendChild(bb);
        return;
      }
      DICE_BETS.forEach(function (v) {
        var b = mk('筹码 ' + v, function () { self.betAmt = v; self._renderActions(); }, self.betAmt === v ? '#ffd98a' : '#8a6a4a');
        if (self.betAmt === v) b.style.background = 'rgba(70,40,12,.95)';
        self.actEl.appendChild(b);
      });
      this.actEl.appendChild(mk('押 大 (11-17)', function () { self.place('big'); }, '#e06060'));
      this.actEl.appendChild(mk('押 小 (4-10)', function () { self.place('small'); }, '#5fa8e0'));
      this.actEl.appendChild(mk('押 围骰 ×30', function () { self.place('triple'); }, '#b070e0'));
      return;
    }
    if (this.phase === 'settle') {
      this.actEl.appendChild(mk('🔄 再来一局', function () { self._awaitBet(); }, '#ffc87a'));
    }
  }

  // ---------- 场景 ----------
  renderScene(c, w, h, t) {
    if (this.destroyed) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    this._posCache = {
      pot: [w / 2, h * 0.60],
      player: [w / 2, h * 0.80],
      cup: [w / 2, h * 0.60]
    };
    c.save();
    if (this.shakeCup) {
      var sp = (this.tick - this.shakeCup.start) / this.shakeCup.dur;
      if (sp < 1) {
        var amp = this.shakeCup.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      } else this.shakeCup = 0;
    }
    P.table(c, w, h);
    Casino.paint.histDots(c, w, h, this.history);
    // 荷官
    P.seat(c, w / 2, h * 0.36, t, { name: '荷官', color: '#c8a050', persona: 'bluff', scale: s * 1.25, active: false, chipsLabel: '' });
    // 桌面押注区：大 / 小（带高亮）
    this._zones(c, w, h, s);
    if (this.phase === 'shake') this._cup(c, w, h, s, t);
    if (this.roll && this.phase !== 'shake') this._dice(c, w, h, s, t);
    this._drawFx(c, s);
    c.restore();
    this._drawBanner(c, w, h);
  }
  _zones(c, w, h, s) {
    var zones = [
      { key: 'big', label: '大 11-17', x: w * 0.34, col: 'rgba(224,96,96,' },
      { key: 'small', label: '小 4-10', x: w * 0.66, col: 'rgba(95,168,224,' }
    ];
    for (var i = 0; i < 2; i++) {
      var z = zones[i];
      var hl = this.pendingBet === z.key;
      var pulse = hl ? 0.2 + 0.12 * Math.abs(Math.sin(this.tick * 0.1)) : 0.10;
      c.save();
      c.fillStyle = z.col + pulse + ')';
      c.strokeStyle = z.col.replace(',1', '') + (hl ? 0.9 : 0.45) + ')';
      c.lineWidth = 2;
      var zw = w * 0.19, zh = h * 0.10;
      this._rr(c, z.x - zw / 2, h * 0.60 - zh / 2, zw, zh, 10 * s);
      c.fill(); c.stroke();
      c.fillStyle = hl ? '#ffe9c0' : 'rgba(230,210,180,.75)';
      c.font = '700 ' + Math.round(14 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(z.label, z.x, h * 0.60);
      if (hl) {
        c.font = Math.round(11 * s) + 'px monospace';
        c.fillStyle = '#ffd98a';
        c.fillText('押 ' + this.betAmt, z.x, h * 0.60 + zh / 2 + 12 * s);
      }
      c.restore();
    }
  }
  _cup(c, w, h, s, t) {
    var p = Math.min(1, (this.tick - this.shakeT) / DICE_SHAKE_TICKS);
    var amp = p < 0.2 ? p * 5 : p < 0.8 ? 1 : (1 - p) * 5; // 摇动强度包络
    var x = w / 2 + Math.sin(this.tick * 0.9) * 7 * s * amp;
    var y = h * 0.60 + Math.cos(this.tick * 1.3) * 4 * s * amp;
    var rot = Math.sin(this.tick * 0.7) * 0.18 * amp;
    if (Math.abs(Math.sin(this.tick * 0.45)) > 0.985) Casino.audio.play('card-hits', 0.25); // 摇盅撞击声
    c.save();
    c.translate(x, y);
    c.rotate(rot);
    var cw2 = 56 * s, ch2 = 66 * s;
    var g = c.createLinearGradient(0, -ch2 / 2, 0, ch2 / 2);
    g.addColorStop(0, '#6a4a26'); g.addColorStop(0.5, '#3a2512'); g.addColorStop(1, '#1a0e06');
    c.fillStyle = g;
    c.beginPath();
    c.moveTo(-cw2 / 2, ch2 / 2);
    c.quadraticCurveTo(-cw2 / 2, -ch2 / 2, 0, -ch2 / 2);
    c.quadraticCurveTo(cw2 / 2, -ch2 / 2, cw2 / 2, ch2 / 2);
    c.closePath(); c.fill();
    c.strokeStyle = 'rgba(255,200,120,.5)'; c.lineWidth = 1.6; c.stroke();
    c.fillStyle = 'rgba(255,200,120,.12)';
    for (var i = 0; i < 3; i++) c.fillRect(-cw2 * 0.36, -ch2 * 0.3 + i * ch2 * 0.26, cw2 * 0.72, 2.4 * s);
    c.restore();
  }
  _dice(c, w, h, s, t) {
    var dsz = 40 * s;
    var revealT = this.revealT || this.shakeT + DICE_SHAKE_TICKS;
    for (var i = 0; i < 3; i++) {
      var t0 = revealT + 16 + i * DICE_REVEAL_GAP;
      var prog = Math.max(0, Math.min(1, (this.tick - t0) / 16));
      if (prog <= 0) continue;
      var targetX = w / 2 + (i - 1) * dsz * 1.9;
      // 落定前翻滚（旋转+弹跳插值）
      var rot = (1 - prog) * (4 + i) + Math.sin(this.tick * 0.05 + i) * 0.04;
      var bounce = Math.abs(Math.sin(prog * Math.PI)) * 26 * s * (1 - prog * 0.4);
      var alpha = Math.min(1, prog * 2);
      this._die(c, targetX, h * 0.60 - bounce, dsz * (0.6 + 0.4 * prog), this.roll.dice[i], rot, alpha, 1);
    }
  }
  _die(c, x, y, size, value, rot, alpha, faceProg) {
    c.save();
    c.globalAlpha = alpha;
    c.translate(x, y);
    c.rotate(rot);
    // 立方体感：亮面+暗面
    var g = c.createLinearGradient(-size / 2, -size / 2, size / 2, size / 2);
    g.addColorStop(0, '#f8f2e2'); g.addColorStop(1, '#d8ccae');
    c.fillStyle = g;
    this._rr(c, -size / 2, -size / 2, size, size, size * 0.18);
    c.fill();
    c.strokeStyle = 'rgba(90,50,20,.6)'; c.lineWidth = 1; c.stroke();
    // 点数（经典布局）
    var pip = size * 0.13;
    c.fillStyle = '#2a1a10';
    var L = -size * 0.26, R = size * 0.26, C = 0;
    var layout = {
      1: [[C, C]],
      2: [[L, L], [R, R]],
      3: [[L, L], [C, C], [R, R]],
      4: [[L, L], [R, L], [L, R], [R, R]],
      5: [[L, L], [R, L], [C, C], [L, R], [R, R]],
      6: [[L, L], [R, L], [L, C], [R, C], [L, R], [R, R]]
    };
    (layout[value] || []).forEach(function (p2) {
      c.beginPath();
      c.arc(p2[0], p2[1], pip, 0, Math.PI * 2);
      c.fill();
    });
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
    if (!this.fx.length) return;
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'chip') {
        var pc = self._posCache;
        var x = pc.pot[0] + (pc.player[0] - pc.pot[0]) * p;
        var y = pc.pot[1] + (pc.player[1] - pc.pot[1]) * p - Math.sin(Math.PI * p) * 40;
        Casino.paint.chips(c, x, y, Math.max(10, Math.round((f.n || 20) / 2)));
      }
    });
  }
  _drawBanner(c, w, h) {
    if (!this.banner) return;
    var p = Math.min(1, (this.tick - this.banner.start) / this.banner.dur);
    var inS = Math.min(1, p * 6);
    var out = p > 0.8 ? (1 - p) / 0.2 : 1;
    var scale = 0.6 + 0.4 * (1 - Math.pow(1 - inS, 2));
    c.save();
    c.translate(w / 2, h * 0.295);
    c.scale(scale, scale);
    c.globalAlpha = Math.max(0, inS * out);
    c.font = '700 ' + Math.max(20, w * 0.034) + 'px monospace';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.shadowColor = this.banner.color; c.shadowBlur = 26;
    c.fillStyle = this.banner.color;
    c.fillText(this.banner.text, 0, 0);
    c.restore();
  }

  // ---------- 帧驱动 ----------
  // bot 模式自动下注（大小/围骰随机；自动化测试/浸泡用）
  _botStep() {
    if (this.tick < 30 || this.tick % 50 !== 30) return;
    var w = this.wallet.get();
    if (w >= 20) {
      this.betAmt = 20;
      this.place(['big', 'small', 'triple'][Math.floor(Math.random() * 3)]);
    } else this.wallet.bailout();
  }
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.phase === 'bet' && this.bot) this._botStep();
    if (this.bot && this.phase === 'settle' && this.tick % 40 === 20) this._awaitBet();
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur + 20; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.phase === 'shake') {
      if (!this.revealT && this.tick - this.shakeT >= DICE_SHAKE_TICKS) {
        this.revealT = this.tick;
        this._msg('开！');
      }
      if (this.revealT) {
        // 逐颗骰子落定声/结算
        for (var i = 0; i < 3; i++) {
          if (this.tick >= this.revealT + 16 + i * DICE_REVEAL_GAP && !this['_d' + i]) {
            this['_d' + i] = true;
            this._reveal(i);
          }
        }
      }
      return;
    }
  }

  destroy() { this.destroyed = true; }
}

Casino.register('dice', {
  name: '骰子大小 Sic Bo',
  icon: '🎲',
  desc: '押大(11-17)或押小(4-10) · 赔 1:1 · 围骰通杀 · 摇盅揭盅逐颗开',
  create: function (container, ctx) { return new CasinoDice(container, ctx); }
});

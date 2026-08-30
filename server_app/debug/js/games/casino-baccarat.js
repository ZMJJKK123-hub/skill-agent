// casino-baccarat.js — 算力赌坊 · 百家乐 Punto Banco
// 押 闲 1:1 / 庄 0.95:1 / 和 8:1。天牌 8-9 直接停牌；补牌规则完整实现
// （闲 0-5 补；庄按闲家第三张的规则表）。珠盘路记近 14 局。
// 动画：牌靴交替发牌（闲庄闲庄）盖牌→逐张翻开→补牌仪式→结算横幅+语音。

// ---------- 引擎（纯函数，供测试） ----------
function __bcVal(card) { if (card.r === 14) return 1; return card.r >= 10 ? 0 : card.r; } // A 先判，再 10/J/Q/K 归 0
function __bcTotal(hand) {
  return hand.reduce(function (a, c) { return a + __bcVal(c); }, 0) % 10;
}
function __bcNewDeck() {
  var d = [];
  for (var s = 0; s < 4; s++) for (var r = 2; r <= 14; r++) d.push({ r: r, s: s });
  return d;
}
function __bcShuffle(d) {
  for (var i = d.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = d[i]; d[i] = d[j]; d[j] = t;
  }
  return d;
}
// 闲家是否补牌（0-5 补，6-7 停）
function __bcPlayerDraws(pHand) { return __bcTotal(pHand) <= 5; }
// 庄家是否补牌（标准规则表；pThird=闲家第三张的点值，null=闲家未补牌）
function __bcBankerDraws(bHand, pThird) {
  var bt = __bcTotal(bHand);
  if (pThird === null || pThird === undefined) return bt <= 5;
  var v = (typeof pThird === 'object') ? __bcVal(pThird) : pThird; // 传牌或点值均可
  if (bt <= 2) return true;
  if (bt === 3) return v !== 8;
  if (bt === 4) return v >= 2 && v <= 7;
  if (bt === 5) return v >= 4 && v <= 7;
  if (bt === 6) return v === 6 || v === 7;
  return false; // 7 停
}
function __bcOutcome(pHand, bHand) {
  var p = __bcTotal(pHand), b = __bcTotal(bHand);
  if (p > b) return 'player';
  if (b > p) return 'banker';
  return 'tie';
}
// 赔付（返还倍数）：闲 2 / 庄 1.95 / 和 9；非本方下注的和局退回 1
function __bcPayout(betType, outcome) {
  if (outcome === 'tie') return betType === 'tie' ? 9 : 1; // 和局退注
  if (outcome === 'player') return betType === 'player' ? 2 : 0;
  return betType === 'banker' ? 1.95 : 0;
}
// 大路 Big Road：连续同结果成一列（最多 6 颗，超出起新列）；和局挂到上一颗（绿斜线计数），
// 开局前的和局记到首个结果上。输入为时间正序的 outcome 数组，输出列结构。
function __bcBigRoad(outcomes) {
  var cols = [], pend = 0;
  outcomes.forEach(function (o) {
    if (o === 'tie') {
      if (cols.length) {
        var lc = cols[cols.length - 1];
        var last = lc.cells[lc.cells.length - 1];
        last.ties = (last.ties || 0) + 1;
      } else pend++;
      return;
    }
    var cell = { outcome: o, ties: pend };
    pend = 0;
    var cur = cols.length ? cols[cols.length - 1] : null;
    if (cur && cur.outcome === o && cur.cells.length < 6) cur.cells.push(cell);
    else cols.push({ outcome: o, cells: [cell] });
  });
  return cols;
}

var BC_BETS = [
  { key: 'player', label: '闲 PLAYER', cls: '#5fa8e0', mult: '1:1' },
  { key: 'banker', label: '庄 BANKER', cls: '#e06060', mult: '0.95:1' },
  { key: 'tie', label: '和 TIE', cls: '#7ee8a0', mult: '8:1' }
];
var BC_CHIPS = [20, 50, 100];
var BC_DEAL_GAP = 18, BC_FLIGHT = 12;

// ---------- 百家乐桌 ----------
class CasinoBaccarat {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.banner = null;
    this.shake = 0;
    this.history = []; // {outcome, p, b}
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
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:196px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px 12px;pointer-events:auto;max-width:94vw;box-sizing:border-box', '');
    this.root.appendChild(this.actEl);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }
  _fxText(text, color, big) {
    this.fx.push({ kind: 'text', at: 'center', text: text, color: color || '#ffd98a', start: this.tick, dur: 46, big: !!big });
  }
  _fxChips(n, delay) {
    this.fx.push({ kind: 'chip', start: this.tick + (delay || 0), dur: 24, n: n });
  }
  _fxShake(amp, dur) { this.shake = { amp: amp, start: this.tick, dur: dur }; }

  _awaitBet() {
    this.phase = 'bet';
    this.deck = __bcShuffle(__bcNewDeck());
    this.pHand = [];
    this.bHand = [];
    this.bet = null; // {key, amt}
    this.outcome = null;
    this.revealed = 0;   // 已翻开的牌数（按发牌序 P0 B0 P1 B1 [P2] [B2]）
    this.dealSeq = 0;
    this.dealT = 0;
    this.pThird = null;  // 闲家是否补了第三张
    this._msg('押 闲 / 庄 / 和');
    Casino.audio.play('voice-bets', 0.7);
    this._renderActions();
  }

  place(key) {
    if (this.phase !== 'bet') return;
    this.chipAmt = this.chipAmt || BC_CHIPS[0];
    if (!this.wallet.sub(this.chipAmt)) { this._msg('算力不足'); return; }
    this.bet = { key: key, amt: this.chipAmt };
    this.phase = 'deal';
    this.dealT = this.tick;
    this.dealSeq = 0;
    this._msg((key === 'player' ? '押闲' : key === 'banker' ? '押庄' : '押和') + ' ' + this.chipAmt + ' · 发牌…');
    Casino.audio.play('card-shuffle', 0.55);
    Casino.audio.play('voice-no-more', 0.7);
    this._renderActions();
  }
  _dealOne(target) {
    var card = this.deck.pop();
    (target === 'p' ? this.pHand : this.bHand).push(card);
    Casino.audio.play('card-flick', 0.5);
  }
  _cardRevealAt(seqIdx) { // 第 N 张牌翻开时刻
    return this.dealT + 24 + seqIdx * (BC_DEAL_GAP + 14);
  }

  _settle() {
    this.phase = 'settle';
    var oc = __bcOutcome(this.pHand, this.bHand);
    this.outcome = oc;
    this.history.unshift({ outcome: oc, p: __bcTotal(this.pHand), b: __bcTotal(this.bHand) });
    Casino.stats.record('baccarat', 'R');
    if (this.history.length > 14) this.history.pop();
    var mult = __bcPayout(this.bet.key, oc);
    var ret = Math.floor(this.bet.amt * mult);
    if (ret > 0) {
      this.wallet.add(ret);
      this._fxChips(ret, 0);
      this._fxChips(ret, 5);
    }
    var ocName = oc === 'player' ? '闲赢' : oc === 'banker' ? '庄赢' : '和局';
    var net = ret - this.bet.amt;
    this._msg(ocName + ' · 闲 ' + __bcTotal(this.pHand) + ' 点 vs 庄 ' + __bcTotal(this.bHand) + ' 点 · ' + (net > 0 ? '净赢 +' + net : net === 0 ? '打平（和局退注）' : '净输 ' + (-net)));
    this.banner = {
      text: ocName.toUpperCase() + '  ' + __bcTotal(this.pHand) + ' : ' + __bcTotal(this.bHand) + (net > 0 ? '  +' + net : ''),
      color: net > 0 ? '#ffd98a' : (oc === 'tie' ? '#7ee8a0' : '#e08080'),
      start: this.tick, dur: 100
    };
    Casino.audio.play(oc === 'player' ? 'voice-player' : oc === 'banker' ? 'voice-banker' : 'voice-tie', 0.85);
    if (mult > 1.5) { Casino.audio.play('voice-win', 0.8); this._fxShake(6, 12); }
    else if (net < 0) Casino.audio.play('voice-lose', 0.6);
    this._renderActions();
  }

  _renderActions() {
    var self = this;
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b></span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet') {
      if (this.wallet.get() < BC_CHIPS[0]) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f');
        if (!this.wallet.canBailout()) { bb.disabled = true; bb.style.opacity = .5; bb.style.cursor = 'not-allowed'; }
        this.actEl.appendChild(bb);
        return;
      }
      this.chipAmt = this.chipAmt || BC_CHIPS[0];
      BC_CHIPS.forEach(function (v) {
        var b = mk('筹码 ' + v, function () { self.chipAmt = v; self._renderActions(); }, self.chipAmt === v ? '#ffd98a' : '#8a6a4a');
        if (self.chipAmt === v) b.style.background = 'rgba(70,40,12,.95)';
        self.actEl.appendChild(b);
      });
      BC_BETS.forEach(function (bt) {
        self.actEl.appendChild(mk('押 ' + bt.label + ' ' + bt.mult, function () { self.place(bt.key); }, bt.cls));
      });
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
    this._posCache = { shoe: [w / 2, h * 0.44], center: [w / 2, h * 0.58] };
    c.save();
    if (this.shake) {
      var sp = (this.tick - this.shake.start) / this.shake.dur;
      if (sp < 1) {
        var amp = this.shake.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      } else this.shake = 0;
    }
    P.table(c, w, h);
    // 荷官
    P.seat(c, w / 2, h * 0.33, t, { name: '荷官', color: '#c8a050', persona: 'tight', scale: s * 1.2, active: false, chipsLabel: '' });
    // 珠盘路（右上）+ 大路（其下）
    this._beadRoad(c, w, h, s);
    this._bigRoad(c, w, h, s);
    // 庄家手牌（上）/ 闲家手牌（下）
    var revealCut = this._revealCut();
    this._row(c, this.bHand, w / 2, h * 0.545, 'banker', w, s);
    this._row(c, this.pHand, w / 2, h * 0.735, 'player', w, s);
    // 点数标签
    if (this.bHand.length) {
      var bShow = this._shownTotal(this.bHand, 'banker', revealCut);
      this._label(c, w / 2, h * 0.545 + 52 * s, '庄 ' + bShow, '#e0a8a0', s);
    }
    if (this.pHand.length) {
      var pShow = this._shownTotal(this.pHand, 'player', revealCut);
      this._label(c, w / 2, h * 0.735 + 52 * s, '闲 ' + pShow + (this.bet ? ' · 押' + (this.bet.key === 'player' ? '闲' : this.bet.key === 'banker' ? '庄' : '和') + ' ' + this.bet.amt : ''), '#8fbce8', s);
    }
    this._drawFx(c, s);
    c.restore();
    this._drawBanner(c, w, h);
  }
  // 发牌序列里第 n 张是庄还是闲：0 闲 1 庄 2 闲 3 庄 [4 闲] [5 庄]
  _seqTarget(n) { return (n % 2 === 0) ? 'p' : 'b'; }
  _revealCut() { // 当前应翻开几张（0..4..6）
    if (this.phase === 'settle') return 99;
    if (this.phase !== 'deal' && this.phase !== 'third') return 0;
    var n = 0;
    while (n < 6 && this.tick >= this._cardRevealAt(n)) n++;
    return n;
  }
  _shownTotal(hand, side, cut) {
    // 只统计已翻开的牌的点数
    var shown = [];
    for (var i = 0; i < hand.length; i++) {
      var seq = side === 'player' ? (i === 0 ? 0 : i === 1 ? 2 : 4) : (i === 0 ? 1 : i === 1 ? 3 : 5);
      if (seq < cut) shown.push(hand[i]);
    }
    return __bcTotal(shown);
  }
  _row(c, hand, cx, cy, side, w, s) {
    if (!hand.length) return;
    var cw = Math.max(40, Math.min(70, w * 0.055)), chh = cw * 1.45;
    var gap = cw * 0.78;
    var startX = cx - (hand.length - 1) * gap / 2;
    var cut = this._revealCut();
    for (var i = 0; i < hand.length; i++) {
      var seq = side === 'player' ? (i === 0 ? 0 : i === 1 ? 2 : 4) : (i === 0 ? 1 : i === 1 ? 3 : 5);
      // 飞入动画：该牌出现时刻起 12 帧
      var appearT = this.dealT + 20 + seq * (BC_DEAL_GAP + 14) - BC_DEAL_GAP;
      var prog = Math.max(0, Math.min(1, (this.tick - appearT) / BC_FLIGHT));
      if (prog <= 0) continue;
      var x = startX + i * gap;
      var shoe = this._posCache.shoe;
      var px = shoe[0] + (x - shoe[0]) * prog;
      var py = shoe[1] + (cy - shoe[1]) * prog;
      // 翻面：cut 越过 seq 后 10 帧内横翻
      var flip = Math.max(0, Math.min(1, (cut - seq) / 1 * ((this.tick - this._cardRevealAt(seq)) / 10)));
      flip = Math.max(0, Math.min(1, (this.tick - this._cardRevealAt(seq)) / 10));
      var faceUp = this.phase === 'settle' || flip >= 0.5;
      c.save();
      c.translate(px, py);
      if (flip < 1) {
        var sx = 1 - Math.abs(1 - 2 * flip);
        if (sx > 0.05) Casino.paint.card(c, 0, 0, cw * Math.max(0.05, sx), chh, hand[i], faceUp, 0.5 + 0.5 * prog);
      } else {
        Casino.paint.card(c, 0, 0, cw, chh, hand[i], faceUp, 0.5 + 0.5 * prog);
      }
      c.restore();
    }
  }
  _label(c, x, y, text, color, s) {
    c.save();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = '700 ' + Math.round(12 * s) + 'px monospace';
    c.fillStyle = color;
    c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 5;
    c.fillText(text, x, y);
    c.restore();
  }
  _beadRoad(c, w, h, s) {
    var x0 = w * 0.72, y0 = h * 0.14;
    var cell = 20 * s;
    c.save();
    c.fillStyle = 'rgba(240,198,116,.7)';
    c.font = Math.max(9, 11 * s) + 'px monospace';
    c.fillText('珠盘路', x0, y0 - 10 * s);
    // 网格 7×2
    for (var gx = 0; gx < 7; gx++) for (var gy = 0; gy < 2; gy++) {
      var idx = gx * 2 + gy;
      c.strokeStyle = 'rgba(240,198,116,.22)';
      c.strokeRect(x0 + gx * cell, y0 + gy * cell, cell, cell);
      var his = this.history[idx];
      if (!his) continue;
      var col = his.outcome === 'player' ? '#5fa8e0' : his.outcome === 'banker' ? '#e06060' : '#7ee8a0';
      c.fillStyle = col;
      c.beginPath();
      c.arc(x0 + gx * cell + cell / 2, y0 + gy * cell + cell / 2, cell * 0.34, 0, Math.PI * 2);
      c.fill();
      c.fillStyle = '#0d0805';
      c.font = '700 ' + Math.max(7, cell * 0.34) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(his.outcome === 'player' ? '闲' : his.outcome === 'banker' ? '庄' : '和', x0 + gx * cell + cell / 2, y0 + gy * cell + cell / 2);
    }
    c.restore();
  }
  // 大路 Big Road：红圈=庄 蓝圈=闲 绿斜线=和（挂在上一次结果上）
  _bigRoad(c, w, h, s) {
    var x0 = w * 0.72, y0 = h * 0.14 + 46 * s;
    var cell = 15 * s;
    c.save();
    c.fillStyle = 'rgba(240,198,116,.7)';
    c.font = Math.max(9, 11 * s) + 'px monospace';
    c.fillText('大路', x0, y0 - 8 * s);
    var cols = __bcBigRoad(this.history.map(function (x) { return x.outcome; }).reverse()).slice(-8);
    for (var ci = 0; ci < cols.length; ci++) {
      var col = cols[ci];
      for (var ri = 0; ri < col.cells.length; ri++) {
        var cellD = col.cells[ri];
        var cx = x0 + ci * cell + cell / 2, cy = y0 + ri * cell + cell / 2;
        c.strokeStyle = cellD.outcome === 'banker' ? '#e06060' : '#5fa8e0';
        c.lineWidth = 1.8;
        c.beginPath(); c.arc(cx, cy, cell * 0.4, 0, Math.PI * 2); c.stroke();
        if (cellD.ties) {
          c.strokeStyle = '#3aa860'; c.lineWidth = 1.6;
          c.beginPath(); c.moveTo(cx - cell * 0.4, cy + cell * 0.4); c.lineTo(cx + cell * 0.4, cy - cell * 0.4); c.stroke();
          if (cellD.ties > 1) {
            c.fillStyle = '#7ee8a0';
            c.font = '700 ' + Math.max(7, cell * 0.45) + 'px monospace';
            c.textAlign = 'left'; c.textBaseline = 'top';
            c.fillText(String(cellD.ties), cx + cell * 0.34, cy - cell * 0.55);
          }
        }
      }
    }
    c.restore();
  }
  _drawFx(c, s) {
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'chip') {
        var from = self._posCache.center, to = [self._posCache.center[0], self._posCache.center[1] + 180 * s];
        var x = from[0] + (to[0] - from[0]) * p;
        var y = from[1] + (to[1] - from[1]) * p - Math.sin(Math.PI * p) * 40;
        Casino.paint.chips(c, x, y, Math.max(10, Math.round((f.n || 20) / 2)));
      } else if (f.kind === 'text') {
        var at = self._posCache.center;
        c.save();
        c.globalAlpha = p < 0.75 ? 1 : (1 - p) / 0.25;
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.font = '700 ' + (f.big ? 26 : 14) + 'px monospace';
        c.fillStyle = f.color || '#ffd98a';
        c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 6;
        c.fillText(f.text, at[0], at[1] - 120 * s - p * 30);
        c.restore();
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

  // ---------- 帧驱动 ----------
  // bot 模式自动下注（闲/庄/和随机；自动化测试/浸泡用）
  _botStep() {
    if (this.tick < 30 || this.tick % 50 !== 30) return;
    var w = this.wallet.get();
    if (w >= 20) {
      this.chipAmt = 20;
      this.place(['player', 'banker', 'tie'][Math.floor(Math.random() * 3)]);
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
    if (this.shake && this.tick - this.shake.start >= this.shake.dur) this.shake = 0;
    if (this.phase !== 'deal' && this.phase !== 'third') return;

    if (this.phase === 'deal') {
      // 发 4 张（闲庄闲庄），随 reveal 节奏
      var seqN = Math.floor((this.tick - this.dealT - 20) / (BC_DEAL_GAP + 14));
      while (this.dealSeq <= seqN && this.dealSeq < 4) {
        this._dealOne(this._seqTarget(this.dealSeq));
        this.dealSeq++;
      }
      // 4 张发完并全部翻开
      if (this.dealSeq >= 4 && this.tick >= this._cardRevealAt(4) + 12) {
        var pT = __bcTotal(this.pHand), bT = __bcTotal(this.bHand);
        if (pT >= 8 || bT >= 8) {
          // 天牌：直接结算
          this._fxText('天牌 NATURAL ' + (pT >= 8 ? '闲 ' + pT : '庄 ' + bT), '#ffd98a', true);
          Casino.audio.play('voice-natural', 0.85);
          this._natT = this.tick;
          this.phase = 'third';
          this._thirdDone = true; // 不补牌，等展示后结算
          return;
        }
        this.phase = 'third';
        this._thirdStep = 0; // 0=等闲补 1=等庄补 2=结算
        this._stepT = this.tick;
        this._thirdDone = false;
      }
      return;
    }
    // third：补牌仪式（带停顿）
    if (!this._thirdDone) {
      if (this._thirdStep === 0 && this.tick - this._stepT > 40) {
        if (__bcPlayerDraws(this.pHand)) {
          this._dealOne('p');
          this.pThird = this.pHand[2];
          Casino.audio.play('card-flick', 0.5);
          this._msg('闲家补牌…');
          this._stepT = this.tick;
        }
        this._thirdStep = 1;
        return;
      }
      if (this._thirdStep === 1 && this.tick - this._stepT > 50) {
        var pThirdVal = this.pThird ? __bcVal(this.pThird) : null;
        if (__bcBankerDraws(this.bHand, this.pThird)) {
          this._dealOne('b');
          Casino.audio.play('card-flick', 0.5);
          this._msg('庄家补牌…');
          this._stepT = this.tick;
        }
        this._thirdStep = 2;
        return;
      }
      if (this._thirdStep === 2 && this.tick - this._stepT > 50) {
        this._thirdDone = true;
      }
      return;
    }
    // 展示停顿后结算
    if (this.tick - (this._natT || this._stepT) > 45) this._settle();
  }

  destroy() { this.destroyed = true; }
}

Casino.register('baccarat', {
  name: '百家乐 Baccarat',
  icon: '🀄',
  desc: '押闲 1:1 / 庄 0.95:1 / 和 8:1 · 天牌 8-9 停 · 完整补牌规则 · 珠盘路',
  create: function (container, ctx) { return new CasinoBaccarat(container, ctx); }
});

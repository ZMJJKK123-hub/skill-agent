// casino-goldenflower.js — 算力赌坊 · 炸金花（三张牌）
// 牌型：豹子 > 顺金 > 金花 > 顺子 > 对子 > 高张；特例 235 杂色 > 豹子。
// 闷牌（不看）跟注半价，看牌后跟注翻倍；加注 = 底注翻倍；
// 比牌：付一次跟注与任一存活玩家比大小，输者立即弃牌；剩一人或满 5 轮开牌。
// 交互：空格 看自己的牌（盖回仍算已看）；AI 有思考与随机看牌动作。

// ---------- 引擎（纯函数，供测试） ----------
var GF_SUITS = ['♠', '♥', '♣', '♦'];
var GF_RED = [1, 3];
function __gfNewDeck() {
  var d = [];
  for (var s = 0; s < 4; s++) for (var r = 2; r <= 14; r++) d.push({ r: r, s: s });
  return d;
}
function __gfShuffle(d) {
  for (var i = d.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = d[i]; d[i] = d[j]; d[j] = t;
  }
  return d;
}
var GF_RANK_NAMES = ['高张', '对子', '顺子', '金花', '顺金', '豹子'];
// 评估 3 张 → {rank 0..5, keys[], special235}
function __gfEval(h) {
  var rs = h.map(function (c) { return c.r; }).sort(function (a, b) { return b - a; });
  var flush = h[0].s === h[1].s && h[1].s === h[2].s;
  var trips = rs[0] === rs[2];
  var pair = rs[0] === rs[1] || rs[1] === rs[2];
  var straight = false, sHigh = 0;
  if (rs[0] - rs[1] === 1 && rs[1] - rs[2] === 1) { straight = true; sHigh = rs[0]; }
  else if (rs[0] === 14 && rs[1] === 3 && rs[2] === 2) { straight = true; sHigh = 3; } // A32 最小顺
  // 特例 235 杂色 > 豹子
  var special235 = !flush && rs[0] === 5 && rs[1] === 3 && rs[2] === 2;
  if (special235) return { rank: 5.5, keys: [5], special235: true, name: '235 特杀' };
  if (trips) return { rank: 5, keys: [rs[0]], name: '豹子' };
  if (straight && flush) return { rank: 4, keys: [sHigh], name: '顺金' };
  if (flush) return { rank: 3, keys: rs, name: '金花' };
  if (straight) return { rank: 2, keys: [sHigh], name: '顺子' };
  if (pair) {
    var pr = rs[0] === rs[1] ? rs[0] : rs[1];
    var kick = rs[0] === rs[1] ? rs[2] : rs[0];
    return { rank: 1, keys: [pr, kick], name: '对子' };
  }
  return { rank: 0, keys: rs, name: '高张' };
}
function __gfCompare(a, b) {
  var ea = __gfEval(a), eb = __gfEval(b);
  if (ea.rank !== eb.rank) return ea.rank - eb.rank;
  for (var i = 0; i < Math.max(ea.keys.length, eb.keys.length); i++) {
    var ka = ea.keys[i] || 0, kb = eb.keys[i] || 0;
    if (ka !== kb) return ka - kb;
  }
  return 0;
}
function __gfStrength(hand) {
  var e = __gfEval(hand);
  // 强度曲线（中位散牌 ~0.09、对子 0.33+、顺子 0.55、金花 0.62、顺金 0.85、豹子 0.95）
  // 旧公式散牌中位仅 0.078 且挤在 0.03~0.08，阈值形同虚设 → AI 首轮弃牌率畸高
  if (e.rank === 0) return 0.05 + (((e.keys[0] || 7) - 5) / 9) * 0.15; // 散牌 0.05~0.20
  if (e.rank === 1) return 0.30 + ((e.keys[0] || 7) / 14) * 0.18;     // 对子 0.33~0.48
  if (e.rank === 2) return 0.55;                                        // 顺子
  if (e.rank === 3) return 0.62;                                        // 金花
  if (e.rank === 4) return 0.85;                                        // 顺金
  return e.rank === 5.5 ? 0.90 : 0.95;                                  // 235 特杀 / 豹子
}
// AI 决策：call/raise/fold/peek（peek=这次先看牌再决定 → 返回 call 由调用方处理）
function __gfAI(strength, persona, toCall, canRaise, roll) {
  roll = roll === undefined ? Math.random() : roll;
  if (toCall <= 0) {
    if (canRaise && strength > 0.45 && roll < 0.5) return { type: 'raise' };
    return { type: 'call' };
  }
  if (persona === 'aggr') {
    if (strength < 0.09 && roll < 0.5) return { type: 'fold' };       // 只有真正烂牌才走
    if (canRaise && strength > 0.42 && roll < 0.4) return { type: 'raise' };
    return { type: 'call' };
  }
  if (persona === 'tight') {
    if (strength < 0.10 && roll < 0.75) return { type: 'fold' };
    if (strength < 0.065) return { type: 'fold' };
    if (canRaise && strength > 0.58 && roll < 0.3) return { type: 'raise' };
    return { type: 'call' };
  }
  // bluff
  if (strength < 0.19 && roll < 0.16 && canRaise) return { type: 'raise' };
  if (strength < 0.10 && roll < 0.5) return { type: 'fold' };
  if (canRaise && strength > 0.40 && roll < 0.3) return { type: 'raise' };
  return { type: 'call' };
}

var GF_ANTE = 10, GF_MAX_ROUNDS = 5;
var GF_DEAL_GAP = 16, GF_DEAL_FLIGHT = 12;
var GF_THINK = { aggr: [110, 220], tight: [200, 320], bluff: [140, 260] };
var GF_NAMES = ['老K', '阿豪', '薇薇', 'Momo', 'Jack', '强叔', 'Kiki', '小美', '阿杰', '苏珊', '刀仔', '老钱', 'Tony', '露露', '大飞', '娜娜', 'K哥', '阿灿', '莉莉', '肥猫'];
function __gfRand(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }
function __gfPickNames(n) {
  var pool = GF_NAMES.slice(), out = [];
  for (var i = 0; i < n && pool.length; i++) out.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
  return out;
}

// ---------- 炸金花桌 ----------
class CasinoGoldenflower {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.history = [];   // 战绩点 W/L
    this.dispPot = 0;
    this.banner = null;
    this.shake = null;
    this.flash = null;
    this._posCache = null;
    this.peek = false; this.peekT = 0;
    this.aiPeek = [null, null, null, null];
    this._nextIdlePeek = [0, 0, 0, 0];
    this._keyHdlr = this._onKey.bind(this);
    document.addEventListener('keydown', this._keyHdlr);
    this._buildDom(container);
    this._startHand();
  }
  _onKey(e) {
    var tag = (e.target && e.target.tagName) || '';
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (e.code === 'Space' || e.key === ' ') {
      e.preventDefault();
      if (this.destroyed || this.phase === 'deal') return;
      this.peek = !this.peek; this.peekT = this.tick;
      Casino.audio.play('card-flick', 0.5);
    }
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
    var helpBtn = this._el('button', 'padding:4px 12px;border-radius:6px;border:1px solid rgba(240,200,140,.4);background:rgba(10,5,3,.45);color:#e8c890;cursor:pointer;font-family:inherit;font-size:11px', '？牌型速查');
    helpBtn.onclick = function () { self.helpEl.style.display = self.helpEl.style.display === 'none' ? 'block' : 'none'; };
    bar.appendChild(helpBtn);
    var exitBtn = this._el('button', 'padding:4px 12px;border-radius:6px;border:1px solid rgba(240,120,100,.4);background:rgba(10,5,3,.45);color:#e0a090;cursor:pointer;font-family:inherit;font-size:11px', '← 离开');
    exitBtn.onclick = function () { self.destroy(); self.ctx.exit(); };
    bar.appendChild(exitBtn);
    this.root.appendChild(bar);
    this.helpEl = this._el('div', 'display:none;position:absolute;top:46px;left:10px;max-width:min(560px,86vw);padding:10px 14px;border:1px solid #5a3a1c;border-radius:8px;background:rgba(16,8,4,.93);font-size:12px;line-height:1.9;color:#d8c0a0;pointer-events:auto',
      '每人 3 张牌。牌型：<b style="color:#ffc87a">豹子</b>(三同) &gt; <b>顺金</b>(同花顺) &gt; <b>金花</b>(同花) &gt; <b>顺子</b> &gt; <b>对子</b> &gt; 高张；特例 <b style="color:#7ee8a0">2·3·5 杂色</b> 反杀豹子。<br>玩法：底注后轮流行动——<b>闷跟</b>(不看牌，半价) / <b>看牌</b>后跟注翻倍 / <b>加注</b>(底注翻倍) / <b>弃牌</b> / <b>比牌</b>(付跟注与一人比大小，输者离场)。剩一人或满 5 轮开牌。<br><b>空格</b>=翻看/盖回自己的牌。');
    this.root.appendChild(this.helpEl);
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:198px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px 12px;pointer-events:auto;max-width:94vw;box-sizing:border-box', '');
    this.root.appendChild(this.actEl);
    this.againEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);pointer-events:auto', '');
    this.root.appendChild(this.againEl);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }
  _taunt(seat) {
    var arr = { aggr: ['全压了！', '这点钱也敢跟？', '我牌好得很（也许）'], tight: ['风险太高', '这手不稳', '撤了撤了'], bluff: ['你猜？', '我在钓你', '信息不对称，朋友'] }[this.players[seat].persona];
    return arr[Math.floor(Math.random() * arr.length)];
  }
  _fxText(seat, text, color, big) { this.fx.push({ kind: 'text', at: 'seat' + seat, text: text, color: color || '#ffd98a', start: this.tick, dur: 46, big: !!big }); }
  _fxChipsToPot(seat, n) { this.fx.push({ kind: 'chip', from: 'seat' + seat, to: 'pot', start: this.tick, dur: 22, n: n }); this._potPopT = this.tick; }
  _fxChipsToSeat(seat, n, delay) { this.fx.push({ kind: 'chip', from: 'pot', to: 'seat' + seat, start: this.tick + (delay || 0), dur: 24, n: n }); }
  _fxShake(amp, dur) { this.shake = { amp: amp, start: this.tick, dur: dur }; }
  _fxFlash(color) { this.flash = { color: color, start: this.tick, dur: 16 }; }

  _startHand() {
    if (this.wallet.get() < GF_ANTE) {
      this._msg('算力不足（底注 ' + GF_ANTE + '）——去大厅领救济金');
      this.phase = 'broke';
      this._renderActions();
      this.againEl.innerHTML = '';
      return;
    }
    var deck = __gfShuffle(__gfNewDeck());
    this.players = [{ human: true, name: '你', folded: false, seen: false, hand: deck.splice(0, 3), paid: GF_ANTE }];
    var personas = ['aggr', 'tight', 'bluff'];
    var names = __gfPickNames(3);
    for (var i = 0; i < 3; i++) {
      if (this.aiChips === undefined) this.aiChips = [1000, 1000, 1000];
      if (this.aiChips[i] < GF_ANTE) this.aiChips[i] = 1000; // 重购
      this.aiChips[i] -= GF_ANTE;
      this.players.push({ human: false, persona: personas[i], name: names[i], chips: this.aiChips[i], folded: false, seen: false, hand: deck.splice(0, 3), paid: GF_ANTE });
    }
    this.wallet.sub(GF_ANTE);
    this.pot = GF_ANTE * 4;
    this.baseBet = GF_ANTE;   // 闷跟价
    this.round = 1;
    this.turn = 0;
    this.dealT = this.tick;
    this._dealt = false;
    this._dealSnd = 0;
    this.phase = 'bet';
    this.winnerSeat = undefined;
    this.peek = false; this.peekT = 0;
    this.fx = []; this.banner = null; this.shake = null; this.flash = null;
    this.dispPot = 0;
    this.aiPeek = [null, null, null, null];
    this._nextIdlePeek = [0, 0, 0, 0];
    this.lastActTick = this.tick + GF_DEAL_TICKS();
    this.leader = 0; // 本轮起点（转回即一轮结束）
    this._msg('发牌中…');
    for (var a = 0; a < 4; a++) this.fx.push({ kind: 'chip', from: 'seat' + a, to: 'pot', start: this.dealT + 26 + a * 12, dur: 20, n: GF_ANTE });
    this._renderActions();
  }

  _active() { return this.players.filter(function (p) { return !p.folded; }); }
  _callCost(p) { return p.seen ? this.baseBet * 2 : this.baseBet; }
  _canRaise() { return this.baseBet < 640; } // 封顶防无限翻

  _setThink(seat) {
    var p = this.players[seat];
    if (!p || p.human) { this.thinkUntil = this.tick + 80; return; }
    var range = GF_THINK[p.persona] || [150, 280];
    this.thinkUntil = this.tick + __gfRand(range[0], range[1]);
    if (!p.seen && Math.random() < 0.5) {
      var total = this.thinkUntil - this.tick;
      this.aiPeek[seat] = { start: Math.round(this.tick + Math.max(20, total * (0.2 + Math.random() * 0.4))), dur: __gfRand(45, 80), realLook: true };
    } else if (Math.random() < 0.4) {
      this.aiPeek[seat] = { start: this.tick + __gfRand(20, 80), dur: __gfRand(40, 70), realLook: false };
    }
  }
  _advanceTurn() {
    // 找下一个行动者；转回本轮起点（leader）即一轮结束
    for (var i = 1; i <= 4; i++) {
      var seat = (this.turn + i) % 4;
      if (this.players[seat].folded) continue;
      if (seat === this.leader) break; // 一圈了
      this.turn = seat; this.lastActTick = this.tick; this._setThink(seat);
      return;
    }
    // 一轮结束
    var alive = this._active();
    if (alive.length <= 1) return this._awardFoldWin(alive[0]);
    if (this.round >= GF_MAX_ROUNDS) return this._showdown();
    this.round++;
    this._msg('第 ' + this.round + '/' + GF_MAX_ROUNDS + ' 轮 · 底注 ' + this.baseBet);
    for (var k = 0; k < 4; k++) {
      if (!this.players[k].folded) {
        this.turn = k; this.leader = k; this.lastActTick = this.tick; this._setThink(k);
        return;
      }
    }
  }

  act(seat, action, target) {
    if (this.phase !== 'bet' || seat !== this.turn) return;
    var p = this.players[seat];
    var cost = this._callCost(p);
    if (action === 'fold') {
      p.folded = true;
      this._msg((p.human ? '你' : p.name) + ' 弃牌');
      this._fxText(seat, '弃牌', '#a08a6a');
      Casino.audio.play('voice-fold', 0.6);
    } else if (action === 'call') {
      var pay = p.human ? Math.min(cost, this.wallet.get()) : Math.min(cost, p.chips);
      if (p.human) { if (!this.wallet.sub(pay)) { this._msg('算力不足'); return; } }
      else { p.chips -= pay; this.aiChips[seat - 1] = p.chips; }
      this.pot += pay;
      this._msg((p.human ? '你' : p.name) + (p.seen ? '（明）' : '（闷）') + '跟注 ' + pay);
      this._fxChipsToPot(seat, pay);
      this._fxText(seat, (p.seen ? '跟 ' : '闷 ') + pay, p.seen ? '#8fce8f' : '#a0c8e8');
      Casino.audio.play('voice-call', 0.55);
      Casino.audio.play('coins', 0.35);
    } else if (action === 'raise') {
      this.baseBet *= 2;
      var cost2 = this._callCost(p);
      var pay2 = p.human ? cost2 : Math.min(cost2, p.chips);
      if (p.human) { if (!this.wallet.sub(pay2)) { this.baseBet /= 2; this._msg('算力不足'); return; } }
      else { p.chips -= pay2; this.aiChips[seat - 1] = p.chips; }
      this.pot += pay2;
      this._msg((p.human ? '你' : p.name) + ' 加注！底注 → ' + this.baseBet + (p.human ? '' : '：「' + this._taunt(seat) + '」'));
      this._fxChipsToPot(seat, pay2);
      this._fxText(seat, '加注！', '#ffc87a');
      Casino.audio.play('voice-raise', 0.6);
      Casino.audio.play('coins', 0.45);
    } else if (action === 'see') { // 看牌（不花钱、不交回合，看了之后跟注翻倍）
      if (p.seen) return;
      p.seen = true;
      if (p.human) { this.peek = true; this.peekT = this.tick; }
      this._msg((p.human ? '你' : p.name) + ' 看牌（跟注翻倍）');
      this._fxText(seat, '看牌', '#c0a8ff');
      Casino.audio.play('card-flick', 0.5);
      this._renderActions();
      return; // 不推进回合
    } else if (action === 'compare') {
      // 比牌：付一次跟注，与 target 比大小，输者立即弃牌
      var t = this.players[target];
      if (!t || t.folded || target === seat) return;
      var cPay = cost;
      if (p.human) { if (!this.wallet.sub(cPay)) { this._msg('算力不足'); return; } }
      else { p.chips -= cPay; this.aiChips[seat - 1] = p.chips; }
      this.pot += cPay;
      this._fxChipsToPot(seat, cPay);
      var cmp = __gfCompare(p.hand, t.hand);
      var loser = cmp >= 0 ? target : seat; // 平局按点数比，仍输给主动比牌方（从严）
      this.players[loser].folded = true;
      this._msg((seat === 0 ? '你' : this.players[seat].name) + ' 与 ' + (target === 0 ? '你' : t.name) + ' 比牌 · ' + (loser === 0 ? '你输了' : (loser === target ? t.name : this.players[seat].name) + ' 输') + '（' + __gfEval(cmp >= 0 ? p.hand : t.hand).name + '）');
      this._fxText(loser, '比牌 输', '#ff6a5a', true);
      this.fx.push({ kind: 'foldcard', at: 'seat' + loser, start: this.tick + 10, dur: 18 });
      Casino.audio.play('voice-compare-cards', 0.8);
      var alive2 = this._active();
      if (alive2.length <= 1) { this._advanceTurn(); return this._awardFoldWin(alive2[0]); }
    }
    this._advanceTurn();
    this._renderActions(this.phase === 'settle');
  }

  _awardFoldWin(winner) {
    this.phase = 'settle';
    this.winnerSeat = this.players.indexOf(winner);
    this.history.push(winner.human ? 'W' : 'L');
    if (this.history.length > 14) this.history.shift();
    var potNow = this.pot;
    if (winner.human) this.wallet.add(this.pot);
    else { winner.chips += this.pot; this.aiChips[this.winnerSeat - 1] = winner.chips; }
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, potNow / 3), 0);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, potNow / 3), 5);
    this.banner = { text: winner.human ? '你赢得底池 +' + potNow : winner.name + ' 收走底池 ' + potNow, color: winner.human ? '#ffd98a' : '#e08080', start: this.tick, dur: 90 };
    this._msg(winner.human ? '其他人全弃/比输，你收走底池 ' + potNow : winner.name + ' 收走底池 ' + potNow);
    this._fxShake(6, 12);
    Casino.audio.play(winner.human ? 'voice-win' : 'voice-lose', 0.8);
    this.pot = 0;
    this._renderActions(true);
    this._againBtn();
  }
  _showdown() {
    this.phase = 'reveal';
    var alive = this._active();
    var best = alive[0];
    for (var i = 1; i < alive.length; i++) if (__gfCompare(alive[i].hand, best.hand) > 0) best = alive[i];
    this._revealWinner = best;
    this.revealStart = this.tick;
    this._revealOrder = [0].concat(alive.filter(function (p) { return !p.human; }).map(function (p) { return this.indexOf(p); }, this.players));
    this._revealIdx = 0;
    this._saidCompare = false;
    this._revealDur = 36 + this._revealOrder.length * 85 + 50;
    this._msg('开牌！');
    Casino.audio.play('voice-open', 0.85);
  }
  _finishReveal() {
    var best = this._revealWinner;
    this.phase = 'settle';
    this.history.push(best.human ? 'W' : 'L');
    if (this.history.length > 14) this.history.shift();
    var potNow = this.pot;
    var ev = __gfEval(best.hand);
    if (best.human) {
      this.wallet.add(this.pot);
      this.banner = { text: '你赢得底池 +' + potNow, color: '#ffd98a', start: this.tick, dur: 100 };
      Casino.audio.play('voice-win', 0.9);
      this._msg('开牌：你的 ' + ev.name + ' 最大，赢得底池 ' + potNow + '！');
    } else {
      best.chips += this.pot; this.aiChips[this.players.indexOf(best) - 1] = best.chips;
      this.banner = { text: best.name + ' 以 ' + ev.name + ' 收走底池', color: '#e08080', start: this.tick, dur: 100 };
      Casino.audio.play('voice-lose', 0.8);
      this._msg('开牌：' + best.name + ' 以 ' + ev.name + ' 收走底池 ' + potNow);
    }
    this.winnerSeat = this.players.indexOf(best);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, potNow / 3), 0);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, potNow / 3), 5);
    this._fxShake(6, 14);
    this.pot = 0;
    this._renderActions(true);
    this._againBtn();
  }
  _againBtn() {
    var self = this;
    this.actEl.innerHTML = '';
    this.againEl.innerHTML = '';
    var b = this._el('button', 'padding:10px 30px;border-radius:8px;border:1px solid #ffc87a;background:rgba(50,28,10,.92);color:#ffc87a;cursor:pointer;font-family:inherit;font-size:14px;font-weight:700', '🔄 再来一局');
    b.onclick = function () { self.againEl.innerHTML = ''; self._startHand(); };
    this.againEl.appendChild(b);
  }

  _renderActions() {
    var self = this;
    if (this.phase === 'settle') { this.actEl.innerHTML = ''; return; }
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b> · 底池 <b>' + Math.round(this.dispPot) + '</b> · 底注 <b>' + this.baseBet + '</b></span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    if (this.phase !== 'bet' || this.players[0].folded || this.turn !== 0) {
      if (this.phase === 'bet' && this.players[0].folded) this.actEl.insertAdjacentHTML('beforeend', '<span style="font-size:12px;color:#a08a6a">你已弃牌，等待开牌…</span>');
      else if (this.phase === 'bet') this.actEl.insertAdjacentHTML('beforeend', '<span style="font-size:12px;color:#a08a6a">' + this.players[this.turn].name + ' 思考中…</span>');
      else if (!this._dealt) this.actEl.insertAdjacentHTML('beforeend', '<span style="font-size:12px;color:#a08a6a">发牌中…</span>');
      return;
    }
    if (!this._dealt) { this.actEl.insertAdjacentHTML('beforeend', '<span style="font-size:12px;color:#a08a6a">发牌中…</span>'); return; }
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 16px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    var me = this.players[0];
    var cost = this._callCost(me);
    this.actEl.appendChild(mk((me.seen ? '跟注 ' : '闷跟 ') + cost, function () { self.act(0, 'call'); }, me.seen ? '#8fce8f' : '#5fa8e0'));
    if (!me.seen) this.actEl.appendChild(mk('👁 看牌', function () { self.act(0, 'see'); }, '#b070e0'));
    if (this._canRaise()) this.actEl.appendChild(mk('加注 → ' + this.baseBet * 2, function () { self.act(0, 'raise'); }, '#ffc87a'));
    // 比牌对象（存活对手）
    this.players.forEach(function (p2, i2) {
      if (i2 > 0 && !p2.folded) {
        self.actEl.appendChild(mk('⚔ 比 ' + p2.name + ' (' + cost + ')', function () { self.act(0, 'compare', i2); }, '#e06060'));
      }
    });
    this.actEl.appendChild(mk('弃牌', function () { self.act(0, 'fold'); }, '#a08a6a'));
  }

  // ---------- 场景 ----------
  _dealHoleProg(seat, i) {
    if (this._dealt) return 1;
    var order = seat === 0 ? 3 : seat - 1;
    var nth = i * 4 + order;
    var t0 = this.dealT + 12 + nth * GF_DEAL_GAP;
    return Math.max(0, Math.min(1, (this.tick - t0) / GF_DEAL_FLIGHT));
  }
  _peekProg(i) {
    var dur = 9;
    if (this.peek) return Math.max(0, Math.min(1, (this.tick - this.peekT - i * 4) / dur));
    return Math.max(0, 1 - Math.max(0, Math.min(1, (this.tick - this.peekT - i * 4) / dur)));
  }
  _revealProg(seat, i) {
    if (seat === 0 || this.phase === 'settle') return 1;
    if (this.phase !== 'reveal') return 0;
    var oi = (this._revealOrder || []).indexOf(seat);
    if (oi < 0) return 1;
    return Math.max(0, Math.min(1, (this.tick - (this.revealStart + 36 + oi * 85 + i * 6)) / 10));
  }
  _pt(ref) {
    var pc = this._posCache || { seats: [[400, 560], [170, 250], [400, 225], [630, 250]], pot: [400, 400], deck: [400, 370] };
    if (ref === 'pot') return pc.pot;
    if (ref === 'deck') return pc.deck;
    if (ref && ref.indexOf('seat') === 0) return pc.seats[parseInt(ref.slice(4), 10)];
    return pc.pot;
  }

  renderScene(c, w, h, t) {
    if (this.destroyed || !this.players) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    var aiPos = [[w * 0.205, h * 0.415, s * 1.15], [w * 0.5, h * 0.375, s * 1.3], [w * 0.795, h * 0.415, s * 1.15]];
    this._posCache = {
      seats: [[w / 2, h * 0.94], aiPos[0], aiPos[1], aiPos[2]],
      pot: [w / 2, h * 0.68],
      deck: [w / 2, h * 0.56]
    };
    c.save();
    if (this.shake) {
      var sp = (this.tick - this.shake.start) / this.shake.dur;
      if (sp < 1) {
        var amp = this.shake.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      }
    }
    P.table(c, w, h);
    Casino.paint.histDots(c, w, h, this.history);
    var reveal = this.phase === 'settle';
    var colors = { aggr: '#e06040', tight: '#5fa8e0', bluff: '#b070e0', player: '#4ac070' };
    for (var i = 1; i <= 3; i++) {
      var p = this.players[i];
      var pos = aiPos[i - 1];
      var peekA = this.aiPeek[i];
      var leaning = false;
      if (peekA) {
        var pp = (this.tick - peekA.start) / peekA.dur;
        if (pp > 0 && pp < 1) leaning = true;
        else if (pp >= 1) { if (peekA.realLook) p.seen = true; this.aiPeek[i] = null; }
      }
      P.seat(c, pos[0], pos[1], t, {
        name: p.name + (p.seen ? ' ·明' : ' ·闷'), color: colors[p.persona], persona: p.persona, scale: pos[2],
        folded: p.folded, active: this.phase === 'bet' && this.turn === i && this._dealt,
        winner: reveal && this.winnerSeat === i, chipsLabel: '◈ ' + p.chips, lean: leaning
      });
      if (this.phase === 'bet' && this.turn === i && this._dealt) {
        var frac = Math.max(0, Math.min(1, (this.tick - this.lastActTick) / Math.max(1, this.thinkUntil - this.lastActTick)));
        if (frac > 0.02) {
          c.save();
          c.strokeStyle = 'rgba(255,200,120,.9)'; c.lineWidth = 3;
          c.shadowColor = '#ffc87a'; c.shadowBlur = 6;
          c.beginPath();
          c.ellipse(pos[0], pos[1] + 64 * pos[2], 48 * pos[2], 13 * pos[2], 0, -Math.PI / 2, -Math.PI / 2 + frac * Math.PI * 2);
          c.stroke();
          c.restore();
        }
      }
      if (!p.folded) this._holeFan(c, pos[0], h * 0.545, p.hand, i, s, leaning);
    }
    var showPot = Math.round(this.dispPot);
    if (showPot > 0) {
      var pop = this._potPopT !== undefined ? Math.max(0, 1 - (this.tick - this._potPopT) / 12) : 0;
      c.save();
      c.translate(w / 2, h * 0.68); c.scale(1 + 0.22 * pop, 1 + 0.22 * pop); c.translate(-w / 2, -h * 0.68);
      P.chips(c, w / 2, h * 0.68, showPot);
      c.restore();
      c.fillStyle = '#ffc87a';
      c.font = '700 ' + Math.round(13 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.shadowColor = '#000'; c.shadowBlur = 5;
      c.fillText('底池 ' + showPot, w / 2, h * 0.68 + 20 * s);
      c.shadowBlur = 0;
    }
    this._playerHand(c, w, h, s);
    this._drawFx(c, s);
    if (reveal && this.winnerSeat !== undefined) P.confetti(c, w, h, t);
    c.restore();
    this._drawBanner(c, w, h);
    this._drawFlash(c, w, h);
  }
  _holeFan(c, x, y, hand, seat, s, leaning) {
    var deck = this._pt('deck');
    var cw = 32 * s;
    c.save();
    c.translate(x, y);
    for (var i = 0; i < 3; i++) {
      var prog = this._dealHoleProg(seat, i);
      if (prog <= 0) continue;
      var cx = (i - 1) * cw * 1.0;
      var lift = leaning ? -16 * s : 0;
      var rot = leaning ? (i - 1) * 0.16 : 0;
      c.save();
      if (prog < 1) {
        c.translate((deck[0] - x) * (1 - prog) + cx * prog, (deck[1] - y) * (1 - prog));
        c.rotate((1 - prog) * 0.6);
        c.globalAlpha = 0.35 + 0.65 * prog;
        Casino.paint.card(c, 0, 0, cw, cw * 0.7, null, false);
      } else {
        c.translate(cx, lift);
        c.rotate(rot);
        var flip = this._revealProg(seat, i);
        var sx = 1 - Math.abs(1 - 2 * flip);
        if (sx > 0.05) Casino.paint.card(c, 0, 0, cw * Math.max(0.05, sx), cw * 0.7, flip >= 0.5 ? hand[i] : null, flip >= 0.5);
      }
      c.restore();
    }
    c.restore();
  }
  _playerHand(c, w, h, s) {
    var p = this.players[0];
    if (!p || !p.hand || this._dealHoleProg(0, 0) <= 0) return;
    var cw = Math.max(54, Math.min(96, w * 0.078)), chh = cw * 1.45;
    var cy = h - chh * 0.56;
    c.save();
    c.fillStyle = 'rgba(0,0,0,.5)';
    c.beginPath();
    c.ellipse(w / 2, cy + chh * 0.52, cw * 2.2, chh * 0.55, 0, 0, Math.PI * 2);
    c.fill();
    c.restore();
    var reveal = this.phase === 'settle';
    var win = reveal && this.winnerSeat === 0;
    var active = this.phase === 'bet' && this.turn === 0 && !p.folded;
    for (var i = 0; i < 3; i++) {
      var prog = this._dealHoleProg(0, i);
      if (prog <= 0) continue;
      var k = i - 1;
      var pk = this._peekProg(i);
      var spread = cw * (0.42 + 0.4 * pk);
      var cx = k * spread * prog;
      var rise = (1 - prog) * 70;
      var idle = this._dealt ? Math.sin(this.tick * 0.05 + i) * 3 : 0;
      c.save();
      c.translate(w / 2 + cx, cy + Math.abs(k) * chh * 0.06 + rise + idle);
      c.rotate(k * (0.05 + 0.09 * pk) * prog);
      if (p.folded) { c.globalAlpha = 0.55; Casino.paint.card(c, 0, 0, cw, chh, null, false); }
      else if (reveal || pk >= 1) this._bigCard(c, p.hand[i], cw, chh, active, win);
      else if (pk > 0) {
        var sx = 1 - Math.abs(1 - 2 * pk);
        if (sx > 0.05) Casino.paint.card(c, 0, 0, cw * Math.max(0.05, sx), chh, pk >= 0.5 ? p.hand[i] : null, pk >= 0.5);
      } else Casino.paint.card(c, 0, 0, cw, chh, null, false);
      c.restore();
    }
    var ev = __gfEval(p.hand);
    var label = p.folded ? '已弃牌'
      : reveal ? '你的手牌 · ' + ev.name
      : !this._dealt ? '发牌中…'
      : (this.peek || p.seen) ? '你的牌 · ' + ev.name + (p.seen ? '（明）' : '')
      : (p.seen ? '已看过（空格再看）' : '按 空格 看牌');
    c.save();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = '700 ' + Math.round(13 * s) + 'px monospace';
    c.fillStyle = win ? '#ffd98a' : '#ecd9b8';
    c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 5;
    c.fillText(label, w / 2, cy - chh * 0.74);
    c.restore();
  }
  _bigCard(c, card, cw, chh, active, win) {
    if (active) { c.shadowColor = '#ffc87a'; c.shadowBlur = 14; }
    if (win) { c.shadowColor = '#ffd98a'; c.shadowBlur = 20; }
    Casino.paint.card(c, 0, 0, cw, chh, card, true);
    c.shadowBlur = 0;
  }
  _drawFx(c, s) {
    if (!this.fx.length) return;
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'chip') {
        var from = self._pt(f.from), to = self._pt(f.to);
        var x = from[0] + (to[0] - from[0]) * p;
        var y = from[1] + (to[1] - from[1]) * p - Math.sin(Math.PI * p) * 46;
        Casino.paint.chips(c, x, y, Math.max(10, Math.round((f.n || 20) / 2)));
      } else if (f.kind === 'text') {
        var at = self._pt(f.at);
        c.save();
        c.globalAlpha = p < 0.75 ? 1 : (1 - p) / 0.25;
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.font = '700 ' + (f.big ? 26 : 14) + 'px monospace';
        c.fillStyle = f.color || '#ffd98a';
        c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 6;
        c.fillText(f.text, at[0], at[1] - 95 * s - p * 34);
        c.restore();
      } else if (f.kind === 'foldcard') {
        var at2 = self._pt(f.at), muck = self._pt('pot');
        c.save();
        c.globalAlpha = 1 - p * 0.6;
        c.translate(at2[0] + (muck[0] - at2[0]) * p, at2[1] + 30 + (muck[1] - at2[1]) * p);
        c.rotate(p * 1.2);
        Casino.paint.card(c, 0, 0, 34 * (s || 1), 24 * (s || 1), null, false);
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
  _drawFlash(c, w, h) {
    if (!this.flash) return;
    var p = (this.tick - this.flash.start) / this.flash.dur;
    if (p > 1) return;
    c.save();
    c.globalAlpha = (1 - p) * 0.30;
    c.fillStyle = this.flash.color;
    c.fillRect(0, 0, w, h);
    c.restore();
  }

  // ---------- 帧驱动 ----------
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.bot && this.phase === 'settle' && this.tick % 40 === 20) {
      this.againEl.innerHTML = '';
      this._startHand();
    }
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= this.shake.dur) this.shake = null;
    if (this.flash && this.tick - this.flash.start >= this.flash.dur) this.flash = null;
    if (typeof this.dispPot !== 'number') this.dispPot = this.pot || 0;
    if (this.dispPot < this.pot) this.dispPot = Math.min(this.pot, this.dispPot + Math.max(2, Math.round((this.pot - this.dispPot) * 0.3)));
    else if (this.dispPot > this.pot) this.dispPot = Math.max(this.pot, this.dispPot - Math.max(1, Math.round((this.dispPot - this.pot) * 0.2)));
    // 发牌
    if (this.phase === 'bet' && !this._dealt) {
      var landN = Math.floor((this.tick - this.dealT - 12 - GF_DEAL_FLIGHT) / GF_DEAL_GAP) + 1;
      while (this._dealSnd < Math.min(12, landN)) { Casino.audio.play('card-flick', 0.45); this._dealSnd++; }
      if (this.tick - this.dealT >= GF_DEAL_TICKS()) {
        this._dealt = true;
        this._msg('第 1/' + GF_MAX_ROUNDS + ' 轮 · 闷跟 ' + this.baseBet + ' / 看牌后 ' + this.baseBet * 2);
        this._renderActions();
      }
      return;
    }
    if (this.phase === 'reveal') {
      while (this._revealIdx < this._revealOrder.length &&
             this.tick - this.revealStart >= 36 + this._revealIdx * 85 + 26) {
        var st = this._revealOrder[this._revealIdx];
        var ev = __gfEval(this.players[st].hand);
        this.fx.push({ kind: 'text', at: 'seat' + st, text: (st === 0 ? '你' : this.players[st].name) + ' · ' + ev.name, color: st === 0 ? '#8fce8f' : '#ffd98a', start: this.tick, dur: 85, big: true });
        Casino.say(ev.name === '豹子' ? '豹子！' : ev.name, { pitch: 0.75, rate: 1.05 });
        Casino.audio.play('card-flick', 0.4);
        this._revealIdx++;
      }
      if (!this._saidCompare && this.tick - this.revealStart >= 36 + this._revealOrder.length * 85) {
        this._saidCompare = true;
        this._msg('比大小…');
        Casino.audio.play('voice-compare-cards', 0.8);
      }
      if (this.tick - this.revealStart >= this._revealDur) this._finishReveal();
      return;
    }
    if (this.phase !== 'bet') return;
    // AI 随机看牌动作
    for (var pi = 1; pi <= 3; pi++) {
      if (this.players[pi].folded) continue;
      if (!this._nextIdlePeek[pi]) this._nextIdlePeek[pi] = this.tick + __gfRand(260, 640);
      if (!this.aiPeek[pi] && this.tick >= this._nextIdlePeek[pi]) {
        this.aiPeek[pi] = { start: this.tick, dur: __gfRand(45, 80), realLook: this.players[pi].seen ? false : Math.random() < 0.35 };
        this._nextIdlePeek[pi] = this.tick + __gfRand(380, 900);
      }
    }
    var p = this.players[this.turn];
    if (!p || p.folded) { this._advanceTurn(); return; }
    if (p.human) {
      if (this.bot && this.tick - this.lastActTick >= 36) this.act(0, 'call');
      return;
    }
    if (this.tick < this.thinkUntil) return;
    var strength = __gfStrength(p.hand);
    var decision = __gfAI(p.seen ? strength : strength * 0.75, p.persona, this._callCost(p), this._canRaise());
    // AI 偶发比牌：剩 2 人且牌强
    var alive = this._active();
    if (alive.length === 2 && strength > 0.62 && Math.random() < 0.3) {
      var target = alive[0] === p ? this.players.indexOf(alive[1]) : this.players.indexOf(alive[0]);
      return this.act(this.turn, 'compare', target);
    }
    this.act(this.turn, decision.type);
  }

  destroy() {
    this.destroyed = true;
    document.removeEventListener('keydown', this._keyHdlr);
  }
}
function GF_DEAL_TICKS() { return 14 + 12 * GF_DEAL_GAP + GF_DEAL_FLIGHT + 14; }

Casino.register('goldenflower', {
  name: '炸金花',
  icon: '🂱',
  desc: '3 张牌 · 闷牌半价/看牌翻倍 · 加注/比牌/弃牌 · 235 杂色反杀豹子',
  create: function (container, ctx) { return new CasinoGoldenflower(container, ctx); }
});

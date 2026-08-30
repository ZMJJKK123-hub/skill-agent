// casino-holdem.js — 算力赌坊 · 德州扑克 Texas Hold'em
// 规则：每人 2 张底牌 + 桌面 5 张公共牌（翻牌圈 3 张 / 转牌 / 河牌逐街翻开）。
// 期前（第 1 轮）只能跟注/弃牌；翻牌后可 加注/加倍/全压/弃牌；最后 7 选 5 比大小。
// 交互：空格 翻看/盖回自己的手牌；AI 有 2~6 秒性格化思考与随机看牌动作。
// 所有动画按帧计数驱动（无 setTimeout 主逻辑），兼容 &step 自动化测试。

// ---------- 牌型引擎（纯函数，供测试） ----------
// 牌：{r: 2..14(A), s: 0..3}；cat: 8豹子 7同花顺 6金刚 5同花 4顺子 3三条 2两对 1对子 0散牌
var __thSuits = ['♠', '♥', '♣', '♦'];
var __thRed = [1, 3];

function __thNewDeck() {
  var d = [];
  for (var s = 0; s < 4; s++) for (var r = 2; r <= 14; r++) d.push({ r: r, s: s });
  return d;
}
function __thShuffle(d) {
  for (var i = d.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = d[i]; d[i] = d[j]; d[j] = t;
  }
  return d;
}
function __thEval(cards) { // 5 张评估
  var rs = cards.map(function (c) { return c.r; }).sort(function (a, b) { return b - a; });
  var flush = cards.every(function (c) { return c.s === cards[0].s; });
  var uniq = {};
  rs.forEach(function (r) { uniq[r] = (uniq[r] || 0) + 1; });
  var groups = Object.keys(uniq).map(Number).sort(function (a, b) {
    return uniq[b] - uniq[a] || b - a;
  });
  var straight = false, sKeys = null;
  if (groups.length === 5) {
    if (rs[0] - rs[4] === 4) { straight = true; sKeys = [rs[0]]; }
    else if (rs[0] === 14 && rs[1] === 5 && rs[4] === 2) { straight = true; sKeys = [5]; } // A2345 最小顺
  }
  if (groups.length === 1) return { cat: 8, keys: [rs[0]] };
  var c0 = uniq[groups[0]];
  if (c0 === 4) return { cat: 6, keys: groups };
  if (c0 === 3 && groups.length === 2) return { cat: 8, keys: groups }; // 葫芦
  if (flush && straight) return { cat: 7, keys: sKeys };
  if (flush) return { cat: 5, keys: rs };
  if (straight) return { cat: 4, keys: sKeys };
  if (c0 === 3) return { cat: 3, keys: groups };
  if (c0 === 2 && groups.length === 3) return { cat: 2, keys: groups };
  if (c0 === 2) return { cat: 1, keys: groups };
  return { cat: 0, keys: rs };
}
var __thCatName = ['散牌', '对子', '两对', '三条', '顺子', '同花', '金刚', '同花顺', '豹子'];
function __thCompare(a, b) {
  var ea = __thEval(a), eb = __thEval(b);
  if (ea.cat !== eb.cat) return ea.cat - eb.cat;
  for (var i = 0; i < Math.max(ea.keys.length, eb.keys.length); i++) {
    var ka = ea.keys[i] || 0, kb = eb.keys[i] || 0;
    if (ka !== kb) return ka - kb;
  }
  return 0;
}
// 7 选 5：预生成 21 个组合索引
var __TH_COMBOS = (function () {
  var idx = [];
  for (var a = 0; a < 3; a++) for (var b = a + 1; b < 4; b++) for (var c = b + 1; c < 5; c++)
    for (var d = c + 1; d < 6; d++) for (var e = d + 1; e < 7; e++) idx.push([a, b, c, d, e]);
  return idx;
})();
function __thBest(seven) { // 7 选 5 → {cat, keys, cards}
  var bestEv = null, bestCards = null;
  for (var i = 0; i < __TH_COMBOS.length; i++) {
    var combo = __TH_COMBOS[i].map(function (k) { return seven[k]; });
    var ev = __thEval(combo);
    if (!bestEv || __thCompare(combo, bestCards) > 0) { bestEv = ev; bestCards = combo; }
  }
  return { cat: bestEv.cat, keys: bestEv.keys, cards: bestCards };
}
// 任意 ≥5 张选最佳 5 张（翻牌圈 5 张 / 转牌 6 张 / 河牌 7 张通用）
function __thBestAny(cards) {
  if (cards.length === 5) { var e5 = __thEval(cards); return { cat: e5.cat, keys: e5.keys, cards: cards }; }
  if (cards.length > 5 && cards.length < 7) {
    var bestE = null, bestC = null;
    for (var drop = 0; drop < cards.length; drop++) {
      var five = cards.slice(); five.splice(drop, 1);
      var ev = __thEval(five);
      if (!bestE || __thCompare(five, bestC) > 0) { bestE = ev; bestC = five; }
    }
    return { cat: bestE.cat, keys: bestE.keys, cards: bestC };
  }
  return __thBest(cards);
}
// AI 强度：期前看底牌质量（分布上移，期前弃牌率贴近真实 15~35%）；翻牌后看当前成牌
function __thStrength(hole, comm) {
  if (!comm || comm.length < 3) {
    var r1 = hole[0].r, r2 = hole[1].r, hi = Math.max(r1, r2), lo = Math.min(r1, r2);
    if (r1 === r2) return Math.min(1, 0.55 + (r1 - 2) / 28);         // 对子
    var s = 0.2 + (hi - 2) / 24 * 0.4 + (lo - 2) / 12 * 0.12;       // 两张都有价值
    if (hi - lo === 1) s += 0.06;                                    // 连张
    if (hi >= 12 && lo >= 10) s += 0.12;                             // 双高张
    if (hole[0].s === hole[1].s) s += 0.04;                          // 同花色
    return Math.min(0.85, s);
  }
  var b = __thBestAny(hole.concat(comm));
  // 成牌强度曲线：散牌 0.10+、对子 0.34+、两对 0.60+、三条 0.72+、顺子 0.80+、同花 0.86+…
  // （旧公式一对仅 ~0.12，阈值全落弃牌区 → 翻牌后 AI 六成弃牌、桌面毫无对抗）
  var base = [0.10, 0.34, 0.60, 0.72, 0.80, 0.86, 0.93, 0.97, 1.0][b.cat];
  var span = [0.14, 0.16, 0.08, 0.06, 0.04, 0.04, 0.03, 0.02, 0.0][b.cat];
  var kick = (((b.keys && b.keys[0]) || 7) - 2) / 12; // 0..1（主关键张相对高度）
  return Math.min(1, base + kick * span);
}

// ---------- AI 决策（纯函数，供测试） ----------
// persona: aggr | tight | bluff；期前（canRaise/canAllin 均为 false）只能跟/弃且弃牌更克制
function __thAI(strength, persona, toCall, canRaise, canAllin, roll) {
  roll = roll === undefined ? Math.random() : roll;
  if (toCall <= 0) {
    if (canRaise && strength > 0.45 && roll < 0.6) return { type: 'raise' };
    return { type: 'call' };
  }
  if (!canRaise && !canAllin) { // 期前：只能跟注或弃牌（弃牌率 ~15%/人）
    if (persona === 'tight') { if (strength < 0.38 && roll < 0.6) return { type: 'fold' }; return { type: 'call' }; }
    if (persona === 'bluff') { if (strength < 0.3 && roll < 0.5) return { type: 'fold' }; return { type: 'call' }; }
    if (strength < 0.25 && roll < 0.4) return { type: 'fold' };
    return { type: 'call' };
  }
  if (persona === 'aggr') {
    if (strength < 0.16 && roll < 0.5) return { type: 'fold' };
    if (canRaise && strength > 0.45 && roll < 0.5) return { type: roll < 0.15 ? 'double' : 'raise' };
    if (canAllin && strength > 0.75 && roll < 0.22) return { type: 'allin' };
    return { type: 'call' };
  }
  if (persona === 'tight') {
    if (strength < 0.3 && roll < 0.85) return { type: 'fold' };
    if (strength < 0.22) return { type: 'fold' };
    if (canRaise && strength > 0.68 && roll < 0.4) return { type: 'raise' };
    return { type: 'call' };
  }
  // bluff：弱牌偶尔装强，强牌慢打
  if (strength < 0.2 && roll < 0.2 && canRaise) return { type: 'raise' };
  if (strength < 0.28 && roll < 0.55) return { type: 'fold' };
  if (canAllin && strength > 0.8 && roll < 0.15) return { type: 'allin' };
  if (canRaise && strength > 0.58 && roll < 0.38) return { type: roll < 0.3 ? 'double' : 'raise' };
  return { type: 'call' };
}
var __thTaunts = {
  aggr: ['这把我梭了！', '内存就是拿来烧的', 'raise or die', '这点注码也想吓我？'],
  tight: ['风险太高，撤', '我先做下边界检查', '这手牌 stack 不稳', '保守是一种美德'],
  bluff: ['你猜我有没有？', '编译错误也是特性', '我在钓你，真的', '信息不对称，朋友']
};

// ---------- 常量 ----------
var TH_ANTE = 10, TH_PFR = 20, TH_RAISE = 50, TH_BOT_TICKS = 40;
// 发牌节奏（帧，60fps ≈ 每张 0.37s，一张一张绕桌背面发）
var TH_DEAL_GAP = 22, TH_DEAL_FLIGHT = 16;
var TH_HOLE_TICKS = 14 + 8 * TH_DEAL_GAP + TH_DEAL_FLIGHT + 16;     // 8 张底牌
var TH_COMM_TICKS = 14 + 5 * TH_DEAL_GAP + TH_DEAL_FLIGHT + 16;     // 5 张公共牌盖上
var TH_DEAL_TICKS = TH_HOLE_TICKS + 24 + TH_COMM_TICKS + 16;
var TH_FLIP_DUR = 10, TH_FLIP_CARD_STEP = 9, TH_FLIP_TAIL = 30;
// AI 思考时长（帧）：性格随机范围 2.2~6s——激进快、保守慢
var TH_THINK = { aggr: [130, 240], tight: [240, 360], bluff: [160, 300] };
var TH_STREET_NAMES = ['期前', '翻牌圈', '转牌圈', '河牌圈'];
var TH_NAMES = ['老K', '阿豪', '薇薇', 'Momo', 'Jack', '强叔', 'Kiki', '小美', '阿杰', '苏珊', '刀仔', '老钱', 'Tony', '露露', '大飞', '娜娜', 'K哥', '阿灿', '莉莉', '肥猫'];

function __thRand(a, b) { return a + Math.floor(Math.random() * (b - a + 1)); }
function __thPickNames(n) {
  var pool = TH_NAMES.slice();
  var out = [];
  for (var i = 0; i < n && pool.length; i++) out.push(pool.splice(Math.floor(Math.random() * pool.length), 1)[0]);
  return out;
}

// ---------- 德州扑克桌 ----------
class CasinoHoldem {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.phase = 'deal'; // deal → bet(×4街) → flip(翻公共牌) → reveal → settle
    this.destroyed = false;
    this.aiChips = [1000, 1000, 1000];
    this.fx = [];
    this.history = [];   // 战绩点 W/L
    this.dispPot = 0;
    this.banner = null;
    this.shake = null;
    this.flash = null;
    this._posCache = null;
    this.peek = false;        // 玩家是否翻看手牌（空格切换）
    this.peekT = 0;           // 最近一次切换的帧
    this.aiPeek = [null, null, null, null]; // {start, dur} AI 看牌动作
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
      this.peek = !this.peek;
      this.peekT = this.tick;
      Casino.audio.play('card-flick', 0.5);
    }
  }

  // ---------- DOM ----------
  _el(tag, css, html) {
    var e = document.createElement(tag);
    if (css) e.style.cssText = css;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  _buildDom(container) {
    var self = this;
    // 全屏浮层：场景全由 canvas 绘制；顶栏只留 速查+离开（无底框）
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
      '每人 2 张底牌 + 桌面 5 张公共牌，最终 7 选 5 组成最大牌型。<br>流程：期前（只能跟/弃）→ 翻牌圈 3 张 → 转牌 1 张 → 河牌 1 张 → 摊牌比大小。<br>牌型从大到小：<b style="color:#ffc87a">豹子</b>(葫芦) &gt; <b>同花顺</b> &gt; <b>金刚</b> &gt; <b>同花</b> &gt; <b>顺子</b> &gt; <b>三条</b> &gt; <b>两对</b> &gt; <b>对子</b> &gt; 散牌<br>操作：<b>空格</b>=翻看/盖回手牌 · <b>跟注</b> · <b>加注 +' + TH_RAISE + '</b> · <b>加倍 ×2</b> · <b>全压</b>(期前不可) · <b>弃牌</b>');
    this.root.appendChild(this.helpEl);
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:198px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    this.handEl = this._el('div', 'display:none', '');
    this.root.appendChild(this.handEl);
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px 12px;pointer-events:auto;max-width:94vw;box-sizing:border-box', '');
    this.root.appendChild(this.actEl);
    this.againEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);pointer-events:auto', '');
    this.root.appendChild(this.againEl);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }
  _taunt(seat) {
    var arr = __thTaunts[this.players[seat].persona];
    return arr[Math.floor(Math.random() * arr.length)];
  }

  // ---------- 牌局 ----------
  _startHand() {
    if (this.wallet.get() < TH_ANTE) {
      this._msg('算力不足以下注（底注 ' + TH_ANTE + '）——去大厅领救济金吧');
      this.phase = 'broke';
      this._renderAll();
      this.againEl.innerHTML = '';
      return;
    }
    var deck = __thShuffle(__thNewDeck());
    // AI 破产重购：筹码不够底注就重新买入 1000（朋友局规矩，游戏不中断）
    for (var rb = 0; rb < 3; rb++) {
      if (this.aiChips[rb] < TH_ANTE) {
        this.aiChips[rb] = 1000;
        this.fx.push({ kind: 'text', at: 'seat' + (rb + 1), text: '重新买入 1000', color: '#8fce8f', start: this.tick + 30, dur: 60 });
      }
    }
    this.players = [];
    this.players.push({ human: true, name: '你', chips: -1, folded: false, allIn: false, bet: 0, hand: deck.splice(0, 2) });
    var personas = ['aggr', 'tight', 'bluff'];
    var names = __thPickNames(3);
    for (var i = 0; i < 3; i++) {
      this.players.push({ human: false, persona: personas[i], name: names[i], chips: this.aiChips[i], folded: false, allIn: false, bet: 0, hand: deck.splice(0, 2) });
    }
    this.comm = deck.splice(0, 5); // 5 张公共牌（先盖上）
    this.commUp = 0;
    this.wallet.sub(TH_ANTE);
    this.pot = TH_ANTE * 4;
    for (var j = 1; j < 4; j++) this.aiChips[j - 1] -= TH_ANTE;
    this.players.forEach(function (p) { p.bet = TH_ANTE; });
    this.street = 0;
    this.currentBet = TH_PFR;
    this.allInMode = false;
    this.turn = 0;
    this.dealT = this.tick;
    this._dealt = false;
    this._dealSnd = 0;
    this.phase = 'deal';
    this.winnerSeat = undefined;
    this.peek = false;
    this.fx = []; this.banner = null; this.shake = null; this.flash = null;
    this.dispPot = 0;
    this.aiPeek = [null, null, null, null];
    this._nextIdlePeek = [0, 0, 0, 0];
    this._msg('发牌中…');
    Casino.audio.play('card-shuffle', 0.7);
    for (var a = 0; a < 4; a++) {
      this.fx.push({ kind: 'chip', from: 'seat' + a, to: 'pot', start: this.dealT + 30 + a * 16, dur: 22, n: TH_ANTE });
    }
    this._renderAll();
  }

  _active() { return this.players.filter(function (p) { return !p.folded; }); }
  _pending(p) { return !p.folded && !p.allIn && p.bet < this.currentBet; }
  _anyCanRaise() {
    var self = this;
    return this._active().some(function (p) { return !p.allIn && (p.human ? self.wallet.get() : p.chips) >= self.currentBet + TH_RAISE; });
  }

  _beginStreet(s) {
    this.street = s;
    this.phase = 'bet';
    this.currentBet = Math.max(this.currentBet, TH_PFR);
    if (s > 0) this.players.forEach(function (p) { p.bet = 0; });
    this.currentBet = TH_PFR;
    this._msg(TH_STREET_NAMES[s] + '下注 · 跟注 ' + TH_PFR);
    this.lastActTick = this.tick;
    for (var k = 0; k < 4; k++) {
      if (!this.players[k].folded && !this.players[k].allIn) { this.turn = k; break; }
    }
    this._setThink(this.turn);
    this._renderAll();
  }
  _setThink(seat) {
    var p = this.players[seat];
    if (!p || p.human) { this.thinkUntil = this.tick + 90; return; }
    var range = TH_THINK[p.persona] || [150, 300];
    this.thinkUntil = this.tick + __thRand(range[0], range[1]);
    // 思考途中随机看一眼牌（约 55%）
    if (Math.random() < 0.55) {
      var total = this.thinkUntil - this.tick;
      var at = this.tick + Math.max(20, total * (0.15 + Math.random() * 0.5));
      this.aiPeek[seat] = { start: Math.round(at), dur: __thRand(45, 85) };
    }
  }

  // 当前该谁行动；全部跟齐 → 结束本街
  _advanceTurn() {
    for (var i = 1; i <= 4; i++) {
      var seat = (this.turn + i) % 4;
      if (this._pending(this.players[seat])) {
        this.turn = seat; this.lastActTick = this.tick; this._setThink(seat);
        return;
      }
    }
    var alive = this._active();
    if (alive.length <= 1) { this._awardFoldWin(alive[0]); return; }
    this._endStreet();
  }
  _endStreet() {
    if (this.allInMode) {
      if (this.commUp < 5) return this._flipComm(this.commUp === 0 ? 3 : this.commUp + 1, true);
      return this._showdown();
    }
    if (this.street >= 3) return this._showdown();
    var target = this.street === 0 ? 3 : this.street + 3; // 翻牌圈一次翻 3 张；转/河各 1 张
    this._flipComm(target, false);
  }
  _flipComm(target, runout) {
    this.phase = 'flip';
    this.flipStart = this.tick;
    this.flipFrom = this.commUp;
    this.flipTarget = target;
    this.flipUntil = this.tick + (target - this.commUp) * TH_FLIP_CARD_STEP + TH_FLIP_DUR + TH_FLIP_TAIL;
    this._msg(runout ? '全压！剩余公共牌逐张翻开…' : (target === 3 ? '翻牌圈！' : target === 4 ? '转牌！' : '河牌！'));
    this._flipSnd = 0;
  }

  // 玩家/AI 通用行动入口
  act(seat, action, amt) {
    if (this.phase !== 'bet' || seat !== this.turn) return;
    var p = this.players[seat];
    var toCall = this.currentBet - p.bet;
    if (action === 'fold') {
      p.folded = true;
      this._msg((p.human ? '你' : p.name) + ' 弃牌');
      this._fxText(seat, '弃牌', '#a08a6a');
      this.fx.push({ kind: 'foldcard', at: 'seat' + seat, start: this.tick, dur: 18 });
      Casino.audio.play('voice-fold', 0.6);
    } else if (action === 'call') {
      var pay = p.human ? Math.min(toCall, this.wallet.get()) : Math.min(toCall, p.chips);
      if (p.human) {
        if (!this.wallet.sub(pay)) { this._msg('算力不足'); return; }
      } else {
        p.chips -= pay; this.aiChips[seat - 1] = p.chips;
      }
      p.bet += pay;
      if (pay < toCall) p.allIn = true;
      this.pot += pay;
      this._msg((p.human ? '你' : p.name) + ' 跟注 ' + pay);
      this._fxChipsToPot(seat, pay);
      this._fxText(seat, '跟注 ' + pay, '#8fce8f');
      Casino.audio.play('voice-call', 0.6);
      Casino.audio.play('coins', 0.4);
    } else if (action === 'raise' || action === 'double') {
      var need = action === 'double' ? (this.currentBet * 2 - p.bet) : (toCall + TH_RAISE);
      var bank = p.human ? this.wallet.get() : p.chips;
      if (bank < need) { return this.act(seat, 'call'); }
      if (p.human) this.wallet.sub(need); else { p.chips -= need; this.aiChips[seat - 1] = p.chips; }
      p.bet += need;
      this.pot += need;
      this.currentBet = p.bet;
      var verb = action === 'double' ? '加倍到' : '加注到';
      this._msg((p.human ? '你' : p.name) + ' ' + verb + ' ' + this.currentBet + (p.human ? '' : '：「' + this._taunt(seat) + '」'));
      this._fxChipsToPot(seat, need);
      this._fxText(seat, action === 'double' ? '加倍 ×2！' : '加注！', '#ffc87a');
      Casino.audio.play(action === 'double' ? 'voice-double' : 'voice-raise', 0.6);
      Casino.audio.play('coins', 0.4);
    } else if (action === 'allin') {
      if (this.street === 0) return; // 期前不允许全压
      var all = p.human ? this.wallet.get() : p.chips;
      if (p.human) this.wallet.sub(all); else { p.chips = 0; this.aiChips[seat - 1] = 0; }
      p.bet += all;
      this.pot += all;
      if (p.bet > this.currentBet) this.currentBet = p.bet;
      p.allIn = true;
      this.allInMode = true;
      this._msg((p.human ? '你' : p.name) + ' 全压 ' + all + (p.human ? '' : '：「' + this._taunt(seat) + '」'));
      this._fxChipsToPot(seat, all);
      this._fxText(seat, 'ALL IN！', '#ff6a5a', true);
      this.banner = { text: 'ALL IN · 全压 ' + all, color: '#ff8a70', start: this.tick, dur: 70 };
      this._fxShake(10, 16);
      this._fxFlash('#ff3018');
      Casino.audio.play('voice-allin', 0.9);
    }
    this._advanceTurn();
    this._renderAll(this.phase === 'settle');
  }

  _awardFoldWin(winner) {
    this.phase = 'settle';
    this.winnerSeat = this.players.indexOf(winner);
    this.history.push(winner.human ? 'W' : 'L');
    if (this.history.length > 14) this.history.shift();
    var potNow = this.pot;
    if (winner.human) {
      this.wallet.add(this.pot);
      this._msg('其他玩家全部弃牌，你直接赢得底池 ' + this.pot + '！');
    } else {
      this._msg('其他玩家全部弃牌，' + winner.name + ' 收走底池 ' + this.pot);
      winner.chips += this.pot; this.aiChips[this.players.indexOf(winner) - 1] = winner.chips;
    }
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 0);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 5);
    this.banner = {
      text: winner.human ? '你赢得底池 +' + potNow : winner.name + ' 收走底池 ' + potNow,
      color: winner.human ? '#ffd98a' : '#e08080', start: this.tick, dur: 90
    };
    this._fxShake(6, 12);
    Casino.audio.play(winner.human ? 'voice-win' : 'voice-lose', 0.8);
    this.pot = 0;
    this._renderAll(true);
    this._againBtn();
  }

  // 摊牌：你先亮，对手一家一家翻底牌、报牌型，全部亮完"比大小"再结算
  _showdown() {
    this.phase = 'reveal';
    var alive = this._active();
    var best = alive[0], bestEv = __thBestAny(alive[0].hand.concat(this.comm));
    for (var i = 1; i < alive.length; i++) {
      var ev = __thBestAny(alive[i].hand.concat(this.comm));
      if (__thCompare(ev.cards, bestEv.cards) > 0) { best = alive[i]; bestEv = ev; }
    }
    this._revealWinner = best;
    this.revealStart = this.tick;
    this._revealOrder = [0].concat(alive.filter(function (p) { return !p.human; }).map(function (p) { return this.indexOf(p); }, this.players));
    this._revealIdx = 0;
    this._saidCompare = false;
    this._revealDur = 40 + this._revealOrder.length * 95 + 55;
    this._msg('摊牌！');
    Casino.audio.play('voice-showdown', 0.8);
  }
  _finishReveal() {
    var best = this._revealWinner;
    this.phase = 'settle';
    this.history.push(best.human ? 'W' : 'L');
    if (this.history.length > 14) this.history.shift();
    var potNow = this.pot;
    var cat = __thCatName[__thBestAny(best.hand.concat(this.comm)).cat];
    if (best.human) {
      this.wallet.add(this.pot);
      this._msg('摊牌：你的 ' + cat + ' 最大，赢得底池 ' + this.pot + '！');
      this.banner = { text: '你赢得底池 +' + potNow, color: '#ffd98a', start: this.tick, dur: 100 };
      Casino.audio.play('voice-win', 0.9);
    } else {
      this._msg('摊牌：' + best.name + ' 以 ' + cat + ' 收走底池 ' + this.pot);
      this.banner = { text: best.name + ' 以 ' + cat + ' 收走底池', color: '#e08080', start: this.tick, dur: 100 };
      Casino.audio.play('voice-lose', 0.8);
    }
    this.winnerSeat = this.players.indexOf(best);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 0);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 5);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 10);
    this._fxShake(6, 14);
    this.pot = 0;
    this._renderAll(true);
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

  // ---------- 特效派生 ----------
  _fxText(seat, text, color, big) {
    this.fx.push({ kind: 'text', at: 'seat' + seat, text: text, color: color, start: this.tick, dur: 46, big: !!big });
  }
  _fxChipsToPot(seat, n) {
    this.fx.push({ kind: 'chip', from: 'seat' + seat, to: 'pot', start: this.tick, dur: 22, n: n });
    this._potPopT = this.tick;
  }
  _fxChipsToSeat(seat, n, delay) {
    this.fx.push({ kind: 'chip', from: 'pot', to: 'seat' + seat, start: this.tick + (delay || 0), dur: 24, n: n });
  }
  _fxShake(amp, dur) { this.shake = { amp: amp, start: this.tick, dur: dur }; }
  _fxFlash(color) { this.flash = { color: color, start: this.tick, dur: 16 }; }

  // ---------- 渲染 ----------
  _renderAll(reveal) {
    if (this.destroyed) return;
    this._renderActions();
  }
  _renderActions() {
    var self = this;
    if (this.phase === 'settle') { this.actEl.innerHTML = ''; return; }
    // 信息位：算力/底池 与按钮同排（左侧）
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b> · 底池 <b>' + Math.round(this.dispPot) + '</b></span>';
    if (this.phase !== 'bet') { this.actEl.innerHTML = info; return; }
    if (this.players[0].folded) {
      this.actEl.innerHTML = info + '<span style="font-size:12px;color:#a08a6a">你已弃牌，等待其他玩家…</span>';
      return;
    }
    if (this.turn !== 0) {
      this.actEl.innerHTML = info + '<span style="font-size:12px;color:#a08a6a">' + this.players[this.turn].name + ' 思考中…</span>';
      return;
    }
    if (!this._dealt) {
      this.actEl.innerHTML = info + '<span style="font-size:12px;color:#a08a6a">发牌中…</span>';
      return;
    }
    var toCall = this.currentBet - this.players[0].bet;
    var mk = function (label, action, cls) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = function () { self.act(0, action); };
      return b;
    };
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    this.actEl.appendChild(mk(toCall > 0 ? '跟注 ' + Math.min(toCall, this.wallet.get()) : '过牌', 'call', '#8fce8f'));
    if (this.street > 0) {
      if (!this.allInMode && this._anyCanRaise()) {
        this.actEl.appendChild(mk('加注 +' + TH_RAISE, 'raise', '#ffc87a'));
        var dblNeed = this.currentBet * 2 - this.players[0].bet;
        if (this.wallet.get() >= dblNeed) this.actEl.appendChild(mk('加倍 ×2 → ' + this.currentBet * 2, 'double', '#ff9f5a'));
      }
      if (!this.allInMode && this.wallet.get() > 0) this.actEl.appendChild(mk('全压 ' + this.wallet.get(), 'allin', '#e06060'));
    }
    this.actEl.appendChild(mk('弃牌', 'fold', '#a08a6a'));
  }

  // ---------- 场景渲染（大厅 canvas 每帧调用） ----------
  // 底牌发牌进度（绕桌一张张：每张 → 对手1→2→3→你）
  _dealHoleProg(seat, cardIdx) {
    if (this._dealt) return 1;
    var order = seat === 0 ? 3 : seat - 1;
    var nth = cardIdx * 4 + order;
    var t0 = this.dealT + 14 + nth * TH_DEAL_GAP;
    return Math.max(0, Math.min(1, (this.tick - t0) / TH_DEAL_FLIGHT));
  }
  // 公共牌发牌进度（底牌发完后 5 张依次盖上）
  _dealCommProg(i) {
    if (this._dealt) return 1;
    var base = TH_HOLE_TICKS + 24;
    var t0 = this.dealT + base + 14 + i * TH_DEAL_GAP;
    return Math.max(0, Math.min(1, (this.tick - t0) / TH_DEAL_FLIGHT));
  }
  // 玩家看牌翻面进度（0 背面 → 1 正面）
  _peekProg(i) {
    var dur = 9;
    if (this.peek) return Math.max(0, Math.min(1, (this.tick - this.peekT - i * 4) / dur));
    return Math.max(0, 1 - Math.max(0, Math.min(1, (this.tick - this.peekT - i * 4) / dur)));
  }
  // 公共牌翻面进度（0 背面 → 1 正面）
  _commFlipProg(i) {
    if (i < this.commUp) return 1;
    if (this.phase !== 'flip' || i >= this.flipTarget) return 0;
    var t0 = this.flipStart + (i - this.flipFrom) * TH_FLIP_CARD_STEP;
    return Math.max(0, Math.min(1, (this.tick - t0) / TH_FLIP_DUR));
  }
  // 摊牌翻底牌进度
  _revealProg(seat, cardIdx) {
    if (seat === 0 || this.phase === 'settle') return 1;
    if (this.phase !== 'reveal') return 0;
    var oi = (this._revealOrder || []).indexOf(seat);
    if (oi < 0) return 1;
    var t0 = this.revealStart + 40 + oi * 95 + cardIdx * 6;
    return Math.max(0, Math.min(1, (this.tick - t0) / TH_FLIP_DUR));
  }
  _pt(ref) {
    var pc = this._posCache || { seats: [[400, 560], [170, 250], [400, 225], [630, 250]], pot: [400, 400], deck: [400, 380] };
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
      pot: [w / 2, h * 0.755],
      deck: [w / 2, h * 0.62]
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
    // 三个对手（含思考倒计时环与看牌前倾）
    for (var i = 1; i <= 3; i++) {
      var p = this.players[i];
      var pos = aiPos[i - 1];
      var peekA = this.aiPeek[i];
      var leaning = false;
      if (peekA) {
        var pp = (this.tick - peekA.start) / peekA.dur;
        if (pp > 0 && pp < 1) leaning = true;
        else if (pp >= 1) this.aiPeek[i] = null;
      }
      P.seat(c, pos[0], pos[1], t, {
        name: p.name, color: colors[p.persona], persona: p.persona, scale: pos[2],
        folded: p.folded, active: this.phase === 'bet' && this.turn === i && this._dealt,
        winner: reveal && this.winnerSeat === i, chipsLabel: '◈ ' + p.chips, lean: leaning
      });
      if (this.phase === 'bet' && this.turn === i && this._dealt && !p.human && this.thinkUntil > this.lastActTick) {
        var frac = Math.max(0, Math.min(1, (this.tick - this.lastActTick) / (this.thinkUntil - this.lastActTick)));
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
      // 底牌（2 张）：发牌飞行 → 摊牌一家家翻
      if (!p.folded) this._holeFan(c, pos[0], h * 0.545, p.hand, i, s, leaning);
      if (!p.folded && this.phase === 'bet' && this._dealt && p.bet > TH_ANTE) P.chips(c, pos[0] + 62 * s, h * 0.60, p.bet);
    }
    // 公共牌（5 张）：发牌时逐张盖上，之后逐街翻开
    this._commRow(c, w, h, s);
    // 底池
    var showPot = Math.round(this.dispPot);
    if (showPot > 0) {
      var pop = this._potPopT !== undefined ? Math.max(0, 1 - (this.tick - this._potPopT) / 12) : 0;
      var scl = 1 + 0.22 * pop;
      c.save();
      c.translate(w / 2, h * 0.755); c.scale(scl, scl); c.translate(-w / 2, -h * 0.755);
      P.chips(c, w / 2, h * 0.755, showPot);
      c.restore();
      c.fillStyle = '#ffc87a';
      c.font = '700 ' + Math.round(13 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.shadowColor = '#000'; c.shadowBlur = 5;
      c.fillText('底池 ' + showPot, w / 2, h * 0.755 + 20 * s);
      c.shadowBlur = 0;
    }
    // 你的底牌（空格翻看）
    this._playerHand(c, w, h, s);
    this._drawFx(c, s);
    if (reveal && this.winnerSeat !== undefined) P.confetti(c, w, h, t);
    c.restore();
    this._drawBanner(c, w, h);
    this._drawFlash(c, w, h);
  }

  _commRow(c, w, h, s) {
    if (!this.comm) return;
    var cw = 34 * s, chh = 24 * s;
    var y = h * 0.625;
    var startX = w / 2 - 2 * cw * 1.18;
    var deck = this._pt('deck');
    for (var i = 0; i < 5; i++) {
      var prog = this._dealCommProg(i);
      if (prog <= 0) continue;
      var x = startX + i * cw * 1.18;
      var flip = this._commFlipProg(i);
      c.save();
      if (prog < 1) {
        c.translate((deck[0] - x) * (1 - prog) + x, (deck[1] - y) * (1 - prog) + y);
        c.rotate((1 - prog) * 0.5);
        c.globalAlpha = 0.35 + 0.65 * prog;
        this._miniCard(c, 0, 0, false, s);
      } else {
        c.translate(x, y);
        var sx = 1 - Math.abs(1 - 2 * flip);
        if (sx > 0.05) {
          c.scale(Math.max(0.05, sx), 1);
          this._miniCard(c, 0, 0, flip >= 0.5, s, this.comm[i]);
        }
      }
      c.restore();
    }
  }

  _holeFan(c, x, y, hand, seat, s, leaning) {
    s = s || 1;
    var deck = this._pt('deck');
    var cw = 30 * s, chh = 21 * s;
    c.save();
    c.translate(x, y);
    var self = this;
    hand.forEach(function (card, i) {
      var prog = self._dealHoleProg(seat, i);
      if (prog <= 0) return;
      var cx = (i - 0.5) * cw * 0.95;
      var lift = leaning ? -16 * s : 0; // 看牌动作：牌抬起
      var rot = leaning ? (i - 0.5) * 0.18 : 0;
      c.save();
      if (prog < 1) {
        c.translate((deck[0] - x) * (1 - prog) + cx * prog, (deck[1] - y) * (1 - prog));
        c.rotate((1 - prog) * 0.6);
        c.globalAlpha = 0.35 + 0.65 * prog;
        self._miniCard(c, 0, 0, false, s);
      } else {
        c.translate(cx, lift);
        c.rotate(rot);
        var flip = self._revealProg(seat, i);
        var sx = 1 - Math.abs(1 - 2 * flip);
        if (sx > 0.05) {
          c.scale(Math.max(0.05, sx), 1);
          self._miniCard(c, 0, 0, flip >= 0.5, s, card);
        }
      }
      c.restore();
    }, this);
    c.restore();
  }

  _miniCard(c, x, y, faceUp, s, card) {
    s = s || 1;
    var cw = 32 * s, chh = 22.5 * s;
    c.save();
    c.translate(x, y);
    if (faceUp && card) {
      var red = __thRed.indexOf(card.s) >= 0;
      c.fillStyle = '#f5efe2';
      this._rr(c, -cw / 2, -chh / 2, cw, chh, 2.5 * s);
      c.fill();
      c.strokeStyle = 'rgba(60,30,10,.5)'; c.lineWidth = 0.8; c.stroke();
      var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
      c.fillStyle = red ? '#c0392b' : '#2c3e50';
      c.font = '700 ' + Math.round(10 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(rl, 0, -2.5 * s);
      c.font = Math.round(8 * s) + 'px monospace';
      c.fillText(__thSuits[card.s], 0, 6.5 * s);
    } else {
      c.fillStyle = '#3a1018';
      this._rr(c, -cw / 2, -chh / 2, cw, chh, 2.5 * s);
      c.fill();
      c.strokeStyle = '#6a2830'; c.lineWidth = 0.8; c.stroke();
      c.strokeStyle = 'rgba(255,190,110,.28)';
      c.beginPath();
      c.moveTo(-cw * 0.3, -chh * 0.3); c.lineTo(cw * 0.3, chh * 0.3);
      c.moveTo(cw * 0.3, -chh * 0.3); c.lineTo(-cw * 0.3, chh * 0.3);
      c.stroke();
    }
    c.restore();
  }

  // 你的底牌：一只手拿着 2 张——空格翻看（扇形展开）/再按盖回
  _playerHand(c, w, h, s) {
    var p = this.players[0];
    if (!p || !p.hand) return;
    if (this._dealHoleProg(0, 0) <= 0) return;
    var cw = Math.max(52, Math.min(92, w * 0.075)), chh = cw * 1.45;
    var cy = h - chh * 0.56;
    var n = 2;
    var reveal = this.phase === 'settle';
    var win = reveal && this.winnerSeat === 0;
    var active = this.phase === 'bet' && this.turn === 0 && !p.folded;
    // 捧牌手影
    c.save();
    c.fillStyle = 'rgba(0,0,0,.5)';
    c.beginPath();
    c.ellipse(w / 2, cy + chh * 0.52, cw * (n / 2 + 0.8), chh * 0.55, 0, 0, Math.PI * 2);
    c.fill();
    c.restore();
    var self = this;
    p.hand.forEach(function (card, i) {
      var prog = self._dealHoleProg(0, i);
      if (prog <= 0) return;
      var k = i - (n - 1) / 2;
      var pk = self._peekProg(i);
      var spread = cw * (0.35 + 0.45 * pk);         // 看牌时扇形展开
      var cx = k * spread * prog;
      var rise = (1 - prog) * 70;
      var idle = self._dealt ? Math.sin(self.tick * 0.05 + i) * 3 : 0;
      var lift = Math.abs(k) * chh * 0.06;
      c.save();
      c.translate(w / 2 + cx, cy + lift + rise + idle);
      c.rotate(k * (0.05 + 0.10 * pk) * prog);
      if (p.folded) {
        c.globalAlpha = 0.55;
        self._bigBack(c, cw, chh);
      } else if (reveal || pk >= 1) {
        self._bigFace(c, card, cw, chh, active, win);
      } else if (pk > 0) {
        var sx = 1 - Math.abs(1 - 2 * pk);
        c.save();
        if (sx > 0.05) c.scale(Math.max(0.05, sx), 1);
        if (pk >= 0.5) self._bigFace(c, card, cw, chh, active, win);
        else self._bigBack(c, cw, chh);
        c.restore();
      } else {
        self._bigBack(c, cw, chh);
      }
      c.restore();
    }, this);
    // 标签：背面时提示空格看牌；看牌时显示当前成牌
    var label;
    if (p.folded) label = '已弃牌';
    else if (reveal) label = '你的手牌 · ' + __thCatName[__thBestAny(p.hand.concat(this.comm || [])).cat];
    else if (!this._dealt) label = '发牌中…';
    else if (this.peek || this.peekT > 0 && this._peekProg(0) >= 1) {
      label = this.commUp >= 3
        ? '你的手牌 · ' + __thCatName[__thBestAny(p.hand.concat(this.comm.slice(0, this.commUp))).cat]
        : '你的底牌';
    } else label = '按 空格 看牌';
    c.save();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = '700 ' + Math.round(13 * s) + 'px monospace';
    c.fillStyle = win ? '#ffd98a' : '#ecd9b8';
    c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 5;
    c.fillText(label, w / 2, cy - chh * 0.74);
    c.restore();
  }
  _bigBack(c, cw, chh) {
    c.fillStyle = '#3a1018';
    this._rr(c, -cw / 2, -chh / 2, cw, chh, cw * 0.12);
    c.fill();
    c.strokeStyle = '#6a2830'; c.lineWidth = 1.2; c.stroke();
    c.strokeStyle = 'rgba(255,190,110,.25)'; c.lineWidth = 1;
    c.beginPath();
    c.moveTo(-cw * 0.3, -chh * 0.3); c.lineTo(cw * 0.3, chh * 0.3);
    c.moveTo(cw * 0.3, -chh * 0.3); c.lineTo(-cw * 0.3, chh * 0.3);
    c.stroke();
  }
  _bigFace(c, card, cw, chh, active, win) {
    var red = __thRed.indexOf(card.s) >= 0;
    c.fillStyle = 'rgba(0,0,0,.48)';
    this._rr(c, -cw / 2 + 3, -chh / 2 + 6, cw, chh, cw * 0.12);
    c.fill();
    if (active) { c.shadowColor = '#ffc87a'; c.shadowBlur = 14; }
    if (win) { c.shadowColor = '#ffd98a'; c.shadowBlur = 20; }
    var face = c.createLinearGradient(0, -chh / 2, 0, chh / 2);
    face.addColorStop(0, '#fbf6ea'); face.addColorStop(1, '#e8dfc8');
    c.fillStyle = face;
    this._rr(c, -cw / 2, -chh / 2, cw, chh, cw * 0.12);
    c.fill();
    c.shadowBlur = 0;
    c.strokeStyle = win ? '#ffc87a' : 'rgba(90,50,20,.6)'; c.lineWidth = win ? 2.4 : 1;
    c.stroke();
    var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
    var col = red ? '#c0392b' : '#2c3e50';
    c.fillStyle = col;
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = '700 ' + Math.round(cw * 0.30) + 'px Georgia,serif';
    c.fillText(rl, -cw * 0.32, -chh * 0.36);
    c.font = Math.round(cw * 0.26) + 'px Georgia,serif';
    c.fillText(__thSuits[card.s], -cw * 0.32, -chh * 0.19);
    c.save();
    c.rotate(Math.PI);
    c.font = '700 ' + Math.round(cw * 0.30) + 'px Georgia,serif';
    c.fillText(rl, -cw * 0.32, -chh * 0.36);
    c.font = Math.round(cw * 0.26) + 'px Georgia,serif';
    c.fillText(__thSuits[card.s], -cw * 0.32, -chh * 0.19);
    c.restore();
    c.globalAlpha = 0.16;
    c.font = Math.round(cw * 0.62) + 'px Georgia,serif';
    c.fillText(__thSuits[card.s], 0, chh * 0.02);
    c.globalAlpha = 1;
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
        var x2 = at2[0] + (muck[0] - at2[0]) * p, y2 = at2[1] + 30 + (muck[1] - at2[1]) * p;
        c.save();
        c.globalAlpha = 1 - p * 0.6;
        c.translate(x2, y2); c.rotate(p * 1.2);
        self._miniCard(c, 0, 0, false, (s || 1) * 0.9);
        c.restore();
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

    if (this.phase === 'deal') {
      // 每张牌落位一声弹牌（8 底牌 + 5 公共）
      var landN = Math.floor((this.tick - this.dealT - 14 - TH_DEAL_FLIGHT) / TH_DEAL_GAP) + 1;
      while (this._dealSnd < Math.min(13, landN)) { Casino.audio.play('card-flick', 0.45); this._dealSnd++; }
      if (this.tick - this.dealT >= TH_DEAL_TICKS) {
        this._dealt = true;
        Casino.audio.play('voice-deal', 0.5);
        this._beginStreet(0);
      }
      return;
    }
    if (this.phase === 'flip') {
      var flipN = Math.floor((this.tick - this.flipStart) / TH_FLIP_CARD_STEP) + 1;
      while (this._flipSnd < Math.min(this.flipTarget - this.flipFrom, flipN)) {
        Casino.audio.play('card-place', 0.55);
        this._flipSnd++;
      }
      if (this.tick >= this.flipUntil) {
        this.commUp = this.flipTarget;
        if (this.allInMode) {
          if (this.commUp < 5) return this._flipComm(this.commUp + 1, true);
          this._showdown();
        } else {
          this._beginStreet(this.street + 1);
        }
      }
      return;
    }
    if (this.phase === 'reveal') {
      while (this._revealIdx < this._revealOrder.length &&
             this.tick - this.revealStart >= 40 + this._revealIdx * 95 + 26) {
        var st = this._revealOrder[this._revealIdx];
        var cat = __thCatName[__thBestAny(this.players[st].hand.concat(this.comm)).cat];
        this.fx.push({
          kind: 'text', at: 'seat' + st,
          text: (st === 0 ? '你' : this.players[st].name) + ' · ' + cat,
          color: st === 0 ? '#8fce8f' : '#ffd98a', start: this.tick, dur: 95, big: true
        });
        Casino.say(cat, { pitch: 0.75, rate: 1.05 });
        Casino.audio.play('card-flick', 0.4);
        this._revealIdx++;
      }
      if (!this._saidCompare && this.tick - this.revealStart >= 40 + this._revealOrder.length * 95) {
        this._saidCompare = true;
        this._msg('比大小…');
        Casino.audio.play('voice-compare', 0.8);
      }
      if (this.tick - this.revealStart >= this._revealDur) this._finishReveal();
      return;
    }
    if (this.phase !== 'bet') return;

    // AI 随机看牌动作（不在自己回合也会偶尔看一下）
    for (var pi = 1; pi <= 3; pi++) {
      if (this.players[pi].folded) continue;
      if (!this._nextIdlePeek[pi]) this._nextIdlePeek[pi] = this.tick + __thRand(240, 600);
      if (!this.aiPeek[pi] && this.tick >= this._nextIdlePeek[pi]) {
        this.aiPeek[pi] = { start: this.tick, dur: __thRand(45, 85) };
        this._nextIdlePeek[pi] = this.tick + __thRand(360, 900);
      }
    }

    var p = this.players[this.turn];
    if (!p || p.folded || p.allIn) { this._advanceTurn(); return; }
    if (p.human) {
      if (this.bot && this.tick - this.lastActTick >= TH_BOT_TICKS) this.act(0, 'call');
      return;
    }
    if (this.tick < this.thinkUntil) return;
    var strength = __thStrength(p.hand, this.comm.slice(0, this.commUp));
    var decision = __thAI(strength, p.persona, this.currentBet - p.bet,
      this.street > 0 && !this.allInMode && this._anyCanRaise(), this.street > 0 && !this.allInMode);
    this.act(this.turn, decision.type);
  }

  destroy() {
    this.destroyed = true;
    document.removeEventListener('keydown', this._keyHdlr);
  }
}

// ---------- 注册进赌坊 ----------
Casino.register('holdem', {
  name: '德州扑克 Hold\'em',
  icon: '🂡',
  desc: '2 张底牌 + 5 张公共牌 · 期前/翻牌/转牌/河牌四轮 · 跟注/加注/加倍/全压/弃牌',
  create: function (container, ctx) { return new CasinoHoldem(container, ctx); }
});

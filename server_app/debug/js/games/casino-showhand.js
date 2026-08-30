// casino-showhand.js — 算力赌坊 · 首桌：梭哈 Show Hand
// 4 人桌（玩家 + 3 个性格化 AI），5 张牌，底注 → 3 轮下注 → 摊牌。
// AI 行动用帧计数延迟（不用 setTimeout），兼容 &step 自动化测试。

// ---------- 牌型引擎（纯函数，供测试） ----------
// 牌：{r: 2..14(A), s: 0..3}；花色名仅展示用
var __shSuits = ['♠', '♥', '♣', '♦'];
var __shRed = [1, 3];

function __shNewDeck() {
  var d = [];
  for (var s = 0; s < 4; s++) for (var r = 2; r <= 14; r++) d.push({ r: r, s: s });
  return d;
}
function __shShuffle(d) {
  for (var i = d.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = d[i]; d[i] = d[j]; d[j] = t;
  }
  return d;
}
// 评估 5 张牌 → {cat, keys[]}；cat: 8豹子 7同花顺 6金刚 5同花 4顺子 3三条 2两对 1对子 0散牌
function __shEval(cards) {
  var rs = cards.map(function (c) { return c.r; }).sort(function (a, b) { return b - a; });
  var flush = cards.every(function (c) { return c.s === cards[0].s; });
  var uniq = {};
  rs.forEach(function (r) { uniq[r] = (uniq[r] || 0) + 1; });
  var groups = Object.keys(uniq).map(Number).sort(function (a, b) {
    return uniq[b] - uniq[a] || b - a; // 数量降序，同数量点数降序
  });
  var straight = false, sKeys = null;
  if (groups.length === 5) {
    if (rs[0] - rs[4] === 4) { straight = true; sKeys = [rs[0]]; }
    else if (rs[0] === 14 && rs[1] === 5 && rs[4] === 2) { straight = true; sKeys = [5]; } // A2345 最小顺
  }
  if (groups.length === 1) return { cat: 8, keys: [rs[0]] };               // 5同（万能牌时才可能，防御）
  var c0 = uniq[groups[0]];
  if (c0 === 4) return { cat: 6, keys: groups };                            // 金刚（四条）
  if (c0 === 3 && groups.length === 2) return { cat: 8, keys: groups };     // 豹子（三条+对子=葫芦）
  if (flush && straight) return { cat: 7, keys: sKeys };                    // 同花顺
  if (flush) return { cat: 5, keys: rs };                                   // 同花
  if (straight) return { cat: 4, keys: sKeys };                             // 顺子
  if (c0 === 3) return { cat: 3, keys: groups };                            // 三条
  if (c0 === 2 && groups.length === 3) return { cat: 2, keys: groups };     // 两对
  if (c0 === 2) return { cat: 1, keys: groups };                            // 对子
  return { cat: 0, keys: rs };                                              // 散牌
}
var __shCatName = ['散牌', '对子', '两对', '三条', '顺子', '同花', '金刚', '同花顺', '豹子'];
function __shCompare(a, b) {
  var ea = __shEval(a), eb = __shEval(b);
  if (ea.cat !== eb.cat) return ea.cat - eb.cat;
  for (var i = 0; i < Math.max(ea.keys.length, eb.keys.length); i++) {
    var ka = ea.keys[i] || 0, kb = eb.keys[i] || 0;
    if (ka !== kb) return ka - kb;
  }
  return 0;
}
// 摊牌用强度归一化（AI 决策输入）
function __shStrength(cards) {
  var e = __shEval(cards);
  var base = e.cat * 1000;
  var kick = (e.keys[0] || 0) * 10;
  return Math.min(1, (base + kick) / 8500);
}

// ---------- AI 决策（纯函数，供测试） ----------
// persona: aggr | tight | bluff；返回 {type: call|raise|fold|allin}
function __shAI(strength, persona, toCall, canRaise, roll) {
  roll = roll === undefined ? Math.random() : roll;
  if (toCall <= 0) {
    // 无人下注（不会发生在本流程，防御）：中强以上加注
    if (canRaise && strength > 0.45 && roll < 0.7) return { type: 'raise' };
    return { type: 'call' };
  }
  if (persona === 'aggr') {
    if (strength < 0.18 && roll < 0.5) return { type: 'fold' };
    if (strength > 0.5 && roll < 0.6 && canRaise) return { type: 'raise' };
    if (strength > 0.75 && roll < 0.25) return { type: 'allin' };
    return { type: 'call' };
  }
  if (persona === 'tight') {
    if (strength < 0.35) return { type: 'fold' };
    if (strength > 0.7 && roll < 0.45 && canRaise) return { type: 'raise' };
    return { type: 'call' };
  }
  // bluff：弱牌偶尔装强，强牌慢打
  if (strength < 0.2 && roll < 0.22 && canRaise) return { type: 'raise' };
  if (strength < 0.3 && roll < 0.6) return { type: 'fold' };
  if (strength > 0.8 && roll < 0.15) return { type: 'allin' };
  if (strength > 0.6 && roll < 0.4 && canRaise) return { type: 'raise' };
  return { type: 'call' };
}
var __shTaunts = {
  aggr: ['这把我梭了！', '内存就是拿来烧的', 'raise or die', '这点注码也想吓我？'],
  tight: ['风险太高，撤', '我先做下边界检查', '这手牌 stack 不稳', '保守是一种美德'],
  bluff: ['你猜我有没有？', '编译错误也是特性', '我在钓你，真的', '信息不对称，朋友']
};

// ---------- 梭哈桌 ----------
const SH_ANTE = 10, SH_ROUND_BET = 20, SH_RAISE = 50, SH_TURNS = 3, SH_AI_TICKS = 42, SH_BOT_TICKS = 26;
// 动画节奏（帧数，60fps）：发牌总时长 / 摊牌首翻延迟 / 每家翻牌间隔 / 翻牌时长 / 收尾停顿
const SH_DEAL_TICKS = 108, SH_FLIP_BASE = 26, SH_FLIP_STEP = 30, SH_FLIP_DUR = 10, SH_REVEAL_TAIL = 22;

class CasinoShowhand {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.phase = 'deal'; // deal(发牌动画) → bet → reveal(摊牌翻牌) → settle
    this.destroyed = false;
    this.aiChips = [1000, 1000, 1000]; // AI 筹码仅本桌会话（玩家直接用共享钱包）
    this.fx = [];          // 帧驱动特效：飞筹码 / 漂浮文字 / 弃牌飞牌
    this.dispPot = 0;      // 底池滚动显示值（数字有上升动画）
    this.banner = null;    // 中央横幅（ALL IN / 胜负宣告）
    this.shake = null;     // 屏幕震动
    this.flash = null;     // 全屏闪光
    this._posCache = null; // 座位/底池坐标（renderScene 每帧刷新，供 act() 派生特效）
    this._buildDom(container);
    this._startHand();
  }

  // ---------- DOM ----------
  _el(tag, css, html) {
    var e = document.createElement(tag);
    if (css) e.style.cssText = css;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }
  _cardHtml(card, hidden, small) {
    if (hidden) return '<div style="width:' + (small ? 26 : 38) + 'px;height:' + (small ? 36 : 52) + 'px;border-radius:5px;background:linear-gradient(135deg,#2a1f45,#1a1230);border:1px solid #4a3a6a;display:inline-flex;align-items:center;justify-content:center;color:#6a5a80;font-size:14px;margin:1px">🂠</div>';
    var red = __shRed.indexOf(card.s) >= 0;
    var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
    return '<div style="width:' + (small ? 26 : 38) + 'px;height:' + (small ? 36 : 52) + 'px;border-radius:5px;background:' + (red ? '#fff5f5' : '#f5f7ff') + ';border:1px solid #999;display:inline-flex;flex-direction:column;align-items:center;justify-content:center;color:' + (red ? '#d33' : '#335') + ';font-weight:700;font-size:' + (small ? 11 : 15) + 'px;margin:1px;box-shadow:1px 1px 3px rgba(0,0,0,.4)"><div>' + rl + '</div><div style="font-size:' + (small ? 10 : 13) + 'px">' + __shSuits[card.s] + '</div></div>';
  }
  _buildDom(container) {
    var self = this;
    // 全屏浮层：场景（酒馆/桌/对手/手牌）全由大厅 canvas 绘制，DOM 只承载信息与按钮
    this.root = this._el('div', 'position:absolute;inset:0;color:#ecd9b8;pointer-events:none');
    // 顶栏（左上）
    var bar = this._el('div', 'position:absolute;top:10px;left:10px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:10px;padding:6px 12px;pointer-events:auto');
    bar.appendChild(this._el('div', 'font-size:15px;font-weight:700;color:#ffc87a', '🃏 梭哈'));
    this.chipsEl = this._el('div', 'font-size:12px;color:#8fce8f', '');
    bar.appendChild(this.chipsEl);
    this.potEl = this._el('div', 'font-size:12px;color:#ffc87a', '');
    bar.appendChild(this.potEl);
    var helpBtn = this._el('button', 'padding:3px 10px;border-radius:6px;border:1px solid #5a3a1c;background:rgba(30,16,8,.85);color:#e8c890;cursor:pointer;font-family:inherit;font-size:11px', '？牌型速查');
    helpBtn.onclick = function () { self.helpEl.style.display = self.helpEl.style.display === 'none' ? 'block' : 'none'; };
    bar.appendChild(helpBtn);
    var exitBtn = this._el('button', 'padding:3px 10px;border-radius:6px;border:1px solid #6a2a22;background:rgba(40,12,8,.85);color:#e0a090;cursor:pointer;font-family:inherit;font-size:11px', '← 离开');
    exitBtn.onclick = function () { self.destroy(); self.ctx.exit(); };
    bar.appendChild(exitBtn);
    bar.appendChild(this._el('div', 'font-size:10px;color:#8a7048', '虚拟筹码·仅供娱乐'));
    this.root.appendChild(bar);
    // 牌型速查（顶栏下方，可开合）
    this.helpEl = this._el('div', 'display:none;position:absolute;top:52px;left:10px;max-width:min(560px,86vw);padding:10px 14px;border:1px solid #5a3a1c;border-radius:8px;background:rgba(16,8,4,.93);font-size:12px;line-height:1.9;color:#d8c0a0;pointer-events:auto',
      '牌型从大到小：<b style="color:#ffc87a">豹子</b>(葫芦) &gt; <b>同花顺</b> &gt; <b>金刚</b>(四条) &gt; <b>同花</b> &gt; <b>顺子</b>(含 A2345) &gt; <b>三条</b> &gt; <b>两对</b> &gt; <b>对子</b> &gt; 散牌<br>操作：<b>跟注</b>=投入相同筹码继续 · <b>加注</b>=+' + SH_RAISE + ' 抬价 · <b>弃牌</b>=放弃本局 · <b>梭哈</b>=全压，其余玩家跟或弃后直接摊牌');
    this.root.appendChild(this.helpEl);
    // 消息（中下，悬浮在手牌上方）
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:198px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    // 玩家手牌 DOM（保留元素但隐藏：手牌改由 canvas 以第一人称大牌呈现）
    this.handEl = this._el('div', 'display:none', '');
    this.root.appendChild(this.handEl);
    // 操作栏（底部居中）
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px;pointer-events:auto;max-width:94vw;box-sizing:border-box', '');
    this.root.appendChild(this.actEl);
    // 再来一局（同位置）
    this.againEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);pointer-events:auto', '');
    this.root.appendChild(this.againEl);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }
  _taunt(seat) {
    var arr = __shTaunts[this.players[seat].persona];
    return arr[Math.floor(Math.random() * arr.length)];
  }

  // ---------- 牌局 ----------
  _startHand() {
    var self = this;
    if (this.wallet.get() < SH_ANTE) {
      this._msg('算力不足以下注（底注 ' + SH_ANTE + '）——去大厅领救济金吧');
      this.phase = 'broke';
      this._renderAll();
      this.againEl.innerHTML = '';
      return;
    }
    var deck = __shShuffle(__shNewDeck());
    this.players = [];
    // seat 0 = 玩家；1..3 = AI（性格固定轮换）
    this.players.push({ human: true, name: '你', chips: -1, folded: false, allIn: false, bet: 0, hand: deck.splice(0, 5) });
    var personas = ['aggr', 'tight', 'bluff'];
    var names = ['Overflow_bot', 'NullSafe', 'PhishMaster'];
    for (var i = 0; i < 3; i++) {
      this.players.push({ human: false, persona: personas[i], name: names[i], chips: this.aiChips[i], folded: false, allIn: false, bet: 0, hand: deck.splice(0, 5) });
    }
    // 底注
    this.wallet.sub(SH_ANTE);
    this.pot = SH_ANTE * 4;
    for (var j = 1; j < 4; j++) this.aiChips[j - 1] -= SH_ANTE;
    this.players.forEach(function (p) { p.bet = SH_ANTE; });
    this.round = 1;
    this.currentBet = SH_ROUND_BET;
    this.allInMode = false;
    this.turn = 0;           // 轮到 seat 0（玩家）起步
    // 发牌动画窗口：视觉上牌逐张飞出，动画结束后才轮到行动
    this.dealT = this.tick;
    this._dealt = false;
    this.lastActTick = this.tick + SH_DEAL_TICKS;
    this.phase = 'bet';
    this.winnerSeat = undefined;
    this.fx = []; this.banner = null; this.shake = null; this.flash = null;
    this.dispPot = 0;
    this._msg('发牌中…');
    // 底注筹码从各家飞入底池
    for (var a = 0; a < 4; a++) {
      this.fx.push({ kind: 'chip', from: 'seat' + a, to: 'pot', start: this.dealT + 26 + a * 6, dur: 20, n: SH_ANTE });
    }
    this._renderAll();
  }

  _active() { return this.players.filter(function (p) { return !p.folded; }); }
  _pending(p) { return !p.folded && !p.allIn && p.bet < this.currentBet; }
  _anyCanRaise() {
    var self = this;
    return this._active().some(function (p) { return !p.allIn && (p.human ? self.wallet.get() : p.chips) >= self.currentBet + SH_RAISE; });
  }

  // ---------- 特效派生（act/结算时调用；坐标由 renderScene 的 _posCache 解析） ----------
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

  // 当前该谁行动；全部跟齐 → 推进轮次/摊牌
  _advanceTurn() {
    var self = this;
    // 找下一个待行动玩家
    for (var i = 1; i <= 4; i++) {
      var seat = (this.turn + i) % 4;
      if (this._pending(this.players[seat])) { this.turn = seat; this.lastActTick = this.tick; return; }
    }
    // 无人待行动：本轮结束
    var alive = this._active();
    if (alive.length <= 1) { this._awardFoldWin(alive[0]); return; }
    if (this.allInMode || this.round >= SH_TURNS) { this._showdown(); return; }
    this.round++;
    this.currentBet = Math.max(this.currentBet, SH_ROUND_BET);
    this.players.forEach(function (p) { p.bet = 0; });
    this._msg('第 ' + this.round + '/' + SH_TURNS + ' 轮下注');
    // 新一轮从第一个活着的玩家开始
    for (var k = 0; k < 4; k++) {
      if (!this.players[k].folded && !this.players[k].allIn) { this.turn = k; this.lastActTick = this.tick; return; }
    }
    this._showdown();
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
      sfx('click');
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
      sfx('click');
    } else if (action === 'raise') {
      var need = toCall + SH_RAISE;
      var bank = p.human ? this.wallet.get() : p.chips;
      if (bank < need) { action = 'call'; return this.act(seat, 'call'); }
      if (p.human) this.wallet.sub(need); else { p.chips -= need; this.aiChips[seat - 1] = p.chips; }
      p.bet += need;
      this.pot += need;
      this.currentBet = p.bet;
      this._msg((p.human ? '你' : p.name) + ' 加注到 ' + this.currentBet + (p.human ? '' : '：「' + this._taunt(seat) + '」'));
      this._fxChipsToPot(seat, need);
      this._fxText(seat, '加注！', '#ffc87a');
      sfx('powerup');
    } else if (action === 'allin') {
      var all = p.human ? this.wallet.get() : p.chips;
      if (p.human) this.wallet.sub(all); else { p.chips = 0; this.aiChips[seat - 1] = 0; }
      p.bet += all;
      this.pot += all;
      if (p.bet > this.currentBet) this.currentBet = p.bet;
      p.allIn = true;
      this.allInMode = true;
      this._msg((p.human ? '你' : p.name) + ' 梭哈！全压 ' + all + (p.human ? '' : '：「' + this._taunt(seat) + '」'));
      this._fxChipsToPot(seat, all);
      this._fxText(seat, 'ALL IN！', '#ff6a5a', true);
      this.banner = { text: 'ALL IN · 全压 ' + all, color: '#ff8a70', start: this.tick, dur: 70 };
      this._fxShake(10, 16);
      this._fxFlash('#ff3018');
      sfx('win');
    }
    // 先推进回合再渲染：行动权回到谁手上，就渲染谁的操作面板
    // （否则 AI 行动后轮到玩家时按钮不会刷新，玩家被卡死无法操作）
    this._advanceTurn();
    this._renderAll(this.phase === 'settle');
  }

  _awardFoldWin(winner) {
    this.phase = 'settle';
    this.winnerSeat = this.players.indexOf(winner);
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
    sfx('win');
    this.pot = 0;
    this._renderAll(true);
    this._againBtn();
  }

  // 摊牌分两幕：先逐张翻牌营造悬念（reveal），翻完再 _finishReveal 结算
  _showdown() {
    this.phase = 'reveal';
    var alive = this._active();
    var best = alive[0];
    for (var i = 1; i < alive.length; i++) {
      if (__shCompare(alive[i].hand, best.hand) > 0) best = alive[i];
    }
    this._revealWinner = best;
    this.revealStart = this.tick;
    this._revealOrder = alive.filter(function (p) { return !p.human; }).map(function (p) { return this.indexOf(p); }, this.players);
    this._revealIdx = 0;
    this._revealDur = SH_FLIP_BASE + this._revealOrder.length * SH_FLIP_STEP + SH_REVEAL_TAIL;
    this._msg('摊牌！');
    sfx('powerup');
  }
  _finishReveal() {
    var best = this._revealWinner;
    this.phase = 'settle';
    var potNow = this.pot;
    if (best.human) {
      this.wallet.add(this.pot);
      sfx('win');
      this._msg('摊牌：你的 ' + __shCatName[__shEval(best.hand).cat] + ' 最大，赢得底池 ' + this.pot + '！');
      this.banner = { text: '你赢得底池 +' + potNow, color: '#ffd98a', start: this.tick, dur: 100 };
    } else {
      sfx('lose');
      this._msg('摊牌：' + best.name + ' 以 ' + __shCatName[__shEval(best.hand).cat] + ' 收走底池 ' + this.pot);
      this.banner = { text: best.name + ' 以 ' + __shCatName[__shEval(best.hand).cat] + ' 收走底池', color: '#e08080', start: this.tick, dur: 100 };
    }
    this.winnerSeat = this.players.indexOf(best);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 0);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 5);
    this._fxChipsToSeat(this.winnerSeat, Math.max(30, Math.round(potNow / 3)), 10);
    this._fxShake(6, 14);
    this.pot = 0; // dispPot 动画式下降
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

  // ---------- 渲染 ----------
  _renderAll(reveal) {
    if (this.destroyed) return;
    this.chipsEl.textContent = '你的算力 ' + this.wallet.get().toLocaleString();
    this.potEl.textContent = '底池 ' + (this.pot || 0);
    this._renderHand(reveal);
    this._renderActions();
  }

  // ---------- 场景渲染（大厅 canvas 每帧调用：第一人称桌面 + 对面三人 + 底池 + 手持牌 + 特效） ----------
  // 摊牌翻牌进度：0=背面 1=翻开（reveal 阶段逐张翻）
  _flipProg(seat, cardIdx) {
    if (this.phase === 'settle') return 1;
    if (this.phase !== 'reveal') return 0;
    var oi = (this._revealOrder || []).indexOf(seat);
    if (oi < 0) return 1; // 玩家的牌一直可见
    var t0 = this.revealStart + SH_FLIP_BASE + oi * SH_FLIP_STEP + cardIdx * 3;
    return Math.max(0, Math.min(1, (this.tick - t0) / SH_FLIP_DUR));
  }
  // 发牌进度：0 未动 → 1 落位（对手先发，玩家最后）
  _dealProg(seat, cardIdx) {
    if (this._dealt) return 1;
    var base = seat === 0 ? 75 + cardIdx * 5 : 6 + ((seat - 1) * 5 + cardIdx) * 4;
    var dur = seat === 0 ? 12 : 9;
    return Math.max(0, Math.min(1, (this.tick - (this.dealT + base)) / dur));
  }
  // 坐标解析（特效引用座位/底池，画时才换算，适配任意画布尺寸）
  _pt(ref) {
    var pc = this._posCache || { seats: [[400, 560], [170, 250], [400, 225], [630, 250]], pot: [400, 390] };
    if (ref === 'pot') return pc.pot;
    if (ref && ref.indexOf('seat') === 0) return pc.seats[parseInt(ref.slice(4), 10)];
    return pc.pot;
  }

  renderScene(c, w, h, t) {
    if (this.destroyed || !this.players) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    // 座位坐标缓存（act()/特效画时解析）
    var aiPos = [[w * 0.205, h * 0.415, s * 1.15], [w * 0.5, h * 0.375, s * 1.3], [w * 0.795, h * 0.415, s * 1.15]];
    this._posCache = {
      seats: [[w / 2, h * 0.94], aiPos[0], aiPos[1], aiPos[2]],
      pot: [w / 2, h * 0.665],
      deck: [w / 2, h * 0.58]
    };
    // 屏幕震动（ALL IN / 胜负时刻；过期由 update 清理）
    c.save();
    if (this.shake) {
      var sp = (this.tick - this.shake.start) / this.shake.dur;
      if (sp < 1) {
        var amp = this.shake.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      }
    }
    P.table(c, w, h);
    var reveal = this.phase === 'settle';
    var colors = { aggr: '#e06040', tight: '#5fa8e0', bluff: '#b070e0', player: '#4ac070' };
    // 三个对手坐在对面：正对镜头（中央稍远稍小、两侧稍近）
    for (var i = 1; i <= 3; i++) {
      var p = this.players[i];
      var pos = aiPos[i - 1];
      P.seat(c, pos[0], pos[1], t, {
        name: p.name, color: colors[p.persona], persona: p.persona, scale: pos[2],
        folded: p.folded, active: this.phase === 'bet' && this.turn === i && this._dealt,
        winner: reveal && this.winnerSeat === i, chipsLabel: '◈ ' + p.chips
      });
      // 行动倒计时环（AI 思考进度可视化）
      if (this.phase === 'bet' && this.turn === i && this._dealt && !p.human) {
        var frac = Math.max(0, Math.min(1, (this.tick - this.lastActTick) / SH_AI_TICKS));
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
      // 桌面牌：发牌飞行落位 + 摊牌逐张翻开（弃牌飞走后不画）
      if (!p.folded) this._cardFan(c, pos[0], h * 0.545, p.hand, i, s);
      // 本轮已下注：桌前小筹码堆
      if (!p.folded && this.phase === 'bet' && this._dealt && p.bet > SH_ANTE) P.chips(c, pos[0] + 62 * s, h * 0.60, p.bet);
    }
    // 底池（数字滚动 + 落注弹跳放大）
    var showPot = Math.round(this.dispPot);
    if (showPot > 0) {
      var pop = this._potPopT !== undefined ? Math.max(0, 1 - (this.tick - this._potPopT) / 12) : 0;
      var scl = 1 + 0.22 * pop;
      c.save();
      c.translate(w / 2, h * 0.665); c.scale(scl, scl); c.translate(-w / 2, -h * 0.665);
      P.chips(c, w / 2, h * 0.665, showPot);
      c.restore();
      c.fillStyle = '#ffc87a';
      c.font = '700 ' + Math.round(13 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.shadowColor = '#000'; c.shadowBlur = 5;
      c.fillText('底池 ' + showPot, w / 2, h * 0.665 - 12 * s);
      c.shadowBlur = 0;
    }
    // 你的手牌：第一人称，发牌时逐张升起展开
    this._playerFan(c, w, h, reveal, s);
    // 特效层（飞筹码 / 漂浮文字 / 弃牌飞牌）
    this._drawFx(c, s);
    // 摊牌庆祝
    if (reveal && this.winnerSeat !== undefined) P.confetti(c, w, h, t);
    c.restore(); // 结束震动位移
    // 横幅与全屏闪光（不随震动位移）
    this._drawBanner(c, w, h);
    this._drawFlash(c, w, h);
  }

  // 特效层
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
  // 中央横幅（ALL IN / 胜负宣告）：弹入 + 停留 + 淡出（过期由 update 清理）
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
  // 全屏闪光（ALL IN 红闪；过期由 update 清理）
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

  // 对手桌面牌（压扁小牌：发牌飞行 → 落位 → 摊牌翻面）
  _cardFan(c, x, y, hand, seat, s) {
    s = s || 1;
    var deck = this._posCache ? this._posCache.deck : [x, y];
    c.save();
    c.translate(x, y);
    hand.forEach(function (card, i) {
      var prog = this._dealProg(seat, i);
      if (prog <= 0) return;
      var cx = (i - 2) * 30 * s * 0.78;
      c.save();
      if (prog < 1) {
        // 飞行中：从牌堆插值到落位
        c.translate((deck[0] - x) * (1 - prog) + cx * prog, (deck[1] - y) * (1 - prog));
        c.rotate((1 - prog) * 0.6);
        c.globalAlpha = 0.35 + 0.65 * prog;
        this._miniCard(c, 0, 0, false, s);
      } else {
        c.translate(cx, 0);
        // 翻面动画：横向压缩翻转（背面→正面）
        var flip = this._flipProg(seat, i);
        var sx = 1 - Math.abs(1 - 2 * flip);
        if (sx > 0.05) {
          c.scale(Math.max(0.05, sx), 1);
          this._miniCard(c, 0, 0, flip >= 0.5, s, card);
        }
      }
      c.restore();
    }, this);
    c.restore();
  }
  // 单张压扁小牌（牌面/牌背）
  _miniCard(c, x, y, faceUp, s, card) {
    s = s || 1;
    var cw = 30 * s, chh = 21 * s;
    c.save();
    c.translate(x, y);
    if (faceUp && card) {
      var red = __shRed.indexOf(card.s) >= 0;
      c.fillStyle = '#f5efe2';
      this._rr(c, -cw / 2, -chh / 2, cw, chh, 2.5 * s);
      c.fill();
      c.strokeStyle = 'rgba(60,30,10,.5)'; c.lineWidth = 0.8; c.stroke();
      var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
      c.fillStyle = red ? '#c0392b' : '#2c3e50';
      c.font = '700 ' + Math.round(9 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(rl, 0, -2 * s);
      c.font = Math.round(7 * s) + 'px monospace';
      c.fillText(__shSuits[card.s], 0, 6 * s);
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
  // 你的手牌：第一人称大扇形——发牌逐张升起展开，呼吸浮动，行动/胜利发光
  _playerFan(c, w, h, reveal, s) {
    var p = this.players[0];
    if (!p || !p.hand) return;
    if (this._dealProg(0, 0) <= 0) return; // 还没发到玩家
    var cw = Math.max(46, Math.min(80, w * 0.062)), chh = cw * 1.45;
    var cy = h - chh * 0.58;
    var n = p.hand.length;
    var active = this.phase === 'bet' && this.turn === 0 && !p.folded;
    var win = reveal && this.winnerSeat === 0;
    // 手部阴影（捧牌的暗影垫在牌后）
    c.save();
    c.fillStyle = 'rgba(0,0,0,.5)';
    c.beginPath();
    c.ellipse(w / 2, cy + chh * 0.52, cw * (n / 2 + 0.8), chh * 0.55, 0, 0, Math.PI * 2);
    c.fill();
    c.restore();
    p.hand.forEach(function (card, i) {
      var prog = this._dealProg(0, i);
      if (prog <= 0) return;
      var k = i - (n - 1) / 2;
      var cx = k * cw * 0.74 * prog;                 // 扇形随发牌展开
      var rise = (1 - prog) * 70;                    // 从画面下方升起
      var idle = this._dealt ? Math.sin(this.tick * 0.05 + i) * 3 : 0; // 呼吸浮动
      var lift = Math.abs(k) * chh * 0.07;
      c.save();
      c.translate(w / 2 + cx, cy + lift + rise + idle);
      c.rotate(k * 0.10 * prog);
      if (p.folded) { // 弃牌：暗淡牌背摊开
        c.globalAlpha = 0.55;
        c.fillStyle = '#3a1018';
        this._rr(c, -cw / 2, -chh / 2, cw, chh, cw * 0.12);
        c.fill();
        c.strokeStyle = '#6a2830'; c.lineWidth = 1.2; c.stroke();
      } else {
        var red = __shRed.indexOf(card.s) >= 0;
        // 牌影
        c.fillStyle = 'rgba(0,0,0,.48)';
        this._rr(c, -cw / 2 + 3, -chh / 2 + 6, cw, chh, cw * 0.12);
        c.fill();
        // 到你行动：牌缘暖光 / 赢家：金光
        if (active) { c.shadowColor = '#ffc87a'; c.shadowBlur = 14; }
        if (win) { c.shadowColor = '#ffd98a'; c.shadowBlur = 20; }
        // 牌面
        var face = c.createLinearGradient(0, -chh / 2, 0, chh / 2);
        face.addColorStop(0, '#fbf6ea'); face.addColorStop(1, '#e8dfc8');
        c.fillStyle = face;
        this._rr(c, -cw / 2, -chh / 2, cw, chh, cw * 0.12);
        c.fill();
        c.shadowBlur = 0;
        c.strokeStyle = win ? '#ffc87a' : 'rgba(90,50,20,.6)'; c.lineWidth = win ? 2.4 : 1;
        c.stroke();
        // 角标（左上正、右下倒）
        var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
        var col = red ? '#c0392b' : '#2c3e50';
        c.fillStyle = col;
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.font = '700 ' + Math.round(cw * 0.30) + 'px Georgia,serif';
        c.fillText(rl, -cw * 0.32, -chh * 0.36);
        c.font = Math.round(cw * 0.26) + 'px Georgia,serif';
        c.fillText(__shSuits[card.s], -cw * 0.32, -chh * 0.19);
        c.save();
        c.rotate(Math.PI);
        c.font = '700 ' + Math.round(cw * 0.30) + 'px Georgia,serif';
        c.fillText(rl, -cw * 0.32, -chh * 0.36);
        c.font = Math.round(cw * 0.26) + 'px Georgia,serif';
        c.fillText(__shSuits[card.s], -cw * 0.32, -chh * 0.19);
        c.restore();
        // 中央大花色淡印
        c.globalAlpha = 0.16;
        c.font = Math.round(cw * 0.62) + 'px Georgia,serif';
        c.fillText(__shSuits[card.s], 0, chh * 0.02);
        c.globalAlpha = 1;
      }
      c.restore();
    }, this);
    // 牌型标签（悬于牌上方；发牌中显示进度提示）
    var label = this._dealt
      ? '你的手牌' + (reveal ? ' · ' + __shCatName[__shEval(p.hand).cat] : '') + (p.folded ? ' · 已弃牌' : '')
      : '发牌中…';
    c.save();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = '700 ' + Math.round(13 * s) + 'px monospace';
    c.fillStyle = win ? '#ffd98a' : '#ecd9b8';
    c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 5;
    c.fillText(label, w / 2, cy - chh * 0.74);
    c.restore();
  }
  // 圆角矩形路径
  _rr(c, x, y, w2, h2, r) {
    c.beginPath();
    c.moveTo(x + r, y);
    c.arcTo(x + w2, y, x + w2, y + h2, r);
    c.arcTo(x + w2, y + h2, x, y + h2, r);
    c.arcTo(x, y + h2, x, y, r);
    c.arcTo(x, y, x + w2, y, r);
    c.closePath();
  }
  _renderHand(reveal) {
    var self = this;
    this.handEl.innerHTML = '';
    if (!this.players) return;
    var p = this.players[0];
    var win = this.winnerSeat === 0;
    this.handEl.innerHTML = '<div style="font-size:12px;color:' + (win ? '#f0c674' : '#9d8cb8') + ';margin-bottom:2px">你的手牌' + (reveal ? ' · ' + __shCatName[__shEval(p.hand).cat] : '') + (p.folded ? ' · 已弃牌' : '') + '</div>' +
      '<div>' + p.hand.map(function (c) { return self._cardHtml(c, false, false); }).join('') + '</div>';
  }
  _renderActions() {
    var self = this;
    if (this.phase === 'settle') { this.actEl.innerHTML = ''; return; } // 结算面板只留"再来一局"
    if (this.phase !== 'bet' || this.players[0].folded || this.turn !== 0) {
      this.actEl.innerHTML = this.players[0].folded ? '<span style="font-size:12px;color:#a08a6a">你已弃牌，等待其他玩家…</span>' : '';
      return;
    }
    if (!this._dealt) { // 发牌动画期间暂不开放操作
      this.actEl.innerHTML = '<span style="font-size:12px;color:#a08a6a">发牌中…</span>';
      return;
    }
    this.actEl.innerHTML = '';
    var toCall = this.currentBet - this.players[0].bet;
    var mk = function (label, action, cls) {
      var b = self._el('button', 'padding:9px 20px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = function () { self.act(0, action); };
      return b;
    };
    this.actEl.appendChild(mk(toCall > 0 ? '跟注 ' + Math.min(toCall, this.wallet.get()) : '过牌', 'call', '#8fce8f'));
    if (!this.allInMode && this._anyCanRaise()) this.actEl.appendChild(mk('加注 +' + SH_RAISE, 'raise', '#ffc87a'));
    if (!this.allInMode && this.wallet.get() > 0) this.actEl.appendChild(mk('梭哈 全压 ' + this.wallet.get(), 'allin', '#e06060'));
    this.actEl.appendChild(mk('弃牌', 'fold', '#a08a6a'));
  }

  // ---------- 帧驱动（所有动画按 tick 推进，无 setTimeout，兼容 &step 自动化） ----------
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    // 过期特效清理（横幅/震动/闪光在 update 里过期，绘制保持纯函数）
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= this.shake.dur) this.shake = null;
    if (this.flash && this.tick - this.flash.start >= this.flash.dur) this.flash = null;
    // 底池数字滚动（升快降慢）
    if (typeof this.dispPot !== 'number') this.dispPot = this.pot || 0;
    if (this.dispPot < this.pot) this.dispPot = Math.min(this.pot, this.dispPot + Math.max(2, Math.round((this.pot - this.dispPot) * 0.3)));
    else if (this.dispPot > this.pot) this.dispPot = Math.max(this.pot, this.dispPot - Math.max(1, Math.round((this.dispPot - this.pot) * 0.2)));
    // 发牌动画结束 → 正式开赌
    if (this.phase === 'bet' && !this._dealt && this.tick - this.dealT >= SH_DEAL_TICKS) {
      this._dealt = true;
      this._msg('第 ' + this.round + '/' + SH_TURNS + ' 轮下注 · 底注 ' + SH_ANTE);
      this._renderAll();
    }
    // 摊牌节奏：逐张翻牌（每家翻完浮出牌型）→ 收尾结算
    if (this.phase === 'reveal') {
      while (this._revealIdx < this._revealOrder.length &&
             this.tick - this.revealStart >= SH_FLIP_BASE + this._revealIdx * SH_FLIP_STEP + SH_FLIP_DUR) {
        var st = this._revealOrder[this._revealIdx];
        this.fx.push({ kind: 'text', at: 'seat' + st, text: __shCatName[__shEval(this.players[st].hand).cat], color: '#ffd98a', start: this.tick, dur: 50 });
        sfx('click');
        this._revealIdx++;
      }
      if (this.tick - this.revealStart >= this._revealDur) this._finishReveal();
      return;
    }
    if (this.phase !== 'bet') return;
    var p = this.players[this.turn];
    if (!p || p.folded || p.allIn) { this._advanceTurn(); return; }
    if (p.human) {
      // bot 模式（自动化测试）：到点自动跟注
      if (this.bot && this.tick - this.lastActTick >= SH_BOT_TICKS) this.act(0, 'call');
      return;
    }
    if (this.tick - this.lastActTick < SH_AI_TICKS) return;
    var strength = __shStrength(p.hand);
    var decision = __shAI(strength, p.persona, this.currentBet - p.bet, !this.allInMode && this._anyCanRaise());
    this.act(this.turn, decision.type);
  }

  destroy() { this.destroyed = true; }
}

// ---------- 注册进赌坊 ----------
Casino.register('showhand', {
  name: '梭哈 Show Hand',
  icon: '🃏',
  desc: '5 张牌 · 4 人桌 · 跟/加/弃/梭哈全压，胆量与牌型的双重博弈',
  create: function (container, ctx) { return new CasinoShowhand(container, ctx); }
});

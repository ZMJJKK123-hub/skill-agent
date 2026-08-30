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

class CasinoShowhand {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.phase = 'deal'; // deal → bet → showdown → settle
    this.destroyed = false;
    this.aiChips = [1000, 1000, 1000]; // AI 筹码仅本桌会话（玩家直接用共享钱包）
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
    // DOM 为半透明浮层（z=1），场景（房间/桌/人物）由大厅 canvas 绘制（z=0）
    this.root = this._el('div', 'position:relative;z-index:1;max-width:900px;margin:0 auto;color:#e6d9f2;min-height:560px;padding:0 10px;box-sizing:border-box');
    // 顶栏
    var bar = this._el('div', 'display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px;background:rgba(8,4,13,.72);border:1px solid #3a2d52;border-radius:10px;padding:6px 10px');
    bar.appendChild(this._el('div', 'font-size:15px;font-weight:700;color:#f0c674', '🃏 梭哈'));
    this.chipsEl = this._el('div', 'font-size:12px;color:#7dd87d', '');
    bar.appendChild(this.chipsEl);
    this.potEl = this._el('div', 'font-size:12px;color:#f0c674', '');
    bar.appendChild(this.potEl);
    var helpBtn = this._el('button', 'padding:3px 10px;border-radius:6px;border:1px solid #4a3a6a;background:#1b1230;color:#d8c8f0;cursor:pointer;font-family:inherit;font-size:11px', '？牌型速查');
    helpBtn.onclick = function () { self.helpEl.style.display = self.helpEl.style.display === 'none' ? 'block' : 'none'; };
    bar.appendChild(helpBtn);
    var exitBtn = this._el('button', 'padding:3px 10px;border-radius:6px;border:1px solid #6a3a4a;background:#2a1220;color:#e0a0b0;cursor:pointer;font-family:inherit;font-size:11px', '← 离开');
    exitBtn.onclick = function () { self.destroy(); self.ctx.exit(); };
    bar.appendChild(exitBtn);
    this.root.appendChild(bar);
    // 牌型速查
    this.helpEl = this._el('div', 'display:none;margin-bottom:8px;padding:10px 14px;border:1px solid #4a3a6a;border-radius:8px;background:rgba(18,10,30,.9);font-size:12px;line-height:1.9;color:#c8b8e0',
      '牌型从大到小：<b style="color:#f0c674">豹子</b>(葫芦) &gt; <b>同花顺</b> &gt; <b>金刚</b>(四条) &gt; <b>同花</b> &gt; <b>顺子</b>(含 A2345) &gt; <b>三条</b> &gt; <b>两对</b> &gt; <b>对子</b> &gt; 散牌<br>操作：<b>跟注</b>=投入相同筹码继续 · <b>加注</b>=+' + SH_RAISE + ' 抬价 · <b>弃牌</b>=放弃本局 · <b>梭哈</b>=全压，其余玩家跟或弃后直接摊牌');
    this.root.appendChild(this.helpEl);
    // AI 座位区：人物由 canvas 绘制，DOM 占位保持布局（顶部让出人物区）
    this.seatsEl = this._el('div', 'height:' + 0 + 'px', '');
    this.root.appendChild(this.seatsEl);
    // 消息行
    this.msgEl = this._el('div', 'min-height:24px;text-align:center;font-size:13px;color:#ffe9a0;margin:4px 0;text-shadow:0 1px 3px rgba(0,0,0,.8)', '');
    this.root.appendChild(this.msgEl);
    // 玩家手牌
    this.handEl = this._el('div', 'text-align:center;margin:4px 0;background:rgba(8,4,13,.6);border:1px solid #3a2d52;border-radius:10px;padding:6px 0', '');
    this.root.appendChild(this.handEl);
    // 操作栏
    this.actEl = this._el('div', 'display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:6px 0;background:rgba(8,4,13,.72);border:1px solid #3a2d52;border-radius:10px;padding:8px', '');
    this.root.appendChild(this.actEl);
    // 再来一局
    this.againEl = this._el('div', 'text-align:center;margin:4px 0', '');
    this.root.appendChild(this.againEl);
    this.root.appendChild(this._el('div', 'text-align:center;font-size:10px;color:#8a7ba0;margin-top:6px;text-shadow:0 1px 2px #000', '虚拟筹码 · 仅供娱乐'));
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
      this._renderSeats();
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
    this.lastActTick = this.tick;
    this.phase = 'bet';
    this._msg('第 ' + this.round + '/' + SH_TURNS + ' 轮 · 底注已收');
    this._renderAll();
  }

  _active() { return this.players.filter(function (p) { return !p.folded; }); }
  _pending(p) { return !p.folded && !p.allIn && p.bet < this.currentBet; }
  _anyCanRaise() {
    var self = this;
    return this._active().some(function (p) { return !p.allIn && (p.human ? self.wallet.get() : p.chips) >= self.currentBet + SH_RAISE; });
  }

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
      sfx('win');
    }
    this._renderAll();
    this._advanceTurn();
  }

  _awardFoldWin(winner) {
    this.phase = 'settle';
    this.winnerSeat = this.players.indexOf(winner);
    if (winner.human) {
      this.wallet.add(this.pot);
      this._msg('其他玩家全部弃牌，你直接赢得底池 ' + this.pot + '！');
    } else {
      this._msg('其他玩家全部弃牌，' + winner.name + ' 收走底池 ' + this.pot);
      winner.chips += this.pot; this.aiChips[this.players.indexOf(winner) - 1] = winner.chips;
    }
    sfx('win');
    this.pot = 0;
    this._renderAll(true);
    this._againBtn();
  }

  _showdown() {
    this.phase = 'showdown';
    var alive = this._active();
    var best = alive[0];
    for (var i = 1; i < alive.length; i++) {
      if (__shCompare(alive[i].hand, best.hand) > 0) best = alive[i];
    }
    this.phase = 'settle';
    if (best.human) {
      this.wallet.add(this.pot);
      sfx('win');
      this._msg('摊牌：你的 ' + __shCatName[__shEval(best.hand).cat] + ' 最大，赢得底池 ' + this.pot + '！');
    } else {
      sfx('lose');
      this._msg('摊牌：' + best.name + ' 以 ' + __shCatName[__shEval(best.hand).cat] + ' 收走底池 ' + this.pot);
      best.chips += this.pot; this.aiChips[this.players.indexOf(best) - 1] = best.chips;
    }
    this.winnerSeat = this.players.indexOf(best);
    this.pot = 0;
    this._renderAll(true);
    this._againBtn();
  }

  _againBtn() {
    var self = this;
    this.actEl.innerHTML = '';
    this.againEl.innerHTML = '';
    var b = this._el('button', 'padding:8px 26px;border-radius:8px;border:1px solid #f0c674;background:#2a1f10;color:#f0c674;cursor:pointer;font-family:inherit;font-size:14px;font-weight:700', '🔄 再来一局');
    b.onclick = function () { self.againEl.innerHTML = ''; self._startHand(); };
    this.againEl.appendChild(b);
  }

  // ---------- 渲染 ----------
  _renderAll(reveal) {
    if (this.destroyed) return;
    this.chipsEl.textContent = '你的算力 ' + this.wallet.get().toLocaleString();
    this.potEl.textContent = '底池 ' + (this.pot || 0);
    this._renderSeats(reveal);
    this._renderHand(reveal);
    this._renderActions();
  }
  _renderSeats(reveal) {
    // 人物/座位由 canvas 场景层绘制（renderScene），DOM 不再渲染座位框
    this.seatsEl.innerHTML = '';
  }

  // ---------- 场景渲染（大厅 canvas 每帧调用：桌面 + 人物 + 手牌扇 + 底池） ----------
  renderScene(c, w, h, t) {
    if (this.destroyed || !this.players) return;
    var P = Casino.paint;
    P.table(c, w, h);
    var reveal = this.phase === 'settle';
    var colors = { aggr: '#e06040', tight: '#5fa8e0', bluff: '#b070e0', player: '#4ac070' };
    // AI 三人围桌
    var aiPos = [[w * 0.2, h * 0.42, 1.05], [w * 0.5, h * 0.33, 1.05], [w * 0.8, h * 0.42, 1.05]];
    for (var i = 1; i <= 3; i++) {
      var p = this.players[i];
      var pos = aiPos[i - 1];
      P.seat(c, pos[0], pos[1], t, {
        name: p.name, color: colors[p.persona], persona: p.persona, scale: pos[2],
        folded: p.folded, active: this.phase === 'bet' && this.turn === i,
        winner: reveal && this.winnerSeat === i, chipsLabel: '◈ ' + p.chips
      });
      // 手牌扇：弃牌不画；摊牌亮真牌，平时牌背
      if (!p.folded) this._cardFan(c, pos[0], pos[1] + 28 * pos[2], p.hand, reveal);
    }
    // 玩家（下中）
    var me = this.players[0];
    P.seat(c, w * 0.5, h * 0.9, t, {
      name: '你', color: colors.player, persona: 'player', scale: 1.2,
      folded: me.folded, active: this.phase === 'bet' && this.turn === 0,
      winner: reveal && this.winnerSeat === 0, chipsLabel: '◈ ' + this.wallet.get()
    });
    // 底池筹码（桌心）
    if (this.pot > 0) {
      P.chips(c, w / 2, h * 0.5, this.pot);
      c.fillStyle = '#f0c674';
      c.font = '700 13px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.shadowColor = '#000'; c.shadowBlur = 4;
      c.fillText('底池 ' + this.pot, w / 2, h * 0.5 - 6);
      c.shadowBlur = 0;
    }
    // 摊牌庆祝
    if (reveal && this.winnerSeat !== undefined) P.confetti(c, w, h, t);
  }
  // 迷你手牌扇（canvas 版）
  _cardFan(c, x, y, hand, faceUp) {
    var self = this;
    c.save();
    c.translate(x, y);
    hand.forEach(function (card, i) {
      c.save();
      c.rotate((i - 2) * 0.16);
      var cw = 17, chh = 24, cx = (i - 2) * 7;
      if (faceUp) {
        var red = __shRed.indexOf(card.s) >= 0;
        c.fillStyle = '#f8f8ff';
        c.fillRect(cx - cw / 2, -chh - 6, cw, chh);
        c.strokeStyle = '#889'; c.lineWidth = 0.8; c.strokeRect(cx - cw / 2, -chh - 6, cw, chh);
        c.fillStyle = red ? '#d33' : '#335';
        c.font = '700 9px monospace'; c.textAlign = 'center'; c.textBaseline = 'middle';
        var rl = card.r === 11 ? 'J' : card.r === 12 ? 'Q' : card.r === 13 ? 'K' : card.r === 14 ? 'A' : card.r;
        c.fillText(rl, cx, -chh - 18);
        c.font = '8px monospace';
        c.fillText(__shSuits[card.s], cx, -chh - 10);
      } else {
        c.fillStyle = '#2a1f45';
        c.fillRect(cx - cw / 2, -chh - 6, cw, chh);
        c.strokeStyle = '#4a3a6a'; c.lineWidth = 0.8; c.strokeRect(cx - cw / 2, -chh - 6, cw, chh);
        c.fillStyle = '#6a5a80'; c.font = '9px monospace'; c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText('░', cx, -chh / 2 - 6);
      }
      c.restore();
    });
    c.restore();
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
    if (this.phase !== 'bet' || this.players[0].folded || this.turn !== 0) {
      this.actEl.innerHTML = this.phase === 'bet' && !this.players[0].folded ? '' : '<span style="font-size:12px;color:#6a5a80">等待其他玩家…</span>';
      return;
    }
    this.actEl.innerHTML = '';
    var toCall = this.currentBet - this.players[0].bet;
    var mk = function (label, action, cls) {
      var b = self._el('button', 'padding:8px 18px;border-radius:8px;border:1px solid ' + cls + ';background:#160d26;color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = function () { self.act(0, action); };
      return b;
    };
    this.actEl.appendChild(mk(toCall > 0 ? '跟注 ' + Math.min(toCall, this.wallet.get()) : '过牌', 'call', '#7dd87d'));
    if (!this.allInMode && this._anyCanRaise()) this.actEl.appendChild(mk('加注 +' + SH_RAISE, 'raise', '#f0c674'));
    if (!this.allInMode && this.wallet.get() > 0) this.actEl.appendChild(mk('梭哈 全压 ' + this.wallet.get(), 'allin', '#e06060'));
    this.actEl.appendChild(mk('弃牌', 'fold', '#8a7ba0'));
  }

  // ---------- 帧驱动 ----------
  update() {
    if (this.destroyed || this.phase !== 'bet') return;
    this.tick++;
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

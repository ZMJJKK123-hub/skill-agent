// casino-paigow.js — 算力赌坊 · 牌九（大牌九）
// 第一人称：庄家对面砌牌，玩家 4 张骨牌分「前手/后手」两副比牌。
// 规则：32 张骨牌（文子 11 种×2 + 武子 10）；对牌 16 级（至尊宝最大）；
//       非对牌两手点数相加取个位，9 最大、0 憋十最小，同点庄家吃；
//       两手全胜才赢（1:1），一胜一负平局退注；至尊宝赢局赔 2 倍。
// 丁三(1-2)/二四(2-4) 单算点数可作 3 或 6 取优（至尊宝灵活点）。

// ---------- 引擎（纯函数，供测试） ----------
// 文子（每种 2 张）：天6-6 地1-1 人4-4 和鹅1-3 梅5-5 长三3-3 板凳2-2
//                   斧5-6 红头十4-6 高脚七1-6 零霖六2-4
// 武子（各 1 张）：杂九(3-6/4-5) 杂八(2-6/3-5) 杂七(2-5/3-4) 杂五(1-4/2-3)
//                 + 丁三(1-2)×2（与二四合成至尊宝）
function __pgNewSet() {
  var civ = [
    ['tian', 6, 6], ['di', 1, 1], ['ren', 4, 4], ['he', 1, 3], ['mei', 5, 5],
    ['chang', 3, 3], ['ban', 2, 2], ['fu', 5, 6], ['hong', 4, 6], ['jiao', 1, 6], ['er', 2, 4]
  ];
  var mil = [
    ['za9a', 3, 6], ['za9b', 4, 5], ['za8a', 2, 6], ['za8b', 3, 5],
    ['za7a', 2, 5], ['za7b', 3, 4], ['za5a', 1, 4], ['za5b', 2, 3]
  ];
  var set = [];
  civ.forEach(function (d) {
    set.push({ k: d[0], top: d[1], bot: d[2] });
    set.push({ k: d[0], top: d[1], bot: d[2] });
  });
  mil.forEach(function (d) { set.push({ k: d[0], top: d[1], bot: d[2] }); });
  set.push({ k: 'ding', top: 1, bot: 2 });
  set.push({ k: 'ding', top: 1, bot: 2 });
  return set; // 32 张
}
function __pgShuffle(s) {
  for (var i = s.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = s[i]; s[i] = s[j]; s[j] = t;
  }
  return s;
}
// 对牌等级：1=至尊宝(丁三+二四) 2=双天 … 12=双零霖六 13=杂九 14=杂八 15=杂七 16=杂五；0=非对牌
var PG_CIV_RANK = { tian: 2, di: 3, ren: 4, he: 5, mei: 6, chang: 7, ban: 8, fu: 9, hong: 10, jiao: 11, er: 12 };
var PG_PAIR_NAMES = ['—', '至尊宝', '双天', '双地', '孖人', '双鹅', '双梅', '双长三', '双板凳', '双斧', '双红头十', '双高脚七', '双零霖六', '杂九对', '杂八对', '杂七对', '杂五对'];
function __pgMilGroup(k) {
  return k === 'za9a' || k === 'za9b' ? 13
    : k === 'za8a' || k === 'za8b' ? 14
    : k === 'za7a' || k === 'za7b' ? 15
    : k === 'za5a' || k === 'za5b' ? 16 : 0;
}
function __pgPairRank(a, b) {
  if (!a || !b) return 0;
  if ((a.k === 'ding' && b.k === 'er') || (a.k === 'er' && b.k === 'ding')) return 1;
  if (a.k === b.k && PG_CIV_RANK[a.k]) return PG_CIV_RANK[a.k];
  var g = __pgMilGroup(a.k);
  return g && g === __pgMilGroup(b.k) ? g : 0;
}
// 点数：两手全部点数相加取个位；至尊宝两牌（丁三/二四）可作 3 或 6 取优
function __pgVal(hand) {
  var sums = [0];
  hand.forEach(function (t) {
    var base = t.top + t.bot;
    var alt = t.k === 'ding' ? 6 : t.k === 'er' ? 3 : null;
    var next = [];
    sums.forEach(function (sv) {
      next.push(sv + base);
      if (alt !== null) next.push(sv + alt);
    });
    sums = next;
  });
  var best = 0;
  sums.forEach(function (sv) { if (sv % 10 > best) best = sv % 10; });
  return best; // 0=憋十
}
function __pgEval(hand) {
  var rank = __pgPairRank(hand[0], hand[1]);
  return { rank: rank, val: rank ? 0 : __pgVal(hand) };
}
function __pgStrength(hand) { // 单副牌综合强度（越大越强）
  var e = __pgEval(hand);
  return e.rank ? (17 - e.rank) * 100 : e.val;
}
function __pgCompare(a, b) { // >0 a 胜；<0 b 胜；0 同级（同点/同对级 → 庄家吃）
  var ea = __pgEval(a), eb = __pgEval(b);
  if (ea.rank && eb.rank) return eb.rank - ea.rank; // 对牌级数小者大
  if (ea.rank) return 1;                            // 对牌压制一切点数牌
  if (eb.rank) return -1;
  return ea.val - eb.val;
}
function __pgLabel(hand) {
  var e = __pgEval(hand);
  if (e.rank) return PG_PAIR_NAMES[e.rank];
  return e.val === 0 ? '憋十' : e.val + '点';
}
// 大牌九分牌：4 张拆 2+2，后手不得小于前手；先保最强后手，再保前手
function __pgSplitBest(tiles) {
  return __pgSplitBy(tiles, 'safe');
}
// 闲家分层：safe 后手优先（保大不作死）；bold（aggr）极大极小——平衡两手搏双赢，
// 为此会拆对子（如 双斧+地+人 → 拆成 9点+3点 而非 对斧+2点）。庄家始终 safe。
function __pgSplitBy(tiles, persona) {
  var bold = persona === 'bold';
  var best = null;
  for (var i = 0; i < 4; i++) for (var j = i + 1; j < 4; j++) {
    var pick = [tiles[i], tiles[j]];
    var rest = tiles.filter(function (_, x) { return x !== i && x !== j; });
    [[rest, pick], [pick, rest]].forEach(function (cand) {
      var front = cand[0], back = cand[1];
      if (__pgCompare(back, front) < 0) return; // 倒牌：非法
      var sb = __pgStrength(back), sf = __pgStrength(front);
      var score = bold
        ? Math.min(sb, sf) * 10000 + sb // 两手平衡优先（弱手决定双胜概率）
        : sb * 10000 + sf;              // 后手优先
      if (!best || score > best.score) best = { front: front, back: back, score: score };
    });
  }
  return best;
}

var PG_BETS = [20, 50, 100, 200];
var PG_DEAL_GAP = 9, PG_DEAL_FLIGHT = 13, PG_REVEAL_STEP = 105;
var PG_NAMES = ['老K', '阿豪', '薇薇', 'Momo', 'Jack', '强叔', 'Kiki', '小美', '阿杰', '苏珊', '刀仔', '老钱', 'Tony', '露露', '大飞', '娜娜', 'K哥', '阿灿', '莉莉', '肥猫'];
var PG_PIPS = {
  1: [[0, 0]],
  2: [[0, -0.34], [0, 0.34]],
  3: [[-0.3, -0.32], [0, 0], [0.3, 0.32]],
  4: [[-0.27, -0.3], [0.27, -0.3], [-0.27, 0.3], [0.27, 0.3]],
  5: [[-0.27, -0.3], [0.27, -0.3], [0, 0], [-0.27, 0.3], [0.27, 0.3]],
  6: [[-0.27, -0.34], [-0.27, 0], [-0.27, 0.34], [0.27, -0.34], [0.27, 0], [0.27, 0.34]]
};

// ---------- 牌九桌 ----------
class CasinoPaigow {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.banner = null;
    this.shake = null;
    this._posCache = null;
    this.history = [];
    // 座位：0=玩家（第一人称），1..3=AI 闲家；庄家独立
    var pool = PG_NAMES.slice();
    this.seats = [];
    var personas = ['aggr', 'tight', 'bluff'];
    for (var i = 0; i < 3; i++) {
      var nm = pool.splice(Math.floor(Math.random() * pool.length), 1)[0];
      this.seats.push({
        human: false, name: nm, persona: personas[i], chips: 800 + Math.floor(Math.random() * 1600),
        tiles: [], split: null, splitT: 0, res: null, thinkUntil: 0, leanAt: 0
      });
    }
    this.seats.unshift({ human: true, name: '你', chips: 0, tiles: [], split: null, splitT: 0, res: null });
    this.dealer = { name: '庄家', tiles: [], split: null, splitT: 0, flipAt: 0 };
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
    var bar = this._el('div', 'position:absolute;top:10px;left:10px;display:flex;gap:8px;pointer-events:auto;z-index:3');
    var exitBtn = this._el('button', 'padding:4px 12px;border-radius:6px;border:1px solid rgba(240,120,100,.4);background:rgba(10,5,3,.45);color:#e0a090;cursor:pointer;font-family:inherit;font-size:11px', '← 离开');
    exitBtn.onclick = function () { self.destroy(); self.ctx.exit(); };
    bar.appendChild(exitBtn);
    var helpBtn = this._el('button', 'padding:4px 12px;border-radius:6px;border:1px solid #5a3a1c;background:rgba(10,5,3,.45);color:#e8c890;cursor:pointer;font-family:inherit;font-size:11px', '? 对牌速查');
    helpBtn.onclick = function () { self._toggleHelp(); };
    bar.appendChild(helpBtn);
    this.root.appendChild(bar);
    this.msgEl = this._el('div', 'position:absolute;left:6%;right:6%;bottom:212px;text-align:center;font-size:14px;color:#ffe9c0;text-shadow:0 1px 4px rgba(0,0,0,.95)', '');
    this.root.appendChild(this.msgEl);
    this.actEl = this._el('div', 'position:absolute;left:50%;bottom:14px;transform:translateX(-50%);display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;background:rgba(10,5,3,.78);border:1px solid #5a3a1c;border-radius:12px;padding:8px 12px;pointer-events:auto;max-width:94vw;box-sizing:border-box;z-index:3', '');
    this.root.appendChild(this.actEl);
    // 骨牌点击层（分牌阶段选牌；z 低于按钮栏，避免盖住操作）
    this.clickLayer = this._el('div', 'position:absolute;inset:0;pointer-events:none;z-index:1');
    this.clickLayer.onclick = function (ev) { self._onTap(ev, this); };
    this.root.appendChild(this.clickLayer);
    // 速查面板
    this.helpEl = this._el('div', 'position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(92vw,640px);max-height:82vh;overflow:auto;background:rgba(16,9,5,.97);border:1px solid #6a4a28;border-radius:12px;padding:16px 18px;pointer-events:auto;display:none;z-index:6;line-height:1.7;font-size:12.5px;color:#d8c3a0');
    this.helpEl.innerHTML =
      '<div style="font-size:15px;font-weight:700;color:#ffc87a;margin-bottom:8px">牌九 · 对牌速查</div>' +
      '<div style="color:#e8d5b0;margin-bottom:6px">对牌 16 级（大→小）：</div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 18px;font-family:monospace">' +
      '至尊宝 丁三+二四|双天 6-6|双地 1-1|孖人 4-4|双鹅 1-3|双梅 5-5|双长三 3-3|双板凳 2-2|双斧 5-6|双红头十 4-6|双高脚七 1-6|双零霖六 2-4|杂九对 3-6/4-5|杂八对 2-6/3-5|杂七对 2-5/3-4|杂五对 1-4/2-3'
        .split('|').map(function (s) { return '<div>· ' + s + '</div>'; }).join('') +
      '</div>' +
      '<div style="margin-top:10px;color:#e8d5b0">非对牌：两张牌四段点数相加只取个位，<b>9 最大、憋十（0）最小</b>；丁三/二四可作 3 或 6 取优。</div>' +
      '<div style="margin-top:6px;color:#e8d5b0">大牌九：4 张牌分前/后两手，后手不得小于前手；前后都赢才赢（1:1），一胜一负平局退注。<b>同点/同对级庄家吃。</b>至尊宝在手且赢局，赔 2 倍。</div>';
    var foot = this._el('div', 'margin-top:12px;text-align:center');
    var closeBtn = this._el('button', 'padding:6px 20px;border-radius:8px;border:1px solid #6a4a28;background:rgba(40,22,10,.9);color:#e8c890;cursor:pointer;font-family:inherit', '关闭');
    closeBtn.onclick = function () { self._toggleHelp(); };
    foot.appendChild(closeBtn);
    this.helpEl.appendChild(foot);
    this.root.appendChild(this.helpEl);
    container.appendChild(this.root);
  }
  _toggleHelp() {
    this.helpEl.style.display = this.helpEl.style.display === 'none' ? 'block' : 'none';
  }
  _msg(t) { this.msgEl.textContent = t; }
  _fxText(text, color, big) {
    this.fx.push({ kind: 'text', at: 'center', text: text, color: color || '#ffd98a', start: this.tick, dur: 46, big: !!big });
  }
  _fxChips(toSeat, n, delay) { // toSeat=-1 → 飞向庄家
    this.fx.push({ kind: 'chip', to: toSeat, start: this.tick + (delay || 0), dur: 26, n: n });
  }
  _fxShake(amp, dur) { this.shake = { amp: amp, start: this.tick, dur: dur }; }

  _awaitBet() {
    this.phase = 'bet';
    this.set = __pgShuffle(__pgNewSet());
    this.bet = 0;
    for (var i = 0; i < this.seats.length; i++) {
      var s = this.seats[i];
      s.tiles = []; s.split = null; s.splitT = 0; s.res = null; s.thinkUntil = 0; s.leanAt = 0;
    }
    this.dealer.tiles = []; this.dealer.split = null; this.dealer.splitT = 0; this.dealer.flipAt = 0;
    this._dealN = 0;
    this.flipAt = 0;          // 玩家开牌帧
    this._revealN = 0;
    this.playerRes = null;
    this.settleAt = 0;
    this.splitSel = [];
    this._botSplitAt = 0;
    this.waitT = 0;
    this._gleeAt = 0;
    this.fx = [];
    this.banner = null;
    this.shake = null;
    this._msg('下注开局 · 4 张骨牌分前/后两手对庄家');
    Casino.audio.play('voice-bets', 0.7);
    this._renderActions();
    this._syncClickLayer();
  }

  start(bet) {
    if (this.phase !== 'bet') return;
    if (!this.wallet.sub(bet)) { this._msg('算力不足'); return; }
    this.bet = bet;
    this.phase = 'deal';
    this.dealT = this.tick;
    this._dealN = 0;
    Casino.audio.play('card-shuffle', 0.6);
    Casino.audio.play('voice-deal', 0.5);
    this._msg('洗牌 · 砌牌…');
    this._renderActions();
    this._syncClickLayer();
  }

  // ---------- 分牌交互 ----------
  _onTap(ev, layer) {
    if (this.phase !== 'split' || this.bot) return;
    var rect = layer.getBoundingClientRect();
    var x = ev.clientX - rect.left, y = ev.clientY - rect.top;
    var rects = (this._posCache && this._posCache.tileRects) || [];
    var hit = -1, bd = 1e9;
    for (var i = 0; i < rects.length; i++) {
      var r = rects[i];
      if (!r) continue;
      var dx = Math.max(Math.abs(x - r.x) - r.w / 2, 0);
      var dy = Math.max(Math.abs(y - r.y) - r.h / 2, 0);
      var d = dx * dx + dy * dy;
      if (d < bd) { bd = d; hit = i; }
    }
    if (hit >= 0 && bd <= (rects[hit].w * 0.4) * (rects[hit].w * 0.4)) this._toggleTile(hit);
  }
  _toggleTile(i) {
    if (this.phase !== 'split') return;
    var ix = this.splitSel.indexOf(i);
    if (ix >= 0) this.splitSel.splice(ix, 1);
    else if (this.splitSel.length < 2) this.splitSel.push(i);
    Casino.audio.play('card-flick', 0.4);
    var tiles = this.seats[0].tiles;
    if (this.splitSel.length === 2) {
      var back = [tiles[this.splitSel[0]], tiles[this.splitSel[1]]];
      var rest = tiles.filter(function (_, x) { return this.splitSel.indexOf(x) < 0; }, this);
      this._msg('后手 ' + __pgLabel(back) + ' · 前手 ' + __pgLabel(rest) +
        (__pgCompare(back, rest) < 0 ? '（后手偏小，需重选！）' : ' · 可以定局'));
    } else {
      this._msg('已选 ' + this.splitSel.length + '/2 张作后手（大的一组）');
    }
    this._renderActions();
  }
  _smartSplit() {
    if (this.phase !== 'split') return;
    var b = __pgSplitBest(this.seats[0].tiles);
    if (!b) return;
    this.splitSel = [0, 1, 2, 3].filter(function (i) { return b.back.indexOf(this.seats[0].tiles[i]) >= 0; }, this);
    Casino.audio.play('card-flick', 0.4);
    this._msg('智能分牌：后手 ' + __pgLabel(b.back) + ' · 前手 ' + __pgLabel(b.front));
    this._renderActions();
  }
  _clearSel() {
    if (this.phase !== 'split') return;
    this.splitSel = [];
    this._msg('重新选择两张作后手');
    this._renderActions();
  }
  _confirmSplit() {
    if (this.phase !== 'split' || this.splitSel.length !== 2) return;
    var tiles = this.seats[0].tiles;
    var back = [tiles[this.splitSel[0]], tiles[this.splitSel[1]]];
    var front = tiles.filter(function (_, x) { return this.splitSel.indexOf(x) < 0; }, this);
    if (__pgCompare(back, front) < 0) {
      this._fxShake(6, 12);
      this._msg('后手不能小于前手（倒牌）· 重选');
      return;
    }
    this.seats[0].split = { front: front, back: back };
    this.seats[0].splitT = this.tick;
    Casino.audio.play('card-place', 0.5);
    this.phase = 'splitwait';
    this.waitT = this.tick;
    this._msg('定局 · 后手 ' + __pgLabel(back) + ' · 前手 ' + __pgLabel(front));
    this._renderActions();
    this._syncClickLayer();
  }

  // ---------- 开牌结算 ----------
  _processSeat(i) { // i：座位（0=玩家，1..3=AI）
    var seat = this.seats[i];
    if (!seat.split) seat.split = __pgSplitBy(seat.tiles, seat.persona === 'aggr' ? 'bold' : 'safe');
    seat.splitT = this.tick;
    var cb = __pgCompare(seat.split.back, this.dealer.split.back);
    var cf = __pgCompare(seat.split.front, this.dealer.split.front);
    var bw = cb > 0, fw = cf > 0; // 同级算庄赢
    var t0 = this.tick;
    this.fx.push({ kind: 'badge', at: i, hand: 'back', res: bw ? 'win' : 'lose', start: t0 + 20, dur: 1e9 }); // 徽章保留到下一局
    this.fx.push({ kind: 'badge', at: i, hand: 'front', res: fw ? 'win' : 'lose', start: t0 + 48, dur: 1e9 });
    Casino.audio.play(i === 0 ? 'voice-compare-cards' : 'card-place', i === 0 ? 0.8 : 0.35);
    var res = bw && fw ? 'win' : (!bw && !fw) ? 'lose' : 'push';
    seat.res = res;
    var stake = seat.human ? this.bet : 40;
    if (res === 'win') {
      seat.chips += stake;
      this._fxChips(i, stake, 66);
      this.fx.push({ kind: 'text', at: 'seat' + i, text: (seat.human ? '赢' : seat.name + ' 赢'), color: '#ffd98a', start: t0 + 68, dur: 52 });
    } else if (res === 'lose') {
      seat.chips -= stake;
      this._fxChips(-1, stake, 66);
      this.fx.push({ kind: 'text', at: 'seat' + i, text: (seat.human ? '输' : seat.name + ' 输'), color: '#e08080', start: t0 + 68, dur: 52 });
    } else {
      this.fx.push({ kind: 'text', at: 'seat' + i, text: '平', color: '#a0c8e8', start: t0 + 68, dur: 52 });
    }
    if (seat.human) this.playerRes = res;
  }
  _settle() {
    this.phase = 'settle';
    var res = this.playerRes || 'push';
    var ps = this.seats[0].split;
    var gee = ps && (__pgPairRank(ps.back[0], ps.back[1]) === 1 || __pgPairRank(ps.front[0], ps.front[1]) === 1);
    var payout = 0;
    if (res === 'win') payout = gee ? this.bet * 3 : this.bet * 2;
    else if (res === 'push') payout = this.bet;
    if (payout > 0) {
      this.wallet.add(payout);
      for (var k = 0; k < 3; k++) this._fxChips(0, payout / 3, k * 5);
    }
    var texts = {
      win: [gee ? '至尊宝！两手全胜 赔 2 倍 +' + this.bet * 2 : '两手全胜！赢 ' + this.bet, '#ffd98a', gee ? 'voice-jackpot' : 'voice-win'],
      lose: ['庄家两手全胜，输 ' + this.bet, '#e08080', 'voice-lose'],
      push: ['一胜一负 · 平局退注', '#a0c8e8', 'voice-push']
    };
    var tx = texts[res];
    this._msg(tx[0]);
    this.banner = {
      text: res === 'win' ? (gee ? '至尊宝 ×2 ！' : '你赢了 +' + this.bet) : res === 'push' ? 'PUSH 平局' : '庄家胜',
      color: tx[1], start: this.tick, dur: 100
    };
    this._fxText(res === 'win' ? (gee ? 'GEE JOON ×2' : 'WIN') : res === 'push' ? 'PUSH' : 'LOSE', tx[1], true);
    Casino.audio.play(tx[2], 0.85);
    if (res === 'win') { this._fxShake(gee ? 9 : 6, 14); this._gleeAt = this.tick; }
    this.history.push(res === 'win' ? 'W' : res === 'lose' ? 'L' : 'P');
    if (this.history.length > 14) this.history.shift();
    Casino.stats.record('paigow', res === 'win' ? 'W' : res === 'lose' ? 'L' : 'P');
    this._renderActions();
  }

  _againBtn() {
    var self = this;
    var b = this._el('button', 'padding:10px 30px;border-radius:8px;border:1px solid #ffc87a;background:rgba(50,28,10,.92);color:#ffc87a;cursor:pointer;font-family:inherit;font-size:14px;font-weight:700', '🔄 再来一局');
    b.onclick = function () { self._awaitBet(); };
    return b;
  }
  _renderActions() {
    var self = this;
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b>' + (this.bet ? ' · 押 ' + this.bet : '') + '</span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls, dis) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      if (dis) { b.disabled = true; b.style.opacity = .45; b.style.cursor = 'not-allowed'; }
      else b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet') {
      if (this.wallet.get() < (PG_BETS[0] || 20)) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f', !this.wallet.canBailout());
        this.actEl.appendChild(bb);
        return;
      }
      PG_BETS.forEach(function (b) {
        if (self.wallet.get() >= b) self.actEl.appendChild(mk('下注 ' + b, function () { self.start(b); }, '#ffc87a'));
      });
      return;
    }
    if (this.phase === 'split') {
      this.actEl.appendChild(mk('🧠 智能分牌', function () { self._smartSplit(); }, '#8fce8f'));
      this.actEl.appendChild(mk('🔄 重选', function () { self._clearSel(); }, '#a0c8e8'));
      this.actEl.appendChild(mk('✅ 定局开牌', function () { self._confirmSplit(); }, '#ffc87a', this.splitSel.length !== 2));
      return;
    }
    if (this.phase === 'settle') {
      this.actEl.appendChild(this._againBtn());
    }
  }
  _syncClickLayer() {
    if (this.clickLayer) this.clickLayer.style.pointerEvents = (this.phase === 'split' && !this.bot) ? 'auto' : 'none';
  }

  // ---------- 场景 ----------
  _seatPos(w, h, s) {
    return {
      dealer: [w / 2, h * 0.30, s * 1.28],
      dealerTiles: [w * 0.5, h * 0.455],
      ai: [[w * 0.155, h * 0.435, s * 1.02], [w * 0.845, h * 0.435, s * 1.02], [w * 0.878, h * 0.695, s * 0.95]],
      aiTiles: [[w * 0.155, h * 0.565], [w * 0.845, h * 0.565], [w * 0.878, h * 0.80]],
      player: [w * 0.42, h * 0.795],
      bet: [w * 0.575, h * 0.775],
      tray: [w * 0.625, h * 0.40]
    };
  }
  _tileW(w, big) {
    return big ? Math.max(30, Math.min(64, w * 0.055)) : Math.max(20, Math.min(44, w * 0.038));
  }
  renderScene(c, w, h, t) {
    if (this.destroyed) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    var L = this._seatPos(w, h, s);
    var twBig = this._tileW(w, true), twSml = this._tileW(w, false);
    this._posCache = {
      tray: L.tray,
      dealer: L.dealerTiles,
      player: L.player,
      seats: [[0, 0]].concat(L.ai),
      tileRects: null
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
    // 庄家（对面中央）
    P.seat(c, L.dealer[0], L.dealer[1], t, {
      name: '庄家 · 荷官', color: '#c8a050', persona: 'tight', scale: L.dealer[2],
      active: this.phase === 'reveal', chipsLabel: this.phase === 'settle' ? '' : '坐庄'
    });
    // AI 闲家
    var colors = { aggr: '#d05545', tight: '#5f8fd0', bluff: '#9a6ad0' };
    for (var ai = 0; ai < 3; ai++) {
      var st = this.seats[ai + 1];
      var pos = L.ai[ai];
      var thinking = this.phase === 'split' && !st.split;
      P.seat(c, pos[0], pos[1], t, {
        name: st.name, color: colors[st.persona], persona: st.persona, scale: pos[2],
        lean: thinking && st.thinkUntil - this.tick < 46,
        winner: st.res === 'win', active: false,
        chipsLabel: '◈ ' + Math.max(0, st.chips)
      });
      if (thinking && st.thinkUntil > this.tick) { // 思考进度环
        var frac = Math.max(0, Math.min(1, 1 - (st.thinkUntil - this.tick) / 140));
        c.save();
        c.strokeStyle = 'rgba(255,200,120,.85)'; c.lineWidth = 3;
        c.shadowColor = '#ffc87a'; c.shadowBlur = 6;
        c.beginPath();
        c.ellipse(pos[0], pos[1] + 60 * pos[2], 44 * pos[2], 12 * pos[2], 0, -Math.PI / 2, -Math.PI / 2 + frac * Math.PI * 2);
        c.stroke();
        c.restore();
      }
    }
    // 牌匣（右上一摞待发骨牌）
    this._tray(c, L.tray, twSml, s);
    // 庄家 4 张
    this._drawSeatTiles(c, 4, L.dealerTiles, twSml, s);
    // AI 闲家牌
    for (var aj = 0; aj < 3; aj++) this._drawSeatTiles(c, aj + 1, L.aiTiles[aj], twSml, s);
    // 玩家 4 张（大）
    this._drawSeatTiles(c, 0, L.player, twBig, s);
    // 押注筹码
    if (this.bet && this.phase !== 'bet') Casino.paint.chips(c, L.bet[0], L.bet[1], this.bet);
    // 战绩点
    Casino.paint.histDots(c, w, h, this.history);
    this._drawFx(c, s);
    c.restore();
    if (this._gleeAt && this.phase === 'settle') Casino.paint.confetti(c, w, h, t);
    this._drawBanner(c, w, h);
  }
  _tray(c, at, tw, s) {
    var th = tw * 1.55;
    c.save();
    var g = c.createLinearGradient(at[0], at[1] - th, at[0], at[1] + th);
    g.addColorStop(0, '#4a2a14'); g.addColorStop(1, '#1c0e06');
    c.fillStyle = g;
    c.fillRect(at[0] - tw * 0.75, at[1] - th * 0.62, tw * 1.5, th * 1.24);
    c.strokeStyle = 'rgba(255,200,120,.4)'; c.lineWidth = 1.5;
    c.strokeRect(at[0] - tw * 0.75, at[1] - th * 0.62, tw * 1.5, th * 1.24);
    // 匣内立牌剪影
    c.fillStyle = 'rgba(244,234,208,.16)';
    for (var i = 0; i < 3; i++) c.fillRect(at[0] - tw * 0.5 + i * tw * 0.5, at[1] - th * 0.45, tw * 0.34, th * 0.9);
    c.restore();
  }
  // 座位牌绘制：seatIdx 4=庄家；处理飞行/翻面/分牌分组/选中
  _drawSeatTiles(c, seatIdx, at, tw, s) {
    var seat = seatIdx === 4 ? this.dealer : this.seats[seatIdx];
    if (!seat || !seat.tiles.length) return;
    var th = tw * 1.55;
    var isPlayer = seatIdx === 0;
    // 目标位置：分牌后 前手(左)/后手(右)
    var posOf = function (i) {
      if (seat.split) {
        var bi = seat.split.back.indexOf(seat.tiles[i]);
        var grp = bi >= 0 ? 1 : 0; // 1=后手(右) 0=前手(左)
        var gi = bi >= 0 ? bi : seat.split.front.indexOf(seat.tiles[i]);
        var gap = tw * 1.08;
        return [at[0] + (grp === 0 ? -1 : 1) * tw * 1.62 + (gi - 0.5) * gap, at[1]];
      }
      return [at[0] + (i - 1.5) * tw * 1.12, at[1]];
    };
    var rects = [];
    for (var i = 0; i < seat.tiles.length; i++) {
      var p = posOf(i);
      var x = p[0], y = p[1];
      // 分牌滑动动画
      if (seat.split && seat.splitT) {
        var sp2 = Math.max(0, Math.min(1, (this.tick - seat.splitT) / 12));
        var bx = at[0] + (i - 1.5) * tw * 1.12;
        x = bx + (x - bx) * sp2;
      }
      // 选中后手上提 + 金环（玩家分牌阶段）
      var sel = isPlayer && this.phase === 'split' && this.splitSel.indexOf(i) >= 0;
      if (sel) y -= 10 * s;
      // 飞行：从牌匣滑入
      var fly = this.fx.find(function (f) {
        return f.kind === 'tilefly' && f.to === seatIdx && f.idx === i;
      });
      var alpha = 1;
      if (fly) {
        var fp = Math.max(0, Math.min(1, (this.tick - fly.start) / fly.dur));
        var tray = (this._posCache && this._posCache.tray) || [600, 300];
        x = tray[0] + (x - tray[0]) * fp;
        y = tray[1] + (y - tray[1]) * fp + Math.sin(Math.PI * fp) * 18;
        alpha = 0.35 + 0.65 * fp;
      }
      // 翻面：玩家发完翻上（发牌期间背面）；庄家/AI 开牌时翻上（动画完成后保持全宽）
      var up = false, sx = 1;
      if (isPlayer) {
        if (this.flipAt) {
          var fp2 = Math.max(0, Math.min(1, (this.tick - this.flipAt - i * 6) / 10));
          sx = fp2 >= 1 ? 1 : 1 - Math.abs(1 - 2 * fp2);
          up = fp2 >= 0.5;
        }
      } else {
        var flipAt = seatIdx === 4 ? this.dealer.flipAt : seat.splitT;
        if (flipAt) {
          var fp3 = Math.max(0, Math.min(1, (this.tick - flipAt) / 10));
          sx = fp3 >= 1 ? 1 : 1 - Math.abs(1 - 2 * fp3);
          up = fp3 >= 0.5;
        }
      }
      this._tile(c, x, y, tw, th, seat.tiles[i], up, sx, alpha);
      if (sel) {
        c.save();
        c.strokeStyle = 'rgba(255,210,120,.95)'; c.lineWidth = 2.4;
        c.shadowColor = '#ffc87a'; c.shadowBlur = 10;
        c.strokeRect(x - tw / 2 - 3, y - th / 2 - 3, tw + 6, th + 6);
        c.restore();
      }
      if (isPlayer) rects.push({ x: x, y: y, w: tw, h: th });
    }
    if (isPlayer && this._posCache) this._posCache.tileRects = rects;
    // 前/后手标签（玩家定牌后与已开牌的庄家）
    var showLbl = !!seat.split && (isPlayer || seatIdx === 4);
    if (showLbl) {
      this._label(c, at[0] - tw * 1.62, at[1] + th * 0.74, '前 ' + __pgLabel(seat.split ? seat.split.front : seat.tiles.slice(0, 2)), '#a8c8e0', s * (isPlayer ? 1.1 : 0.9));
      this._label(c, at[0] + tw * 1.62, at[1] + th * 0.74, '后 ' + __pgLabel(seat.split ? seat.split.back : seat.tiles.slice(2)), '#ffd98a', s * (isPlayer ? 1.1 : 0.9));
    }
    if (seatIdx === 4 && this.dealer.split && this.dealer.flipAt) {
      this._label(c, at[0], at[1] - th * 0.85, '庄家 · 后 ' + __pgLabel(this.dealer.split.back) + ' / 前 ' + __pgLabel(this.dealer.split.front), '#e0a8a0', s * 0.9);
    }
  }
  _pips(c, x0, y0, w, h, n) {
    var cx = x0 + w / 2, cy = y0 + h / 2;
    var R = Math.min(w, h) * 0.115;
    c.fillStyle = (n === 1 || n === 4) ? '#b23530' : '#26211a';
    var L = PG_PIPS[n] || [];
    for (var i = 0; i < L.length; i++) {
      c.beginPath();
      c.arc(cx + L[i][0] * w * 0.6, cy + L[i][1] * h * 0.54, R, 0, Math.PI * 2);
      c.fill();
    }
  }
  _tile(c, x, y, tw, th, tile, faceUp, sx, alpha) {
    c.save();
    if (alpha !== undefined && alpha < 1) c.globalAlpha = alpha;
    c.translate(x, y);
    if (sx !== undefined && sx < 1) c.scale(Math.max(0.04, sx), 1);
    var hw = tw / 2, hh = th / 2, r = Math.min(tw, th) * 0.1;
    c.beginPath();
    c.moveTo(-hw + r, -hh);
    c.arcTo(hw, -hh, hw, hh, r);
    c.arcTo(hw, hh, -hw, hh, r);
    c.arcTo(-hw, hh, -hw, -hh, r);
    c.arcTo(-hw, -hh, hw, -hh, r);
    c.closePath();
    if (faceUp && tile) {
      c.fillStyle = 'rgba(0,0,0,.4)';
      c.save(); c.translate(2, 3); c.fill(); c.restore();
      var bone = c.createLinearGradient(-hw, -hh, hw, hh);
      bone.addColorStop(0, '#f6edd4'); bone.addColorStop(1, '#d9caa4');
      c.fillStyle = bone; c.fill();
      c.strokeStyle = 'rgba(118,86,44,.8)'; c.lineWidth = 1; c.stroke();
      c.strokeStyle = 'rgba(118,86,44,.45)';
      c.beginPath(); c.moveTo(-hw + 2, 0); c.lineTo(hw - 2, 0); c.stroke();
      this._pips(c, -hw, -hh, tw, th / 2, tile.top);
      this._pips(c, -hw, 0, tw, th / 2, tile.bot);
    } else {
      c.fillStyle = 'rgba(0,0,0,.4)';
      c.save(); c.translate(2, 3); c.fill(); c.restore();
      var back = c.createLinearGradient(0, -hh, 0, hh);
      back.addColorStop(0, '#3f1219'); back.addColorStop(1, '#22090e');
      c.fillStyle = back; c.fill();
      c.strokeStyle = 'rgba(255,190,110,.5)'; c.lineWidth = 1; c.stroke();
      c.strokeStyle = 'rgba(255,190,110,.22)';
      c.strokeRect(-hw * 0.7, -hh * 0.82, hw * 1.4, hh * 1.64);
      c.beginPath(); c.arc(0, 0, Math.min(hw, hh * 0.5) * 0.5, 0, Math.PI * 2); c.stroke();
      c.beginPath(); c.arc(0, 0, Math.min(hw, hh * 0.5) * 0.26, 0, Math.PI * 2); c.stroke();
    }
    c.restore();
  }
  _label(c, x, y, text, color, s) {
    c.save();
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = '700 ' + Math.max(10, Math.round(11.5 * s)) + 'px monospace';
    c.fillStyle = color;
    c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 5;
    c.fillText(text, x, y);
    c.restore();
  }
  _handCenter(i, which) { // 座位 i 前/后手牌组中心（供徽章）
    var pc = this._posCache;
    if (!pc) return [400, 300];
    var at = i === 4 ? pc.dealer : (i === 0 ? pc.player : pc.seats[i]);
    if (!at) return [400, 300];
    var tw = i === 0 ? 52 : 36;
    return [at[0] + (which === 'back' ? 1 : -1) * tw * 1.62, at[1] - tw * 1.55 * 0.8];
  }
  _pt(ref) {
    var pc = this._posCache || { dealer: [400, 260], player: [400, 480], tray: [600, 260] };
    if (ref === 'dealer') return pc.dealer;
    if (ref && ref.indexOf('seat') === 0) {
      var i = parseInt(ref.slice(4), 10);
      return i === 0 ? pc.player : (pc.seats[i] || pc.player);
    }
    return pc.player;
  }
  _drawFx(c, s) {
    if (!this.fx.length) return;
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'chip') {
        var to = f.to === -1 ? self._pt('dealer') : self._pt('seat' + f.to);
        var from = self._pt('dealer');
        var x = from[0] + (to[0] - from[0]) * p;
        var y = from[1] + (to[1] - from[1]) * p - Math.sin(Math.PI * p) * 40;
        Casino.paint.chips(c, x, y, Math.max(10, Math.round((f.n || 20) / 2)));
      } else if (f.kind === 'text') {
        var at = self._pt(f.at);
        c.save();
        c.globalAlpha = p < 0.75 ? 1 : (1 - p) / 0.25;
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.font = '700 ' + (f.big ? 26 : 14) + 'px monospace';
        c.fillStyle = f.color || '#ffd98a';
        c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 6;
        c.fillText(f.text, at[0], at[1] - 120 * s - p * 30);
        c.restore();
      } else if (f.kind === 'badge') {
        var hc = self._handCenter(f.at, f.hand);
        var el = self.tick - f.start;
        var a = el < 0 ? 0 : Math.min(1, el / 8); // 淡入后常驻（下一局清空）
        c.save();
        c.globalAlpha = Math.max(0, a);
        var win = f.res === 'win';
        c.fillStyle = win ? 'rgba(60,40,8,.92)' : 'rgba(50,10,10,.92)';
        c.strokeStyle = win ? '#ffd98a' : '#e08080';
        c.lineWidth = 2;
        c.shadowColor = win ? '#ffc87a' : '#c05050'; c.shadowBlur = 10;
        c.beginPath(); c.arc(hc[0], hc[1], 15 * s, 0, Math.PI * 2); c.fill(); c.stroke();
        c.shadowBlur = 0;
        c.fillStyle = win ? '#ffd98a' : '#e08080';
        c.font = '700 ' + Math.round(15 * s) + 'px monospace';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText(win ? '胜' : '负', hc[0], hc[1]);
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

  // ---------- 帧驱动 ----------
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur + 30; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= this.shake.dur) this.shake = null;

    if (this.phase === 'bet' && this.bot && this.tick > 30) {
      var w0 = this.wallet.get();
      if (w0 >= 20) this.start(Math.min(100, w0));
      else this.wallet.bailout();
    }
    if (this.bot && this.phase === 'settle' && this.tick % 40 === 20) this._awaitBet();
    if (this.phase === 'deal') {
      var seq = Math.floor((this.tick - this.dealT - 16) / PG_DEAL_GAP);
      while (this._dealN <= seq && this._dealN < 20) {
        var si = this._dealN % 5; // 0 玩家 1..3 AI 4 庄家，轮流各 4 张
        var seat = si === 4 ? this.dealer : this.seats[si];
        seat.tiles.push(this.set.pop());
        this.fx.push({ kind: 'tilefly', to: si, idx: seat.tiles.length - 1, start: this.tick, dur: PG_DEAL_FLIGHT });
        if (this._dealN % 2 === 0) Casino.audio.play('card-place', 0.3);
        this._dealN++;
      }
      if (this._dealN >= 20 && this.tick - this.dealT > 16 + 20 * PG_DEAL_GAP + PG_DEAL_FLIGHT + 6) {
        this.phase = 'split';
        this.flipAt = this.tick; // 玩家四张依次翻开
        Casino.audio.play('card-place', 0.5);
        this.seats.forEach(function (st) {
          if (!st.human) st.thinkUntil = self.tick + (st.persona === 'tight' ? 150 : st.persona === 'bluff' ? 70 : 100) + Math.floor(Math.random() * 40);
        });
        this._msg('点两张牌作「后手」（大的一组）· 或用智能分牌');
        this._renderActions();
        this._syncClickLayer();
      }
      return;
    }
    if (this.phase === 'split' || this.phase === 'splitwait') {
      // AI 思考后自动分牌（两个阶段都要推进：玩家可能先定局）
      this.seats.forEach(function (st) {
        if (st.human || st.split) return;
        if (self.tick >= st.thinkUntil) {
          st.split = __pgSplitBy(st.tiles, st.persona === 'aggr' ? 'bold' : 'safe');
          st.splitT = self.tick;
        }
      });
      if (this.phase === 'split') {
        if (this.bot && this.tick - this.flipAt > 40 && !this._botSplitAt) this._botSplitAt = this.tick;
        if (this._botSplitAt && this.tick - this._botSplitAt > 24) {
          this._smartSplit();
          this._confirmSplit();
        }
        return;
      }
      var allDone = this.seats.every(function (st) { return !!st.split; });
      if (allDone && this.tick - this.waitT > 26) {
        this.phase = 'reveal';
        this.revealStart = this.tick;
        this.dealer.flipAt = this.tick;
        this.dealer.split = __pgSplitBest(this.dealer.tiles); // 庄家同时定牌
        Casino.audio.play('voice-open', 0.8);
        this._msg('庄家开牌…');
      }
      return;
    }
    if (this.phase === 'reveal') {
      var order = [1, 2, 3, 0]; // 闲家依次，玩家最后
      while (this._revealN < 4 && this.tick >= this.revealStart + 55 + this._revealN * PG_REVEAL_STEP) {
        this._processSeat(order[this._revealN]);
        this._revealN++;
        if (this._revealN >= 4 && !this.settleAt) this.settleAt = this.tick + 70;
      }
      if (this.settleAt && this.tick >= this.settleAt) this._settle();
      return;
    }
  }

  destroy() {
    this.destroyed = true;
    if (this.clickLayer) this.clickLayer.onclick = null;
  }
}

Casino.register('paigow', {
  name: '牌九 Pai Gow',
  icon: '🀄',
  desc: '大牌九 · 32 张骨牌分前/后两手对庄家 · 至尊宝赢局赔 2 倍',
  create: function (container, ctx) { return new CasinoPaigow(container, ctx); }
});

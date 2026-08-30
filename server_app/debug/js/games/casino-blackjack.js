// casino-blackjack.js — 算力赌坊 · 21 点 Blackjack
// 第一人称：荷官对面发牌，玩家 要牌/停牌/加倍；BJ 赔 3:2，庄家 17 停。
// 动画：靴牌逐张飞出、庄家暗牌翻开、筹码飞移、横幅+语音。全帧驱动。

// ---------- 引擎（纯函数，供测试） ----------
function __bjNewDeck() {
  var d = [];
  for (var s = 0; s < 4; s++) for (var r = 2; r <= 14; r++) d.push({ r: r, s: s });
  return d;
}
function __bjShuffle(d) {
  for (var i = d.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = d[i]; d[i] = d[j]; d[j] = t;
  }
  return d;
}
// 手牌点数：A 先按 11 算，爆了按 1 → {total, soft}
function __bjValue(hand) {
  var total = 0, aces = 0;
  hand.forEach(function (c) {
    if (c.r === 14) { aces++; total += 11; }
    else if (c.r >= 11) total += 10;
    else total += c.r;
  });
  while (total > 21 && aces > 0) { total -= 10; aces--; }
  return { total: total, soft: aces > 0 };
}
function __bjIsBJ(hand) { return hand.length === 2 && __bjValue(hand).total === 21; }
// 庄家规则：17 点或以上停牌（含软 17 停）
function __bjDealerShouldHit(hand) { return __bjValue(hand).total < 17; }
// 分牌：两手起手牌点数相同（含 A-A），且余额够再押一份
function __bjCanSplit(hand, walletChips, bet) {
  return !!hand && hand.length === 2 && hand[0].r === hand[1].r && walletChips >= bet;
}
// 保险：庄家明牌为 A 时可买（半注为限）；庄家天牌赔 2:1（返还 3×保费）
function __bjInsOffer(dealer) {
  return !!dealer && !!dealer[0] && dealer[0].r === 14;
}
function __bjInsStake(bet) {
  return Math.floor(bet / 2);
}
function __bjInsPayout(insAmt, dealerBJ) {
  return dealerBJ ? insAmt * 3 : 0;
}
// 迟投降：起手两张（未分牌）可投降，退回半注
function __bjCanSurrender(hand, splitDone) {
  return !!hand && hand.length === 2 && !splitDone;
}
function __bjSurrenderReturn(bet) {
  return Math.floor(bet / 2);
}

var BJ_BETS = [20, 50, 100, 200];
var BJ_DEAL_GAP = 16, BJ_DEAL_FLIGHT = 12;

// ---------- 21 点桌 ----------
class CasinoBlackjack {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.history = [];   // 战绩点 W/L/P
    this.banner = null;
    this.shake = null;
    this.flash = null;
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
  _fxText(text, color, big) {
    this.fx.push({ kind: 'text', at: 'center', text: text, color: color || '#ffd98a', start: this.tick, dur: 46, big: !!big });
  }
  _fxChips(to, n, delay) {
    this.fx.push({ kind: 'chip', from: 'pot', to: to, start: this.tick + (delay || 0), dur: 24, n: n });
  }
  _fxShake(amp, dur) { this.shake = { amp: amp, start: this.tick, dur: dur }; }

  _awaitBet() {
    this.phase = 'bet';
    this.deck = __bjShuffle(__bjNewDeck());
    this.hands = null;      // 分牌后为多手：[{..卡..}, bet, done, busted 挂在数组属性上]
    this.curHand = 0;
    this._splitDone = false;
    this._acesSplit = false;
    this.dealer = [];
    this.bet = 0;
    this.holeFlipT = 0;   // 清上一局残留（否则第二局暗牌开局就翻开）
    this._nextHitT = 0;
    this.dealSeq = 0;
    this.insAmt = 0;      // 保险侧注
    this._insDone = false;
    this._msg('选择下注额开始一局');
    Casino.audio.play('voice-bets', 0.7);
    this._renderActions();
  }

  start(bet) {
    if (!this.wallet.sub(bet)) { this._msg('算力不足'); return; }
    this.bet = bet;
    this.phase = 'deal';
    this.dealSeq = 0; // 0:玩家 1:庄家明 2:玩家 3:庄家暗
    this.dealT = this.tick;
    this._msg('发牌中…');
    Casino.audio.play('card-shuffle', 0.6);
    this._renderActions();
  }

  // ---------- 保险（庄家明牌 A） ----------
  takeInsurance() {
    if (this.phase !== 'insurance') return;
    var amt = __bjInsStake(this.bet);
    if (amt > 0 && this.wallet.sub(amt)) {
      this.insAmt = amt;
      Casino.audio.play('coins', 0.5);
      this._fxText('保险 ' + amt, '#a0c8e8');
    }
    this._afterInsurance(false);
  }
  declineInsurance() {
    if (this.phase !== 'insurance') return;
    this._afterInsurance(false);
  }
  _afterInsurance(fromDeal) {
    this._insDone = true;
    var pv0 = __bjValue(this.hands[0]);
    this.phase = 'player'; // 先进入玩家阶段，_stand 的守卫才放行
    if (__bjIsBJ(this.hands[0]) || __bjIsBJ(this.dealer)) {
      this._stand(true); // 天牌直接进亮牌
    } else if (!fromDeal) {
      this._msg('你的牌 ' + pv0.total + (pv0.soft ? '（软）' : '') + ' 点 · 要牌还是停牌？');
    }
    this._renderActions();
  }
  _dealOne(target) {
    var card = this.deck.pop();
    (target === 'd' ? this.dealer : target).push(card);
    Casino.audio.play('card-flick', 0.5);
    return card;
  }
  _dealTo(hand) { return this._dealOne(hand); }
  _cardT(target, idx) { // 第 target/idx 张牌的起始帧
    return this.dealT + 20 + idx * BJ_DEAL_GAP;
  }

  // ---------- 玩家动作（分牌后逐手操作） ----------
  split() {
    var h = this.hands && this.hands[this.curHand];
    if (this.phase !== 'player' || !__bjCanSplit(h, this.wallet.get(), this.bet)) return;
    if (!this.wallet.sub(this.bet)) { this._msg('算力不足，不能分牌'); return; }
    this._splitDone = true;
    var isAces = h[0].r === 14;
    this._acesSplit = isAces;
    h.bet = h.bet || this.bet;
    var h2 = [h.pop()];
    h2.bet = this.bet;
    this.hands.push(h2);
    this._fxText('分牌 SPLIT', '#ffc87a');
    Casino.audio.play('voice-double', 0.6);
    // 第一手立即补一张
    this._dealTo(h);
    this.fx.push({ kind: 'dealcard', to: 'h0', idx: h.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
    var v = __bjValue(h);
    if (isAces || v.total === 21) { // 分 A 各补一张即停；补成 21 也直接停
      h.done = true;
      this._nextHand();
    } else {
      this._msg('第 1 手 ' + v.total + (v.soft ? '（软）' : '') + ' 点 · 要牌还是停牌？');
    }
    this._renderActions();
  }
  hit() {
    if (this.phase !== 'player') return;
    var h = this.hands[this.curHand];
    Casino.audio.play('voice-hit', 0.6);
    this._dealTo(h);
    this.fx.push({ kind: 'dealcard', to: 'h' + this.curHand, idx: h.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
    var v = __bjValue(h);
    if (v.total > 21) {
      this._msg('第 ' + (this.curHand + 1) + ' 手爆牌！' + v.total + ' 点');
      this._fxText('爆牌 BUST', '#ff6a5a', true);
      Casino.audio.play('voice-lose', 0.8);
      h.busted = true;
      h.done = true;
      if (this.curHand < this.hands.length - 1) this._nextHand();
      else this._toDealer();
    } else if (v.total === 21) {
      this._stand(true);
    } else {
      this._msg('第 ' + (this.curHand + 1) + ' 手 ' + v.total + (v.soft ? '（软）' : '') + ' 点');
    }
    this._renderActions();
  }
  stand() { this._stand(false); }
  _nextHand() {
    this.curHand++;
    var h = this.hands[this.curHand];
    this._dealTo(h);
    this.fx.push({ kind: 'dealcard', to: 'h' + this.curHand, idx: h.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
    var v = __bjValue(h);
    if (this._acesSplit || v.total === 21) {
      h.done = true;
      if (this.curHand < this.hands.length - 1) this._nextHand();
      else this._toDealer();
      return;
    }
    this._msg('第 ' + (this.curHand + 1) + ' 手 ' + v.total + (v.soft ? '（软）' : '') + ' 点 · 要牌还是停牌？');
  }
  // 迟投降：弃掉当前手，退回半注（只在起手两张且未分牌时可用）
  surrender() {
    if (this.phase !== 'player') return;
    var h = this.hands[this.curHand];
    if (!__bjCanSurrender(h, this._splitDone)) return;
    h.surrendered = true;
    h.done = true;
    Casino.audio.play('voice-fold', 0.6);
    this._fxText('投降 退半注', '#a0c8e8');
    if (this.curHand < this.hands.length - 1) { this._nextHand(); return; }
    this._toDealer();
  }
  _toDealer() {
    this.phase = 'dealer';
    Casino.audio.play('voice-stand', 0.6);
    this.holeFlipT = this.tick;
    this._msg('庄家亮牌…');
    this._renderActions();
  }
  _stand(auto) {
    if (this.phase !== 'player') return;
    var h = this.hands[this.curHand];
    h.done = true;
    if (this.curHand < this.hands.length - 1) { this._nextHand(); return; }
    this._toDealer();
  }
  double() {
    if (this.phase !== 'player') return;
    var h = this.hands[this.curHand];
    if (h.length !== 2) return;
    if (!this.wallet.sub(h.bet || this.bet)) { this._msg('算力不足，不能加倍'); return; }
    h.bet = (h.bet || this.bet) * 2;
    Casino.audio.play('voice-double-down', 0.7);
    Casino.audio.play('coins', 0.5);
    this._fxText('加倍 ×2', '#ffc87a');
    this._dealTo(h);
    this.fx.push({ kind: 'dealcard', to: 'h' + this.curHand, idx: h.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
    var v = __bjValue(h);
    if (v.total > 21) {
      this._msg('加倍后爆牌 ' + v.total);
      this._fxText('爆牌 BUST', '#ff6a5a', true);
      Casino.audio.play('voice-lose', 0.8);
      h.busted = true;
      h.done = true;
      if (this.curHand < this.hands.length - 1) this._nextHand();
      else this._toDealer();
    } else {
      this._stand(true);
    }
    this._renderActions();
  }

  _settle(mode) {
    this.phase = 'settle';
    var self = this;
    var dv = __bjValue(this.dealer);
    var payout = 0, staked = 0, results = [];
    this.hands.forEach(function (h) {
      var bet = h.bet || self.bet;
      staked += bet;
      var pv = __bjValue(h).total;
      var isBJ = !self._splitDone && __bjIsBJ(h); // 分牌后的 21 不算 Blackjack
      var result; // win | lose | push | bj | bust | surrender
      if (h.surrendered) result = 'surrender';
      else if (h.busted) result = 'bust';
      else if (isBJ && !__bjIsBJ(self.dealer)) result = 'bj';
      else if (__bjIsBJ(self.dealer) && !isBJ) result = 'lose';
      else if (dv.total > 21 || pv > dv.total) result = 'win';
      else if (pv < dv.total) result = 'lose';
      else result = 'push';
      if (result === 'bj') payout += Math.floor(bet * 2.5);
      else if (result === 'win') payout += bet * 2;
      else if (result === 'push') payout += bet;
      else if (result === 'surrender') payout += __bjSurrenderReturn(bet); // 退半注
      results.push(result);
    });
    // 保险结算（庄家天牌赔 2:1，计入净额）
    var ins0 = this.insAmt;
    var insRet = ins0 > 0 ? __bjInsPayout(ins0, __bjIsBJ(this.dealer)) : 0;
    this.insAmt = 0;
    if (insRet > 0) payout += insRet;
    if (ins0 > 0) staked += ins0;
    var insNote = ins0 > 0 ? (insRet > 0 ? ' · 保险中 +' + (insRet - ins0) : ' · 保险失效') : '';
    if (payout > 0) {
      this.wallet.add(payout);
      for (var k = 0; k < 3; k++) this._fxChips('player', payout / 3, k * 5);
    }
    var net = payout - staked;
    var r0 = results[0];
    var voices = { bj: 'voice-blackjack', win: 'voice-win', push: 'voice-push', lose: 'voice-lose', bust: 'voice-lose' };
    var voice = net > 0 ? (r0 === 'bj' ? 'voice-blackjack' : 'voice-win') : net === 0 ? 'voice-push' : 'voice-lose';
    var bannerText;
    if (this.hands.length === 1) {
      var texts = {
        bj: ['Blackjack！赔 3:2，赢 ' + (payout - staked), '#ffd98a'],
        win: ['你赢了 ' + (payout - staked) + '！', '#ffd98a'],
        push: ['平局，退回下注', '#a0c8e8'],
        surrender: ['投降 · 退回半注 ' + payout, '#a0c8e8'],
        lose: ['庄家胜（' + (dv.total > 21 ? '庄爆 ' + dv.total : dv.total + ' 比 ' + __bjValue(this.hands[0]).total) + '）', '#e08080'],
        bust: ['你爆牌，输 ' + staked, '#e08080']
      };
      var tx = texts[r0];
      this._msg(tx[0] + insNote);
      this.banner = { text: r0 === 'bj' ? 'BLACKJACK ×1.5' : r0 === 'win' ? '你赢了 +' + (payout - staked) : r0 === 'push' ? 'PUSH 平局' : r0 === 'surrender' ? '投降 退半注' : r0 === 'bust' ? 'BUST 爆牌' : '庄家胜', color: tx[1], start: this.tick, dur: 90 };
      this._fxText(r0 === 'bj' ? 'Blackjack!' : r0 === 'win' ? 'WIN' : r0 === 'push' || r0 === 'surrender' ? 'HALF BACK' : 'LOSE', tx[1], true);
    } else {
      var col = net > 0 ? '#ffd98a' : net === 0 ? '#a0c8e8' : '#e08080';
      this._msg('两手 ' + results.join('/') + ' · 净 ' + (net >= 0 ? '+' : '') + net + insNote);
      this.banner = { text: net > 0 ? '分牌净赢 +' + net : net === 0 ? '分牌打平' : '分牌净输 ' + net, color: col, start: this.tick, dur: 90 };
      this._fxText(net > 0 ? 'WIN' : net === 0 ? 'PUSH' : 'LOSE', col, true);
    }
    Casino.audio.play(voice, 0.85);
    if (net > 0) { this._fxShake(7, 14); Casino.paint && 0; }
    this.result = this.hands.length === 1 ? r0 : (net > 0 ? 'win' : net === 0 ? 'push' : 'lose');
    this.splitNet = this.hands.length > 1 ? net : null;
    this.history.push(net > 0 ? 'W' : net === 0 ? 'P' : 'L');
    if (this.history.length > 14) this.history.shift();
    Casino.stats.record('blackjack', net > 0 ? 'W' : net === 0 ? 'P' : 'L');
    this._renderActions();
  }
  _againBtn() {
    var self = this;
    var b = this._el('button', 'padding:10px 30px;border-radius:8px;border:1px solid #ffc87a;background:rgba(50,28,10,.92);color:#ffc87a;cursor:pointer;font-family:inherit;font-size:14px;font-weight:700', '🔄 再来一局');
    b.onclick = function () { self._awaitBet(); };
    this.againBtn = b;
    return b;
  }

  _renderActions() {
    var self = this;
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b>' + (this.bet ? ' · 下注 <b>' + this.bet + '</b>' : '') + '</span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet') {
      if (this.wallet.get() < (BJ_BETS[0] || 20)) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f');
        if (!this.wallet.canBailout()) { bb.disabled = true; bb.style.opacity = .5; bb.style.cursor = 'not-allowed'; }
        this.actEl.appendChild(bb);
        return;
      }
      BJ_BETS.forEach(function (b) {
        if (self.wallet.get() >= b) self.actEl.appendChild(mk('下注 ' + b, function () { self.start(b); }, '#ffc87a'));
      });
      return;
    }
    if (this.phase === 'insurance') {
      var ins2 = __bjInsStake(this.bet);
      this.actEl.appendChild(mk('🛡 买保险 ' + ins2 + '（天牌赔 2:1）', function () { self.takeInsurance(); }, '#a0c8e8'));
      this.actEl.appendChild(mk('不买保险', function () { self.declineInsurance(); }, '#8a7ba0'));
      return;
    }
    if (this.phase === 'player') {
      var h0 = this.hands[this.curHand];
      this.actEl.appendChild(mk('要牌', function () { self.hit(); }, '#8fce8f'));
      this.actEl.appendChild(mk('停牌', function () { self.stand(); }, '#a0c8e8'));
      if (__bjCanSplit(h0, this.wallet.get(), this.bet) && !this._splitDone) {
        this.actEl.appendChild(mk('⑧ 分牌', function () { self.split(); }, '#b070e0'));
      }
      if (h0.length === 2 && this.wallet.get() >= (h0.bet || this.bet)) {
        this.actEl.appendChild(mk('加倍 ×2', function () { self.double(); }, '#ff9f5a'));
      }
      if (__bjCanSurrender(h0, this._splitDone)) {
        this.actEl.appendChild(mk('🏳 投降退半', function () { self.surrender(); }, '#8a7ba0'));
      }
      return;
    }
    if (this.phase === 'settle') {
      this.actEl.appendChild(this._againBtn());
    }
  }

  // ---------- 场景 ----------
  renderScene(c, w, h, t) {
    if (this.destroyed) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    this._posCache = {
      center: [w / 2, h * 0.60],
      pot: [w / 2, h * 0.62],
      player: [w / 2, h * 0.80],
      shoe: [w * 0.68, h * 0.50],
      dealerCards: [w / 2, h * 0.545],
      playerCards: [w / 2, h * 0.78]
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
    // 荷官（对面中央，圆顶礼帽）
    P.seat(c, w / 2, h * 0.36, t, {
      name: '荷官', color: '#c8a050', persona: 'tight', scale: s * 1.25,
      active: false, chipsLabel: ''
    });
    // 靴牌（右侧牌靴）
    this._shoe(c, w, h, s);
    // 庄家手牌
    this._handRow(c, this.dealer, this._posCache.dealerCards, w, s, this.phase === 'dealer' || this.phase === 'settle', 'dealer');
    // 玩家手牌（分牌后两手并排，当前手下方金线指示）
    if (this.hands && this.hands.length) {
      var two = this.hands.length > 1;
      var base = this._posCache.playerCards;
      for (var hi = 0; hi < this.hands.length; hi++) {
        var off = two ? (hi === 0 ? -w * 0.095 : w * 0.095) : 0;
        var at2 = [base[0] + off, base[1] - (two ? 10 * s : 0)];
        this._handRow(c, this.hands[hi], at2, w * (two ? 0.82 : 1), s, true, 'h' + hi);
        var hv = __bjValue(this.hands[hi]);
        var lbl = (two ? '手' + (hi + 1) + ' ' : '你 ') + (this.hands[hi].busted ? '爆' : hv.total + (hv.soft && hv.total < 21 ? '软' : '')) +
          ' · 押 ' + (this.hands[hi].bet || this.bet);
        this._label(c, at2[0], at2[1] + 62 * s, lbl, this.phase === 'player' && this.curHand === hi ? '#ffd98a' : '#8fce8f', s);
        if (two && this.phase === 'player' && this.curHand === hi) {
          c.save();
          c.strokeStyle = 'rgba(255,210,120,.9)'; c.lineWidth = 2.4;
          c.shadowColor = '#ffc87a'; c.shadowBlur = 8;
          c.beginPath(); c.moveTo(at2[0] - 44 * s, at2[1] + 46 * s); c.lineTo(at2[0] + 44 * s, at2[1] + 46 * s); c.stroke();
          c.restore();
        }
      }
    }
    // 点数标签（庄家）
    if (this.dealer.length) {
      var dv = __bjValue(this.dealer);
      var showDv = (this.phase === 'dealer' || this.phase === 'settle') ? dv.total : __bjValue([this.dealer[0]]).total + ' + ?';
      this._label(c, w / 2, h * 0.545 + 46 * s, '庄家 ' + showDv, '#e0a8a0', s);
    }
    this._drawFx(c, s);
    c.restore();
    this._drawBanner(c, w, h);
  }
  _shoe(c, w, h, s) {
    var x = w * 0.68, y = h * 0.50;
    c.save();
    var g = c.createLinearGradient(x, y - 26 * s, x, y + 26 * s);
    g.addColorStop(0, '#4a2a14'); g.addColorStop(1, '#1c0e06');
    c.fillStyle = g;
    c.beginPath();
    c.moveTo(x - 30 * s, y - 26 * s); c.lineTo(x + 26 * s, y - 26 * s);
    c.lineTo(x + 30 * s, y + 26 * s); c.lineTo(x - 26 * s, y + 26 * s);
    c.closePath(); c.fill();
    c.strokeStyle = 'rgba(255,200,120,.4)'; c.lineWidth = 1.5; c.stroke();
    c.restore();
  }
  _handRow(c, hand, at, w, s, faceUpAll, fxTo) {
    if (!hand || !hand.length) return;
    var cw = Math.max(34, Math.min(64, w * 0.052)), chh = cw * 1.45;
    var gap = cw * 0.72;
    var startX = at[0] - (hand.length - 1) * gap / 2;
    for (var i = 0; i < hand.length; i++) {
      var x = startX + i * gap;
      var card = hand[i];
      // 新牌 BJ_DEAL_FLIGHT 帧内从牌靴飞来（fx 记录）
      var fly = this.fx.find(function (f) {
        return f.kind === 'dealcard' && f.to === fxTo && f.idx === i;
      });
      var prog = fly ? Math.max(0, Math.min(1, (this.tick - fly.start) / fly.dur)) : 1;
      var shoe = this._posCache.shoe;
      var px = shoe[0] + (x - shoe[0]) * prog;
      var py = shoe[1] + (at[1] - shoe[1]) * prog;
      var faceUp = faceUpAll || fxTo !== 'dealer';
      // 庄家暗牌翻开动画（dealer/settle 阶段）
      var flip = 1;
      if (fxTo === 'dealer' && i === 1 && this.holeFlipT) {
        flip = Math.max(0, Math.min(1, (this.tick - this.holeFlipT - 20) / 10));
        faceUp = flip >= 0.5;
      }
      c.save();
      c.translate(px, py);
      if (flip < 1) {
        var sx = 1 - Math.abs(1 - 2 * flip);
        if (sx > 0.05) Casino.paint.card(c, 0, 0, cw * Math.max(0.05, sx), chh, card, faceUp, 0.5 + 0.5 * prog);
      } else {
        Casino.paint.card(c, 0, 0, cw, chh, card, faceUp, 0.5 + 0.5 * prog);
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
  _drawFx(c, s) {
    if (!this.fx.length) return;
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'chip') {
        var to = self._pt(f.to);
        var from = self._pt('pot');
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
      }
    });
  }
  _pt(ref) {
    var pc = this._posCache || { center: [400, 360], pot: [400, 370], player: [400, 480], shoe: [544, 300] };
    return pc[ref] || pc.center;
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
  // bot 模式自动下注+基本策略（自动化测试/浸泡用；真人不受影响）
  _botStep() {
    if (this.phase === 'bet') {
      if (this.tick < 30 || this.tick % 50 !== 30) return;
      var w = this.wallet.get();
      if (w >= 20) this.start(Math.min(100, Math.max(20, w)));
      else this.wallet.bailout();
      return;
    }
    if (this.phase === 'insurance' && this.tick % 25 === 12) {
      if (Math.random() < 0.35) this.takeInsurance();
      else this.declineInsurance();
      return;
    }
    if (this.phase === 'player' && this.tick % 25 === 12) {
      var hb = this.hands[this.curHand];
      var bv = __bjValue(hb);
      if (__bjCanSplit(hb, this.wallet.get(), this.bet) && Math.random() < 0.8) this.split();
      else if (bv.total === 16 && !bv.soft && [9, 10, 13, 14].indexOf(this.dealer[0].r) >= 0 && __bjCanSurrender(hb, this._splitDone)) this.surrender(); // 基本策略：16 硬牌 vs 9/10/A 投降
      else if (bv.total < 17) this.hit();
      else this.stand();
    }
  }
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.bot && (this.phase === 'bet' || this.phase === 'player' || this.phase === 'insurance')) this._botStep();
    if (this.bot && this.phase === 'settle' && this.tick % 40 === 20) this._awaitBet();
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur + 20; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= this.shake.dur) this.shake = null;

    if (this.phase === 'deal') {
      // 发牌序列：玩家→庄家明→玩家→庄家暗，帧间隔发
      var seq = Math.floor((this.tick - this.dealT - 20) / BJ_DEAL_GAP);
      if (!this.hands) this.hands = [[]];
      while (this.dealSeq <= seq && this.dealSeq < 4) {
        if (this.dealSeq % 2 === 0) {
          this._dealTo(this.hands[0]);
          this.fx.push({ kind: 'dealcard', to: 'h0', idx: this.hands[0].length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
        } else {
          this._dealOne('d');
          this.fx.push({ kind: 'dealcard', to: 'dealer', idx: this.dealer.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
        }
        this.dealSeq++;
      }
      if (this.dealSeq >= 4 && this.tick - this.dealT > 20 + 4 * BJ_DEAL_GAP + BJ_DEAL_FLIGHT) {
        this.hands[0].bet = this.bet;
        var pv0 = __bjValue(this.hands[0]);
        // 保险：庄家明牌 A → 先问保险，再进玩家阶段/天牌亮牌
        if (__bjInsOffer(this.dealer) && !this._insDone) {
          this.phase = 'insurance';
          this._msg('庄家亮出 A · 买保险吗？（最多 ' + __bjInsStake(this.bet) + '，庄家天牌赔 2:1）');
          Casino.say('庄家王牌，买保险吗', { pitch: 0.7 });
          this._renderActions();
          return;
        }
        this._afterInsurance(true);
        return;
      }
      return;
    }
    if (this.phase === 'dealer') {
      // 亮暗牌后按规则补牌（每张间隔 34 帧，有节奏）；玩家全爆则不补
      var allBust = this.hands.every(function (h) { return h.busted || h.surrendered; });
      var ready = this.tick - this.holeFlipT > 34;
      if (ready && !allBust && __bjDealerShouldHit(this.dealer)) {
        if (!this._nextHitT) this._nextHitT = this.tick;
        if (this.tick - this._nextHitT >= 34) {
          this._dealOne('d');
          this.fx.push({ kind: 'dealcard', to: 'dealer', idx: this.dealer.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
          this._nextHitT = this.tick;
          this._msg('庄家补牌… ' + __bjValue(this.dealer).total + ' 点');
        }
      } else if (ready && (allBust || !__bjDealerShouldHit(this.dealer))) {
        this._nextHitT = 0;
        this._settle('normal');
      }
      return;
    }
  }

  destroy() { this.destroyed = true; }
}

Casino.register('blackjack', {
  name: '21 点 Blackjack',
  icon: '🂿',
  desc: '对抗荷官 · 要牌/停牌/加倍 · Blackjack 赔 3:2，庄家 17 停牌',
  create: function (container, ctx) { return new CasinoBlackjack(container, ctx); }
});

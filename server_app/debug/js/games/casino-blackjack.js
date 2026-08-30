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
    this.player = [];
    this.dealer = [];
    this.bet = 0;
    this.holeFlipT = 0;   // 清上一局残留（否则第二局暗牌开局就翻开）
    this._nextHitT = 0;
    this.dealSeq = 0;
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

  _dealOne(target) {
    var card = this.deck.pop();
    (target === 'p' ? this.player : this.dealer).push(card);
    Casino.audio.play('card-flick', 0.5);
    return card;
  }
  _cardT(target, idx) { // 第 target/idx 张牌的起始帧
    return this.dealT + 20 + idx * BJ_DEAL_GAP;
  }

  // 玩家动作
  hit() {
    if (this.phase !== 'player') return;
    this._dealOne('p');
    Casino.audio.play('voice-hit', 0.6);
    this.fx.push({ kind: 'dealcard', to: 'player', idx: this.player.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
    var v = __bjValue(this.player);
    if (v.total > 21) {
      this._msg('爆牌！' + v.total + ' 点');
      this._fxText('爆牌 BUST', '#ff6a5a', true);
      Casino.audio.play('voice-lose', 0.8);
      this._settle('bust');
    } else if (v.total === 21) {
      this._stand(true);
    } else {
      this._msg('你的牌 ' + v.total + (v.soft ? '（软）' : '') + ' 点');
    }
    this._renderActions();
  }
  stand() { this._stand(false); }
  _stand(auto) {
    if (this.phase !== 'player') return;
    this.phase = 'dealer';
    Casino.audio.play('voice-stand', 0.6);
    this.holeFlipT = this.tick;
    this._msg('庄家亮牌…');
    this._renderActions();
  }
  double() {
    if (this.phase !== 'player' || this.player.length !== 2) return;
    if (!this.wallet.sub(this.bet)) { this._msg('算力不足，不能加倍'); return; }
    this.bet *= 2;
    Casino.audio.play('voice-double-down', 0.7);
    Casino.audio.play('coins', 0.5);
    this._fxText('加倍 ×2', '#ffc87a');
    this._dealOne('p');
    this.fx.push({ kind: 'dealcard', to: 'player', idx: this.player.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
    var v = __bjValue(this.player);
    if (v.total > 21) {
      this._msg('加倍后爆牌 ' + v.total);
      this._fxText('爆牌 BUST', '#ff6a5a', true);
      Casino.audio.play('voice-lose', 0.8);
      this._settle('bust');
    } else {
      this._stand(true);
    }
    this._renderActions();
  }

  _settle(mode) {
    this.phase = 'settle';
    var dv = __bjValue(this.dealer);
    var pv = __bjValue(this.player);
    var result; // win | lose | push | bj | bust
    if (mode === 'bust') result = 'bust';
    else if (__bjIsBJ(this.player) && !__bjIsBJ(this.dealer)) result = 'bj';
    else if (__bjIsBJ(this.dealer) && !__bjIsBJ(this.player)) result = 'lose';
    else if (dv.total > 21 || pv.total > dv.total) result = 'win';
    else if (pv.total < dv.total) result = 'lose';
    else result = 'push';
    var payout = 0;
    if (result === 'bj') payout = Math.floor(this.bet * 2.5);
    else if (result === 'win') payout = this.bet * 2;
    else if (result === 'push') payout = this.bet;
    if (payout > 0) {
      this.wallet.add(payout);
      for (var k = 0; k < 3; k++) this._fxChips('player', payout / 3, k * 5);
    }
    var texts = {
      bj: ['Blackjack！赔 3:2，赢 ' + payout, '#ffd98a', 'voice-blackjack'],
      win: ['你赢了 ' + this.bet + '！', '#ffd98a', 'voice-win'],
      push: ['平局，退回下注', '#a0c8e8', 'voice-push'],
      lose: ['庄家胜（' + (dv.total > 21 ? '庄爆 ' + dv.total : dv.total + ' 比 ' + pv.total) + '）', '#e08080', 'voice-lose'],
      bust: ['你爆牌，输 ' + this.bet, '#e08080', 'voice-lose']
    };
    var tx = texts[result];
    this._msg(tx[0]);
    this.banner = { text: result === 'bj' ? 'BLACKJACK ×1.5' : result === 'win' ? '你赢了 +' + this.bet : result === 'push' ? 'PUSH 平局' : result === 'bust' ? 'BUST 爆牌' : '庄家胜', color: tx[1], start: this.tick, dur: 90 };
    this._fxText(result === 'bj' ? 'Blackjack!' : result === 'win' ? 'WIN' : result === 'push' ? 'PUSH' : 'LOSE', tx[1], true);
    Casino.audio.play(tx[2], 0.85);
    if (result === 'bj' || result === 'win') { this._fxShake(7, 14); Casino.paint && 0; }
    this.result = result;
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
    if (this.phase === 'player') {
      this.actEl.appendChild(mk('要牌', function () { self.hit(); }, '#8fce8f'));
      this.actEl.appendChild(mk('停牌', function () { self.stand(); }, '#a0c8e8'));
      if (this.player.length === 2 && this.wallet.get() >= this.bet) {
        this.actEl.appendChild(mk('加倍 ×2', function () { self.double(); }, '#ff9f5a'));
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
    // 荷官（对面中央，圆顶礼帽）
    P.seat(c, w / 2, h * 0.36, t, {
      name: '荷官', color: '#c8a050', persona: 'tight', scale: s * 1.25,
      active: false, chipsLabel: ''
    });
    // 靴牌（右侧牌靴）
    this._shoe(c, w, h, s);
    // 庄家手牌
    this._handRow(c, this.dealer, this._posCache.dealerCards, w, s, this.phase === 'dealer' || this.phase === 'settle', this._cardT('d', 0) < 0);
    // 玩家手牌
    this._handRow(c, this.player, this._posCache.playerCards, w, s, true);
    // 点数标签
    if (this.dealer.length) {
      var dv = __bjValue(this.dealer);
      var showDv = (this.phase === 'dealer' || this.phase === 'settle') ? dv.total : __bjValue([this.dealer[0]]).total + ' + ?';
      this._label(c, w / 2, h * 0.545 + 46 * s, '庄家 ' + showDv, '#e0a8a0', s);
    }
    if (this.player.length) {
      var pv = __bjValue(this.player);
      this._label(c, w / 2, h * 0.78 + 62 * s, '你 ' + pv.total + (pv.soft && pv.total < 21 ? '（软）' : '') + (this.bet ? ' · 押 ' + this.bet : ''), '#8fce8f', s);
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
  _handRow(c, hand, at, w, s, faceUpAll) {
    if (!hand.length) return;
    var cw = Math.max(34, Math.min(64, w * 0.052)), chh = cw * 1.45;
    var gap = cw * 0.72;
    var isPlayer = hand === this.player;
    var startX = at[0] - (hand.length - 1) * gap / 2;
    for (var i = 0; i < hand.length; i++) {
      var x = startX + i * gap;
      var card = hand[i];
      // 新牌 12 帧内从牌靴飞来（fx 记录）
      var fly = this.fx.find(function (f) {
        return f.kind === 'dealcard' && f.to === (isPlayer ? 'player' : 'dealer') && f.idx === i;
      });
      var prog = fly ? Math.max(0, Math.min(1, (this.tick - fly.start) / fly.dur)) : 1;
      var shoe = this._posCache.shoe;
      var px = shoe[0] + (x - shoe[0]) * prog;
      var py = shoe[1] + (at[1] - shoe[1]) * prog;
      var faceUp = faceUpAll || isPlayer;
      // 庄家暗牌翻开动画（dealer/settle 阶段）
      var flip = 1;
      if (!isPlayer && i === 1 && this.holeFlipT) {
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
    if (this.phase === 'player' && this.tick % 25 === 12) {
      if (__bjValue(this.player).total < 17) this.hit();
      else this.stand();
    }
  }
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.bot && (this.phase === 'bet' || this.phase === 'player')) this._botStep();
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur + 20; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= this.shake.dur) this.shake = null;

    if (this.phase === 'deal') {
      // 发牌序列：玩家→庄家明→玩家→庄家暗，帧间隔发
      var seq = Math.floor((this.tick - this.dealT - 20) / BJ_DEAL_GAP);
      while (this.dealSeq <= seq && this.dealSeq < 4) {
        this._dealOne(this.dealSeq % 2 === 0 ? 'p' : 'd');
        this.fx.push({ kind: 'dealcard', to: this.dealSeq % 2 === 0 ? 'player' : 'dealer', idx: Math.floor(this.dealSeq / 2), start: this.tick, dur: BJ_DEAL_FLIGHT });
        this.dealSeq++;
      }
      if (this.dealSeq >= 4 && this.tick - this.dealT > 20 + 4 * BJ_DEAL_GAP + BJ_DEAL_FLIGHT) {
        var pv = __bjValue(this.player);
        this.phase = 'player'; // 先进入玩家阶段，_stand 的守卫才放行
        if (__bjIsBJ(this.player) || __bjIsBJ(this.dealer)) {
          this._stand(true); // 天牌直接进亮牌
        } else {
          this._msg('你的牌 ' + pv.total + (pv.soft ? '（软）' : '') + ' 点 · 要牌还是停牌？');
        }
        this._renderActions();
      }
      return;
    }
    if (this.phase === 'dealer') {
      // 亮暗牌后按规则补牌（每张间隔 34 帧，有节奏）
      var ready = this.tick - this.holeFlipT > 34;
      if (ready && __bjDealerShouldHit(this.dealer)) {
        if (!this._nextHitT) this._nextHitT = this.tick;
        if (this.tick - this._nextHitT >= 34) {
          this._dealOne('d');
          this.fx.push({ kind: 'dealcard', to: 'dealer', idx: this.dealer.length - 1, start: this.tick, dur: BJ_DEAL_FLIGHT });
          this._nextHitT = this.tick;
          this._msg('庄家补牌… ' + __bjValue(this.dealer).total + ' 点');
        }
      } else if (ready && !__bjDealerShouldHit(this.dealer)) {
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

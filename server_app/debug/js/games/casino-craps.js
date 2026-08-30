// casino-craps.js — 算力赌坊 · Craps 双骰桌
// Pass Line：come-out 7/11 即赢、2/3/12 即输、其余设点；掷出点数赢、7 输。
// Don't Pass（_bar 12）：come-out 2/3 赢、12 平、7/11 输；设点后 7 赢、点数输。
// Field（一掷性）：2/12 赔 2:1、3/4/9/10/11 赔 1:1、5/6/7/8 输。
// 动画：两颗骰子从桌右端掷出（抛物线翻滚+弹跳落定）→ 荷官语音报点 → puck ON/OFF。

// ---------- 引擎（纯函数，供测试） ----------
function __crapsRoll(rng) {
  var r = rng || Math.random;
  var a = 1 + Math.floor(r() * 6), b = 1 + Math.floor(r() * 6);
  return { dice: [a, b], total: a + b };
}
// come-out 阶段 pass line 结果：'win' | 'lose' | 'point:n'
function __crapsComeOut(total) {
  if (total === 7 || total === 11) return 'win';
  if (total === 2 || total === 3 || total === 12) return 'lose';
  return 'point:' + total;
}
// 设点后：'win' | 'lose' | 'roll'（继续掷）
function __crapsPointRoll(point, total) {
  if (total === point) return 'win';
  if (total === 7) return 'lose';
  return 'roll';
}
// don't pass come-out：'win' | 'push'(12) | 'lose' | 'point'
function __crapsDontComeOut(total) {
  if (total === 2 || total === 3) return 'win';
  if (total === 12) return 'push';
  if (total === 7 || total === 11) return 'lose';
  return 'point';
}
// don't pass 设点后：7 赢、点数输、其余继续
function __crapsDontPoint(point, total) {
  if (total === 7) return 'win';
  if (total === point) return 'lose';
  return 'roll';
}
// field 返还倍数（0=输）
function __crapsField(total) {
  if (total === 2 || total === 12) return 3;
  if (total === 3 || total === 4 || total === 9 || total === 10 || total === 11) return 2;
  return 0;
}

var CR_BETS = [20, 50, 100];
var CR_ROLL_TICKS = 110;

// ---------- Craps 桌 ----------
class CasinoCraps {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.banner = null;
    this.shake = 0;
    this.chipAmt = CR_BETS[0];
    this.point = null;        // 当前点数（null = come-out 阶段）
    this.bets = { pass: 0, dont: 0, field: 0 };
    this.history = [];
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

  _awaitBet() {
    this.phase = 'bet';
    this.roll = null;
    this._msg(this.point ? '点数 ' + this.point + ' 已设 · 可加注再掷' : 'Come-out 下注 → 掷骰');
    if (!this.point) Casino.audio.play('voice-come-out', 0.7);
    this._renderActions();
  }
  place(zone) {
    if (this.phase !== 'bet') return;
    if (!this.wallet.sub(this.chipAmt)) { this._msg('算力不足'); return; }
    this.bets[zone] += this.chipAmt;
    Casino.audio.play('coins', 0.4);
    var names = { pass: 'Pass Line', dont: 'Don\'t Pass', field: 'Field' };
    this._msg(names[zone] + ' 押 ' + this.bets[zone] + (this.point ? '（点数 ' + this.point + '）' : ''));
    this._renderActions();
  }
  rollNow() {
    if (this.phase !== 'bet') return;
    var total = this.bets.pass + this.bets.dont + this.bets.field;
    if (total === 0) { this._msg('先下注再掷'); return; }
    this.phase = 'roll';
    this.rollT = this.tick;
    this.roll = __crapsRoll();
    this._msg('掷骰…');
    Casino.audio.play('card-shuffle', 0.3);
    this._renderActions();
  }

  _resolve() {
    this.phase = 'bet';
    var r = this.roll, n = r.total;
    this.history.unshift(n);
    if (this.history.length > 10) this.history.pop();
    var lines = [];
    var banner = null;
    // Field 一掷结算
    if (this.bets.field > 0) {
      var fm = __crapsField(n);
      if (fm > 0) {
        var win = this.bets.field * fm;
        this.wallet.add(win);
        lines.push('Field 赢 ' + (win - this.bets.field));
      } else lines.push('Field 输 ' + this.bets.field);
      this.bets.field = 0;
    }
    if (!this.point) {
      // come-out
      var pr = __crapsComeOut(n);
      var dr = __crapsDontComeOut(n);
      if (pr === 'win') {
        var w1 = this.bets.pass * 2; this.wallet.add(w1);
        if (this.bets.pass) lines.push('Pass 赢 ' + this.bets.pass);
        this.bets.pass = 0;
      } else if (pr === 'lose') {
        if (this.bets.pass) lines.push('Pass 输 ' + this.bets.pass);
        this.bets.pass = 0;
      }
      if (dr === 'win') {
        var w2 = this.bets.dont * 2; this.wallet.add(w2);
        if (this.bets.dont) lines.push('Don\'t 赢 ' + this.bets.dont);
        this.bets.dont = 0;
      } else if (dr === 'lose') {
        if (this.bets.dont) lines.push('Don\'t 输 ' + this.bets.dont);
        this.bets.dont = 0;
      } else if (dr === 'push') {
        if (this.bets.dont) lines.push('Don\'t 平（12）退注');
        // 退注
        this.wallet.add(this.bets.dont); this.bets.dont = 0;
      }
      if (pr.indexOf('point:') === 0) {
        this.point = n;
        banner = { text: 'POINT ' + n, color: '#ffd98a', start: this.tick, dur: 80 };
        Casino.audio.play('voice-point', 0.8);
        Casino.say('点数 ' + n, { pitch: 0.7 });
        lines.push('设点 ' + n + ' · 掷出 ' + n + ' 赢 / 7 输');
      } else {
        banner = { text: (pr === 'win' ? 'PASS 赢！' : 'CRAPS ' + n), color: pr === 'win' ? '#ffd98a' : '#e08080', start: this.tick, dur: 80 };
        Casino.audio.play(pr === 'win' ? 'voice-winner' : 'voice-craps', 0.85);
      }
    } else {
      // 点数阶段
      var pr2 = __crapsPointRoll(this.point, n);
      var dr2 = __crapsDontPoint(this.point, n);
      if (pr2 === 'win') {
        this.wallet.add(this.bets.pass * 2);
        if (this.bets.pass) lines.push('Pass 赢 ' + this.bets.pass);
        this.bets.pass = 0;
      } else if (pr2 === 'lose') {
        if (this.bets.pass) lines.push('Pass 输（7 out）' + this.bets.pass);
        this.bets.pass = 0;
      }
      if (dr2 === 'win') {
        this.wallet.add(this.bets.dont * 2);
        if (this.bets.dont) lines.push('Don\'t 赢（7 out）' + this.bets.dont);
        this.bets.dont = 0;
      } else if (dr2 === 'lose') {
        if (this.bets.dont) lines.push('Don\'t 输 ' + this.bets.dont);
        this.bets.dont = 0;
      }
      if (pr2 === 'win') {
        banner = { text: n + ' 点命中！WINNER', color: '#ffd98a', start: this.tick, dur: 90 };
        Casino.audio.play('voice-winner', 0.9);
        this.point = null; // 回到 come-out
      } else if (pr2 === 'lose') {
        banner = { text: 'SEVEN OUT', color: '#e08080', start: this.tick, dur: 90 };
        Casino.audio.play('voice-seven', 0.9);
        this.point = null;
      } else {
        banner = { text: n + ' · 继续', color: '#c0c8d8', start: this.tick, dur: 60 };
      }
    }
    this.banner = banner;
    this._msg('掷出 ' + r.dice[0] + ' + ' + r.dice[1] + ' = ' + n + (lines.length ? ' · ' + lines.join(' · ') : ''));
    if (lines.some(function (l) { return l.indexOf('赢') >= 0; })) {
      Casino.audio.play('voice-win', 0.6);
      this.shake = { amp: 5, start: this.tick, dur: 10 };
    }
    this._renderActions();
  }

  _renderActions() {
    var self = this;
    var staked = this.bets.pass + this.bets.dont + this.bets.field;
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b>' + (this.point ? ' · 点数 <b>' + this.point + '</b>' : ' · come-out') + (staked ? ' · 押 <b>' + staked + '</b>' : '') + '</span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 16px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet') {
      if (this.wallet.get() < CR_BETS[0] && staked === 0) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f');
        if (!this.wallet.canBailout()) { bb.disabled = true; bb.style.opacity = .5; bb.style.cursor = 'not-allowed'; }
        this.actEl.appendChild(bb);
        return;
      }
      CR_BETS.forEach(function (v) {
        var b = mk('筹码 ' + v, function () { self.chipAmt = v; self._renderActions(); }, self.chipAmt === v ? '#ffd98a' : '#8a6a4a');
        if (self.chipAmt === v) b.style.background = 'rgba(70,40,12,.95)';
        self.actEl.appendChild(b);
      });
      this.actEl.appendChild(mk('押 Pass ' + (this.bets.pass || ''), function () { self.place('pass'); }, '#8fce8f'));
      this.actEl.appendChild(mk("押 Don't " + (this.bets.dont || ''), function () { self.place('dont'); }, '#e0a8a0'));
      this.actEl.appendChild(mk('押 Field ' + (this.bets.field || ''), function () { self.place('field'); }, '#a0c8e8'));
      this.actEl.appendChild(mk('🎲 掷骰 ROLL', function () { self.rollNow(); }, '#e06060'));
      return;
    }
  }

  // ---------- 场景 ----------
  renderScene(c, w, h, t) {
    if (this.destroyed) return;
    var P = Casino.paint;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    this._posCache = { center: [w / 2, h * 0.55] };
    c.save();
    if (this.shake) {
      var sp = (this.tick - this.shake.start) / this.shake.dur;
      if (sp < 1) {
        var amp = this.shake.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      } else this.shake = 0;
    }
    P.table(c, w, h);
    P.seat(c, w / 2, h * 0.33, t, { name: '荷官', color: '#c8a050', persona: 'tight', scale: s * 1.2, active: false, chipsLabel: '' });
    // 下注区
    this._zones(c, w, h, s);
    // 骰子
    this._dice(c, w, h, s);
    this._history(c, w, h, s);
    c.restore();
    this._drawBanner(c, w, h);
  }
  _zones(c, w, h, s) {
    var zs = [
      { key: 'pass', label: 'PASS LINE', x: w * 0.33, cls: '#8fce8f' },
      { key: 'dont', label: "DON'T PASS", x: w * 0.52, cls: '#e0a8a0' },
      { key: 'field', label: 'FIELD 2·12 ×2', x: w * 0.71, cls: '#a0c8e8' }
    ];
    for (var i = 0; i < 3; i++) {
      var z = zs[i];
      var amt = this.bets[z.key];
      var zw = w * 0.165, zh = h * 0.11;
      var y = h * 0.56;
      c.save();
      c.fillStyle = 'rgba(20,12,8,.65)';
      this._rr(c, z.x - zw / 2, y - zh / 2, zw, zh, 8 * s);
      c.fill();
      c.strokeStyle = amt > 0 ? z.cls : 'rgba(240,198,116,.4)';
      c.lineWidth = amt > 0 ? 2.5 : 1.5;
      if (amt > 0) { c.shadowColor = z.cls; c.shadowBlur = 8; }
      this._rr(c, z.x - zw / 2, y - zh / 2, zw, zh, 8 * s);
      c.stroke();
      c.shadowBlur = 0;
      c.fillStyle = amt > 0 ? '#ffe9c0' : 'rgba(230,210,180,.7)';
      c.font = '700 ' + Math.round(12 * s) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(z.label, z.x, y - 12 * s);
      if (amt > 0) {
        c.fillStyle = z.cls;
        c.beginPath(); c.arc(z.x, y + 14 * s, 11 * s, 0, Math.PI * 2); c.fill();
        c.fillStyle = '#0d0805';
        c.font = '700 ' + Math.round(10 * s) + 'px monospace';
        c.fillText(String(amt), z.x, y + 14 * s);
      }
      c.restore();
    }
    // puck（ON/OFF）
    var px = this.point ? w * 0.79 : w * 0.24;
    var py = h * 0.40;
    c.save();
    c.fillStyle = this.point ? '#f0f0e8' : '#1c1c22';
    c.beginPath(); c.arc(px, py, 15 * s, 0, Math.PI * 2); c.fill();
    c.strokeStyle = this.point ? '#e0a040' : '#606068'; c.lineWidth = 2;
    c.beginPath(); c.arc(px, py, 15 * s, 0, Math.PI * 2); c.stroke();
    c.fillStyle = this.point ? '#c04010' : '#c0c0c8';
    c.font = '900 ' + Math.round(11 * s) + 'px monospace';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText(this.point ? 'ON ' + this.point : 'OFF', px, py);
    c.restore();
  }
  _dice(c, w, h, s) {
    if (!this.roll) return;
    var dsz = 42 * s;
    var p = Math.min(1, (this.tick - this.rollT) / CR_ROLL_TICKS);
    for (var i = 0; i < 2; i++) {
      var t0 = i * 8;
      var pp = Math.max(0, Math.min(1, (this.tick - this.rollT - t0) / (CR_ROLL_TICKS - t0)));
      // 从右侧掷向中央：抛物线
      var startX = w * 0.88, endX = w / 2 + (i - 0.5) * dsz * 1.6;
      var x = startX + (endX - startX) * pp;
      var yBase = h * 0.40;
      var arc = Math.sin(pp * Math.PI) * 90 * s * (1 - pp * 0.3);
      var y = yBase - arc + Math.abs(Math.sin(pp * Math.PI * 3)) * 14 * s * (1 - pp);
      var rot = pp < 1 ? pp * (14 + i * 6) : 0;
      var alpha = Math.min(1, pp * 3);
      // 值：落定前显示滚动面，落定后显示真实值
      var value = pp >= 1 ? this.roll.dice[i] : (Math.floor(this.tick * 0.4 + i * 3) % 6) + 1;
      this._die(c, x, y, dsz * (0.7 + 0.3 * pp), value, rot, alpha);
    }
  }
  _die(c, x, y, size, value, rot, alpha) {
    c.save();
    c.globalAlpha = alpha;
    c.translate(x, y);
    c.rotate(rot);
    var g = c.createLinearGradient(-size / 2, -size / 2, size / 2, size / 2);
    g.addColorStop(0, '#f8f2e2'); g.addColorStop(1, '#d8ccae');
    c.fillStyle = g;
    this._rr(c, -size / 2, -size / 2, size, size, size * 0.18);
    c.fill();
    c.strokeStyle = 'rgba(90,50,20,.6)'; c.lineWidth = 1; c.stroke();
    var pip = size * 0.13;
    c.fillStyle = '#2a1a10';
    var L = -size * 0.26, R = size * 0.26, C2 = 0;
    var layout = { 1: [[C2, C2]], 2: [[L, L], [R, R]], 3: [[L, L], [C2, C2], [R, R]], 4: [[L, L], [R, L], [L, R], [R, R]], 5: [[L, L], [R, L], [C2, C2], [L, R], [R, R]], 6: [[L, L], [R, L], [L, C2], [R, C2], [L, R], [R, R]] };
    (layout[value] || []).forEach(function (p2) {
      c.beginPath(); c.arc(p2[0], p2[1], pip, 0, Math.PI * 2); c.fill();
    });
    c.restore();
  }
  _history(c, w, h, s) {
    if (!this.history.length) return;
    c.save();
    c.font = Math.max(9, 11 * s) + 'px monospace';
    c.fillStyle = '#a08a6a'; c.textBaseline = 'middle';
    c.fillText('近期:', w * 0.33, h * 0.20);
    this.history.slice(0, 10).forEach(function (n, i) {
      c.fillStyle = n === 7 ? '#8a1a1a' : (n === 11 ? '#1a6a3a' : 'rgba(30,30,40,.9)');
      c.fillRect(w * 0.33 + 32 * s + i * 22 * s, h * 0.20 - 8 * s, 18 * s, 16 * s);
      c.fillStyle = '#f0e6d0'; c.textAlign = 'center';
      c.font = Math.max(8, 10 * s) + 'px monospace';
      c.fillText(String(n), w * 0.33 + 32 * s + i * 22 * s + 9 * s, h * 0.20);
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
  _drawBanner(c, w, h) {
    if (!this.banner) return;
    var p = Math.min(1, (this.tick - this.banner.start) / this.banner.dur);
    var inS = Math.min(1, p * 6);
    var out = p > 0.85 ? (1 - p) / 0.15 : 1;
    var scale = 0.6 + 0.4 * (1 - Math.pow(1 - inS, 2));
    c.save();
    c.translate(w / 2, h * 0.26);
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
  // bot 模式自动下注+掷骰（自动化测试/浸泡用；设点后继续追掷）
  _botStep() {
    var staked = this.bets.pass + this.bets.dont + this.bets.field;
    if (this.tick % 50 === 30) {
      if (staked === 0 && this.wallet.get() >= this.chipAmt) {
        this.place(['pass', 'dont', 'field'][Math.floor(Math.random() * 3)]);
      } else if (this.wallet.get() < this.chipAmt) this.wallet.bailout();
    } else if (this.tick % 50 === 5 && staked > 0) {
      this.rollNow();
    }
  }
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.phase === 'bet' && this.bot) this._botStep();
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= (this.shake.dur || 10)) this.shake = 0;
    if (this.phase !== 'roll') return;
    if (this.tick - this.rollT >= CR_ROLL_TICKS + 8) {
      Casino.audio.play('card-hits', 0.5); // 落定
      this._resolve();
    }
  }

  destroy() { this.destroyed = true; }
}

Casino.register('craps', {
  name: 'Craps 双骰',
  icon: '🎲',
  desc: 'Pass/Don\'t Pass 设点制 + Field 一掷 · 7-11 即赢 · 掷点赢 · Seven out',
  create: function (container, ctx) { return new CasinoCraps(container, ctx); }
});

// casino-roulette.js — 算力赌坊 · 欧式轮盘 Roulette
// 单零 37 格；下注：直注 35:1、打 2:1、红黑/单双/大小 1:1（0 通杀外围）。
// 动画：轮盘旋转 + 象牙球反向环绕减速 → 螺旋落袋回弹 → 结果指针+语音报号。
// 下注直接点桌面区域（号码毯/外围区），筹码摆在格子上。

// ---------- 引擎（纯函数，供测试） ----------
var RO_ORDER = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26];
var RO_RED = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];
function __roColor(n) { return n === 0 ? 'green' : (RO_RED.indexOf(n) >= 0 ? 'red' : 'black'); }
function __roSpin(rng) { return Math.floor((rng || Math.random)() * 37); }
// 单注赔付（返回倍数：总返还 = 下注 × mult；0 = 全输）
function __roPayout(type, pick, n) {
  if (n === 0 && type !== 'straight') return 0; // 0 通杀外围
  switch (type) {
    case 'straight': return n === pick ? 36 : 0;
    case 'red': return __roColor(n) === 'red' ? 2 : 0;
    case 'black': return __roColor(n) === 'black' ? 2 : 0;
    case 'odd': return n % 2 === 1 ? 2 : 0;
    case 'even': return n % 2 === 0 ? 2 : 0;
    case 'small': return n <= 18 ? 2 : 0;
    case 'big': return n >= 19 ? 2 : 0;
    case 'dozen1': return n >= 1 && n <= 12 ? 3 : 0;
    case 'dozen2': return n >= 13 && n <= 24 ? 3 : 0;
    case 'dozen3': return n >= 25 ? 3 : 0;
    default: return 0;
  }
}
// 一局多注结算 → {total 返还, hits: [命中的注]}
function __roSettle(bets, n) {
  var total = 0, hits = [];
  bets.forEach(function (b) {
    var m = __roPayout(b.type, b.pick, n);
    if (m > 0) { total += b.amt * m; hits.push(b); }
  });
  return { total: total, hits: hits };
}

var RO_CHIPS = [20, 50, 100];

// ---------- 轮盘桌 ----------
class CasinoRoulette {
  constructor(container, ctx) {
    this.ctx = ctx;
    this.wallet = ctx.wallet;
    this.bot = !!ctx.bot;
    this.tick = 0;
    this.destroyed = false;
    this.fx = [];
    this.banner = null;
    this.shake = 0;
    this.chipAmt = RO_CHIPS[0];
    this.bets = [];          // {type, pick, amt}
    this.wheelAngle = 0;     // 轮盘旋转角（弧度）
    this.wheelVel = 0;
    this.ballAngle = 0;      // 球角（相对屏幕）
    this.ballVel = 0;
    this.ballR = 1;          // 球轨道半径系数（1 外轨 → 0 落袋）
    this.result = null;      // 开奖号码
    this.spinT = 0;
    this.history = [];       // 最近 12 期
    this._zones = [];        // 可点下注区（画布坐标）
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
    // 透明点击层：点到桌面上直接下注（点击命中 canvas 绘制的格子）
    this.clickLayer = this._el('div', 'position:absolute;left:0;right:0;top:14%;bottom:26%;pointer-events:auto;z-index:5'); // 只盖桌面区，不挡顶栏/操作栏
    this.clickLayer.onclick = function (e) { self._onTableClick(e); };
    this.root.appendChild(this.clickLayer);
    container.appendChild(this.root);
  }
  _msg(t) { this.msgEl.textContent = t; }

  _awaitBet() {
    this.phase = 'bet';
    this.bets = [];
    this.result = null;
    this._msg('选筹码 → 点桌面下注（可多处）→ SPIN');
    Casino.audio.play('voice-bets', 0.7);
    this._renderActions();
  }

  _onTableClick(e) {
    if (this.phase !== 'bet') return;
    var host = this.root.parentNode;
    if (!host) return;
    var rect = host.getBoundingClientRect();
    var x = e.clientX - rect.left, y = e.clientY - rect.top;
    var w = rect.width, h = rect.height;
    var s = Math.max(0.8, Math.min(1.7, Math.min(w / 980, h / 620)));
    for (var i = 0; i < this._zones.length; i++) {
      var z = this._zones[i];
      if (x >= z.x && x <= z.x + z.w && y >= z.y && y <= z.y + z.h) {
        if (!this.wallet.sub(this.chipAmt)) { this._msg('算力不足'); return; }
        // 同区叠加
        var same = this.bets.find(function (b) { return b.type === z.type && b.pick === z.pick; });
        if (same) same.amt += this.chipAmt;
        else this.bets.push({ type: z.type, pick: z.pick, amt: this.chipAmt });
        Casino.audio.play('coins', 0.35);
        this._msg(z.label + ' · 已押 ' + this.bets.reduce(function (a, b) { return a + b.amt; }, 0));
        this._renderActions();
        return;
      }
    }
  }

  spin() {
    if (this.phase !== 'bet' || !this.bets.length) { if (this.phase === 'bet') this._msg('先在桌面点一格下注'); return; }
    this.phase = 'spin';
    this.spinT = this.tick;
    this.result = __roSpin();
    this.wheelVel = 0.055;
    this.ballVel = -0.24;           // 球反向
    this.ballR = 1;
    this.catchAt = this.tick + 320; // 落袋锁定帧
    this._done = false;             // 跨局残留清理
    this._clickSnd = false;
    this.bounceT = 0;
    this._msg('No more bets！转动中…');
    Casino.audio.play('voice-wheel', 0.8);
    this._renderActions();
  }

  _finish() {
    this.phase = 'settle';
    var n = this.result;
    var staked = this.bets.reduce(function (a, b) { return a + b.amt; }, 0);
    var res = __roSettle(this.bets, n);
    var net = res.total - staked;
    if (res.total > 0) {
      this.wallet.add(res.total);
      this.fx.push({ kind: 'chips', start: this.tick, dur: 60, n: res.total });
    }
    this.history.unshift(n);
    if (this.history.length > 12) this.history.pop();
    var colName = n === 0 ? '零' : (__roColor(n) === 'red' ? '红' : '黑');
    this._msg('开出 ' + colName + ' ' + n + ' · ' + (net > 0 ? '净赢 +' + net : net === 0 ? '打平' : '净输 ' + net));
    this.banner = {
      text: colName + ' ' + n + (net > 0 ? ' · +' + net : ''),
      color: n === 0 ? '#7ee8a0' : (__roColor(n) === 'red' ? '#ff8a70' : '#cfd8e8'),
      start: this.tick, dur: 110
    };
    Casino.audio.play(n === 0 ? 'voice-zero' : (__roColor(n) === 'red' ? 'voice-red' : 'voice-black'), 0.85);
    Casino.say(colName + ' ' + n, { pitch: 0.75, rate: 1 });
    if (net > 0) { Casino.audio.play('voice-win', 0.8); this.shake = { amp: 6, start: this.tick, dur: 12 }; }
    else if (net < 0) Casino.audio.play('voice-lose', 0.55);
    this._renderActions();
  }

  _renderActions() {
    var self = this;
    var staked = this.bets.reduce(function (a, b) { return a + b.amt; }, 0);
    var info = '<span style="font-size:12px;color:#ffd98a;margin-right:6px;white-space:nowrap">算力 <b>' + this.wallet.get().toLocaleString() + '</b>' + (staked ? ' · 已押 <b>' + staked + '</b>' : '') + '</span>';
    this.actEl.innerHTML = '';
    this.actEl.insertAdjacentHTML('beforeend', info);
    var mk = function (label, fn, cls) {
      var b = self._el('button', 'padding:9px 18px;border-radius:8px;border:1px solid ' + cls + ';background:rgba(26,13,6,.92);color:' + cls + ';cursor:pointer;font-family:inherit;font-size:13px;font-weight:600', label);
      b.onclick = fn;
      return b;
    };
    if (this.phase === 'bet') {
      if (this.wallet.get() < RO_CHIPS[0]) {
        var bb = mk(this.wallet.canBailout() ? '🎁 领救济金 +1000' : '破产中·60秒后再领', function () {
          if (Casino.wallet.bailout()) { self._msg('救济金 +1000'); self._renderActions(); }
          else self._msg('救济金冷却中（间隔 60 秒）');
        }, '#8fce8f');
        if (!this.wallet.canBailout()) { bb.disabled = true; bb.style.opacity = .5; bb.style.cursor = 'not-allowed'; }
        this.actEl.appendChild(bb);
        return;
      }
      RO_CHIPS.forEach(function (v) {
        var b = mk('筹码 ' + v, function () { self.chipAmt = v; self._renderActions(); }, self.chipAmt === v ? '#ffd98a' : '#8a6a4a');
        if (self.chipAmt === v) b.style.background = 'rgba(70,40,12,.95)';
        self.actEl.appendChild(b);
      });
      this.actEl.appendChild(mk('🎡 SPIN 转动', function () { self.spin(); }, '#e06060'));
      if (this.bets.length) this.actEl.appendChild(mk('清空下注', function () {
        self.bets.forEach(function (b) { self.wallet.add(b.amt); });
        self.bets = [];
        self._msg('已撤回下注');
        self._renderActions();
      }, '#8a7ba0'));
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
    c.save();
    if (this.shake) {
      var sp = (this.tick - this.shake.start) / this.shake.dur;
      if (sp < 1) {
        var amp = this.shake.amp * (1 - sp);
        c.translate(Math.sin(this.tick * 1.7) * amp, Math.cos(this.tick * 2.3) * amp);
      } else this.shake = 0;
    }
    P.table(c, w, h);
    // 左：转轮；右：下注毯
    this._wheel(c, w * 0.26, h * 0.42, Math.min(w * 0.17, h * 0.30), s);
    this._layout(c, w, h, s);
    // 已押筹码（摆在格子上）
    this._betsOnTable(c, s);
    this._history(c, w, h, s);
    this._drawFx(c, s);
    c.restore();
    this._drawBanner(c, w, h);
  }

  _wheel(c, cx, cy, R, s) {
    var spinning = this.phase === 'spin';
    // 外木环
    var wood = c.createRadialGradient(cx - R * 0.3, cy - R * 0.3, R * 0.2, cx, cy, R * 1.12);
    wood.addColorStop(0, '#6a3a18'); wood.addColorStop(0.8, '#3a1e0a'); wood.addColorStop(1, '#1c0e05');
    c.fillStyle = wood;
    c.beginPath(); c.arc(cx, cy, R * 1.12, 0, Math.PI * 2); c.fill();
    c.strokeStyle = 'rgba(255,200,120,.6)'; c.lineWidth = 2;
    c.beginPath(); c.arc(cx, cy, R * 1.12, 0, Math.PI * 2); c.stroke();
    // 数字格盘（随轮旋转）
    var seg = Math.PI * 2 / 37;
    c.save();
    c.translate(cx, cy);
    c.rotate(this.wheelAngle);
    for (var i = 0; i < 37; i++) {
      var a0 = i * seg - Math.PI / 2 - seg / 2, a1 = a0 + seg;
      var n = RO_ORDER[i];
      var col = __roColor(n);
      c.fillStyle = col === 'green' ? '#1a7a44' : (col === 'red' ? '#8a1a1a' : '#1c1c22');
      c.beginPath();
      c.moveTo(Math.cos(a0) * R * 0.62, Math.sin(a0) * R * 0.62);
      c.arc(0, 0, R * 0.98, a0, a1);
      c.lineTo(Math.cos(a1) * R * 0.62, Math.sin(a1) * R * 0.62);
      c.closePath(); c.fill();
      c.strokeStyle = 'rgba(200,170,110,.5)'; c.lineWidth = 0.8; c.stroke();
      // 数字（径向）
      c.save();
      c.rotate(a0 + seg / 2);
      c.translate(R * 0.86, 0);
      c.rotate(Math.PI / 2);
      c.fillStyle = '#f0e6d0';
      c.font = '700 ' + Math.max(8, R * 0.11) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(String(n), 0, 0);
      c.restore();
    }
    // 中心转轴（金色十字木辐）
    c.fillStyle = '#7a5a24';
    c.beginPath(); c.arc(0, 0, R * 0.14, 0, Math.PI * 2); c.fill();
    c.strokeStyle = '#e8c874'; c.lineWidth = 2;
    c.beginPath(); c.arc(0, 0, R * 0.14, 0, Math.PI * 2); c.stroke();
    for (var k = 0; k < 4; k++) {
      c.save(); c.rotate(k * Math.PI / 2 + this.wheelAngle * 0.5);
      c.fillStyle = '#5a3c14';
      c.fillRect(-R * 0.028, -R * 0.6, R * 0.056, R * 0.55);
      c.restore();
    }
    c.restore();
    // 球轨道 + 球
    if (spinning || this.phase === 'settle') {
      var orbit = R * (0.62 + 0.38 * this.ballR); // 外轨→格内
      var bx = cx + Math.cos(this.ballAngle) * orbit;
      var by = cy + Math.sin(this.ballAngle) * orbit;
      // 球运动拖影
      if (spinning && this.ballVel !== 0) {
        for (var tr = 1; tr <= 3; tr++) {
          c.fillStyle = 'rgba(240,235,220,' + (0.16 - tr * 0.04) + ')';
          c.beginPath();
          c.arc(cx + Math.cos(this.ballAngle + this.ballVel * tr * 2) * orbit, cy + Math.sin(this.ballAngle + this.ballVel * tr * 2) * orbit, R * 0.032, 0, Math.PI * 2);
          c.fill();
        }
      }
      c.fillStyle = '#f5f0e0';
      c.shadowColor = 'rgba(255,255,255,.7)'; c.shadowBlur = 6;
      c.beginPath(); c.arc(bx, by, R * 0.036, 0, Math.PI * 2); c.fill();
      c.shadowBlur = 0;
    }
    // 结果指针（settle 后指到中奖格）
    if (this.phase === 'settle' && this.result !== null) {
      var idx = RO_ORDER.indexOf(this.result);
      var pocketA = this.wheelAngle + idx * seg - Math.PI / 2;
      var px = cx + Math.cos(pocketA) * R * 1.0, py = cy + Math.sin(pocketA) * R * 1.0;
      c.fillStyle = '#ffd98a';
      c.shadowColor = '#ffd98a'; c.shadowBlur = 10;
      c.beginPath(); c.arc(px, py, R * 0.05, 0, Math.PI * 2); c.fill();
      c.shadowBlur = 0;
    }
  }

  _layout(c, w, h, s) {
    // 经典下注毯：0 + 3×12 号码格 / 三打 / 外围（红黑单双大小）
    this._zones = [];
    var gw = Math.min(w * 0.034, 44), gh = gw * 0.78;
    var ox = w * 0.47, oy = h * 0.30;
    var self = this;
    var cell = function (x, y, w2, h2, label, zone, fill, txtCol) {
      self._zones.push({ x: x, y: y, w: w2, h: h2, type: zone.type, pick: zone.pick, label: label });
      c.fillStyle = fill;
      c.strokeStyle = 'rgba(240,198,116,.55)'; c.lineWidth = 1;
      self._rr(c, x, y, w2, h2, 4);
      c.fill(); c.stroke();
      c.fillStyle = txtCol || '#f0e6d0';
      c.font = '700 ' + Math.max(9, gw * 0.30) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(label, x + w2 / 2, y + h2 / 2);
    };
    // 0
    cell(ox, oy, gw * 0.8, gh * 3, '0', { type: 'straight', pick: 0 }, '#1a7a44');
    // 1-36：上排 3,6..36 中 2,5.. 下 1,4..
    for (var row = 0; row < 3; row++) {
      for (var col = 0; col < 12; col++) {
        var num = col * 3 + (3 - row); // 上排 3,6..36 / 中 2,5.. / 下 1,4..
        var col2 = __roColor(num) === 'red' ? '#8a1a1a' : '#1c1c22';
        cell(ox + gw * 0.8 + col * gw, oy + row * gh, gw, gh, String(num), { type: 'straight', pick: num }, col2);
      }
    }
    // 三打
    var dzY = oy + gh * 3 + 6 * s;
    [['dozen1', '1-12 打一'], ['dozen2', '13-24 打二'], ['dozen3', '25-36 打三']].forEach(function (d, i) {
      cell(ox + gw * 0.8 + i * gw * 4, dzY, gw * 4 - 4, gh * 0.8, d[1], { type: d[0], pick: 0 }, 'rgba(90,20,20,.85)');
    });
    // 外围
    var outY = dzY + gh * 0.8 + 6 * s;
    var outs = [
      ['small', '小 1-18', 'rgba(30,30,40,.9)'],
      ['even', '双', 'rgba(30,30,40,.9)'],
      ['red', '红', '#8a1a1a'],
      ['black', '黑', '#1c1c22'],
      ['odd', '单', 'rgba(30,30,40,.9)'],
      ['big', '大 19-36', 'rgba(30,30,40,.9)']
    ];
    outs.forEach(function (o, i) {
      cell(ox + gw * 0.8 + i * gw * 2, outY, gw * 2 - 4, gh * 0.8, o[1], { type: o[0], pick: 0 }, o[2]);
    });
    // 下注阶段高亮悬停感：全部格子外发光脉冲（简化：已押注格子亮框）
  }

  _betsOnTable(c, s) {
    var self = this;
    this.bets.forEach(function (b) {
      var z = self._zones.find(function (zn) { return zn.type === b.type && zn.pick === b.pick; });
      if (!z) return;
      c.save();
      c.strokeStyle = '#ffd98a'; c.lineWidth = 2;
      c.shadowColor = '#ffc87a'; c.shadowBlur = 8;
      self._rr(c, z.x + 2, z.y + 2, z.w - 4, z.h - 4, 4);
      c.stroke();
      c.shadowBlur = 0;
      // 筹码 + 金额
      var cx2 = z.x + z.w / 2, cy2 = z.y + z.h / 2;
      c.fillStyle = 'rgba(240,198,116,.95)';
      c.beginPath(); c.arc(cx2, cy2, Math.min(z.w, z.h) * 0.36, 0, Math.PI * 2); c.fill();
      c.strokeStyle = '#7a4a14'; c.lineWidth = 1.5;
      c.beginPath(); c.arc(cx2, cy2, Math.min(z.w, z.h) * 0.36, 0, Math.PI * 2); c.stroke();
      c.fillStyle = '#3a2008';
      c.font = '700 ' + Math.max(8, Math.min(z.w, z.h) * 0.22) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText(String(b.amt), cx2, cy2);
      c.restore();
    });
  }
  _history(c, w, h, s) {
    if (!this.history.length) return;
    var x0 = w * 0.47, y = h * 0.30 - 26 * s;
    c.save();
    c.font = Math.max(9, 11 * s) + 'px monospace';
    c.fillStyle = '#a08a6a'; c.textBaseline = 'middle';
    c.fillText('近期:', x0, y);
    this.history.slice(0, 12).forEach(function (n, i) {
      var col = n === 0 ? '#1a7a44' : (__roColor(n) === 'red' ? '#8a1a1a' : '#2a2a32');
      c.fillStyle = col;
      c.fillRect(x0 + 34 * s + i * 22 * s, y - 8 * s, 18 * s, 16 * s);
      c.fillStyle = '#f0e6d0'; c.textAlign = 'center';
      c.font = Math.max(8, 10 * s) + 'px monospace';
      c.fillText(String(n), x0 + 34 * s + i * 22 * s + 9 * s, y);
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
    var self = this;
    this.fx.forEach(function (f) {
      var p = (self.tick - f.start) / f.dur;
      if (p < 0 || p > 1) return;
      if (f.kind === 'chips') {
        for (var i = 0; i < 12; i++) {
          var cx2 = self._posCache ? self._posCache.wheel[0] : 400;
          var cy2 = self._posCache ? self._posCache.wheel[1] : 260;
          var x = cx2 + ((i * 97.3 + self.tick * 3) % 100 - 50) * 3.2 * s;
          var y = cy2 + 40 * s + ((i * 61.7 + self.tick * 4 + i) % 90) / 90 * 120 * s;
          c.fillStyle = i % 2 ? '#ffc87a' : '#ffe3ad';
          c.beginPath(); c.ellipse(x, y, 6, 3, 0, 0, Math.PI * 2); c.fill();
        }
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

  // ---------- 帧驱动：轮盘物理 ----------
  // bot 模式自动下注+转轮（自动化测试/浸泡用）
  _botStep() {
    if (this.tick < 40) return;
    if (this.tick % 45 === 40 || this.tick % 45 === 20) {
      var opts = ['red', 'black', 'odd', 'even', 'dozen1', 'dozen2', 'dozen3'];
      var type = opts[Math.floor(Math.random() * opts.length)];
      if (this.wallet.sub(this.chipAmt)) {
        var same = this.bets.find(function (b) { return b.type === type; });
        if (same) same.amt += this.chipAmt;
        else this.bets.push({ type: type, pick: null, amt: this.chipAmt });
      }
    } else if (this.tick % 45 === 5 && this.bets.length) {
      this.spin();
    } else if (this.wallet.get() < 20) {
      this.wallet.bailout();
    }
  }
  update() {
    if (this.destroyed) return;
    var self = this;
    this.tick++;
    if (this.phase === 'bet' && this.bot) this._botStep();
    if (this.bot && this.phase === 'settle' && this.tick % 40 === 20) this._awaitBet();
    if (this.fx.length) this.fx = this.fx.filter(function (f) { return self.tick - f.start < f.dur + 20; });
    if (this.banner && this.tick - this.banner.start >= this.banner.dur) this.banner = null;
    if (this.shake && this.tick - this.shake.start >= (this.shake.dur || 12)) this.shake = 0;

    // 下注阶段轮盘慢转（氛围）
    if (this.phase === 'bet') {
      this.wheelAngle += 0.004;
      this.ballAngle -= 0.01;
      return;
    }
    if (this.phase !== 'spin') return;
    // 缓存轮盘中心（供特效）
    // 轮减速
    this.wheelAngle += this.wheelVel;
    this.wheelVel *= 0.9965;
    if (this.tick < this.catchAt) {
      // 球自由环绕：反向、快速减速、半径缓慢内收
      this.ballAngle += this.ballVel;
      this.ballVel *= 0.986;
      this.ballR = Math.max(0.28, this.ballR - 0.0022);
      if (Math.abs(this.ballVel) < 0.05 && !this._clickSnd) { this._clickSnd = true; }
    } else if (this.tick < this.catchAt + 46) {
      // 落袋过渡：球角锁定到中奖格相对角（带小回弹）
      var seg = Math.PI * 2 / 37;
      var idx = RO_ORDER.indexOf(this.result);
      var target = this.wheelAngle + idx * seg - Math.PI / 2;
      var k = (this.tick - this.catchAt) / 46;
      // 角度插值（处理环绕）
      var d = target - this.ballAngle;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      this.ballAngle += d * 0.22;
      this.ballR = Math.max(0.14, this.ballR - 0.006);
      if ((this.tick - this.catchAt) % 9 === 0) Casino.audio.play('card-hits', 0.2); // 落袋哒哒声
    } else {
      // 完全锁定随轮转
      var seg2 = Math.PI * 2 / 37;
      var idx2 = RO_ORDER.indexOf(this.result);
      this.ballAngle = this.wheelAngle + idx2 * seg2 - Math.PI / 2;
      this.ballR = 0.14;
      if (!this._done) { this._done = true; this._finish(); }
    }
  }

  destroy() {
    this.destroyed = true;
    if (this.clickLayer) this.clickLayer.onclick = null;
  }
}

Casino.register('roulette', {
  name: '欧式轮盘 Roulette',
  icon: '🎡',
  desc: '单零 37 格 · 直注 35:1 / 打 2:1 / 红黑单双大小 1:1 · 点击桌面直接下注',
  create: function (container, ctx) { return new CasinoRoulette(container, ctx); }
});

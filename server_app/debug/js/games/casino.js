// casino.js — 算力赌坊：大厅 + 共享钱包 + 子游戏注册表
// 架构铺垫：后续新增赌桌（21 点 / 骰子 / 老虎机…）只需：
//   1. 写一个新文件 class XxxTable { constructor(container, ctx) {...} update(){} destroy(){} }
//      ctx = { wallet, exit(), bot }（wallet 为共享算力钱包）
//   2. 文件末尾 Casino.register('xxx', { name, icon, desc, create: (c, ctx) => new XxxTable(c, ctx) })
//   3. game.html GAMES['casino'].files 数组与 index.html <script> 标签加上该文件
// 大厅会自动列出注册的新赌桌，无需改大厅代码。

// ---------- 共享钱包（全赌桌通用，localStorage 持久化；纯虚拟筹码） ----------
const CHIPS_KEY = 'casinoChips';
const _chipListeners = new Set();

window.Casino = {
  wallet: {
    get() {
      var v = parseInt(localStorage.getItem(CHIPS_KEY) || '1000', 10);
      return isFinite(v) && v >= 0 ? v : 1000;
    },
    add(n) { this._save(this.get() + n); },
    sub(n) {
      if (this.get() < n) return false;
      this._save(this.get() - n);
      return true;
    },
    // 破产救济：纯虚拟筹码，随时可领（仅供娱乐）
    bailout() { this._save(this.get() + 1000); },
    onChange(cb) {
      _chipListeners.add(cb);
      try { cb(this.get()); } catch (e) { /* listener error 不影响钱包 */ }
      return () => _chipListeners.delete(cb);
    },
    _save(v) {
      try { localStorage.setItem(CHIPS_KEY, String(v)); } catch (e) {}
      _chipListeners.forEach(function (cb) { try { cb(v); } catch (e) {} });
    }
  },

  // ---------- 子游戏注册表 ----------
  _tables: new Map(),
  register(id, def) { this._tables.set(id, def); },
  tables() { return Array.from(this._tables.keys()); },
  get(id) { return this._tables.get(id); },

  // ---------- 场景画师（大厅/赌桌共用：房间 + 扑克桌 + 人物 + 氛围） ----------
  paint: {
    // 房间：墙面渐变、透视地板、霓虹招牌、吊灯光锥、金尘粒子
    room(c, w, h, t) {
      var wall = c.createLinearGradient(0, 0, 0, h * 0.66);
      wall.addColorStop(0, '#221038'); wall.addColorStop(1, '#0d0718');
      c.fillStyle = wall; c.fillRect(0, 0, w, h * 0.66);
      var floor = c.createLinearGradient(0, h * 0.66, 0, h);
      floor.addColorStop(0, '#241436'); floor.addColorStop(1, '#0a0510');
      c.fillStyle = floor; c.fillRect(0, h * 0.66, w, h * 0.34);
      // 地板透视格
      c.strokeStyle = 'rgba(240,198,116,.07)'; c.lineWidth = 1;
      var vpx = w / 2;
      for (var gx = -4; gx <= 4; gx++) {
        c.beginPath(); c.moveTo(vpx + gx * w * 0.09, h * 0.66); c.lineTo(vpx + gx * w * 0.4, h); c.stroke();
      }
      for (var gy = 1; gy <= 5; gy++) {
        var yy = h * 0.66 + Math.pow(gy / 5, 1.6) * h * 0.34;
        c.beginPath(); c.moveTo(0, yy); c.lineTo(w, yy); c.stroke();
      }
      // 霓虹招牌
      var flick = 0.82 + 0.18 * Math.sin(t * 0.09) * Math.sin(t * 0.023);
      c.save();
      c.globalAlpha = flick;
      c.font = '700 ' + Math.max(18, w * 0.045) + 'px monospace';
      c.textAlign = 'center';
      c.shadowColor = '#ff5fd0'; c.shadowBlur = 22;
      c.fillStyle = '#ffd0f0';
      c.fillText('算 力 赌 坊', w / 2, h * 0.12);
      c.font = Math.max(9, w * 0.016) + 'px monospace';
      c.shadowColor = '#5fd0ff'; c.shadowBlur = 12;
      c.fillStyle = '#a8e8ff';
      c.fillText('~ C O M P U T E   C A S I N O ~', w / 2, h * 0.12 + 18);
      c.restore();
      // 两侧壁灯 + 光锥
      [[w * 0.09, h * 0.2], [w * 0.91, h * 0.2]].forEach(function (lp) {
        var glow = 0.5 + 0.5 * Math.sin(t * 0.05 + lp[0]);
        c.save();
        c.fillStyle = 'rgba(240,198,116,' + (0.5 + glow * 0.3) + ')';
        c.shadowColor = '#f0c674'; c.shadowBlur = 14;
        c.beginPath(); c.arc(lp[0], lp[1], 5, 0, Math.PI * 2); c.fill();
        var cone = c.createLinearGradient(lp[0], lp[1], lp[0], h * 0.6);
        cone.addColorStop(0, 'rgba(240,198,116,' + (0.10 + glow * 0.05) + ')');
        cone.addColorStop(1, 'rgba(240,198,116,0)');
        c.fillStyle = cone;
        c.beginPath(); c.moveTo(lp[0] - 8, lp[1]); c.lineTo(lp[0] + 8, lp[1]);
        c.lineTo(lp[0] + w * 0.13, h * 0.6); c.lineTo(lp[0] - w * 0.13, h * 0.6); c.closePath(); c.fill();
        c.restore();
      });
      // 金尘粒子（确定性漂浮）
      for (var i = 0; i < 26; i++) {
        var px = (Math.sin(i * 12.9898) * 43758.5453) % 1;
        var py = (Math.sin(i * 78.233) * 12345.6789) % 1;
        var fx = ((Math.abs(px) + t * 0.00004 * (1 + (i % 3))) % 1) * w;
        var fy = (Math.abs(py) * 0.9 + 0.03) * h - (t * 0.012 * (1 + (i % 4))) % (h * 0.5);
        if (fy < 0) fy += h * 0.6;
        c.fillStyle = 'rgba(240,198,116,' + (0.06 + 0.10 * Math.abs(Math.sin(t * 0.03 + i))) + ')';
        c.beginPath(); c.arc(fx, fy, 1.6, 0, Math.PI * 2); c.fill();
      }
    },
    // 扑克桌：木沿 + 绿呢 + 金线 + 桌标
    table(c, w, h) {
      var cx = w / 2, cy = h * 0.46, rx = w * 0.42, ry = h * 0.3;
      // 木沿
      var rim = c.createRadialGradient(cx, cy - ry * 0.4, ry * 0.2, cx, cy, rx);
      rim.addColorStop(0, '#7a4a1e'); rim.addColorStop(1, '#3a2210');
      c.fillStyle = rim;
      c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.fill();
      // 绿呢
      var felt = c.createRadialGradient(cx, cy - ry * 0.3, ry * 0.1, cx, cy, rx * 0.94);
      felt.addColorStop(0, '#15904a'); felt.addColorStop(1, '#073d20');
      c.fillStyle = felt;
      c.beginPath(); c.ellipse(cx, cy, rx * 0.92, ry * 0.88, 0, 0, Math.PI * 2); c.fill();
      // 金线 + 桌标
      c.strokeStyle = 'rgba(240,198,116,.4)'; c.lineWidth = 2;
      c.beginPath(); c.ellipse(cx, cy, rx * 0.8, ry * 0.74, 0, 0, Math.PI * 2); c.stroke();
      c.fillStyle = 'rgba(240,198,116,.14)';
      c.font = '700 ' + Math.max(12, w * 0.02) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText('S H O W   H A N D', cx, cy + ry * 0.05);
    },
    // 筹码堆
    chips(c, x, y, n) {
      var stacks = Math.min(6, Math.max(1, Math.ceil(n / 120)));
      var colors = ['#e05555', '#5fa8e0', '#f0c674', '#8ee08a'];
      for (var s = 0; s < stacks; s++) {
        var hgt = Math.min(8, Math.max(2, Math.floor(n / (stacks * 15))));
        for (var i = 0; i < hgt; i++) {
          c.fillStyle = colors[(s + i) % colors.length];
          c.beginPath(); c.ellipse(x + s * 16 - stacks * 8, y - i * 5, 9, 4.5, 0, 0, Math.PI * 2); c.fill();
          c.fillStyle = 'rgba(255,255,255,.25)';
          c.beginPath(); c.ellipse(x + s * 16 - stacks * 8, y - i * 5, 4, 2, 0, 0, Math.PI * 2); c.fill();
        }
      }
    },
    // 人物：造型按 persona 区分（aggr 尖角红 / tight 圆润蓝 / bluff 礼帽紫 / player 绿帽玩家）
    seat(c, x, y, t, o) {
      var s = o.scale || 1;
      var bob = Math.sin(t * 0.04 + x) * 2.5 * s;
      var blink = (Math.sin(t * 0.02 + x * 2) > 0.96);
      c.save();
      c.translate(x, y + bob);
      if (o.folded) { c.globalAlpha = 0.35; c.rotate(0.12); }
      // 行动光环 / 赢家金环
      if (o.winner) {
        c.strokeStyle = 'rgba(240,198,116,.9)'; c.lineWidth = 3;
        c.shadowColor = '#f0c674'; c.shadowBlur = 16;
        c.beginPath(); c.ellipse(0, 30 * s, 42 * s, 12 * s, 0, 0, Math.PI * 2); c.stroke();
        c.shadowBlur = 0;
      } else if (o.active) {
        var pulse = 0.5 + 0.5 * Math.sin(t * 0.15);
        c.strokeStyle = 'rgba(125,216,125,' + (0.35 + pulse * 0.5) + ')'; c.lineWidth = 3;
        c.beginPath(); c.ellipse(0, 30 * s, (38 + pulse * 6) * s, (11 + pulse * 2) * s, 0, 0, Math.PI * 2); c.stroke();
      }
      // 光锥
      if (o.active || o.winner) {
        var cone = c.createLinearGradient(0, -90 * s, 0, 30 * s);
        cone.addColorStop(0, o.winner ? 'rgba(240,198,116,.22)' : 'rgba(125,216,125,.16)');
        cone.addColorStop(1, 'rgba(0,0,0,0)');
        c.fillStyle = cone;
        c.beginPath(); c.moveTo(-14 * s, -80 * s); c.lineTo(14 * s, -80 * s);
        c.lineTo(46 * s, 30 * s); c.lineTo(-46 * s, 30 * s); c.closePath(); c.fill();
      }
      // 身体
      var bodyGrad = c.createLinearGradient(0, -20 * s, 0, 30 * s);
      bodyGrad.addColorStop(0, o.color); bodyGrad.addColorStop(1, '#1a1226');
      c.fillStyle = bodyGrad;
      c.beginPath();
      c.moveTo(-24 * s, 30 * s); c.lineTo(-16 * s, -14 * s);
      c.lineTo(16 * s, -14 * s); c.lineTo(24 * s, 30 * s); c.closePath(); c.fill();
      c.strokeStyle = 'rgba(255,255,255,.15)'; c.lineWidth = 1; c.stroke();
      // 头
      c.fillStyle = '#c8b8e0';
      if (o.persona === 'aggr') { // 尖角头
        c.beginPath(); c.moveTo(-16 * s, -14 * s); c.lineTo(0, -44 * s); c.lineTo(16 * s, -14 * s); c.closePath(); c.fill();
      } else if (o.persona === 'bluff') { // 宽檐礼帽
        c.beginPath(); c.arc(0, -22 * s, 13 * s, Math.PI, 0); c.fill();
        c.fillStyle = o.color;
        c.fillRect(-20 * s, -26 * s, 40 * s, 4 * s);
        c.fillRect(-10 * s, -38 * s, 20 * s, 12 * s);
      } else { // 圆头（tight / player）
        c.beginPath(); c.arc(0, -22 * s, 13 * s, Math.PI, 0); c.fill();
        if (o.persona === 'player') { c.fillStyle = o.color; c.fillRect(-13 * s, -27 * s, 26 * s, 6 * s); } // 棒球帽
        if (o.persona === 'tight') { // 眼镜
          c.strokeStyle = '#7dd3fc'; c.lineWidth = 1.5;
          c.beginPath(); c.arc(-5 * s, -20 * s, 4 * s, 0, Math.PI * 2); c.stroke();
          c.beginPath(); c.arc(5 * s, -20 * s, 4 * s, 0, Math.PI * 2); c.stroke();
          c.beginPath(); c.moveTo(-1 * s, -20 * s); c.lineTo(1 * s, -20 * s); c.stroke();
        }
      }
      // 眼睛（发光，会眨）
      var ey = o.persona === 'aggr' ? -22 * s : -20 * s;
      c.fillStyle = o.color;
      c.shadowColor = o.color; c.shadowBlur = 8;
      if (blink) { c.fillRect(-8 * s, ey, 6 * s, 1.5); c.fillRect(2 * s, ey, 6 * s, 1.5); }
      else {
        c.beginPath(); c.arc(-5 * s, ey, 2.6 * s, 0, Math.PI * 2); c.fill();
        c.beginPath(); c.arc(5 * s, ey, 2.6 * s, 0, Math.PI * 2); c.fill();
      }
      c.shadowBlur = 0;
      c.restore();
      // 名牌 + 筹码
      c.save();
      c.textAlign = 'center'; c.font = Math.max(10, 11 * s) + 'px monospace';
      c.fillStyle = o.folded ? 'rgba(138,123,160,.5)' : '#d8c8f0';
      c.fillText(o.name, x, y + 44 * s);
      c.font = Math.max(9, 10 * s) + 'px monospace';
      c.fillStyle = '#7dd87d';
      c.fillText((o.chipsLabel || '') + '', x, y + 57 * s);
      c.restore();
    },
    // 摊牌庆祝：金色筹码喷泉
    confetti(c, w, h, t) {
      for (var i = 0; i < 18; i++) {
        var ang = (i / 18) * Math.PI * 2 + t * 0.02;
        var r = 30 + (t * 1.4 + i * 20) % 130;
        var px = w / 2 + Math.cos(ang) * r, py = h * 0.46 + Math.sin(ang) * r * 0.5;
        c.fillStyle = i % 2 ? '#f0c674' : '#ffd98a';
        c.beginPath(); c.ellipse(px, py, 5, 2.5, ang, 0, Math.PI * 2); c.fill();
      }
    }
  }
};

// ---------- 大厅（BaseGame：loop 只为驱动活动赌桌的 update） ----------
class CasinoHub extends BaseGame {
  constructor(c) {
    super(c);
    this.container = c;
    this.root = document.createElement('div');
    this.root.style.cssText = 'position:relative;width:100%;min-height:520px;background:#08040d;color:#e6d9f2;font-family:inherit;overflow:hidden';
    // 场景层：房间霓虹背景（canvas 铺满，DOM 面板浮在上面）
    this.scene = document.createElement('canvas');
    this.scene.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:0';
    this.root.appendChild(this.scene);
    this.sceneCtx = this.scene.getContext('2d');
    this.t = 0;
    this.panel = document.createElement('div');
    this.panel.style.cssText = 'position:relative;z-index:1;padding:14px 16px;box-sizing:border-box;min-height:520px';
    this.root.appendChild(this.panel);
    this.container.appendChild(this.root);
    this.state = 'lobby';
    this.table = null;
    this.tableId = null;
    // ?table=xxx（直达/自动化）：脚本全部加载完后注册表同步可用，构造即入座
    this.autoTable = new URLSearchParams(location.search).get('table') || '';
    this.bot = new URLSearchParams(location.search).get('bot') === '1';
    this._unsub = Casino.wallet.onChange(this._onChips.bind(this));
    this.renderLobby();
    if (this.autoTable && Casino.get(this.autoTable)) this.openTable(this.autoTable);
  }

  _onChips(v) {
    var el = this.panel.querySelector('.casino-balance');
    if (el) el.textContent = v.toLocaleString();
  }

  _el(tag, css, text) {
    var e = document.createElement(tag);
    if (css) e.style.cssText = css;
    if (text !== undefined) e.textContent = text;
    return e;
  }

  renderLobby() {
    this.state = 'lobby';
    this.table = null;
    this.tableId = null;
    this.panel.innerHTML = '';
    // 顶栏：标题 + 余额 + 救济金
    var bar = this._el('div', 'display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px');
    bar.appendChild(this._el('div', 'font-size:20px;font-weight:700;color:#f0c674', '🎰 算力赌坊'));
    bar.appendChild(this._el('div', 'font-size:12px;color:#8a7ba0', '算力筹码'));
    var bal = this._el('div', 'casino-balance', Casino.wallet.get().toLocaleString());
    bal.style.cssText = 'font-size:20px;font-weight:700;color:#7dd87d';
    bar.appendChild(bal);
    var bailBtn = this._el('button', 'margin-left:auto;padding:6px 14px;border-radius:8px;border:1px solid #6b5a8a;background:#1b1230;color:#d8c8f0;cursor:pointer;font-family:inherit;font-size:12px', '🎁 领救济金 +1000');
    bailBtn.onclick = function () {
      Casino.wallet.bailout();
      toast('救济金 +1000 算力（仅供娱乐）');
      sfx('powerup');
    };
    bar.appendChild(bailBtn);
    this.panel.appendChild(bar);

    // 赌桌网格：已注册的桌自动出现
    var grid = this._el('div', 'display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;max-width:860px');
    Casino.tables().forEach(function (id) {
      var def = Casino.get(id);
      var card = this._el('div', 'border:1px solid #4a3a6a;border-radius:12px;padding:16px;background:#120a1e;cursor:pointer;transition:border-color .15s');
      card.onmouseenter = function () { card.style.borderColor = '#f0c674'; };
      card.onmouseleave = function () { card.style.borderColor = '#4a3a6a'; };
      card.innerHTML = '<div style="font-size:30px">' + def.icon + '</div>' +
        '<div style="font-size:15px;font-weight:700;margin:6px 0 4px">' + def.name + '</div>' +
        '<div style="font-size:12px;color:#9d8cb8;line-height:1.5">' + def.desc + '</div>';
      card.onclick = function () { sfx('click'); this.openTable(id); }.bind(this);
      grid.appendChild(card);
    }, this);
    // 铺垫位：后续会上的桌（架构已就绪，实现即插即用）
    [['⬛', '21 点', '即将开放'], ['🎲', '骰子大小', '即将开放'], ['🍒', '算力老虎机', '即将开放']].forEach(function (ph) {
      var card = this._el('div');
      card.style.cssText = 'border:1px dashed #3a2d52;border-radius:12px;padding:16px;background:#0d0816;opacity:.55';
      card.innerHTML = '<div style="font-size:30px;filter:grayscale(1)">' + ph[0] + '</div>' +
        '<div style="font-size:14px;font-weight:700;margin:6px 0 4px;color:#8a7ba0">' + ph[1] + '</div>' +
        '<div style="font-size:11px;color:#6a5a80">' + ph[2] + '</div>';
      grid.appendChild(card);
    }, this);
    this.panel.appendChild(grid);
    this.panel.appendChild(this._el('div', 'margin-top:18px;font-size:11px;color:#6a5a80', '⚠️ 虚拟算力筹码，仅供娱乐 · 无任何真实货币 · 输光可随时领救济金'));
  }

  openTable(id) {
    var def = Casino.get(id);
    if (!def) return;
    this.state = 'table';
    this.tableId = id;
    this.panel.innerHTML = '';
    this.tableHost = this._el('div');
    this.tableHost.style.cssText = 'width:100%';
    this.panel.appendChild(this.tableHost);
    var self = this;
    this.table = def.create(this.tableHost, {
      wallet: Casino.wallet,
      bot: this.bot,
      exit: function () { self.renderLobby(); }
    });
  }

  update() {
    this.t++;
    if (this.state === 'table' && this.table && this.table.update) this.table.update();
  }
  // 每帧绘制场景背景（房间由大厅画；活动赌桌自绘桌面/人物）
  render() {
    var cv = this.scene, c = this.sceneCtx;
    if (!cv || !c) return;
    var w = cv.clientWidth || 0, h = cv.clientHeight || 0;
    if (!w || !h) return;
    if (cv.width !== w) cv.width = w;
    if (cv.height !== h) cv.height = h;
    var t = this.t;
    Casino.paint.room(c, w, h, t);
    if (this.state === 'table' && this.table && this.table.renderScene) {
      this.table.renderScene(c, w, h, t);
    }
  }

  stop() {
    super.stop();
    if (this.table && this.table.destroy) this.table.destroy();
    if (this._unsub) this._unsub();
  }
}

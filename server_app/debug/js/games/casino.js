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

  // ---------- 场景画师（骗子酒吧风：第一人称昏暗酒馆） ----------
  // 确定性伪随机：道具/粒子位置帧间稳定
  _r(i) { var x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); },
  paint: {
    // 房间：暗木 板墙、红色霓虹招牌、琥珀吊灯、烟雾、酒瓶架（人物与桌面画在其上）
    room(c, w, h, t) {
      var _r = Casino._r;
      // 暖黑底色
      var base = c.createLinearGradient(0, 0, 0, h);
      base.addColorStop(0, '#0d0705'); base.addColorStop(0.55, '#170d08'); base.addColorStop(1, '#070302');
      c.fillStyle = base; c.fillRect(0, 0, w, h);
      // 背墙暗木板（垂直板缝，板色微差）
      var wallY = h * 0.56, planks = 15;
      for (var i = 0; i < planks; i++) {
        var px = (i / planks) * w, pw = w / planks + 1, sh = 0.8 + _r(i) * 0.4;
        c.fillStyle = 'rgb(' + Math.round(56 * sh) + ',' + Math.round(33 * sh) + ',' + Math.round(17 * sh) + ')';
        c.fillRect(px, 0, pw, wallY);
        c.fillStyle = 'rgba(0,0,0,.4)'; c.fillRect(px + pw - 2, 0, 2, wallY);
      }
      // 横梁
      c.fillStyle = 'rgba(16,8,4,.92)';
      c.fillRect(0, h * 0.045, w, h * 0.022);
      c.fillRect(0, h * 0.345, w, h * 0.016);
      // 后方吧台酒瓶架（左右两段剪影 + 瓶身高光）
      [[w * 0.045, w * 0.235], [w * 0.765, w * 0.955]].forEach(function (seg, si) {
        var by = h * 0.30, bw = seg[1] - seg[0];
        c.fillStyle = 'rgba(10,5,3,.9)';
        c.fillRect(seg[0], h * 0.175, bw, by - h * 0.175);
        for (var b = 0; b < 7; b++) {
          var bx = seg[0] + 8 + (b / 7) * (bw - 20) + _r(b * 7 + si) * 6;
          var bh = h * (0.055 + _r(b + si * 3) * 0.035);
          c.fillStyle = 'rgba(26,13,7,.95)';
          c.fillRect(bx, by - bh, 9, bh);
          c.fillRect(bx + 2.5, by - bh - 7, 4, 7);
          c.fillStyle = 'rgba(255,190,110,.16)';
          c.fillRect(bx + 2, by - bh + 4, 1.6, bh * 0.55);
        }
        c.fillStyle = 'rgba(255,190,110,.05)';
        c.fillRect(seg[0], by, bw, 3);
      });
      // 红色霓虹招牌（闪烁）
      var flick = 0.8 + 0.2 * Math.sin(t * 0.11) * Math.sin(t * 0.023 + 1.7);
      if (flick < 0.55) flick = 0.55; // 濒坏灯管的最低亮度
      c.save();
      c.globalAlpha = flick;
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.font = '700 ' + Math.max(16, w * 0.036) + 'px monospace';
      c.shadowColor = '#ff3b30'; c.shadowBlur = 26;
      c.fillStyle = '#ffb0a8';
      c.fillText('算 力 赌 坊', w / 2, h * 0.062);
      c.font = Math.max(8, w * 0.012) + 'px monospace';
      c.shadowBlur = 12;
      c.fillStyle = '#ff8a80';
      c.fillText('~  L I A R \' S   B A R  ~', w / 2, h * 0.062 + Math.max(16, w * 0.036) * 0.8);
      c.restore();
      // 中央暖光域（主吊灯的氛围光晕）
      var amb = c.createRadialGradient(w / 2, h * 0.38, 10, w / 2, h * 0.38, w * 0.72);
      amb.addColorStop(0, 'rgba(255,190,110,.30)');
      amb.addColorStop(0.4, 'rgba(190,110,50,.12)');
      amb.addColorStop(1, 'rgba(0,0,0,0)');
      c.fillStyle = amb; c.fillRect(0, 0, w, h);
      // 吊灯 ×3：中央大 + 两侧小（电线 + 灯罩 + 灯泡辉光 + 下照光锥）
      Casino.paint._lamp(c, w / 2, h * 0.155, w * 0.055, t, 0);
      Casino.paint._lamp(c, w * 0.215, h * 0.20, w * 0.038, t, 2.1);
      Casino.paint._lamp(c, w * 0.785, h * 0.20, w * 0.038, t, 4.2);
      // 烟雾（大而淡的椭圆，缓慢横移上升）
      for (var sI = 0; sI < 7; sI++) {
        var drift = (t * (0.08 + _r(sI) * 0.10) + sI * 300) % (w + 400) - 200;
        var sy = h * 0.42 - ((t * (0.10 + _r(sI + 9) * 0.15) + sI * 130) % (h * 0.5));
        c.fillStyle = 'rgba(200,170,140,' + (0.018 + 0.014 * Math.sin(t * 0.02 + sI)) + ')';
        c.beginPath();
        c.ellipse(w * 0.5 + (drift - w / 2) * (0.5 + _r(sI + 4) * 0.8), sy, w * 0.16, h * 0.05, 0, 0, Math.PI * 2);
        c.fill();
      }
      // 琥珀浮尘
      for (var d = 0; d < 22; d++) {
        var fx = (( _r(d) + t * 0.00006 * (1 + d % 3)) % 1) * w;
        var fy = h * (0.08 + _r(d + 50) * 0.5) - (t * 0.012 * (1 + d % 4)) % (h * 0.5);
        if (fy < 0) fy += h * 0.6;
        c.fillStyle = 'rgba(255,200,120,' + (0.05 + 0.09 * Math.abs(Math.sin(t * 0.03 + d))) + ')';
        c.beginPath(); c.arc(fx, fy, 1.4, 0, Math.PI * 2); c.fill();
      }
    },
    // 吊灯：电线 + 锥形灯罩 + 灯泡 + 下照光锥（亮度轻微波动）
    _lamp(c, x, y, r, t, seed) {
      var sway = Math.sin(t * 0.012 + seed) * 3;
      var bright = 0.82 + 0.18 * Math.sin(t * 0.07 + seed * 3);
      c.save();
      c.translate(sway, 0);
      // 电线
      c.strokeStyle = 'rgba(8,4,2,.9)'; c.lineWidth = 2;
      c.beginPath(); c.moveTo(x, 0); c.lineTo(x, y - r * 0.7); c.stroke();
      // 下照光锥
      var cone = c.createLinearGradient(x, y, x, y + r * 9);
      cone.addColorStop(0, 'rgba(255,200,120,' + (0.13 * bright) + ')');
      cone.addColorStop(1, 'rgba(255,200,120,0)');
      c.fillStyle = cone;
      c.beginPath();
      c.moveTo(x - r * 0.6, y); c.lineTo(x + r * 0.6, y);
      c.lineTo(x + r * 4.6, y + r * 9); c.lineTo(x - r * 4.6, y + r * 9); c.closePath(); c.fill();
      // 锥形灯罩
      var shade = c.createLinearGradient(x, y - r * 0.7, x, y + r * 0.5);
      shade.addColorStop(0, '#3a2412'); shade.addColorStop(1, '#140a05');
      c.fillStyle = shade;
      c.beginPath();
      c.moveTo(x - r * 0.28, y - r * 0.7); c.lineTo(x + r * 0.28, y - r * 0.7);
      c.lineTo(x + r, y + r * 0.45); c.lineTo(x - r, y + r * 0.45); c.closePath(); c.fill();
      c.strokeStyle = 'rgba(255,200,120,' + (0.5 * bright) + ')'; c.lineWidth = 1.2;
      c.beginPath();
      c.moveTo(x - r, y + r * 0.45); c.lineTo(x + r, y + r * 0.45); c.stroke();
      // 灯泡
      c.fillStyle = 'rgba(255,225,160,' + (0.85 * bright + 0.15) + ')';
      c.shadowColor = '#ffc87a'; c.shadowBlur = 18 * bright;
      c.beginPath(); c.arc(x, y + r * 0.55, r * 0.24, 0, Math.PI * 2); c.fill();
      c.restore();
    },
    // 扑克桌：第一人称透视——远端桌沿在画面中部，近端出血铺满底部（红棕木 + 暗红呢 + 受光亮边 + 道具）
    table(c, w, h) {
      var _r = Casino._r;
      var ty = h * 0.52;                 // 远端桌沿
      var x0 = w * 0.13, x1 = w * 0.87;  // 远端左右
      var bx0 = -w * 0.08, bx1 = w * 1.08; // 近端（出血）
      // 桌面透视梯形
      var wood = c.createLinearGradient(0, ty, 0, h);
      wood.addColorStop(0, '#8a4a1d'); wood.addColorStop(0.3, '#6e3512'); wood.addColorStop(1, '#241006');
      c.fillStyle = wood;
      c.beginPath();
      c.moveTo(x0, ty); c.lineTo(x1, ty); c.lineTo(bx1, h); c.lineTo(bx0, h); c.closePath();
      c.fill();
      // 木纹（沿透视的弧线）
      c.save();
      c.beginPath();
      c.moveTo(x0, ty); c.lineTo(x1, ty); c.lineTo(bx1, h); c.lineTo(bx0, h); c.closePath();
      c.clip();
      for (var i = 0; i < 10; i++) {
        var yy = ty + Math.pow((i + 0.5) / 10, 1.3) * (h - ty);
        c.strokeStyle = 'rgba(28,11,4,' + (0.10 + 0.12 * _r(i + 3)) + ')';
        c.lineWidth = 1 + _r(i + 41) * 2.2;
        c.beginPath(); c.moveTo(bx0, yy + 20); c.quadraticCurveTo(w / 2, yy - 16, bx1, yy + 20); c.stroke();
      }
      // 暗红呢放牌区（中央椭圆 + 金线）
      var cx = w / 2, cy = h * 0.70, rx = w * 0.315, ry = h * 0.155;
      var felt = c.createRadialGradient(cx, cy - ry * 0.3, ry * 0.15, cx, cy, rx);
      felt.addColorStop(0, '#5c1620'); felt.addColorStop(1, '#26060d');
      c.fillStyle = felt;
      c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.fill();
      c.strokeStyle = 'rgba(240,198,116,.30)'; c.lineWidth = 1.6;
      c.beginPath(); c.ellipse(cx, cy, rx * 0.93, ry * 0.88, 0, 0, Math.PI * 2); c.stroke();
      c.fillStyle = 'rgba(240,198,116,.10)';
      c.font = '700 ' + Math.max(11, w * 0.017) + 'px monospace';
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillText('S H O W   H A N D', cx, cy + ry * 0.02);
      c.restore();
      // 受光桌沿（远端亮边：被吊灯照亮）
      var edge = c.createLinearGradient(0, ty - 5, 0, ty + 30);
      edge.addColorStop(0, 'rgba(255,205,130,.5)'); edge.addColorStop(1, 'rgba(255,205,130,0)');
      c.fillStyle = edge;
      c.beginPath();
      c.moveTo(x0 - w * 0.012, ty - 5); c.lineTo(x1 + w * 0.012, ty - 5);
      c.lineTo(x1 + w * 0.05, ty + 30); c.lineTo(x0 - w * 0.05, ty + 30); c.closePath(); c.fill();
      c.strokeStyle = 'rgba(255,215,150,.55)'; c.lineWidth = 2;
      c.shadowColor = '#ffc87a'; c.shadowBlur = 8;
      c.beginPath(); c.moveTo(x0, ty); c.lineTo(x1, ty); c.stroke();
      c.shadowBlur = 0;
      // 道具：左轮弹壳 ×2、威士忌杯、皱纸条（确定性摆位）
      for (var g = 0; g < 2; g++) {
        var gx = w * (0.30 + g * 0.045), gy = h * (0.585 + g * 0.012);
        c.save(); c.translate(gx, gy); c.rotate(0.5 + g * 0.4);
        var casing = c.createLinearGradient(0, -2, 0, 2);
        casing.addColorStop(0, '#d9a44a'); casing.addColorStop(1, '#8a5a1d');
        c.fillStyle = casing;
        c.fillRect(-9, -2.2, 18, 4.4);
        c.fillStyle = '#6a4314'; c.fillRect(7, -2.2, 2.4, 4.4);
        c.restore();
      }
      // 威士忌杯（近右侧，琥珀酒体）
      var glx = w * 0.735, gly = h * 0.66;
      c.save();
      c.fillStyle = 'rgba(210,140,60,.55)';
      c.beginPath(); c.ellipse(glx, gly, 11, 9, 0, 0, Math.PI * 2); c.fill();
      c.strokeStyle = 'rgba(255,225,170,.5)'; c.lineWidth = 1.4;
      c.beginPath(); c.ellipse(glx, gly, 11, 9, 0, 0, Math.PI * 2); c.stroke();
      c.fillStyle = 'rgba(255,200,120,.14)';
      c.beginPath(); c.ellipse(glx, gly - 9, 9, 3, 0, 0, Math.PI * 2); c.fill();
      c.restore();
      // 皱纸条（左下）
      c.save();
      c.translate(w * 0.135, h * 0.86); c.rotate(-0.35);
      c.fillStyle = 'rgba(214,196,160,.6)';
      c.beginPath();
      c.moveTo(-22, -8); c.quadraticCurveTo(-4, -14, 20, -6);
      c.quadraticCurveTo(26, 2, 12, 8); c.quadraticCurveTo(-8, 13, -22, 6);
      c.closePath(); c.fill();
      c.strokeStyle = 'rgba(60,40,20,.5)'; c.lineWidth = 0.8;
      c.beginPath(); c.moveTo(-14, -2); c.lineTo(12, -1); c.moveTo(-12, 3); c.lineTo(8, 4); c.stroke();
      c.restore();
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

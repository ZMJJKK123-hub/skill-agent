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
  get(id) { return this._tables.get(id); }
};

// ---------- 大厅（BaseGame：loop 只为驱动活动赌桌的 update） ----------
class CasinoHub extends BaseGame {
  constructor(c) {
    super(c);
    this.container = c;
    this.root = document.createElement('div');
    this.root.style.cssText = 'width:100%;min-height:100%;background:#08040d;padding:14px 16px;box-sizing:border-box;color:#e6d9f2;font-family:inherit';
    c.appendChild(this.root);
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
    var el = this.root.querySelector('.casino-balance');
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
    this.root.innerHTML = '';
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
    this.root.appendChild(bar);

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
    this.root.appendChild(grid);
    this.root.appendChild(this._el('div', 'margin-top:18px;font-size:11px;color:#6a5a80', '⚠️ 虚拟算力筹码，仅供娱乐 · 无任何真实货币 · 输光可随时领救济金'));
  }

  openTable(id) {
    var def = Casino.get(id);
    if (!def) return;
    this.state = 'table';
    this.tableId = id;
    this.root.innerHTML = '';
    this.tableHost = this._el('div');
    this.tableHost.style.cssText = 'width:100%';
    this.root.appendChild(this.tableHost);
    var self = this;
    this.table = def.create(this.tableHost, {
      wallet: Casino.wallet,
      bot: this.bot,
      exit: function () { self.renderLobby(); }
    });
  }

  update() {
    if (this.state === 'table' && this.table && this.table.update) this.table.update();
  }
  render() {} // 全 DOM 渲染，无 canvas 帧

  stop() {
    super.stop();
    if (this.table && this.table.destroy) this.table.destroy();
    if (this._unsub) this._unsub();
  }
}

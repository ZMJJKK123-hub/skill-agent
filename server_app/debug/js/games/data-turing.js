// data-turing.js — Game 7: Node wiring puzzle

class DataTuring extends BaseGame {
  constructor(c) {
    super(c);
    this.container = c;
    this.w = 640;
    this.h = 400;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'game-canvas';
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    c.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this._mm = e => {
      var r = this.canvas.getBoundingClientRect();
      this.mouseX = (e.clientX - r.left) * (this.w / r.width);
      this.mouseY = (e.clientY - r.top) * (this.h / r.height);
    };
    this._md = e => {
      this._downX = this.mouseX;
      this._downY = this.mouseY;
      this.dragging = this.findNode(this.mouseX, this.mouseY);
    };
    this._mu = () => {
      // click (no drag) = connect/disconnect flow; drag = move node
      var moved = dist(this.mouseX, this.mouseY, this._downX, this._downY);
      if (moved < 6 && this.dragging !== null) this.toggleConnect(this.dragging);
      this.dragging = null;
    };
    this._ctx = e => {
      e.preventDefault();
      var r = this.canvas.getBoundingClientRect();
      var mx = (e.clientX - r.left) * (this.w / r.width);
      var my = (e.clientY - r.top) * (this.h / r.height);
      var idx = this.findNode(mx, my);
      if (idx === null) return;
      if (this.nodes[idx].type === 'source' || this.nodes[idx].type === 'target') { toast('Cannot remove source/target'); return; }
      this.removeNode(idx);
    };
    this.canvas.addEventListener('mousemove', this._mm);
    this.canvas.addEventListener('mousedown', this._md);
    this.canvas.addEventListener('mouseup', this._mu);
    this.canvas.addEventListener('contextmenu', this._ctx);
    this.btn = document.createElement('button');
    this.btn.textContent = 'RUN';
    this.btn.className = 'btn btn-p';
    this.btn.style.cssText = 'margin:8px auto;display:block;padding:8px 24px;border-radius:8px;border:1px solid var(--green-d);background:var(--card);color:var(--green);cursor:pointer;font-family:inherit';
    this.btn.onclick = () => this.run();
    c.appendChild(this.btn);
    // Add node buttons
    var btnRow = document.createElement('div');
    btnRow.style.cssText = 'display:flex;gap:8px;justify-content:center;margin-bottom:4px';
    var addSplit = document.createElement('button');
    addSplit.textContent = '+ Splitter';
    addSplit.style.cssText = 'padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card);color:var(--purple);cursor:pointer;font-family:inherit;font-size:.75em';
    addSplit.onclick = () => this.addNode('splitter');
    var addAdder = document.createElement('button');
    addAdder.textContent = '+ Adder';
    addAdder.style.cssText = 'padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card);color:var(--cyan);cursor:pointer;font-family:inherit;font-size:.75em';
    addAdder.onclick = () => this.addNode('adder');
    var addMult = document.createElement('button');
    addMult.textContent = '+ x2';
    addMult.style.cssText = 'padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card);color:var(--orange);cursor:pointer;font-family:inherit;font-size:.75em';
    addMult.onclick = () => this.addNode('multiplier');
    btnRow.appendChild(addSplit);
    btnRow.appendChild(addAdder);
    btnRow.appendChild(addMult);
    c.appendChild(btnRow);
    this.reset();
  }

  reset() {
    // Randomize target: even or odd
    this.target = Math.random() < 0.5 ? 'even' : 'odd';
    this.nodes = [
      { x: 80, y: this.h / 2, type: 'source', label: 'SRC' },
      { x: 560, y: this.h / 2, type: 'target', label: 'TGT' },
      { x: 300, y: 120, type: 'splitter', label: '/2' },
      { x: 300, y: 280, type: 'adder', label: '+1' },
      { x: 420, y: 200, type: 'multiplier', label: 'x2' },
    ];
    this.connections = [
      { from: 0, to: 2 },
      { from: 0, to: 3 },
      { from: 2, to: 1 },
      { from: 3, to: 4 },
      { from: 4, to: 1 },
    ];
    this.balls = [];
    this.score = 0;
    this.runningSim = false;
    this.mouseX = 0;
    this.mouseY = 0;
    this.dragging = null;
    this.tick = 0;
    this.success = false;
    this.fail = false;
    this.bestScore = parseInt(localStorage.getItem('dtBest') || '0');
    this.trailParticles = [];
    this.level = 1;
    this.puzzleSolved = 0;
    this._timeouts = [];
    this.connectFrom = null;
  }

  addNode(type) {
    var idx = this.nodes.length;
    var labels = { 'splitter': '/2', 'adder': '+1', 'multiplier': 'x2', 'negate': 'n!' };
    this.nodes.push({ x: rnd(150, 480), y: rnd(60, 340), type: type, label: labels[type] || type });
    this.connections.push({ from: 0, to: idx });
    this.connections.push({ from: idx, to: 1 });
    toast('Added ' + type);
  }

  removeNode(idx) {
    var type = this.nodes[idx].type;
    this.connections = this.connections
      .filter(function(c) { return c.from !== idx && c.to !== idx; })
      .map(function(c) { return { from: c.from > idx ? c.from - 1 : c.from, to: c.to > idx ? c.to - 1 : c.to }; });
    this.nodes.splice(idx, 1);
    toast('Removed ' + type);
  }

  findNode(x, y) {
    for (var i = 0; i < this.nodes.length; i++) {
      if (dist(x, y, this.nodes[i].x, this.nodes[i].y) < 25) return i;
    }
    return null;
  }

  // Click node A then node B to toggle a connection A->B.
  // Source only sends, target only receives.
  toggleConnect(idx) {
    if (this.connectFrom === null) {
      if (this.nodes[idx].type === 'target') { toast('Target only receives — pick a source node'); return; }
      this.connectFrom = idx;
      toast('From ' + this.nodes[idx].label + ' → now click destination');
      return;
    }
    var from = this.connectFrom;
    this.connectFrom = null;
    if (from === idx) { toast('Connection cancelled'); return; }
    if (this.nodes[idx].type === 'source') { toast('Source only sends — pick a destination'); return; }
    var exists = this.connections.some(function(c) { return c.from === from && c.to === idx; });
    if (exists) {
      this.connections = this.connections.filter(function(c) { return !(c.from === from && c.to === idx); });
      toast('Disconnected ' + this.nodes[from].label + ' → ' + this.nodes[idx].label);
    } else {
      this.connections.push({ from: from, to: idx });
      sfx('click');
      toast('Connected ' + this.nodes[from].label + ' → ' + this.nodes[idx].label);
    }
  }

  run() {
    if (this.runningSim) return;
    this.balls = [];
    this.runningSim = true;
    this.success = false;
    this.fail = false;
    var delay = 0;
    var self = this;
    for (var i = 1; i <= 10; i++) {
      (function(val) {
        self._timeouts.push(setTimeout(function() { self.spawnBall(val); }, delay));
      })(i);
      delay += 600;
    }
    this._timeouts.push(setTimeout(function() { self.checkResult(); }, delay + 2000));
  }

  spawnBall(val) {
    this.balls.push({ x: this.nodes[0].x, y: this.nodes[0].y, val: val, path: [0], progress: 0, done: false, color: null });
  }

  update() {
    this.tick++;
    if (this.dragging !== null) {
      this.nodes[this.dragging].x = clamp(this.mouseX, 20, this.w - 20);
      this.nodes[this.dragging].y = clamp(this.mouseY, 20, this.h - 20);
    }
    var self = this;
    this.balls.forEach(function(b) {
      if (b.done) return;
      if (b.path.length > 12) { b.done = true; b.color = '#5a6a7a'; return; } // cycle guard
      var conn = self.connections.find(function(c) { return c.from === b.path[b.path.length - 1]; });
      if (!conn) { b.done = true; return; }
      var from = self.nodes[conn.from];
      var to = self.nodes[conn.to];
      b.progress += 0.01; // 速度减半
      if (b.progress >= 1) {
        b.progress = 0;
        b.path.push(conn.to);
        var node = self.nodes[conn.to];
        if (node.type === 'splitter') b.val = Math.floor(b.val / 2);
        if (node.type === 'adder') b.val += 1;
        if (node.type === 'multiplier') b.val *= 2;
        if (node.type === 'negate') b.val = b.val * -1 + 1;
        if (node.type === 'target') {
          b.done = true;
          var correct = (self.target === 'even' && b.val % 2 === 0) || (self.target === 'odd' && b.val % 2 === 1);
          if (correct) { self.score += 10 * self.level; b.color = '#00ff9f'; }
          else { b.color = '#ff3355'; self.fail = true; }
        }
        return;
      }
      b.x = lerp(from.x, to.x, b.progress);
      b.y = lerp(from.y, to.y, b.progress);
      // Trail particles
      if (self.tick % 3 === 0) self.trailParticles.push({ x: b.x, y: b.y, life: 15 });
    });
    // Update trail
    this.trailParticles.forEach(function(p) { p.life--; });
    this.trailParticles = this.trailParticles.filter(function(p) { return p.life > 0; });
  }

  render() {
    var c = this.ctx;
    c.fillStyle = '#050810';
    c.fillRect(0, 0, this.w, this.h);
    var self = this;
    this.connections.forEach(function(conn) {
      var f = self.nodes[conn.from];
      var t = self.nodes[conn.to];
      c.strokeStyle = '#1a2332';
      c.lineWidth = 3;
      c.beginPath();
      c.moveTo(f.x, f.y);
      var mx = (f.x + t.x) / 2;
      c.bezierCurveTo(mx, f.y, mx, t.y, t.x, t.y);
      c.stroke();
    });
    // Render trail particles
    this.trailParticles.forEach(function(p) {
      c.fillStyle = 'rgba(0,212,255,' + (p.life / 15 * 0.4) + ')';
      c.beginPath();
      c.arc(p.x, p.y, 3, 0, Math.PI * 2);
      c.fill();
    });
    this.balls.forEach(function(b) {
      c.fillStyle = b.color || '#00d4ff';
      c.beginPath();
      c.arc(b.x, b.y, 10, 0, Math.PI * 2);
      c.fill();
      c.fillStyle = '#fff';
      c.font = '10px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(b.val, b.x, b.y);
    });
    this.nodes.forEach(function(n) {
      var colors = { source: '#00ff9f', target: '#ffcc00', splitter: '#bb44ff', adder: '#00d4ff', multiplier: '#ff8800', negate: '#ff44aa' };
      c.fillStyle = colors[n.type] || '#00d4ff';
      c.beginPath();
      c.arc(n.x, n.y, 22, 0, Math.PI * 2);
      c.fill();
      c.strokeStyle = '#fff';
      c.lineWidth = 1;
      c.stroke();
      c.fillStyle = '#fff';
      c.font = '9px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(n.label, n.x, n.y);
      // Pending connection source: pulsing ring + dashed line to cursor
      if (self.connectFrom !== null && self.nodes[self.connectFrom] === n) {
        c.strokeStyle = '#00ff9f';
        c.lineWidth = 2;
        c.globalAlpha = 0.6 + 0.4 * Math.sin(self.tick * 0.15);
        c.beginPath();
        c.arc(n.x, n.y, 30, 0, Math.PI * 2);
        c.stroke();
        c.globalAlpha = 1;
        c.setLineDash([4, 4]);
        c.beginPath();
        c.moveTo(n.x, n.y);
        c.lineTo(self.mouseX, self.mouseY);
        c.stroke();
        c.setLineDash([]);
      }
    });
    c.fillStyle = '#5a6a7a';
    c.font = '11px monospace';
    c.textAlign = 'left';
    c.fillText('Target: ' + (this.target === 'even' ? 'Only EVEN' : 'Only ODD') + '  Score: ' + this.score + '  Lv.' + this.level, 8, 18);
    c.fillStyle = '#3a4a5a';
    c.font = '9px monospace';
    c.textAlign = 'right';
    c.fillText('Best: ' + this.bestScore, this.w - 8, 18);
    c.textAlign = 'left';
    c.fillText('Click 2 nodes to connect/cut · drag to move · right-click removes helper · RUN to test', 8, 34);
    if (this.success) {
      c.fillStyle = '#00ff9f'; c.font = '20px monospace'; c.textAlign = 'center';
      c.fillText('CORRECT! Lv.' + this.level, this.w / 2, this.h / 2);
    }
    if (this.fail) {
      c.fillStyle = '#ff3355'; c.font = '20px monospace'; c.textAlign = 'center';
      c.fillText('WRONG OUTPUT', this.w / 2, this.h / 2);
      c.fillStyle = '#5a6a7a'; c.font = '10px monospace';
      c.fillText('Rearrange nodes and try again', this.w / 2, this.h / 2 + 24);
    }
  }

  checkResult() {
    this.runningSim = false;
    if (this.fail) {
      sfx('lose');
      this.fail = false; // allow retry
    } else {
      this.success = true; sfx('win');
      this.puzzleSolved++;
      this.level++;
      if (this.score > this.bestScore) { this.bestScore = this.score; localStorage.setItem('dtBest', this.bestScore); }
      toast('Logic verified! Lv.' + this.level);
      // 关卡过渡：暂停游戏，等玩家点"继续"（保留 auto-advance 重置逻辑）
      if (window.__showLevelTransition) {
        window.__showLevelTransition('LEVEL ' + this.level + ' · PASS');
      }
      // Auto-advance to next puzzle after delay
      var self = this;
      this._timeouts.push(setTimeout(function() {
        self.success = false;
        self.fail = false;
        self.balls = [];
        self.target = Math.random() < 0.5 ? 'even' : 'odd';
        // Shuffle node positions
        self.nodes.forEach(function(n) {
          if (n.type !== 'source' && n.type !== 'target') {
            n.x = rnd(150, 480);
            n.y = rnd(60, 340);
          }
        });
      }, 2000));
    }
  }

  stop() {
    super.stop();
    (this._timeouts || []).forEach(clearTimeout);
    this._timeouts = [];
    this.connectFrom = null;
    this.canvas.removeEventListener('mousemove', this._mm);
    this.canvas.removeEventListener('mousedown', this._md);
    this.canvas.removeEventListener('mouseup', this._mu);
    this.canvas.removeEventListener('contextmenu', this._ctx);
  }
}
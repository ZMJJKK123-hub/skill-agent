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
    this._md = () => { this.dragging = this.findNode(this.mouseX, this.mouseY); };
    this._mu = () => { this.dragging = null; };
    this.canvas.addEventListener('mousemove', this._mm);
    this.canvas.addEventListener('mousedown', this._md);
    this.canvas.addEventListener('mouseup', this._mu);
    this.btn = document.createElement('button');
    this.btn.textContent = 'RUN';
    this.btn.className = 'btn btn-p';
    this.btn.style.cssText = 'margin:8px auto;display:block;padding:8px 24px;border-radius:8px;border:1px solid var(--green-d);background:var(--card);color:var(--green);cursor:pointer;font-family:inherit';
    this.btn.onclick = () => this.run();
    c.appendChild(this.btn);
    this.reset();
  }

  reset() {
    this.nodes = [
      { x: 80, y: 80, type: 'source', label: 'SRC' },
      { x: 80, y: 320, type: 'target', label: 'TGT' },
      { x: 300, y: 120, type: 'splitter', label: 'even?' },
      { x: 300, y: 280, type: 'adder', label: '+1' }
    ];
    this.connections = [
      { from: 0, to: 2 },
      { from: 0, to: 3 },
      { from: 2, to: 1 },
      { from: 3, to: 1 }
    ];
    this.balls = [];
    this.score = 0;
    this.runningSim = false;
    this.target = 'even';
    this.mouseX = 0;
    this.mouseY = 0;
    this.dragging = null;
    this.tick = 0;
    this.success = false;
    this.fail = false;
  }

  findNode(x, y) {
    for (var i = 0; i < this.nodes.length; i++) {
      if (dist(x, y, this.nodes[i].x, this.nodes[i].y) < 25) return i;
    }
    return null;
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
        setTimeout(function() { self.spawnBall(val); }, delay);
      })(i);
      delay += 600;
    }
    setTimeout(function() { self.checkResult(); }, delay + 2000);
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
      var conn = self.connections.find(function(c) { return c.from === b.path[b.path.length - 1]; });
      if (!conn) { b.done = true; return; }
      var from = self.nodes[conn.from];
      var to = self.nodes[conn.to];
      b.progress += 0.02;
      if (b.progress >= 1) {
        b.progress = 0;
        b.path.push(conn.to);
        var node = self.nodes[conn.to];
        if (node.type === 'splitter') b.val = Math.floor(b.val / 2);
        if (node.type === 'adder') b.val += 1;
        if (node.type === 'target') {
          b.done = true;
          if (self.target === 'even' && b.val % 2 === 0) { self.score += 10; b.color = '#00ff9f'; }
          else if (self.target === 'odd' && b.val % 2 === 1) { self.score += 10; b.color = '#00ff9f'; }
          else { b.color = '#ff3355'; self.fail = true; }
        }
        return;
      }
      b.x = lerp(from.x, to.x, b.progress);
      b.y = lerp(from.y, to.y, b.progress);
    });
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
      c.fillStyle = n.type === 'source' ? '#00ff9f' : (n.type === 'target' ? '#ffcc00' : (n.type === 'splitter' ? '#bb44ff' : '#00d4ff'));
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
    });
    c.fillStyle = '#5a6a7a';
    c.font = '11px monospace';
    c.textAlign = 'left';
    c.fillText('Target: ' + (this.target === 'even' ? 'Even numbers' : 'Odd numbers') + '  Score: ' + this.score, 8, 18);
    c.fillText('Drag nodes to route, click RUN', 8, 34);
    if (this.success) { c.fillStyle = '#00ff9f'; c.font = '20px monospace'; c.textAlign = 'center'; c.fillText('CORRECT!', this.w / 2, this.h / 2); }
    if (this.fail) { c.fillStyle = '#ff3355'; c.font = '20px monospace'; c.textAlign = 'center'; c.fillText('WRONG OUTPUT', this.w / 2, this.h / 2); }
  }

  checkResult() {
    this.runningSim = false;
    if (this.fail) { sfx('lose'); }
    else { this.success = true; sfx('win'); toast('Logic verified!'); }
  }

  stop() {
    super.stop();
    this.canvas.removeEventListener('mousemove', this._mm);
    this.canvas.removeEventListener('mousedown', this._md);
    this.canvas.removeEventListener('mouseup', this._mu);
  }
}
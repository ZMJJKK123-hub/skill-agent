// snake-2048.js — Game 3: Snake meets 2048 with auto-path

class Snake2048 extends BaseGame {
  constructor(c) {
    super(c);
    this.cols = 12;
    this.rows = 12;
    this.cell = 36;
    this.w = this.cols * this.cell;
    this.h = this.rows * this.cell;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'game-canvas';
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    c.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this._kd = e => {
      var k = e.key.toLowerCase();
      var d = this.dir;
      if ((k === 'arrowup' || k === 'w') && d.y !== 1) this.ndir = { x: 0, y: -1 };
      else if ((k === 'arrowdown' || k === 's') && d.y !== -1) this.ndir = { x: 0, y: 1 };
      else if ((k === 'arrowleft' || k === 'a') && d.x !== 1) this.ndir = { x: -1, y: 0 };
      else if ((k === 'arrowright' || k === 'd') && d.x !== -1) this.ndir = { x: 1, y: 0 };
      else if (k === ' ') { e.preventDefault(); if (this.snake.length > 15 && this.autoActive === 0) this.activateAuto(); }
    };
    addEventListener('keydown', this._kd);
    this.reset();
  }

  reset() {
    this.snake = [{ x: 5, y: 6, v: 2 }, { x: 4, y: 6, v: 2 }];
    this.dir = { x: 1, y: 0 };
    this.ndir = { x: 1, y: 0 };
    this.foods = [];
    this.spawnFood();
    this.spawnFood();
    this.score = 0;
    this.tick = 0;
    this.spd = 8;
    this.autoActive = 0;
    this.autoCooldown = 0;
    this.gameOver = false;
    this.mergeFlash = 0;
    this.mergeAnims = [];
    this.bestScore = parseInt(localStorage.getItem('snBest') || '0');
  }

  spawnFood() {
    var vals = [2, 2, 2, 4, 4, 8];
    var v = vals[rnd(0, vals.length - 1)];
    var x, y;
    do {
      x = rnd(0, this.cols - 1);
      y = rnd(0, this.rows - 1);
    } while (this.snake.some(s => s.x === x && s.y === y) || this.foods.some(f => f.x === x && f.y === y));
    this.foods.push({ x: x, y: y, v: v });
  }

  activateAuto() {
    if (this.autoCooldown > 0) return;
    this.autoActive = 300;
    this.autoCooldown = 600;
    sfx('powerup');
    toast('AUTO-SCRIPT 2.0 ACTIVATED');
  }

  update() {
    this.tick++;
    if (this.autoCooldown > 0) this.autoCooldown--;
    this.mergeAnims.forEach(a => a.life--);
    this.mergeAnims = this.mergeAnims.filter(a => a.life > 0);
    if (this.tick < this.spd) return;
    this.tick = 0;
    this.dir = this.ndir;

    if (this.autoActive > 0) {
      this.autoActive--;
      this.autoPath();
    }

    var head = { x: this.snake[0].x + this.dir.x, y: this.snake[0].y + this.dir.y, v: this.snake[0].v };
    if (head.x < 0 || head.x >= this.cols || head.y < 0 || head.y >= this.rows) { this.die(); return; }
    if (this.snake.some(s => s.x === head.x && s.y === head.y)) { this.die(); return; }

    this.snake.unshift(head);
    var fi = this.foods.findIndex(f => f.x === head.x && f.y === head.y);
    if (fi >= 0) {
      head.v = this.foods[fi].v;
      this.foods.splice(fi, 1);
      this.spawnFood();
      sfx('eat');
      this.merge();
    } else {
      this.snake.pop();
    }

    if (this.snake.some(s => s.v >= 2048)) { this.win(); }
    if (this.mergeFlash > 0) this.mergeFlash--;
  }

  merge() {
    var changed = true;
    while (changed) {
      changed = false;
      for (var i = 0; i < this.snake.length - 1; i++) {
        if (this.snake[i].v === this.snake[i + 1].v) {
          this.snake[i].v *= 2;
          this.score += this.snake[i].v;
          if (this.snake[i].v >= 2048) { sfx('win'); toast('2048 achieved!'); }
          else { sfx('powerup'); }
          this.snake.splice(i + 1, 1);
          changed = true;
          this.mergeFlash = 10;
          this.mergeAnims.push({ x: this.snake[i].x, y: this.snake[i].y, v: this.snake[i].v, life: 20 });
        }
      }
    }
  }

  autoPath() {
    var head = this.snake[0];
    // Priority 1: find food with same value as head
    var target = null, td = 999;
    this.foods.forEach(f => {
      if (f.v === head.v) {
        var d = Math.abs(f.x - head.x) + Math.abs(f.y - head.y);
        if (d < td) { td = d; target = f; }
      }
    });
    // Priority 2: find any food
    if (!target) target = this.foods[0];
    // Priority 3: avoid walls — move toward center
    if (!target) return;
    if (!target) return;
    var dx = target.x - head.x, dy = target.y - head.y;
    if (Math.abs(dx) > Math.abs(dy)) {
      if (dx > 0 && this.dir.x !== -1) this.ndir = { x: 1, y: 0 };
      else if (dx < 0 && this.dir.x !== 1) this.ndir = { x: -1, y: 0 };
      else if (dy > 0 && this.dir.y !== -1) this.ndir = { x: 0, y: 1 };
      else if (dy < 0 && this.dir.y !== 1) this.ndir = { x: 0, y: -1 };
      else { // No valid direction, try to avoid wall
        if (head.x <= 1) this.ndir = { x: 1, y: 0 };
        else if (head.x >= this.cols - 2) this.ndir = { x: -1, y: 0 };
        else this.ndir = { x: 0, y: this.dir.y === 0 ? (Math.random() < 0.5 ? 1 : -1) : this.dir.y };
      }
    } else {
      if (dy > 0 && this.dir.y !== -1) this.ndir = { x: 0, y: 1 };
      else if (dy < 0 && this.dir.y !== 1) this.ndir = { x: 0, y: -1 };
      else if (dx > 0 && this.dir.x !== -1) this.ndir = { x: 1, y: 0 };
      else if (dx < 0 && this.dir.x !== 1) this.ndir = { x: -1, y: 0 };
      else {
        if (head.y <= 1) this.ndir = { x: 0, y: 1 };
        else if (head.y >= this.rows - 2) this.ndir = { x: 0, y: -1 };
        else this.ndir = { x: this.dir.x === 0 ? (Math.random() < 0.5 ? 1 : -1) : this.dir.x, y: 0 };
      }
    }
  }

  render() {
    var c = this.ctx;
    var scanning = this.autoActive > 0;
    c.fillStyle = scanning ? '#0a0010' : '#050810';
    c.fillRect(0, 0, this.w, this.h);
    if (scanning) {
      // High contrast red-blue scanlines
      c.strokeStyle = 'rgba(0,100,255,.08)';
      c.lineWidth = 1;
      for (var sy = 0; sy < this.h; sy += 4) {
        c.beginPath(); c.moveTo(0, sy); c.lineTo(this.w, sy); c.stroke();
      }
      c.strokeStyle = 'rgba(255,0,100,.1)';
      for (var sx = 0; sx < this.w; sx += 4) {
        c.beginPath(); c.moveTo(sx, 0); c.lineTo(sx, this.h); c.stroke();
      }
    }
    c.strokeStyle = scanning ? 'rgba(255,0,255,.15)' : 'rgba(0,255,159,.05)';
    c.lineWidth = 1;
    for (var i = 0; i <= this.cols; i++) { c.beginPath(); c.moveTo(i * this.cell, 0); c.lineTo(i * this.cell, this.h); c.stroke(); }
    for (var j = 0; j <= this.rows; j++) { c.beginPath(); c.moveTo(0, j * this.cell); c.lineTo(this.w, j * this.cell); c.stroke(); }

    var colors = { 2: '#1a3a1a', 4: '#2a5a2a', 8: '#0d3a6e', 16: '#1a5a8e', 32: '#5a4a0d', 64: '#7a6a1d', 128: '#4a2a6e', 256: '#6a3a8e', 512: '#6e1a2a' };
    this.foods.forEach(f => {
      c.fillStyle = colors[f.v] || '#1a6e4a';
      c.fillRect(f.x * this.cell + 2, f.y * this.cell + 2, this.cell - 4, this.cell - 4);
      c.fillStyle = '#fff';
      c.font = '12px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(f.v, f.x * this.cell + this.cell / 2, f.y * this.cell + this.cell / 2);
    });

    if (scanning) {
      c.strokeStyle = 'rgba(255,0,255,.4)';
      c.lineWidth = 1;
      c.beginPath();
      c.moveTo(this.snake[0].x * this.cell + this.cell / 2, this.snake[0].y * this.cell + this.cell / 2);
      var ang = this.tick * 0.3;
      c.lineTo(this.snake[0].x * this.cell + this.cell / 2 + Math.cos(ang) * 100, this.snake[0].y * this.cell + this.cell / 2 + Math.sin(ang) * 100);
      c.stroke();
    }

    var sc = { 2: '#3fb950', 4: '#56d364', 8: '#58a6ff', 16: '#79c0ff', 32: '#e3b341', 64: '#bc8cff', 128: '#f778ba', 256: '#ffa657', 512: '#ff8800', 1024: '#ff4444', 2048: '#00ff9f' };
    this.snake.forEach((s, i) => {
      var col = i === 0 ? (scanning ? '#ff00ff' : (sc[s.v] || '#00ff9f')) : (sc[s.v] || '#2ea043');
      if (this.mergeFlash > 0 && i === 0) col = '#fff';
      c.fillStyle = col;
      var scale = 1;
      if (this.mergeFlash > 5 && i === 0) scale = 1 + (this.mergeFlash - 5) * 0.03;
      var sz = (this.cell - 4) * scale;
      var off = (this.cell - sz) / 2;
      c.fillRect(s.x * this.cell + off, s.y * this.cell + off, sz, sz);
      c.fillStyle = '#fff';
      c.font = '11px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(s.v, s.x * this.cell + this.cell / 2, s.y * this.cell + this.cell / 2);
    });

    // Merge pop animations
    this.mergeAnims.forEach(a => {
      var pop = a.life / 20;
      var popScale = 1 + (1 - pop) * 0.6;
      var popSize = this.cell * popScale;
      c.strokeStyle = 'rgba(0,255,159,' + pop + ')';
      c.lineWidth = 2;
      c.strokeRect(a.x * this.cell + (this.cell - popSize) / 2, a.y * this.cell + (this.cell - popSize) / 2, popSize, popSize);
      c.fillStyle = 'rgba(0,255,159,' + (pop * 0.3) + ')';
      c.font = '10px monospace';
      c.textAlign = 'center';
      c.fillText('+' + a.v, a.x * this.cell + this.cell / 2, a.y * this.cell - 4);
    });

    c.fillStyle = '#00ff9f';
    c.font = '14px monospace';
    c.textAlign = 'left';
    c.fillText('Score: ' + this.score + '  Len: ' + this.snake.length, 8, 18);
    c.fillStyle = '#5a6a7a';
    c.font = '9px monospace';
    c.textAlign = 'right';
    c.fillText('Best: ' + this.bestScore, this.w - 8, 18);
    c.textAlign = 'left';
    if (scanning) {
      c.fillStyle = '#ff00ff';
      c.font = '10px monospace';
      c.fillText('AUTO-SCRIPT: ' + this.autoActive + 'f', 8, 34);
    } else if (this.autoCooldown > 0) {
      c.fillStyle = '#5a6a7a';
      c.font = '9px monospace';
      c.fillText('Auto cooldown: ' + this.autoCooldown + 'f', 8, 34);
    } else {
      c.fillStyle = '#5a6a7a';
      c.font = '10px monospace';
      c.fillText('Arrows/WASD, Space=Auto (len>15)', 8, this.h - 8);
    }
  }

  die() {
    this.stop(); sfx('die');
    if (this.score > this.bestScore) { this.bestScore = this.score; localStorage.setItem('snBest', this.bestScore); }
    var c = this.ctx;
    c.fillStyle = 'rgba(0,0,0,.8)';
    c.fillRect(0, 0, this.w, this.h);
    c.fillStyle = '#ff3355';
    c.font = '24px monospace';
    c.textAlign = 'center';
    c.fillText('GAME OVER', this.w / 2, this.h / 2 - 10);
    c.fillStyle = '#c8d6e5';
    c.font = '14px monospace';
    c.fillText('Score: ' + this.score, this.w / 2, this.h / 2 + 16);
    c.fillStyle = '#5a6a7a';
    c.font = '12px monospace';
    c.fillText('Best: ' + this.bestScore, this.w / 2, this.h / 2 + 34);
  }

  win() {
    this.stop(); sfx('win');
    if (this.score > this.bestScore) { this.bestScore = this.score; localStorage.setItem('snBest', this.bestScore); }
    var c = this.ctx;
    c.fillStyle = 'rgba(0,0,0,.8)';
    c.fillRect(0, 0, this.w, this.h);
    c.fillStyle = '#00ff9f';
    c.font = '24px monospace';
    c.textAlign = 'center';
    c.fillText('2048 ACHIEVED!', this.w / 2, this.h / 2 - 10);
    c.fillStyle = '#c8d6e5';
    c.font = '14px monospace';
    c.fillText('Score: ' + this.score, this.w / 2, this.h / 2 + 16);
    c.fillStyle = '#5a6a7a';
    c.font = '12px monospace';
    c.fillText('Best: ' + this.bestScore, this.w / 2, this.h / 2 + 34);
  }

  stop() { super.stop(); removeEventListener('keydown', this._kd); }
}
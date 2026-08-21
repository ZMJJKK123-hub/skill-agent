// dimension-parkour.js — Game 5: Gravity-flip dino runner

class DimensionParkour extends BaseGame {
  constructor(c) {
    super(c);
    this.w = 640;
    this.h = 240;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'game-canvas';
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    this.canvas.style.width = '100%';
    c.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this._kd = e => {
      if (e.key === ' ' || e.key === 'ArrowUp' || e.key === 'w') { e.preventDefault(); this.jump(); }
      if (e.key === 'ArrowDown' || e.key === 's') { this.flipGravity(); }
      if (e.key === 'Enter') { this.activateFlatWorld(); }
    };
    this._tap = () => this.jump();
    addEventListener('keydown', this._kd);
    this.canvas.addEventListener('click', this._tap);
    this.reset();
  }

  reset() {
    this.player = { x: 80, y: 200, vy: 0, r: 12, onGround: true };
    this.obstacles = [];
    this.particles = [];
    this.score = 0;
    this.spd = 3;
    this.gravityDir = 1;
    this.tick = 0;
    this.gameOver = false;
    this.flatWorld = 0;
    this.energy = 0;
    this.bgOffset = 0;
  }

  jump() {
    if (this.gameOver) return;
    if (this.player.onGround) { this.player.vy = -9 * this.gravityDir; this.player.onGround = false; sfx('eat'); }
  }

  activateFlatWorld() {
    if (this.gameOver || this.energy < 100) return;
    this.flatWorld = 480; // ~8 seconds at 60fps
    this.energy = 0;
    this.spd = 6;
    sfx('powerup');
    toast('SUPER FLAT WORLD!');
  }

  flipGravity() {
    if (this.gameOver || !this.player.onGround) return;
    this.gravityDir *= -1;
    this.player.vy = 0;
    sfx('powerup');
    this.canvas.style.filter = this.gravityDir < 0 ? 'invert(1)' : 'none';
    for (var i = 0; i < 10; i++) this.particles.push({ x: this.player.x, y: this.player.y, vx: (Math.random() - 0.5) * 4, vy: (Math.random() - 0.5) * 4, life: 20, color: '#bb44ff' });
  }

  update() {
    if (this.gameOver) return;
    this.tick++;
    this.player.vy += 0.5 * this.gravityDir;
    this.player.y += this.player.vy;
    var groundY = this.gravityDir > 0 ? this.h - this.player.r : this.player.r;
    if (this.gravityDir > 0) {
      if (this.player.y >= groundY) { this.player.y = groundY; this.player.vy = 0; this.player.onGround = true; }
    } else {
      if (this.player.y <= groundY) { this.player.y = groundY; this.player.vy = 0; this.player.onGround = true; }
    }
    this.bgOffset += this.spd;
    if (this.flatWorld > 0) {
      this.flatWorld--;
      this.obstacles = this.obstacles.filter(o => o.x > 0);
      if (this.flatWorld <= 0) { this.spd = 3; } // restore speed
    } else if (this.tick % Math.max(40, 90 - Math.floor(this.score / 5)) === 0) {
      this.spawnObstacle();
    }
    this.obstacles.forEach(o => { o.x -= this.spd; });
    this.obstacles = this.obstacles.filter(o => o.x > -50);
    var self = this;
    this.obstacles.forEach(o => {
      if (self.player.x + self.player.r > o.x && self.player.x - self.player.r < o.x + o.w && self.player.y + self.player.r > o.y && self.player.y - self.player.r < o.y + o.h) { self.die(); }
    });
    if (this.tick % 6 === 0) { this.score++; this.energy = Math.min(100, this.energy + 1); }
    this.particles.forEach(p => { p.x += p.vx; p.y += p.vy; p.life--; });
    this.particles = this.particles.filter(p => p.life > 0);
    if (this.spd < 6 && this.tick % 200 === 0) this.spd += 0.2;
  }

  spawnObstacle() {
    var h = rnd(20, 50);
    var y = this.gravityDir > 0 ? this.h - h : 0;
    this.obstacles.push({ x: this.w, y: y, h: h, w: rnd(15, 30), type: Math.random() < 0.2 ? 'tall' : 'normal' });
  }

  render() {
    var c = this.ctx;
    c.fillStyle = '#050810';
    c.fillRect(0, 0, this.w, this.h);
    c.save();
    if (this.flatWorld > 0) {
      // Chunk loading effect: green overlay + flashing grid lines
      c.fillStyle = 'rgba(0,255,159,' + (this.flatWorld / 480 * 0.15) + ')';
      c.fillRect(0, 0, this.w, this.h);
      c.strokeStyle = 'rgba(0,255,159,' + (0.3 + 0.2 * Math.sin(this.tick * 0.3)) + ')';
      c.lineWidth = 1;
      var off = this.bgOffset % 40;
      for (var gx = -off; gx < this.w; gx += 40) {
        c.beginPath(); c.moveTo(gx, 0); c.lineTo(gx, this.h); c.stroke();
      }
      for (var gy = 0; gy < this.h; gy += 40) {
        c.beginPath(); c.moveTo(0, gy); c.lineTo(this.w, gy); c.stroke();
      }
    }
    c.fillStyle = this.gravityDir > 0 ? '#1a2332' : '#2a1a32';
    c.fillRect(0, this.h - 4, this.w, 4);
    c.fillRect(0, 0, this.w, 4);
    var bgChars = ['<div','</div','<span','</span','<p>','</p>','{','}','[',']','(',')','=>','&&','||','!=','==','++','--','//','/*','<img','<a ','</a>','404','ERR','<br>','href','class','div=','id='];
    c.fillStyle = 'rgba(0,255,159,.08)';
    c.font = '10px monospace';
    for (var i = 0; i < 20; i++) {
      var x = (i * 32 - this.bgOffset % 32 + this.w) % this.w;
      c.fillText(bgChars[rnd(0, bgChars.length - 1)], x, rnd(10, this.h - 10));
    }
    this.obstacles.forEach(o => {
      c.fillStyle = o.type === 'tall' ? '#ff3355' : '#ff8800';
      c.fillRect(o.x, o.y, o.w, o.h);
    });
    this.particles.forEach(p => {
      c.fillStyle = p.color;
      c.globalAlpha = p.life / 20;
      c.beginPath();
      c.arc(p.x, p.y, 2, 0, Math.PI * 2);
      c.fill();
      c.globalAlpha = 1;
    });
    c.fillStyle = '#00ff9f';
    c.beginPath();
    c.arc(this.player.x, this.player.y, this.player.r, 0, Math.PI * 2);
    c.fill();
    c.strokeStyle = '#00ff9f';
    c.lineWidth = 1;
    c.beginPath();
    c.arc(this.player.x, this.player.y, this.player.r + 4, 0, Math.PI * 2);
    c.stroke();
    c.restore();
    c.fillStyle = '#00ff9f';
    c.font = '14px monospace';
    c.textAlign = 'left';
    c.fillText('Score: ' + this.score, 8, 18);
    c.fillStyle = '#00d4ff';
    c.fillRect(8, 24, 100, 4);
    c.fillStyle = '#1a2332';
    c.fillRect(8, 24, 100, 4);
    c.fillStyle = '#00d4ff';
    c.fillRect(8, 24, this.energy, 4);
    if (this.energy >= 100) { c.fillStyle = '#00ff9f'; c.font = '9px monospace'; c.fillText('ENTER=SUPER FLAT', 114, 28); }
  }

  die() {
    this.stop(); sfx('die');
    this.canvas.style.filter = 'none';
    var c = this.ctx;
    c.fillStyle = 'rgba(0,0,0,.8)';
    c.fillRect(0, 0, this.w, this.h);
    c.fillStyle = '#ff3355';
    c.font = '20px monospace';
    c.textAlign = 'center';
    c.fillText('CRASH', this.w / 2, this.h / 2 - 10);
    c.fillStyle = '#c8d6e5';
    c.font = '12px monospace';
    c.fillText('Score: ' + this.score, this.w / 2, this.h / 2 + 14);
  }

  stop() { super.stop(); removeEventListener('keydown', this._kd); this.canvas.removeEventListener('click', this._tap); this.canvas.style.filter = 'none'; }
}
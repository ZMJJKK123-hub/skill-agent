// dimension-parkour.js — Game 5: Gravity-flip dino runner with super flat world

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
    this.bestScore = parseInt(localStorage.getItem('dpBest') || '0');
    this.reset();
  }

  reset() {
    this.player = { x: 80, y: 200, vy: 0, r: 12, onGround: true, trail: [] };
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
    this.bgChars = [];
    this.initBgChars();
    this.shakeTime = 0;
    this.dashTrail = [];
  }

  initBgChars() {
    this.bgChars = [];
    var tags = ['<div','</div','<span','</span','<p>','</p>','{','}','[',']','(',')','=>','&&','||','!=','==','++','--','//','/*','<img','<a ','</a>','404','ERR','<br>','href','class','div=','id=','null','void','int','var','let','if(','for('];
    for (var i = 0; i < 30; i++) {
      this.bgChars.push({ text: tags[rnd(0, tags.length - 1)], x: i * 30, y: rnd(10, this.h - 10) });
    }
  }

  jump() {
    if (this.gameOver) return;
    if (this.player.onGround) {
      this.player.vy = -9 * this.gravityDir;
      this.player.onGround = false;
      sfx('eat');
      for (var i = 0; i < 5; i++) this.particles.push({ x: this.player.x, y: this.player.y + this.player.r * this.gravityDir, vx: (Math.random() - 0.5) * 3, vy: Math.random() * 2 * this.gravityDir, life: 15, color: '#00ff9f' });
    }
  }

  activateFlatWorld() {
    if (this.gameOver || this.energy < 100) return;
    this.flatWorld = 480;
    this.energy = 0;
    this.spd = 6;
    sfx('powerup');
    toast('SUPER FLAT WORLD!');
    for (var i = 0; i < 20; i++) {
      this.particles.push({ x: this.w / 2, y: this.h / 2, vx: (Math.random() - 0.5) * 8, vy: (Math.random() - 0.5) * 8, life: 30, color: '#00ff9f' });
    }
    this.shakeTime = 8;
  }

  flipGravity() {
    if (this.gameOver || !this.player.onGround) return;
    this.gravityDir *= -1;
    this.player.vy = 0;
    sfx('powerup');
    this.canvas.style.filter = this.gravityDir < 0 ? 'invert(1)' : 'none';
    for (var i = 0; i < 12; i++) this.particles.push({ x: this.player.x, y: this.player.y, vx: (Math.random() - 0.5) * 5, vy: (Math.random() - 0.5) * 5, life: 25, color: '#bb44ff' });
    this.shakeTime = 4;
  }

  update() {
    if (this.gameOver) return;
    this.tick++;
    if (this.shakeTime > 0) this.shakeTime--;

    // Player trail
    if (this.tick % 2 === 0) {
      this.dashTrail.push({ x: this.player.x, y: this.player.y, life: 10 });
      if (this.dashTrail.length > 8) this.dashTrail.shift();
    }
    this.dashTrail.forEach(t => t.life--);
    this.dashTrail = this.dashTrail.filter(t => t.life > 0);

    this.player.vy += 0.5 * this.gravityDir;
    this.player.y += this.player.vy;
    var groundY = this.gravityDir > 0 ? this.h - this.player.r : this.player.r;
    if (this.gravityDir > 0) {
      if (this.player.y >= groundY) { this.player.y = groundY; this.player.vy = 0; this.player.onGround = true; }
    } else {
      if (this.player.y <= groundY) { this.player.y = groundY; this.player.vy = 0; this.player.onGround = true; }
    }

    // Scroll bg chars
    this.bgChars.forEach(function(ch) { ch.x -= this.spd; if (ch.x < -50) { ch.x = this.w + rnd(0, 50); ch.y = rnd(10, this.h - 10); } }.bind(this));
    this.bgOffset += this.spd;

    // Score-based speed up
    var baseSpd = this.flatWorld > 0 ? 6 : (3 + this.score / 150);
    this.spd = Math.min(baseSpd, 8);

    if (this.flatWorld > 0) {
      this.flatWorld--;
      this.obstacles = this.obstacles.filter(o => o.x > 0);
    } else if (this.tick % Math.max(30, 90 - Math.floor(this.score / 4)) === 0) {
      this.spawnObstacle();
    }
    this.obstacles.forEach(o => { o.x -= this.spd; });
    this.obstacles = this.obstacles.filter(o => o.x > -50);

    var self = this;
    var fullScreenObstacle = false;
    this.obstacles.forEach(o => {
      if (o.fullScreen) fullScreenObstacle = true;
      if (self.player.x + self.player.r > o.x && self.player.x - self.player.r < o.x + o.w &&
          self.player.y + self.player.r > o.y && self.player.y - self.player.r < o.y + o.h) {
        self.die();
      }
    });

    if (this.tick % 6 === 0) { this.score++; this.energy = Math.min(100, this.energy + 1); }
    this.particles.forEach(p => { p.x += p.vx; p.y += p.vy; p.life--; });
    this.particles = this.particles.filter(p => p.life > 0);
  }

  spawnObstacle() {
    var type = Math.random();
    var diffMul = 1 + this.score / 100; // difficulty multiplier
    if (type < 0.12) {
      // Full screen obstacle (requires gravity flip)
      this.obstacles.push({ x: this.w, y: 0, h: this.h, w: 20, type: 'fullscreen', fullScreen: true });
    } else if (type < 0.30) {
      // Tall obstacle
      var h = Math.min(rnd(60, 100) * diffMul, this.h - 40);
      var y = this.gravityDir > 0 ? this.h - h : 0;
      this.obstacles.push({ x: this.w, y: y, h: h, w: 20, type: 'tall' });
    } else {
      // Normal obstacle
      var h = rnd(20, 50);
      var y = this.gravityDir > 0 ? this.h - h : 0;
      this.obstacles.push({ x: this.w, y: y, h: h, w: rnd(15, 30), type: 'normal' });
    }
  }

  render() {
    var c = this.ctx;
    var shakeX = this.shakeTime > 0 ? (Math.random() - 0.5) * 4 : 0;
    var shakeY = this.shakeTime > 0 ? (Math.random() - 0.5) * 4 : 0;
    c.save();
    c.translate(shakeX, shakeY);

    c.fillStyle = '#050810';
    c.fillRect(0, 0, this.w, this.h);

    // Super flat world overlay
    if (this.flatWorld > 0) {
      c.fillStyle = 'rgba(0,255,159,' + (this.flatWorld / 480 * 0.12) + ')';
      c.fillRect(0, 0, this.w, this.h);
      c.strokeStyle = 'rgba(0,255,159,' + (0.3 + 0.2 * Math.sin(this.tick * 0.3)) + ')';
      c.lineWidth = 1;
      var off = this.bgOffset % 40;
      for (var gx = -off; gx < this.w; gx += 40) { c.beginPath(); c.moveTo(gx, 0); c.lineTo(gx, this.h); c.stroke(); }
      for (var gy = 0; gy < this.h; gy += 40) { c.beginPath(); c.moveTo(0, gy); c.lineTo(this.w, gy); c.stroke(); }
    }

    // Ground / ceiling
    c.fillStyle = this.gravityDir > 0 ? '#1a2332' : '#2a1a32';
    c.fillRect(0, this.h - 4, this.w, 4);
    c.fillRect(0, 0, this.w, 4);

    // Scrolling HTML background
    c.fillStyle = 'rgba(0,255,159,.08)';
    c.font = '10px monospace';
    this.bgChars.forEach(function(ch) { c.fillText(ch.text, ch.x, ch.y); });

    // Obstacles
    this.obstacles.forEach(function(o) {
      if (o.type === 'fullscreen') {
        c.fillStyle = '#ff3355';
        c.globalAlpha = 0.3;
        c.fillRect(o.x, 0, o.w, this.h);
        c.globalAlpha = 1;
        c.fillStyle = '#ff3355';
        c.font = '10px monospace';
        c.textAlign = 'center';
        c.fillText('FLIP!', o.x + o.w / 2, this.h / 2);
      } else {
        c.fillStyle = o.type === 'tall' ? '#ff3355' : '#ff8800';
        c.fillRect(o.x, o.y, o.w, o.h);
        c.fillStyle = 'rgba(0,0,0,.4)';
        c.font = '7px monospace';
        c.textAlign = 'center';
        c.textBaseline = 'middle';
        c.fillText('ERR', o.x + o.w / 2, o.y + o.h / 2);
      }
    }.bind(this));

    // Particles
    this.particles.forEach(function(p) {
      c.fillStyle = p.color;
      c.globalAlpha = p.life / 25;
      c.beginPath();
      c.arc(p.x, p.y, 2, 0, Math.PI * 2);
      c.fill();
      c.globalAlpha = 1;
    });

    // Dash trail
    this.dashTrail.forEach(function(t, i) {
      c.fillStyle = 'rgba(0,255,159,' + (t.life / 10 * 0.3) + ')';
      c.beginPath();
      c.arc(t.x, t.y, this.player.r * (t.life / 10), 0, Math.PI * 2);
      c.fill();
    }.bind(this));

    // Player cursor
    c.fillStyle = '#00ff9f';
    c.beginPath();
    c.arc(this.player.x, this.player.y, this.player.r, 0, Math.PI * 2);
    c.fill();
    c.strokeStyle = '#00ff9f';
    c.lineWidth = 1;
    c.beginPath();
    c.arc(this.player.x, this.player.y, this.player.r + 4, 0, Math.PI * 2);
    c.stroke();
    // Cursor pointer
    c.fillStyle = '#050810';
    c.font = '10px monospace';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillText('_', this.player.x, this.player.y);

    c.restore();

    // HUD
    c.fillStyle = '#00ff9f';
    c.font = '14px monospace';
    c.textAlign = 'left';
    c.fillText('Score: ' + this.score, 8, 18);
    c.fillStyle = '#5a6a7a';
    c.font = '9px monospace';
    c.textAlign = 'right';
    c.fillText('Best: ' + this.bestScore, this.w - 8, 18);
    c.textAlign = 'left';
    c.fillStyle = '#1a2332';
    c.fillRect(8, 24, 100, 4);
    c.fillStyle = '#00d4ff';
    c.fillRect(8, 24, this.energy, 4);
    if (this.energy >= 100) { c.fillStyle = '#00ff9f'; c.font = '9px monospace'; c.fillText('ENTER=SUPER FLAT', 114, 28); }
    else { c.fillStyle = '#5a6a7a'; c.font = '8px monospace'; c.fillText('Space=jump, Down=flip, Enter=flat', 114, 28); }
  }

  die() {
    this.stop(); sfx('die');
    this.canvas.style.filter = 'none';
    if (this.score > this.bestScore) { this.bestScore = this.score; localStorage.setItem('dpBest', this.bestScore); }
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
    c.fillStyle = '#5a6a7a';
    c.font = '10px monospace';
    c.fillText('Best: ' + this.bestScore, this.w / 2, this.h / 2 + 32);
  }

  stop() { super.stop(); removeEventListener('keydown', this._kd); this.canvas.removeEventListener('click', this._tap); this.canvas.style.filter = 'none'; }
}
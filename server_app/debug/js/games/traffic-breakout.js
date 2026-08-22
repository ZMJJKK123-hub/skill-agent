// traffic-breakout.js — Game 4: Breakout with tunnels + fork + cache bricks

class TrafficBreakout extends BaseGame {
  constructor(c) {
    super(c);
    this.w = 640;
    this.h = 480;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'game-canvas';
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    c.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this._mm = e => {
      var r = this.canvas.getBoundingClientRect();
      var scale = this.w / r.width;
      this.paddle.x = clamp((e.clientX - r.left) * scale - this.paddle.w / 2, 0, this.w - this.paddle.w);
    };
    this._tm = e => {
      e.preventDefault();
      var r = this.canvas.getBoundingClientRect();
      var scale = this.w / r.width;
      this.paddle.x = clamp((e.touches[0].clientX - r.left) * scale - this.paddle.w / 2, 0, this.w - this.paddle.w);
    };
    this.canvas.addEventListener('mousemove', this._mm);
    this.canvas.addEventListener('touchmove', this._tm, { passive: false });
    this.reset();
  }

  reset() {
    this.paddle = { x: 280, y: this.h - 16, w: 80, h: 8 };
    this.ballSpeed = 3;
    this.balls = [{ x: 320, y: this.h - 30, dx: this.ballSpeed, dy: -this.ballSpeed, r: 6 }];
    this.bricks = [];
    this.particles = [];
    this.tunnel = { in: { x: 0, y: 100, active: false }, out: { x: this.w, y: 50, active: false } };
    this.score = 0;
    this.level = 1;
    this.bricksLeft = 0;
    this.tunnelTimer = 0;
    this.bestScore = parseInt(localStorage.getItem('bkBest') || '0');
    this.makeBricks(1);
  }

  makeBricks(lvl) {
    this.bricks = [];
    var rows = Math.min(3 + lvl, 6);
    var cols = 8;
    var pad = 4;
    var bw = (this.w - pad * (cols + 1)) / cols;
    var bh = 14;
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var roll = Math.random();
        var type;
        if (roll < 0.15) type = 'fork';
        else if (roll < 0.25) type = 'cache';
        else if (roll < 0.28 && lvl >= 2) type = 'strong';
        else type = 'normal';
        var hp = type === 'cache' ? 3 : (type === 'strong' ? 2 : 1);
        this.bricks.push({ x: pad + c * (bw + pad), y: 30 + r * (bh + pad), w: bw, h: bh, alive: true, hp: hp, type: type, maxHp: hp });
      }
    }
    this.bricksLeft = this.bricks.length;
  }

  update() {
    var self = this;
    this.balls.forEach(function(b, bi) {
      b.x += b.dx;
      b.y += b.dy;
      if (b.x < b.r || b.x > self.w - b.r) b.dx = -b.dx;
      if (b.y < b.r) b.dy = -b.dy;
      if (b.y > self.h) { self.balls.splice(bi, 1); if (self.balls.length === 0) { self.gameOver(); return; } }
      // Paddle bounce with angle based on hit position
      if (b.y + b.dy >= self.paddle.y && b.x >= self.paddle.x && b.x <= self.paddle.x + self.paddle.w) {
        b.dy = -Math.abs(b.dy);
        // Angle based on where ball hits paddle (center = straight, edges = angled)
        var hitPos = (b.x - self.paddle.x) / self.paddle.w; // 0 to 1
        var angle = (hitPos - 0.5) * 1.2; // -0.6 to +0.6 radians
        var speed = Math.sqrt(b.dx * b.dx + b.dy * b.dy);
        b.dx = Math.sin(angle) * speed;
        b.dy = -Math.abs(Math.cos(angle) * speed);
        sfx('click');
      }
      if (self.tunnel.in.active && dist(b.x, b.y, self.tunnel.in.x, self.tunnel.in.y) < 20) {
        b.x = self.tunnel.out.x;
        b.y = self.tunnel.out.y;
        b.dx *= 1.8;
        b.dy = -Math.abs(b.dy) * 1.8;
        sfx('powerup');
      }
      self.bricks.forEach(function(br) {
        if (!br.alive) return;
        if (b.x >= br.x && b.x <= br.x + br.w && b.y >= br.y && b.y <= br.y + br.h) {
          br.hp--;
          if (br.hp <= 0) {
            br.alive = false;
            var pts = br.type === 'fork' ? 3 : (br.type === 'cache' ? 2 : (br.type === 'strong' ? 2 : 1));
            self.score += pts;
            self.bricksLeft--;
            sfx('hit');
            for (var i = 0; i < 8; i++) {
              var chars = '404 ERR NULL void int return null undefined'.split(' ');
              self.particles.push({ x: br.x + br.w / 2, y: br.y + br.h / 2, vx: (Math.random() - 0.5) * 4, vy: Math.random() * 2, life: 40, char: chars[rnd(0, chars.length - 1)], color: '#f85' });
            }
            if (br.type === 'fork') {
              for (var a = -1; a <= 1; a += 2) { self.balls.push({ x: b.x, y: b.y, dx: b.dx * a, dy: -Math.abs(b.dy), r: 6 }); }
              sfx('powerup');
            }
          } else { sfx('click'); }
          b.dy = -b.dy;
        }
      });
    });
    this.particles.forEach(function(p) { p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.life--; });
    this.particles = this.particles.filter(function(p) { return p.life > 0; });
    this.tunnelTimer++;
    if (this.tunnelTimer > 300) {
      this.tunnelTimer = 0;
      this.tunnel.in.active = true;
      this.tunnel.out.active = true;
      this.tunnel.in.x = rnd(0, 100);
      this.tunnel.in.y = rnd(80, 200);
      this.tunnel.out.x = rnd(this.w - 100, this.w - 20);
      this.tunnel.out.y = rnd(30, 100);
      setTimeout(function() { self.tunnel.in.active = false; self.tunnel.out.active = false; }, 5000);
    }
    if (this.bricksLeft <= 0) {
      this.level++;
      this.ballSpeed = Math.min(7, 3 + (this.level - 1) * 0.5);
      this.makeBricks(this.level);
      this.balls = [{ x: this.w / 2, y: this.h - 30, dx: this.ballSpeed, dy: -this.ballSpeed, r: 6 }];
      sfx('powerup');
      toast('Level ' + this.level + ' · Speed ' + this.ballSpeed.toFixed(1));
    }
  }

  render() {
    var c = this.ctx;
    c.fillStyle = '#050810';
    c.fillRect(0, 0, this.w, this.h);
    this.bricks.forEach(function(b) {
      if (!b.alive) return;
      c.fillStyle = b.type === 'fork' ? '#bb44ff' : (b.type === 'cache' ? '#ffcc00' : (b.type === 'strong' ? '#ff8800' : '#ff3355'));
      if (b.hp < b.maxHp) c.globalAlpha = 0.5 + b.hp / b.maxHp * 0.5;
      c.fillRect(b.x, b.y, b.w, b.h);
      c.globalAlpha = 1;
      c.fillStyle = 'rgba(0,0,0,.5)';
      c.font = '7px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(b.type === 'fork' ? 'FORK' : (b.type === 'cache' ? 'CACHE' : (b.type === 'strong' ? 'TUFF' : 'BUG')), b.x + b.w / 2, b.y + b.h / 2);
    });
    this.particles.forEach(function(p) {
      c.fillStyle = p.color;
      c.globalAlpha = p.life / 30;
      c.font = '8px monospace';
      c.fillText(p.char, p.x, p.y);
      c.globalAlpha = 1;
    });
    if (this.tunnel.in.active) {
      // Pulsing tunnel portals
      var pulse = 0.7 + 0.3 * Math.sin(this.tunnelTimer * 0.2);
      c.strokeStyle = '#00d4ff';
      c.lineWidth = 2;
      c.setLineDash([4, 4]);
      // IN portal
      c.globalAlpha = pulse;
      c.beginPath(); c.arc(this.tunnel.in.x, this.tunnel.in.y, 18, 0, Math.PI * 2); c.stroke();
      c.beginPath(); c.arc(this.tunnel.in.x, this.tunnel.in.y, 14, 0, Math.PI * 2); c.stroke();
      // OUT portal
      c.beginPath(); c.arc(this.tunnel.out.x, this.tunnel.out.y, 18, 0, Math.PI * 2); c.stroke();
      c.beginPath(); c.arc(this.tunnel.out.x, this.tunnel.out.y, 14, 0, Math.PI * 2); c.stroke();
      c.setLineDash([]);
      c.globalAlpha = 1;
      c.fillStyle = '#00d4ff';
      c.font = '8px monospace';
      c.textAlign = 'center';
      c.fillText('PORT:8000', this.tunnel.in.x, this.tunnel.in.y - 24);
      c.fillText('ROUTE', this.tunnel.out.x, this.tunnel.out.y - 24);
    }
    c.fillStyle = '#00ff9f';
    c.fillRect(this.paddle.x, this.paddle.y, this.paddle.w, this.paddle.h);
    this.balls.forEach(function(b) { c.fillStyle = '#00d4ff'; c.beginPath(); c.arc(b.x, b.y, b.r, 0, Math.PI * 2); c.fill(); });
    c.fillStyle = '#00ff9f';
    c.font = '14px monospace';
    c.textAlign = 'left';
    c.fillText('Score: ' + this.score + '  Lv.' + this.level + '  Balls: ' + this.balls.length, 10, 20);
    c.fillStyle = '#5a6a7a';
    c.font = '9px monospace';
    c.textAlign = 'right';
    c.fillText('Best: ' + this.bestScore, this.w - 8, 20);
    c.textAlign = 'left';
  }

  gameOver() {
    this.stop(); sfx('die');
    if (this.score > this.bestScore) { this.bestScore = this.score; localStorage.setItem('bkBest', this.bestScore); }
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

  stop() { super.stop(); this.canvas.removeEventListener('mousemove', this._mm); this.canvas.removeEventListener('touchmove', this._tm); }
}
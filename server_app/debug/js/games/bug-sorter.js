// bug-sorter.js — Game 6: 3-lane rhythm game (A/S/D)

class BugSorter extends BaseGame {
  constructor(c) {
    super(c);
    this.w = 480;
    this.h = 480;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'game-canvas';
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    c.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this._kd = e => {
      var k = e.key.toLowerCase();
      if (k === 'a') this.hit(0);
      else if (k === 's') this.hit(1);
      else if (k === 'd') this.hit(2);
    };
    addEventListener('keydown', this._kd);
    this._click = e => {
      if (!this.cleanupIcon) return;
      var r = this.canvas.getBoundingClientRect();
      var mx = (e.clientX - r.left) * (this.w / r.width);
      var my = (e.clientY - r.top) * (this.h / r.height);
      if (dist(mx, my, this.cleanupIcon.x, this.cleanupIcon.y) < this.cleanupIcon.r + 10) {
        this.globalCleanup();
      }
    };
    this.canvas.addEventListener('click', this._click);
    this.reset();
  }

  reset() {
    this.notes = [];
    this.score = 0;
    this.combo = 0;
    this.maxCombo = 0;
    this.miss = 0;
    this.tick = 0;
    this.spawnRate = 50;
    this.gameOver = false;
    this.judgeLineY = this.h - 60;
    this.lanes = [
      { x: 80, color: '#ff3355', key: 'A' },
      { x: 240, color: '#00d4ff', key: 'S' },
      { x: 400, color: '#ffcc00', key: 'D' }
    ];
    this.judgeText = [];
    this.fireIntensity = 0;
    this.health = 100;
    this.bugCount = 0;
    this.cleanupIcon = null;
    this.cleanupParticles = [];
    this.hitFlash = [0, 0, 0];
    this.bestScore = parseInt(localStorage.getItem('bgBest') || '0');
  }

  update() {
    this.tick++;
    if (this.tick % this.spawnRate === 0) {
      this.spawn();
      this.spawnRate = Math.max(18, 50 - Math.floor(this.score / 15));
      // Occasionally spawn double
      if (this.score > 200 && Math.random() < 0.3) this.spawn();
    }
    // Speed up notes based on score
    var spdBoost = 1 + this.score / 500;
    this.notes.forEach(n => {
      n.y += n.spd * spdBoost;
      if (n.y > this.judgeLineY + 30) {
        this.miss++;
        this.combo = 0;
        this.health -= 5;
        this.judgeText.push({ text: 'MISS', x: this.lanes[n.lane].x, y: this.judgeLineY, life: 30, color: '#ff3355' });
        n.dead = true;
        sfx('die');
        if (this.health <= 0) this.endGame();
      }
    });
    this.notes = this.notes.filter(n => !n.dead && n.y < this.h + 20);

    // Check if context window is overloaded
    this.bugCount = this.notes.length;
    if (this.bugCount >= 8 && !this.cleanupIcon) {
      // Spawn global cleanup variable icon
      this.cleanupIcon = { x: this.w / 2, y: this.h / 2, r: 20, life: 300 };
    }
    if (this.cleanupIcon) {
      this.cleanupIcon.life--;
      if (this.cleanupIcon.life <= 0) this.cleanupIcon = null;
    }

    // Update cleanup particles
    this.cleanupParticles.forEach(function(p) { p.x += p.vx; p.y += p.vy; p.life--; });
    this.cleanupParticles = this.cleanupParticles.filter(function(p) { return p.life > 0; });

    this.judgeText.forEach(j => { j.y -= 1; j.life--; });
    this.judgeText = this.judgeText.filter(j => j.life > 0);
    this.fireIntensity = clamp(this.miss * 2, 0, 100);
    // Decay hit flashes
    for (var i = 0; i < 3; i++) {
      if (this.hitFlash[i] > 0) this.hitFlash[i] -= 0.05;
    }
  }

  spawn() {
    var lane = rnd(0, 2);
    var types = ['UI', 'API', 'SQL'];
    var spd = 3 + Math.random() * 1.5 + this.score / 300;
    // Occasionally spawn fast "critical" bug (bigger, more points)
    var isCritical = this.score > 100 && Math.random() < 0.1;
    this.notes.push({ lane: lane, y: -20, spd: isCritical ? spd * 1.6 : spd, type: isCritical ? 'CRIT' : types[lane], color: isCritical ? '#ff44aa' : this.lanes[lane].color, critical: isCritical, r: isCritical ? 16 : 12 });
  }

  hit(lane) {
    var hits = this.notes.filter(n => n.lane === lane && Math.abs(n.y - this.judgeLineY) < 30);
    if (hits.length > 0) {
      var best = hits.sort(function(a, b) { return Math.abs(a.y - this.judgeLineY) - Math.abs(b.y - this.judgeLineY); }.bind(this))[0];
      best.dead = true;
      var acc = Math.abs(best.y - this.judgeLineY);
      var basePts = best.critical ? 200 : 100;
      if (acc < 10) { this.score += basePts; this.judgeText.push({ text: 'PERFECT', x: this.lanes[lane].x, y: this.judgeLineY, life: 30, color: '#00ff9f' }); }
      else { this.score += Math.floor(basePts / 2); this.judgeText.push({ text: 'GOOD', x: this.lanes[lane].x, y: this.judgeLineY, life: 30, color: '#ffcc00' }); }
      this.combo++;
      this.maxCombo = Math.max(this.maxCombo, this.combo);
      this.hitFlash[lane] = 1;
      // Combo multiplier bonus
      var mult = 1 + Math.floor(this.combo / 10);
      if (this.combo > 0 && this.combo % 5 === 0) { this.score += 50 * mult; sfx('combo'); }
      sfx(best.critical ? 'powerup' : 'eat');
    } else {
      this.miss++;
      this.combo = 0;
      this.health -= 3;
      this.judgeText.push({ text: 'MISS', x: this.lanes[lane].x, y: this.judgeLineY, life: 30, color: '#ff3355' });
      sfx('die');
      if (this.health <= 0) this.endGame();
    }
  }

  render() {
    var c = this.ctx;
    c.fillStyle = '#050810';
    c.fillRect(0, 0, this.w, this.h);
    this.lanes.forEach(function(l, i) {
      c.strokeStyle = l.color + '20';
      c.lineWidth = 2;
      c.beginPath();
      c.moveTo(l.x, 0);
      c.lineTo(l.x, this.h);
      c.stroke();
      // Hit flash glow
      if (this.hitFlash[i] > 0) {
        c.fillStyle = l.color;
        c.globalAlpha = this.hitFlash[i] * 0.3;
        c.fillRect(l.x - 30, this.judgeLineY - 40, 60, 80);
        c.globalAlpha = 1;
      }
    }.bind(this));
    c.strokeStyle = '#00ff9f';
    c.lineWidth = 2;
    c.beginPath();
    c.moveTo(0, this.judgeLineY);
    c.lineTo(this.w, this.judgeLineY);
    c.stroke();
    this.notes.forEach(function(n) {
      c.fillStyle = n.color;
      var w = n.critical ? 70 : 60;
      var h2 = n.critical ? 28 : 24;
      c.fillRect(n.lane * 160 + 80 - w / 2, n.y - h2 / 2, w, h2);
      if (n.critical) {
        c.strokeStyle = '#fff';
        c.lineWidth = 1;
        c.strokeRect(n.lane * 160 + 80 - w / 2, n.y - h2 / 2, w, h2);
      }
      c.fillStyle = '#fff';
      c.font = n.critical ? '11px monospace' : '10px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(n.type, n.lane * 160 + 80, n.y);
    });
    this.judgeText.forEach(function(j) {
      c.fillStyle = j.color;
      c.globalAlpha = j.life / 30;
      c.font = '12px monospace';
      c.textAlign = 'center';
      c.fillText(j.text, j.x, j.y - 20);
      c.globalAlpha = 1;
    });
    // Render cleanup particles
    this.cleanupParticles.forEach(function(p) {
      c.fillStyle = p.color;
      c.globalAlpha = p.life / 40;
      c.beginPath();
      c.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      c.fill();
      c.globalAlpha = 1;
    });
    // Render global cleanup icon
    if (this.cleanupIcon) {
      var pulse = 0.7 + 0.3 * Math.sin(this.tick * 0.2);
      c.fillStyle = 'rgba(0,255,159,' + pulse + ')';
      c.beginPath();
      c.arc(this.cleanupIcon.x, this.cleanupIcon.y, this.cleanupIcon.r, 0, Math.PI * 2);
      c.fill();
      c.strokeStyle = '#00ff9f';
      c.lineWidth = 2;
      c.beginPath();
      c.arc(this.cleanupIcon.x, this.cleanupIcon.y, this.cleanupIcon.r + 5, 0, Math.PI * 2);
      c.stroke();
      c.fillStyle = '#050810';
      c.font = '14px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText('GC', this.cleanupIcon.x, this.cleanupIcon.y);
      c.fillStyle = '#00ff9f';
      c.font = '8px monospace';
      c.fillText('CLICK ME!', this.cleanupIcon.x, this.cleanupIcon.y + 30);
    }
    if (this.fireIntensity > 0) {
      for (var i = 0; i < 3; i++) {
        var x = i * 160 + 80;
        c.fillStyle = 'rgba(255,' + clamp(255 - this.fireIntensity * 2, 0, 255) + ',0,' + (this.fireIntensity / 200) + ')';
        c.beginPath();
        c.moveTo(x - 30, this.h);
        c.lineTo(x - 10, this.h - rnd(10, 30));
        c.lineTo(x + 10, this.h - rnd(10, 30));
        c.lineTo(x + 30, this.h);
        c.fill();
      }
    }
    this.lanes.forEach(function(l) { c.fillStyle = l.color; c.font = '14px monospace'; c.textAlign = 'center'; c.fillText(l.key, l.x, this.h - 20); }.bind(this));
    c.fillStyle = '#00ff9f';
    c.font = '14px monospace';
    c.textAlign = 'left';
    c.fillText('Score: ' + this.score + '  Combo: ' + this.combo + 'x', 8, 18);
    c.fillStyle = '#5a6a7a';
    c.font = '9px monospace';
    c.textAlign = 'right';
    c.fillText('Best: ' + this.bestScore, this.w - 8, 18);
    c.textAlign = 'left';
    c.fillStyle = '#ff3355';
    c.font = '10px monospace';
    c.fillText('HP', 8, 36);
    c.fillStyle = '#1a2332';
    c.fillRect(30, 28, 100, 6);
    c.fillStyle = this.health > 50 ? '#00ff9f' : (this.health > 20 ? '#ffcc00' : '#ff3355');
    c.fillRect(30, 28, this.health, 6);
    c.fillStyle = '#5a6a7a';
    c.font = '9px monospace';
    c.fillText('Bugs: ' + this.bugCount + '/8 = GC', 8, this.h - 8);
  }

  globalCleanup() {
    // Massive combo + particle explosion
    var bonus = this.notes.length * 50;
    this.score += bonus;
    this.combo += this.notes.length;
    this.maxCombo = Math.max(this.maxCombo, this.combo);
    this.judgeText.push({ text: 'GLOBAL CLEANUP +' + bonus, x: this.w / 2, y: this.h / 2, life: 60, color: '#00ff9f' });
    sfx('win');
    // Spawn explosion particles
    for (var i = 0; i < 50; i++) {
      var ang = (i / 50) * Math.PI * 2;
      var spd = 3 + Math.random() * 5;
      this.cleanupParticles.push({ x: this.cleanupIcon.x, y: this.cleanupIcon.y, vx: Math.cos(ang) * spd, vy: Math.sin(ang) * spd, life: 40, color: ['#00ff9f', '#00d4ff', '#ffcc00'][rnd(0, 2)], r: 2 + Math.random() * 3 });
    }
    this.notes = [];
    this.cleanupIcon = null;
    this.health = Math.min(100, this.health + 20);
  }

  endGame() {
    this.stop(); sfx('lose');
    if (this.score > this.bestScore) {
      this.bestScore = this.score;
      localStorage.setItem('bgBest', this.bestScore);
    }
    var c = this.ctx;
    c.fillStyle = 'rgba(0,0,0,.8)';
    c.fillRect(0, 0, this.w, this.h);
    c.fillStyle = '#ff3355';
    c.font = '20px monospace';
    c.textAlign = 'center';
    c.fillText('CONTEXT OVERLOAD', this.w / 2, this.h / 2 - 20);
    c.fillStyle = '#c8d6e5';
    c.font = '14px monospace';
    c.fillText('Score: ' + this.score + '  Max Combo: ' + this.maxCombo + 'x', this.w / 2, this.h / 2 + 10);
    c.fillStyle = '#5a6a7a';
    c.font = '12px monospace';
    c.fillText('Best: ' + this.bestScore, this.w / 2, this.h / 2 + 30);
  }

  stop() { super.stop(); removeEventListener('keydown', this._kd); this.canvas.removeEventListener('click', this._click); }
}
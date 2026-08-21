// server-defense.js — Game 1: Vampire Survivors style tower defense

class ServerDefense extends BaseGame {
  constructor(c) {
    super(c);
    this.w = 640;
    this.h = 480;
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'game-canvas';
    this.canvas.width = this.w;
    this.canvas.height = this.h;
    this.canvas.style.width = '100%';
    c.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    this.keys = {};
    this._kd = e => { this.keys[e.key.toLowerCase()] = true; };
    this._ku = e => { this.keys[e.key.toLowerCase()] = false; };
    addEventListener('keydown', this._kd);
    addEventListener('keyup', this._ku);
    this.bestScore = parseInt(localStorage.getItem('sdBest') || '0');
    this.reset();
  }

  reset() {
    this.player = { x: this.w / 2, y: this.h / 2, r: 12, spd: 2.5, pulse: 0 };
    this.enemies = [];
    this.bullets = [];
    this.particles = [];
    this.shards = [];
    this.score = 0;
    this.kills = 0;
    this.exp = 0;
    this.expMax = 20;
    this.level = 1;
    this.fireTimer = 0;
    this.spawnTimer = 0;
    this.spawnRate = 60;
    this.upgrades = { multi: 1, range: 0, shield: 0, dmg: 1, pierce: 0, regen: 0 };
    this.time = 0;
    this.paused = false;
    this.shakeTime = 0;
    this.shakeMag = 0;
  }

  update() {
    this.time++;
    this.player.pulse = (this.player.pulse + 0.08) % (Math.PI * 2);
    if (this.shakeTime > 0) this.shakeTime--;
    if (this.paused) return;
    var p = this.player;
    if (this.keys['w'] || this.keys['arrowup']) p.y -= p.spd;
    if (this.keys['s'] || this.keys['arrowdown']) p.y += p.spd;
    if (this.keys['a'] || this.keys['arrowleft']) p.x -= p.spd;
    if (this.keys['d'] || this.keys['arrowright']) p.x += p.spd;
    p.x = clamp(p.x, p.r, this.w - p.r);
    p.y = clamp(p.y, p.r, this.h - p.r);

    // Passive regen
    if (this.upgrades.regen > 0 && this.time % 120 === 0) {
      if (this.upgrades.shield < 3) this.upgrades.shield++;
    }

    this.spawnTimer++;
    if (this.spawnTimer >= this.spawnRate) {
      this.spawnTimer = 0;
      this.spawn();
      this.spawnRate = Math.max(15, 60 - this.level * 3);
    }

    this.fireTimer++;
    var fireInterval = Math.max(8, 20 - this.upgrades.multi);
    if (this.fireTimer >= fireInterval) { this.fireTimer = 0; this.fire(); }

    this.bullets.forEach(b => { b.x += b.dx; b.y += b.dy; b.life--; });
    this.bullets = this.bullets.filter(b => b.life > 0 && b.x > -10 && b.x < this.w + 10 && b.y > -10 && b.y < this.h + 10);

    this.enemies.forEach(e => {
      var dx = p.x - e.x, dy = p.y - e.y, d = Math.hypot(dx, dy) || 1;
      e.x += dx / d * e.spd;
      e.y += dy / d * e.spd;
      if (this.upgrades.range > 0 && this.time % 30 === 0) {
        var rd = 60 + this.upgrades.range * 30;
        if (d < rd) {
          e.hp -= 0.5;
          this.spawnParticle(e.x, e.y, 0, 0, 5, '#00d4ff', 3);
        }
      }
    });

    this.bullets.forEach(b => {
      if (b.dead) return;
      this.enemies.forEach(e => {
        if (dist(b.x, b.y, e.x, e.y) < e.r + 4) {
          e.hp -= b.dmg;
          this.spawnParticle(e.x, e.y, 0, 0, 8, '#ff0', 4);
          if (this.upgrades.pierce <= 0) b.dead = true;
          else this.upgrades.pierce--;
        }
      });
    });
    this.bullets = this.bullets.filter(b => !b.dead);

    // Enemy-enemy collision (soft push)
    for (var ai = 0; ai < this.enemies.length; ai++) {
      for (var bi = ai + 1; bi < this.enemies.length; bi++) {
        var ea = this.enemies[ai], eb = this.enemies[bi];
        var d2 = dist(ea.x, ea.y, eb.x, eb.y);
        var minD = ea.r + eb.r;
        if (d2 < minD && d2 > 0) {
          var push = (minD - d2) / minD * 0.5;
          var ang = Math.atan2(eb.y - ea.y, eb.x - ea.x);
          ea.x -= Math.cos(ang) * push;
          ea.y -= Math.sin(ang) * push;
          eb.x += Math.cos(ang) * push;
          eb.y += Math.sin(ang) * push;
        }
      }
    }

    this.enemies = this.enemies.filter(e => {
      if (e.hp <= 0) {
        this.kills++;
        this.score += e.pts;
        this.exp++;
        this.shards.push({ x: e.x, y: e.y, r: 3, life: 60, vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2, pts: e.pts });
        sfx('hit');
        for (var i = 0; i < 12; i++) {
          var ang = (i / 12) * Math.PI * 2;
          var spd = 2 + Math.random() * 3;
          this.spawnParticle(e.x, e.y, Math.cos(ang) * spd, Math.sin(ang) * spd, 20, e.type === '502' ? '#bb44ff' : '#ff8800', Math.random() * 3 + 1);
        }
        this.spawnParticle(e.x, e.y, 0, 0, 12, '#fff', 20);
        this.shakeTime = 4;
        this.shakeMag = 3;
        return false;
      }
      if (dist(p.x, p.y, e.x, e.y) < p.r + e.r) {
        if (this.upgrades.shield > 0) { this.upgrades.shield--; e.hp = 0; this.spawnParticle(p.x, p.y, 0, 0, 15, '#00d4ff', 25); sfx('powerup'); return false; }
        this.gameOver();
        return false;
      }
      return true;
    });

    this.particles.forEach(pt => { pt.x += pt.vx || 0; pt.y += pt.vy || 0; pt.life--; if (pt.r > 0) pt.r *= 0.95; });
    this.particles = this.particles.filter(pt => pt.life > 0);

    this.shards.forEach(s => {
      s.x += s.vx; s.y += s.vy; s.vx *= 0.95; s.vy *= 0.95; s.life--;
      if (dist(p.x, p.y, s.x, s.y) < p.r + 8) { s.collected = true; this.exp++; this.score += 5; sfx('eat'); }
    });
    this.shards = this.shards.filter(s => !s.collected && s.life > 0);

    if (this.exp >= this.expMax) { this.exp = 0; this.expMax = Math.floor(this.expMax * 1.3); this.levelUp(); }
  }

  spawn() {
    var side = rnd(0, 3), x, y;
    if (side === 0) { x = 0; y = rnd(0, this.h); }
    else if (side === 1) { x = this.w; y = rnd(0, this.h); }
    else if (side === 2) { x = rnd(0, this.w); y = 0; }
    else { x = rnd(0, this.w); y = this.h; }
    var roll = Math.random();
    var type;
    if (roll < 0.12 && this.level >= 3) type = '500';
    else if (roll < 0.35) type = '502';
    else type = '404';
    var cfg = {
      '404': { r: 10, hp: 1, spd: 1.2 + this.level * 0.05, pts: 1 },
      '502': { r: 14, hp: 3, spd: 0.6 + this.level * 0.03, pts: 3 },
      '500': { r: 18, hp: 6, spd: 0.4 + this.level * 0.02, pts: 8 },
    };
    var c = cfg[type];
    // Multiple spawn at high level
    var count = this.level >= 5 ? rnd(1, 2) : 1;
    for (var si = 0; si < count; si++) {
      var px = x + (si > 0 ? rnd(-30, 30) : 0);
      var py = y + (si > 0 ? rnd(-30, 30) : 0);
      this.enemies.push({ x: px, y: py, r: c.r, hp: c.hp, spd: c.spd, type: type, pts: c.pts, maxHp: c.hp });
    }
  }

  spawnParticle(x, y, vx, vy, life, color, r) {
    var dead = null;
    for (var i = 0; i < this.particles.length; i++) {
      if (this.particles[i].life <= 0) { dead = this.particles[i]; break; }
    }
    if (dead) {
      dead.x = x; dead.y = y; dead.vx = vx; dead.vy = vy;
      dead.life = life; dead.color = color; dead.r = r || 2;
    } else {
      if (this.particles.length < 400) {
        this.particles.push({ x: x, y: y, vx: vx, vy: vy, life: life, color: color, r: r || 2 });
      }
    }
  }

  fire() {
    var nearest = null, nd = 999;
    this.enemies.forEach(e => { var d = dist(this.player.x, this.player.y, e.x, e.y); if (d < nd) { nd = d; nearest = e; } });
    if (!nearest) return;
    var dx = nearest.x - this.player.x, dy = nearest.y - this.player.y, d = Math.hypot(dx, dy) || 1;
    for (var i = 0; i < this.upgrades.multi; i++) {
      var ang = Math.atan2(dy, dx) + (i - this.upgrades.multi / 2 + 0.5) * 0.1;
      this.bullets.push({ x: this.player.x, y: this.player.y, dx: Math.cos(ang) * 6, dy: Math.sin(ang) * 6, dmg: this.upgrades.dmg, life: 60 });
    }
    sfx('click');
  }

  levelUp() {
    this.paused = true;
    var opts = [
      { n: '+1 Thread', d: 'Extra bullet stream', apply: () => this.upgrades.multi++ },
      { n: 'GC Pulse', d: 'Range damage aura', apply: () => this.upgrades.range++ },
      { n: 'Cache Shield', d: '+1 immunity charge', apply: () => this.upgrades.shield++ },
      { n: 'Overclock', d: 'Double damage', apply: () => this.upgrades.dmg++ },
      { n: 'Piercing', d: 'Bullets pierce 1 enemy', apply: () => this.upgrades.pierce += 1 },
      { n: 'Auto-Repair', d: 'Regen shield over time', apply: () => this.upgrades.regen++ },
    ];
    var cards = opts.sort(() => Math.random() - 0.5).slice(0, 3);
    var ov = document.createElement('div');
    ov.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.88);display:flex;gap:12px;align-items:center;justify-content:center;z-index:10;flex-wrap:wrap';
    cards.forEach(c => {
      var card = document.createElement('div');
      card.style.cssText = 'background:var(--card);border:2px solid var(--green-d);border-radius:8px;padding:20px 16px;width:140px;text-align:center;cursor:pointer;transition:all .15s';
      card.innerHTML = '<div style="font-size:1.1em;color:var(--green);font-weight:700;margin-bottom:6px">' + c.n + '</div><div style="font-size:.7em;color:var(--dim)">' + c.d + '</div>';
      card.onmouseenter = () => { card.style.borderColor = '#00ff9f'; card.style.transform = 'translateY(-3px)'; };
      card.onmouseleave = () => { card.style.borderColor = 'var(--green-d)'; card.style.transform = ''; };
      card.onclick = () => { c.apply(); sfx('powerup'); ov.remove(); this.paused = false; };
      ov.appendChild(card);
    });
    this.container.appendChild(ov);
  }

  render() {
    var c = this.ctx;
    var shakeX = this.shakeTime > 0 ? (Math.random() - 0.5) * this.shakeMag : 0;
    var shakeY = this.shakeTime > 0 ? (Math.random() - 0.5) * this.shakeMag : 0;
    c.save();
    c.translate(shakeX, shakeY);

    c.fillStyle = '#050810';
    c.fillRect(0, 0, this.w, this.h);
    c.strokeStyle = 'rgba(0,255,159,.05)';
    c.lineWidth = 1;
    for (var x = 0; x < this.w; x += 40) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, this.h); c.stroke(); }
    for (var y = 0; y < this.h; y += 40) { c.beginPath(); c.moveTo(0, y); c.lineTo(this.w, y); c.stroke(); }

    // Range aura
    if (this.upgrades.range > 0) {
      var rd = 60 + this.upgrades.range * 30;
      c.strokeStyle = 'rgba(0,212,255,' + (0.05 + 0.03 * Math.sin(this.time * 0.05)) + ')';
      c.lineWidth = 2;
      c.beginPath();
      c.arc(this.player.x, this.player.y, rd, 0, Math.PI * 2);
      c.stroke();
    }

    this.particles.forEach(p => {
      c.beginPath();
      c.arc(p.x, p.y, Math.max(0.5, p.r), 0, Math.PI * 2);
      c.fillStyle = p.color || '#ff0';
      c.globalAlpha = p.life / 15;
      c.fill();
      c.globalAlpha = 1;
    });

    this.shards.forEach(s => {
      c.fillStyle = 'rgba(0,255,159,' + (s.life / 60) + ')';
      c.beginPath();
      c.arc(s.x, s.y, 3, 0, Math.PI * 2);
      c.fill();
      c.fillStyle = 'rgba(0,255,159,.3)';
      c.beginPath();
      c.arc(s.x, s.y, 6, 0, Math.PI * 2);
      c.fill();
    });

    this.enemies.forEach(e => {
      var col = e.type === '502' ? '#bb44ff' : (e.type === '500' ? '#ff8800' : '#ff3355');
      c.fillStyle = col;
      c.beginPath();
      c.arc(e.x, e.y, e.r, 0, Math.PI * 2);
      c.fill();
      // HP bar for multi-hp enemies
      if (e.maxHp > 1) {
        c.fillStyle = '#1a2332';
        c.fillRect(e.x - e.r, e.y - e.r - 6, e.r * 2, 3);
        c.fillStyle = col;
        c.fillRect(e.x - e.r, e.y - e.r - 6, e.r * 2 * (e.hp / e.maxHp), 3);
      }
      c.fillStyle = '#fff';
      c.font = '8px monospace';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillText(e.type, e.x, e.y);
    });

    this.bullets.forEach(b => {
      c.strokeStyle = 'rgba(0,255,159,.3)';
      c.lineWidth = 4;
      c.beginPath();
      c.moveTo(b.x - b.dx * 2, b.y - b.dy * 2);
      c.lineTo(b.x, b.y);
      c.stroke();
      c.fillStyle = '#00ff9f';
      c.beginPath();
      c.arc(b.x, b.y, 3, 0, Math.PI * 2);
      c.fill();
      c.fillStyle = 'rgba(0,255,159,.3)';
      c.beginPath();
      c.arc(b.x, b.y, 6, 0, Math.PI * 2);
      c.fill();
    });

    // Player core with pulsing glow
    var glowR = this.player.r + 4 + Math.sin(this.player.pulse) * 3;
    c.fillStyle = 'rgba(0,255,159,.15)';
    c.beginPath();
    c.arc(this.player.x, this.player.y, glowR + 8, 0, Math.PI * 2);
    c.fill();
    c.fillStyle = '#00ff9f';
    c.beginPath();
    c.arc(this.player.x, this.player.y, this.player.r, 0, Math.PI * 2);
    c.fill();
    c.strokeStyle = '#00ff9f';
    c.lineWidth = 1;
    c.beginPath();
    c.arc(this.player.x, this.player.y, glowR, 0, Math.PI * 2);
    c.stroke();
    if (this.upgrades.shield > 0) {
      c.strokeStyle = 'rgba(0,212,255,.4)';
      c.lineWidth = 2;
      c.beginPath();
      c.arc(this.player.x, this.player.y, this.player.r + 10, 0, Math.PI * 2);
      c.stroke();
      c.fillStyle = '#00d4ff';
      c.font = '9px monospace';
      c.textAlign = 'center';
      c.fillText(this.upgrades.shield, this.player.x, this.player.y - this.player.r - 14);
    }

    c.restore();

    // HUD (no shake)
    c.fillStyle = '#00ff9f';
    c.font = '14px monospace';
    c.textAlign = 'left';
    c.fillText('Score: ' + this.score + '  Kills: ' + this.kills + '  Lv.' + this.level, 10, 20);
    c.fillStyle = '#00d4ff';
    c.font = '10px monospace';
    c.fillText('EXP', 10, 38);
    c.fillStyle = '#1a2332';
    c.fillRect(40, 30, 100, 8);
    c.fillStyle = '#00d4ff';
    c.fillRect(40, 30, 100 * (this.exp / this.expMax), 8);
    c.fillStyle = '#5a6a7a';
    c.font = '9px monospace';
    c.textAlign = 'right';
    c.fillText('Best: ' + this.bestScore, this.w - 10, 20);
    c.textAlign = 'left';
    c.fillText('WASD move, auto-fire, collect shards', 10, this.h - 10);
  }

  gameOver() {
    this.stop();
    sfx('die');
    if (this.score > this.bestScore) {
      this.bestScore = this.score;
      localStorage.setItem('sdBest', this.bestScore);
    }
    var c = this.ctx;
    c.fillStyle = 'rgba(0,0,0,.8)';
    c.fillRect(0, 0, this.w, this.h);
    c.fillStyle = '#ff3355';
    c.font = '28px monospace';
    c.textAlign = 'center';
    c.fillText('SERVER OVERRUN', this.w / 2, this.h / 2 - 20);
    c.fillStyle = '#c8d6e5';
    c.font = '14px monospace';
    c.fillText('Score: ' + this.score + '  Kills: ' + this.kills, this.w / 2, this.h / 2 + 10);
    c.fillStyle = '#5a6a7a';
    c.font = '12px monospace';
    c.fillText('Best: ' + this.bestScore, this.w / 2, this.h / 2 + 30);
    c.fillText('Close and reopen to retry', this.w / 2, this.h / 2 + 50);
  }

  stop() { super.stop(); removeEventListener('keydown', this._kd); removeEventListener('keyup', this._ku); }
}
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
  }

  update() {
    this.tick++;
    if (this.tick % this.spawnRate === 0) {
      this.spawn();
      this.spawnRate = Math.max(20, 50 - Math.floor(this.score / 20));
    }
    this.notes.forEach(n => {
      n.y += n.spd;
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
    this.judgeText.forEach(j => { j.y -= 1; j.life--; });
    this.judgeText = this.judgeText.filter(j => j.life > 0);
    this.fireIntensity = clamp(this.miss * 2, 0, 100);
  }

  spawn() {
    var lane = rnd(0, 2);
    var types = ['UI', 'API', 'SQL'];
    this.notes.push({ lane: lane, y: -20, spd: 3 + Math.random() * 1.5, type: types[lane], color: this.lanes[lane].color });
  }

  hit(lane) {
    var hits = this.notes.filter(n => n.lane === lane && Math.abs(n.y - this.judgeLineY) < 30);
    if (hits.length > 0) {
      var best = hits.sort(function(a, b) { return Math.abs(a.y - this.judgeLineY) - Math.abs(b.y - this.judgeLineY); }.bind(this))[0];
      best.dead = true;
      var acc = Math.abs(best.y - this.judgeLineY);
      if (acc < 10) { this.score += 100; this.judgeText.push({ text: 'PERFECT', x: this.lanes[lane].x, y: this.judgeLineY, life: 30, color: '#00ff9f' }); }
      else { this.score += 50; this.judgeText.push({ text: 'GOOD', x: this.lanes[lane].x, y: this.judgeLineY, life: 30, color: '#ffcc00' }); }
      this.combo++;
      this.maxCombo = Math.max(this.maxCombo, this.combo);
      if (this.combo > 0 && this.combo % 5 === 0) { this.score += 50; sfx('combo'); }
      sfx('eat');
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
    this.lanes.forEach(function(l) {
      c.strokeStyle = l.color + '20';
      c.lineWidth = 2;
      c.beginPath();
      c.moveTo(l.x, 0);
      c.lineTo(l.x, this.h);
      c.stroke();
    }.bind(this));
    c.strokeStyle = '#00ff9f';
    c.lineWidth = 2;
    c.beginPath();
    c.moveTo(0, this.judgeLineY);
    c.lineTo(this.w, this.judgeLineY);
    c.stroke();
    this.notes.forEach(function(n) {
      c.fillStyle = n.color;
      c.fillRect(n.lane * 160 + 50, n.y - 12, 60, 24);
      c.fillStyle = '#fff';
      c.font = '10px monospace';
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
    c.fillStyle = '#ff3355';
    c.font = '10px monospace';
    c.fillText('HP', 8, 36);
    c.fillStyle = '#1a2332';
    c.fillRect(30, 28, 100, 6);
    c.fillStyle = this.health > 50 ? '#00ff9f' : (this.health > 20 ? '#ffcc00' : '#ff3355');
    c.fillRect(30, 28, this.health, 6);
  }

  endGame() {
    this.stop(); sfx('lose');
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
  }

  stop() { super.stop(); removeEventListener('keydown', this._kd); }
}
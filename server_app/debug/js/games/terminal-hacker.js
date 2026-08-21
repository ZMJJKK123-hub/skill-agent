// terminal-hacker.js — Game 2: Decrypt threats

class TerminalHacker extends BaseGame {
  constructor(c) {
    super(c);
    this.container = c;
    this.div = document.createElement('div');
    this.div.className = 'term-hack';
    c.appendChild(this.div);
    this._kd = e => {
      if (e.key === 'Enter') this.exec();
      else if (e.key === 'ArrowUp') { var h = this.history[this.history.length - 1]; if (h) this.input.value = h; }
    };
    addEventListener('keydown', this._kd);
    this.reset();
  }

  reset() {
    this.div.innerHTML = '';
    this.history = [];
    this.threats = [];
    this.timer = 15;
    this.score = 0;
    this.defended = 0;
    this.gameOver = false;
    this.threat = null;
    this.threatTimer = null;
    this.out('=== TERMINAL HACKER v1.0 ===', 'green');
    this.out('Decrypt threats and block them!', 'dim');
    this.out('Type: block <decrypted_text>', 'cyan');
    this.out('', '');
    this.newLine();
    this.spawnThreat();
  }

  out(text, cls) {
    var d = document.createElement('div');
    d.className = 'tl';
    if (cls) d.classList.add('t-' + cls);
    d.textContent = text;
    this.div.appendChild(d);
    this.div.scrollTop = this.div.scrollHeight;
  }

  newLine() {
    var w = document.createElement('div');
    w.className = 'input-row';
    var p = document.createElement('span');
    p.className = 'prompt';
    p.textContent = 'hack@defense:~$';
    this.input = document.createElement('input');
    this.input.className = 'input';
    this.input.spellcheck = false;
    this.input.autocomplete = 'off';
    w.appendChild(p);
    w.appendChild(this.input);
    this.div.appendChild(w);
    this.div.scrollTop = this.div.scrollHeight;
    this.input.focus();
  }

  spawnThreat() {
    if (this.gameOver) return;
    var words = ['MEMORY', 'OVERFLOW', 'SEGFAULT', 'NULLPTR', 'RACECOND', 'DEADLOCK', 'BUFFERS', 'STACKHEAP', 'INFINITE', 'TIMEOUT'];
    var word = words[rnd(0, words.length - 1)];
    var methods = [
      function(w) { return w.split('').reverse().join(''); },
      function(w) { try { return btoa(w); } catch(e) { return w; } },
      function(w) { return w.split('').map(function(c, i) { return i % 2 ? c : c.toLowerCase(); }).join(''); }
    ];
    var method = methods[rnd(0, methods.length - 1)];
    var encoded = method(word);
    this.threat = { word: word, encoded: encoded };
    this.timer = 15;
    this.out('THREAT DETECTED [' + (this.threats.length + 1) + ']', 'red');
    this.out('  Encrypted: ' + encoded, 'yellow');
    this.out('  Decrypt and type: block <plaintext>', 'dim');
    this.out('  Time: 15s', 'dim');
    this.out('', '');
    this.threats.push({ word: word });
    var self = this;
    this.threatTimer = setInterval(function() {
      self.timer--;
      if (self.timer <= 0) self.fail();
    }, 1000);
  }

  exec() {
    var cmd = this.input.value.trim();
    if (!cmd) return;
    this.input.disabled = true;
    this.history.push(cmd);
    var w = document.createElement('div');
    w.className = 'tl';
    w.textContent = 'hack@defense:~$ ' + cmd;
    this.div.replaceChild(w, this.input.parentElement);
    if (cmd.startsWith('block ')) {
      var ans = cmd.slice(6).toUpperCase();
      if (this.threat && ans === this.threat.word) { this.success(); }
      else { this.out('WRONG! Expected: ' + (this.threat ? this.threat.word : '?'), 'red'); this.fail(); }
    } else if (cmd === 'help') {
      this.out('Commands: block <text> | hint | skip', 'cyan');
      this.newLine();
    } else if (cmd === 'hint') {
      this.out('Hint: ' + (this.threat ? this.threat.word[0] + '***' : '?'), 'yellow');
      this.newLine();
    } else if (cmd === 'skip') { this.fail(); }
    else { this.out('Unknown command. Type: help', 'dim'); this.newLine(); }
  }

  success() {
    clearInterval(this.threatTimer);
    this.defended++;
    this.score += 100;
    this.out('', '');
    this.out('########## DEFENDED ##########', 'green');
    this.out('Score: ' + this.score + ' Defended: ' + this.defended, 'cyan');
    this.out('', '');
    this.newLine();
    var self = this;
    setTimeout(function() { self.spawnThreat(); }, 500);
  }

  fail() {
    clearInterval(this.threatTimer);
    if (this.gameOver) return;
    this.gameOver = true;
    this.div.style.animation = 'shake 0.3s';
    setTimeout(() => { this.div.style.animation = ''; }, 300);
    this.out('', '');
    this.out('########## BREACH ##########', 'red');
    this.out('Server compromised! Final score: ' + this.score, 'red');
    this.out('Defended: ' + this.defended, 'dim');
  }

  update() {}
  render() {}

  stop() {
    super.stop();
    clearInterval(this.threatTimer);
    removeEventListener('keydown', this._kd);
  }
}
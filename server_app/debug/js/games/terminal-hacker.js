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
    this.bestScore = parseInt(localStorage.getItem('thBest') || '0');
    this.out('=== TERMINAL HACKER v1.0 ===', 'green');
    this.out('Decrypt threats and block them!', 'dim');
    this.out('Type: block <decrypted_text>', 'cyan');
    this.out('Type: agent init for multi-agent mode', 'dim');
    this.out('Best Score: ' + this.bestScore, 'dim');
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

  outTypewriter(text, cls, callback) {
    var d = document.createElement('div');
    d.className = 'tl';
    if (cls) d.classList.add('t-' + cls);
    this.div.appendChild(d);
    var i = 0;
    var self = this;
    var iv = setInterval(function() {
      if (i < text.length) {
        d.textContent += text[i];
        i++;
        self.div.scrollTop = self.div.scrollHeight;
      } else {
        clearInterval(iv);
        if (callback) callback();
      }
    }, 15);
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
    var self = this;
    this.outTypewriter('THREAT DETECTED [' + (this.threats.length + 1) + ']', 'red', function() {
      self.outTypewriter('  Encrypted: ' + encoded, 'yellow', function() {
        self.out('  Decrypt and type: block <plaintext>', 'dim');
        self.out('  Time: 15s', 'dim');
        self.out('', '');
      });
    });
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
      this.out('Commands:', 'cyan');
      this.out('  block <text>     - Block a threat');
      this.out('  hint             - Get a hint');
      this.out('  agent init       - Launch multi-agent repair');
      this.out('  grep <pattern>   - Search encrypted log');
      this.out('  solve <uuid>     - Submit entity ID');
      this.out('  skip             - Skip current threat');
      this.newLine();
    } else if (cmd === 'hint') {
      this.out('Hint: ' + (this.threat ? this.threat.word[0] + '***' : '?'), 'yellow');
      this.newLine();
    } else if (cmd === 'agent init') {
      this.startMultiAgent();
    } else if (cmd.startsWith('grep ')) {
      this.grepLog(cmd.slice(5));
    } else if (cmd.startsWith('solve ')) {
      this.solveUUID(cmd.slice(6).trim());
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

  startMultiAgent() {
    clearInterval(this.threatTimer);
    this.out('', '');
    this.out('=== MULTI-AGENT REPAIR PROTOCOL ===', 'purple');
    this.out('Launching 3 AI agents...', 'cyan');
    var self = this;
    var agents = ['[Agent-Alpha]', '[Agent-Beta]', '[Agent-Gamma]'];
    var messages = [
      'Scanning log files for entity references...',
      'Found encrypted log dump with UUID embedded.',
      'Analyzing packet headers... suspicious pattern detected.',
    ];
    agents.forEach(function(a, i) {
      setTimeout(function() {
        self.out(a + ' ' + messages[i], 'cyan');
      }, i * 800);
    });
    setTimeout(function() {
      self.uuid = self.genUUID();
      self.encryptedLog = self.genEncryptedLog(self.uuid);
      self.out('', '');
      self.out('=== ENCRYPTED LOG DUMP ===', 'yellow');
      self.out(self.encryptedLog, 'dim');
      self.out('', '');
      self.out('Use: grep <pattern> to find the UUID', 'cyan');
      self.out('Then: solve <uuid>', 'cyan');
      self.newLine();
    }, 2800);
  }

  genUUID() {
    var hex = '0123456789abcdef';
    var parts = [];
    for (var i = 0; i < 32; i++) {
      if (i === 8 || i === 12 || i === 16 || i === 20) parts.push('-');
      parts.push(hex[rnd(0, 15)]);
    }
    return parts.join('');
  }

  genEncryptedLog(uuid) {
    var garbage = ['0xDEADBEEF', 'ERR_TIMEOUT', '0xCAFEBABE', 'STACK_OVERFLOW', 'NULL_REF', 'SEGFAULT', 'HEAP_CORRUPT', '0xBEEF42', 'RACE_COND', 'DEADLOCK'];
    var lines = [];
    for (var i = 0; i < 8; i++) {
      if (i === 4) {
        lines.push('[CRITICAL] entity_id=' + uuid + ' status=corrupted');
      } else {
        lines.push('[' + (i % 2 === 0 ? 'WARN' : 'INFO') + '] ' + garbage[rnd(0, garbage.length - 1)] + ' offset=0x' + rnd(0, 65535).toString(16).toUpperCase());
      }
    }
    lines = lines.sort(function() { return Math.random() - 0.5; });
    return lines.join('\n');
  }

  grepLog(pattern) {
    if (!this.encryptedLog) { this.out('No log to grep. Run "agent init" first.', 'dim'); this.newLine(); return; }
    var lines = this.encryptedLog.split('\n');
    var matches = lines.filter(function(l) { return l.toLowerCase().indexOf(pattern.toLowerCase()) >= 0; });
    if (matches.length > 0) {
      this.out('=== GREP RESULTS ===', 'green');
      matches.forEach(function(m) { this.out(m, 'green'); }.bind(this));
    } else {
      this.out('No matches found for: ' + pattern, 'red');
    }
    this.newLine();
  }

  solveUUID(answer) {
    if (!this.uuid) { this.out('No active UUID challenge. Run "agent init" first.', 'dim'); this.newLine(); return; }
    if (answer === this.uuid) {
      this.out('', '');
      this.out('########## UUID VERIFIED ##########', 'green');
      this.out('All agents confirmed entity resolution.', 'cyan');
      this.score += 500;
      this.defended++;
      this.out('Score: ' + this.score + ' Defended: ' + this.defended, 'cyan');
      this.uuid = null;
      this.encryptedLog = null;
      this.out('', '');
      this.newLine();
      var self = this;
      setTimeout(function() { self.spawnThreat(); }, 500);
    } else {
      this.out('INCORRECT UUID. Try again or use grep.', 'red');
      this.newLine();
    }
  }

  fail() {
    clearInterval(this.threatTimer);
    if (this.gameOver) return;
    this.gameOver = true;
    if (this.score > this.bestScore) { this.bestScore = this.score; localStorage.setItem('thBest', this.bestScore); }
    this.div.style.animation = 'shake 0.3s';
    setTimeout(() => { this.div.style.animation = ''; }, 300);
    this.out('', '');
    this.out('########## BREACH ##########', 'red');
    this.out('Server compromised! Final score: ' + this.score, 'red');
    this.out('Defended: ' + this.defended, 'dim');
    this.out('Best Score: ' + this.bestScore, 'dim');
  }

  update() {}
  render() {}

  stop() {
    super.stop();
    clearInterval(this.threatTimer);
    removeEventListener('keydown', this._kd);
  }
}
// main.js — Dashboard, StateManager, Clock, Log, Konami, Health, App Grid

// ========== STATE MANAGER ==========
const SM = {
  currentGame: null,
  currentInit: null,
  currentTitle: '',
  modalOpen: false,
  cheats: { god: false, gravity: false }
};

function openGame(title, initFn) {
  closeGame();
  $('modalTitle').textContent = title;
  $('modalBody').innerHTML = '';
  SM.modalOpen = true;
  SM.currentInit = initFn;
  SM.currentTitle = title;
  $('modal').classList.add('show');
  const game = initFn($('modalBody'));
  SM.currentGame = game;
  if (game && game.start) game.start();
}

function closeGame() {
  if (SM.currentGame && SM.currentGame.stop) SM.currentGame.stop();
  SM.currentGame = null;
  SM.currentInit = null;
  SM.modalOpen = false;
  $('modal').classList.remove('show');
}

function restartGame() {
  if (!SM.currentInit) return;
  smCurrentStop();
  $('modalBody').innerHTML = '';
  const game = SM.currentInit($('modalBody'));
  SM.currentGame = game;
  if (game && game.start) game.start();
  toast('Restarted ' + SM.currentTitle);
}

function smCurrentStop() {
  if (SM.currentGame && SM.currentGame.stop) SM.currentGame.stop();
}

addEventListener('keydown', function(e) {
  if (!SM.modalOpen) return;
  var tag = (e.target && e.target.tagName) || '';
  if (tag === 'INPUT' || tag === 'TEXTAREA') return; // don't hijack typing (e.g. Terminal Hacker)
  if (e.key === 'Escape') { closeGame(); }
  else if (e.key === 'r' || e.key === 'R') { e.preventDefault(); restartGame(); }
});

// ========== CLOCK + PROGRESS ==========
function startClock() {
  setInterval(() => {
    const d = new Date();
    $('clock').textContent = d.toLocaleTimeString('zh-CN');
  }, 1000);
}

let repairProgress = 0;
function startProgress() {
  setInterval(() => {
    if (repairProgress < 99) repairProgress += Math.random() * 0.3;
    $('progFill').style.width = repairProgress + '%';
    $('progPct').textContent = Math.floor(repairProgress) + '%';
  }, 1000);
}

// ========== SYSTEM LOG ==========
const LOG_MSGS = [
  ['INFO', 'Booting skill-agent core...'],
  ['INFO', 'Loading 169 skills...'],
  ['OK', 'Skills loaded.'],
  ['WARN', 'Memory leak detected in session pool'],
  ['INFO', 'mc_java_sources symlinked (not copied)'],
  ['INFO', 'DeepSeek API connected'],
  ['WARN', 'Thread pool saturation: 87%'],
  ['INFO', 'daemon idle cleanup: killed 3 processes'],
  ['ERROR', 'Connection timeout on port 8001'],
  ['INFO', 'Retrying connection...'],
  ['WARN', 'Deprecated API: getModEventBus()'],
  ['INFO', 'persona.txt synced'],
  ['ERROR', 'Stack overflow in recursive skill loader'],
  ['INFO', 'Auto-compact triggered'],
  ['OK', 'Context compressed: 12k to 3k tokens'],
  ['WARN', 'Rate limit approaching'],
  ['INFO', 'health check: /api/health -> 503'],
  ['ERROR', 'daemon exited unexpectedly'],
  ['INFO', 'Restarting daemon...'],
  ['WARN', 'Context window 89% full'],
  ['INFO', 'Symlink created: docs/agent'],
];

let logIdx = 0;
function addLog() {
  const body = $('logBody');
  const m = LOG_MSGS[logIdx % LOG_MSGS.length];
  logIdx++;
  const d = document.createElement('div');
  d.className = 'log-line ' + m[0].toLowerCase();
  d.textContent = '[' + new Date().toLocaleTimeString('zh-CN', { hour12: false }) + '] ' + m[0] + '  ' + m[1];
  body.appendChild(d);
  body.scrollTop = body.scrollHeight;
  while (body.children.length > 80) body.removeChild(body.firstChild);
}

function startLog() {
  for (let i = 0; i < 15; i++) addLog();
  setInterval(addLog, 2000 + Math.random() * 1500);
}

// ========== BG PARTICLES ==========
function startBgParticles() {
  const cv = $('bgParticles');
  const ctx = cv.getContext('2d');
  let pts = [];

  function resize() {
    cv.width = innerWidth;
    cv.height = innerHeight;
    pts = [];
    for (let i = 0; i < 50; i++) {
      pts.push({
        x: Math.random() * cv.width,
        y: Math.random() * cv.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 1.5 + 0.5
      });
    }
  }
  resize();
  addEventListener('resize', resize);

  function loop() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > cv.width) p.vx = -p.vx;
      if (p.y < 0 || p.y > cv.height) p.vy = -p.vy;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0,255,159,' + (0.1 + p.r / 6) + ')';
      ctx.fill();
    });
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        const d = dist(pts[i].x, pts[i].y, pts[j].x, pts[j].y);
        if (d < 100) {
          ctx.beginPath();
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.strokeStyle = 'rgba(0,255,159,' + (0.04 * (1 - d / 100)) + ')';
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(loop);
  }
  loop();
}

// ========== APP GRID ==========
let APPS = window.APPS || [];

function buildAppGrid() {
  const grid = $('appGrid');
  grid.innerHTML = '';
  APPS.forEach(app => {
    const el = document.createElement('div');
    el.className = 'app-icon';
    el.innerHTML =
      '<span class="icon">' + app.icon + '</span>' +
      '<div class="name">' + app.name + '</div>' +
      '<div class="desc">' + app.desc + '</div>' +
      (app.badge ? '<span class="badge">' + app.badge + '</span>' : '');
    el.onclick = () => { sfx('click'); openGame(app.name, app.init); };
    grid.appendChild(el);
  });
}

// ========== KONAMI CODE ==========
const K_SEQ = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
let kIdx = 0;

function startKonami() {
  addEventListener('keydown', e => {
    let k = e.key;
    if (k === 'b' || k === 'a' || k === 'B' || k === 'A') k = k.toLowerCase();
    if (k === K_SEQ[kIdx]) {
      kIdx++;
      if (kIdx === K_SEQ.length) {
        kIdx = 0;
        fireKonami();
      }
    } else {
      kIdx = 0;
      if (k === K_SEQ[0]) kIdx = 1;
    }
  });
}

function fireKonami() {
  sfx('win');
  $('konamiCheat').classList.add('show');
}

function startCheatButtons() {
  $('cheatGod').onclick = function() {
    SM.cheats.god = !SM.cheats.god;
    this.querySelector('.switch').classList.toggle('on');
    toast(SM.cheats.god ? 'God mode ON' : 'God mode OFF');
  };
  $('cheatGravity').onclick = function() {
    SM.cheats.gravity = !SM.cheats.gravity;
    this.querySelector('.switch').classList.toggle('on');
    if (SM.cheats.gravity) activateGravity();
    else deactivateGravity();
  };
  $('cheatDeploy').onclick = function() {
    this.querySelector('.switch').classList.toggle('on');
    toast('Deploying...');
    setTimeout(() => (location.href = '/'), 1500);
  };
}

// Gravity effect
function activateGravity() {
  const els = document.querySelectorAll('.app-icon, .topbar, .log-panel, .desktop-title');
  els.forEach(el => {
    const r = el.getBoundingClientRect();
    el.classList.add('float-elem');
    el.style.left = r.left + 'px';
    el.style.top = r.top + 'px';
    el.style.width = r.width + 'px';
    el.dataset.vx = '0';
    el.dataset.vy = '0';
    el.dataset.dragging = '0';

    el.addEventListener('mousedown', e => {
      el.dataset.dragging = '1';
      el.dataset.dragX = e.clientX;
      el.dataset.dragY = e.clientY;
    });
    document.addEventListener('mousemove', e => {
      if (el.dataset.dragging === '1') {
        el.style.left = (parseFloat(el.style.left) + e.clientX - parseFloat(el.dataset.dragX)) + 'px';
        el.style.top = (parseFloat(el.style.top) + e.clientY - parseFloat(el.dataset.dragY)) + 'px';
        el.dataset.dragX = e.clientX;
        el.dataset.dragY = e.clientY;
      }
    });
    document.addEventListener('mouseup', () => {
      if (el.dataset.dragging === '1') {
        el.dataset.dragging = '0';
        el.dataset.vx = (Math.random() - 0.5) * 8;
        el.dataset.vy = -Math.random() * 10;
      }
    });
  });
  gravityLoop();
}

function gravityLoop() {
  document.querySelectorAll('.float-elem').forEach(el => {
    if (el.dataset.dragging === '1') return;
    let vx = parseFloat(el.dataset.vx) || 0;
    let vy = parseFloat(el.dataset.vy) || 0;
    vy += 0.5;
    let x = parseFloat(el.style.left) + vx;
    let y = parseFloat(el.style.top) + vy;
    if (y > innerHeight - 60) { y = innerHeight - 60; vy *= -0.6; vx *= 0.8; }
    el.style.left = x + 'px';
    el.style.top = y + 'px';
    el.dataset.vx = vx;
    el.dataset.vy = vy;
  });
  if (SM.cheats.gravity) requestAnimationFrame(gravityLoop);
}

function deactivateGravity() { location.reload(); }

// ========== HEALTH POLLING ==========
function checkHealth() {
  fetch('/api/health', { signal: AbortSignal.timeout(5000) })
    .then(r => {
      if (r.ok) {
        $('hDot').className = 'hdot green';
        $('hText').textContent = 'Service restored';
        setTimeout(() => (location.href = '/'), 2000);
      } else {
        $('hDot').className = 'hdot red';
        $('hText').textContent = 'Maintaining...';
      }
    })
    .catch(() => {
      $('hDot').className = 'hdot red';
      $('hText').textContent = 'Maintaining...';
    });
}

function startHealth() {
  checkHealth();
  setInterval(checkHealth, 15000);
  $('homeBtn').onclick = () => {
    fetch('/api/health', { signal: AbortSignal.timeout(5000) })
      .then(r => { if (r.ok) location.href = '/'; else toast('Still under maintenance...'); })
      .catch(() => toast('Still under maintenance...'));
  };
}

// ========== INIT ==========
function init() {
  // sound toggle
  $('soundBtn').onclick = function() {
    sndOn = !sndOn;
    this.textContent = sndOn ? '🔊' : '🔇';
    if (sndOn) { ensureAudio(); aCtx.resume(); beep(660, 0.05, 0.05); }
  };

  // modal close
  $('modalClose').onclick = closeGame;

  startClock();
  startProgress();
  startLog();
  startBgParticles();
  startKonami();
  startCheatButtons();
  startHealth();
  buildAppGrid();
}

document.addEventListener('DOMContentLoaded', init);
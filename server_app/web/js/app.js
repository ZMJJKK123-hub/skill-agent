/* ============================================================
   app.js — 主控制器
   状态机、事件绑定、轮询调度、文件树、历史记录。
   ============================================================ */

(() => {
  "use strict";

  // ---------- 状态 ----------
  const state = {
    apiKey: "",
    game: "minecraft",
    sessionId: null,
    taskStarted: false,
    eventCursor: null,
    seenEventIds: new Set(),
    polling: false,
    timerInterval: null,
    startTime: null,
    finished: false,
  };

  // 示例提示词
  const TEMPLATES = {
    weapon: "新增一把水晶长剑武器 MOD：拥有高攻击力与独特附魔效果，附带可合成的配方（需要水晶与铁锭），并生成对应的物品贴图资源。",
    food: "添加一种魔法果实食物 MOD：使用后可恢复大量生命与饱食度，并赋予短暂的速度提升效果，通过稀有掉落或特定结构获取。",
    block: "制作一种发光矿石方块 MOD：在特定群系自然生成，开采掉落稀有材料，可用于合成高级装备，方块本身会发光。",
  };

  const $ = (id) => document.getElementById(id);

  // ---------- 视图切换 ----------
  function switchView(view) {
    $("view-workbench").classList.toggle("hidden", view !== "workbench");
    $("view-history").classList.toggle("hidden", view !== "history");
    document.querySelectorAll(".nav-link").forEach((el) => {
      el.classList.toggle("active", el.dataset.view === view);
    });
    if (view === "history") renderHistory();
  }

  // ---------- 步骤切换 ----------
  function showStep(n) {
    for (let i = 1; i <= 3; i++) {
      $(`step${i}`).classList.toggle("active", i === n);
    }
    document.querySelectorAll(".step-chip").forEach((chip) => {
      const num = Number(chip.dataset.chip);
      chip.classList.toggle("active", num === n);
      chip.classList.toggle("done", num < n);
    });
  }

  // ---------- 历史记录 ----------
  function renderHistory() {
    const list = $("historyList");
    const history = UI.loadHistory();
    list.innerHTML = "";
    if (!history.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "还没有历史记录。完成一次生成后，会话会出现在这里。";
      list.appendChild(empty);
      return;
    }
    history.forEach((h) => {
      const item = document.createElement("div");
      item.className = "history-item";
      item.innerHTML = `
        <div class="h-game">${UI.escapeHtml(h.game)}</div>
        <div class="h-prompt">${UI.escapeHtml(h.prompt)}</div>
        <div class="h-meta">${h.elapsed ? "耗时 " + UI.formatDuration(h.elapsed) : ""}${
          h.fileCount != null ? " · " + h.fileCount + " 个文件" : ""
        } · ${h.date || ""}</div>
        <div class="h-actions">
          <button class="btn btn-ghost btn-sm" data-act="download" data-sid="${h.sessionId}">下载</button>
          <button class="btn btn-ghost btn-sm" data-act="resume" data-sid="${h.sessionId}">复用会话</button>
        </div>`;
      list.appendChild(item);
    });
  }

  // 事件委托：历史记录按钮
  $("historyList").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-act]");
    if (!btn) return;
    const sid = btn.dataset.sid;
    if (btn.dataset.act === "download") {
      window.open(`/api/download?session_id=${encodeURIComponent(sid)}`, "_blank");
      UI.toast("正在下载 mod.zip", "success");
    } else if (btn.dataset.act === "resume") {
      resumeSession(sid);
    }
  });

  async function resumeSession(sid) {
    try {
      const st = await API.getSession(sid);
      state.sessionId = sid;
      state.finished = st.finished;
      state.taskStarted = st.started_at != null;
      state.apiKey = $("apiKey").value.trim();
      state.game = st.game || "minecraft";
      $("sessionIdLabel").textContent = `会话 ID: ${sid}`;
      showStep(3);
      switchView("workbench");
      if (st.finished) {
        await loadArtifacts();
        finishUI(st);
      } else {
        startTiming(st.started_at);
        startPolling();
      }
      UI.toast("已复用会话", "success");
    } catch (err) {
      UI.toast("复用会话失败：" + err.message, "error");
    }
  }

  // ---------- 游戏模板加载 ----------
  async function loadGames() {
    try {
      const data = await API.getGames();
      const grid = $("gameGrid");
      grid.innerHTML = "";
      data.games.forEach((g) => {
        const card = document.createElement("div");
        card.className = "game-card";
        card.dataset.game = g.id;
        card.dataset.name = g.name;
        card.innerHTML = `
          <div class="game-icon">◆</div>
          <div class="game-name">${UI.escapeHtml(g.name)}</div>
          <div class="game-desc">${UI.escapeHtml(g.description || "可用模板")}</div>`;
        if (g.id === state.game) card.classList.add("selected");
        card.addEventListener("click", () => selectGame(card, g.id));
        grid.appendChild(card);
      });
      $("gameLoading").classList.add("hidden");
    } catch (err) {
      $("gameLoading").textContent = "模板加载失败，已使用默认 Minecraft。";
      $("signal").classList.add("offline");
      $("signal").classList.remove("online");
    }
  }

  function selectGame(card, gameId) {
    document.querySelectorAll(".game-card").forEach((c) => c.classList.remove("selected"));
    card.classList.add("selected");
    state.game = gameId;
  }

  // ---------- 创建会话 ----------
  async function handleCreate() {
    const key = $("apiKey").value.trim();
    if (!key) {
      UI.toast("请填写 DeepSeek API Key", "warn");
      return;
    }
    $("btnCreate").disabled = true;
    try {
      const res = await API.createSession(key, state.game);
      state.sessionId = res.session_id;
      state.apiKey = key;
      $("sessionIdLabel").textContent = `会话 ID: ${res.session_id}`;
      UI.toast("会话创建成功", "success");
      showStep(2);
    } catch (err) {
      UI.toast("创建会话失败：" + err.message, "error");
    } finally {
      $("btnCreate").disabled = false;
    }
  }

  // ---------- 启动生成 ----------
  async function handleRun() {
    const prompt = $("promptInput").value.trim();
    if (!prompt) {
      UI.toast("请填写 MOD 需求描述", "warn");
      return;
    }
    if (!state.sessionId) {
      UI.toast("请先创建会话", "warn");
      return;
    }
    $("btnRun").disabled = true;
    try {
      await API.startTask(state.sessionId, prompt);
      state.taskStarted = true;
      state.finished = false;
      state.eventCursor = null;
      state.seenEventIds.clear();
      $("timeline").innerHTML = "";
      $("eventCount").textContent = "0 个事件";
      $("artifactCard").classList.add("hidden");
      $("btnDownload").classList.add("hidden");
      $("btnRestart").classList.add("hidden");
      $("failureWarn").classList.add("hidden");
      UI.toast("生成任务已启动", "success");
      startTiming();
      startPolling();
      showStep(3);
    } catch (err) {
      UI.toast("启动失败：" + err.message, "error");
      $("btnRun").disabled = false;
    }
  }

  // ---------- 计时 ----------
  function startTiming(ts) {
    state.startTime = ts ? new Date(ts * 1000) : Date.now();
    if (state.timerInterval) clearInterval(state.timerInterval);
    updateTimer();
    state.timerInterval = setInterval(updateTimer, 1000);
  }

  function updateTimer() {
    if (!state.startTime) return;
    const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
    $("timer").textContent = UI.formatDuration(elapsed);
  }

  function stopTiming() {
    if (state.timerInterval) {
      clearInterval(state.timerInterval);
      state.timerInterval = null;
    }
  }

  // ---------- 事件流轮询 ----------
  async function startPolling() {
    if (state.polling) return;
    state.polling = true;
    await pollLoop();
  }

  async function pollLoop() {
    if (!state.sessionId || !state.taskStarted) {
      state.polling = false;
      return;
    }
    try {
      const data = await API.getEvents(state.sessionId, state.eventCursor);
      state.eventCursor = data.cursor;
      appendEvents(data.events);

      const status = await API.getSession(state.sessionId);
      updateStatusUI(status);

      if (status.finished) {
        state.finished = true;
        state.polling = false;
        stopTiming();
        finishUI(status);
        return;
      }
    } catch (err) {
      // 轮询失败不终止，继续尝试（网络抖动场景）
      console.warn("poll error", err);
      if (!state.taskStarted) {
        $("failureWarn").classList.remove("hidden");
        state.polling = false;
        return;
      }
    }
    setTimeout(pollLoop, 1500);
  }

  function appendEvents(events) {
    if (!events || !events.length) return;
    const timeline = $("timeline");
    let added = 0;
    events.forEach((ev) => {
      if (state.seenEventIds.has(ev.id)) return;
      state.seenEventIds.add(ev.id);
      timeline.appendChild(UI.renderEvent(ev));
      added++;
    });
    if (added) {
      const count = state.seenEventIds.size;
      $("eventCount").textContent = `${count} 个事件`;
      // 自动滚动到底部
      timeline.scrollTop = timeline.scrollHeight;
    }
  }

  // ---------- 状态 UI 更新 ----------
  function updateStatusUI(status) {
    const el = $("stateValue");
    const phases = ["thinking", "executing", "generating", "done"];
    if (status.running && status.state === "running") {
      el.textContent = "生成中";
      el.className = "state-value running";
      $("progressBar").style.width = "55%";
    } else if (status.state === "finished") {
      el.textContent = "已完成";
      el.className = "state-value finished";
      $("progressBar").style.width = "100%";
      phases.forEach((p) => {
        const ph = document.querySelector(`[data-phase="${p}"]`);
        if (ph) ph.classList.add("done");
      });
      return;
    } else {
      el.textContent = "等待启动";
      el.className = "state-value";
    }
    // 阶段推进（粗略）
    const evCount = state.seenEventIds.size;
    document.querySelectorAll("[data-phase]").forEach((ph, i) => {
      ph.classList.remove("active", "done");
      if (evCount > 0) {
        ph.classList.add("active");
      }
    });
    if (status.elapsed != null) {
      $("timer").textContent = UI.formatDuration(status.elapsed);
    }
    if (status.file_count != null) {
      $("artifactStats").textContent =
        `${status.file_count} 个文件 · ${UI.formatBytes(status.total_bytes)}`;
    }
    void phases;
  }

  // ---------- 完成任务 UI ----------
  async function finishUI(status) {
    $("stateValue").textContent = "已完成";
    $("stateValue").className = "state-value finished";
    $("progressBar").style.width = "100%";
    document.querySelectorAll("[data-phase]").forEach((p) => p.classList.add("done"));
    if (status.elapsed != null) $("timer").textContent = UI.formatDuration(status.elapsed);
    if (status.file_count != null) {
      $("artifactStats").textContent =
        `${status.file_count} 个文件 · ${UI.formatBytes(status.total_bytes)}`;
    }

    // 保存历史
    UI.saveHistory({
      sessionId: state.sessionId,
      game: state.game,
      prompt: $("promptInput").value.trim().slice(0, 120),
      elapsed: status.elapsed,
      fileCount: status.file_count,
      date: new Date().toLocaleString("zh-CN", { hour12: false }),
    });

    // 下载 / 重启按钮
    $("btnDownload").href = `/api/download?session_id=${encodeURIComponent(state.sessionId)}`;
    $("btnDownload").classList.remove("hidden");
    $("btnRestart").classList.remove("hidden");

    // 加载产物浏览器
    await loadArtifacts();
  }

  // ---------- 产物浏览器 ----------
  async function loadArtifacts() {
    if (!state.sessionId) return;
    try {
      const data = await API.getFiles(state.sessionId);
      if (!data.tree) return;
      const treeBox = $("fileTree");
      treeBox.innerHTML = "";
      data.tree.children.forEach((child) => {
        treeBox.appendChild(UI.renderTreeNode(child, 0));
      });
      $("artifactCard").classList.remove("hidden");
      $("artifactCount").textContent = countFiles(data.tree) + " 个文件";
    } catch (err) {
      console.warn("load artifacts failed", err);
    }
  }

  function countFiles(node) {
    if (node.type === "file") return 1;
    return (node.children || []).reduce((acc, c) => acc + countFiles(c), 0);
  }

  // 文件树点击 → 预览
  $("fileTree").addEventListener("click", async (e) => {
    const row = e.target.closest("[data-path]");
    if (!row || !row.dataset.path) return;
    document.querySelectorAll(".tree-node.selected").forEach((n) => n.classList.remove("selected"));
    row.classList.add("selected");
    try {
      const data = await API.getFiles(state.sessionId, row.dataset.path);
      $("previewHead").textContent = row.dataset.path + (data.size != null ? ` · ${UI.formatBytes(data.size)}` : "");
      $("previewBody").textContent = data.content || "(空文件)";
    } catch (err) {
      $("previewHead").textContent = row.dataset.path;
      $("previewBody").textContent = "预览失败：" + err.message;
    }
  });

  // ---------- 重新生成 ----------
  function handleRestart() {
    state.taskStarted = false;
    state.finished = false;
    state.eventCursor = null;
    state.seenEventIds.clear();
    $("timeline").innerHTML = "";
    $("eventCount").textContent = "0 个事件";
    $("artifactCard").classList.add("hidden");
    $("btnDownload").classList.add("hidden");
    $("btnRestart").classList.add("hidden");
    $("progressBar").style.width = "0%";
    $("stateValue").textContent = "等待启动";
    $("stateValue").className = "state-value";
    document.querySelectorAll("[data-phase]").forEach((p) => p.classList.remove("active", "done"));
    showStep(2);
  }

  // ---------- 事件绑定 ----------
  function bindEvents() {
    // 视图切换
    document.querySelectorAll(".nav-link").forEach((el) => {
      el.addEventListener("click", () => switchView(el.dataset.view));
    });

    // API Key 显示/隐藏
    $("toggleKey").addEventListener("click", () => {
      const input = $("apiKey");
      const showing = input.type === "text";
      input.type = showing ? "password" : "text";
      $("toggleKey").textContent = showing ? "显示" : "隐藏";
    });

    // 创建 / 运行
    $("btnCreate").addEventListener("click", handleCreate);
    $("btnRun").addEventListener("click", handleRun);
    $("btnBack1").addEventListener("click", () => showStep(1));
    $("btnRestart").addEventListener("click", handleRestart);

    // 复制会话 ID
    $("btnCopyId").addEventListener("click", async () => {
      if (!state.sessionId) return;
      try {
        await navigator.clipboard.writeText(state.sessionId);
        UI.toast("会话 ID 已复制", "success");
      } catch (e) {
        UI.toast("复制失败，请手动复制", "warn");
      }
    });

    // 示例模板
    document.querySelectorAll(".template-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        $("promptInput").value = TEMPLATES[chip.dataset.tpl] || "";
        updateCharCount();
        UI.toast("已填充示例需求", "success");
      });
    });

    // 字数统计
    $("promptInput").addEventListener("input", updateCharCount);

    // 历史按钮
    $("clearHistoryBtn") && $("clearHistoryBtn").addEventListener("click", () => {
      UI.clearHistory();
      renderHistory();
    });
  }

  function updateCharCount() {
    const len = $("promptInput").value.length;
    $("charCount").textContent = len + " 字";
  }

  // ---------- 启动 ----------
  function init() {
    bindEvents();
    loadGames();
    renderHistory();
  }

  document.addEventListener("DOMContentLoaded", init);
})();

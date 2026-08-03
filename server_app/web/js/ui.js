/* ============================================================
   ui.js — UI 渲染层
   负责 DOM 渲染：Toast、事件时间线、文件树、格式化工具。
   ============================================================ */

const UI = (() => {
  "use strict";

  /* ---------- Toast 通知 ---------- */

  function toast(message, type = "success", duration = 3500) {
    const wrap = document.getElementById("toastWrap");
    const el = document.createElement("div");
    el.className = `toast toast-${type}`;

    const icon = document.createElement("span");
    icon.className = "toast-icon";
    icon.innerHTML = type === "success"
      ? "&#10003;"   // ✓
      : type === "error"
        ? "&#10005;" // ✕
        : "&#33;";   // !

    const text = document.createElement("span");
    text.textContent = message;

    el.appendChild(icon);
    el.appendChild(text);
    wrap.appendChild(el);

    setTimeout(() => {
      el.classList.add("out");
      setTimeout(() => el.remove(), 300);
    }, duration);
  }

  /* ---------- 格式化 ---------- */

  /** 秒 → mm:ss */
  function formatDuration(totalSeconds) {
    const s = Math.max(0, Math.floor(totalSeconds || 0));
    const m = Math.floor(s / 60);
    const r = s % 60;
    return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
  }

  /** 字节 → 可读文本 */
  function formatBytes(n) {
    if (n == null) return "-";
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / 1024 / 1024).toFixed(1)} MB`;
  }

  /** 转义 HTML，防止日志内容破坏 DOM */
  function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s == null ? "" : String(s);
    return div.innerHTML;
  }

  /** 摘要：截断长文本，保留首行 */
  function summarize(text, max = 160) {
    const t = String(text || "").trim();
    if (t.length <= max) return t;
    return t.slice(0, max) + "…";
  }

  /* ---------- 事件时间线 ---------- */

  /** 工具调用文本 → { name, args } */
  function parseToolText(content) {
    const idx = content.indexOf("|");
    if (idx === -1) return { name: content.trim().slice(0, 40), args: "" };
    return {
      name: content.slice(0, idx).trim(),
      args: content.slice(idx + 1).trim(),
    };
  }

  /** 根据事件类型返回 CSS 类名 */
  function eventClass(type) {
    switch (type) {
      case "thinking": return "ev-thinking";
      case "tool_call": return "ev-tool";
      case "todo": return "ev-todo";
      case "round": return "ev-round";
      case "system": return "ev-system";
      case "background":
      case "teammate_report":
      case "protocol":
      case "worktree": return "ev-system";
      default: return "ev-log";
    }
  }

  /** 事件类型 → 中文标签 */
  const EVENT_LABEL = {
    thinking: "思考",
    tool_call: "工具调用",
    todo: "待办更新",
    round: "回合",
    system: "系统",
    background: "后台任务",
    teammate_report: "队友汇报",
    protocol: "协议",
    worktree: "工作树",
    log: "日志",
  };

  /** 渲染单个事件 DOM 节点 */
  function renderEvent(ev) {
    const item = document.createElement("div");
    item.className = `ev ${eventClass(ev.type)}`;

    const marker = document.createElement("span");
    marker.className = "ev-marker";
    item.appendChild(marker);

    const body = document.createElement("div");
    body.className = "ev-body";

    // meta 行：类型 + 来源/工具
    const meta = document.createElement("div");
    meta.className = "ev-meta";

    const typeBadge = document.createElement("span");
    typeBadge.textContent = EVENT_LABEL[ev.type] || ev.type;
    meta.appendChild(typeBadge);

    if (ev.type === "tool_call") {
      const { name } = parseToolText(ev.content || "");
      const t = document.createElement("span");
      t.className = "badge-tool";
      t.textContent = name || "unknown";
      meta.appendChild(t);
    }
    if (ev.peer) {
      const p = document.createElement("span");
      p.className = "badge-peer";
      p.textContent = ev.peer;
      meta.appendChild(p);
    }
    if (ev.source === "agent") {
      const s = document.createElement("span");
      s.className = "badge-src";
      s.textContent = "agent.log";
      meta.appendChild(s);
    }

    body.appendChild(meta);

    // 内容
    if (ev.type === "tool_call") {
      const { name, args } = parseToolText(ev.content || "");
      const sum = document.createElement("div");
      sum.className = "ev-summary";
      sum.textContent = summarize(args || name, 200);
      body.appendChild(sum);

      // 完整输出折叠
      if (args && args.length > 0) {
        const out = document.createElement("div");
        out.className = "tool-output";
        out.innerHTML = `<div class="out-summary">点击展开完整输出（${args.length} 字符）</div><pre class="out-full">${escapeHtml(args)}</pre>`;
        out.addEventListener("click", () => out.classList.toggle("open"));
        body.appendChild(out);
      }
    } else if (ev.type === "thinking") {
      const c = document.createElement("div");
      c.className = "ev-content";
      c.textContent = ev.content || "";
      body.appendChild(c);
    } else {
      const c = document.createElement("div");
      c.className = "ev-summary";
      c.textContent = summarize(ev.content || "", 240);
      body.appendChild(c);
    }

    item.appendChild(body);
    return item;
  }

  /* ---------- 文件树 ---------- */

  /** 递归渲染文件树节点 */
  function renderTreeNode(node, depth = 0) {
    const wrap = document.createElement("div");

    const row = document.createElement("div");
    row.className = "tree-node";
    row.style.paddingLeft = `${8 + depth * 16}px`;
    row.setAttribute("data-path", node.path || "");

    const tw = document.createElement("span");
    tw.className = "tw";
    tw.textContent = node.type === "dir" ? "▸" : " ";
    row.appendChild(tw);

    const tn = document.createElement("span");
    tn.className = "tn";
    tn.textContent = node.name;
    row.appendChild(tn);

    if (node.type === "file") {
      const fs = document.createElement("span");
      fs.className = "file-size";
      fs.textContent = formatBytes(node.size);
      row.appendChild(fs);
    }
    wrap.appendChild(row);

    // 子节点
    if (node.type === "dir" && node.children && node.children.length) {
      const children = document.createElement("div");
      children.className = "tree-children";
      node.children.forEach(child => {
        children.appendChild(renderTreeNode(child, depth + 1));
      });
      wrap.appendChild(children);
    }
    return wrap;
  }

  /* ---------- 历史记录 ---------- */

  /** 存储历史到 localStorage（最多保留 20 条） */
  function saveHistory(entry) {
    let history = [];
    try {
      history = JSON.parse(localStorage.getItem("modforge_history") || "[]");
    } catch (e) { history = []; }
    history.unshift(entry);
    history = history.slice(0, 20);
    try {
      localStorage.setItem("modforge_history", JSON.stringify(history));
    } catch (e) { /* 忽略存储失败 */ }
  }

  function loadHistory() {
    try {
      return JSON.parse(localStorage.getItem("modforge_history") || "[]");
    } catch (e) { return []; }
  }

  function clearHistory() {
    try { localStorage.removeItem("modforge_history"); } catch (e) { /* noop */ }
  }

  return {
    toast, formatDuration, formatBytes, escapeHtml, summarize,
    renderEvent, renderTreeNode, saveHistory, loadHistory, clearHistory,
  };
})();

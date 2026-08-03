/* ============================================================
   api.js — 后端接口封装层
   与后端交互的唯一出口：所有 fetch 都经过这里，错误统一归一化。
   ============================================================ */

const API = (() => {
  "use strict";

  /** 通用请求：返回解析后的 JSON，非 2xx 抛错（带后端 detail 文案） */
  async function request(url, options = {}) {
    const res = await fetch(url, options);
    if (!res.ok) {
      let msg = res.statusText || `HTTP ${res.status}`;
      try {
        const data = await res.json();
        if (data && data.detail) msg = data.detail;
      } catch (e) { /* 非 JSON 响应，保留 statusText */ }
      const err = new Error(msg);
      err.status = res.status;
      throw err;
    }
    return res.json();
  }

  /** 创建会话 */
  function createSession(apiKey, game) {
    return request("/api/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey, game }),
    });
  }

  /** 启动生成任务 */
  function startTask(sessionId, prompt) {
    return request("/api/task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, prompt }),
    });
  }

  /** 会话状态汇总 */
  function getSession(sessionId) {
    return request(`/api/session?session_id=${encodeURIComponent(sessionId)}`);
  }

  /** 实时状态 + 日志尾部（兼容旧接口） */
  function getStatus(sessionId) {
    return request(`/api/status?session_id=${encodeURIComponent(sessionId)}`);
  }

  /** 事件流（增量）：cursor 传上次返回的 cursor 对象 */
  function getEvents(sessionId, cursor = null) {
    const params = new URLSearchParams({ session_id: sessionId });
    if (cursor) params.set("cursor", JSON.stringify(cursor));
    return request(`/api/events?${params.toString()}`);
  }

  /** 文件树 / 单文件预览 */
  function getFiles(sessionId, path = "") {
    const params = new URLSearchParams({ session_id: sessionId });
    if (path) params.set("path", path);
    return request(`/api/files?${params.toString()}`);
  }

  /** 原始日志增量 */
  function getLog(sessionId, offset = 0) {
    const params = new URLSearchParams({ session_id: sessionId, offset });
    return request(`/api/log?${params.toString()}`);
  }

  /** 可用游戏模板 */
  function getGames() {
    return request("/api/games");
  }

  return {
    request, createSession, startTask, getSession, getStatus,
    getEvents, getFiles, getLog, getGames,
  };
})();

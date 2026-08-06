"use client";

/**
 * 认证工具：token 存取 + 注册/登录/登出/免登检查。
 *
 * token 持久化在 localStorage（key：modforge_token），
 * 页面刷新后自动恢复登录态。
 */

const TOKEN_KEY = "modforge_token";

export function getToken(): string {
  try {
    return localStorage.getItem(TOKEN_KEY) || "";
  } catch {
    return "";
  }
}

export function setToken(token: string): void {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  } catch {
    /* noop */
  }
}

export function clearToken(): void {
  setToken("");
}

interface AuthResult {
  username: string;
  token: string;
}

async function authFetch<T>(url: string, body: Record<string, string>): Promise<T> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText || `HTTP ${res.status}`;
    try {
      const data = await res.json();
      if (data?.detail) detail = data.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export async function register(username: string, password: string): Promise<AuthResult> {
  const data = await authFetch<AuthResult>("/api/register", { username, password });
  setToken(data.token);
  return data;
}

export async function login(username: string, password: string): Promise<AuthResult> {
  const data = await authFetch<AuthResult>("/api/login", { username, password });
  setToken(data.token);
  return data;
}

export async function logout(): Promise<void> {
  const token = getToken();
  try {
    if (token) {
      await fetch("/api/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    }
  } catch {
    /* 服务不可达也照常清本地 */
  }
  clearToken();
}

/** 校验本地 token 是否仍有效；有效返回用户名，无效返回 null 并清除。 */
export async function checkSession(): Promise<string | null> {
  const token = getToken();
  if (!token) return null;
  try {
    const res = await fetch("/api/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      clearToken();
      return null;
    }
    const data = (await res.json()) as { username: string };
    return data.username;
  } catch {
    return null;
  }
}
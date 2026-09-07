/**
 * HTTP 基础设施：token 注入、JSON 请求封装、浏览器下载触发
 * （由 lib/api.ts 迁出；下载函数的重复 fetch+blob+click 提取为
 * downloadBlob，行为不变）。
 */

const TOKEN_KEY = 'modforge_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export async function api<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`
  if (options.body && typeof options.body === 'string') headers['Content-Type'] = 'application/json'

  const res = await fetch(path, { ...options, headers })
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const j = await res.json()
      if (j && j.detail) detail = j.detail
    } catch {
      /* ignore non-JSON error body */
    }
    throw new Error(detail)
  }
  // 空响应体返回 undefined
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return (await res.json()) as T
  return undefined as T
}

/** fetch + blob 触发浏览器下载（jar/zip 共用；带 token 头） */
export async function downloadBlob(url: string, filename: string): Promise<void> {
  const token = getToken()
  const res = await fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  if (!res.ok) throw new Error(`下载失败: ${res.status}`)
  const blob = await res.blob()
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  a.download = filename
  a.click()
  URL.revokeObjectURL(objectUrl)
}

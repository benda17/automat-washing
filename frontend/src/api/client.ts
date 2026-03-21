const TOKEN_KEY = 'aw_token'

/** Set `VITE_API_BASE=http://127.0.0.1:8010` in `frontend/.env` if `/api` proxy fails. */
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ?? ''

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

function buildUrl(path: string): string {
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
}

function formatDetail(detail: unknown): string {
  if (detail == null) return 'Request failed'
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg: unknown }).msg)
        }
        return JSON.stringify(item)
      })
      .join(' ')
  }
  return JSON.stringify(detail)
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body instanceof FormData) {
    headers.delete('Content-Type')
  } else if (!headers.has('Content-Type') && init.body && typeof init.body === 'string') {
    headers.set('Content-Type', 'application/json')
  }
  const url = buildUrl(path)
  let res: Response
  try {
    res = await fetch(url, { ...init, headers })
  } catch (e) {
    const hint =
      API_BASE === ''
        ? ' Is the API running on port 8010? (Vite proxies /api only when dev server is used.)'
        : ''
    throw new Error(e instanceof Error ? `${e.message}.${hint}` : `Network error.${hint}`)
  }
  if (!res.ok) {
    let detail: unknown = res.statusText
    try {
      const j = (await res.json()) as { detail?: unknown }
      if (j.detail !== undefined) detail = j.detail
    } catch {
      /* ignore */
    }
    throw new Error(formatDetail(detail))
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

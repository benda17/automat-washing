import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api, getToken, setToken } from '../api/client'
import type { User } from '../api/types'

type AuthState =
  | { status: 'loading' }
  | { status: 'anonymous' }
  | { status: 'authenticated'; user: User }

type AuthContextValue = {
  state: AuthState
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  const refresh = useCallback(async () => {
    if (!getToken()) {
      setState({ status: 'anonymous' })
      return
    }
    try {
      const user = await api<User>('/api/me')
      setState({ status: 'authenticated', user })
    } catch {
      setToken(null)
      setState({ status: 'anonymous' })
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const login = useCallback(async (username: string, password: string) => {
    const res = await api<{ access_token: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    setToken(res.access_token)
    await refresh()
  }, [refresh])

  const logout = useCallback(() => {
    setToken(null)
    setState({ status: 'anonymous' })
  }, [])

  const value = useMemo(
    () => ({
      state,
      login,
      logout,
      refresh,
    }),
    [state, login, logout, refresh],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth outside AuthProvider')
  return ctx
}

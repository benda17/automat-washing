import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { state, login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (state.status === 'authenticated') return <Navigate to="/" replace />

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setErr(null)
    setBusy(true)
    try {
      await login(username.trim(), password)
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="aw-login">
      <div className="aw-login-bg" aria-hidden />
      <div className="aw-login-center">
        <div className="aw-login-stack">
          <div className="aw-login-brand-mark" aria-hidden>
            <span className="aw-droplet">◌</span>
          </div>
          <form className="aw-login-card" onSubmit={onSubmit}>
            <h1 className="aw-display aw-login-title">Automat Washing</h1>
            <p className="aw-login-sub">Sign in to your cohort space.</p>

            <div className="aw-grid" style={{ gap: '1rem' }}>
              <label>
                <div>Username</div>
                <input
                  className="aw-input"
                  name="username"
                  type="text"
                  autoComplete="username"
                  autoCapitalize="none"
                  spellCheck={false}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </label>
              <label>
                <div>Password</div>
                <input
                  className="aw-input"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>
              {err && <div className="aw-error">{err}</div>}
              <button className="aw-btn" type="submit" disabled={busy}>
                {busy ? 'Signing in…' : 'Sign in'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

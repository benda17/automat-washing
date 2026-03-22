import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function Shell() {
  const { state, logout } = useAuth()
  const role = state.status === 'authenticated' ? state.user.role : null

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    isActive ? 'aw-nav-active' : undefined

  return (
    <div className="aw-shell">
      <header className="aw-topnav aw-topnav-wash">
        <div className="aw-brand">
          <img
            className="aw-brand-logo"
            src="/logo.png?v=6"
            alt=""
            width={56}
            height={42}
            decoding="async"
          />
          <div className="aw-brand-text">
            <strong>Automat Washing</strong>
            <span>rinse · build · ship</span>
          </div>
        </div>
        {state.status === 'authenticated' && (
          <nav className="aw-nav-links" aria-label="Primary">
            <NavLink to="/" end className={linkClass}>
              Today
            </NavLink>
            <NavLink to="/guide" className={linkClass}>
              How to use
            </NavLink>
            <NavLink to="/roadmap" className={linkClass}>
              15-day roadmap
            </NavLink>
            <NavLink to="/submissions" className={linkClass}>
              Submissions
            </NavLink>
            {(role === 'teacher' || role === 'admin') && (
              <NavLink to="/admin" className={linkClass}>
                Mentor console
              </NavLink>
            )}
            <span className="aw-pill">
              {state.user.full_name} (@{state.user.username}) · {state.user.role}
            </span>
            <button type="button" className="aw-btn secondary" onClick={logout}>
              Sign out
            </button>
          </nav>
        )}
      </header>
      <Outlet />
    </div>
  )
}

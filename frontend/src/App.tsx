import type { ReactElement } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Shell } from './components/Shell'
import { useAuth } from './auth/AuthContext'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { RoadmapPage } from './pages/RoadmapPage'
import { LessonPage } from './pages/LessonPage'
import { SubmissionsPage } from './pages/SubmissionsPage'
import { AdminPage } from './pages/AdminPage'
import { GuidePage } from './pages/GuidePage'

function RequireAuth({ children }: { children: ReactElement }) {
  const { state } = useAuth()
  if (state.status === 'loading')
    return (
      <div className="aw-loading">
        <div className="aw-loading-inner">
          <div className="aw-spinner" aria-hidden />
          Loading session…
        </div>
      </div>
    )
  if (state.status !== 'authenticated') return <Navigate to="/login" replace />
  return children
}

function RequireMentor({ children }: { children: ReactElement }) {
  const { state } = useAuth()
  if (state.status !== 'authenticated') return <Navigate to="/login" replace />
  if (state.user.role !== 'teacher' && state.user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <RequireAuth>
            <Shell />
          </RequireAuth>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/guide" element={<GuidePage />} />
        <Route path="/roadmap" element={<RoadmapPage />} />
        <Route path="/lessons/:lessonId" element={<LessonPage />} />
        <Route path="/submissions" element={<SubmissionsPage />} />
        <Route
          path="/admin"
          element={
            <RequireMentor>
              <AdminPage />
            </RequireMentor>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

type Dashboard = {
  course: { title: string; slug: string; duration_days: number } | null
  today: { lesson_id: number; day_index: number; title: string; slug: string } | null
  roadmap: {
    day_index: number
    lesson_id: number
    title: string
    slug: string
    completed: boolean
    completion_percent: number
  }[]
  submissions: { id: number; exercise_id: number; status: string; created_at: string }[]
  readiness: {
    readiness_score: number
    completion_percent: number
    average_grade: number
    lessons_completed: number
    lessons_total: number
    weak_dimensions: { dimension: string; avg_score: number }[]
  } | null
}

export function DashboardPage() {
  const q = useQuery({
    queryKey: ['me-dashboard'],
    queryFn: () => api<Dashboard>('/api/me/dashboard'),
  })

  if (q.isPending)
    return (
      <div className="aw-card aw-card-wash">
        <div className="aw-inline-loading">
          <span className="aw-droplet aw-droplet-pulse" aria-hidden>
            ◌
          </span>
          Loading…
        </div>
      </div>
    )

  if (q.isError)
    return (
      <div className="aw-card aw-error">
        Could not load today&apos;s view. {q.error instanceof Error ? q.error.message : ''}
      </div>
    )

  const d = q.data!
  const done = d.roadmap.filter((x) => x.completed).length
  const total = d.roadmap.length || 15
  const pct = Math.round((done / total) * 100)

  return (
    <div className="aw-grid" style={{ gap: '1rem' }}>
      <section className="aw-card aw-card-wash">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
          <div>
            <div className="aw-pill">Today</div>
            <h1 className="aw-display" style={{ margin: '0.5rem 0 0.25rem' }}>
              {d.today ? d.today.title : 'Bootcamp complete — revisit lessons or pending reviews'}
            </h1>
            <p style={{ margin: 0, opacity: 0.8 }}>
              {d.course?.title} · {d.course?.duration_days} days
            </p>
          </div>
          {d.today && (
            <Link className="aw-btn" to={`/lessons/${d.today.lesson_id}`} style={{ alignSelf: 'center' }}>
              Open day {d.today.day_index}
            </Link>
          )}
        </div>
      </section>

      <div className="aw-grid cols-2">
        <section className="aw-card aw-card-wash">
          <h2 style={{ marginTop: 0 }}>Roadmap rinse</h2>
          <div className="aw-progress" aria-hidden>
            <div style={{ width: `${pct}%` }} />
          </div>
          <p style={{ marginTop: '0.65rem', opacity: 0.85 }}>
            {done}/{total} days marked complete · {pct}%
          </p>
          <Link to="/roadmap" style={{ fontSize: '0.92rem' }}>
            Full 15-day arc →
          </Link>
        </section>

        <section className="aw-card aw-card-wash">
          <h2 style={{ marginTop: 0 }}>Readiness</h2>
          {d.readiness ? (
            <>
              <p style={{ fontSize: '2rem', margin: '0.25rem 0', fontWeight: 700 }}>
                {d.readiness.readiness_score}
                <span style={{ fontSize: '1rem', opacity: 0.6 }}>/100</span>
              </p>
              <p style={{ margin: 0, opacity: 0.8 }}>
                Completion {d.readiness.completion_percent}% · Avg grade {d.readiness.average_grade}
              </p>
              {d.readiness.weak_dimensions.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="aw-pill">Focus areas</div>
                  <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.1rem' }}>
                    {d.readiness.weak_dimensions.map((w) => (
                      <li key={w.dimension}>
                        {w.dimension.replace(/_/g, ' ')} · avg {w.avg_score}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <p style={{ opacity: 0.8 }}>Readiness scores apply to student accounts.</p>
          )}
        </section>
      </div>

      <section className="aw-card aw-card-wash">
        <h2 style={{ marginTop: 0 }}>Recent submissions</h2>
        {d.submissions.length === 0 ? (
          <p style={{ opacity: 0.75 }}>Nothing submitted yet — open a lesson and run an exercise.</p>
        ) : (
          <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
            {d.submissions.map((s) => (
              <li key={s.id}>
                <Link to={`/submissions#${s.id}`}>
                  #{s.id} · {s.status} · {new Date(s.created_at).toLocaleString()}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

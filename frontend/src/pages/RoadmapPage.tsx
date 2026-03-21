import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Course } from '../api/types'

export function RoadmapPage() {
  const q = useQuery({
    queryKey: ['course'],
    queryFn: () => api<Course>('/api/course/current'),
  })

  if (q.isLoading) return <div className="aw-card">Loading roadmap…</div>
  if (q.isError) return <div className="aw-card aw-error">Could not load course.</div>

  const course = q.data!

  return (
    <div className="aw-grid" style={{ gap: '1rem' }}>
      <section className="aw-card">
        <h1 className="aw-display" style={{ marginTop: 0 }}>
          {course.title}
        </h1>
        <p style={{ opacity: 0.85, marginTop: 0 }}>{course.description}</p>
      </section>

      {course.modules
        .slice()
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((mod) => (
          <section key={mod.id} className="aw-card">
            <h2 style={{ marginTop: 0 }}>{mod.title}</h2>
            {mod.summary && <p style={{ opacity: 0.8 }}>{mod.summary}</p>}
            <div className="aw-grid" style={{ gap: '0.65rem' }}>
              {mod.lessons
                .slice()
                .sort((a, b) => a.day_index - b.day_index)
                .map((les) => (
                  <div
                    key={les.id}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'auto 1fr auto',
                      gap: '0.75rem',
                      alignItems: 'center',
                      padding: '0.65rem 0',
                      borderBottom: '1px solid rgba(255,255,255,0.06)',
                    }}
                  >
                    <span className="aw-pill">Day {les.day_index}</span>
                    <div>
                      <div style={{ fontWeight: 600 }}>{les.title}</div>
                      <div style={{ fontSize: '0.88rem', opacity: 0.72 }}>{les.summary.slice(0, 140)}…</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="aw-progress" style={{ width: 120, display: 'inline-block' }}>
                        <div style={{ width: `${les.completion_percent}%` }} />
                      </div>
                      <div style={{ marginTop: '0.25rem' }}>
                        <Link className="aw-btn secondary" to={`/lessons/${les.id}`} style={{ fontSize: '0.85rem' }}>
                          {les.completed ? 'Review' : 'Open'}
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </section>
        ))}
    </div>
  )
}

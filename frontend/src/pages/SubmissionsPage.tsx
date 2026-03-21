import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Submission } from '../api/types'
import { ReviewDiscussion } from '../components/ReviewDiscussion'

export function SubmissionsPage() {
  const q = useQuery({
    queryKey: ['submissions-mine'],
    queryFn: () => api<Submission[]>('/api/submissions/mine'),
  })

  if (q.isLoading) return <div className="aw-card">Loading submissions…</div>
  if (q.isError) return <div className="aw-card aw-error">Could not load submissions.</div>

  const rows = q.data!

  return (
    <div className="aw-grid" style={{ gap: '1rem' }}>
      <section className="aw-card">
        <h1 className="aw-display" style={{ marginTop: 0 }}>
          Your submissions
        </h1>
        <p style={{ opacity: 0.8, marginTop: 0 }}>
          Each submission receives an automatic review; mentors can add manual feedback. Use the discussion under each
          review to debate points, ask for clarification, or show how you addressed feedback.
        </p>
      </section>

      {rows.length === 0 ? (
        <div className="aw-card">No submissions yet.</div>
      ) : (
        rows.map((s) => {
          const top = s.reviews[0]
          return (
            <article key={s.id} className="aw-card" id={String(s.id)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                <div>
                  <div className="aw-pill">
                    #{s.id} · exercise {s.exercise_id} · {s.status}
                  </div>
                  <div style={{ opacity: 0.7, fontSize: '0.88rem', marginTop: '0.35rem' }}>
                    {new Date(s.created_at).toLocaleString()}
                  </div>
                </div>
                {top && (
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>
                      {top.overall_score}
                      <span style={{ fontSize: '1rem', opacity: 0.55 }}>/100</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.65 }}>{top.is_auto ? 'Auto review' : 'Mentor review'}</div>
                  </div>
                )}
              </div>
              <details style={{ marginTop: '0.75rem' }}>
                <summary style={{ cursor: 'pointer' }}>Your content</summary>
                <pre
                  style={{
                    whiteSpace: 'pre-wrap',
                    background: 'rgba(0,0,0,0.35)',
                    padding: '0.75rem',
                    borderRadius: 12,
                    border: '1px solid rgba(255,255,255,0.08)',
                  }}
                >
                  {s.content}
                </pre>
              </details>
              {s.reviews.map((r) => (
                <div key={r.id} style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                  <div className="aw-pill" style={{ marginBottom: '0.5rem' }}>
                    Review #{r.id} · {r.is_auto ? 'automatic' : 'human'}
                  </div>
                  <div style={{ whiteSpace: 'pre-wrap', opacity: 0.92 }}>{r.feedback}</div>
                  <ReviewDiscussion
                    submissionId={s.id}
                    reviewId={r.id}
                    comments={r.comments ?? []}
                    invalidateKeys={[['submissions-mine']]}
                  />
                </div>
              ))}
            </article>
          )
        })
      )}
    </div>
  )
}

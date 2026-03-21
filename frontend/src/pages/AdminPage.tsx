import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { api } from '../api/client'
import type { Review, Submission } from '../api/types'
import { ReviewDiscussion } from '../components/ReviewDiscussion'

type Analytics = {
  students: {
    user_id: number
    full_name: string
    username: string
    email: string | null
    readiness_score: number
    completion_percent: number
    average_grade: number
    lessons_completed: number
    lessons_total: number
    weak_dimensions: { dimension: string; avg_score: number }[]
  }[]
  auto_only_submissions: { id: number; student: string; exercise: string; created_at: string }[]
  heatmap: { user_id: number; full_name: string; days: { day: number; completed: boolean; percent: number }[] }[]
}

function sortReviewsDesc(reviews: Review[]) {
  return [...reviews].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
}

function latestAutoReview(reviews: Review[]): Review | undefined {
  return sortReviewsDesc(reviews).find((r) => r.is_auto)
}

function hasHumanReview(reviews: Review[]) {
  return reviews.some((r) => !r.is_auto)
}

export function AdminPage() {
  const qc = useQueryClient()
  const aq = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => api<Analytics>('/api/admin/analytics'),
  })
  const sq = useQuery({
    queryKey: ['admin-submissions-all'],
    queryFn: () => api<Submission[]>('/api/admin/submissions/all'),
  })

  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [score, setScore] = useState(80)
  const [feedback, setFeedback] = useState('')
  const [strengths, setStrengths] = useState('')
  const [weaknesses, setWeaknesses] = useState('')
  const [improvements, setImprovements] = useState('')
  const [mentorNotes, setMentorNotes] = useState('')
  const [scoreChangeExplanation, setScoreChangeExplanation] = useState('')
  const [clientError, setClientError] = useState<string | null>(null)

  const selected = useMemo(
    () => sq.data?.find((s) => s.id === selectedId) ?? null,
    [sq.data, selectedId],
  )

  const refAuto = selected ? latestAutoReview(selected.reviews)?.overall_score ?? null : null

  useEffect(() => {
    if (!selected) return
    const auto = latestAutoReview(selected.reviews)
    const base = auto
    setScore(base?.overall_score ?? 80)
    setFeedback(base?.feedback ?? '')
    setStrengths((base?.strengths ?? []).join(', '))
    setWeaknesses((base?.weaknesses ?? []).join(', '))
    setImprovements((base?.improvements ?? []).join(', '))
    setMentorNotes('')
    setScoreChangeExplanation('')
    setClientError(null)
  }, [selected])

  const review = useMutation({
    mutationFn: async () => {
      if (!selectedId) throw new Error('Select a submission')
      const ref = refAuto
      if (ref !== null && score < ref) {
        if (scoreChangeExplanation.trim().length < 20) {
          throw new Error(
            'When the manual score is below the automatic score, add a score change explanation (at least 20 characters).',
          )
        }
      }
      return api<Submission>(`/api/admin/submissions/${selectedId}/review`, {
        method: 'POST',
        body: JSON.stringify({
          overall_score: score,
          dimension_scores: { correctness: score, readability: Math.max(0, score - 2), testing_effort: Math.max(0, score - 5) },
          feedback,
          strengths: strengths.split(',').map((s) => s.trim()).filter(Boolean),
          weaknesses: weaknesses.split(',').map((s) => s.trim()).filter(Boolean),
          improvements: improvements.split(',').map((s) => s.trim()).filter(Boolean),
          mentor_tone_notes: mentorNotes.trim() || null,
          score_change_explanation: scoreChangeExplanation.trim() || null,
        }),
      })
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['admin-analytics'] })
      void qc.invalidateQueries({ queryKey: ['admin-submissions-all'] })
      setClientError(null)
    },
    onError: () => {
      setClientError(null)
    },
  })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setClientError(null)
    if (refAuto !== null && score < refAuto && scoreChangeExplanation.trim().length < 20) {
      setClientError(
        'When the manual score is below the automatic score, add a score change explanation (at least 20 characters).',
      )
      return
    }
    void review.mutate()
  }

  if (aq.isLoading) return <div className="aw-card">Loading mentor console…</div>
  if (aq.isError) return <div className="aw-card aw-error">Forbidden or unavailable.</div>

  const a = aq.data!

  return (
    <div className="aw-grid" style={{ gap: '1rem' }}>
      <section className="aw-card">
        <h1 className="aw-display" style={{ marginTop: 0 }}>
          Mentor console
        </h1>
        <p style={{ opacity: 0.8, marginTop: 0 }}>
          Readiness, heatmaps, and grading: open a student submission, read the full text and auto feedback, then publish a
          manual review. Lowering the grade below the automatic score requires a short explanation (stored for the student).
        </p>
      </section>

      <section className="aw-card">
        <h2 style={{ marginTop: 0 }}>Roster readiness</h2>
        <div className="aw-grid" style={{ gap: '0.65rem' }}>
          {a.students.map((s) => (
            <div
              key={s.user_id}
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr auto',
                gap: '0.75rem',
                padding: '0.65rem 0',
                borderBottom: '1px solid rgba(255,255,255,0.08)',
              }}
            >
              <div>
                <div style={{ fontWeight: 600 }}>{s.full_name}</div>
                <div style={{ fontSize: '0.85rem', opacity: 0.65 }}>
                  @{s.username}
                  {s.email ? ` · ${s.email}` : ''}
                </div>
                {s.weak_dimensions.length > 0 && (
                  <div style={{ fontSize: '0.85rem', opacity: 0.78, marginTop: '0.35rem' }}>
                    Weakest: {s.weak_dimensions.map((w) => `${w.dimension} (${w.avg_score})`).join(' · ')}
                  </div>
                )}
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{s.readiness_score}</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.65 }}>
                  {s.completion_percent}% done · avg {s.average_grade}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="aw-card">
        <h2 style={{ marginTop: 0 }}>Completion heatmap (by day)</h2>
        <div className="aw-grid" style={{ gap: '0.75rem' }}>
          {a.heatmap.map((row) => (
            <div key={row.user_id}>
              <div style={{ fontSize: '0.9rem', marginBottom: '0.35rem', opacity: 0.8 }}>{row.full_name}</div>
              <div className="aw-heatmap" title={`Student ${row.user_id}`}>
                {row.days.map((d) => (
                  <div key={d.day} className={`aw-heatmap-cell ${d.completed ? 'on' : ''}`} title={`Day ${d.day}`} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="aw-card">
        <h2 style={{ marginTop: 0 }}>Grade submissions</h2>
        {sq.isLoading && <div>Loading submissions…</div>}
        {sq.isError && <div className="aw-error">Could not load submissions.</div>}
        {sq.data && sq.data.length === 0 && <div style={{ opacity: 0.75 }}>No submissions yet.</div>}
        {sq.data && sq.data.length > 0 && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1.2fr)',
              gap: '1rem',
              alignItems: 'start',
            }}
          >
            <div style={{ maxHeight: 420, overflow: 'auto', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 12 }}>
              {sq.data.map((s) => {
                const auto = latestAutoReview(s.reviews)
                const human = sortReviewsDesc(s.reviews).find((r) => !r.is_auto)
                const needs = !hasHumanReview(s.reviews)
                return (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setSelectedId(s.id)}
                    style={{
                      display: 'block',
                      width: '100%',
                      textAlign: 'left',
                      padding: '0.65rem 0.75rem',
                      border: 'none',
                      borderBottom: '1px solid rgba(255,255,255,0.06)',
                      background: selectedId === s.id ? 'rgba(120,180,255,0.12)' : 'transparent',
                      color: 'inherit',
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ fontWeight: 600 }}>
                      {s.student_full_name ?? `Student ${s.student_id}`}
                      {needs && (
                        <span style={{ marginLeft: '0.35rem', fontSize: '0.72rem', opacity: 0.85 }}>(auto only)</span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                      {s.student_username != null ? `@${s.student_username}` : `Student ${s.student_id}`}
                      {s.student_email ? ` · ${s.student_email}` : ''}
                    </div>
                    <div style={{ fontSize: '0.82rem', marginTop: '0.25rem' }}>
                      Day {s.lesson_day_index ?? '—'} · {s.exercise_title ?? `Exercise #${s.exercise_id}`}
                    </div>
                    <div style={{ fontSize: '0.8rem', opacity: 0.75, marginTop: '0.2rem' }}>
                      Auto {auto?.overall_score ?? '—'}
                      {human != null && ` · Human ${human.overall_score}`}
                    </div>
                  </button>
                )
              })}
            </div>

            <div className="aw-grid" style={{ gap: '0.75rem' }}>
              {!selected && <div style={{ opacity: 0.75 }}>Select a submission on the left.</div>}
              {selected && (
                <>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>
                      {selected.student_full_name} · {selected.exercise_title}
                    </div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.7 }}>
                      {selected.student_username != null ? `@${selected.student_username}` : `Student ${selected.student_id}`}
                      {selected.student_email ? ` · ${selected.student_email}` : ''} · Submitted{' '}
                      {new Date(selected.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.75, marginBottom: '0.35rem' }}>Submission</div>
                    <pre
                      style={{
                        margin: 0,
                        maxHeight: 220,
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        background: 'rgba(0,0,0,0.35)',
                        padding: '0.75rem',
                        borderRadius: 12,
                        fontSize: '0.82rem',
                      }}
                    >
                      {selected.content}
                    </pre>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.85rem', opacity: 0.75, marginBottom: '0.35rem' }}>Reviews &amp; discussion</div>
                    <div className="aw-grid" style={{ gap: '0.85rem' }}>
                      {sortReviewsDesc(selected.reviews).map((r) => (
                        <div
                          key={r.id}
                          style={{
                            padding: '0.75rem',
                            borderRadius: 12,
                            border: '1px solid rgba(255,255,255,0.1)',
                            background: 'rgba(0,0,0,0.2)',
                          }}
                        >
                          <div style={{ fontSize: '0.82rem', opacity: 0.8, marginBottom: '0.35rem' }}>
                            <strong>{r.is_auto ? 'Automatic' : 'Human'}</strong> · {r.overall_score}/100 ·{' '}
                            {new Date(r.created_at).toLocaleString()}
                          </div>
                          <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.88rem', opacity: 0.92 }}>{r.feedback}</div>
                          <ReviewDiscussion
                            submissionId={selected.id}
                            reviewId={r.id}
                            comments={r.comments ?? []}
                            invalidateKeys={[['submissions-mine'], ['admin-submissions-all'], ['admin-analytics']]}
                            placeholder="Reply as mentor — clarify expectations, respond to pushback, or confirm a fix."
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                  <form className="aw-grid" style={{ gap: '0.65rem' }} onSubmit={onSubmit}>
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>Overall score (0–100)</div>
                      <input
                        className="aw-input"
                        type="number"
                        min={0}
                        max={100}
                        value={score}
                        onChange={(e) => setScore(Number(e.target.value))}
                      />
                    </label>
                    {refAuto !== null && (
                      <div style={{ fontSize: '0.82rem', opacity: 0.78 }}>
                        Latest automatic score: <strong>{refAuto}</strong>
                        {score < refAuto && (
                          <span style={{ color: 'var(--aw-warn, #f5a623)' }}>
                            {' '}
                            — explanation required if you keep a lower score.
                          </span>
                        )}
                      </div>
                    )}
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>Feedback (student-visible)</div>
                      <textarea className="aw-input" rows={5} value={feedback} onChange={(e) => setFeedback(e.target.value)} />
                    </label>
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>
                        Score change explanation {refAuto !== null && score < refAuto ? '(required, ≥20 chars)' : '(optional)'}
                      </div>
                      <textarea
                        className="aw-input"
                        rows={3}
                        value={scoreChangeExplanation}
                        onChange={(e) => setScoreChangeExplanation(e.target.value)}
                        placeholder="If you reduced points vs the auto grader, say exactly what was missing or wrong."
                      />
                    </label>
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>Strengths (comma-separated)</div>
                      <input className="aw-input" value={strengths} onChange={(e) => setStrengths(e.target.value)} />
                    </label>
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>Weaknesses (comma-separated)</div>
                      <input className="aw-input" value={weaknesses} onChange={(e) => setWeaknesses(e.target.value)} />
                    </label>
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>Improvements (comma-separated)</div>
                      <input className="aw-input" value={improvements} onChange={(e) => setImprovements(e.target.value)} />
                    </label>
                    <label>
                      <div style={{ fontSize: '0.85rem', opacity: 0.75 }}>Mentor addendum (optional)</div>
                      <textarea className="aw-input" rows={2} value={mentorNotes} onChange={(e) => setMentorNotes(e.target.value)} />
                    </label>
                    {(clientError || review.isError) && (
                      <div className="aw-error">{clientError ?? (review.error as Error).message}</div>
                    )}
                    <button className="aw-btn" type="submit" disabled={review.isPending}>
                      Publish manual review
                    </button>
                  </form>
                </>
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  )
}

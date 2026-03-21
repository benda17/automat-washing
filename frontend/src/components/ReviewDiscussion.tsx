import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import type { ReviewComment } from '../api/types'
import { useAuth } from '../auth/AuthContext'

type QueryKey = readonly unknown[]

function roleLabel(role: string) {
  if (role === 'admin' || role === 'teacher') return 'Mentor'
  return 'Student'
}

export function ReviewDiscussion({
  submissionId,
  reviewId,
  comments,
  invalidateKeys,
  placeholder = 'Reply in the thread — ask questions, push back, or confirm you fixed the issue.',
}: {
  submissionId: number
  reviewId: number
  comments: ReviewComment[]
  invalidateKeys: QueryKey[]
  placeholder?: string
}) {
  const qc = useQueryClient()
  const { state } = useAuth()
  const selfId = state.status === 'authenticated' ? state.user.id : null
  const [text, setText] = useState('')
  const [err, setErr] = useState<string | null>(null)

  const post = useMutation({
    mutationFn: () =>
      api(`/api/submissions/${submissionId}/reviews/${reviewId}/comments`, {
        method: 'POST',
        body: JSON.stringify({ body: text.trim() }),
      }),
    onSuccess: async () => {
      setText('')
      setErr(null)
      await Promise.all(invalidateKeys.map((key) => qc.invalidateQueries({ queryKey: [...key] })))
    },
  })

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    setErr(null)
    if (!text.trim()) {
      setErr('Write something before sending.')
      return
    }
    void post.mutate()
  }

  return (
    <div style={{ marginTop: '0.65rem' }}>
      <div style={{ fontSize: '0.8rem', opacity: 0.72, marginBottom: '0.4rem' }}>Discussion</div>
      {comments.length === 0 ? (
        <div style={{ fontSize: '0.85rem', opacity: 0.65, marginBottom: '0.5rem' }}>No replies yet — start the thread.</div>
      ) : (
        <ul style={{ listStyle: 'none', margin: '0 0 0.65rem', padding: 0, display: 'grid', gap: '0.5rem' }}>
          {comments.map((c) => (
            <li
              key={c.id}
              style={{
                padding: '0.55rem 0.65rem',
                borderRadius: 10,
                background: 'rgba(0,0,0,0.22)',
                border: '1px solid rgba(255,255,255,0.06)',
              }}
            >
              <div style={{ fontSize: '0.78rem', opacity: 0.75, marginBottom: '0.25rem' }}>
                <strong>{c.author_full_name}</strong>
                <span style={{ opacity: 0.85 }}> @{c.author_username}</span>
                <span style={{ marginLeft: '0.35rem' }}>· {roleLabel(c.author_role)}</span>
                {selfId === c.author_id && (
                  <span style={{ marginLeft: '0.35rem', opacity: 0.9 }}>
                    · <em>you</em>
                  </span>
                )}
                <span style={{ marginLeft: '0.35rem', opacity: 0.6 }}>{new Date(c.created_at).toLocaleString()}</span>
              </div>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.88rem', opacity: 0.92 }}>{c.body}</div>
            </li>
          ))}
        </ul>
      )}
      <form className="aw-grid" style={{ gap: '0.45rem' }} onSubmit={onSubmit}>
        <textarea
          className="aw-input"
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
        />
        {(err || post.isError) && <div className="aw-error">{err ?? (post.error as Error).message}</div>}
        <button className="aw-btn secondary" type="submit" disabled={post.isPending} style={{ alignSelf: 'start' }}>
          {post.isPending ? 'Sending…' : 'Send reply'}
        </button>
      </form>
    </div>
  )
}

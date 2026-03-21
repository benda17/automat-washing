import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { ComposeFromFilesResponse, Exercise, LessonDetail, LessonResource } from '../api/types'
import { normalizeYoutubeEmbedUrl, youtubeWatchUrlFromAny } from '../utils/youtube'

function ResourceList({ resources }: { resources: LessonResource[] }) {
  return (
    <ul style={{ paddingLeft: '0', listStyle: 'none', margin: 0 }}>
      {resources.map((r, i) => (
        <li key={i} style={{ marginBottom: '1rem' }}>
          {r.blocks && r.blocks.length > 0 ? (
            <div>
              <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>{r.label}</div>
              <ul style={{ paddingLeft: '1rem', margin: 0 }}>
                {r.blocks.map((b, j) => (
                  <li key={j} style={{ marginBottom: '0.65rem', opacity: 0.9 }}>
                    <span className="aw-schedule-hours">{b.hours}h</span> — <strong>{b.title}</strong>
                    <div style={{ fontSize: '0.88rem', opacity: 0.78, marginTop: '0.2rem' }}>{b.detail}</div>
                  </li>
                ))}
              </ul>
            </div>
          ) : r.url.startsWith('#') ? (
            <span style={{ opacity: 0.85 }}>{r.label}</span>
          ) : (
            <div>
              <a href={r.url} target="_blank" rel="noreferrer">
                {r.label}
              </a>
              {r.note ? (
                <div style={{ fontSize: '0.82rem', opacity: 0.72, marginTop: '0.3rem', maxWidth: '52ch' }}>
                  {r.note}
                </div>
              ) : null}
            </div>
          )}
        </li>
      ))}
    </ul>
  )
}

export function LessonPage() {
  const { lessonId } = useParams()
  const id = Number(lessonId)
  const qc = useQueryClient()
  const [content, setContent] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const q = useQuery({
    queryKey: ['lesson', id],
    queryFn: () => api<LessonDetail>(`/api/lessons/${id}`),
    enabled: Number.isFinite(id),
  })

  const exercises = useMemo(() => {
    const list = q.data?.exercises ?? []
    return [...list].sort((a, b) => a.sort_order - b.sort_order)
  }, [q.data?.exercises])

  useEffect(() => {
    setSelectedExerciseId(null)
    setContent('')
    setMsg(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }, [id])

  useEffect(() => {
    if (exercises.length && selectedExerciseId === null) {
      setSelectedExerciseId(exercises[0].id)
    }
  }, [exercises, selectedExerciseId])

  const ex = exercises.find((e) => e.id === selectedExerciseId) ?? exercises[0]
  const exIndex = ex ? exercises.findIndex((e) => e.id === ex.id) : -1

  const complete = useMutation({
    mutationFn: () => api(`/api/lessons/${id}/complete`, { method: 'POST' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['lesson', id] }),
  })

  const composeFiles = useMutation({
    mutationFn: async (fileList: FileList) => {
      const fd = new FormData()
      for (let i = 0; i < fileList.length; i += 1) {
        fd.append('files', fileList[i]!)
      }
      return api<ComposeFromFilesResponse>('/api/submissions/compose-from-files', {
        method: 'POST',
        body: fd,
      })
    },
    onSuccess: (data) => {
      const warnings = data.parts
        .filter((p) => p.warning)
        .map((p) => `${p.filename}: ${p.warning}`)
      setContent((prev) => {
        const block = data.combined.trim()
        if (!block) return prev
        if (!prev.trim()) return block
        return `${prev.trim()}\n\n---\n\n${block}`
      })
      if (warnings.length) {
        setMsg(`Inserted file text. Notes: ${warnings.join(' · ')}`)
      } else {
        setMsg('Inserted text from file(s) into your answer. Edit or add context, then submit.')
      }
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
    onError: (e: Error) => setMsg(e.message),
  })

  const submit = useMutation({
    mutationFn: async () => {
      if (!ex) throw new Error('No exercise selected')
      return api(`/api/submissions`, {
        method: 'POST',
        body: JSON.stringify({ exercise_id: ex.id, content }),
      })
    },
    onSuccess: () => {
      setMsg('Submitted — open Submissions to read your feedback.')
      setContent('')
      qc.invalidateQueries({ queryKey: ['me-dashboard'] })
    },
    onError: (e: Error) => setMsg(e.message),
  })

  const lessonVideoUrl = q.data?.video_url ?? null
  const videoEmbedSrc = useMemo(() => normalizeYoutubeEmbedUrl(lessonVideoUrl), [lessonVideoUrl])
  const videoWatchUrl = useMemo(() => {
    if (!lessonVideoUrl) return null
    return youtubeWatchUrlFromAny(lessonVideoUrl) ?? lessonVideoUrl
  }, [lessonVideoUrl])

  if (!Number.isFinite(id)) return <div className="aw-card aw-error">Invalid lesson</div>
  if (q.isLoading) return <div className="aw-card aw-card-wash">Loading lesson…</div>
  if (q.isError) return <div className="aw-card aw-error">Lesson not found.</div>

  const les = q.data!

  function pickExercise(e: Exercise) {
    setSelectedExerciseId(e.id)
    setContent('')
    setMsg(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  function onFilesChosen(files: FileList | null) {
    if (!files?.length) return
    setMsg(null)
    void composeFiles.mutate(files)
  }

  return (
    <div className="aw-grid" style={{ gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
        <Link to="/roadmap" style={{ opacity: 0.75 }}>
          ← Back to roadmap
        </Link>
        <button type="button" className="aw-btn secondary" onClick={() => complete.mutate()} disabled={complete.isPending}>
          Mark day complete
        </button>
      </div>

      <section className="aw-card aw-card-wash">
        <div className="aw-pill">Day {les.day_index}</div>
        <h1 className="aw-display" style={{ margin: '0.5rem 0 0.5rem' }}>
          {les.title}
        </h1>
        <p style={{ opacity: 0.85 }}>{les.summary}</p>
      </section>

      {/* Exercises first so “what do I do?” is obvious */}
      <section className="aw-card aw-card-wash aw-exercises-hero">
        <h2 style={{ marginTop: 0 }}>Your exercises today</h2>
        <p className="aw-exercises-lead">
          <strong>Six graded exercises per day</strong> — main topic, extended Part 2, then four shorter drills (checklist,
          tradeoff, procedure, snippet review). Each tab is its own submission with length and keyword checks. Use Markdown;
          shallow answers usually score low on auto-review.
        </p>
        {les.exercise_brief ? (
          <p style={{ opacity: 0.82, fontSize: '0.95rem', marginBottom: '1rem' }}>
            <strong>Day theme:</strong> {les.exercise_brief}
          </p>
        ) : null}

        <div className="aw-exercise-outline" role="navigation" aria-label="Exercise list">
          {exercises.map((e, i) => (
            <button
              key={e.id}
              type="button"
              className={e.id === selectedExerciseId ? 'aw-ex-outline-row aw-ex-outline-on' : 'aw-ex-outline-row'}
              onClick={() => pickExercise(e)}
            >
              <span className="aw-ex-num">{i + 1}</span>
              <span className="aw-ex-outline-title">{e.title}</span>
              <span className="aw-pill aw-pill-diff">{e.difficulty}</span>
            </button>
          ))}
        </div>

        <div className="aw-exercise-tabs" role="tablist" aria-label="Switch exercise">
          {exercises.map((e) => (
            <button
              key={e.id}
              type="button"
              role="tab"
              aria-selected={e.id === selectedExerciseId}
              className={e.id === selectedExerciseId ? 'aw-ex-tab aw-ex-tab-on' : 'aw-ex-tab'}
              onClick={() => pickExercise(e)}
            >
              {e.title.length > 36 ? `${e.title.slice(0, 34)}…` : e.title}
            </button>
          ))}
        </div>

        {ex && (
          <>
            <div className="aw-task-panel">
              <div className="aw-task-kicker">
                Task {exIndex + 1} of {exercises.length}
              </div>
              <h3 className="aw-task-title">{ex.title}</h3>
              <div className="aw-task-body">{ex.description}</div>
              {ex.source_attribution ? (
                <p className="aw-task-attrib">
                  <em>Source note:</em> {ex.source_attribution}
                </p>
              ) : null}
            </div>

            <div className="aw-submit-panel">
              <h3 className="aw-submit-heading">Your answer (graded)</h3>
              <p className="aw-submit-hint">
                Type here, paste Markdown, or <strong>add from files</strong> — source code (.py, .ts, …), plain text,
                Markdown, <strong>PDF</strong>, or <strong>Word (.docx)</strong> are turned into text below (multiple files
                merge with separators). Minimum length still applies before you can submit.
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                className="aw-sr-only"
                aria-label="Upload files to insert into your answer"
                accept=".txt,.md,.markdown,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml,.toml,.sh,.ps1,.sql,.html,.css,.scss,.rs,.go,.java,.kt,.c,.h,.cpp,.hpp,.cs,.rb,.php,.swift,.vue,.xml,.csv,.pdf,.docx,text/*,.gitignore"
                onChange={(e) => onFilesChosen(e.target.files)}
              />
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.65rem' }}>
                <button
                  type="button"
                  className="aw-btn secondary"
                  disabled={composeFiles.isPending}
                  onClick={() => fileInputRef.current?.click()}
                >
                  {composeFiles.isPending ? 'Reading files…' : 'Add text from files'}
                </button>
              </div>
              <label>
                <textarea className="aw-input" value={content} onChange={(e) => setContent(e.target.value)} />
              </label>
              {msg && (
                <div
                  className={
                    msg.startsWith('Submitted') || msg.startsWith('Inserted') ? 'aw-submit-msg-ok' : 'aw-error'
                  }
                >
                  {msg}
                </div>
              )}
              <button
                type="button"
                className="aw-btn"
                disabled={submit.isPending || content.length < 20}
                onClick={() => submit.mutate()}
              >
                Submit this exercise
              </button>
            </div>
          </>
        )}
      </section>

      {les.video_url && (
        <section className="aw-card aw-card-wash">
          <h2 style={{ marginTop: 0 }}>Video lesson</h2>
          <p style={{ opacity: 0.78, fontSize: '0.9rem', marginTop: 0 }}>
            Curated YouTube tutorial for this topic. If the player does not load (network or embed restrictions), open the
            same video on YouTube.
          </p>
          {videoEmbedSrc ? (
            <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, borderRadius: 14, overflow: 'hidden' }}>
              <iframe
                title="Lesson video"
                src={videoEmbedSrc}
                style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', border: 0 }}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                loading="lazy"
                referrerPolicy="strict-origin-when-cross-origin"
              />
            </div>
          ) : (
            <p className="aw-error" style={{ marginTop: '0.5rem' }}>
              This lesson’s video URL could not be turned into a YouTube embed.{' '}
              {videoWatchUrl ? (
                <a href={videoWatchUrl} target="_blank" rel="noreferrer">
                  Watch on YouTube
                </a>
              ) : null}
            </p>
          )}
          {videoWatchUrl ? (
            <p style={{ marginTop: '0.75rem', fontSize: '0.9rem', opacity: 0.82 }}>
              <a href={videoWatchUrl} target="_blank" rel="noreferrer">
                Open on YouTube
              </a>{' '}
              (new tab)
            </p>
          ) : null}
        </section>
      )}

      <div className="aw-grid cols-2">
        <section className="aw-card aw-card-wash">
          <h2 style={{ marginTop: 0 }}>Learning goals</h2>
          <ul>
            {les.learning_goals.map((g, i) => (
              <li key={i}>{String(g)}</li>
            ))}
          </ul>
          <h3>Key concepts</h3>
          <ul>
            {les.key_concepts.map((g, i) => (
              <li key={i}>{String(g)}</li>
            ))}
          </ul>
        </section>
        <section className="aw-card aw-card-wash">
          <h2 style={{ marginTop: 0 }}>Deliverables</h2>
          <ul>
            {les.deliverables.map((g, i) => (
              <li key={i}>{String(g)}</li>
            ))}
          </ul>
          <h3>Resources &amp; schedule</h3>
          <ResourceList resources={les.resources} />
        </section>
      </div>

      <section className="aw-card aw-card-wash">
        <h2 style={{ marginTop: 0 }}>Evaluation rubric</h2>
        <ul>
          {les.evaluation_rubric.map((row, i) => (
            <li key={i}>
              <code>{JSON.stringify(row)}</code>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

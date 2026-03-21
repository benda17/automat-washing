import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const stages = [
  {
    title: '1. Sign in',
    body: (
      <>
        Sign in with the username and password issued by your organization. If you cannot access your account, contact
        your cohort administrator.
      </>
    ),
  },
  {
    title: '2. Start from Today',
    body: (
      <>
        Open <Link to="/">Today</Link> to see your current day, readiness, and recent activity. Use{' '}
        <strong>Open day …</strong> to jump straight into that lesson.
      </>
    ),
  },
  {
    title: '3. Use the roadmap when you need the big picture',
    body: (
      <>
        <Link to="/roadmap">15-day roadmap</Link> lists every day in order. Open any day to see its title and summary before
        you commit time to it.
      </>
    ),
  },
  {
    title: '4. Work through each lesson (six graded exercises)',
    body: (
      <>
        Each day has <strong>six separate exercises</strong>, each with its own tab, prompt, minimum length, and keyword
        checks. Suggested order: <strong>main topic</strong> → <strong>Part 2</strong> (extended scenario) →{' '}
        <strong>checklist</strong> → <strong>tradeoff memo</strong> → <strong>procedure</strong> →{' '}
        <strong>snippet review</strong>.
        <ul style={{ marginTop: '0.75rem', paddingLeft: '1.25rem' }}>
          <li>Read the <strong>Day theme</strong> and the task panel before you write.</li>
          <li>
            Markdown is welcome (headings, lists, fenced code blocks); structure usually helps both readers and auto-feedback.
          </li>
          <li>
            Use the <strong>Video lesson</strong> for context; use <strong>Open on YouTube</strong> if the player does not
            load.
          </li>
          <li>
            Submit each exercise when it is complete — you will have six submissions for that day when done. You can use{' '}
            <strong>Add text from files</strong> on the lesson page to pull code, notes, PDF, or Word into the answer box as
            plain text before submitting.
          </li>
        </ul>
      </>
    ),
  },
  {
    title: '5. Submit and read feedback',
    body: (
      <>
        Click <strong>Submit this exercise</strong>. Your answer is stored and an{' '}
        <strong>automatic review</strong> is attached (score out of 100 and written feedback). Open{' '}
        <Link to="/submissions">Submissions</Link> for history: expand <strong>Your content</strong>, read each review, and use
        the <strong>discussion</strong> under a review to reply to mentors, ask questions, or explain how you fixed an issue.
      </>
    ),
  },
  {
    title: '6. Mark the day complete when you are done',
    body: (
      <>
        On the lesson page, use <strong>Mark day complete</strong> when you have finished that day’s exercises and reviewed
        feedback. This updates your progress on Today and the roadmap.
      </>
    ),
  },
  {
    title: '7. If you are a mentor or admin',
    body: (
      <>
        Open <Link to="/admin">Mentor console</Link> (visible only for teacher/admin roles) for roster readiness, submission
        queues, manual reviews, and threaded discussion with students on each review.
      </>
    ),
  },
]

export function GuidePage() {
  const { state } = useAuth()
  const isMentor = state.status === 'authenticated' && (state.user.role === 'teacher' || state.user.role === 'admin')

  return (
    <div className="aw-grid" style={{ gap: '1rem' }}>
      <section className="aw-card aw-card-wash">
        <h1 className="aw-display" style={{ marginTop: 0 }}>
          Using Automat Washing — step by step
        </h1>
        <p style={{ opacity: 0.88, marginBottom: 0 }}>
          Follow these stages in order the first time; afterward you will mostly move between <strong>Today</strong>,{' '}
          <strong>lessons</strong>, and <strong>Submissions</strong>.
        </p>
      </section>

      {stages.map((s, i) => {
        if (s.title.startsWith('7.') && !isMentor) return null
        return (
          <section key={i} className="aw-card aw-card-wash aw-guide-stage">
            <h2 style={{ marginTop: 0, fontSize: '1.15rem' }}>{s.title}</h2>
            <div className="aw-guide-stage-body" style={{ opacity: 0.92 }}>
              {s.body}
            </div>
          </section>
        )
      })}

      <section className="aw-card aw-card-wash" style={{ borderColor: 'var(--border-focus)' }}>
        <h2 style={{ marginTop: 0, fontSize: '1.05rem' }}>If something looks wrong</h2>
        <p style={{ margin: 0, opacity: 0.9 }}>
          Contact your cohort administrator if lessons do not load, login always fails, or grades look out of date.
        </p>
      </section>
    </div>
  )
}

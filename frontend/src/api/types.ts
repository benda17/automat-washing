export type Role = 'admin' | 'teacher' | 'student'

export interface User {
  id: number
  username: string
  email: string | null
  full_name: string
  role: Role
}

export interface Exercise {
  id: number
  slug: string
  title: string
  description: string
  difficulty: string
  exercise_type: string
  source_attribution: string | null
  sort_order: number
}

export interface ScheduleBlock {
  hours: number
  title: string
  detail: string
}

export interface LessonResource {
  label: string
  url: string
  note?: string
  blocks?: ScheduleBlock[]
}

export interface LessonSummary {
  id: number
  day_index: number
  slug: string
  title: string
  summary: string
  locked: boolean
  video_url: string | null
  completed: boolean
  completion_percent: number
}

export interface LessonDetail extends LessonSummary {
  key_concepts: unknown[]
  resources: LessonResource[]
  learning_goals: unknown[]
  deliverables: unknown[]
  evaluation_rubric: unknown[]
  exercise_brief: string
  exercises: Exercise[]
}

export interface Module {
  id: number
  slug: string
  title: string
  summary: string | null
  sort_order: number
  lessons: LessonSummary[]
}

export interface Course {
  id: number
  slug: string
  title: string
  description: string | null
  duration_days: number
  modules: Module[]
}

export interface ReviewComment {
  id: number
  author_id: number
  author_username: string
  author_full_name: string
  author_role: Role
  body: string
  created_at: string
}

export interface Review {
  id: number
  is_auto: boolean
  overall_score: number
  dimension_scores: Record<string, number>
  feedback: string
  strengths: string[]
  weaknesses: string[]
  improvements: string[]
  mentor_tone_notes: string | null
  created_at: string
  reviewer_id: number | null
  comments: ReviewComment[]
}

export interface ComposedFilePart {
  filename: string
  text: string
  warning: string | null
}

export interface ComposeFromFilesResponse {
  parts: ComposedFilePart[]
  combined: string
}

export interface Submission {
  id: number
  exercise_id: number
  student_id: number
  content: string
  status: string
  created_at: string
  reviews: Review[]
  student_username?: string | null
  student_email?: string | null
  student_full_name?: string | null
  exercise_title?: string | null
  lesson_title?: string | null
  lesson_day_index?: number | null
}

/** Normalize any common YouTube URL into a canonical embed URL so iframes load reliably. */

const ID_RE = /^[A-Za-z0-9_-]{11}$/

export function normalizeYoutubeEmbedUrl(raw: string | null | undefined): string | null {
  if (!raw?.trim()) return null
  const s = raw.trim()
  try {
    const u = new URL(s, 'https://www.youtube.com')
    const host = u.hostname.replace(/^www\./, '')
    let id: string | null = null

    if (host === 'youtube.com' || host === 'm.youtube.com' || host === 'youtube-nocookie.com') {
      if (u.pathname.startsWith('/embed/')) {
        id = u.pathname.slice('/embed/'.length).split('/')[0]?.split('?')[0] ?? null
      } else if (u.pathname === '/watch' || u.pathname.startsWith('/watch/')) {
        id = u.searchParams.get('v')
      }
    } else if (host === 'youtu.be') {
      id = u.pathname.slice(1).split('/')[0] || null
    }

    if (!id || !ID_RE.test(id)) return null
    return `https://www.youtube.com/embed/${id}?rel=0`
  } catch {
    return null
  }
}

export function youtubeWatchUrlFromAny(raw: string | null | undefined): string | null {
  if (!raw?.trim()) return null
  const s = raw.trim()
  const fromEmbed = normalizeYoutubeEmbedUrl(s)
  if (fromEmbed) {
    const m = fromEmbed.match(/\/embed\/([^?]+)/)
    const id = m?.[1]
    if (id) return `https://www.youtube.com/watch?v=${id}`
  }
  try {
    const u = new URL(s, 'https://www.youtube.com')
    if (u.hostname.includes('youtube.com') && u.searchParams.get('v')) {
      return `https://www.youtube.com/watch?v=${u.searchParams.get('v')}`
    }
    if (u.hostname === 'youtu.be' && u.pathname.length > 1) {
      const id = u.pathname.slice(1).split('/')[0]
      if (id && ID_RE.test(id)) return `https://www.youtube.com/watch?v=${id}`
    }
  } catch {
    /* ignore */
  }
  return /^https?:\/\//i.test(s) ? s : null
}

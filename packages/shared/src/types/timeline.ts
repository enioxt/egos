// AUTO-GENERATED Supabase TypeScript types — timeline + AI publishing
// Source: egos-lab project (lhscgsqhiooyatkebose)
// Generated: 2026-04-08 | TL-001
// DO NOT EDIT manually — regenerate with: supabase gen types typescript

// Base Json type (from Supabase)
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface TimelineDrafts {
  approved_at: string | null
  approved_by: string | null
  body_md: string
  created_at: string | null
  drift_check_passed: boolean | null
  id: string
  llm_cost_usd: number | null
  llm_provider: string | null
  pii_check_passed: boolean | null
  rejected_reason: string | null
  slug: string
  source_commits: string[]
  source_files: string[] | null
  status: string
  summary: string
  tags: string[] | null
  title: string
}

export type TimelineDraftsRow = TimelineDrafts
export type TimelineDraftsInsert = Partial<TimelineDrafts> & Pick<TimelineDrafts, 'slug' | 'title' | 'summary' | 'body_md' | 'source_commits'>

export interface TimelineArticles {
  body_html: string
  draft_id: string | null
  engagement_json: Json | null
  id: string
  published_at: string | null
  slug: string
  title: string
  url: string
  views: number | null
  x_post_id: string | null
  x_post_url: string | null
}

export type TimelineArticlesRow = TimelineArticles
export type TimelineArticlesInsert = Partial<TimelineArticles> & Pick<TimelineArticles, 'slug' | 'title' | 'body_html' | 'url'>

export interface XPostQueue {
  article_id: string | null
  id: string
  posted_at: string | null
  scheduled_for: string | null
  status: string | null
  text: string
  thread_position: number | null
  tweet_id: string | null
}

export type XPostQueueRow = XPostQueue
export type XPostQueueInsert = Partial<XPostQueue> & Pick<XPostQueue, 'text'>

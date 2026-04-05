import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? '';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? '';

// Server-side client (service role — never expose to browser)
export function createServerClient() {
  return createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
}

// Browser-safe client (anon key)
export function createBrowserClient() {
  return createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
}

export type XReplyRun = {
  id: string;
  run_at: string;
  topic: string | null;
  tweet_id: string | null;
  tweet_text: string | null;
  tweet_author: string | null;
  tweet_likes: number;
  generated_reply: string | null;
  status: 'pending' | 'approved' | 'rejected' | 'sent' | 'dry_run';
  sent_at: string | null;
  error: string | null;
  created_at: string;
};

export type AgentEvent = {
  id: string;
  created_at: string;
  source: string;
  event_type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  payload: Record<string, unknown>;
  correlation_id: string | null;
};

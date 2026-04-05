'use client';

import { useEffect, useState, useCallback } from 'react';
import { HQLayout } from '../hq-layout';

type XRun = {
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
};

type Tweet = {
  id: string;
  text: string;
  created_at: string;
  author: { name: string; username: string; profile_image_url?: string };
  metrics: { like_count: number; retweet_count: number; reply_count: number };
  url: string;
};

type Tab = 'queue' | 'search' | 'history';

function TweetCard({ run, onApprove, onReject }: { run: XRun; onApprove: (id: string, text: string) => void; onReject: (id: string) => void }) {
  const [reply, setReply] = useState(run.generated_reply ?? '');
  const [loading, setLoading] = useState(false);

  async function handleApprove() {
    if (!reply.trim()) return;
    setLoading(true);
    await onApprove(run.id, reply);
    setLoading(false);
  }

  async function regenerate() {
    setLoading(true);
    try {
      const res = await fetch('/api/x', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'suggest', tweet_text: run.tweet_text }),
      });
      const d = await res.json();
      if (d.suggestions?.[0]) setReply(d.suggestions[0]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 10, padding: '1.25rem', marginBottom: '1rem' }}>
      {/* Tweet */}
      <div style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ color: '#22c55e', fontSize: 12, fontWeight: 700 }}>@{run.tweet_author ?? 'unknown'}</span>
          <div style={{ display: 'flex', gap: 12, fontSize: 11, color: '#555' }}>
            <span>♥ {run.tweet_likes}</span>
            <span style={{ color: '#555' }}>{run.topic ?? 'manual'}</span>
            <a href={`https://x.com/i/status/${run.tweet_id}`} target="_blank" rel="noopener" style={{ color: '#3b82f6' }}>↗</a>
          </div>
        </div>
        <div style={{ fontSize: 13, color: '#e5e5e5', lineHeight: 1.5, borderLeft: '2px solid #1f1f1f', paddingLeft: 10 }}>
          {run.tweet_text}
        </div>
      </div>

      {/* Reply editor */}
      <div style={{ marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 11, color: '#555', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Sua resposta</span>
          <span style={{ fontSize: 11, color: reply.length > 260 ? '#ef4444' : '#555' }}>{reply.length}/280</span>
        </div>
        <textarea
          value={reply}
          onChange={e => setReply(e.target.value)}
          rows={3}
          maxLength={280}
          style={{
            width: '100%',
            background: '#0a0a0a',
            border: '1px solid #1f1f1f',
            borderRadius: 8,
            color: '#e5e5e5',
            padding: '0.75rem',
            fontSize: 13,
            lineHeight: 1.5,
            resize: 'vertical',
            outline: 'none',
            fontFamily: 'inherit',
          }}
        />
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={handleApprove}
          disabled={loading || !reply.trim()}
          style={{ padding: '0.5rem 1.25rem', background: '#22c55e', color: '#000', fontWeight: 700, fontSize: 13, border: 'none', borderRadius: 6, cursor: loading ? 'wait' : 'pointer', fontFamily: 'inherit', opacity: !reply.trim() ? 0.5 : 1 }}
        >
          {loading ? '...' : '✓ Aprovar e Postar'}
        </button>
        <button
          onClick={regenerate}
          disabled={loading}
          style={{ padding: '0.5rem 0.75rem', background: 'transparent', border: '1px solid #1f1f1f', color: '#737373', fontSize: 13, borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit' }}
        >
          ↺ Regenerar
        </button>
        <button
          onClick={() => onReject(run.id)}
          disabled={loading}
          style={{ padding: '0.5rem 0.75rem', background: 'transparent', border: '1px solid #2a1010', color: '#ef4444', fontSize: 13, borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit', marginLeft: 'auto' }}
        >
          ✕ Rejeitar
        </button>
      </div>
    </div>
  );
}

function SearchTab() {
  const [query, setQuery] = useState('');
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Array<{ q: string; label: string }>>([]);
  const [selectedTweet, setSelectedTweet] = useState<Tweet | null>(null);
  const [replyText, setReplyText] = useState('');
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<{ ok: boolean; msg: string } | null>(null);

  useEffect(() => {
    fetch('/api/x?action=suggestions').then(r => r.json()).then(d => setSuggestions(d.queries ?? []));
  }, []);

  async function search(q: string) {
    setQuery(q);
    setLoading(true);
    try {
      const res = await fetch(`/api/x?action=search&q=${encodeURIComponent(q)}&max=15`);
      const d = await res.json();
      setTweets(d.tweets ?? []);
    } finally {
      setLoading(false);
    }
  }

  async function openReply(tweet: Tweet) {
    setSelectedTweet(tweet);
    setReplyText('');
    setPostResult(null);
    // Auto-suggest
    const res = await fetch('/api/x', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'suggest', tweet_text: tweet.text }),
    });
    const d = await res.json();
    setReplyText(d.suggestions?.[0] ?? '');
  }

  async function postReply() {
    if (!selectedTweet || !replyText.trim()) return;
    setPosting(true);
    try {
      const res = await fetch('/api/x', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'reply', tweet_id: selectedTweet.id, text: replyText }),
      });
      const d = await res.json();
      if (d.success) {
        setPostResult({ ok: true, msg: 'Reply postado!' });
        setSelectedTweet(null);
      } else {
        setPostResult({ ok: false, msg: d.error ?? 'Erro ao postar' });
      }
    } finally {
      setPosting(false);
    }
  }

  return (
    <div>
      {/* Search bar */}
      <div style={{ display: 'flex', gap: 8, marginBottom: '1rem' }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search(query)}
          placeholder="Buscar tweets... (Enter para pesquisar)"
          style={{ flex: 1, padding: '0.6rem 1rem', background: '#111', border: '1px solid #1f1f1f', borderRadius: 8, color: '#e5e5e5', fontSize: 13, outline: 'none', fontFamily: 'inherit' }}
        />
        <button onClick={() => search(query)} disabled={loading || !query.trim()} style={{ padding: '0.6rem 1.25rem', background: '#22c55e', color: '#000', fontWeight: 700, border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 13, fontFamily: 'inherit' }}>
          {loading ? '...' : 'Buscar'}
        </button>
      </div>

      {/* Preset queries */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: '1.5rem' }}>
        {suggestions.map(s => (
          <button
            key={s.q}
            onClick={() => search(s.q)}
            style={{ padding: '0.3rem 0.75rem', background: '#0f0f0f', border: '1px solid #1f1f1f', borderRadius: 9999, color: '#737373', fontSize: 11, cursor: 'pointer', fontFamily: 'inherit' }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {postResult && (
        <div style={{ padding: '0.75rem', background: postResult.ok ? '#0f1f0f' : '#1a0505', border: `1px solid ${postResult.ok ? '#22c55e' : '#ef4444'}`, borderRadius: 8, color: postResult.ok ? '#22c55e' : '#ef4444', fontSize: 13, marginBottom: '1rem' }}>
          {postResult.msg}
        </div>
      )}

      {/* Results */}
      {tweets.length > 0 && (
        <div>
          {tweets.map(tweet => (
            <div key={tweet.id} style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 10, padding: '1rem', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{ color: '#22c55e', fontSize: 12, fontWeight: 700 }}>@{tweet.author.username}</span>
                <div style={{ display: 'flex', gap: 12, fontSize: 11, color: '#555' }}>
                  <span>♥ {tweet.metrics?.like_count ?? 0}</span>
                  <a href={tweet.url} target="_blank" rel="noopener" style={{ color: '#3b82f6' }}>↗</a>
                </div>
              </div>
              <div style={{ fontSize: 13, color: '#e5e5e5', lineHeight: 1.5, marginBottom: 10 }}>{tweet.text}</div>
              <button
                onClick={() => openReply(tweet)}
                style={{ padding: '0.4rem 1rem', background: 'transparent', border: '1px solid #22c55e', color: '#22c55e', fontSize: 12, borderRadius: 6, cursor: 'pointer', fontFamily: 'inherit' }}
              >
                ↩ Responder
              </button>
            </div>
          ))}
        </div>
      )}

      {loading && <div style={{ color: '#555', fontSize: 13 }}>Buscando...</div>}

      {/* Reply Modal */}
      {selectedTweet && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: '1rem' }}>
          <div style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 12, padding: '1.5rem', width: '100%', maxWidth: 560 }}>
            <div style={{ fontSize: 13, color: '#e5e5e5', marginBottom: '1rem', borderLeft: '2px solid #22c55e', paddingLeft: 10 }}>
              {selectedTweet.text}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontSize: 11, color: '#555' }}>Sua resposta</span>
              <span style={{ fontSize: 11, color: replyText.length > 260 ? '#ef4444' : '#555' }}>{replyText.length}/280</span>
            </div>
            <textarea
              value={replyText}
              onChange={e => setReplyText(e.target.value)}
              rows={4}
              maxLength={280}
              style={{ width: '100%', background: '#0a0a0a', border: '1px solid #1f1f1f', borderRadius: 8, color: '#e5e5e5', padding: '0.75rem', fontSize: 13, lineHeight: 1.5, resize: 'vertical', outline: 'none', fontFamily: 'inherit', marginBottom: '1rem' }}
            />
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={postReply} disabled={posting || !replyText.trim()} style={{ padding: '0.6rem 1.5rem', background: '#22c55e', color: '#000', fontWeight: 700, border: 'none', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit', opacity: !replyText.trim() ? 0.5 : 1 }}>
                {posting ? 'Postando...' : '✓ Postar Reply'}
              </button>
              <button onClick={() => setSelectedTweet(null)} style={{ padding: '0.6rem 1rem', background: 'transparent', border: '1px solid #1f1f1f', color: '#737373', borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit' }}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function XPage() {
  const [tab, setTab] = useState<Tab>('queue');
  const [queue, setQueue] = useState<XRun[]>([]);
  const [history, setHistory] = useState<XRun[]>([]);
  const [loadingQueue, setLoadingQueue] = useState(true);

  const loadQueue = useCallback(async () => {
    setLoadingQueue(true);
    try {
      const res = await fetch('/api/x?action=queue&status=pending');
      const d = await res.json();
      setQueue(d.runs ?? []);
    } finally {
      setLoadingQueue(false);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    const res = await fetch('/api/x?action=queue&status=sent&limit=50');
    const d = await res.json();
    setHistory(d.runs ?? []);
  }, []);

  useEffect(() => { loadQueue(); }, [loadQueue]);
  useEffect(() => { if (tab === 'history') loadHistory(); }, [tab, loadHistory]);

  async function handleApprove(runId: string, text: string) {
    const res = await fetch('/api/x', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'approve', run_id: runId, text }),
    });
    if (res.ok) setQueue(q => q.filter(r => r.id !== runId));
  }

  async function handleReject(runId: string) {
    await fetch('/api/x', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'reject', run_id: runId }),
    });
    setQueue(q => q.filter(r => r.id !== runId));
  }

  const tabStyle = (t: Tab) => ({
    padding: '0.5rem 1.25rem',
    background: tab === t ? '#0f1f0f' : 'transparent',
    border: 'none',
    borderBottom: tab === t ? '2px solid #22c55e' : '2px solid transparent',
    color: tab === t ? '#22c55e' : '#737373',
    fontSize: 13,
    cursor: 'pointer',
    fontFamily: 'inherit',
  });

  return (
    <HQLayout pendingCount={queue.length}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e5e5e5', margin: 0 }}>𝕏 Monitor</h1>
          <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>Cron horário · Bot monitorando 8 tópicos</div>
        </div>
        <button onClick={loadQueue} style={{ padding: '0.4rem 1rem', background: 'transparent', border: '1px solid #1f1f1f', borderRadius: 6, color: '#737373', fontSize: 12, cursor: 'pointer', fontFamily: 'inherit' }}>
          ↻ Refresh
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1f1f1f', marginBottom: '1.5rem' }}>
        <button style={tabStyle('queue')} onClick={() => setTab('queue')}>
          Fila do Bot {queue.length > 0 && <span style={{ marginLeft: 6, background: '#22c55e', color: '#000', fontSize: 10, fontWeight: 700, padding: '1px 5px', borderRadius: 9999 }}>{queue.length}</span>}
        </button>
        <button style={tabStyle('search')} onClick={() => setTab('search')}>Busca Manual</button>
        <button style={tabStyle('history')} onClick={() => setTab('history')}>Histórico</button>
      </div>

      {/* Queue tab */}
      {tab === 'queue' && (
        <div>
          {loadingQueue ? (
            <div style={{ color: '#555', fontSize: 13 }}>Carregando fila...</div>
          ) : queue.length === 0 ? (
            <div style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 10, padding: '2rem', textAlign: 'center' }}>
              <div style={{ fontSize: 32, marginBottom: 8 }}>✓</div>
              <div style={{ color: '#555', fontSize: 13 }}>Fila vazia — nenhum reply pendente.</div>
              <div style={{ color: '#444', fontSize: 12, marginTop: 4 }}>O bot horário adicionará tweets aqui automaticamente.</div>
            </div>
          ) : (
            queue.map(run => (
              <TweetCard key={run.id} run={run} onApprove={handleApprove} onReject={handleReject} />
            ))
          )}
        </div>
      )}

      {/* Search tab */}
      {tab === 'search' && <SearchTab />}

      {/* History tab */}
      {tab === 'history' && (
        <div>
          {history.length === 0 ? (
            <div style={{ color: '#555', fontSize: 13 }}>Nenhum reply enviado ainda.</div>
          ) : (
            history.map(run => (
              <div key={run.id} style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 8, padding: '1rem', marginBottom: '0.5rem', display: 'flex', gap: 12 }}>
                <span style={{
                  fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 9999, height: 'fit-content',
                  background: run.status === 'sent' ? '#0f1f0f' : '#1a0a0a',
                  color: run.status === 'sent' ? '#22c55e' : '#ef4444',
                  border: `1px solid ${run.status === 'sent' ? '#22c55e' : '#ef4444'}`,
                  textTransform: 'uppercase',
                  flexShrink: 0,
                }}>
                  {run.status}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, color: '#22c55e', marginBottom: 4 }}>@{run.tweet_author ?? '?'} · {run.topic}</div>
                  <div style={{ fontSize: 12, color: '#737373', lineHeight: 1.4, marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{run.tweet_text}</div>
                  {run.generated_reply && <div style={{ fontSize: 12, color: '#e5e5e5', lineHeight: 1.4 }}>↩ {run.generated_reply}</div>}
                </div>
                <div style={{ fontSize: 11, color: '#555', flexShrink: 0 }}>
                  {run.sent_at ? new Date(run.sent_at).toLocaleDateString('pt-BR') : new Date(run.run_at).toLocaleDateString('pt-BR')}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </HQLayout>
  );
}

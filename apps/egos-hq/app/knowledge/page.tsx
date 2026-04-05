'use client';

import { useEffect, useState, useCallback } from 'react';
import { HQLayout } from '../hq-layout';

const GW = process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'https://gateway.egos.ia.br';

interface WikiPage {
  id: string;
  slug: string;
  title: string;
  category: string;
  quality_score: number;
  tags: string[];
  summary?: string;
  updated_at: string;
}

interface WikiStats {
  pages: { total: number; avg_quality: number; by_category: Record<string, number> };
  learnings: { total: number; by_domain: Record<string, number>; by_outcome: Record<string, number> };
}

interface Learning {
  id: string;
  domain: string;
  outcome: string;
  description: string;
  created_at: string;
}

const CAT_COLOR: Record<string, string> = {
  synthesis: '#8b5cf6',
  decision: '#3b82f6',
  pattern: '#22c55e',
  entity: '#f59e0b',
  concept: '#ec4899',
  'how-to': '#06b6d4',
};

function QualityBar({ score }: { score: number }) {
  const color = score >= 80 ? '#22c55e' : score >= 60 ? '#f59e0b' : '#ef4444';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{ flex: 1, height: 4, background: '#1f1f1f', borderRadius: 2 }}>
        <div style={{ width: `${score}%`, height: '100%', background: color, borderRadius: 2 }} />
      </div>
      <span style={{ fontSize: 11, color, minWidth: 28, textAlign: 'right' }}>{score}</span>
    </div>
  );
}

export default function KnowledgePage() {
  const [stats, setStats] = useState<WikiStats | null>(null);
  const [pages, setPages] = useState<WikiPage[]>([]);
  const [learnings, setLearnings] = useState<Learning[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [activeTab, setActiveTab] = useState<'pages' | 'learnings'>('pages');
  const [selectedPage, setSelectedPage] = useState<WikiPage | null>(null);

  async function loadAll() {
    const [statsRes, pagesRes, learningsRes] = await Promise.all([
      fetch(`${GW}/knowledge/stats`).then(r => r.ok ? r.json() : null),
      fetch(`${GW}/knowledge/pages?limit=100`).then(r => r.ok ? r.json() : null),
      fetch(`${GW}/knowledge/learnings?limit=50`).then(r => r.ok ? r.json() : null),
    ]);
    if (statsRes) setStats(statsRes);
    if (pagesRes) setPages(pagesRes.pages ?? pagesRes ?? []);
    if (learningsRes) setLearnings(learningsRes.learnings ?? learningsRes ?? []);
    setLoading(false);
  }

  const search = useCallback(async (q: string) => {
    if (!q.trim()) { loadAll(); return; }
    setSearching(true);
    try {
      const res = await fetch(`${GW}/knowledge/search?q=${encodeURIComponent(q)}`);
      if (res.ok) { const d = await res.json(); setPages(d.results ?? []); }
    } finally { setSearching(false); }
  }, []);

  useEffect(() => { loadAll(); }, []);
  useEffect(() => {
    const t = setTimeout(() => search(query), 300);
    return () => clearTimeout(t);
  }, [query, search]);

  return (
    <HQLayout>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: '#e5e5e5', margin: 0 }}>Knowledge Base</h1>
          <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>
            {loading ? 'Carregando...' : `${stats?.pages.total ?? 0} páginas · qualidade ${stats?.pages.avg_quality ?? 0}/100 · ${stats?.learnings.total ?? 0} learnings`}
          </div>
        </div>
        <a href={`${GW}/ui`} target="_blank" rel="noreferrer"
          style={{ padding: '0.4rem 0.8rem', background: '#1f1f1f', border: '1px solid #2f2f2f', borderRadius: 6, color: '#737373', fontSize: 12, textDecoration: 'none' }}>
          ↗ Gateway UI
        </a>
      </div>

      {/* Category pills */}
      {stats && (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: '1.25rem' }}>
          {Object.entries(stats.pages.by_category).map(([cat, count]) => (
            <button key={cat} onClick={() => setQuery(cat)}
              style={{ padding: '0.3rem 0.7rem', background: '#111', border: `1px solid ${CAT_COLOR[cat] ?? '#2f2f2f'}44`, borderRadius: 20, display: 'flex', alignItems: 'center', gap: 5, cursor: 'pointer', fontFamily: 'inherit' }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: CAT_COLOR[cat] ?? '#555' }} />
              <span style={{ fontSize: 12, color: '#d4d4d4' }}>{cat}</span>
              <span style={{ fontSize: 11, color: '#555' }}>{count}</span>
            </button>
          ))}
        </div>
      )}

      {/* Search */}
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Buscar páginas... (ex: orchestration, guard, agent)"
        style={{ width: '100%', padding: '0.6rem 0.875rem', background: '#111', border: '1px solid #1f1f1f', borderRadius: 6, color: '#e5e5e5', fontSize: 13, outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box', marginBottom: '1.25rem' }}
      />

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 0, marginBottom: '1rem', borderBottom: '1px solid #1f1f1f' }}>
        {(['pages', 'learnings'] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            style={{ padding: '0.5rem 1rem', background: 'transparent', border: 'none', borderBottom: `2px solid ${activeTab === tab ? '#22c55e' : 'transparent'}`, color: activeTab === tab ? '#22c55e' : '#555', fontSize: 13, cursor: 'pointer', fontFamily: 'inherit' }}>
            {tab === 'pages' ? `Páginas (${pages.length})` : `Learnings (${learnings.length})`}
          </button>
        ))}
      </div>

      {/* Pages list */}
      {activeTab === 'pages' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {searching && <div style={{ fontSize: 12, color: '#555', padding: '0.5rem' }}>Buscando...</div>}
          {pages.map(page => (
            <div key={page.id} onClick={() => setSelectedPage(selectedPage?.id === page.id ? null : page)}
              style={{ padding: '0.75rem 1rem', background: '#111', border: `1px solid ${selectedPage?.id === page.id ? '#22c55e44' : '#1f1f1f'}`, borderRadius: 6, cursor: 'pointer' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: CAT_COLOR[page.category] ?? '#555', flexShrink: 0 }} />
                <span style={{ fontSize: 13, color: '#e5e5e5', flex: 1, fontWeight: 500 }}>{page.title}</span>
                <span style={{ fontSize: 11, color: '#444' }}>{page.category}</span>
              </div>
              <QualityBar score={page.quality_score ?? 0} />
              {selectedPage?.id === page.id && page.summary && (
                <div style={{ marginTop: 8, fontSize: 12, color: '#737373', lineHeight: 1.5, borderTop: '1px solid #1a1a1a', paddingTop: 8 }}>
                  {page.summary}
                  <div style={{ marginTop: 6, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    {(page.tags ?? []).map(t => (
                      <span key={t} onClick={e => { e.stopPropagation(); setQuery(t); }}
                        style={{ padding: '1px 6px', background: '#1f1f1f', borderRadius: 4, fontSize: 10, color: '#555', cursor: 'pointer' }}>#{t}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {pages.length === 0 && !searching && (
            <div style={{ fontSize: 13, color: '#555', padding: '1rem', textAlign: 'center' }}>Nenhuma página encontrada</div>
          )}
        </div>
      )}

      {/* Learnings list */}
      {activeTab === 'learnings' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {learnings.map(l => (
            <div key={l.id} style={{ padding: '0.75rem 1rem', background: '#111', border: '1px solid #1f1f1f', borderRadius: 6 }}>
              <div style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'center' }}>
                <span style={{ fontSize: 11, padding: '1px 6px', background: '#1f1f1f', borderRadius: 4, color: '#737373' }}>{l.domain}</span>
                <span style={{ fontSize: 11, padding: '1px 6px', background: l.outcome === 'success' ? '#0f1f0f' : '#1f0f0f', borderRadius: 4, color: l.outcome === 'success' ? '#22c55e' : '#ef4444' }}>{l.outcome}</span>
                <span style={{ fontSize: 11, color: '#444', marginLeft: 'auto' }}>{new Date(l.created_at).toLocaleDateString('pt-BR')}</span>
              </div>
              <div style={{ fontSize: 12, color: '#d4d4d4', lineHeight: 1.5 }}>{l.description}</div>
            </div>
          ))}
          {learnings.length === 0 && (
            <div style={{ fontSize: 13, color: '#555', padding: '1rem', textAlign: 'center' }}>Nenhum learning ainda. Use /end para registrar insights de sessão.</div>
          )}
        </div>
      )}
    </HQLayout>
  );
}

'use client';

import { useEffect, useState, useRef } from 'react';
import { HQLayout } from '../hq-layout';

type AgentEvent = {
  id: string;
  created_at: string;
  source: string;
  event_type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  payload: Record<string, unknown>;
  correlation_id: string | null;
};

const SEV_COLOR: Record<string, string> = { info: '#3b82f6', warning: '#f59e0b', error: '#ef4444', critical: '#dc2626' };
const SEV_BG: Record<string, string> = { info: '#0a1020', warning: '#1a1200', error: '#1a0505', critical: '#1a0505' };

export default function EventsPage() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load initial events
    fetch('/api/hq/events')
      .then(r => r.json())
      .then(d => { setEvents(d.events ?? []); setLoading(false); });
  }, []);

  useEffect(() => {
    if (!live) return;
    const iv = setInterval(async () => {
      const res = await fetch('/api/hq/events?limit=5');
      const d = await res.json();
      if (d.events?.length > 0) {
        setEvents(prev => {
          const ids = new Set(prev.map(e => e.id));
          const newEvs = (d.events as AgentEvent[]).filter(e => !ids.has(e.id));
          if (newEvs.length === 0) return prev;
          setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
          return [...prev, ...newEvs].slice(-200); // keep last 200
        });
      }
    }, 5000);
    return () => clearInterval(iv);
  }, [live]);

  const filtered = filter === 'all' ? events : events.filter(e => e.severity === filter);

  return (
    <HQLayout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e5e5e5', margin: 0 }}>◉ Eventos Live</h1>
          <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>Stream de eventos do backend · Polling 5s</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={() => setLive(!live)}
            style={{
              padding: '0.4rem 1rem',
              background: live ? '#0f1f0f' : 'transparent',
              border: `1px solid ${live ? '#22c55e' : '#1f1f1f'}`,
              borderRadius: 6,
              color: live ? '#22c55e' : '#737373',
              fontSize: 12,
              cursor: 'pointer',
              fontFamily: 'inherit',
            }}
          >
            {live ? '● Live' : '○ Pausado'}
          </button>
        </div>
      </div>

      {/* Severity filter */}
      <div style={{ display: 'flex', gap: 8, marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {['all', 'info', 'warning', 'error', 'critical'].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{
              padding: '0.3rem 0.75rem',
              background: filter === s ? `${SEV_COLOR[s] ?? '#555'}20` : 'transparent',
              border: `1px solid ${filter === s ? (SEV_COLOR[s] ?? '#22c55e') : '#1f1f1f'}`,
              borderRadius: 9999,
              color: filter === s ? (SEV_COLOR[s] ?? '#22c55e') : '#737373',
              fontSize: 12,
              cursor: 'pointer',
              fontFamily: 'inherit',
            }}
          >
            {s === 'all' ? `Todos (${events.length})` : `${s} (${events.filter(e => e.severity === s).length})`}
          </button>
        ))}
      </div>

      {/* Event log */}
      <div style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 10, overflow: 'hidden', maxHeight: 'calc(100vh - 260px)', overflowY: 'auto' }}>
        {loading ? (
          <div style={{ padding: '2rem', color: '#555', fontSize: 13 }}>Carregando eventos...</div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>◉</div>
            <div style={{ color: '#555', fontSize: 13 }}>Nenhum evento registrado ainda.</div>
            <div style={{ color: '#444', fontSize: 12, marginTop: 4 }}>Quando agentes rodarem, os eventos aparecerão aqui em tempo real.</div>
          </div>
        ) : (
          <div style={{ fontFamily: 'monospace' }}>
            {filtered.map((ev, i) => (
              <div
                key={ev.id}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '160px 80px 140px 1fr',
                  gap: '0 12px',
                  padding: '0.4rem 1rem',
                  background: i % 2 === 0 ? '#111' : '#0d0d0d',
                  borderBottom: '1px solid #161616',
                  alignItems: 'start',
                }}
              >
                <span style={{ fontSize: 11, color: '#555', whiteSpace: 'nowrap' }}>
                  {new Date(ev.created_at).toLocaleString('pt-BR', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
                <span style={{
                  fontSize: 10,
                  fontWeight: 700,
                  color: SEV_COLOR[ev.severity],
                  background: SEV_BG[ev.severity],
                  padding: '1px 6px',
                  borderRadius: 3,
                  textTransform: 'uppercase',
                  width: 'fit-content',
                }}>
                  {ev.severity}
                </span>
                <span style={{ fontSize: 12, color: '#22c55e', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {ev.source}
                </span>
                <div>
                  <span style={{ fontSize: 12, color: '#e5e5e5' }}>{ev.event_type}</span>
                  {ev.payload && Object.keys(ev.payload).length > 0 && (
                    <span style={{ fontSize: 11, color: '#555', marginLeft: 8 }}>
                      {JSON.stringify(ev.payload).slice(0, 80)}
                    </span>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </HQLayout>
  );
}

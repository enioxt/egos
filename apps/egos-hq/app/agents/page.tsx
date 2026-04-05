'use client';

import { useEffect, useState } from 'react';
import { HQLayout } from '../hq-layout';

type Agent = {
  id: string;
  name: string;
  area: string;
  status: 'active' | 'placeholder' | 'pending' | 'disabled' | 'dead';
  kind: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  triggers: string[];
  entrypoint: string;
  description?: string;
};

const RISK_COLOR: Record<string, string> = { low: '#22c55e', medium: '#f59e0b', high: '#ef4444', critical: '#dc2626' };
const STATUS_COLOR: Record<string, string> = { active: '#22c55e', placeholder: '#f59e0b', pending: '#3b82f6', disabled: '#555', dead: '#ef4444' };

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetch('/api/hq/agents')
      .then(r => r.json())
      .then(d => { setAgents(d.agents ?? []); setLoading(false); });
  }, []);

  const filtered = filter === 'all' ? agents : agents.filter(a => a.status === filter);
  const counts = agents.reduce<Record<string, number>>((acc, a) => { acc[a.status] = (acc[a.status] ?? 0) + 1; return acc; }, {});

  return (
    <HQLayout>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e5e5e5', margin: 0 }}>Agentes EGOS</h1>
        <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>Registry v2.1.0 · {agents.length} agentes registrados</div>
      </div>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {['all', 'active', 'placeholder', 'dead', 'disabled'].map(s => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{
              padding: '0.3rem 0.75rem',
              background: filter === s ? '#0f1f0f' : 'transparent',
              border: `1px solid ${filter === s ? '#22c55e' : '#1f1f1f'}`,
              borderRadius: 9999,
              color: filter === s ? '#22c55e' : '#737373',
              fontSize: 12,
              cursor: 'pointer',
              fontFamily: 'inherit',
            }}
          >
            {s === 'all' ? `Todos (${agents.length})` : `${s} (${counts[s] ?? 0})`}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ color: '#555' }}>Carregando agentes...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '0.75rem' }}>
          {filtered.map(agent => (
            <div key={agent.id} style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 10, padding: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#e5e5e5' }}>{agent.id}</div>
                  <div style={{ fontSize: 11, color: '#737373', marginTop: 2 }}>{agent.name}</div>
                </div>
                <span style={{
                  fontSize: 10,
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: 9999,
                  background: `${STATUS_COLOR[agent.status] ?? '#555'}20`,
                  color: STATUS_COLOR[agent.status] ?? '#555',
                  border: `1px solid ${STATUS_COLOR[agent.status] ?? '#555'}40`,
                  textTransform: 'uppercase',
                  flexShrink: 0,
                }}>
                  {agent.status}
                </span>
              </div>

              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
                <span style={{ fontSize: 10, color: '#555', background: '#0a0a0a', padding: '2px 6px', borderRadius: 4 }}>{agent.kind}</span>
                <span style={{ fontSize: 10, color: '#555', background: '#0a0a0a', padding: '2px 6px', borderRadius: 4 }}>{agent.area}</span>
                <span style={{ fontSize: 10, color: RISK_COLOR[agent.risk_level], background: '#0a0a0a', padding: '2px 6px', borderRadius: 4 }}>risk:{agent.risk_level}</span>
              </div>

              {agent.triggers?.length > 0 && (
                <div style={{ fontSize: 11, color: '#555' }}>
                  ⚡ {agent.triggers.join(' · ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </HQLayout>
  );
}

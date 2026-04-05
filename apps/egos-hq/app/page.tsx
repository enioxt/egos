'use client';

import { useEffect, useState } from 'react';
import { HQLayout } from './hq-layout';

type HealthData = {
  timestamp: string;
  services: {
    guard_brasil: { ok: boolean; latency: number | null; calls_today: number; revenue_today_usd: number; mrr_brl: number };
    gateway: { ok: boolean; latency: number | null; data: Record<string, unknown> };
  };
  x_bot: { pending: number; sent_today: number; rejected_today: number };
  knowledge?: { pages: number; avg_quality: number; learnings: number };
  recent_events: Array<{ id: string; source: string; event_type: string; severity: string; created_at: string; payload: Record<string, unknown> }>;
};

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span style={{
      display: 'inline-block',
      width: 8,
      height: 8,
      borderRadius: '50%',
      background: ok ? '#22c55e' : '#ef4444',
      marginRight: 6,
      flexShrink: 0,
    }} />
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: '#111', border: '1px solid #1f1f1f', borderRadius: 10, padding: '1.25rem' }}>
      <div style={{ fontSize: 11, color: '#555', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '0.75rem' }}>{title}</div>
      {children}
    </div>
  );
}

function Metric({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <span style={{ color: '#737373', fontSize: 12 }}>{label}</span>
        <span style={{ color: '#e5e5e5', fontWeight: 700 }}>{value}</span>
      </div>
      {sub && <div style={{ fontSize: 11, color: '#555', textAlign: 'right' }}>{sub}</div>}
    </div>
  );
}

const SEV_COLOR: Record<string, string> = { info: '#3b82f6', warning: '#f59e0b', error: '#ef4444', critical: '#dc2626' };

export default function HomePage() {
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState('');

  async function load() {
    try {
      const res = await fetch('/api/hq/health');
      if (res.ok) {
        const d = await res.json();
        setData(d);
        setLastUpdated(new Date().toLocaleTimeString('pt-BR'));
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const iv = setInterval(load, 30000); // refresh every 30s
    return () => clearInterval(iv);
  }, []);

  const pending = data?.x_bot.pending ?? 0;

  return (
    <HQLayout pendingCount={pending}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#e5e5e5', margin: 0 }}>Mission Control</h1>
          <div style={{ fontSize: 12, color: '#555', marginTop: 4 }}>
            {loading ? 'Carregando...' : `Atualizado às ${lastUpdated} · Auto-refresh 30s`}
          </div>
        </div>
        <button onClick={load} style={{ padding: '0.4rem 1rem', background: 'transparent', border: '1px solid #1f1f1f', borderRadius: 6, color: '#737373', fontSize: 12, cursor: 'pointer', fontFamily: 'inherit' }}>
          ↻ Refresh
        </button>
      </div>

      {loading ? (
        <div style={{ color: '#555', fontSize: 14 }}>Conectando aos serviços...</div>
      ) : (
        <>
          {/* Health Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>

            {/* Guard Brasil */}
            <Card title="Guard Brasil API">
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                <StatusDot ok={data?.services.guard_brasil.ok ?? false} />
                <span style={{ color: data?.services.guard_brasil.ok ? '#22c55e' : '#ef4444', fontWeight: 700 }}>
                  {data?.services.guard_brasil.ok ? 'Online' : 'Offline'}
                </span>
                {data?.services.guard_brasil.latency && (
                  <span style={{ marginLeft: 'auto', color: '#555', fontSize: 12 }}>{data.services.guard_brasil.latency}ms</span>
                )}
              </div>
              <Metric label="Chamadas hoje" value={data?.services.guard_brasil.calls_today ?? 0} />
              <Metric label="Receita hoje" value={`$${(data?.services.guard_brasil.revenue_today_usd ?? 0).toFixed(4)}`} />
              <Metric label="MRR ativo" value={`R$ ${(data?.services.guard_brasil.mrr_brl ?? 0).toFixed(0)}`} />
            </Card>

            {/* EGOS Gateway */}
            <Card title="EGOS Gateway">
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                <StatusDot ok={data?.services.gateway.ok ?? false} />
                <span style={{ color: data?.services.gateway.ok ? '#22c55e' : '#ef4444', fontWeight: 700 }}>
                  {data?.services.gateway.ok ? 'Online' : 'Offline'}
                </span>
                {data?.services.gateway.latency && (
                  <span style={{ marginLeft: 'auto', color: '#555', fontSize: 12 }}>{data.services.gateway.latency}ms</span>
                )}
              </div>
              <div style={{ fontSize: 12, color: '#737373' }}>
                {data?.services.gateway.ok
                  ? 'Gateway v0.1.0 — WhatsApp · Telegram · Knowledge'
                  : 'gateway.egos.ia.br não está respondendo'}
              </div>
            </Card>

            {/* X Bot */}
            <Card title="X.com Bot">
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                <StatusDot ok={(data?.x_bot.pending ?? 0) >= 0} />
                <span style={{ color: '#22c55e', fontWeight: 700 }}>Ativo · Cron horário</span>
              </div>
              <Metric label="Pendentes" value={pending} />
              <Metric label="Enviados hoje" value={data?.x_bot.sent_today ?? 0} />
              <Metric label="Rejeitados hoje" value={data?.x_bot.rejected_today ?? 0} />
              {pending > 0 && (
                <a href="/x" style={{ display: 'block', marginTop: 10, padding: '0.4rem', background: '#0f1f0f', border: '1px solid #22c55e', borderRadius: 6, color: '#22c55e', fontSize: 12, textAlign: 'center', textDecoration: 'none' }}>
                  → Ver fila ({pending} pendentes)
                </a>
              )}
            </Card>

            {/* Agentes */}
            <Card title="Agentes">
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                <StatusDot ok={true} />
                <span style={{ color: '#22c55e', fontWeight: 700 }}>Registry v2.1.0</span>
              </div>
              <Metric label="Agentes registrados" value="17" />
              <Metric label="Ativos" value="15" />
              <Metric label="Dead/Desativados" value="2" />
              <a href="/agents" style={{ display: 'block', marginTop: 10, padding: '0.4rem', background: '#111', border: '1px solid #1f1f1f', borderRadius: 6, color: '#737373', fontSize: 12, textAlign: 'center', textDecoration: 'none' }}>
                → Ver todos os agentes
              </a>
            </Card>

            {data?.knowledge && (
              <Card title="Knowledge Base">
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
                  <StatusDot ok={(data.knowledge.avg_quality ?? 0) >= 60} />
                  <span style={{ color: (data.knowledge.avg_quality ?? 0) >= 60 ? '#22c55e' : '#f59e0b', fontWeight: 700 }}>
                    {data.knowledge.avg_quality >= 60 ? 'Saudavel' : 'Atencao — qualidade baixa'}
                  </span>
                </div>
                <Metric label="Wiki pages" value={data.knowledge.pages} />
                <Metric label="Qualidade media" value={String(data.knowledge.avg_quality) + '/100'} />
                <Metric label="Learnings" value={data.knowledge.learnings} />
                <a href="/knowledge" style={{ display: 'block', marginTop: 10, padding: '0.4rem', background: '#111', border: '1px solid #1f1f1f', borderRadius: 6, color: '#737373', fontSize: 12, textAlign: 'center', textDecoration: 'none' }}>
                  {'→'} Abrir Knowledge Base
                </a>
              </Card>
            )}

          </div>

          {/* Recent Events */}
          <Card title={`Eventos Recentes (${data?.recent_events.length ?? 0})`}>
            {(data?.recent_events.length ?? 0) === 0 ? (
              <div style={{ color: '#555', fontSize: 13 }}>Nenhum evento registrado. Quando agentes rodarem, aparecerão aqui.</div>
            ) : (
              <div>
                {data?.recent_events.map(ev => (
                  <div key={ev.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '0.5rem 0', borderBottom: '1px solid #1a1a1a' }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: SEV_COLOR[ev.severity] ?? '#555', flexShrink: 0 }} />
                    <span style={{ color: '#22c55e', fontSize: 12, minWidth: 120 }}>{ev.source}</span>
                    <span style={{ color: '#e5e5e5', fontSize: 12, flex: 1 }}>{ev.event_type}</span>
                    <span style={{ color: '#555', fontSize: 11 }}>{new Date(ev.created_at).toLocaleTimeString('pt-BR')}</span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </HQLayout>
  );
}

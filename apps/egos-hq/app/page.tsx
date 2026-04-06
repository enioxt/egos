'use client';

import { useEffect, useState, useCallback } from 'react';
import { HQLayout } from './hq-layout';

// ── Types ────────────────────────────────────────────────────────────────────

type QuotaInfo = {
  requests_in_window: number;
  requests_window_max: number;
  usage_pct: number;
  status: 'ok' | 'warning' | 'exhausted';
  window_resets_in_minutes: number;
  requests_total: number;
  last_request_at: string | null;
  rate_limited_count: number;
};

type ServiceBase = { label: string; ok: boolean; latency: number | null; status: number };

type HealthData = {
  timestamp: string;
  services: {
    guard_brasil: ServiceBase & { calls_today: number; revenue_today_usd: number; mrr_brl: number };
    gateway: ServiceBase & { channels: string[]; uptime_seconds: number | null; data: Record<string, unknown> };
    openclaw: ServiceBase & { default_model: string; fallback_chain: string[]; data: Record<string, unknown> };
    billing_proxy: ServiceBase & { requests_served: number | null; token_expires_in_hours: number | null };
    codex_proxy: ServiceBase & { model: string; quota: QuotaInfo | null; last_review: Record<string, unknown> | null };
  };
  x_bot: { pending: number; sent_today: number; rejected_today: number };
  knowledge: { pages: number; avg_quality: number; learnings: number };
  recent_events: Array<{ id: string; source: string; event_type: string; severity: string; created_at: string; payload: Record<string, unknown> }>;
};

type GTMData = {
  revenue: { mrr_brl: number; formatted: string };
  customers: { count: number; active: number };
  outreach: { last_sent_days_ago: number; total_this_week: number; stale: boolean };
  activity: { has_recent: boolean; last_event_at: string | null; events_this_week: number };
  timestamp: string;
};

// ── Design tokens ─────────────────────────────────────────────────────────────

const C = {
  bg: '#0a0a0a',
  card: '#111',
  border: '#1f1f1f',
  borderHover: '#333',
  text: '#e5e5e5',
  muted: '#737373',
  dim: '#555',
  green: '#22c55e',
  yellow: '#f59e0b',
  red: '#ef4444',
  blue: '#3b82f6',
  purple: '#a855f7',
  orange: '#f97316',
} as const;

const SEV_COLOR: Record<string, string> = {
  info: C.blue, warning: C.yellow, error: C.red, critical: '#dc2626',
};

// ── Primitive components ──────────────────────────────────────────────────────

function Dot({ ok, color }: { ok?: boolean; color?: string }) {
  const bg = color ?? (ok ? C.green : C.red);
  return <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: bg, marginRight: 6, flexShrink: 0 }} />;
}

function Tag({ children, color = C.muted }: { children: React.ReactNode; color?: string }) {
  return (
    <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, border: `1px solid ${color}33`, color, fontFamily: 'monospace' }}>
      {children}
    </span>
  );
}

function Btn({ children, onClick, variant = 'ghost', small }: { children: React.ReactNode; onClick?: () => void; variant?: 'ghost' | 'primary' | 'danger'; small?: boolean }) {
  const styles: Record<string, React.CSSProperties> = {
    ghost: { background: 'transparent', border: `1px solid ${C.border}`, color: C.muted },
    primary: { background: '#0f2f0f', border: `1px solid ${C.green}`, color: C.green },
    danger: { background: '#2f0f0f', border: `1px solid ${C.red}`, color: C.red },
  };
  return (
    <button onClick={onClick} style={{
      ...styles[variant],
      padding: small ? '2px 8px' : '0.35rem 0.85rem',
      borderRadius: 6,
      fontSize: small ? 11 : 12,
      cursor: 'pointer',
      fontFamily: 'inherit',
      transition: 'opacity 0.15s',
    }}>
      {children}
    </button>
  );
}

function QuotaBar({ pct, status }: { pct: number; status: string }) {
  const color = status === 'exhausted' ? C.red : status === 'warning' ? C.yellow : C.green;
  return (
    <div style={{ marginTop: 4 }}>
      <div style={{ height: 4, background: C.border, borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${Math.min(pct, 100)}%`, background: color, transition: 'width 0.4s' }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: C.dim, marginTop: 2 }}>
        <span>{pct}% usado</span>
        <span style={{ color }}>{status.toUpperCase()}</span>
      </div>
    </div>
  );
}

// ── Collapsible Card ──────────────────────────────────────────────────────────

function Card({
  title, status, latency, defaultOpen = true, actions, children, accent,
}: {
  title: string;
  status?: 'ok' | 'warn' | 'error' | 'offline';
  latency?: number | null;
  defaultOpen?: boolean;
  actions?: React.ReactNode;
  children: React.ReactNode;
  accent?: string;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const statusColors: Record<string, string> = { ok: C.green, warn: C.yellow, error: C.red, offline: C.red };
  const dotColor = status ? statusColors[status] : undefined;

  return (
    <div style={{
      background: C.card,
      border: `1px solid ${accent ? accent + '44' : C.border}`,
      borderRadius: 10,
      overflow: 'hidden',
      transition: 'border-color 0.2s',
    }}>
      {/* Header — always visible, clickable */}
      <div
        onClick={() => setOpen(o => !o)}
        style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '0.85rem 1.1rem',
          cursor: 'pointer',
          userSelect: 'none',
          borderBottom: open ? `1px solid ${C.border}` : 'none',
        }}
      >
        {dotColor && <Dot color={dotColor} />}
        <span style={{ fontSize: 12, color: C.muted, textTransform: 'uppercase', letterSpacing: '0.1em', flex: 1 }}>{title}</span>
        {latency != null && <span style={{ fontSize: 11, color: C.dim }}>{latency}ms</span>}
        {actions && <div onClick={e => e.stopPropagation()} style={{ display: 'flex', gap: 6 }}>{actions}</div>}
        <span style={{ fontSize: 12, color: C.dim, marginLeft: 4 }}>{open ? '▲' : '▼'}</span>
      </div>

      {/* Body — collapsible */}
      {open && (
        <div style={{ padding: '1rem 1.1rem' }}>
          {children}
        </div>
      )}
    </div>
  );
}

function Row({ label, value, sub, mono }: { label: string; value: React.ReactNode; sub?: string; mono?: boolean }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
        <span style={{ color: C.muted, fontSize: 12, flexShrink: 0 }}>{label}</span>
        <span style={{ color: C.text, fontWeight: 600, fontSize: 13, fontFamily: mono ? 'monospace' : 'inherit', textAlign: 'right' }}>{value}</span>
      </div>
      {sub && <div style={{ fontSize: 11, color: C.dim, textAlign: 'right' }}>{sub}</div>}
    </div>
  );
}

function LinkBtn({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a href={href} style={{
      display: 'block', marginTop: 10,
      padding: '0.4rem', background: C.bg,
      border: `1px solid ${C.border}`, borderRadius: 6,
      color: C.muted, fontSize: 12, textAlign: 'center', textDecoration: 'none',
    }}>
      {children}
    </a>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [data, setData] = useState<HealthData | null>(null);
  const [gtmData, setGtmData] = useState<GTMData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState('');
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [healthRes, gtmRes] = await Promise.all([
        fetch('/api/hq/health'),
        fetch('/api/hq/gtm'),
      ]);
      if (healthRes.ok) {
        setData(await healthRes.json());
      }
      if (gtmRes.ok) {
        setGtmData(await gtmRes.json());
      }
      setLastUpdated(new Date().toLocaleTimeString('pt-BR'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const iv = setInterval(load, 30000);
    return () => clearInterval(iv);
  }, [load]);

  function notify(msg: string) {
    setActionMsg(msg);
    setTimeout(() => setActionMsg(null), 4000);
  }

  async function triggerAction(label: string, url: string) {
    notify(`⏳ ${label}...`);
    try {
      const r = await fetch(url, { method: 'POST' });
      notify(r.ok ? `✅ ${label} OK` : `❌ ${label} falhou (${r.status})`);
    } catch (e) {
      notify(`❌ ${label} — erro de rede`);
    }
  }

  const svc = data?.services;
  const pending = data?.x_bot.pending ?? 0;

  const guardStatus = svc?.guard_brasil.ok ? 'ok' : 'offline';
  const gatewayStatus = svc?.gateway.ok ? 'ok' : 'offline';
  const openclawStatus = svc?.openclaw.ok ? 'ok' : 'offline';
  const billingStatus = svc?.billing_proxy.ok ? 'ok' : 'offline';
  const codexStatus = svc?.codex_proxy.ok
    ? (svc.codex_proxy.quota?.status === 'exhausted' ? 'error' : svc.codex_proxy.quota?.status === 'warning' ? 'warn' : 'ok')
    : 'offline';

  return (
    <HQLayout pendingCount={pending}>

      {/* Toast notification */}
      {actionMsg && (
        <div style={{
          position: 'fixed', top: 16, right: 16, zIndex: 9999,
          padding: '0.6rem 1rem', background: '#1a1a1a',
          border: `1px solid ${C.border}`, borderRadius: 8,
          fontSize: 13, color: C.text, boxShadow: '0 4px 20px #0006',
        }}>
          {actionMsg}
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: C.text, margin: 0 }}>Mission Control</h1>
          <div style={{ fontSize: 12, color: C.dim, marginTop: 4 }}>
            {loading ? 'Conectando...' : `↻ ${lastUpdated} · auto-refresh 30s`}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Btn onClick={load}>↻ Refresh</Btn>
          <Btn onClick={() => window.open('/agents', '_blank')}>Agentes →</Btn>
        </div>
      </div>

      {loading ? (
        <div style={{ color: C.dim, fontSize: 14 }}>Conectando aos serviços...</div>
      ) : (
        <>
          {/* ── Services Grid ─────────────────────────────────── */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>

            {/* Guard Brasil */}
            <Card
              title="Guard Brasil API"
              status={guardStatus}
              latency={svc?.guard_brasil.latency}
              accent={C.green}
              actions={
                <>
                  <Btn small onClick={() => window.open('https://guard.egos.ia.br/health', '_blank')}>⬡ Health</Btn>
                  <Btn small onClick={() => window.open('https://guard.egos.ia.br/v1/meta', '_blank')}>Meta</Btn>
                </>
              }
            >
              <Row label="Status" value={<span style={{ color: svc?.guard_brasil.ok ? C.green : C.red }}>{svc?.guard_brasil.ok ? 'Online' : 'Offline'}</span>} />
              <Row label="Chamadas hoje" value={svc?.guard_brasil.calls_today ?? 0} />
              <Row label="Receita hoje" value={`$${(svc?.guard_brasil.revenue_today_usd ?? 0).toFixed(4)}`} />
              <Row label="MRR ativo" value={`R$ ${(svc?.guard_brasil.mrr_brl ?? 0).toFixed(0)}`} />
              <div style={{ marginTop: 10, display: 'flex', gap: 6 }}>
                <Btn small variant="primary" onClick={() => window.open('https://guard.egos.ia.br', '_blank')}>→ Docs</Btn>
                <Btn small onClick={() => window.open('/api/hq/health', '_blank')}>JSON</Btn>
              </div>
            </Card>

            {/* EGOS Gateway */}
            <Card
              title="EGOS Gateway"
              status={gatewayStatus}
              latency={svc?.gateway.latency}
              actions={<Btn small onClick={() => window.open('https://gateway.egos.ia.br/health', '_blank')}>⬡ Health</Btn>}
            >
              <Row label="Status" value={<span style={{ color: svc?.gateway.ok ? C.green : C.red }}>{svc?.gateway.ok ? 'Online' : 'Offline'}</span>} />
              <Row label="Uptime" value={svc?.gateway.uptime_seconds ? `${Math.round((svc.gateway.uptime_seconds ?? 0) / 3600)}h` : '—'} />
              <Row label="Canais" value={
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                  {(svc?.gateway.channels ?? []).map(ch => <Tag key={ch} color={C.blue}>{ch}</Tag>)}
                </div>
              } />
              <LinkBtn href="https://gateway.egos.ia.br/ui">→ Gateway UI</LinkBtn>
            </Card>

            {/* OpenClaw */}
            <Card
              title="OpenClaw (Claude)"
              status={openclawStatus}
              latency={svc?.openclaw.latency}
              accent={C.purple}
              actions={<Btn small onClick={() => window.open('http://127.0.0.1:18789', '_blank')}>WebUI</Btn>}
            >
              <Row label="Status" value={<span style={{ color: svc?.openclaw.ok ? C.green : C.red }}>{svc?.openclaw.ok ? 'Online' : 'Offline'}</span>} />
              <Row label="Modelo padrão" value={<Tag color={C.purple}>{svc?.openclaw.default_model ?? '—'}</Tag>} mono />
              <div style={{ marginTop: 8 }}>
                <div style={{ fontSize: 11, color: C.dim, marginBottom: 4 }}>Fallback chain</div>
                {(svc?.openclaw.fallback_chain ?? []).map((m, i) => (
                  <div key={m} style={{ fontSize: 11, color: C.muted, padding: '2px 0' }}>
                    <span style={{ color: C.dim, marginRight: 6 }}>{i + 1}.</span>{m}
                  </div>
                ))}
              </div>
            </Card>

            {/* Billing Proxy (Claude) */}
            <Card
              title="Billing Proxy · Claude"
              status={billingStatus}
              latency={svc?.billing_proxy.latency}
            >
              <Row label="Status" value={<span style={{ color: svc?.billing_proxy.ok ? C.green : C.red }}>{svc?.billing_proxy.ok ? 'Online' : 'Offline'}</span>} />
              <Row label="Requisições servidas" value={svc?.billing_proxy.requests_served ?? '—'} />
              <Row label="Token expira em" value={
                svc?.billing_proxy.token_expires_in_hours != null
                  ? `${svc.billing_proxy.token_expires_in_hours.toFixed(1)}h`
                  : '—'
              } />
              <Row label="Porta" value={<Tag color={C.muted}>:18801</Tag>} />
              <div style={{ marginTop: 10 }}>
                <Btn small onClick={() => triggerAction('Token refresh', '/api/hq/actions/billing-refresh')}>
                  ↻ Refresh token
                </Btn>
              </div>
            </Card>

            {/* Codex Proxy (GPT) */}
            <Card
              title="Codex Proxy · GPT-5.4"
              status={codexStatus}
              latency={svc?.codex_proxy.latency}
              accent={C.orange}
              actions={<Btn small onClick={() => window.open('http://127.0.0.1:18802/v1/usage', '_blank')}>Quota</Btn>}
            >
              <Row label="Status" value={<span style={{ color: svc?.codex_proxy.ok ? C.green : C.red }}>{svc?.codex_proxy.ok ? 'Online' : 'Offline'}</span>} />
              <Row label="Modelo" value={<Tag color={C.orange}>{svc?.codex_proxy.model ?? 'gpt-5.4'}</Tag>} />
              {svc?.codex_proxy.quota && (
                <>
                  <Row
                    label="Quota (5h janela)"
                    value={`${svc.codex_proxy.quota.requests_in_window} / ${svc.codex_proxy.quota.requests_window_max}`}
                  />
                  <QuotaBar
                    pct={svc.codex_proxy.quota.usage_pct}
                    status={svc.codex_proxy.quota.status}
                  />
                  <Row label="Reset em" value={`${svc.codex_proxy.quota.window_resets_in_minutes}min`} />
                  <Row label="Total de requisições" value={svc.codex_proxy.quota.requests_total} />
                  {svc.codex_proxy.quota.last_request_at && (
                    <Row label="Última requisição" value={new Date(svc.codex_proxy.quota.last_request_at).toLocaleTimeString('pt-BR')} />
                  )}
                </>
              )}
              {svc?.codex_proxy.last_review && (
                <div style={{ marginTop: 10, padding: '8px', background: '#0a0a0a', borderRadius: 6, fontSize: 11, color: C.muted }}>
                  <div style={{ color: C.dim, marginBottom: 4 }}>Última review constitucional</div>
                  <div>{new Date((svc.codex_proxy.last_review as { created_at: string }).created_at).toLocaleString('pt-BR')}</div>
                </div>
              )}
              <div style={{ marginTop: 10, display: 'flex', gap: 6 }}>
                <Btn small variant="primary" onClick={() => triggerAction('Constitutional Review', '/api/hq/actions/codex-review')}>
                  ▶ Rodar Review
                </Btn>
              </div>
            </Card>

            {/* Knowledge Base */}
            {data?.knowledge && (
              <Card title="Knowledge Base" status={(data.knowledge.avg_quality ?? 0) >= 60 ? 'ok' : 'warn'}>
                <Row label="Wiki pages" value={data.knowledge.pages} />
                <Row label="Qualidade média" value={`${data.knowledge.avg_quality}/100`} />
                <Row label="Learnings" value={data.knowledge.learnings} />
                <LinkBtn href="/knowledge">→ Abrir Knowledge Base</LinkBtn>
              </Card>
            )}

          </div>

          {/* ── X Bot + GTM ───────────────────────────────────── */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
            <Card
              title="X.com Bot"
              status={pending > 0 ? 'warn' : 'ok'}
              defaultOpen={pending > 0}
              actions={<Btn small onClick={() => window.open('/x', '_blank')}>Fila →</Btn>}
            >
              <Row label="Pendentes" value={pending} />
              <Row label="Enviados hoje" value={data?.x_bot.sent_today ?? 0} />
              <Row label="Rejeitados hoje" value={data?.x_bot.rejected_today ?? 0} />
              {pending > 0 && (
                <div style={{ marginTop: 10 }}>
                  <Btn variant="primary" small onClick={() => window.open('/x', '_blank')}>→ Aprovar {pending} replies</Btn>
                </div>
              )}
            </Card>

            <Card title="GTM" defaultOpen={false}>
              <Row label="Revenue" value={gtmData?.revenue?.formatted ?? 'R$ 0 MRR'} />
              <Row label="Customers" value={gtmData?.customers?.count ?? 0} />
              <Row label="M-007 outreach" value={
                gtmData?.outreach?.stale
                  ? <span style={{ color: C.red }}>⚠ {gtmData.outreach.last_sent_days_ago}+ days stale</span>
                  : <span style={{ color: C.green }}>✓ {gtmData?.outreach?.last_sent_days_ago ?? 0} days ago</span>
              } />
              <div style={{ marginTop: 10, display: 'flex', gap: 6 }}>
                <Btn small variant="primary" onClick={() => window.open('/docs/GTM_SSOT.md', '_blank')}>→ GTM SSOT</Btn>
                <Btn small onClick={() => window.open('/x', '_blank')}>→ X posts</Btn>
              </div>
            </Card>
          </div>

          {/* ── Recent Events ─────────────────────────────────── */}
          <Card
            title={`Eventos Recentes (${data?.recent_events.length ?? 0})`}
            defaultOpen={(data?.recent_events.length ?? 0) > 0}
            actions={<Btn small onClick={() => window.open('/events', '_blank')}>Ver todos →</Btn>}
          >
            {(data?.recent_events.length ?? 0) === 0 ? (
              <div style={{ color: C.dim, fontSize: 13 }}>Nenhum evento. Quando agentes rodarem, aparecerão aqui.</div>
            ) : (
              <div>
                {data?.recent_events.map(ev => (
                  <details key={ev.id} style={{ borderBottom: `1px solid ${C.border}` }}>
                    <summary style={{
                      display: 'flex', alignItems: 'center', gap: 10,
                      padding: '0.5rem 0', cursor: 'pointer', listStyle: 'none',
                    }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: SEV_COLOR[ev.severity] ?? C.dim, flexShrink: 0, display: 'inline-block' }} />
                      <span style={{ color: C.green, fontSize: 12, minWidth: 120 }}>{ev.source}</span>
                      <span style={{ color: C.text, fontSize: 12, flex: 1 }}>{ev.event_type}</span>
                      <span style={{ color: C.dim, fontSize: 11 }}>{new Date(ev.created_at).toLocaleTimeString('pt-BR')}</span>
                    </summary>
                    <pre style={{ margin: '0 0 8px 16px', fontSize: 11, color: C.muted, whiteSpace: 'pre-wrap', wordBreak: 'break-word', background: C.bg, padding: '8px', borderRadius: 6 }}>
                      {JSON.stringify(ev.payload, null, 2)}
                    </pre>
                  </details>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </HQLayout>
  );
}

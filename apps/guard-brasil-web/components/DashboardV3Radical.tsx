/**
 * DASHBOARD V3 — REVOLUCIONÁRIA (Radical Transparency Canvas)
 *
 * Conceito: O dashboard É o produto. Não é uma tela que mostra dados —
 * é uma tela que PROVA que seus dados estão seguros, em tempo real,
 * de uma forma que nunca existiu antes.
 *
 * Inspiração: Um "raio-X" vivo dos seus dados passando pelo Guard Brasil.
 * Como um scanner de aeroporto: você VÊ seus dados entrando,
 * sendo processados, e saindo limpos.
 *
 * Diferencial: Visualização de fluxo contínuo. Não lista de eventos.
 * Os dados FLUEM pela tela como um rio. Cada pacote é uma bolha
 * que entra pela esquerda (raw data), passa pelo centro (processing),
 * e sai pela direita (clean/blocked).
 *
 * Ninguém faz isso. Grepture tem uma lista. Protecto tem um painel.
 * Nós temos um SCANNER VIVO.
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

// ── Types ──────────────────────────────────────────────────

interface DataPacket {
  id: string;
  text_preview: string;       // Primeiras 30 chars do input
  pii_found: string[];        // ['cpf', 'rg']
  atrian_score: number;       // 0-100
  cost_usd: number;
  duration_ms: number;
  model_used: string;
  verdict: 'clean' | 'masked' | 'blocked';
  phase: 'entering' | 'scanning' | 'processed';
  x: number;                  // Position 0-100 (left to right)
  y: number;                  // Vertical position
}

interface StreamStats {
  total_processed: number;
  total_blocked: number;
  total_cost: number;
  avg_latency: number;
  pii_breakdown: Record<string, number>;
  current_throughput: number;  // packets per second
}

// ── Packet Generator ───────────────────────────────────────

function generatePacket(): DataPacket {
  const samples = [
    { text: 'CPF: 123.456.789-00...', pii: ['cpf'], verdict: 'masked' as const },
    { text: 'SELECT * FROM users...', pii: [], verdict: 'clean' as const },
    { text: 'RG 1234567 paciente...', pii: ['rg'], verdict: 'masked' as const },
    { text: 'Placa ABC-1234 no...', pii: ['placa'], verdict: 'masked' as const },
    { text: 'Jovem negro empres...', pii: [], verdict: 'blocked' as const },
    { text: 'Email: joao@gov.br...', pii: ['email'], verdict: 'masked' as const },
    { text: 'MASP 12345678 del...', pii: ['masp'], verdict: 'masked' as const },
    { text: 'Relatório mensal d...', pii: [], verdict: 'clean' as const },
    { text: 'PIX b74c886c-020f...', pii: ['pix_key'], verdict: 'masked' as const },
    { text: 'Processo 1234567-...', pii: ['processo'], verdict: 'masked' as const },
  ];
  const sample = samples[Math.floor(Math.random() * samples.length)];
  const isLLM = sample.pii.length > 0 && Math.random() > 0.5;

  return {
    id: Math.random().toString(36).slice(2, 10),
    text_preview: sample.text,
    pii_found: sample.pii,
    atrian_score: sample.verdict === 'blocked' ? Math.floor(Math.random() * 40) + 10 : Math.floor(Math.random() * 20) + 80,
    cost_usd: isLLM ? 0.00007 : 0,
    duration_ms: isLLM ? Math.floor(Math.random() * 150) + 50 : Math.floor(Math.random() * 5) + 1,
    model_used: isLLM ? 'qwen-plus' : 'regex',
    verdict: sample.verdict,
    phase: 'entering',
    x: 0,
    y: Math.random() * 80 + 10,
  };
}

// ── Main Component ─────────────────────────────────────────

export default function DashboardV3Radical() {
  const [packets, setPackets] = useState<DataPacket[]>([]);
  const [stats, setStats] = useState<StreamStats>({
    total_processed: 0,
    total_blocked: 0,
    total_cost: 0,
    avg_latency: 0,
    pii_breakdown: {},
    current_throughput: 0,
  });
  const [isPaused, setIsPaused] = useState(false);
  const [selectedPacket, setSelectedPacket] = useState<DataPacket | null>(null);
  const animationRef = useRef<number>(0);

  // Generate new packets periodically
  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      const newPacket = generatePacket();
      setPackets((prev) => [...prev, newPacket].slice(-30));
      setStats((prev) => ({
        total_processed: prev.total_processed + 1,
        total_blocked: prev.total_blocked + (newPacket.verdict === 'blocked' ? 1 : 0),
        total_cost: prev.total_cost + newPacket.cost_usd,
        avg_latency: Math.round((prev.avg_latency * prev.total_processed + newPacket.duration_ms) / (prev.total_processed + 1)),
        pii_breakdown: newPacket.pii_found.reduce((acc, pii) => ({
          ...acc,
          [pii]: (prev.pii_breakdown[pii] || 0) + 1,
        }), { ...prev.pii_breakdown }),
        current_throughput: prev.total_processed / ((Date.now() - animationRef.current) / 1000) || 0,
      }));
    }, 2000 + Math.random() * 3000);
    return () => clearInterval(interval);
  }, [isPaused]);

  // Animate packets moving across the screen
  useEffect(() => {
    if (!animationRef.current) animationRef.current = Date.now();
    const animate = () => {
      setPackets((prev) =>
        prev
          .map((p) => ({
            ...p,
            x: Math.min(100, p.x + 0.5),
            phase: p.x < 30 ? 'entering' as const : p.x < 70 ? 'scanning' as const : 'processed' as const,
          }))
          .filter((p) => p.x < 100)
      );
      requestAnimationFrame(animate);
    };
    const raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, []);

  const verdictColor = useCallback((v: string) => {
    if (v === 'clean') return 'border-emerald-500 bg-emerald-500/10';
    if (v === 'masked') return 'border-blue-500 bg-blue-500/10';
    return 'border-red-500 bg-red-500/10';
  }, []);

  const phaseLabel = useCallback((x: number) => {
    if (x < 30) return 'ENTERING';
    if (x < 70) return 'SCANNING';
    return 'PROCESSED';
  }, []);

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden select-none">
      {/* Top Bar — Minimal */}
      <div className="absolute top-0 left-0 right-0 z-20 bg-black/80 backdrop-blur border-b border-slate-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-bold tracking-wider">GUARD BRASIL</h1>
          <span className="text-[10px] text-slate-500 tracking-widest uppercase">Radical Transparency Scanner</span>
        </div>
        <div className="flex items-center gap-6">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`text-xs px-3 py-1 rounded border ${isPaused ? 'border-emerald-500 text-emerald-400' : 'border-slate-700 text-slate-400'}`}
          >
            {isPaused ? '▶ Resume' : '⏸ Pause'}
          </button>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isPaused ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'}`} />
            <span className="text-xs text-slate-400">{isPaused ? 'Paused' : 'Live'}</span>
          </div>
        </div>
      </div>

      {/* Main Canvas — The Scanner */}
      <div className="relative w-full h-screen pt-14">
        {/* Zone labels */}
        <div className="absolute top-16 left-0 right-0 flex z-10 pointer-events-none">
          <div className="w-[30%] text-center">
            <span className="text-[10px] text-slate-600 tracking-[0.3em] uppercase">Input</span>
          </div>
          <div className="w-[40%] text-center">
            <span className="text-[10px] text-emerald-800 tracking-[0.3em] uppercase">Guard Processing</span>
          </div>
          <div className="w-[30%] text-center">
            <span className="text-[10px] text-slate-600 tracking-[0.3em] uppercase">Output</span>
          </div>
        </div>

        {/* Zone dividers */}
        <div className="absolute top-14 bottom-0 left-[30%] w-px bg-gradient-to-b from-emerald-900/50 via-emerald-600/20 to-transparent z-10" />
        <div className="absolute top-14 bottom-0 left-[70%] w-px bg-gradient-to-b from-emerald-900/50 via-emerald-600/20 to-transparent z-10" />

        {/* Processing zone glow */}
        <div className="absolute top-14 bottom-0 left-[30%] w-[40%] bg-gradient-to-b from-emerald-950/30 via-emerald-950/10 to-transparent z-0" />

        {/* Packets flowing */}
        {packets.map((packet) => (
          <div
            key={packet.id}
            onClick={() => setSelectedPacket(packet)}
            className={`absolute z-10 cursor-pointer transition-all duration-300 ${verdictColor(packet.verdict)} border rounded-lg px-3 py-2 hover:scale-110`}
            style={{
              left: `${packet.x}%`,
              top: `${packet.y}%`,
              opacity: packet.x > 90 ? (100 - packet.x) / 10 : packet.x < 5 ? packet.x / 5 : 1,
              transform: `translateX(-50%) scale(${packet.phase === 'scanning' ? 1.05 : 1})`,
            }}
          >
            <p className="text-[10px] font-mono text-slate-300 whitespace-nowrap max-w-[120px] truncate">
              {packet.text_preview}
            </p>
            <div className="flex items-center gap-1 mt-1">
              {packet.pii_found.map((pii) => (
                <span key={pii} className="text-[8px] bg-white/10 px-1 rounded">{pii}</span>
              ))}
              {packet.verdict === 'blocked' && (
                <span className="text-[8px] bg-red-500/30 text-red-300 px-1 rounded">BLOCKED</span>
              )}
            </div>
          </div>
        ))}

        {/* Bottom Stats Bar */}
        <div className="absolute bottom-0 left-0 right-0 z-20 bg-black/90 backdrop-blur border-t border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <div className="text-center">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Processed</p>
              <p className="text-xl font-bold font-mono">{stats.total_processed}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Blocked</p>
              <p className="text-xl font-bold font-mono text-red-400">{stats.total_blocked}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Total Cost</p>
              <p className="text-xl font-bold font-mono text-amber-400">${stats.total_cost.toFixed(5)}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">Avg Latency</p>
              <p className="text-xl font-bold font-mono text-blue-400">{stats.avg_latency}ms</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] text-slate-500 uppercase tracking-wider">PII Types</p>
              <div className="flex gap-1 mt-1">
                {Object.entries(stats.pii_breakdown)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 4)
                  .map(([type, count]) => (
                    <span key={type} className="text-[9px] bg-blue-900/50 text-blue-300 px-1.5 py-0.5 rounded">
                      {type}: {count}
                    </span>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Packet Detail Panel (click to inspect) */}
      {selectedPacket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm" onClick={() => setSelectedPacket(null)}>
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold">Packet Inspection</h3>
              <button onClick={() => setSelectedPacket(null)} className="text-slate-400 hover:text-white">x</button>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-xs text-slate-500 mb-1">Input Preview</p>
                <p className="text-sm font-mono bg-slate-800 rounded p-3">{selectedPacket.text_preview}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Verdict</p>
                  <span className={`text-sm font-bold ${
                    selectedPacket.verdict === 'clean' ? 'text-emerald-400' :
                    selectedPacket.verdict === 'masked' ? 'text-blue-400' : 'text-red-400'
                  }`}>
                    {selectedPacket.verdict.toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">ATRiAN Score</p>
                  <span className={`text-sm font-bold ${selectedPacket.atrian_score > 70 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {selectedPacket.atrian_score}/100
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Model Used</p>
                  <p className="text-sm font-mono">{selectedPacket.model_used}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">Cost</p>
                  <p className="text-sm font-mono text-amber-400">
                    {selectedPacket.cost_usd > 0 ? `$${selectedPacket.cost_usd.toFixed(5)}` : 'Free (regex)'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Latency</p>
                  <p className="text-sm font-mono text-blue-400">{selectedPacket.duration_ms}ms</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 mb-1">PII Found</p>
                  <div className="flex gap-1 flex-wrap">
                    {selectedPacket.pii_found.length > 0
                      ? selectedPacket.pii_found.map((p) => (
                          <span key={p} className="text-xs bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded">{p}</span>
                        ))
                      : <span className="text-xs text-slate-400">None</span>}
                  </div>
                </div>
              </div>

              <div className="bg-emerald-900/20 border border-emerald-800/50 rounded-lg p-3 mt-4">
                <p className="text-[10px] text-emerald-400 uppercase tracking-wider mb-1">Transparency Note</p>
                <p className="text-xs text-slate-300">
                  This exact record is stored in your audit trail. You can export it,
                  query it, or delete it. We hide nothing.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

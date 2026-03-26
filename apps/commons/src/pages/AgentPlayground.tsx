import { useState, useEffect } from 'react';
import { Bot, Activity, Clock, Zap } from 'lucide-react';

export function AgentPlayground() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    // In a real app, this would connect to a Server-Sent Events (SSE) or WebSocket endpoint.
    // Simulating Mycelium Event Bus events for demonstration:
    const mockAgents = ['ATRiAN_Guard', 'ETHIK_Tracker', 'Doc_Auditor', 'Code_Reviewer'];
    
    const interval = setInterval(() => {
      setEvents(prev => {
        const newEvent = {
          id: Date.now().toString(),
          agent: mockAgents[Math.floor(Math.random() * mockAgents.length)],
          action: 'Processed task validation',
          cost: (Math.random() * 0.05).toFixed(4),
          time: new Date().toLocaleTimeString()
        };
        return [newEvent, ...prev].slice(0, 10);
      });
    }, 4500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto mt-20">
      <div className="flex items-center gap-3 mb-2">
        <Bot size={32} className="text-cyan-400" />
        <h1 className="text-3xl font-bold text-slate-100">Agent Playground</h1>
      </div>
      <p className="text-slate-400 mb-8">Monitoramento ao vivo do barramento Mycelium (SSE). Veja os agentes do kernel operando em tempo real.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {['ATRiAN_Guard', 'ETHIK_Tracker', 'Doc_Auditor', 'Code_Reviewer'].map((agent) => (
          <div key={agent} className="p-5 bg-slate-900 border border-slate-700/50 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-500"></div>
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-bold text-slate-200">{agent}</h3>
              <div className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Active
              </div>
            </div>
            <div className="text-xs text-slate-400 mb-1">Custo estimado hoje</div>
            <div className="text-lg font-mono text-cyan-300">$ {(Math.random() * 2 + 0.5).toFixed(2)}</div>
          </div>
        ))}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
            <Activity size={18} className="text-cyan-500" /> Live Event Stream
          </h2>
          <span className="text-xs text-slate-500">Aguardando eventos...</span>
        </div>
        <div className="divide-y divide-slate-800">
          {events.length === 0 ? (
            <div className="p-12 text-center text-slate-500 text-sm">Nenhum evento detectado ainda.</div>
          ) : (
            events.map(ev => (
              <div key={ev.id} className="p-4 flex items-center justify-between hover:bg-slate-800/50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                    <Zap size={16} className="text-amber-400" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-300">{ev.agent}</div>
                    <div className="text-xs text-slate-500">{ev.action}</div>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-right">
                  <div>
                    <div className="text-xs text-slate-500 mb-0.5 flex items-center justify-end gap-1"><Clock size={12}/> Time</div>
                    <div className="text-sm font-mono text-slate-300">{ev.time}</div>
                  </div>
                  <div className="w-24">
                    <div className="text-xs text-slate-500 mb-0.5">Cost</div>
                    <div className="text-sm font-mono text-cyan-400">${ev.cost}</div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

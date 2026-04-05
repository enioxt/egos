'use client';

import { useState, useEffect, useCallback } from 'react';

interface Tweet {
  id: string;
  text: string;
  created_at: string;
  url: string;
  author: { name: string; username: string; profile_image_url?: string; public_metrics?: { followers_count: number } };
  metrics: { like_count: number; reply_count: number; retweet_count: number; impression_count?: number };
}

interface SuggestedQuery { q: string; label: string }

const API_BASE = '/api/x';

export default function XDashboard() {
  const [key, setKey] = useState('');
  const [authed, setAuthed] = useState(false);
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('LGPD API -is:retweet lang:pt');
  const [suggestions, setSuggestions] = useState<SuggestedQuery[]>([]);
  const [replyTo, setReplyTo] = useState<Tweet | null>(null);
  const [replyText, setReplyText] = useState('');
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<string | null>(null);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [newTweet, setNewTweet] = useState('');
  const [tab, setTab] = useState<'search' | 'compose' | 'queue'>('search');
  const [queue, setQueue] = useState<{ tweet: Tweet; reply: string; status: 'pending' | 'sent' | 'edited' }[]>([]);

  // Load saved key
  useEffect(() => {
    const saved = localStorage.getItem('x-dash-key');
    if (saved) { setKey(saved); setAuthed(true); }
  }, []);

  // Auth
  const login = useCallback(() => {
    localStorage.setItem('x-dash-key', key);
    setAuthed(true);
    // Load suggestions
    fetch(`${API_BASE}?action=suggestions&key=${key}`)
      .then(r => r.json())
      .then(d => setSuggestions(d.queries ?? []))
      .catch(() => {});
  }, [key]);

  // Search
  const search = useCallback(async (q?: string) => {
    const searchQuery = q ?? query;
    setQuery(searchQuery);
    setLoading(true);
    setTweets([]);
    try {
      const res = await fetch(`${API_BASE}?action=search&q=${encodeURIComponent(searchQuery)}&max=20&key=${key}`);
      const data = await res.json();
      if (data.tweets) setTweets(data.tweets);
      else if (data.error) setPostResult(`Erro: ${data.error}`);
    } catch (e) {
      setPostResult(`Erro de conexão: ${String(e)}`);
    }
    setLoading(false);
  }, [query, key]);

  // Load suggestions on auth
  useEffect(() => {
    if (authed) {
      fetch(`${API_BASE}?action=suggestions&key=${key}`)
        .then(r => r.json())
        .then(d => setSuggestions(d.queries ?? []))
        .catch(() => {});
    }
  }, [authed, key]);

  // Start reply
  const startReply = useCallback(async (tweet: Tweet) => {
    setReplyTo(tweet);
    setReplyText('');
    setAiSuggestions([]);
    setPostResult(null);

    // Get AI suggestions
    try {
      const res = await fetch(`${API_BASE}?key=${key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'suggest', tweet_text: tweet.text }),
      });
      const data = await res.json();
      if (data.suggestions) setAiSuggestions(data.suggestions);
    } catch {}
  }, [key]);

  // Post reply
  const sendReply = useCallback(async () => {
    if (!replyTo || !replyText.trim()) return;
    setPosting(true);
    setPostResult(null);
    try {
      const res = await fetch(`${API_BASE}?key=${key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'reply', tweet_id: replyTo.id, text: replyText }),
      });
      const data = await res.json();
      if (data.success) {
        setPostResult(`✅ Respondido! ${data.tweet_url}`);
        setReplyTo(null);
        setReplyText('');
      } else {
        setPostResult(`❌ Erro: ${data.error ?? data.detail}`);
      }
    } catch (e) {
      setPostResult(`❌ Falha: ${String(e)}`);
    }
    setPosting(false);
  }, [replyTo, replyText, key]);

  // Add to queue instead of posting immediately
  const addToQueue = useCallback(() => {
    if (!replyTo || !replyText.trim()) return;
    setQueue(prev => [...prev, { tweet: replyTo, reply: replyText, status: 'pending' }]);
    setReplyTo(null);
    setReplyText('');
    setPostResult('📋 Adicionado à fila de respostas');
  }, [replyTo, replyText]);

  // Post new tweet
  const postNewTweet = useCallback(async () => {
    if (!newTweet.trim()) return;
    setPosting(true);
    try {
      const res = await fetch(`${API_BASE}?key=${key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'post', text: newTweet }),
      });
      const data = await res.json();
      if (data.success) {
        setPostResult(`✅ Publicado! ${data.tweet_url}`);
        setNewTweet('');
      } else {
        setPostResult(`❌ Erro: ${data.error}`);
      }
    } catch (e) {
      setPostResult(`❌ Falha: ${String(e)}`);
    }
    setPosting(false);
  }, [newTweet, key]);

  // Send queued reply
  const sendQueued = useCallback(async (index: number) => {
    const item = queue[index];
    if (!item || item.status === 'sent') return;

    try {
      const res = await fetch(`${API_BASE}?key=${key}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'reply', tweet_id: item.tweet.id, text: item.reply }),
      });
      const data = await res.json();
      if (data.success) {
        setQueue(prev => prev.map((q, i) => i === index ? { ...q, status: 'sent' as const } : q));
      }
    } catch {}
  }, [queue, key]);

  const timeAgo = (date: string) => {
    const diff = Date.now() - new Date(date).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h`;
    return `${Math.floor(hours / 24)}d`;
  };

  // Login screen
  if (!authed) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
        <div className="w-full max-w-sm space-y-4">
          <h1 className="text-2xl font-bold text-center">🐦 X.com Dashboard</h1>
          <p className="text-sm text-gray-500 text-center">EGOS — Painel de respostas e engajamento</p>
          <input
            type="password"
            placeholder="Dashboard key"
            value={key}
            onChange={e => setKey(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && login()}
            className="w-full bg-gray-900 border border-gray-800 rounded-xl p-3 text-sm"
          />
          <button onClick={login} className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition text-sm">
            Entrar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Mobile-first tabs */}
      <div className="sticky top-0 bg-black/95 backdrop-blur border-b border-gray-800 z-20">
        <div className="flex">
          {([['search', '🔍 Buscar'], ['compose', '✏️ Publicar'], ['queue', `📋 Fila (${queue.filter(q => q.status === 'pending').length})`]] as const).map(([id, label]) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex-1 py-3 text-sm font-medium transition border-b-2 ${
                tab === id ? 'text-blue-400 border-blue-400' : 'text-gray-500 border-transparent'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Status bar */}
      {postResult && (
        <div className={`p-3 text-sm text-center ${postResult.startsWith('✅') || postResult.startsWith('📋') ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          {postResult}
          <button onClick={() => setPostResult(null)} className="ml-2 text-gray-500">✕</button>
        </div>
      )}

      <div className="max-w-lg mx-auto px-3 py-4">

        {/* === SEARCH TAB === */}
        {tab === 'search' && (
          <div className="space-y-4">
            {/* Search bar */}
            <div className="flex gap-2">
              <input
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && search()}
                placeholder="Buscar no X.com..."
                className="flex-1 bg-gray-900 border border-gray-800 rounded-xl px-3 py-2.5 text-sm"
              />
              <button
                onClick={() => search()}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 text-white px-4 rounded-xl text-sm font-medium transition"
              >
                {loading ? '...' : '🔍'}
              </button>
            </div>

            {/* Quick search pills */}
            <div className="flex flex-wrap gap-2">
              {suggestions.slice(0, 6).map(s => (
                <button
                  key={s.q}
                  onClick={() => search(s.q)}
                  className="text-xs px-3 py-1.5 bg-gray-900 border border-gray-800 rounded-full text-gray-400 hover:text-blue-400 hover:border-blue-600/50 transition"
                >
                  {s.label}
                </button>
              ))}
            </div>

            {/* Tweet list */}
            <div className="space-y-3">
              {tweets.map(tweet => (
                <div key={tweet.id} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                  {/* Author */}
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-bold">
                      {tweet.author.username[0]?.toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold truncate">{tweet.author.name}</p>
                      <p className="text-xs text-gray-500">@{tweet.author.username} · {timeAgo(tweet.created_at)}</p>
                    </div>
                    <a
                      href={tweet.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-gray-600 hover:text-blue-400"
                    >
                      ↗
                    </a>
                  </div>

                  {/* Text */}
                  <p className="text-sm text-gray-200 leading-relaxed mb-3 whitespace-pre-wrap">{tweet.text}</p>

                  {/* Metrics */}
                  <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
                    <span>❤️ {tweet.metrics.like_count}</span>
                    <span>💬 {tweet.metrics.reply_count}</span>
                    <span>🔄 {tweet.metrics.retweet_count}</span>
                    {tweet.author.public_metrics && (
                      <span className="text-gray-600">👥 {(tweet.author.public_metrics.followers_count / 1000).toFixed(1)}k</span>
                    )}
                  </div>

                  {/* Action buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => startReply(tweet)}
                      className="flex-1 bg-blue-600/20 text-blue-400 py-2 rounded-lg text-xs font-medium hover:bg-blue-600/30 transition"
                    >
                      Responder
                    </button>
                    <a
                      href={tweet.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 bg-gray-800 text-gray-400 rounded-lg text-xs hover:text-white transition"
                    >
                      Abrir
                    </a>
                  </div>

                  {/* Reply composer (inline) */}
                  {replyTo?.id === tweet.id && (
                    <div className="mt-3 pt-3 border-t border-gray-800 space-y-3">
                      {/* AI suggestions */}
                      {aiSuggestions.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs text-gray-500 font-medium">🤖 Sugestões (clique para usar):</p>
                          {aiSuggestions.map((s, i) => (
                            <button
                              key={i}
                              onClick={() => setReplyText(s)}
                              className="w-full text-left p-2 bg-gray-800 rounded-lg text-xs text-gray-300 hover:bg-gray-700 transition"
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      )}

                      {/* Text area */}
                      <textarea
                        value={replyText}
                        onChange={e => setReplyText(e.target.value)}
                        placeholder="Escreva sua resposta..."
                        className="w-full bg-gray-800 border border-gray-700 rounded-xl p-3 text-sm resize-none h-24"
                        maxLength={280}
                      />
                      <div className="flex items-center justify-between">
                        <span className={`text-xs ${replyText.length > 260 ? 'text-red-400' : 'text-gray-500'}`}>
                          {replyText.length}/280
                        </span>
                        <div className="flex gap-2">
                          <button
                            onClick={addToQueue}
                            disabled={!replyText.trim()}
                            className="px-3 py-1.5 bg-gray-700 text-gray-300 rounded-lg text-xs disabled:opacity-50"
                          >
                            📋 Fila
                          </button>
                          <button
                            onClick={sendReply}
                            disabled={posting || !replyText.trim()}
                            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white rounded-lg text-xs font-medium transition"
                          >
                            {posting ? '...' : '🚀 Enviar'}
                          </button>
                          <button
                            onClick={() => { setReplyTo(null); setReplyText(''); }}
                            className="px-2 py-1.5 text-gray-500 text-xs"
                          >
                            ✕
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {tweets.length === 0 && !loading && (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-3xl mb-2">🔍</p>
                  <p className="text-sm">Use os filtros acima para buscar tweets sobre LGPD, PII, compliance...</p>
                </div>
              )}

              {loading && (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-sm animate-pulse">Buscando tweets...</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* === COMPOSE TAB === */}
        {tab === 'compose' && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold">Novo post</h2>
            <textarea
              value={newTweet}
              onChange={e => setNewTweet(e.target.value)}
              placeholder="O que você quer compartilhar?..."
              className="w-full bg-gray-900 border border-gray-800 rounded-xl p-4 text-sm resize-none h-32"
              maxLength={280}
            />
            <div className="flex items-center justify-between">
              <span className={`text-xs ${newTweet.length > 260 ? 'text-red-400' : 'text-gray-500'}`}>
                {newTweet.length}/280
              </span>
              <button
                onClick={postNewTweet}
                disabled={posting || !newTweet.trim()}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 text-white rounded-xl text-sm font-medium transition"
              >
                {posting ? 'Publicando...' : '🚀 Publicar'}
              </button>
            </div>

            {/* Quick templates */}
            <div className="border-t border-gray-800 pt-4">
              <p className="text-xs text-gray-500 mb-3 font-medium">Templates rápidos:</p>
              <div className="space-y-2">
                {[
                  '🛡️ Construindo uma ferramenta open-source para detecção de PII brasileiro — CPF, CNPJ, RG, placa, processo judicial e mais. Em desenvolvimento ativo, feedback bem-vindo: guard.egos.ia.br',
                  '💡 Sabia que nenhum LLM (ChatGPT, Claude, Gemini) é considerado plenamente LGPD-compliant no Brasil? (FGV 2025) — Mascarar CPF/CNPJ antes de enviar é responsabilidade sua. npm install @egosbr/guard-brasil',
                  '📊 ANPD planeja 40 ações de fiscalização para 2026-2027. Se sua startup usa IA com dados brasileiros, vale ter audit trail. guard.egos.ia.br gera receipts SHA-256 por inspeção.',
                ].map((t, i) => (
                  <button
                    key={i}
                    onClick={() => setNewTweet(t)}
                    className="w-full text-left p-3 bg-gray-900 border border-gray-800 rounded-lg text-xs text-gray-400 hover:text-gray-200 hover:border-gray-700 transition"
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* === QUEUE TAB === */}
        {tab === 'queue' && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold">Fila de respostas</h2>
            {queue.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <p className="text-3xl mb-2">📋</p>
                <p className="text-sm">Adicione respostas à fila na aba Buscar.</p>
                <p className="text-xs text-gray-600 mt-1">Revise e envie quando quiser.</p>
              </div>
            )}
            {queue.map((item, i) => (
              <div key={i} className={`bg-gray-900 rounded-xl p-4 border ${item.status === 'sent' ? 'border-green-800 opacity-60' : 'border-gray-800'}`}>
                {/* Original tweet */}
                <div className="mb-3">
                  <p className="text-xs text-gray-500 mb-1">
                    Respondendo a @{item.tweet.author.username}:
                  </p>
                  <p className="text-xs text-gray-400 line-clamp-2">{item.tweet.text}</p>
                  <a href={item.tweet.url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:text-blue-400">
                    abrir ↗
                  </a>
                </div>

                {/* Reply */}
                <div className="bg-gray-800 rounded-lg p-3 mb-3">
                  {item.status === 'pending' ? (
                    <textarea
                      value={item.reply}
                      onChange={e => setQueue(prev => prev.map((q, idx) => idx === i ? { ...q, reply: e.target.value, status: 'edited' as const } : q))}
                      className="w-full bg-transparent text-sm resize-none"
                      rows={3}
                    />
                  ) : (
                    <p className="text-sm">{item.reply}</p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {item.status !== 'sent' ? (
                    <>
                      <button
                        onClick={() => sendQueued(i)}
                        className="flex-1 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg text-xs font-medium transition"
                      >
                        🚀 Enviar agora
                      </button>
                      <button
                        onClick={() => setQueue(prev => prev.filter((_, idx) => idx !== i))}
                        className="px-3 py-2 bg-gray-800 text-red-400 rounded-lg text-xs"
                      >
                        🗑
                      </button>
                    </>
                  ) : (
                    <span className="text-xs text-green-400">✅ Enviado</span>
                  )}
                </div>
              </div>
            ))}

            {/* Bulk send */}
            {queue.filter(q => q.status !== 'sent').length > 1 && (
              <button
                onClick={() => queue.forEach((_, i) => { if (queue[i].status !== 'sent') sendQueued(i); })}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white py-3 rounded-xl text-sm font-medium transition"
              >
                🚀 Enviar todos ({queue.filter(q => q.status !== 'sent').length} pendentes)
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

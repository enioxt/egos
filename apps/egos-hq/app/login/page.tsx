'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [secret, setSecret] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ secret }),
      });

      if (res.ok) {
        router.push('/');
        router.refresh();
      } else {
        setError('Credenciais inválidas.');
        setSecret('');
      }
    } catch {
      setError('Erro de conexão.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: 360, padding: '2.5rem', background: '#111', border: '1px solid #1f1f1f', borderRadius: 12 }}>
        {/* Logo */}
        <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>⬡</div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#22c55e', letterSpacing: '0.1em' }}>EGOS HQ</div>
          <div style={{ fontSize: 12, color: '#737373', marginTop: 4 }}>Mission Control — Acesso Privado</div>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: 11, color: '#737373', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              Senha de Acesso
            </label>
            <input
              type="password"
              value={secret}
              onChange={e => setSecret(e.target.value)}
              placeholder="••••••••••••••••"
              autoFocus
              required
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: '#0a0a0a',
                border: `1px solid ${error ? '#ef4444' : '#1f1f1f'}`,
                borderRadius: 8,
                color: '#e5e5e5',
                fontSize: 14,
                outline: 'none',
                fontFamily: 'inherit',
              }}
            />
          </div>

          {error && (
            <div style={{ fontSize: 12, color: '#ef4444', marginBottom: '1rem', padding: '0.5rem', background: '#1a0505', borderRadius: 6 }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !secret}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: loading ? '#16a34a' : '#22c55e',
              color: '#000',
              fontWeight: 700,
              fontSize: 14,
              border: 'none',
              borderRadius: 8,
              cursor: loading || !secret ? 'not-allowed' : 'pointer',
              opacity: !secret ? 0.5 : 1,
              fontFamily: 'inherit',
            }}
          >
            {loading ? 'Verificando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  );
}

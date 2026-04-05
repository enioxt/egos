'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const NAV = [
  { href: '/', label: 'Mission Control', icon: '⬡' },
  { href: '/x', label: 'X.com Monitor', icon: '𝕏', badge: 'pending' },
  { href: '/agents', label: 'Agentes', icon: '◈' },
  { href: '/events', label: 'Eventos Live', icon: '◉' },
  { href: '/knowledge', label: 'Knowledge Base', icon: '◎' },
];

export function HQLayout({ children, pendingCount = 0 }: { children: React.ReactNode; pendingCount?: number }) {
  const pathname = usePathname();
  const router = useRouter();

  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    router.push('/login');
    router.refresh();
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0a0a0a' }}>
      {/* Sidebar */}
      <nav style={{
        width: 220,
        background: '#111',
        borderRight: '1px solid #1f1f1f',
        display: 'flex',
        flexDirection: 'column',
        padding: '1.5rem 0',
        position: 'fixed',
        top: 0,
        left: 0,
        height: '100vh',
        zIndex: 50,
      }}>
        {/* Brand */}
        <div style={{ padding: '0 1.25rem', marginBottom: '2rem' }}>
          <div style={{ fontSize: 11, color: '#22c55e', letterSpacing: '0.15em', fontWeight: 700 }}>⬡ EGOS HQ</div>
          <div style={{ fontSize: 10, color: '#555', marginTop: 2 }}>Mission Control</div>
        </div>

        {/* Nav items */}
        <div style={{ flex: 1 }}>
          {NAV.map(item => {
            const active = item.href === '/' ? pathname === '/' : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '0.6rem 1.25rem',
                  color: active ? '#22c55e' : '#737373',
                  background: active ? '#0f1f0f' : 'transparent',
                  borderLeft: active ? '2px solid #22c55e' : '2px solid transparent',
                  textDecoration: 'none',
                  fontSize: 13,
                  transition: 'color 0.15s',
                }}
              >
                <span style={{ fontSize: 16, minWidth: 20, textAlign: 'center' }}>{item.icon}</span>
                <span style={{ flex: 1 }}>{item.label}</span>
                {item.badge === 'pending' && pendingCount > 0 && (
                  <span style={{
                    background: '#22c55e',
                    color: '#000',
                    fontSize: 10,
                    fontWeight: 700,
                    padding: '1px 6px',
                    borderRadius: 9999,
                  }}>{pendingCount}</span>
                )}
              </Link>
            );
          })}
        </div>

        {/* Logout */}
        <div style={{ padding: '0 1rem' }}>
          <button
            onClick={logout}
            style={{
              width: '100%',
              padding: '0.5rem',
              background: 'transparent',
              border: '1px solid #1f1f1f',
              borderRadius: 6,
              color: '#555',
              fontSize: 12,
              cursor: 'pointer',
              fontFamily: 'inherit',
            }}
          >
            Sair
          </button>
        </div>
      </nav>

      {/* Main content */}
      <main style={{ marginLeft: 220, flex: 1, padding: '2rem', maxWidth: 'calc(100vw - 220px)' }}>
        {children}
      </main>
    </div>
  );
}

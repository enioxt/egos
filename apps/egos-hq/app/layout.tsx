import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'EGOS HQ',
  description: 'Mission Control — private dashboard',
  robots: 'noindex, nofollow',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}

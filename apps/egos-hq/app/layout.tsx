import type { Metadata } from 'next';
import './globals.css';

const siteUrl = 'https://hq.egos.ia.br';
const title = 'EGOS HQ — Mission Control';
const description = 'Observability, governance and agent runtime for the EGOS ecosystem.';

export const metadata: Metadata = {
  title,
  description,
  metadataBase: new URL(siteUrl),
  robots: 'noindex, nofollow',
  openGraph: {
    title,
    description,
    url: siteUrl,
    siteName: 'EGOS HQ',
    locale: 'pt_BR',
    type: 'website',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: title }],
  },
  twitter: { card: 'summary_large_image', title, description, images: ['/og-image.png'] },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}

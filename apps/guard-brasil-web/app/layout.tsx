import type { Metadata } from 'next';
import './globals.css';

const siteUrl = 'https://guard.egos.ia.br';
const title = 'Guard Brasil — Mascaramento de PII LGPD + Ética ATRiAN';
const description =
  'API de segurança de IA para dados brasileiros. Detecta e mascara 15 tipos de PII (CPF, CNPJ, RG, CNH) em tempo real. 500 chamadas/mês grátis. Compliance LGPD automático.';
const ogImage = `${siteUrl}/og-image.png`;

export const metadata: Metadata = {
  title,
  description,
  metadataBase: new URL(siteUrl),
  alternates: {
    canonical: '/',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    title,
    description,
    url: siteUrl,
    siteName: 'Guard Brasil',
    locale: 'pt_BR',
    type: 'website',
    images: [
      {
        url: ogImage,
        width: 1200,
        height: 630,
        alt: title,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title,
    description,
    images: [ogImage],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">{children}</body>
    </html>
  );
}

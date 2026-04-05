import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Guard Brasil — Mascaramento de PII LGPD + Ética ATRiAN',
  description: 'Proteja dados sensíveis brasileiros em tempo real. CPF, RG, MASP, placa — masking em 4ms.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">{children}</body>
    </html>
  );
}

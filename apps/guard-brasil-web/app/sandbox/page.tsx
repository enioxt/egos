import type { Metadata } from 'next';
import SandboxClient from './sandbox-client';

export const metadata: Metadata = {
  title: 'Sandbox Auditável — Guard Brasil',
  description:
    'Teste a API Guard Brasil ao vivo com seus próprios dados. 20 cenários pré-validados, resultados em tempo real, recibos criptograficamente verificáveis. Free tier 500 chamadas/mês.',
};

export default function SandboxPage() {
  return <SandboxClient />;
}

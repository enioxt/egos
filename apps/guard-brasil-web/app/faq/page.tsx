'use client';

import Link from 'next/link';
import { useState } from 'react';

interface FaqItem {
  q: string;
  a: string;
}

const FAQ_PTBR: FaqItem[] = [
  {
    q: 'O Guard Brasil armazena meus dados?',
    a: 'Nao. O texto e processado em memoria e descartado. Apenas o hash SHA-256 e mantido como receipt.',
  },
  {
    q: 'Preciso de cartao de credito?',
    a: 'Nao. O plano gratuito (500 chamadas/mes) nao exige cartao.',
  },
  {
    q: 'Quais tipos de dados sao detectados?',
    a: 'CPF, CNPJ, RG, CNH, Titulo de Eleitor, PIS/PASEP, MASP, REDS, Placa Veicular (Mercosul e antiga), Processo Judicial (CNJ), Telefone, Email, CEP, Data de Nascimento e Nome Completo.',
  },
  {
    q: 'O Guard Brasil e open source?',
    a: 'O pacote npm @egosbr/guard-brasil e MIT. A API e um servico pago.',
  },
  {
    q: 'Como funciona a validacao etica ATRiAN?',
    a: 'Score 0-100 que detecta vies, conteudo discriminatorio e violacoes eticas. Textos com score abaixo de 30 sao sinalizados para revisao.',
  },
  {
    q: 'Quais formatos de arquivo sao suportados?',
    a: 'Apenas texto puro (string). PDFs e imagens nao sao suportados neste momento.',
  },
  {
    q: 'A API e compativel com LGPD?',
    a: 'Sim. Cada chamada gera um receipt com hash SHA-256, citando Lei 13.709/2018. Os dados sao processados em memoria e nunca armazenados.',
  },
];

const FAQ_EN: FaqItem[] = [
  {
    q: 'Does Guard Brasil store my data?',
    a: 'No. Text is processed in memory and discarded. Only the SHA-256 hash is kept as a receipt.',
  },
  {
    q: 'Do I need a credit card?',
    a: 'No. The free tier (500 calls/month) does not require a credit card.',
  },
  {
    q: 'What types of data are detected?',
    a: 'CPF, CNPJ, RG, CNH, Voter ID, PIS/PASEP, MASP, REDS, Vehicle Plate (Mercosul and legacy), Lawsuit Number (CNJ), Phone, Email, ZIP Code, Date of Birth, and Full Name.',
  },
  {
    q: 'Is Guard Brasil open source?',
    a: 'The npm package @egosbr/guard-brasil is MIT licensed. The API is a paid service.',
  },
  {
    q: 'How does the ATRiAN ethical validation work?',
    a: 'Score from 0-100 that detects bias, discriminatory content, and ethical violations. Texts scoring below 30 are flagged for review.',
  },
  {
    q: 'What file formats are supported?',
    a: 'Plain text (string) only. PDFs and images are not supported at this time.',
  },
  {
    q: 'Is the API LGPD compliant?',
    a: 'Yes. Each call generates a receipt with a SHA-256 hash, citing Law 13.709/2018. Data is processed in memory and never stored.',
  },
];

function FaqSection({ title, items }: { title: string; items: FaqItem[] }) {
  const [open, setOpen] = useState<number | null>(null);

  return (
    <section className="mb-12">
      <h2 className="text-xl font-bold text-emerald-400 mb-6">{title}</h2>
      <div className="space-y-3">
        {items.map((item, i) => (
          <div
            key={i}
            className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden"
          >
            <button
              onClick={() => setOpen(open === i ? null : i)}
              className="w-full text-left px-6 py-4 flex items-center justify-between hover:bg-slate-800/50 transition cursor-pointer"
            >
              <span className="text-sm font-medium text-slate-200">{item.q}</span>
              <span className="text-slate-500 text-lg ml-4 flex-shrink-0">
                {open === i ? '−' : '+'}
              </span>
            </button>
            {open === i && (
              <div className="px-6 pb-4">
                <p className="text-sm text-slate-400 leading-relaxed">{item.a}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

export default function FaqPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/landing" className="text-emerald-400 font-bold text-lg hover:text-emerald-300 transition">
            Guard Brasil
          </Link>
          <nav className="flex gap-6 text-sm text-slate-400">
            <Link href="/about" className="hover:text-white transition">Sobre</Link>
            <Link href="/terms" className="hover:text-white transition">Termos</Link>
            <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-16">
        <h1 className="text-4xl font-bold mb-4">FAQ</h1>
        <p className="text-slate-400 mb-12">Perguntas frequentes / Frequently asked questions</p>

        <FaqSection title="Portugues" items={FAQ_PTBR} />
        <FaqSection title="English" items={FAQ_EN} />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center">
        <div className="flex justify-center gap-6 text-xs text-slate-500 mb-4">
          <Link href="/landing" className="hover:text-white transition">Inicio</Link>
          <Link href="/about" className="hover:text-white transition">Sobre</Link>
          <Link href="/terms" className="hover:text-white transition">Termos</Link>
          <Link href="/privacy" className="hover:text-white transition">Privacidade</Link>
        </div>
        <p className="text-xs text-slate-600">
          Guard Brasil | @egosbr/guard-brasil | MIT License
        </p>
      </footer>
    </div>
  );
}

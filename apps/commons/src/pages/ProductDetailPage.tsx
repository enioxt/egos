import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft, Github, CheckCircle2, Star, Users,
  Code2, Zap, ShieldCheck, Play, ExternalLink,
  Download, BookOpen, MessageSquare
} from 'lucide-react'

interface ProductDetail {
  id: string
  title: string
  subtitle: string
  description: string
  longDescription: string
  price: number | 'free' | 'custom'
  githubUrl: string
  demoUrl?: string
  docsUrl?: string
  tier: 'free' | 'pro' | 'enterprise'
  category: string
  tags: string[]
  rating: number
  downloads?: number
  useCases: string[]
  techStack: string[]
  features: { title: string; description: string }[]
  screenshots?: string[]
  pricing: {
    implementation: number
    support_basic?: number
    support_pro?: number
    support_enterprise?: number
  }
  splitDetails: string
}

// Mock data - será substituído por fetch dinâmico
const productDatabase: Record<string, ProductDetail> = {
  'egos-kernel': {
    id: 'egos-kernel',
    title: 'EGOS Kernel',
    subtitle: 'Orchestration Engine',
    description: 'O núcleo de governança, pipeline de prompts e runtime base para construir agentes baseados em TypeScript/Node.',
    longDescription: 'O EGOS Kernel é o coração do ecossistema EGOS. Ele fornece governança como código (RuleOps), enforcement automático via pre-commit hooks, multi-LLM provider abstraction, event bus para coordenação de agentes e frozen zones para proteção de código crítico. Construído para times que precisam de IA governada desde o dia 1.',
    price: 2500,
    githubUrl: 'https://github.com/enioxt/egos',
    docsUrl: '/docs/kernel',
    tier: 'pro',
    category: 'tool',
    tags: ['kernel', 'governança', 'runtime', 'RuleOps', 'TypeScript'],
    rating: 5.0,
    downloads: 127,
    useCases: [
      'Software houses que precisam de governança LGPD desde o início',
      'Startups de IA que querem evitar dívida técnica de governance',
      'Empresas com múltiplos LLMs que precisam de abstração unificada',
      'Times que trabalham com agentes autônomos e precisam de auditoria'
    ],
    techStack: ['TypeScript', 'Node.js', 'Bun', 'Git Hooks', 'Event Bus'],
    features: [
      {
        title: 'RuleOps (Governance-as-Code)',
        description: 'Regras de governança versionadas como código. Pre-commit hooks bloqueiam commits que violam políticas LGPD, segurança ou compliance.'
      },
      {
        title: 'Multi-LLM Provider',
        description: 'Abstração para Qwen, Gemini, Claude, OpenAI. Troque de provider sem reescrever código. Rate limiting e fallback automáticos.'
      },
      {
        title: 'Frozen Zones',
        description: 'Proteja arquivos críticos de edição acidental. Qualquer tentativa de alterar código frozen gera alerta e bloqueia o commit.'
      },
      {
        title: 'Agent Runtime',
        description: 'Event bus + runner orchestration. Coordene múltiplos agentes com comunicação via eventos e logging centralizado.'
      },
      {
        title: 'Workflows /start e /end',
        description: 'Protocolo de ativação e desativação de sessões. Garante que todas checagens de governança rodem no início e fim de cada sessão.'
      }
    ],
    pricing: {
      implementation: 2500,
      support_basic: 500,
      support_pro: 1500,
      support_enterprise: 3000
    },
    splitDetails: 'R$ 2.375 (Implementador) / R$ 125 (Kernel)',
    screenshots: []
  },
  'carteira-livre': {
    id: 'carteira-livre',
    title: 'Carteira Livre',
    subtitle: 'SaaS Marketplace Base',
    description: 'Plataforma Next.js 15 pronta com auth Supabase, pagamentos integrado (Asaas), onboarding e agendamento.',
    longDescription: 'Carteira-Livre é um SaaS marketplace production-ready. Fork limpo para qualquer negócio multi-prestador: instrutores, freelancers, consultores. Stack moderna (Next.js 15 + Supabase + Asaas), 161k LOC, 546 testes passando, 100 tabelas, 241 APIs. Deploy white-label em 2 dias.',
    price: 4900,
    githubUrl: 'https://github.com/enioxt/carteira-livre',
    demoUrl: 'https://carteira-livre.vercel.app',
    tier: 'pro',
    category: 'template',
    tags: ['SaaS', 'Asaas', 'Next.js', 'Marketplace', 'Supabase'],
    rating: 4.8,
    downloads: 43,
    useCases: [
      'Founders de marketplace (educação, serviços, saúde)',
      'Plataformas multi-prestador que precisam de onboarding e agendamento',
      'Empresas que querem split de pagamento automático (Asaas)',
      'Times que precisam de SaaS white-label em produção rápido'
    ],
    techStack: ['Next.js 15', 'React 19', 'Supabase', 'Asaas Payments', 'Tailwind CSS', 'TypeScript'],
    features: [
      {
        title: 'Pagamentos Asaas (PIX, Boleto, Cartão)',
        description: 'Integração completa com Asaas. Split automático entre plataforma e prestador. Webhooks configurados para todos status de pagamento.'
      },
      {
        title: 'Auth Supabase Multi-Provider',
        description: 'Login via Google, Facebook, Email/Password. RLS (Row Level Security) configurado para multi-tenant. Roles de admin, instrutor, aluno.'
      },
      {
        title: 'Agendamento e Calendário',
        description: 'Sistema de agendamento com disponibilidade do prestador, bloqueio de horários, notificações automáticas e integração com Google Calendar.'
      },
      {
        title: 'Dashboard Administrativo',
        description: 'Painel completo para admin gerenciar prestadores, pedidos, pagamentos, disputas. Analytics em tempo real com métricas de conversão.'
      },
      {
        title: 'AI/LLM com Guardrails',
        description: 'Chatbot integrado com PII masking (Guard Brasil) e validação ética ATRiAN. Respostas dentro de escopo definido.'
      }
    ],
    pricing: {
      implementation: 4900,
      support_basic: 800,
      support_pro: 2000,
      support_enterprise: 4500
    },
    splitDetails: 'R$ 4.655 (Implementador) / R$ 245 (Kernel)',
    screenshots: []
  },
  '852-inteligencia': {
    id: '852-inteligencia',
    title: '852 Inteligência',
    subtitle: 'Chatbot Institucional Seguro',
    description: 'Chatbot Next.js + Qwen/Gemini com detecção PII agressiva e ATRiAN level 1. Feito originalmente para a Polícia Civil.',
    longDescription: '852 Inteligência é um chatbot institucional com governança de segurança extrema. Desenvolvido para Polícia Civil MG, processa consultas sensíveis sem vazar PII (CPF, RG, nomes). ATRiAN ethical validation garante que respostas não violem diretrizes legais. Ideal para govtech, tribunais, MP, empresas com dados sensíveis.',
    price: 3500,
    githubUrl: 'https://github.com/enioxt/852',
    tier: 'pro',
    category: 'agent',
    tags: ['chatbot', 'ATRiAN', 'segurança', 'LGPD', 'govtech'],
    rating: 4.9,
    downloads: 18,
    useCases: [
      'Tribunais e Ministério Público (consultas de processos sem vazar dados)',
      'Polícias e órgãos de segurança (inteligência sem expor fontes)',
      'Empresas com dados sensíveis (RH, compliance, jurídico)',
      'Órgãos públicos que precisam de chatbot anônimo e auditável'
    ],
    techStack: ['Next.js', 'Qwen/Gemini', 'Guard Brasil', 'ATRiAN', 'Docker', 'Supabase'],
    features: [
      {
        title: 'PII Detection Agressiva',
        description: 'Guard Brasil integrado. Detecta CPF, RG, CNH, telefones, emails, endereços. Mascara automaticamente antes de enviar para LLM. Zero chance de vazamento.'
      },
      {
        title: 'ATRiAN Ethical Validation',
        description: 'Valida respostas do LLM contra diretrizes éticas. Bloqueia respostas que violam LGPD, discriminação, fake news. Level 1 (bloqueio) ou Level 2 (warning).'
      },
      {
        title: 'Chatbot Anônimo',
        description: 'Sem login obrigatório. Sessões anônimas com ID de sessão. Logs auditáveis mas sem identificação de usuário final (LGPD compliant).'
      },
      {
        title: 'Smart Correlation Engine',
        description: 'Correlaciona entidades mencionadas (pessoas, lugares, eventos) via grafo interno. Responde perguntas complexas sem expor dados brutos.'
      },
      {
        title: 'Report Sharing',
        description: 'Gera relatórios PDF com fontes citadas. Compartilhamento via link criptografado com expiração configurável.'
      }
    ],
    pricing: {
      implementation: 3500,
      support_basic: 600,
      support_pro: 1800,
      support_enterprise: 3500
    },
    splitDetails: 'R$ 3.325 (Implementador) / R$ 175 (Kernel)',
    screenshots: []
  }
}

export function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const product = id ? productDatabase[id] : null

  if (!product) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] pt-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-3xl font-bold text-slate-100 mb-4">Produto não encontrado</h1>
          <Link to="/" className="text-violet-400 hover:underline">← Voltar para catálogo</Link>
        </div>
      </div>
    )
  }

  const priceDisplay = typeof product.price === 'number'
    ? `R$ ${product.price.toLocaleString('pt-BR')}`
    : product.price === 'free' ? 'Grátis' : 'Sob consulta'

  return (
    <div className="min-h-screen bg-[#0a0a0f] pt-24 pb-20">
      {/* Breadcrumb */}
      <div className="max-w-6xl mx-auto px-6 mb-8">
        <Link to="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-violet-400 transition-colors">
          <ArrowLeft size={16} />
          Voltar para catálogo
        </Link>
      </div>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 mb-16">
        <div className="grid lg:grid-cols-2 gap-12 items-start">
          {/* Left: Product Info */}
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/30 text-violet-300 text-sm font-semibold mb-4">
              {product.tier === 'pro' && '💼 Professional'}
              {product.tier === 'enterprise' && '🏢 Enterprise'}
              {product.tier === 'free' && '🎁 Grátis'}
            </div>

            <h1 className="text-5xl font-black text-slate-100 mb-4 leading-tight">{product.title}</h1>
            <p className="text-xl text-violet-300 font-semibold mb-6">{product.subtitle}</p>
            <p className="text-lg text-slate-300 leading-relaxed mb-8">{product.longDescription}</p>

            {/* Stats */}
            <div className="flex gap-6 mb-8">
              <div className="flex items-center gap-2">
                <Star size={18} fill="#fbbf24" color="#fbbf24" />
                <span className="text-lg font-bold text-amber-400">{product.rating}</span>
              </div>
              {product.downloads && (
                <div className="flex items-center gap-2">
                  <Download size={18} className="text-cyan-400" />
                  <span className="text-lg font-semibold text-slate-300">{product.downloads} implementações</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Users size={18} className="text-emerald-400" />
                <span className="text-lg font-semibold text-slate-300">Em Produção</span>
              </div>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-8">
              {product.tags.map(tag => (
                <span
                  key={tag}
                  className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-sm font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4">
              <a
                href={product.githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-white font-bold transition-all shadow-lg shadow-emerald-600/30"
              >
                <Github size={18} />
                Ver no GitHub (Grátis)
              </a>
              <button className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 rounded-xl text-white font-bold transition-all shadow-lg shadow-violet-600/40">
                <Zap size={18} />
                Adquirir Implementação
              </button>
              {product.demoUrl && (
                <a
                  href={product.demoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-slate-200 font-semibold transition-all"
                >
                  <Play size={18} />
                  Ver Demo
                </a>
              )}
            </div>
          </div>

          {/* Right: Pricing Card */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-violet-500/30 rounded-3xl p-8 shadow-2xl shadow-violet-500/10">
            <h3 className="text-2xl font-bold text-slate-100 mb-6">Opções de Aquisição</h3>

            {/* Free Option */}
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6 mb-4">
              <div className="flex items-center gap-3 mb-3">
                <Github size={20} className="text-emerald-400" />
                <span className="text-lg font-bold text-emerald-300">Código Aberto</span>
              </div>
              <p className="text-slate-300 text-sm mb-4">
                Clone o repositório, estude o código, implemente você mesmo. Totalmente grátis, open-source.
              </p>
              <div className="text-3xl font-black text-emerald-400 mb-2">R$ 0</div>
              <a
                href={product.githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-center py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-white font-bold transition-colors"
              >
                Acessar GitHub
              </a>
            </div>

            {/* Paid Implementation */}
            <div className="bg-violet-500/10 border border-violet-500/30 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-3">
                <Code2 size={20} className="text-violet-400" />
                <span className="text-lg font-bold text-violet-300">Implementação Profissional</span>
              </div>
              <p className="text-slate-300 text-sm mb-4">
                Implementação completa, customização, deploy, treinamento da equipe. Pronto para produção em 5-10 dias.
              </p>
              <div className="text-4xl font-black text-slate-100 mb-1">{priceDisplay}</div>
              <div className="text-xs text-violet-400 mb-4">{product.splitDetails}</div>

              <div className="space-y-2 mb-6">
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={16} className="text-violet-400 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-slate-300">Setup completo e deploy em produção</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={16} className="text-violet-400 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-slate-300">Customização de branding e configurações</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={16} className="text-violet-400 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-slate-300">Treinamento da equipe técnica (4h)</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={16} className="text-violet-400 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-slate-300">Suporte pós-implantação (30 dias)</span>
                </div>
              </div>

              <button className="block w-full py-3 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 rounded-xl text-white font-bold transition-all shadow-lg shadow-violet-600/40">
                Solicitar Orçamento
              </button>
            </div>

            {/* Support Plans */}
            {product.pricing.support_basic && (
              <div className="mt-6 pt-6 border-t border-slate-800">
                <h4 className="text-sm font-bold text-slate-300 mb-3">Planos de Suporte Mensal</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between text-slate-400">
                    <span>Basic (manutenção)</span>
                    <span className="font-semibold">R$ {product.pricing.support_basic}/mês</span>
                  </div>
                  {product.pricing.support_pro && (
                    <div className="flex justify-between text-slate-400">
                      <span>Pro (manutenção + features)</span>
                      <span className="font-semibold">R$ {product.pricing.support_pro}/mês</span>
                    </div>
                  )}
                  {product.pricing.support_enterprise && (
                    <div className="flex justify-between text-slate-400">
                      <span>Enterprise (SLA + customização)</span>
                      <span className="font-semibold">R$ {product.pricing.support_enterprise}/mês</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-6xl mx-auto px-6 mb-16">
        <h2 className="text-3xl font-bold text-slate-100 mb-8 flex items-center gap-3">
          <ShieldCheck className="text-violet-400" size={32} />
          Features Principais
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          {product.features.map((feature, idx) => (
            <div
              key={idx}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-violet-500/30 transition-all"
            >
              <h3 className="text-lg font-bold text-slate-100 mb-3">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Use Cases */}
      <div className="max-w-6xl mx-auto px-6 mb-16">
        <h2 className="text-3xl font-bold text-slate-100 mb-8 flex items-center gap-3">
          <Users className="text-cyan-400" size={32} />
          Casos de Uso
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {product.useCases.map((useCase, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 bg-slate-900/50 border border-slate-800 rounded-xl p-5"
            >
              <CheckCircle2 size={20} className="text-cyan-400 flex-shrink-0 mt-0.5" />
              <span className="text-slate-300 leading-relaxed">{useCase}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div className="max-w-6xl mx-auto px-6 mb-16">
        <h2 className="text-3xl font-bold text-slate-100 mb-8 flex items-center gap-3">
          <Code2 className="text-emerald-400" size={32} />
          Stack Tecnológica
        </h2>
        <div className="flex flex-wrap gap-3">
          {product.techStack.map((tech, idx) => (
            <div
              key={idx}
              className="px-5 py-3 bg-gradient-to-r from-emerald-600/20 to-cyan-600/20 border border-emerald-500/30 rounded-xl text-emerald-300 font-semibold"
            >
              {tech}
            </div>
          ))}
        </div>
      </div>

      {/* Resources */}
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-3xl font-bold text-slate-100 mb-8">Recursos e Documentação</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <a
            href={product.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-4 bg-slate-900 border border-slate-800 hover:border-violet-500/30 rounded-2xl p-6 transition-all group"
          >
            <Github size={28} className="text-slate-400 group-hover:text-violet-400 transition-colors flex-shrink-0" />
            <div>
              <h3 className="font-bold text-slate-100 mb-1 group-hover:text-violet-300 transition-colors">Repositório GitHub</h3>
              <p className="text-sm text-slate-400">Código-fonte completo e documentação técnica</p>
            </div>
            <ExternalLink size={16} className="text-slate-600 ml-auto" />
          </a>

          {product.docsUrl && (
            <Link
              to={product.docsUrl}
              className="flex items-start gap-4 bg-slate-900 border border-slate-800 hover:border-cyan-500/30 rounded-2xl p-6 transition-all group"
            >
              <BookOpen size={28} className="text-slate-400 group-hover:text-cyan-400 transition-colors flex-shrink-0" />
              <div>
                <h3 className="font-bold text-slate-100 mb-1 group-hover:text-cyan-300 transition-colors">Documentação</h3>
                <p className="text-sm text-slate-400">Guias de instalação, configuração e uso</p>
              </div>
            </Link>
          )}

          <a
            href="#"
            className="flex items-start gap-4 bg-slate-900 border border-slate-800 hover:border-amber-500/30 rounded-2xl p-6 transition-all group"
          >
            <MessageSquare size={28} className="text-slate-400 group-hover:text-amber-400 transition-colors flex-shrink-0" />
            <div>
              <h3 className="font-bold text-slate-100 mb-1 group-hover:text-amber-300 transition-colors">Suporte</h3>
              <p className="text-sm text-slate-400">Tire dúvidas com a equipe técnica</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  )
}

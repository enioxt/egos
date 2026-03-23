import { useState, useEffect } from 'react'
import { supabase } from './lib/supabase'
import { emitMyceliumEvent } from './lib/mycelium'
import { processWithEthik } from './lib/agents'
import {
  Bot, Sparkles, ShieldCheck, BookOpen, Code2, Zap,
  Star, Users, TrendingUp, ArrowRight, Play,
  CheckCircle, Lock, Globe, Menu, X,
  Brain, Cpu, Layers, Award
} from 'lucide-react'
import './App.css'

// ─── Types ──────────────────────────────────────────────────────────────────

interface Product {
  id: string
  title: string
  subtitle: string
  description: string
  icon: React.ReactNode
  price: number | 'free' | 'custom'
  originalPrice?: number
  tier: 'free' | 'pro' | 'enterprise'
  category: 'course' | 'tool' | 'template' | 'agent'
  tags: string[]
  rating: number
  students: number
  featured?: boolean
  badge?: string
}

interface Category {
  id: string
  label: string
  icon: React.ReactNode
  count: number
}

// ─── Data ────────────────────────────────────────────────────────────────────

const categories: Category[] = [
  { id: 'all', label: 'Todos', icon: <Layers size={16} />, count: 18 },
  { id: 'course', label: 'Cursos', icon: <BookOpen size={16} />, count: 5 },
  { id: 'tool', label: 'Ferramentas', icon: <Cpu size={16} />, count: 6 },
  { id: 'template', label: 'Templates', icon: <Code2 size={16} />, count: 4 },
  { id: 'agent', label: 'Agentes IA', icon: <Bot size={16} />, count: 3 },
]

const products: Product[] = [
  {
    id: 'guard-brasil-sdk',
    title: 'EGOS Guard Brasil SDK',
    subtitle: 'Guardrails para IA em português',
    description: 'ATRiAN + PII Scanner + LGPD masking + Evidence Chain. O stack completo para IA segura no Brasil.',
    icon: <ShieldCheck size={28} className="text-violet-400" />,
    price: 'free',
    tier: 'free',
    category: 'tool',
    tags: ['LGPD', 'IA', 'segurança', 'compliance'],
    rating: 4.9,
    students: 312,
    featured: true,
    badge: 'Open Source',
  },
  {
    id: 'ia-com-autonomia',
    title: 'IA com Autonomia',
    subtitle: 'Do prompt ao agente governado',
    description: 'Do zero ao seu primeiro agente autônomo com governança real. Cascade, Codex, Claude Code — você escolhe o cockpit.',
    icon: <Brain size={28} className="text-cyan-400" />,
    price: 297,
    originalPrice: 497,
    tier: 'pro',
    category: 'course',
    tags: ['agentes', 'autonomia', 'governança', 'IA'],
    rating: 4.8,
    students: 847,
    featured: true,
    badge: 'Mais Vendido',
  },
  {
    id: 'egos-init-template',
    title: 'EGOS Init Template',
    subtitle: 'Bootstrap de repo governado',
    description: 'Estrutura completa com .guarani, hooks, SSOT, CI/CD e drift detection. Ative em < 2 minutos.',
    icon: <Zap size={28} className="text-yellow-400" />,
    price: 'free',
    tier: 'free',
    category: 'template',
    tags: ['template', 'governança', 'CI/CD'],
    rating: 4.7,
    students: 1204,
    badge: 'Grátis',
  },
  {
    id: 'orquestracao-multi-agente',
    title: 'Orquestração Multi-Agente',
    subtitle: 'Sistemas que se governam',
    description: 'Human in the loop onde importa. Pipelines com Cascade, Alibaba, Claude rodando em paralelo sem caos.',
    icon: <Layers size={28} className="text-violet-400" />,
    price: 497,
    originalPrice: 797,
    tier: 'pro',
    category: 'course',
    tags: ['multi-agente', 'orquestração', 'automação'],
    rating: 4.9,
    students: 423,
    badge: 'Novo',
  },
  {
    id: 'lgpd-ai-checklist',
    title: 'LGPD para IA — Checklist',
    subtitle: 'Compliance sem jurídico',
    description: 'Template auditável para validar conformidade de sistemas de IA com a Lei 13.709/2018.',
    icon: <CheckCircle size={28} className="text-green-400" />,
    price: 97,
    tier: 'pro',
    category: 'template',
    tags: ['LGPD', 'compliance', 'auditoria'],
    rating: 4.6,
    students: 678,
  },
  {
    id: 'agent-028-dashbot',
    title: 'Dashbot AIXBT — Agent-028',
    subtitle: 'Dashboard de inteligência de repo',
    description: 'Painel premium que mapeia seus repositórios em tempo real: LOC, APIs, saúde, commits e alertas.',
    icon: <TrendingUp size={28} className="text-cyan-400" />,
    price: 197,
    tier: 'pro',
    category: 'agent',
    tags: ['dashboard', 'métricas', 'repositório'],
    rating: 4.8,
    students: 156,
    badge: 'Beta',
  },
  {
    id: 'whatsapp-ia-flow',
    title: 'WhatsApp + IA Flow',
    subtitle: 'Chatbot com cérebro real',
    description: 'Template de chatbot WhatsApp com ATRiAN, memória de sessão, roteamento de modelos e LGPD out-of-the-box.',
    icon: <Bot size={28} className="text-green-400" />,
    price: 197,
    tier: 'pro',
    category: 'template',
    tags: ['WhatsApp', 'chatbot', 'IA'],
    rating: 4.7,
    students: 389,
  },
  {
    id: 'guard-brasil-api',
    title: 'Guard Brasil API',
    subtitle: 'Hosted guardrails para seu produto',
    description: 'REST API gerenciada com dashboard de compliance, audit logs, alertas de violação e SLA 99.5%.',
    icon: <Globe size={28} className="text-violet-400" />,
    price: 'custom',
    tier: 'enterprise',
    category: 'tool',
    tags: ['API', 'hosted', 'enterprise', 'LGPD'],
    rating: 5.0,
    students: 42,
    badge: 'Enterprise',
  },
]

const stats = [
  { label: 'Produtos ativos', value: '18', icon: <Sparkles size={20} /> },
  { label: 'Alunos & usuários', value: '4.200+', icon: <Users size={20} /> },
  { label: 'Repos governados', value: '7', icon: <Code2 size={20} /> },
  { label: 'Agentes em produção', value: '30+', icon: <Bot size={20} /> },
]

const howItWorks = [
  {
    step: '01',
    title: 'Escolha seu produto',
    description: 'Cursos, ferramentas, templates ou agentes — tudo com curadoria real e evidência de uso em produção.',
    icon: <BookOpen size={24} className="text-violet-400" />,
  },
  {
    step: '02',
    title: 'Agentes entregam',
    description: 'Acesso instantâneo. Agentes orquestram onboarding, suporte e atualizações automaticamente.',
    icon: <Bot size={24} className="text-cyan-400" />,
  },
  {
    step: '03',
    title: 'Human in the loop',
    description: 'Onde importa, você decide. Governança real — não burocracia. Resultados, não promessas.',
    icon: <Brain size={24} className="text-violet-400" />,
  },
]

// ─── Components ──────────────────────────────────────────────────────────────

function Navbar({ menuOpen, setMenuOpen }: { menuOpen: boolean; setMenuOpen: (v: boolean) => void }) {
  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: 'rgba(10,10,15,0.85)', backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(124,58,237,0.15)',
      padding: '0 24px',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Sparkles size={18} color="white" />
          </div>
          <div>
            <span style={{ fontWeight: 700, fontSize: 15, color: '#f1f5f9', letterSpacing: '-0.3px' }}>EGOS</span>
            <span style={{ fontWeight: 400, fontSize: 15, color: '#94a3b8' }}> Commons</span>
          </div>
        </div>

        {/* Desktop Nav */}
        <div style={{ display: 'flex', gap: 32, alignItems: 'center' }} className="desktop-nav">
          {['Produtos', 'Cursos', 'Agentes', 'Sobre'].map(item => (
            <a key={item} href="#" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: 14, fontWeight: 500, transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#e2e8f0')}
              onMouseLeave={e => (e.currentTarget.style.color = '#94a3b8')}>{item}</a>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <a href="#" style={{
            padding: '8px 20px', background: 'linear-gradient(135deg, #7c3aed, #5b21b6)',
            border: 'none', borderRadius: 8, color: 'white', fontSize: 14, fontWeight: 600,
            cursor: 'pointer', textDecoration: 'none', transition: 'all 0.2s',
          }}>Começar grátis</a>
          <button onClick={() => setMenuOpen(!menuOpen)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: 4 }} className="mobile-menu-btn">
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>
    </nav>
  )
}

function HeroBadge({ text }: { text: string }) {
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px',
      background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.4)',
      borderRadius: 100, fontSize: 13, fontWeight: 500, color: '#a78bfa',
      marginBottom: 24,
    }}>
      <Sparkles size={14} />
      {text}
    </div>
  )
}

function ProductCard({ product }: { product: Product }) {
  const priceDisplay = product.price === 'free'
    ? 'Grátis'
    : product.price === 'custom'
    ? 'Sob consulta'
    : `R$ ${product.price}`

  const tierColors = {
    free: { bg: 'rgba(16,185,129,0.15)', text: '#6ee7b7', border: 'rgba(16,185,129,0.3)' },
    pro: { bg: 'rgba(124,58,237,0.15)', text: '#a78bfa', border: 'rgba(124,58,237,0.3)' },
    enterprise: { bg: 'rgba(6,182,212,0.15)', text: '#67e8f9', border: 'rgba(6,182,212,0.3)' },
  }

  const tc = tierColors[product.tier]

  const handleAction = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await emitMyceliumEvent('INTENT_ACQUIRE', { product_id: product.id, price: product.price });
    if (product.price !== 'free' && product.price !== 'custom') {
        const result = await processWithEthik({ product_id: product.id, amount: product.price });
        console.log("ETHIK Gateway:", result);
    }
    alert('Intenção registrada no Mycelium Graph. Redirecionando para o Gateway Governado...');
  }

  return (
    <div style={{
      background: 'rgba(18,18,26,0.8)',
      border: `1px solid ${product.featured ? 'rgba(124,58,237,0.4)' : 'rgba(255,255,255,0.07)'}`,
      borderRadius: 16,
      padding: 28,
      display: 'flex',
      flexDirection: 'column',
      gap: 16,
      transition: 'all 0.3s ease',
      position: 'relative',
      backdropFilter: 'blur(8px)',
      cursor: 'pointer',
    }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-4px)'
        ;(e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(124,58,237,0.5)'
        ;(e.currentTarget as HTMLDivElement).style.boxShadow = '0 20px 60px rgba(124,58,237,0.15)'
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'
        ;(e.currentTarget as HTMLDivElement).style.borderColor = product.featured ? 'rgba(124,58,237,0.4)' : 'rgba(255,255,255,0.07)'
        ;(e.currentTarget as HTMLDivElement).style.boxShadow = 'none'
      }}
    >
      {product.badge && (
        <div style={{
          position: 'absolute', top: 16, right: 16,
          padding: '3px 10px', borderRadius: 100, fontSize: 11, fontWeight: 700,
          background: tc.bg, color: tc.text, border: `1px solid ${tc.border}`,
          letterSpacing: '0.5px', textTransform: 'uppercase',
        }}>{product.badge}</div>
      )}

      {/* Icon */}
      <div style={{
        width: 52, height: 52, borderRadius: 14,
        background: 'rgba(124,58,237,0.1)',
        border: '1px solid rgba(124,58,237,0.2)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>{product.icon}</div>

      {/* Title */}
      <div>
        <div style={{ fontSize: 17, fontWeight: 700, color: '#f1f5f9', marginBottom: 4, lineHeight: 1.3 }}>{product.title}</div>
        <div style={{ fontSize: 13, color: '#94a3b8', fontWeight: 500 }}>{product.subtitle}</div>
      </div>

      <p style={{ fontSize: 14, color: '#64748b', lineHeight: 1.6, flexGrow: 1 }}>{product.description}</p>

      {/* Tags */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {product.tags.slice(0, 3).map(tag => (
          <span key={tag} style={{
            padding: '3px 10px', borderRadius: 100, fontSize: 11, fontWeight: 500,
            background: 'rgba(255,255,255,0.05)', color: '#64748b',
            border: '1px solid rgba(255,255,255,0.08)',
          }}>{tag}</span>
        ))}
      </div>

      {/* Stats */}
      <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Star size={13} fill="#fbbf24" color="#fbbf24" />
          <span style={{ fontSize: 13, color: '#fbbf24', fontWeight: 600 }}>{product.rating}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Users size={13} color="#64748b" />
          <span style={{ fontSize: 13, color: '#64748b' }}>{product.students.toLocaleString()}</span>
        </div>
      </div>

      {/* Price + CTA */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <div>
          {product.originalPrice && (
            <div style={{ fontSize: 12, color: '#475569', textDecoration: 'line-through', marginBottom: 2 }}>R$ {product.originalPrice}</div>
          )}
          <div style={{
            fontSize: 20, fontWeight: 800, color: product.price === 'free' ? '#6ee7b7' : '#f1f5f9',
            letterSpacing: '-0.5px',
          }}>{priceDisplay}</div>
        </div>
        <button 
          onClick={handleAction}
          style={{
          padding: '9px 18px',
          background: product.price === 'free'
            ? 'rgba(16,185,129,0.15)'
            : 'linear-gradient(135deg, #7c3aed, #5b21b6)',
          border: product.price === 'free' ? '1px solid rgba(16,185,129,0.4)' : 'none',
          borderRadius: 9, color: product.price === 'free' ? '#6ee7b7' : 'white',
          fontSize: 13, fontWeight: 600, cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 6, transition: 'all 0.2s',
        }}>
          {product.price === 'free' ? 'Baixar grátis' : product.price === 'custom' ? 'Falar com time' : 'Adquirir'}
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  )
}

function StatsBar() {
  return (
    <div style={{
      display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 1,
      background: 'rgba(124,58,237,0.1)',
      border: '1px solid rgba(124,58,237,0.15)',
      borderRadius: 16, overflow: 'hidden',
      margin: '64px 0',
    }}>
      {stats.map((stat, i) => (
        <div key={i} style={{
          padding: '28px 24px',
          background: 'rgba(18,18,26,0.9)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
          borderRight: i < stats.length - 1 ? '1px solid rgba(124,58,237,0.1)' : 'none',
        }}>
          <div style={{ color: '#7c3aed' }}>{stat.icon}</div>
          <div style={{ fontSize: 32, fontWeight: 800, color: '#f1f5f9', letterSpacing: '-1px' }}>{stat.value}</div>
          <div style={{ fontSize: 13, color: '#64748b', textAlign: 'center' }}>{stat.label}</div>
        </div>
      ))}
    </div>
  )
}

// ─── Main App ────────────────────────────────────────────────────────────────

function App() {
  const [activeCategory, setActiveCategory] = useState('all')
  const [menuOpen, setMenuOpen] = useState(false)
  const [dynamicProducts, setDynamicProducts] = useState<Product[]>(products)

  useEffect(() => {
    async function loadCourses() {
      // Fetch dynamic courses from Supabase
      const { data, error } = await supabase.from('courses').select('*');
      if (error) console.error('Erro ao buscar cursos no Supabase:', error);
      if (data && data.length > 0) {
        const mapped: Product[] = data.map(c => ({
          id: c.slug || c.id,
          title: c.title,
          subtitle: 'Curso EGOS',
          description: c.description || 'Domine ' + c.title,
          icon: <BookOpen size={28} className="text-violet-400" />,
          price: c.price > 0 ? c.price : 'free',
          tier: c.price > 0 ? 'pro' : 'free',
          category: 'course',
          tags: ['curso'],
          rating: 5.0,
          students: 0,
          badge: 'DB Fetch'
        }))
        // Prepend dynamic DB products to the catalog safely
        setDynamicProducts(prev => {
           const existingIds = new Set(prev.map(p => p.id));
           const newProducts = mapped.filter(p => !existingIds.has(p.id));
           return [...newProducts, ...prev];
        });
      }
    }
    loadCourses();
  }, [])

  const filtered = activeCategory === 'all'
    ? dynamicProducts
    : dynamicProducts.filter(p => p.category === activeCategory)

  const featured = dynamicProducts.filter(p => p.featured)

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0f' }}>
      <Navbar menuOpen={menuOpen} setMenuOpen={setMenuOpen} />

      {/* ── Hero ── */}
      <section style={{
        paddingTop: 140, paddingBottom: 80, textAlign: 'center',
        background: 'radial-gradient(ellipse 80% 50% at 50% -5%, rgba(124,58,237,0.22), transparent)',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Background grid */}
        <div style={{
          position: 'absolute', inset: 0, opacity: 0.03,
          backgroundImage: 'linear-gradient(rgba(124,58,237,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.5) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
          pointerEvents: 'none',
        }} />

        <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px', position: 'relative' }}>
          <HeroBadge text="Plataforma de produtos governados por IA" />

          <h1 style={{
            fontSize: 'clamp(36px, 6vw, 68px)', fontWeight: 900, lineHeight: 1.08,
            letterSpacing: '-2px', color: '#f1f5f9', marginBottom: 24,
          }}>
            O marketplace onde{' '}
            <span style={{
              background: 'linear-gradient(135deg, #a78bfa, #06b6d4)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
            }}>agentes entregam</span>
            <br />o que humanos precisam
          </h1>

          <p style={{ fontSize: 18, color: '#94a3b8', lineHeight: 1.7, marginBottom: 40, maxWidth: 580, margin: '0 auto 40px' }}>
            Cursos, ferramentas, templates e agentes de IA — tudo com governança real,
            entrega automatizada e human in the loop onde importa.
          </p>

          <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button style={{
              padding: '14px 32px',
              background: 'linear-gradient(135deg, #7c3aed, #5b21b6)',
              border: 'none', borderRadius: 12, color: 'white', fontSize: 15, fontWeight: 700,
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
              boxShadow: '0 8px 32px rgba(124,58,237,0.4)',
            }}>
              Explorar produtos <ArrowRight size={16} />
            </button>
            <button style={{
              padding: '14px 32px',
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.12)', borderRadius: 12,
              color: '#e2e8f0', fontSize: 15, fontWeight: 600, cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 8,
            }}>
              <Play size={16} /> Ver demo
            </button>
          </div>

          {/* Trust badges */}
          <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 48, flexWrap: 'wrap' }}>
            {[
              { icon: <ShieldCheck size={14} />, text: 'LGPD compliant' },
              { icon: <Zap size={14} />, text: 'Entrega automática' },
              { icon: <Lock size={14} />, text: 'Pagamento seguro' },
              { icon: <Award size={14} />, text: 'Garantia 30 dias' },
            ].map((badge, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#64748b', fontSize: 13 }}>
                <span style={{ color: '#7c3aed' }}>{badge.icon}</span>
                {badge.text}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Stats ── */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
        <StatsBar />
      </div>

      {/* ── Featured ── */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px 80px' }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
            <Star size={18} fill="#fbbf24" color="#fbbf24" />
            <span style={{ fontSize: 13, fontWeight: 600, color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '1px' }}>Destaques</span>
          </div>
          <h2 style={{ fontSize: 'clamp(24px, 3vw, 36px)', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.8px' }}>
            Mais acessados agora
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 24 }}>
          {featured.map(product => <ProductCard key={product.id} product={product} />)}
        </div>
      </section>

      {/* ── How it works ── */}
      <section style={{
        background: 'rgba(124,58,237,0.05)',
        borderTop: '1px solid rgba(124,58,237,0.1)',
        borderBottom: '1px solid rgba(124,58,237,0.1)',
        padding: '80px 24px',
      }}>
        <div style={{ maxWidth: 900, margin: '0 auto', textAlign: 'center' }}>
          <HeroBadge text="Como funciona" />
          <h2 style={{ fontSize: 'clamp(24px, 3vw, 42px)', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-1px', marginBottom: 16 }}>
            Tudo orquestrado por IA
          </h2>
          <p style={{ color: '#94a3b8', fontSize: 16, marginBottom: 60 }}>
            Agentes entregam o produto, o suporte e as atualizações. Você foca nos resultados.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 32 }}>
            {howItWorks.map((step, i) => (
              <div key={i} style={{ textAlign: 'left' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <div style={{
                    width: 40, height: 40, borderRadius: 12,
                    background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                  }}>{step.icon}</div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: '#7c3aed', letterSpacing: '2px' }}>PASSO {step.step}</span>
                </div>
                <h3 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 10 }}>{step.title}</h3>
                <p style={{ fontSize: 14, color: '#64748b', lineHeight: 1.6 }}>{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── All Products ── */}
      <section style={{ maxWidth: 1200, margin: '0 auto', padding: '80px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 32, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h2 style={{ fontSize: 'clamp(24px, 3vw, 36px)', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.8px', marginBottom: 8 }}>
              Todos os produtos
            </h2>
            <p style={{ color: '#64748b', fontSize: 14 }}>{filtered.length} produtos disponíveis</p>
          </div>

          {/* Category filters */}
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {categories.map(cat => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                style={{
                  padding: '8px 16px',
                  background: activeCategory === cat.id ? 'rgba(124,58,237,0.2)' : 'rgba(255,255,255,0.04)',
                  border: activeCategory === cat.id ? '1px solid rgba(124,58,237,0.5)' : '1px solid rgba(255,255,255,0.08)',
                  borderRadius: 100, color: activeCategory === cat.id ? '#a78bfa' : '#64748b',
                  fontSize: 13, fontWeight: 500, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
                  transition: 'all 0.2s',
                }}
              >
                {cat.icon} {cat.label}
                <span style={{
                  padding: '1px 6px', borderRadius: 100, fontSize: 11,
                  background: activeCategory === cat.id ? 'rgba(124,58,237,0.3)' : 'rgba(255,255,255,0.08)',
                  color: activeCategory === cat.id ? '#c4b5fd' : '#475569',
                }}>{cat.count}</span>
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 24 }}>
          {filtered.map(product => <ProductCard key={product.id} product={product} />)}
        </div>
      </section>

      {/* ── CTA Banner ── */}
      <section style={{ padding: '0 24px 100px' }}>
        <div style={{
          maxWidth: 900, margin: '0 auto',
          background: 'linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.1))',
          border: '1px solid rgba(124,58,237,0.3)',
          borderRadius: 24, padding: '60px 48px', textAlign: 'center',
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: -40, right: -40, width: 200, height: 200,
            background: 'radial-gradient(circle, rgba(124,58,237,0.3), transparent)',
            pointerEvents: 'none',
          }} />
          <div style={{ position: 'relative' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🚀</div>
            <h2 style={{ fontSize: 'clamp(24px, 3vw, 38px)', fontWeight: 800, color: '#f1f5f9', letterSpacing: '-1px', marginBottom: 16 }}>
              Construa com IA governada.<br />Do jeito certo desde o início.
            </h2>
            <p style={{ color: '#94a3b8', fontSize: 16, marginBottom: 40, maxWidth: 500, margin: '0 auto 40px' }}>
              Junte-se a centenas de times que já usam o EGOS Commons para entregar produtos de IA que funcionam — com LGPD, ética e rastreabilidade embutidos.
            </p>
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
              <button style={{
                padding: '14px 36px',
                background: 'linear-gradient(135deg, #7c3aed, #5b21b6)',
                border: 'none', borderRadius: 12, color: 'white', fontSize: 15, fontWeight: 700,
                cursor: 'pointer', boxShadow: '0 8px 32px rgba(124,58,237,0.4)',
              }}>
                Começar agora — é grátis
              </button>
              <button style={{
                padding: '14px 32px',
                background: 'transparent',
                border: '1px solid rgba(255,255,255,0.2)', borderRadius: 12,
                color: '#e2e8f0', fontSize: 15, fontWeight: 600, cursor: 'pointer',
              }}>
                Falar com a equipe
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '48px 24px', textAlign: 'center',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 24 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 9,
              background: 'linear-gradient(135deg, #7c3aed, #06b6d4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <Sparkles size={15} color="white" />
            </div>
            <span style={{ fontWeight: 700, color: '#94a3b8', fontSize: 14 }}>commons.egos.ia.br</span>
          </div>
          <p style={{ color: '#374151', fontSize: 13 }}>
            © 2026 EGOS. Todos os direitos reservados.{' '}
            <span style={{ color: '#4b5563' }}>Plataforma orquestrada por agentes de IA com governança real.</span>
          </p>
          <div style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 16 }}>
            {['Termos de uso', 'Privacidade', 'LGPD', 'Contato'].map(item => (
              <a key={item} href="#" style={{ color: '#374151', fontSize: 12, textDecoration: 'none', transition: 'color 0.2s' }}
                onMouseEnter={e => (e.currentTarget.style.color = '#6b7280')}
                onMouseLeave={e => (e.currentTarget.style.color = '#374151')}>{item}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

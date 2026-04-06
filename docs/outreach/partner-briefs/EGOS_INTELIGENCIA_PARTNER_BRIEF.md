# Partner Brief — EGOS Inteligência

> **Produto:** EGOS Inteligência — Plataforma de OSINT e Due Diligence  
> **Status:** Merge 98% completo (documentado, não fisicamente implementado)  
> **Equity Oferecido:** 25-35%  
> **Parceiro Ideal:** Govtech boutique / Due diligence consultoria  
> **Data:** 2026-04-06  
> **SSOT:** docs/business/MONETIZATION_SSOT.md | docs/INTELIGENCIA_TOPOLOGY_REALITY_2026-04-06.md

---

## 🎯 O Problema que Resolvemos

**Investigações corporativas e due diligence no Brasil são lentas, caras e fragmentadas.**

- KYC (Know Your Customer) de grandes empresas: dias de trabalho manual
- PEPs (Pessoas Expostas Politicamente): checagem em múltiplos portais
- Sanções: listas internacionais + brasileiras para verificar
- Sócios e parentesco: relações escondidas em documentos dispersos
- Custo de soluções enterprise (Palantir, Thomson Reuters): $500K+/ano

**Nossa proposta:** Grafo de 77M+ entidades brasileiras + UI sofisticada = Palantir acessível.

---

## 🛠️ O Que Construímos

### Motor de Dados: BR-ACC (Standalone)
- **77M+ entidades** (empresas, pessoas, órgãos)
- **25M+ relacionamentos** (sócios, parentesco, endereços)
- **36 fontes de dados públicas** (Receita Federal, PEP, sanções, licitações)
- **46 ETL pipelines** Python (automáticos, atualizados)
- **Neo4j:** Grafo navegável, consultas em milissegundos

### Interface: EGOS Inteligência (Shell Comercial)
- **Next.js 15:** Frontend moderno, responsivo
- **Visualização de rede:** Cytoscape/D3 para grafos interativos
- **AI Router:** Contexto Neo4j enriquecido para queries em linguagem natural
- **Busca unificada:** Empresas, pessoas, documentos, relações

### Cross-References (Diferencial)
- **Match por CPF/CNPJ:** Identifica mesma pessoa em diferentes casos
- **Match por endereço:** Fuzzy matching de endereços similares
- **Match por telefone:** Ligações entre entidades por contato
- **Timeline:** Cronologia de aparições em investigações

---

## 📊 Prova de Capacidade

### Dados Reais Disponíveis

| Categoria | Volume | Fontes |
|-----------|--------|--------|
| Empresas (CNPJ) | 45M+ | Receita Federal |
| PEPs | 8K+ | Planalto, TCU, CGU |
| Sanções | 25K+ | ONU, OFAC, UE, Interpol |
| Licitações | 12M+ | TCMs, diários oficiais |
| Sócios | 25M+ | Receita Federal |
| Endereços | 40M+ | Múltiplas fontes |

### Query de Exemplo
```cypher
// Encontrar todas as empresas de um sócio
// que aparecem em licitações com valores > R$ 10M
MATCH (p:Pessoa {cpf: "XXX.XXX.XXX-XX"})-[:SOCIO_DE]->(e:Empresa)
MATCH (e)-[:PARTICIPOU]->(l:Licitacao)
WHERE l.valor > 10000000
RETURN e.nome, l.objeto, l.valor, l.data
```

### Tempo de Resposta
- Busca simples: <100ms
- Cross-references: <500ms
- Grafo completo (2° grau): <2s

---

## 🎯 ICP (Ideal Customer Profile)

### Primário
- **Boutiques de due diligence** — 5-50 pessoas, foco em KYC/AML
- **Consultorias govtech** — vendem para órgãos públicos e estatais
- **Investigadores privados** — casos de fraude, recuperação de ativos
- **Compliance officers** — bancos, seguradoras, fundos

### Casos de Uso
1. **Due diligence pré-aquisição:** Mapear sócios ocultos, PEPs, sanções
2. **Investigação de fraude:** Conectar entidades em esquemas complexos
3. **Compliance AML:** Monitorar clientes em listas de sanções
4. **Inteligência competitiva:** Mapear relacionamentos corporativos

---

## 💰 Modelos de Parceria

### Opção A — Co-fundador Equity (recomendado)
- **Equity:** 25-35% do produto
- **Vesting:** 12 meses
- **Sua contribuição:** Clientes piloto, cases de sucesso, refine de ICP
- **Nossa contribuição:** Tech, dados, evolução da plataforma
- **Ideal para:** Boutique de due diligence que quer diferencial tecnológico

### Opção B — Revenue Share por Projeto
- **Split:** 30% do valor do projeto de due diligence
- **Uso da plataforma:** Ilimitado para projetos do parceiro
- **White-label:** Opcional (sua marca na interface)
- **Ideal para:** Consultorias com fluxo constante de KYC

### Opção C — Licenciamento de Dados
- **Modelo:** Acesso à API BR-ACC para seu produto próprio
- **Custo:** Revenue share ou fee mensal
- **Exclusividade:** Por indústria (não compete com mesmo parceiro)
- **Ideal para:** Quem já tem plataforma, precisa só dos dados

---

## 🚀 Próximos Passos Imediatos

### Se você é boutique de due diligence:
1. **Demo:** Acesso ao ambiente de teste (dados anonimizados)
2. **Case piloto:** Um KYC real, nosso suporte técnico incluso
3. **Validação:** Mostre para seu cliente o grafo de relacionamentos
4. **Parceria:** Nota de compromisso, comece a usar em produção

### Se você é consultoria govtech:
1. **Conversa:** Entenda como integrar em licitações que você já participa
2. **Proposta:** Montamos um pacote "Inteligência + Licitação" para seus clientes
3. **Pilot:** Projeto piloto com um órgão público
4. **Escala:** Replicar modelo para outros territórios

---

## 📞 Contato

**Enio Rocha**
- Email: enioxt@gmail.com
- X.com: @anoineim
- Código: github.com/enioxt/egos
- Demo: (aguardando deploy final)

---

**Sacred Code:** 000.111.369.963.1618  
**Topologia:** docs/INTELIGENCIA_TOPOLOGY_REALITY_2026-04-06.md  
**Nota de Compromisso:** docs/legal/NOTA_COMPROMISSO_EQUITY_GTM_TEMPLATE.md


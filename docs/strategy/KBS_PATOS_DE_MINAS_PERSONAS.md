# KB-as-a-Service — 10 Perfis de Patos de Minas, MG

> **Version:** 1.0.0 — 2026-04-08
> **SSOT:** Este arquivo + templates Notion (criados via MCP 2026-04-08)
> **Parent:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md`
> **Cidade-alvo:** Patos de Minas, MG — 155k hab., triângulo mineiro/alto paranaíba, forte produção de soja/milho/pecuária, SENAR, EMATER, múltiplas cooperativas (COMIGO, COOPA)

---

## Critério de seleção dos 10 perfis

Perfis selecionados por:
1. **Volume na cidade** — profissões com alta densidade em Patos de Minas
2. **Dor de knowledge** — atualmente resolvida com "papel+cabeça" ou planilhas caóticas
3. **LGPD relevância** — dados sensíveis → Guard Brasil LGPD agrega valor direto
4. **ROI visível** — cliente consegue medir antes/depois (tempo de resposta, erro evitado)
5. **Acessibilidade ao Claude Pro $20** — profissional já tem cartão internacional ou Wise

---

## Os 10 Perfis

### Perfil 01 — Escritório de Advocacia (Direito Agrário + Civil)
**Densidade:** Alta (Patos tem 3+ OAB-MG núcleos, direito agrário é nicho forte)
**Dor principal:** Jurisprudência espalhada em e-mails, pastas de HD, "lembro que tinha um caso de INCRA assim..."
**Dados típicos:**
- Processos (número, comarca, partes, tipo, status, próximo prazo)
- Jurisprudência (tribunal, data, ementa, área, aplicabilidade)
- Clientes (nome, CPF, tipo de caso, documentos entregues)
- Modelos de petição (tipo, área, last_update, uso_frequente)
- Prazos e audiências (data, processo, ação_necessária, status)

**Guard Brasil:** CPF/CNPJ dos clientes, dados de processos → auto-redação antes de indexar
**ROI demo:** "Qual o prazo máximo para contestar uma ação de usucapião em Minas?" → resposta com citação de jurisprudência específica em 10s vs 2h de pesquisa manual
**Setor LGPD sensível:** Dados de clientes (art. 5, inc. II LGPD — dados pessoais de identificação)

---

### Perfil 02 — Agrônomo / Técnico Agrícola Independente
**Densidade:** Muito alta (Patos tem EMATER, SENAR, CREA-MG regional, 100+ profissionais)
**Dor principal:** "Tenho 40 propriedades atendidas, cada uma com solo diferente, cultura diferente — não lembro o que recomendei no ano passado"
**Dados típicos:**
- Propriedades (nome, município, hectares, coordenadas, solo_tipo, cultura_atual)
- Análises de solo (data, propriedade, N/P/K/pH/matéria_orgânica, recomendação)
- ARTs emitidas (número_ART, CREA, propriedade, serviço, data, valor)
- Defensivos aprovados (princípio_ativo, cultura_alvo, carência, registro_MAPA)
- Visitas técnicas (data, propriedade, problema_relatado, recomendação, follow_up)
- Normas ABNT/MAPA (código, título, validade, aplicação)

**Guard Brasil:** Dados do produtor rural (CPF/CNPJ do cliente), coordenadas GPS
**ROI demo:** "Qual foi a recomendação de adubação para a fazenda São João em março?" → resposta imediata vs buscar e-mail enviado há 8 meses
**Diferencial:** Base de dados de defensivos aprovados por cultura = evita erro técnico grave

---

### Perfil 03 — Veterinário (Clínica Pet + Atendimento Rural)
**Densidade:** Alta (mercado pet crescendo + pecuária forte)
**Dor principal:** "Tenho fichas de 500 pacientes, vacinas vencidas, protocolos na cabeça"
**Dados típicos:**
- Pacientes (nome, espécie/raça, tutor_CPF, data_nascimento, peso, histórico_vacinação)
- Protocolos clínicos (espécie, condição, tratamento_padrão, dosagem_kg, referência)
- Medicamentos (princípio_ativo, apresentação, dose_espécie, carência_abate, MAPA)
- Campanhas de vacinação (data, local, vacinas_disponíveis, animais_vacinados)
- Notificações MAPA (doença, animais_afetados, ação_tomada, status_notificação)
- Animais rurais por propriedade (espécie, quantidade, último_manejo, sanidade)

**Guard Brasil:** CPF do tutor, dados de saúde animal relacionados a consumo humano
**ROI demo:** "Qual a dose de Ivermectina para bovino de 450kg antes do abate e qual a carência?" → resposta em 5s com referência MAPA vs consultar bula
**Diferencial:** Compliance MAPA automático — evita embargo de lote por carência ignorada

---

### Perfil 04 — Médico / Clínica Médica (Clínica Geral + Especialidades)
**Densidade:** Alta (Patos tem hospital regional, UPA, clínicas privadas)
**Dor principal:** "Protocolo de conduta para dengue hemorrágica — cadê o que o MS atualizou?"
**Dados típicos:**
- Protocolos clínicos (condição, classificação, conduta_inicial, critério_internação, fonte_MS)
- Medicamentos (princípio_ativo, dose_adulto, dose_pediátrica, contraindicações, interações)
- Regulação ANS (procedimento, código_TUSS, cobertura_obrigatória, prazo_autorização)
- Legislação CFM (resolução, tema, aplicação, data_vigência)
- Casos educativos (condição, apresentação_clínica, diagnóstico_diferencial, conduta, resultado)
- Orientações para pacientes (condição, linguagem_simples, quando_voltar, sinais_alarme)

**Guard Brasil:** Dados de saúde dos pacientes (dado sensível art. 5, II, LGPD) — Guard Brasil obrigatório
**ROI demo:** "Qual o protocolo atual do MS para sepse em adulto?" → resposta citada em 10s
**LGPD crítico:** Dado de saúde = dado sensível, exige consentimento explícito e proteção extra

---

### Perfil 05 — Contador Especializado em Produtor Rural
**Densidade:** Alta (Patos tem muitos pequenos/médios produtores que precisam de contabilidade rural)
**Dor principal:** "ITR, Funrural, Bloco K, LALUR rural — cada cliente tem uma situação diferente"
**Dados típicos:**
- Clientes (nome, CPF/CNPJ, tipo_produtor, regime_tributário, módulos_fiscais)
- Legislação tributária rural (tributo, alíquota, base_cálculo, vigência, IN_RFB)
- Obrigações por mês (cliente, obrigação, prazo, status, valor_estimado)
- Custo de produção por cultura (soja/milho/café, safra, custo_fixo, custo_variável, ponto_equilíbrio)
- Incentivos fiscais (programa, requisito, benefício, prazo_adesão, fonte)
- Exportações/CNPJ (RADAR, NF-e rural, DANFE, SPED, e-Social rural)

**Guard Brasil:** CPF/CNPJ de todos os clientes, dados fiscais sensíveis
**ROI demo:** "Meu cliente tem 120 hectares de soja no Cerrado, simples nacional, qual alíquota de Funrural e tem exceção para exportação?" → resposta precisa vs 30min de pesquisa
**Diferencial:** Base legislativa tributária rural → evita multa por erro

---

### Perfil 06 — Engenheiro Civil / de Segurança do Trabalho
**Densidade:** Média-alta (construção e agronegócio geram demanda constante)
**Dor principal:** "Qual a norma ABNT de fundação para terreno argiloso, quais as tolerâncias?"
**Dados típicos:**
- Normas técnicas (código_ABNT, título, versão, resumo, aplicação, link_acesso)
- ARTs emitidas (número, CREA, obra, tipo_serviço, valor_obra, data, status)
- Projetos (nome, cliente, tipo, município, ART, status, prazo_entrega)
- NRs Segurança (número_NR, tema, obrigação_resumo, data_publicação, penalidade)
- Materiais e especificações (material, norma_aplicável, fck/resistência, fornecedores_local)
- Orçamentos referência (SINAPI, data_referência, item, custo_unitário, BDI)

**Guard Brasil:** CPF/CNPJ de clientes em projetos
**ROI demo:** "ABNT NBR 6118:2014 — qual a cobertura mínima de armadura para estruturas em ambiente agressivo classe III?" → resposta em segundos vs abrir PDF de 280 páginas
**Diferencial:** SINAPI indexado = orçamentos rápidos e defensáveis

---

### Perfil 07 — Consultor de Gestão Rural / Agribusiness
**Densidade:** Média e crescendo (fazendas maiores buscando profissionalização)
**Dor principal:** "Tenho 15 clientes, cada um tem um benchmark diferente — não consigo comparar e dar insights rápidos"
**Dados típicos:**
- Propriedades clientes (fazenda, hectares, cultura, produtividade_média, custo_produção)
- Preços de commodities (produto, data, Bolsa_Chicago/CBOT, Esalq, paridade_local)
- Benchmarks regionais (cultura, Alto_Paranaíba, produtividade_média, custo_médio, safra)
- Insumos e fornecedores (produto, marca, fornecedor_Patos, preço_kg/L, validade_cotação)
- Contratos de venda (cliente, cultura, volume_ton, preço_contratado, data_entrega, cooperativa)
- Relatórios de safra (cliente, cultura, safra, área_plantada, produção_real, receita, margem)

**Guard Brasil:** Dados financeiros dos produtores
**ROI demo:** "Compare o custo de produção de soja do cliente A com o benchmark do Alto Paranaíba 2025" → gráfico + análise em 30s
**Diferencial:** Indexação de preços históricos locais (COMIGO/COOPA) = comparativo real de margem

---

### Perfil 08 — Imobiliária Rural / Corretor de Imóveis Rurais
**Densidade:** Média (terras rurais em Patos valem muito — corrida por área pós-pandemia)
**Dor principal:** "Tenho 30 fazendas para vender, cada uma com documentação diferente, CAR, CCIR, INCRA — preciso responder rápido"
**Dados típicos:**
- Propriedades (matrícula, município, hectares, módulos_fiscais, CAR, CCIR, ITR_pago)
- Situação fundiária (embargos_IBAMA, sobreposição_UC, APP_ha, RL_ha, passivo_ambiental)
- Histórico de transações (fazenda, comprador, vendedor, valor_ha, data, cartório)
- Laudos e laudêmio (tipo_laudo, data, valor_laudo, responsável_CREA/CAU)
- INCRA regulação (módulo_fiscal_município, ITR_base, registro_SNCR, CAR_status)
- Cotações de terra (microrregião, tipo_solo, valor_mínimo_máximo_ha, data)

**Guard Brasil:** CPF/CNPJ de compradores e vendedores em transações fundiárias
**ROI demo:** "A fazenda São Pedro tem CAR regularizado? Qual o passivo ambiental?" → resposta imediata vs ligar para INCRA
**Diferencial:** Base de valores de terra regionalizada = estimativa rápida de preço justo

---

### Perfil 09 — SENAR / SENAI / Escola Técnica Agrícola
**Densidade:** Média (SENAR tem unidade em Patos, SENAI Uberaba cobre região, CEFET local)
**Dor principal:** "Tenho 12 instrutores, 40 cursos diferentes, material didático espalhado em pen-drive"
**Dados típicos:**
- Cursos oferecidos (código, nome, carga_horária, público_alvo, pré-requisito, material_didático)
- Competências por curso (competência, indicadores, métodos_avaliação, instrumentos)
- Legislação educacional (LDB, DCNs, BNCC, normativas_SENAR, vigência)
- Experimentos de campo (cultura, safra, tratamento, parcela, resultado, conclusão)
- Alunos/turmas (turma, instrutor, período, inscritos, concluintes, avaliação_média)
- Recursos didáticos (tipo, título, curso_aplicado, link, ultima_revisão)

**Guard Brasil:** Dados de alunos (CPF, notas, dados de saúde em cursos de segurança)
**ROI demo:** "Quais são as competências obrigatórias do curso de Operador de Máquinas Agrícolas nível básico?" → resposta com indicadores vs buscar no pen-drive do coordenador
**Diferencial:** Material didático indexado = instrutor novo treinado em 1 dia em vez de 1 semana

---

### Perfil 10 — Cooperativa / Associação de Produtores Rurais
**Densidade:** Alta (COMIGO, COOPA, COOPERPATOS + associações municipais)
**Dor principal:** "Temos 800 cooperados, cada um com realidade diferente — como responder perguntas sobre preço, insumos, prazo rápido?"
**Dados típicos:**
- Cooperados (nome, CPF/CNPJ, município, culturas, área_ha, capacidade_armazenagem)
- Cotas e capital social (cooperado, cota_capital, integralização, dividendo_último)
- Preços praticados (produto, data, preço_compra, preço_venda, origem, safra)
- Insumos disponíveis (produto, categoria, estoque_kg/L, preço_cooperado, prazo_pagamento)
- CONAB regulações (programa, requisito, volume_mínimo, prazo_entrega, preço_referência)
- Receitas de safra (cooperado, cultura, volume_entregue, preço_médio, receita_bruta, desconto_coop)

**Guard Brasil:** CPF/CNPJ de centenas de cooperados, dados financeiros coletivos
**ROI demo:** "Qual o preço de soja praticado na cooperativa para entrega em 60 dias?" → funcionário responde em 5s vs buscar no sistema legado
**Diferencial:** Base de CONAB + políticas públicas = assessoria a cooperados sobre programas de governo

---

## Resumo de priorização para venda

| # | Perfil | Densidade PM | Urgência KB | Guard LGPD | Ticket Estimado | **Score** |
|---|--------|-------------|-------------|------------|-----------------|-----------|
| 1 | Agrônomo/Técnico Agrícola | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | R$3-5k | **🥇 P0** |
| 2 | Escritório Advocacia | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | R$3-5k | **🥇 P0** |
| 3 | Contador Rural | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | R$3-5k | **🥇 P0** |
| 4 | Consultor Gestão Rural | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | R$5-10k | **🥈 P1** |
| 5 | Veterinário | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | R$1.5-3k | **🥈 P1** |
| 6 | Engenheiro Civil | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | R$3-5k | **🥈 P1** |
| 7 | Médico/Clínica | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | R$3-8k | **🥈 P1** |
| 8 | Cooperativa | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | R$15-50k | **🥉 P2** |
| 9 | Imobiliária Rural | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | R$3-5k | **🥉 P2** |
| 10 | SENAR/Escola Técnica | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | R$5-15k | **🥉 P2** |

**Top 3 para fechar primeiro:** Agrônomo, Advogado, Contador Rural — todos têm:
- Alta densidade em Patos de Minas
- Dor clara e mensurável
- Disposição a pagar por ferramenta profissional
- Recomendação entre pares (um agrônomo fala com 10 outros na EMATER)

---

## Template base (configurável por perfil)

Todos os 10 perfis recebem o mesmo **scaffold base**, customizado na camada de dados:

```
EGOS Knowledge — [Nome do Perfil]
├── 📋 CLAUDE.md                    ← schema do AI (regras, tom, contexto setorial)
├── .guarani/
│   └── kbs-[setor]-rules.md       ← limites específicos do setor
├── raw/                            ← documentos brutos (PDFs, planilhas, e-mails)
│   ├── normas/
│   ├── clientes/
│   └── referencias/
├── wiki/                           ← compilado pelo wiki-compiler
│   ├── conceitos/
│   ├── procedimentos/
│   └── index.md
└── notion-workspace/               ← interface do cliente
    ├── DB: Documentos
    ├── DB: Q&A / Consultas
    ├── DB: [Principal do setor]    ← e.g. "Processos" para advocacia
    ├── DB: Normas & Compliance
    └── Página: Como Usar (PT-BR)
```

---

## Dados de demonstração (por perfil)

Para cada perfil, criamos **10–20 registros fictícios mas realistas** que simulam um profissional de Patos de Minas:
- Nomes de fazendas reais da região (São João, Boa Vista, Vereda do Rio)
- Municípios vizinhos reais (Carmo do Paranaíba, Rio Paranaíba, Lagoa Formosa, Presidente Olegário)
- Normas reais (ABNT NBR 6118, NR-31, IN MAPA 14/2020)
- Referências de cooperativas locais (COMIGO, COOPA)

---

*Próxima ação: criar templates Notion via MCP para os 3 perfis P0 (KBS-PM-001..003)*

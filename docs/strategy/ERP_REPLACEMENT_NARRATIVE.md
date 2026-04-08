# O ERP Virou Gaveta — Sua Inteligência Fica com a EGOS

> **Versão:** 1.0.0 — 2026-04-08  
> **SSOT:** Este arquivo  
> **Destino:** Landing page, demos presenciais, DMs para donos de empresa, pitch para FORJA  

---

## O Problema Real

O seu ERP registra. Mas não responde.

Você abre o sistema, clica em vinte menus, exporta uma planilha, procura na coluna errada, fecha, abre o e-mail antigo, pergunta para o Geraldo — e 40 minutos depois você tem a resposta que precisava.

**Isso acontece todo dia.** Com orçamentos, com notas fiscais, com fichas técnicas, com contratos, com atas de reunião, com laudos, com normas.

O ERP não foi feito para responder perguntas. Foi feito para guardar dados.

---

## O que a EGOS faz

A EGOS não substitui o seu ERP. Ela senta **por cima** dele.

```
Seus documentos (ERP, PDF, Word, Excel, áudio, vídeo)
              ↓
    EGOS Knowledge (atomiza tudo)
              ↓
  Você pergunta em português natural
              ↓
    Resposta em segundos — com a fonte citada
```

**Exemplo real (FORJA):**
> *"Qual o custo médio da bucha BC-007 nos últimos 6 meses, considerando a alta do aço de fevereiro?"*

Antes da EGOS: Geraldo para o que está fazendo, abre planilha Excel 2023, 2024, 2025, cruza com nota fiscal, calcula na mão. **45 minutos.**

Com a EGOS: você digita a pergunta. **8 segundos.** Com as fontes.

---

## O que pode ser ingerido

Qualquer coisa que tem conhecimento dentro:

| Tipo | Exemplo | Como ingerir |
|------|---------|--------------|
| PDF | Orçamento, contrato, laudo técnico, ABNT | Arrastar para pasta `/raw` → `/ingest` |
| DOCX/Excel | Planilha de custo, ficha técnica, proposta | Arrastar → `/ingest` |
| Áudio (MP3/WAV) | Gravação de reunião, negociação telefônica | `/ingest --audio reuniao.mp3` (Whisper transcreve) |
| Vídeo (MP4) | Vistoria de peça, treinamento, inspeção | `/ingest --video vistoria.mp4` |
| E-mail exportado | Histórico de pedido, reclamação de cliente | Exportar como .eml → `/ingest` |
| Dados do ERP | Exportação CSV/Excel do sistema | `/ingest --sheet custos-2024.xlsx` |

---

## Por que não é "ChatGPT com meus documentos"

Há dezenas de ferramentas que prometem isso. O que a EGOS entrega diferente:

**1. Citação obrigatória**  
Toda resposta vem com a fonte exata: "segundo o Orçamento ORC-2024-087, página 3, seção custos de matéria-prima". Sem alucinação. Sem invenção.

**2. LGPD desde o dia 1**  
O Guard Brasil verifica automaticamente se algum dado sensível (CPF de cliente, dados bancários, informação de saúde) está sendo indexado sem proteção. Audit trail completo. Você tem evidência de compliance.

**3. Governança de conhecimento**  
O sistema avisa quando um documento ficou desatualizado, quando há contradições entre fontes, quando uma norma técnica foi revisada. Seu conhecimento não apodrece.

**4. Roda no seu computador**  
Os dados ficam no **seu Notion** e no **seu computador**. Não passam por servidor nosso. Não alimentam modelos de terceiros. Você é dono.

**5. Custa R$110/mês**  
Claude Pro ($20/mês) + Notion (grátis até 1.000 blocos). EGOS cobra pelo setup e manutenção — não pelo uso. Sem surpresa na fatura.

---

## Para quem é isso agora (Patos de Minas)

### 🏭 Metalúrgica / Fundição / Tornearia
**ROI imediato:** orçamentos que demoram 2h passam a demorar 10 minutos.  
**Dados ingeridos:** fichas técnicas de peças, histórico de custos, normas ABNT, gravações de reunião de produção.  
**Pergunta-demo:** *"Qual peça teve maior variação de custo real vs. orçado no primeiro trimestre?"*

### 🌾 Agrônomo / Técnico Agrícola
**ROI imediato:** consulta de defensivos aprovados por cultura + carência em segundos.  
**Dados ingeridos:** ARTs emitidas, análises de solo, visitas técnicas, bulas de defensivos, laudos MAPA.  
**Pergunta-demo:** *"Qual o último resultado de pH da Fazenda Cerradão e o que foi recomendado?"*

### ⚖️ Escritório de Advocacia
**ROI imediato:** jurisprudência relevante encontrada em 10 segundos em vez de 30 minutos.  
**Dados ingeridos:** petições anteriores, acórdãos, contratos de clientes, prazos processuais.  
**Pergunta-demo:** *"Qual jurisprudência do STJ favorece o arrendatário no processo 0033221?"*

### 💰 Contador Rural
**ROI imediato:** legislação tributária rural consultada com citação — sem risco de erro de memória.  
**Dados ingeridos:** IN RFB, legislação ITR/Funrural, dados de clientes, obrigações mensais.  
**Pergunta-demo:** *"Quais clientes têm obrigação vencendo nos próximos 15 dias?"*

---

## O que NÃO muda

- O ERP continua registrando os dados operacionais
- Os documentos físicos continuam onde estão
- A equipe não precisa aprender nenhum sistema novo
- Nenhuma migração de dados

**A EGOS é uma camada de inteligência. Não uma substituição.**

---

## Como funciona o setup (2 horas)

1. **Chamada de diagnóstico (30min)** — entender quais documentos têm mais valor, quem vai usar, quais perguntas precisam ser respondidas.

2. **Setup técnico remoto (1h)** —
   - Criar workspace Notion do setor
   - Instalar Claude Code no computador do responsável
   - Conectar Notion MCP (OAuth automático)
   - Ingerir primeiros 10-20 documentos reais

3. **Primeira consulta real (15min)** — mostrar o sistema respondendo com a **própria documentação do cliente**.

4. **Treinamento (15min)** — ensinar os 3 comandos principais: `/ask`, `/ingest`, `/lint`.

---

## Tiers de investimento

| Tier | Para quem | Setup | Manutenção |
|------|-----------|-------|------------|
| **Starter** | Profissional autônomo (1 usuário) | R$ 1.500 | R$ 200/mês |
| **Pro** | PME até 5 usuários, 100 docs iniciais | R$ 5.000 | R$ 800/mês |
| **Enterprise** | Indústria, multi-usuário, integração ERP | R$ 15k–50k | R$ 2.500–5k/mês |

> **Não incluso no preço:** Claude Pro do cliente ($20/mês = ~R$110) e Notion (grátis ou R$40/mês).
> O cliente paga diretamente à Anthropic. Sem repasse por nossa parte.

---

## Pergunta frequente: "E o meu ERP vai virar inútil?"

Não. O ERP é excelente para o que ele faz: **registro estruturado, faturamento, fiscal, controle de estoque**.

A EGOS resolve o que o ERP nunca vai resolver: **consulta em linguagem natural sobre o conhecimento acumulado da empresa** — incluindo o que está em documentos, gravações, e-mails e na cabeça das pessoas.

ERP = banco de dados. EGOS = o funcionário que leu tudo e lembra de tudo.

---

## Próximo passo

Demo ao vivo de 30 minutos com seus próprios dados.

**Enio Rocha** — [egos.ia.br](https://egos.ia.br) | WhatsApp/Telegram: Patos de Minas, MG

*"Traga 5 documentos seus para a demo. A gente responde a primeira pergunta real na frente de você."*

---

*Fim do documento. Versão PT-BR. Revisão: a cada lançamento de produto ou mudança de pricing.*

# KBS Entity Schema — Delegacia / Segurança Pública

> **Version:** 1.0.0 | **Data:** 2026-04-12
> **Propósito:** Schema canônico de entidades para implementação do KBS em delegacias e órgãos de segurança pública.
> **SSOT:** Este arquivo. Base para KBS-036 (validação DHPP) e futuros clientes de segurança.
> **Referência:** `docs/strategy/KBS_ENTITY_SCHEMA_EGOS.md` para o padrão base.

---

## Contexto

Uma delegacia produz e consome dados altamente estruturados: boletins de ocorrência, inquéritos, mandados, laudos, relatórios de inteligência. O desafio não é ter dados — é **achar o que se precisa** quando se precisa. Um investigador perde horas procurando:

- Todas as ocorrências envolvendo uma placa específica
- Histórico completo de um suspeito (ocorrências, mandados, associados)
- Padrão de atuação de uma organização criminosa (horários, locais, modus operandi)
- Vinculações entre suspeitos de casos diferentes

O KBS v2 com entity graph resolve isso: cada entidade é uma ficha viva, cada relacionamento é uma conexão automática.

---

## Entidades Delegacia

### 1. Pessoa

**O que é:** Qualquer indivíduo relevante para investigação — suspeito, vítima, testemunha, policial.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `nome_completo` | string | `João Silva Santos` | Dado pessoal |
| `cpf` | string | `***.456.789-**` (mascarado externo) | Dado sensível |
| `rg` | string | — | Dado pessoal |
| `data_nascimento` | date | `1985-03-15` | Dado pessoal |
| `genero` | string | — | Dado pessoal |
| `naturalidade` | string | `Patos de Minas/MG` | — |
| `alcunha` | string | `Zé do Bico` | Dado policial |
| `telefone` | string[] | — | Dado pessoal |
| `endereco_atual` | string | — | Dado sensível |
| `papel` | enum | `suspeito \| vitima \| testemunha \| investigador \| perito` | — |
| `situacao` | enum | `foragido \| preso \| solto \| falecido` | — |
| `bnmp_mandados` | int | `2` | — (cruzamento BNMP) |
| `antecedentes` | boolean | — | Dado policial |
| `foto_id` | string | URL ou hash | Biométrico |

**Relacionamentos:**
- `INVESTIGADO_EM → Caso` (1:N — aparece em quais casos)
- `ASSOCIADO_A → Pessoa` (N:M — associados/parceiros conhecidos)
- `RESIDE_EM → Local` (N:1)
- `POSSUI → Veiculo` (N:M)
- `INTEGRANTE_DE → Organizacao` (N:M)
- `VITIMA_DE → Evento` (N:M)
- `AUTOR_DE → Evento` (N:M)
- `POSSUI_MANDADO → Mandado` (1:N)

**Fontes de extração:**
- BOs digitais (PDF → OCR → NER)
- Planilhas de triagem (XLSX → CSV → parser)
- BNMP (API cruzamento de mandados)
- Datajud (processos CNJ)

---

### 2. Veículo

**O que é:** Veículo associado a casos, suspeitos ou eventos.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `placa` | string | `ABC-1234` ou `ABC1D23` (Mercosul) | Dado pessoal indiretamente |
| `renavam` | string | — | Dado pessoal |
| `tipo` | enum | `carro \| moto \| caminhao \| van \| barco` | — |
| `marca_modelo` | string | `Honda CG 160 Fan` | — |
| `cor` | string | `prata` | — |
| `ano` | int | `2019` | — |
| `situacao` | enum | `regular \| roubado \| furtado \| clonado \| apreendido` | — |
| `proprietario_cpf` | string | — | Dado pessoal |
| `uf_registro` | string | `MG` | — |

**Relacionamentos:**
- `UTILIZADO_EM → Evento` (N:M — veículo usado no crime)
- `ASSOCIADO_A → Pessoa` (N:M — proprietário, condutor habitual)
- `APREENDIDO_EM → Caso` (N:1)

---

### 3. Caso

**O que é:** Inquérito policial, boletim de ocorrência, ou processo investigativo.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `numero_bo` | string | `0012/2026` | — |
| `numero_inquerito` | string | `001.2026.000123-4` | — |
| `numero_cnj` | string | — | — (Datajud) |
| `tipo` | enum | `roubo \| furto \| homicidio \| trafico \| estelionato \| lesao` | — |
| `data_ocorrencia` | date | `2026-03-15` | — |
| `data_abertura` | date | — | — |
| `status` | enum | `aberto \| arquivado \| indiciado \| em_julgamento \| encerrado` | — |
| `delegado_responsavel` | string | — | — |
| `comarca` | string | `Patos de Minas/MG` | — |
| `descricao` | text | — | — |
| `natureza_principal` | string | Código REDS / MASP | — |

**Relacionamentos:**
- `ENVOLVE → Pessoa` (N:M — vítimas, suspeitos, testemunhas)
- `OCORREU_EM → Local` (N:1)
- `COMPOSTO_DE → Evento` (1:N — fatos que compõem o caso)
- `UTILIZA → Veiculo` (N:M)
- `LIGADO_A → Caso` (N:M — casos conexos)
- `INVESTIGADO_POR → Pessoa` (N:1 — investigador responsável)
- `RESULTA_EM → Mandado` (1:N)

---

### 4. Local

**O que é:** Lugar georreferenciado relevante para a investigação.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `endereco` | string | `Rua das Flores, 123 — Centro, Patos de Minas` | Pode ser dado pessoal |
| `cep` | string | `38700-000` | — |
| `coordenadas` | string | `-18.5802, -46.5181` | — |
| `tipo` | enum | `residencia \| comercio \| via_publica \| rural \| abandono` | — |
| `bairro` | string | — | — |
| `municipio` | string | `Patos de Minas` | — |
| `uf` | string | `MG` | — |
| `relevancia` | enum | `cena_crime \| residencia_suspeito \| ponto_trafico \| refugio` | — |

**Relacionamentos:**
- `LOCAL_DE → Evento` (1:N)
- `VINCULADO_A → Pessoa` (N:M — residência, local de trabalho)
- `PROXIMOS → Local` (N:M — vizinhança / raio de ação)

---

### 5. Evento

**O que é:** Fato específico ocorrido em data/hora/local determinados.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `tipo` | enum | `disparo_arma \| perseguicao \| prisao \| abordagem \| furto \| agressao` | — |
| `data_hora` | datetime | `2026-03-15T22:30:00-03:00` | — |
| `descricao` | text | — | — |
| `fonte` | string | `BO 0012/2026` | — |
| `confirmado` | boolean | `true` | — |
| `gravidade` | enum | `leve \| grave \| morte` | — |

**Relacionamentos:**
- `OCORRE_EM → Local` (N:1)
- `ENVOLVE → Pessoa` (N:M — autor/vítima/testemunha)
- `UTILIZA → Veiculo` (N:M)
- `UTILIZA → Arma` (N:M)
- `PARTE_DE → Caso` (N:1)
- `PRECEDE → Evento` (N:M — sequência temporal)

---

### 6. Organização

**O que é:** Grupo criminoso, empresa usada para lavagem, ou organização de interesse.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `nome` | string | — | — |
| `alcunha` | string | `Quadrilha do Norte` | Dado policial |
| `cnpj` | string | — | Dado público |
| `tipo` | enum | `empresa \| grupo_criminoso \| milicia \| trafico \| fraude` | — |
| `atuacao` | string[] | `['roubo_cargas', 'trafico']` | — |
| `territorio` | string[] | `['Centro', 'Bairro X']` | — |
| `status` | enum | `ativa \| desarticulada \| sob_investigacao` | — |

**Relacionamentos:**
- `INTEGRA → Pessoa` (1:N)
- `LIDERA → Pessoa` (1:N — liderança identificada)
- `OPERA_EM → Local` (N:M)
- `LIGADA_A → Organizacao` (N:M — facções/alianças)
- `INVESTIGADA_EM → Caso` (N:M)

---

### 7. Arma

**O que é:** Arma de fogo, branca ou objeto usado como arma.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `tipo` | enum | `fogo \| branca \| improvisada` | — |
| `calibre` | string | `9mm \| .40 \| 12` | — |
| `marca_modelo` | string | `Taurus G2C` | — |
| `numero_serie` | string | — | — |
| `situacao` | enum | `apreendida \| circulando \| destruida \| desaparecida` | — |
| `registro_sigma` | string | — | — (SIGMA/SINARM) |
| `proprietario_cpf` | string | — | Dado pessoal |

**Relacionamentos:**
- `UTILIZADA_EM → Evento` (N:M)
- `APREENDIDA_EM → Caso` (N:1)
- `ASSOCIADA_A → Pessoa` (N:M)

---

### 8. Mandado

**O que é:** Mandado de prisão (BNMP), busca e apreensão, ou outro mandado judicial.

| Atributo | Tipo | Exemplo | LGPD |
|----------|------|---------|------|
| `numero_bnmp` | string | — | — |
| `tipo` | enum | `prisao \| busca_apreensao \| conducao_coercitiva` | — |
| `status` | enum | `ativo \| cumprido \| expirado \| revogado` | — |
| `data_expedicao` | date | — | — |
| `data_validade` | date | — | — |
| `comarca_origem` | string | — | — |
| `crime` | string | — | — |
| `vara` | string | — | — |

**Relacionamentos:**
- `EXPEDIDO_CONTRA → Pessoa` (N:1)
- `ORIGINADO_EM → Caso` (N:1)
- `CUMPRIDO_EM → Evento` (1:N)

---

## Diagrama de Relacionamentos

```
Pessoa ──INVESTIGADO_EM──> Caso ──COMPOSTO_DE──> Evento ──OCORRE_EM──> Local
  │                          │                      │
  ASSOCIADO_A                ENVOLVE                UTILIZA
  │                          │                      │
Pessoa                     Pessoa                 Veiculo / Arma
  │
  INTEGRANTE_DE
  │
Organizacao ──OPERA_EM──> Local
  │
  INVESTIGADA_EM
  │
Caso ──RESULTA_EM──> Mandado ──EXPEDIDO_CONTRA──> Pessoa
```

---

## Fontes de Dados e Extração

| Entidade | Fontes primárias | Extração |
|----------|-----------------|---------|
| Pessoa | BO PDF, BNMP API, Datajud | BERTimbau NER + OCR |
| Veículo | BO PDF, planilhas DEPATRAN | regex placa + NER |
| Caso | BO digital, sistema REDS/MASP | parser estruturado |
| Local | BO texto, endereços IBGE | NER + geocoding |
| Evento | BO narrativa | NER temporal + eventos |
| Organização | Relatos de investigadores | NER manual + regex |
| Arma | BO PDF, SIGMA | regex + NER |
| Mandado | BNMP API | API estruturada |

---

## LGPD — Classificação dos Dados

| Categoria | Tratamento |
|-----------|-----------|
| Dados pessoais (CPF, RG, nome) | Armazenado sem máscara para operadores autorizados. Guard Brasil audita acessos. |
| Dados sensíveis (biometria, saúde) | Armazenado com aviso Guard Brasil + audit trail obrigatório. |
| Dados públicos (BNMP, CNPJ) | Sem restrição de acesso interno. |
| Exportação externa | Guard Brasil mascara automaticamente antes de qualquer envio. |

**Nota:** O delegado e investigadores VEEM os dados completos — esse é o trabalho deles. O sistema registra QUEM acessou O QUE e QUANDO (audit trail LGPD Art. 37). Mascaramento só ocorre em exportações externas.

Ver: `packages/guard-brasil/src/lib/evidence-chain.ts` — provenance SHA-256 para LGPD Art. 37.

---

## Relatório de Inteligência Semanal — Delegacia

Template de relatório gerado automaticamente (KBS-031 adaptado):

1. **Casos abertos há mais de 30 dias sem atualização** — aging alert
2. **Pessoas com mandados ativos identificadas em novos BOs** — cruzamento BNMP
3. **Veículos com status "roubado/furtado" vistos em novos eventos** — alerta automático
4. **Cluster geográfico de eventos** — concentração em bairros/horários
5. **Novas associações entre suspeitos** — grafo de relacionamentos expandido
6. **Casos sem indiciamento após 30 dias de inquérito** — alerta de prescrição

---

*Primeiro cliente planejado: DHPP Patos de Minas / BH (KBS-036 — validação com Enio).*
*Schema é ponto de partida — refinamento acontece no Discovery Protocol (KBS-032).*

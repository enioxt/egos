# OSINT Brasil Toolkit — Curadoria Operacional 2026

> **Versão:** 1.0.0 | **Atualizado:** 2026-04-08 | **SSOT:** Este documento
> **Contexto:** Curadoria prática de ferramentas OSINT para contexto brasileiro, filtrada por utilidade real e conformidade legal (LGPD, Marco Civil, LAI).

---

## 🎯 Visão Geral

**Não existe "lista de todas as melhores"** — o ecossistema OSINT muda rápido e muitas ferramentas envelhecem. Esta curadoria foca em **utilidade real no Brasil**, priorizando:

1. **Portais oficiais e bases públicas nacionais** (Receita, Transparência, TSE)
2. **Ferramentas com manutenção ativa** (commits < 6 meses)
3. **Precisão sobre cobertura** (menos falsos positivos)
4. **Conformidade legal** (LGPD, Marco Civil da Internet, LAI)

---

## 🏆 Tier S — Essenciais Brasil

| Ferramenta | Categoria | Uso Principal | Brasil Priority |
|------------|-----------|-------------|-----------------|
| **OSINT Brazuca** | Hub/Index | Melhor hub brasileiro — organiza fontes, portais, regex nacionais | ⭐⭐⭐⭐⭐ |
| **Brasil.IO** | Dados Públicos | Cruzamentos de dados abertos: eleições, sócios/empresas, CNPJ | ⭐⭐⭐⭐⭐ |
| **Querido Diário** | Diários Oficiais | Indexa diários oficiais municipais com API pública | ⭐⭐⭐⭐⭐ |
| **Portal da Transparência** | Gasto Público | Favorecidos, servidores, viagens, sanções, dados abertos federais | ⭐⭐⭐⭐⭐ |
| **Escavador** | Jurídico | Processos, diários oficiais, monitoramento (consolida tribunais) | ⭐⭐⭐⭐⭐ |
| **Receita Federal / CPF** | Pessoa Física | Situação cadastral oficial do CPF | ⭐⭐⭐⭐⭐ |
| **Receita Federal / CNPJ** | Empresas | Inscrição e situação cadastral de pessoa jurídica | ⭐⭐⭐⭐⭐ |
| **Registro.br WHOIS/RDAP** | Domínios | Investigação de domínios `.br` — obrigatório | ⭐⭐⭐⭐⭐ |

---

## 🔍 Username / Perfil Social

**Ordem prática para Brasil:** Blackbird → Maigret → Sherlock → WhatsMyName

| Ferramenta | Plataformas | Status 2026 | Notas |
|------------|-------------|-------------|-------|
| **Blackbird** | 600+ | ⭐ Ativo (2026) | Melhor para triagem ampla, baixo falso positivo, Bellingcat toolkit reference |
| **Maigret** | 3000+ (500 populares) | ⭐ Ativo (ago/2025) | Mais agressivo em cobertura, ideal para investigação profunda de alias |
| **Sherlock** | 400+ | ⭐ Ativo (fev/2026) | Ótimo para primeira passada, simples e mantido |
| **WhatsMyName** | Base de referência | ⭐ Mantido | Menos ferramenta, mais base de dados para enumeração |

---

## 📧 Email / Telefone / Exposição

| Ferramenta | Tipo | Brasil Utility | Notas |
|------------|------|----------------|-------|
| **Have I Been Pwned (HIBP)** | Vazamentos email | ⭐⭐⭐⭐⭐ | API v3 atual, essencial para verificar exposição |
| **Holehe** | Email → contas | ⭐⭐⭐⭐ | Verifica presença em serviços, usar como confirmação não "verdade absoluta" |
| **PhoneInfoga** | Telefone internacional | ⭐⭐⭐ | Framework para números, melhor como ponto de apoio no Brasil |
| **Consulta Número / ABR Telecom** | Portabilidade BR | ⭐⭐⭐⭐⭐ | Operadora/portabilidade — mais útil que muita ferramenta global |
| **Consulta Aparelho Impedido** | IMEI BR | ⭐⭐⭐⭐⭐ | Verifica impedimento por furto/roubo/extravio (Anatel) |

---

## 🏢 Empresas / Vínculos / Dados Oficiais BR

| Ferramenta | Dataset | Uso Principal | Free/Paid |
|------------|---------|---------------|-----------|
| **Brasil.IO (sócios)** | QSA, CNPJ | Cruzamentos estruturados de empresas e sócios | Free |
| **TSE / DivulgaCandContas** | Candidaturas | Perfil, evolução patrimonial, certidões criminais | Free |
| **Jusbrasil** | Processos | Busca processual rápida e acompanhamento | Freemium |
| **BNMP 3.0 / CNJ** | Mandados | ⚠️ Base sensível, uso institucional apenas | Restricted |

---

## 🌐 Domínio / Infraestrutura / Ativos Digitais

| Ferramenta | Função | Status | Brasil Notes |
|------------|--------|--------|--------------|
| **theHarvester** | Emails, subdomínios, IPs | ⭐ Ativo | Excelente para footprinting passivo |
| **SpiderFoot** | Automação multi-fonte | ⭐ Ativo | Escalar coleta e navegação de resultados |
| **Recon-ng** | Framework modular | ⭐ Ativo | Marketplace oficial de módulos |
| **Shodan** | Exposição de serviços | ⭐ Ativo | Indispensável para mapeamento de superfície exposta |
| **Registro.br** | WHOIS/RDAP `.br` | ⭐ Oficial | Obrigatório para domínios brasileiros |

---

## 🗺️ GEOINT / Imagem / Metadados / Arquivamento

| Ferramenta | Função | Brasil Priority |
|------------|--------|-----------------|
| **ExifTool** | Metadados arquivos | ⭐⭐⭐⭐⭐ Padrão de fato para imagem/vídeo/documentos |
| **Wayback Machine** | Arquivamento web | ⭐⭐⭐⭐⭐ Preservar/recuperar versões antigas |
| **Google Earth** | Visualização espacial | ⭐⭐⭐⭐ Contexto territorial e comparação visual |
| **Mapillary** | Imagens nível rua | ⭐⭐⭐⭐ Camada alternativa onde Street View é fraco |
| **Sentinel Hub / EO Browser** | Sensoriamento remoto | ⭐⭐⭐ Comparação temporal, change detection |
| **TerraBrasilis / INPE** | Monitoramento ambiental BR | ⭐⭐⭐⭐⭐ **Diferencial real**: queimadas, desmatamento, análise territorial |

---

## 🔗 Correlação / Visualização

| Ferramenta | Função | Notas |
|------------|--------|-------|
| **Maltego** | Correlação gráfica | Muito forte para investigações relacionais, opção Community disponível |
| **OSINT Framework** | Diretório global | Ótimo para lembrar caminhos e categorias |
| **Bellingcat Toolkit** | Curadoria por caso | Mais confiável que listas aleatórias do GitHub |

---

## 📋 Shortlist Prático — 12 Ferramentas Essenciais

Se tivesse que reduzir a um kit enxuto e muito forte:

1. **OSINT Brazuca** — hub brasileiro definitivo
2. **OSINTKit-Brasil** — arsenal de bookmarks operacional
3. **Blackbird** — username OSINT de precisão
4. **Maigret** — investigação profunda de alias
5. **Sherlock** — verificação rápida de username
6. **Receita Federal / Redesim** — dados oficiais CPF/CNPJ
7. **Portal da Transparência** — gasto público federal
8. **Escavador** — processos e diários
9. **Registro.br WHOIS/RDAP** — domínios `.br`
10. **theHarvester** — footprinting passivo
11. **ExifTool** — metadados
12. **Wayback Machine + TerraBrasilis** — arquivamento + GEOINT BR

---

## ⚖️ Conformidade Legal — Brasil

**LGPD (Lei 13.709/2018):**
- Tratamento de dados pessoais requer base legal
- Dados públicos ≠ dados livres de responsabilidade
- Anonimização em publicações e relatórios

**Marco Civil da Internet (Lei 12.965/2014):**
- Guarda de registros por provedores
- Dados de conexão e aplicação sujeitos a ordem judicial

**LAI (Lei 12.527/2011):**
- Acesso a informações públicas é direito
- Classificações: sigilosas, pessoais sensíveis, classificadas

**Regras de Uso por Base:**
- Portal da Transparência: dados públicos, uso livre com citação
- BNMP/CNJ: dados sensíveis, uso institucional controlado
- Receita Federal: dados oficiais para consulta, não para comercialização
- Diários Oficiais: domínio público

---

## 🔧 Ferramentas EGOS Relacionadas

| Produto | Capacidade OSINT | Integração |
|---------|------------------|------------|
| **852** | Cruzamento de dados policiais, forense digital | Core product for law enforcement |
| **Guard Brasil** | Detecção PII brasileira, LGPD compliance | PII scanner + provenance |
| **Eagle Eye** | Monitoramento GovTech, licitações | PNCP enrichment, territory mapping |
| **Gem Hunter** | Discovery de ferramentas/frameworks | Pesquisa automática OSINT tools |

---

## 📚 Referências e Recursos

- [OSINT Brazuca GitHub](https://github.com/osintbrazuca)
- [OSINT Framework](https://osintframework.com)
- [Bellingcat Toolkit](https://www.bellingcat.com/resources/2024/09/24/bellingcat-online-investigations-toolkit)
- [Blackbird](https://github.com/p1ngul1n0/blackbird)
- [Maigret](https://github.com/soxoj/maigret)
- [Sherlock](https://github.com/sherlock-project/sherlock)

---

## 🎯 Matriz por Objetivo de Investigação

Ver também: `OSINT_BRASIL_MATRIX.md` — sequência ideal de uso por tipo de alvo.

---

*Documento mantido pelo EGOS Intelligence. Última verificação de atividade: 2026-04-08.*

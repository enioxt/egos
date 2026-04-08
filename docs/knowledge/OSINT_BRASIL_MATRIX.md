# OSINT Brasil — Matriz Operacional por Objetivo

> **Versão:** 1.0.0 | **Atualizado:** 2026-04-08 | **Fonte:** Curadoria OSINT Brazuca + EGOS Inteligência
> **Uso:** Sequência recomendada de ferramentas por tipo de alvo de investigação

---

## 🎯 Objetivo 1: Identificar Pessoa Física (PF)

**Cenário:** Nome, apelido ou username conhecido → identificar CPF, endereço, vínculos.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Google / DuckDuckGo** | Nome + cidade + ocupação | Referências iniciais, possíveis redes sociais |
| 2 | **Blackbird** | Username em 600+ plataformas | Perfis sociais confirmados |
| 3 | **Maigret** | Username/email | Cobertura profunda de alias |
| 4 | **Sherlock** | Username | Validação cruzada de existência |
| 5 | **Escavador** | Nome completo | Processos, histórico jurídico |
| 6 | **Jusbrasil** | Nome | Processos complementares |
| 7 | **TSE / DivulgaCandContas** | Nome | Se for candidato: perfil, patrimônio, certidões |
| 8 | **Portal da Transparência** | Nome ou CPF (se tiver) | Viagens, gastos como servidor/favorecido |
| 9 | **Brasil.IO (sócios)** | Nome | Empresas onde é sócio |
| 10 | **Receita Federal / CPF** | CPF (se descobrir) | Situação cadastral oficial |

### Verificação de Dados

| Check | Ferramenta | Validação |
|-------|------------|-----------|
| Email válido? | **Holehe** | Presença em serviços |
| Tel exposto? | **Have I Been Pwned** | Vazamentos conhecidos |
| Portabilidade? | **Consulta Número / ABR** | Operadora atual (se tiver telefone) |

---

## 🏢 Objetivo 2: Mapear Empresa e Sócios

**Cenário:** Nome fantasia, CNPJ ou marca → mapear estrutura societária, endereços, vínculos.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Google / Receita Federal** | Nome fantasia → CNPJ | CNPJ oficial |
| 2 | **Receita Federal / CNPJ** | CNPJ | Razão social, endereço, situação cadastral |
| 3 | **Brasil.IO (sócios)** | CNPJ | QSA completo (sócios e participações) |
| 4 | **Brasil.IO (empresas)** | Nome sócios | Outras empresas dos mesmos sócios |
| 5 | **Escavador** | Nome empresa + sócios | Processos judiciais |
| 6 | **Jusbrasil** | Nome empresa | Processos complementares |
| 7 | **Portal da Transparência** | CNPJ | Contratos públicos, pagamentos recebidos |
| 8 | **Registro.br** | Domínios relacionados | Sites oficiais e alternativos |
| 9 | **theHarvester** | Domínio | Emails, subdomínios expostos |
| 10 | **Shodan** | IP do domínio | Infraestrutura exposta |

### Cruzamentos Úteis

| Cruzamento | Ferramentas | Insight |
|------------|-------------|---------|
| Sócio → outras empresas | Brasil.IO | Grupo econômico não declarado |
| Empresa → contratos públicos | Portal da Transparência + Querido Diário | Histórico de contratações |
| CNPJ → domínios | Registro.br + WHOIS | Presença digital oficial |

---

## 🌐 Objetivo 3: Investigar Domínio .br

**Cenário:** Website suspeito → identificar dono, infraestrutura, histórico.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Registro.br WHOIS/RDAP** | Domínio `.br` | Titular, responsável técnico, datas |
| 2 | **Wayback Machine** | URL | Histórico de versões do site |
| 3 | **theHarvester** | Domínio | Emails, subdomínios, hosts |
| 4 | **SpiderFoot** | Domínio/IP | Automação de footprinting completo |
| 5 | **Shodan** | IP do domínio | Serviços expostos, tecnologias |
| 6 | **Recon-ng** | Domínio | Módulos específicos para .br |
| 7 | **Google Dorks** | `site:dominio.com` | Páginas indexadas, diretórios expostos |
| 8 | **ExifTool** (se baixar arquivos) | Metadados de PDFs/imagens | Software usado, datas, possíveis autores |

### Alertas de Segurança

| Check | Ferramenta | Risco |
|-------|------------|-------|
| Serviços expostos? | **Shodan** | Vulnerabilidades potenciais |
| Subdomínios antigos? | **theHarvester** | Sistemas legados não protegidos |
| Vazamento de emails? | **Have I Been Pwned** | Contas do domínio comprometidas |

---

## 📍 Objetivo 4: GEOINT no Brasil

**Cenário:** Localização aproximada → imagens, contexto territorial, mudanças temporais.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Google Earth** | Coordenadas ou endereço | Contexto visual 3D, histórico de imagens |
| 2 | **Google Street View** | Endereço | Vista nível rua, data da imagem |
| 3 | **Mapillary** | Coordenadas | Imagens complementares onde Street View é fraco |
| 4 | **Sentinel Hub / EO Browser** | Coordenadas | Imagens de satélite, change detection |
| 5 | **TerraBrasilis / INPE** | Coordenadas (rural/Amazônia) | Queimadas, desmatamento, análise territorial |
| 6 | **ExifTool** | Fotos do local (se houver) | Coordenadas GPS exatas, data/hora real |
| 7 | **Wayback Machine** | URLs de mapas locais | Evolução de comércios, construções |

### Casos Especiais Brasil

| Cenário | Ferramenta | Uso |
|---------|------------|-----|
| Área rural/Amazônia | **TerraBrasilis** | Única fonte confiável de imagens recentes |
| Queimadas | **INPE Queimadas** | Dados oficiais de focos de calor |
| Desmatamento | **TerraBrasilis PRODES/DETER** | Alertas de desmatamento em tempo real |
| Enchentes/desastres | **Sentinel Hub** | Imagens pós-evento gratuitas |

---

## 📧 Objetivo 5: Investigar Email Específico

**Cenário:** Email suspeito → verificar exposição, contas associadas, validade.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Have I Been Pwned (HIBP)** | Email | Breaches conhecidos, data da exposição |
| 2 | **Holehe** | Email | Contas em serviços (Twitter, Instagram, etc.) |
| 3 | **Blackbird** | Email | Perfis em 600+ plataformas |
| 4 | **Maigret** | Email | Investigação profunda de alias |
| 5 | **theHarvester** | Domínio do email | Outros emails da mesma organização |
| 6 | **Google** | Email entre aspas | Ocorrências públicas, vazamentos indexados |
| 7 | **Wayback Machine** | Email (se aparecia em sites) | Histórico de exposição |

### Validação

| Check | Como fazer |
|-------|------------|
| Email existe? | **Holehe** + tentativa de recuperação de senha (cautelosamente) |
| Formatado corretamente? | Regex básico: `^[^\s@]+@[^\s@]+\.[^\s@]+$` |
| Domínio válido? | **Registro.br** (se .br) ou WHOIS geral |

---

## 📱 Objetivo 6: Investigar Telefone (BR)

**Cenário:** Número desconhecido → identificar operadora, portabilidade, possível dono.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Consulta Número / ABR Telecom** | Número completo (DDD + 9 dígitos) | Operadora atual, data da portabilidade |
| 2 | **PhoneInfoga** | Número internacional | Framework de análise, footprinting |
| 3 | **Google / DuckDuckGo** | Número entre aspas | Ocorrências públicas, anúncios, reclamações |
| 4 | **Blackbird/Maigret** | Número (como username) | Se o número foi usado como identificador em redes |
| 5 | **WhatsApp** | Tentar adicionar contato | Foto de perfil, status, "visto por último" |
| 6 | **Truecaller** (app) | Número | Identificação colaborativa (grande base BR) |

### IMEI — Aparelho Específico

| Situação | Ferramenta | Uso |
|----------|------------|-----|
| Compra de usado | **Consulta Aparelho Impedido** | Verificar se não é roubado/furtado |
| Recuperação | **Anatel + BO** | Registrar impedimento se necessário |

---

## 🏛️ Objetivo 7: Monitorar Contratos e Gastos Públicos

**Cenário:** Acompanhar contratações de órgão ou empresa específica.

### Fluxo Recomendado

| Etapa | Ferramenta | O que buscar | Output |
|-------|------------|--------------|--------|
| 1 | **Portal da Transparência** | CNPJ do órgão ou empresa | Contratos, pagamentos, aditivos |
| 2 | **Querido Diário** | Nome do órgão (municipal) | Dispensa de licitação, contratos emergenciais |
| 3 | **Compras Governamentais (gov.br)** | CNPJ ou objeto | Licitações federais |
| 4 | **TCEs estaduais** | Órgão estadual/municipal | Fiscalização local |
| 5 | **Escavador** | Nome do gestor/empresário | Processos relacionados |
| 6 | **Brasil.IO** | Empresa contratada | Outros contratos no país |

### Alertas Automatizados

| O que monitorar | Onde | Frequência |
|-----------------|------|------------|
| Novos contratos | **Portal da Transparência** | Diária |
| Dispensa de licitação | **Querido Diário** | Diária |
| Aditivos contratuais | **Portal da Transparência** | Semanal |

---

## 🗂️ Objetivo 8: Pesquisa Jurídica Completa

**Cenário:** Mapear histórico processual de pessoa ou empresa.

### Fluxo Recomendado

| Etapa | Ferramenta | Cobertura | Dados |
|-------|------------|-----------|-------|
| 1 | **Escavador** | Tribunais estaduais e federais (majoritário) | Processos, movimentações, partes |
| 2 | **Jusbrasil** | Complementar a Escavador | Processos adicionais, jurisprudência |
| 3 | **TSE / DivulgaCandContas** | Se for candidato | Processos eleitorais, certidões criminais |
| 4 | **CNJ / BNMP 3.0** | Mandados de prisão | ⚠️ Acesso institucional apenas |
| 5 | **TRTs (regionais)** | Trabalhista | Passivos trabalhistas |
| 6 | **TJ estaduais** | Estadual | Processos locais não indexados |

### Cruzamentos Úteis

| Cruzamento | Insight |
|------------|---------|
| Processo → partes → outras empresas | Litigiosidade empresarial |
| Processo → advogados → outros clientes | Rede de relacionamentos |
| Data da ação → eventos públicos | Contexto temporal |

---

## ⚡ Quick Reference — Quando Usar O Quê

| Se você tem... | Use primeiro... | Depois... |
|----------------|-----------------|-----------|
| Username | **Blackbird** → **Maigret** | **Sherlock** |
| Email | **Have I Been Pwned** → **Holehe** | **Blackbird** |
| Telefone BR | **Consulta Número** → **PhoneInfoga** | Google |
| CNPJ | **Receita Federal** → **Brasil.IO** | **Portal da Transparência** |
| CPF | **Receita Federal** | **Portal da Transparência** |
| Domínio .br | **Registro.br** → **theHarvester** | **Shodan** |
| Endereço BR | **Google Earth** → **Street View** | **TerraBrasilis** (rural) |
| Processo | **Escavador** → **Jusbrasil** | TJ/TRT específico |
| Contrato público | **Portal da Transparência** | **Querido Diário** |
| Empresa/sócios | **Brasil.IO** → **Escavador** | **Portal da Transparência** |

---

## 🔗 Integração EGOS

Esta matriz alimenta diretamente:

- **`scripts/x-opportunity-alert.ts`** — queries de busca por palavras-chave
- **`docs/social/X_MOAT_KEYWORDS.md`** — termos de alta conversão
- **`852`** — fluxos de investigação digital policial
- **`Guard Brasil`** — conformidade LGPD em coleta de dados

---

*Matriz operacional mantida pelo EGOS Intelligence. Para sugestões de atualização: abrir issue em `github.com/enioxt/egos`.*

# Self-Discovery — Arquitetura de Container (Porta 3098)

> **Versão:** 1.1.0  
> **Data:** 2026-04-06  
> **Status:** Documentação de arquitetura — **DOMÍNIO REGISTRADO: self.egos.ia.br**  
> **Decisão:** HUM-002 — Produtizar como container Docker standalone  
> **DNS:** self.egos.ia.br → 204.168.217.125 (VPS Hetzner)

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** Architecture specification for Self-Discovery container (port 3098)
- **Summary:** Therapeutic chatbot with pattern detection and Socratic questioning — containerized deployment
- **Type:** FIXO — Implementation spec for VPS-002
- **Read next:**
  - `docs/ARCHIVE_GEMS_CATALOG.md` — Gem #17 (Self-Discovery) decision
  - `docs/EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — HUM-002 confirmed decision
  - `docs/INFRASTRUCTURE_ARCHIVE_AUDIT.md` — VPS container patterns
- **Related:** VPS-002 (container creation task)

<!-- llmrefs:end -->

---

## 🎯 Visão do Produto

**Self-Discovery** é um chatbot terapêutico que:
1. **Detecta padrões psicológicos** em textos do usuário
2. **Gera perguntas socráticas** (método maiêutico) para reflexão
3. **Não dá respostas** — estimula auto-descoberta

**Diferencial:** "IA que pergunta, não responde"

---

## 📊 Especificações Técnicas

### Porta e Endpoint

| Parâmetro | Valor |
|-----------|-------|
| **Domínio** | self.egos.ia.br |
| **Porta VPS** | 3098 |
| **Container Name** | egos-self-discovery |
| **Health Check** | GET /health |
| **API Base** | https://self.egos.ia.br/api/v1 |
| **Frontend** | https://self.egos.ia.br |

### Stack Tecnológico

| Camada | Tecnologia | Origem |
|--------|-----------|--------|
| **Backend** | FastAPI (Python) | v2/core/maieutic_engine/ |
| **Pattern Detection** | Python NLP | v2/core/intelligence/pattern_detector.py |
| **Frontend** | Next.js 15 (React) | v2/websiteNOVO/src/app/self-discovery/ |
| **Database** | Supabase (PostgreSQL) | v2 migrations |
| **Container** | Docker + docker-compose | VPS pattern |

---

## 🗂️ Estrutura do Container

```
egos-self-discovery/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── patterns.py         # POST /api/v1/patterns/detect
│   │   │   └── maieutic.py         # POST /api/v1/maieutic/generate
│   │   ├── core/
│   │   │   ├── maieutic_engine.py  # Question generator
│   │   │   └── pattern_detector.py # Pattern detection
│   │   └── models/
│   │       └── schemas.py          # Pydantic models
│   ├── requirements.txt            # Python deps
│   └── Dockerfile                  # Backend image
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── self-discovery/     # Next.js app
│   │   └── components/
│   ├── package.json
│   └── Dockerfile                  # Frontend image
├── docker-compose.yml              # Orchestration
└── .env.example                    # Environment template
```

---

## 🔌 API Endpoints

### 1. Detectar Padrões

```http
POST /api/v1/patterns/detect
Content-Type: application/json

{
  "text": "Tenho dificuldade de finalizar projetos por medo de não serem perfeitos"
}

Response:
{
  "patterns": [
    {
      "name": "perfectionism_procrastination",
      "confidence": 0.87,
      "category": "behavioral",
      "indicators": ["medo de fracassar", "perfeccionismo"]
    }
  ],
  "suggestions": ["explore_fear", "reframe_perfectionism"]
}
```

### 2. Gerar Perguntas Socráticas

```http
POST /api/v1/maieutic/generate
Content-Type: application/json

{
  "pattern": "perfectionism_procrastination",
  "depth": "analytical",
  "context": "projeto pessoal"
}

Response:
{
  "questions": [
    "O que 'perfeito' significa para você neste contexto?",
    "Como seria 'bom o suficiente'?",
    "Qual é o custo real de esperar pelo momento perfeito?"
  ],
  "method": "socratic_maietic",
  "depth_level": 3
}
```

### 3. Health Check

```http
GET /health

Response:
{
  "status": "healthy",
  "service": "egos-self-discovery",
  "port": 3098,
  "version": "1.0.0",
  "patterns_loaded": 12,
  "ready": true
}
```

---

## 🐳 Docker Compose Specification

```yaml
version: '3.8'

services:
  self-discovery-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: self-discovery-backend
    ports:
      - "3098:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  self-discovery-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: self-discovery-frontend
    ports:
      - "3099:3000"  # Frontend porta separada (opcional)
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:3098
    depends_on:
      - self-discovery-backend
    restart: unless-stopped

networks:
  default:
    name: egos-network
    external: true  # Usar rede compartilhada do EGOS
```

---

## 🔗 Integração com EGOS Gateway e DNS

### DNS Configurado

```
self.egos.ia.br → 204.168.217.125 (VPS Hetzner)
```

✅ **Registro A criado no DNS**

### Roteamento via Caddy (Reverse Proxy)

```
Caddy (infra-caddy-1) porta 80/443
    ├── self.egos.ia.br/* → localhost:3098
    └── Health check → http://localhost:3098/health
```

### Configuração Caddy

```caddyfile
# Caddyfile adicionar:
self.egos.ia.br {
    reverse_proxy localhost:3098
    
    # Health check
    handle /health {
        reverse_proxy localhost:3098
    }
    
    # TLS automático (Let's Encrypt)
    tls internal
}
```

---

## 📋 Checklist de Implementação (VPS-002)

### Fase 1: Preparação (Dia 1)

- [ ] Extrair código v2 para estrutura container
- [ ] Criar Dockerfile backend (Python/FastAPI)
- [ ] Criar Dockerfile frontend (Next.js)
- [ ] Criar docker-compose.yml
- [ ] Configurar .env.example

### Fase 2: Testes Locais (Dia 2)

- [ ] Build container local
- [ ] Testar endpoints /patterns/detect e /maieutic/generate
- [ ] Validar health check
- [ ] Testar via Gateway (localhost:3050/self-discovery)

### Fase 3: Deploy VPS (Dia 3)

- [ ] Transferir para VPS (204.168.217.125)
- [ ] Configurar environment variables
- [ ] Subir container: `docker-compose up -d`
- [ ] Verificar porta 3098 aberta
- [ ] Testar health check remoto

### Fase 4: Integração (Dia 4)

- [ ] Configurar Gateway roteamento
- [ ] Adicionar ao watchdog script
- [ ] Configurar Telegram alerts
- [ ] Testar end-to-end

---

## 🚨 Considerações de Compliance

### NÃO Medical Device

- **Categoria:** Wellness/Self-improvement (não terapia clínica)
- **Nicho inicial:** Procrastinação, produtividade, autoconhecimento
- **EVITAR:** Diagnósticos de saúde mental, depressão, ansiedade clínica
- **Disclaimer necessário:** "Esta ferramenta é para auto-reflexão, não substitui terapia profissional"

### Dados e Privacidade

- Dados armazenados no Supabase (mesma infra EGOS)
- PII (Personally Identifiable Information) minimizada
- LGPD compliance via Guard Brasil patterns

---

## 📊 Métricas de Sucesso

| Métrica | Target | Como medir |
|---------|--------|------------|
| **Uptime** | > 99% | Watchdog script |
| **Latência API** | < 500ms | Health check logs |
| **Usuários ativos** | 100/month (pilot) | Supabase analytics |
| **Sessões completadas** | > 60% | API tracking |

---

## 🔄 Roadmap Pós-Deploy

### Semana 1-2 (Stabilization)
- Monitorar logs e erros
- Ajustar thresholds de pattern detection
- Coletar feedback inicial

### Mês 2 (Enhancement)
- Adicionar mais patterns (foco em produtividade)
- Melhorar UX do frontend
- Integração com Telegram (notifications)

### Mês 3+ (Scale)
- Avaliar port para TypeScript (se tração alta)
- Adicionar analytics dashboard
- Considerar standalone domain (self-discovery.egos.ia.br)

---

## 📎 Referências

- **Código origem:** `/home/enio/egos-archive/v2/EGOSv2/core/maieutic_engine/`
- **Código origem:** `/home/enio/egos-archive/v2/EGOSv2/core/intelligence/pattern_detector.py`
- **Testes v2:** `/home/enio/egos-archive/v2/EGOSv2/docs/SELF_DISCOVERY_TEST.md`
- **Decisão:** `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — HUM-002

---

**Data:** 2026-04-06  
**Status:** ✅ Arquitetura documentada — **DOMÍNIO self.egos.ia.br REGISTRADO**  
**Próximo:** Implementar container (task VPS-002) + Configurar Caddy + Deploy

# Test & Validation Orchestrator v2 — Multi-Agent Review System

> **SSOT:** Este documento | **Versão:** 1.0.0 | **Atualizado:** 2026-04-08

## Visão Geral

Sistema multi-agent para validação automática de código, geração de E2E tests, e review swarm com evidence chain integrada ao EGOS.

## Contexto

Pesquisas (Braintrust, AutoEvals, EPOCH-Bench, Arun Baby) revelam padrão comum para agent evaluation:
1. **Tracing completo** de cada decisão
2. **Scorers** (deterministic + LLM-as-judge)
3. **Regression gates** em CI/CD
4. **Feedback loop** produção→teste

Thread X (Bruno Pinheiro) confirma: breakdown estruturado (epic→stories) + E2E tests auto-gerados + multi-agent swarm review = crescimento rápido validado.

## Arquitetura 6-Agent Swarm

```
┌─────────────────────────────────────────────────────────────┐
│                  Test & Validation Orchestrator            │
│                    (Comando: egos validate)                │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Input: Epic/Story/Bug description                          │
│  "Add user authentication with MFA"                         │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │         1. PLANNER AGENT               │
        │  Quebra em stories com acceptance      │
        │  criteria e regras de negócio          │
        └────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │        2. GENERATOR AGENT               │
        │  Gera código + E2E tests               │
        │  (Playwright/TestNG templates)         │
        └────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │       3. REVIEWER1 AGENT                │
        │  Review: acceptance criteria coverage   │
        │  Flag: gaps nos requisitos              │
        └────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │       4. REVIEWER2 AGENT                │
        │  Review: security/best practices       │
        │  Scan: vulnerabilidades, anti-patterns │
        └────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │       5. VALIDATOR AGENT                │
        │  Executa: lint → type-check → tests    │
        │  → E2E (paralelizável)                 │
        │  Output: Pass/Fail + logs              │
        └────────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │       6. REPORTER AGENT                 │
        │  Consolida: evidence entry               │
        │  Gera: report human-readable           │
        │  Trigger: content.demo (se passou)     │
        └────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Output: Evidence entry + Report + Demo video (opcional)     │
└─────────────────────────────────────────────────────────────┘
```

## Agentes Detalhados

### 1. Planner Agent
**Função:** Decompor epic em stories técnicas

**Input:**
```
Epic: "Add user authentication with MFA"
Context: EGOS framework, TypeScript, Supabase
```

**Output:**
```yaml
stories:
  - id: AUTH-001
    title: Setup Supabase Auth schema
    acceptance_criteria:
      - Users table with MFA fields
      - RLS policies configured
    effort: 2h
    
  - id: AUTH-002
    title: Implement TOTP MFA
    acceptance_criteria:
      - QR code generation
      - Verification endpoint
      - Backup codes
    effort: 4h
    
  - id: AUTH-003
    title: Login UI with MFA flow
    acceptance_criteria:
      - Email/password step
      - MFA code input
      - Error handling
    effort: 3h
```

**Modelo recomendado:** Kimi K2.5 (planning specialist)

### 2. Generator Agent
**Função:** Gerar código e E2E tests

**Templates Playwright:**
```typescript
// E2E test template for web features
test('user can complete MFA login', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password');
  await page.click('button[type="submit"]');
  
  // MFA step
  await page.waitForSelector('[name="mfa-code"]');
  await page.fill('[name="mfa-code"]', generateTOTP());
  await page.click('button[data-testid="verify-mfa"]');
  
  // Assert
  await expect(page).toHaveURL('/dashboard');
});
```

**Templates TestNG (API):**
```java
@Test
group = "auth"
public void testMFAEndpoint() {
    // Given
    String email = "test@example.com";
    String password = "password";
    String totp = generateTOTP();
    
    // When
    Response response = given()
        .body(jsonPayload)
        .post("/api/auth/mfa/verify");
    
    // Then
    assertEquals(response.statusCode(), 200);
    assertTrue(response.jsonPath().getBoolean("success"));
}
```

**Modelo recomendado:** Qwen3 Coder (coding SOTA)

### 3. Reviewer1 Agent (Acceptance)
**Função:** Verificar cobertura de acceptance criteria

**Checklist:**
- Cada critério tem teste correspondente?
- Edge cases estão cobertos?
- User journeys completos?
- Fluxos de erro documentados?

**Output:**
```yaml
review:
  coverage_score: 85%
  gaps:
    - "Missing test: MFA backup codes flow"
    - "Missing test: Rate limiting on MFA attempts"
  recommendations:
    - "Add test for backup code usage"
```

### 4. Reviewer2 Agent (Security/Best Practices)
**Função:** Security scan e best practices review

**Verificações:**
- OWASP Top 10 vulnerabilidades
- Hardcoded secrets
- SQL injection risks
- XSS prevention
- CSRF tokens
- Rate limiting
- Input validation
- LGPD/PII handling

**Modelo recomendado:** Guard Brasil integration + LLM review

### 5. Validator Agent
**Função:** Execução de testes

**Pipeline:**
```bash
# Paralelizável
lint & type-check &
unit-tests &
e2e-tests &
wait
security-scan
```

**Integração pre-commit:**
```bash
# .husky/pre-commit (enhanced)
bun run validate-swarm --staged-files
```

### 6. Reporter Agent
**Função:** Consolidação e evidence chain

**Evidence Entry:**
```json
{
  "evidence_id": "EV-2026-04-08-001",
  "epic": "MFA Authentication",
  "stories_validated": ["AUTH-001", "AUTH-002", "AUTH-003"],
  "test_results": {
    "unit": { "passed": 15, "failed": 0, "coverage": 92 },
    "e2e": { "passed": 8, "failed": 0, "coverage": 85 },
    "security": { "findings": 0, "severity": "none" }
  },
  "agents_involved": ["planner", "generator", "reviewer1", "reviewer2", "validator"],
  "timestamp": "2026-04-08T14:30:00Z",
  "signature": "sha256:...",
  "report_url": "https://egos.io/reports/EV-2026-04-08-001"
}
```

## Comandos EGOS

### egos validate
```bash
# Validar epic completo
egos validate "Add user authentication with MFA"

# Validar story específica
egos validate story AUTH-001

# Modo dry-run (simulação)
egos validate "Add MFA" --dry

# Com geração de demo
egos validate "Add MFA" --with-demo
```

### egos test
```bash
# Gerar E2E tests para story
egos test story AUTH-001 --framework=playwright

# Regression check (após bug fix)
egos test regression --bug-id=BUG-123

# Flaky test detection
egos test detect-flaky --history-days=30
```

### egos regression-check
```bash
# Verificar regressões no codebase
egos regression-check --scope=changed-files

# Full regression (CI/CD)
egos regression-check --scope=all --fail-fast
```

## Test Categories & Prompts

### Coding Tests
Verificam: function generation, debugging, refactoring, algorithms
Meta-prompt: `.guarani/prompts/meta/llm-test-coding.md`

### Reasoning Tests
Verificam: logical deduction, math problems, planning, abductive reasoning
Meta-prompt: `.guarani/prompts/meta/llm-test-reasoning.md`

### Context Tests
Verificam: needle-in-haystack (128K-1M), multi-needle retrieval, summarization
Meta-prompt: `.guarani/prompts/meta/llm-test-context.md`

### Agentic Tests
Verificam: tool selection, state management, error recovery, multi-tool coordination
Meta-prompt: `.guarani/prompts/meta/llm-test-agentic.md`

### Creative Tests
Verificam: brand voice, multi-format adaptation, headlines, email sequences
Meta-prompt: `.guarani/prompts/meta/llm-test-creative.md`

## Self-Verification Gates

### Pre-Commit Integration
```bash
# .husky/pre-commit
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Se arquivos >5 ou alterações >100 linhas, usar swarm
if [ $(echo "$STAGED_FILES" | wc -l) -gt 5 ]; then
    echo "Large change detected - running validation swarm..."
    bun run test-swarm --files "$STAGED_FILES"
fi
```

### CI/CD Integration
```yaml
# .github/workflows/validate-swarm.yml
name: Validation Swarm
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Validation Swarm
        run: bun run egos validate --pr=${{ github.event.pull_request.number }}
      - name: Post Results
        run: bun run comment-pr --with-evidence
```

## MemPalace Integration (Test Memory)

```typescript
// Wake-up antes de validar
const similarTests = await mempalace.recall({
  wing: 'tests',
  query: 'MFA authentication tests',
  k: 5
});

// Prevent regressions
for (const test of similarTests) {
  if (test.result === 'failed' && test.bug_id) {
    console.log(`⚠️ Similar test failed before: ${test.bug_id}`);
    // Adiciona à lista de verificação especial
  }
}

// Store results
await mempalace.retain({
  wing: 'tests',
  room: 'auth-mfa-2026-04',
  data: {
    epic: 'MFA Authentication',
    test_results: results,
    coverage: 92,
    agents: ['planner', 'generator', 'reviewer1', 'reviewer2', 'validator'],
    evidence_id: 'EV-2026-04-08-001'
  }
});
```

## Self-Healing Tests

### Detecção de Falha
```typescript
// Quando teste quebra
if (testResult.status === 'failed') {
  // LLM analisa erro
  const analysis = await llm.analyze({
    error: testResult.error,
    test_code: testResult.code,
    source_code: testResult.target
  });
  
  // Sugere fix
  const suggestedFix = await llm.generate({
    prompt: `Fix this failing test: ${analysis.root_cause}`,
    context: testResult
  });
  
  // Cria PR com fix sugerido
  await createAutoFixPR(suggestedFix);
}
```

### Aprovação Humana
- PR criado automaticamente
- Notificação Telegram com diff
- `/approve` para merge automático
- `/reject` para descartar

## Flaky Test Detection

### Algoritmo
```typescript
function detectFlakyTests(testHistory: TestRun[], days: number): string[] {
  const flaky = [];
  
  for (const test of testHistory) {
    const runs = test.runs.filter(r => 
      r.date > Date.now() - days * 24 * 60 * 60 * 1000
    );
    
    if (runs.length < 5) continue;
    
    const passRate = runs.filter(r => r.status === 'passed').length / runs.length;
    const variance = calculateVariance(runs.map(r => r.duration));
    
    // Pass rate entre 20% e 80% = flaky
    if (passRate > 0.2 && passRate < 0.8) {
      flaky.push(test.name);
    }
    
    // Alta variância de tempo também indica instabilidade
    if (variance > threshold) {
      flaky.push(test.name);
    }
  }
  
  return flaky;
}
```

### Quarentena
```typescript
// Auto-quarantine flaky tests
for (const testName of flakyTests) {
  await quarantineTest(testName, {
    reason: 'Flaky - requires investigation',
    quarantine_duration: '7d',
    notify: 'team-channel'
  });
}
```

## Test Analytics Dashboard (HQ)

### Métricas
- **Coverage por repo:** Unit, integration, E2E
- **Tempo médio de execução:** Trend ao longo do tempo
- **Taxa de falha:** Por suite, por arquivo
- **Flaky tests:** Count e trend
- **Economia de tempo:** Horas salvas com auto-tests vs manual

### Visualizações
- Heatmap: Arquivos com maior risco de regressão
- Timeline: Execuções de teste ao longo do tempo
- Comparison: EGOS vs benchmarks industriais

## LLM-MON Integration

### Model Selection por Tarefa de Teste
```typescript
// Usar modelos mais baratos/free quando qualidade é equivalente
const testTaskModels = {
  'generate-unit-test': 'qwen/qwen3-coder:free',  // Free tier
  'generate-e2e-test': 'qwen/qwen3-coder:free',     // Free tier
  'security-review': 'qwen-plus',                   // Quality required
  'complex-planning': 'moonshotai/kimi-k2.5'        // Planning specialist
};

// Fallback automático
const model = await llmMon.selectModel({
  task: 'generate-unit-test',
  quality_threshold: 8.0,
  prefer_free: true
});
```

## Referências

- **Braintrust Agent Evaluation:** https://www.braintrust.dev/articles/ai-agent-evaluation-framework
- **AutoEvals (Medium):** https://medium.com/@madhur.prashant7/autoevals-building-a-multi-agent-system
- **EPOCH-Bench:** https://www.askaibrain.com/en/posts/epoch-bench-testing-models-as-agents
- **Arun Baby Testing AI Agents:** https://www.arunbaby.com/ai-agents/0043-testing-ai-agents/

## Tasks Relacionadas

- TEST-001..013 (TASKS.md §Test & Validation Orchestrator v2)

---

**Nota:** Este sistema garante que todo código EGOS seja validado por 6 agentes especializados antes de ir para produção, com evidence chain completa, self-healing para testes quebrados, e otimização de custos via LLM-MON integration.

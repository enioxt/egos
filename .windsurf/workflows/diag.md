# /diag — System Diagnostic (EGOS v1.0)

> **Trigger:** `/diag`, `diagnóstico`, `system health`, `como estamos`
> **Purpose:** Instant full-ecosystem diagnostic with brutal honesty
> **Output:** Structured report with facts → problems → actions
> **Time:** ~60 seconds

---

## Protocol

### 1. Infrastructure Health (10s)
```bash
bash scripts/egos-repo-health.sh
bun run doctor --json
```
- Report: repos clean/dirty, unpushed commits, doctor score
- Docker: `ssh hetzner 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'` (if VPS accessible)

### 2. Burn Rate vs Revenue (5s)
Read and report:
- Monthly infrastructure cost (Hetzner, Vercel, Supabase, AI APIs)
- Monthly revenue (currently R$0 — update when this changes)
- Burn rate trend

### 3. Product Maturity Matrix (15s)
For each product, report current stage:

| Product | Stage | Metric |
|---|---|---|
| Guard Brasil | `packaged` / `published` / `api_live` / `first_customer` | npm downloads, API calls |
| Santiago | `code_ready` / `deployed` / `first_order` | orders/month |
| FORJA | `proposal` / `poc` / `contract_signed` | MRR |
| Carteira Livre | `mvp` / `launched` / `traction` | instructors, transactions |
| br-acc | `live` / `monetized` | queries/month |
| 852 | `live` / `reference_case` | users, ATRiAN violations caught |

### 4. Agent Runtime Health (10s)
```bash
bun agent:list
```
- Total registered vs actually executable
- Last execution timestamp for each
- Dead agents (no entrypoint or broken imports)

### 5. CRCDM Mesh Status (5s)
```bash
wc -l ~/.egos/crcdm/logs/*.log
du -sh ~/.egos/crcdm/
```
- DAG size, log freshness, retention status

### 6. Observability Gap Report (5s)
- MetricsTracker: instantiated? → YES/NO
- Telemetry: active consumers? → YES/NO
- Dashboard: deployed? → YES/NO
- CRCDM viz: exists? → YES/NO

### 7. Critical Actions (10s)
List top 3 actions ranked by **revenue impact**, not technical elegance:
1. What generates R$ fastest?
2. What unblocks customers?
3. What reduces burn rate?

---

## Output Format

```markdown
# EGOS Diagnostic — {date}

## Infrastructure: {score}%
- Repos: {n}/9 clean
- Docker: {n} containers running
- Doctor: {score}/100

## Burn Rate: R${x}/mês → Revenue: R${y}/mês
- Delta: -R${z}/mês

## Product Maturity
| Product | Stage | Next Milestone | ETA |
|---|---|---|---|

## Agent Health
- Registered: {n} | Executable: {n} | Dead: {n}

## Observability Gaps
- {list}

## Top 3 Actions (revenue-ranked)
1. {action} → R${impact}/mês
2. {action} → R${impact}/mês
3. {action} → R${impact}/mês
```

---

## When to Run
- Every `/start` should include a mini `/diag` (infrastructure + burn rate only)
- Full `/diag` on demand or weekly
- After any deployment or infrastructure change

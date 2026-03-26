# EGOS Values Manifesto — What We Believe

> **Version:** 1.0.0 | **Updated:** 2026-03-26
> **A Living Document of Principles**

---

## Preamble

This is not a marketing document. This is what EGOS *actually believes* based on hard-won production experience with governed AI agents. These values guide every decision we make about code, governance, and community.

---

## Core Beliefs

### 1. **Governance is Infrastructure**

We believe governance rules are not policies to audit after-the-fact. They are infrastructure.

Just as you wouldn't run a server without firewall rules, you shouldn't run AI agents without governance rules.

- Rules must be **explicit, versioned, and auditable**
- Rules must be **enforced at commit time**, not discovered in incidents
- Rules must be **portable** — they live in your repo, they belong to you
- Rules must be **community-evolved** — locked governance breaks trust

**In Practice:**
- Every agent is born into `.guarani/` governance
- Pre-commit hooks enforce rules before merge (no exceptions)
- Governance changes are voted on and signed (proof-of-work)
- If you fork EGOS, your rules come with you

---

### 2. **Rules Govern Agents. Agents Enforce Rules. Community Evolves Rules.**

This is the three-part harmony that makes EGOS work.

**Rules Govern Agents:**
- An agent's behavior is entirely bounded by `.windsurfrules` and `DOMAIN_RULES.md`
- An agent cannot read, write, or delete files outside its sandboxed scope
- An agent cannot use LLM providers without explicit allowance
- An agent cannot decide its own rules (that's human-only)

**Agents Enforce Rules:**
- An agent is the *executor* of community-decided rules
- When rules change, agents immediately follow new rules
- An agent logs every decision it makes, traceable back to which rule authorized it
- An agent's autonomy exists *within* clear boundaries, making it trustworthy

**Community Evolves Rules:**
- New challenges → community proposes rule changes
- Rule changes live in version control → full history
- Contributors can argue for rule modifications → transparent debate
- Rules are not locked by platform; they grow with the community

**In Practice:**
- `DOMAIN_RULES.md` is a living YAML file; any contributor can propose changes via PR
- Pre-commit hooks validate new rules against existing architecture
- Governance changes require Signed-Off-By (provenance signature)
- Agent runs reference the exact rule version that authorized them (archaeology)

---

### 3. **Evidence-Driven Decision-Making**

We believe hunches are not governance.

Every decision—whether agent or human—must be backed by measurable evidence.

- **Agent decisions:** Logged to JSONL, traceable by correlation ID, attached to rule version
- **Governance changes:** Proposed with data (e.g., "ATRiAN scores dropped 5% because rule X was ambiguous")
- **Operational decisions:** Cost tracking, incident metrics, drift detection reports
- **Hiring/community:** Contributions are measured (commits, PRs, quality gates), not hunches

**What We Track:**
- Cost per agent run (LLM provider, tokens, inference time)
- Governance check pass rate (drift incidents, policy violations)
- Agent success rate (dry-run vs. execution, rollback frequency)
- Provenance chain (who changed what rule and when)
- Incident root cause (linked to governance version, agent action)

**What We Don't Track:**
- ❌ Vanity metrics (GitHub stars alone)
- ❌ Hunches ("I think this agent is helpful")
- ❌ Untraceable logs (all logs correlated by ID)

**In Practice:**
- `governance:check` reports drift as measurable incidents
- Agent logs attached to rule version that authorized them
- Archaeology agent traces incidents back to philosophical catalyst
- Every governance change must include "Evidence:" section in PR body

---

### 4. **Transparency in Operations**

We believe secrecy breeds mistrust.

Every agent run, every governance decision, every incident is visible and auditable. No black boxes.

**What's Public:**
- All governance rules (`.guarani/`, `.windsurfrules`)
- All agent code (agents/registry)
- All incident reports (archaeology digger output)
- All cost breakdowns (per provider, per repo)
- All governance change history (git log)

**What's Private:**
- LLM API keys (never committed, always environment variables)
- User data in production apps (PII handling)
- Security vulnerability disclosures (responsible disclosure)

**What's Open-Source:**
- The entire governance system (MIT license)
- The agent runtime (zero dependencies)
- Case studies from real repos (sanitized)

**In Practice:**
- Incident reports published on egos.ia.br after resolution
- Cost breakdowns visible in agent execution logs
- Governance change rationale documented in commit messages
- Capability Registry searchable and filterable on website

---

### 5. **Autonomous Intelligence Within Hard Boundaries**

We believe autonomy without rules = chaos. Autonomy with rules = trust.

Agents should be given as much freedom as possible *within their safety boundaries*.

**The Boundary Principle:**
- Define what an agent CAN do (file paths, API calls, LLM choice)
- Define what an agent MUST do (logging, dry-run mode, post-execution review)
- Define what an agent CANNOT do (delete production, make security exceptions, violate SSOT)
- Within those bounds, let the agent choose its own execution path

**Why This Matters:**
- Human operators can sleep knowing agents won't break critical systems
- Agents have enough freedom to be creative and effective
- Violations are caught at commit time, not in production
- Rules are *protective*, not *restrictive*

**In Practice:**
- Security Scanner agent: Can read code, flag issues, suggest fixes. Cannot merge PRs or deploy.
- Code Reviewer agent: Can read/comment, propose changes. Cannot commit without human approval.
- UI Designer agent: Can generate Figma frames, test responsive layouts. Cannot modify production design tokens.
- Each agent has explicit `.windsurfrules` entry defining its sandbox

---

### 6. **You Own Your Governance DNA**

We believe lock-in is the enemy of trust.

Your governance rules live in plain-text markdown and YAML in `.guarani/`. You own them entirely.

**Portability:**
- Fork EGOS? Your rules come with you
- Migrate to a different framework? Export your rules as a migration guide
- Governance is not locked in our product; it's locked in your repository
- You can read, modify, and version-control every rule

**No Vendor Lock:**
- Core runtime (`runner.ts`) is frozen but readable
- All tooling is open-source (MIT)
- Event bus is decentralized; you can plug in your own
- Cost tracking doesn't require our SaaS; it's local-first

**In Practice:**
- `.guarani/DESIGN_IDENTITY.md` is human-readable markdown
- `DOMAIN_RULES.md` is YAML you can validate offline
- Pre-commit hooks are bash scripts, not platform magic
- You can run `bun governance:check` entirely offline

---

## Secondary Beliefs

### 7. **Speed Matters. Governance Shouldn't Slow You Down.**

Good governance is *fast* governance.

- `egos-init` should work in <2 minutes
- `governance:check` should run in <30 seconds
- Agent dry-run should show results in <10 seconds
- Governance rules should be human-readable (not compiled bytecode)

**When Governance is Slow, People Skip It.** We optimize for speed first.

---

### 8. **Simple Rules, Not Complicated Rules**

We believe complex governance creates loopholes.

- Rules should be readable in <5 minutes
- Edge cases are *documented*, not baked into rule logic
- If a rule is hard to understand, it's a bad rule
- Simplicity breeds compliance

---

### 9. **Community Over Hierarchy**

We believe governance shouldn't be top-down.

- Contributors can propose rule changes
- Rules are debated openly in PRs
- No secret governance councils
- "Benevolent operator" model: we facilitate, but community decides

---

### 10. **Evidence of Work > Promises of Work**

We believe "coming soon" is noise.

- Ship working features (not roadmaps)
- Show case studies with real numbers
- Publish incident reports and what you learned
- Under-promise, over-deliver

---

## What We DON'T Believe

### ❌ "Agents Should Have No Rules"
Autonomous agents with no governance are unpredictable and dangerous. Boundaries are protective.

### ❌ "Governance is a Cost Center"
Governance infrastructure *reduces* costs by preventing incidents, drift, and audit failures.

### ❌ "One Framework for Everything"
EGOS is opinionated. If you hate governance-first design, pick something else. We're not for you, and that's okay.

### ❌ "Developer Experience = Ease of Use"
True DX is ease of understanding. We ship docs, examples, and case studies. We don't hide complexity.

### ❌ "Community Governance = Slow Governance"
With async voting and clear processes, community governance is *faster* than centralized control.

### ❌ "Open-Source = Free Support"
We ship MIT-licensed code. We provide docs and examples. We don't guarantee 24/7 support. (Paid support is a separate offering.)

---

## Values in Action: Real Scenarios

### Scenario 1: An Agent Hallucination Happens

**The Event:** Code Review Agent suggests deleting a "test file" that is actually critical infrastructure.

**Our Values in Action:**
1. Pre-commit hook catches the deletion (Governance is Infrastructure) ✓
2. Incident is logged with correlation ID and rule version (Evidence-Driven) ✓
3. Report published: "Why rule X failed" → propose improvement (Transparency) ✓
4. Community votes on new rule that prevents this class of error (Community Evolves) ✓
5. Agent sandbox is tightened (just right boundaries) ✓

**Result:** Operator sleeps soundly. Incident was *prevented*, not discovered in production.

---

### Scenario 2: A New Governance Rule Needs to Exist

**The Proposal:** "Agents shouldn't use OpenAI when Alibaba Qwen is available (cost savings)"

**Our Values in Action:**
1. Team proposes change in PR to `DOMAIN_RULES.md` (Community Evolves) ✓
2. Proposal includes evidence: "Qwen is 3x cheaper, same quality on 80% of tasks" (Evidence-Driven) ✓
3. Discussion is open; someone argues "Qwen has higher latency" (Transparency) ✓
4. Compromise: "Use Qwen by default, except for latency-critical paths" (Rules, not hacky code) ✓
5. Rule is signed, merged, symlink propagates to all 7 repos (Governance is Infrastructure) ✓
6. All future agent runs follow the new rule (Rules Govern Agents) ✓

**Result:** Cost savings achieved. Community debate made the rule better. All repos synchronized.

---

### Scenario 3: Governance Change Causes an Incident

**The Event:** New rule forbids agents from writing to `/tmp`, but an agent legitimately needs temp storage.

**Our Values in Action:**
1. Incident is logged with full context (Evidence-Driven) ✓
2. Archaeology agent traces the incident to the rule change commit (Transparency) ✓
3. Postmortem shows rule was well-intentioned but incomplete (You Own Your Rules) ✓
4. Community proposes: "Forbid `/tmp` writes EXCEPT for `.cache/` directories" (Community Evolves) ✓
5. Rule is refined, re-signed, propagated (Governance is Infrastructure) ✓
6. Future versions of the agent work with the updated rule (Agents Enforce Rules) ✓

**Result:** Incident resolved. System is now more resilient. Community trust increases.

---

## The EGOS Covenant

By using EGOS, you agree:

1. **You will define your governance rules explicitly.** (No "security by obscurity")
2. **You will evolve rules openly with your community.** (No locked-in mandates)
3. **You will make decisions based on evidence.** (Not hunches)
4. **You will operate transparently.** (Incidents, costs, changes are visible)
5. **You will respect agent boundaries.** (Autonomy requires clear limits)

In return, EGOS promises:

1. **Your governance rules are yours to keep.** (No lock-in)
2. **Your agents will stay bounded.** (Pre-commit enforcement)
3. **Your costs will be visible.** (Tracking, not surprises)
4. **Your incidents will be preventable.** (Evidence-driven governance)
5. **Your community will help you grow.** (Shared ownership of rules)

---

## The EGOS Manifesto, Condensed

> **Governance is infrastructure, not overhead.**
> **Rules precede execution. Agents execute rules. Communities evolve rules.**
> **Autonomy thrives within clear boundaries.**
> **Transparency breeds trust. Secrets breed incidents.**
> **You own your governance DNA. Portability is freedom.**
> **Evidence is our north star. Hunches are logs, not decisions.**
> **Simple rules, not complicated loopholes.**
> **Community over hierarchy. Collaboration over mandates.**
> **Show proof, not promises. Ship code, not roadmaps.**

---

*EGOS makes governed AI agents. We believe the future of AI is not unconstrained autonomy, but autonomy with clear, community-defined boundaries. We build the infrastructure for that future.*


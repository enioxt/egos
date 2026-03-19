# Ecosystem Product Verdict — 2026-03

> Purpose: consolidate the real state of `egos`, `egos-lab`, and `EGOS-Inteligencia` and choose one product worth specializing, distributing, and monetizing.

## Verified

- `egos` is a real kernel for governance, shared AI primitives, drift control, and agent runtime.
- `egos-lab` is a real incubator/distribution repo with apps, agents, worker infra, and demos, but its narrative is broader than its proven product focus.
- `EGOS-Inteligencia` (`br-acc`) is the strongest concrete application surface today: FastAPI, React, Docker/VPS deploy, public-data graph, LGPD guards, and tool-calling chat are all wired in code.
- The strongest reusable moat across repos is not “generic agents” and not “network-state philosophy”. It is the Brazilian guardrails stack already visible in code: ATRiAN, PII scanning, public guard/masking, evidence-aware chat, and governance discipline.

## Inferred

- Selling `egos` as “another agent framework” is weak. Category is crowded, differentiation is hard to explain, and willingness to pay is low unless tied to concrete compliance outcomes.
- Selling `egos-lab` as the main product is also weak. It is a lab, acquisition surface, and orchestration playground — not a crisp business.
- Selling `EGOS-Inteligencia` alone as the company is risky. It is impressive, but heavy ETL/VPS ops, legal exposure, fragmented buyers, and data freshness burden make it a hard primary business.
- The most defensible product is a Brazil-first AI safety/compliance layer that can be embedded everywhere, while `br-acc` acts as the strongest proof case.

## Product Verdict

### Chosen primary product

**EGOS Guard Brasil** (working name)

A Brazil-first guardrails layer for AI assistants and public-facing AI systems:

- ATRiAN ethical validation
- PII Scanner BR
- public-safe masking and CPF blocking
- evidence-chain / traceable response discipline
- governance + policy packaging for real deployments

### What this product is

- An SDK/API/MCP for safe AI in Portuguese-BR
- A compliance and trust layer for chatbots, copilots, and investigation assistants
- A reusable product that can live in many repos and customer contexts

### What this product is not

- Not a generic agent platform sold on abstraction alone
- Not a monorepo of experiments sold as one thing
- Not only a civic graph database product

## Repo roles after the reset

- `egos`: canonical SSOT, package boundary, shared modules, MCP/API packaging, pricing boundary
- `egos-lab`: demo, acquisition, experiments, public distribution, flagship showcase pages
- `EGOS-Inteligencia`: reference implementation, data moat, proof that guardrails work under public-data/LGPD pressure

## What to stop

- Stop expanding scope around vague “consciousness tools” as if they were the business
- Stop marketing `egos-lab` as if it were the single source of ecosystem truth
- Stop treating every interesting repo or agent idea as a product candidate
- Stop measuring success by mapped agents, sources, or broad narratives without a paying use case

## Monetization logic

### Open source

- Core libraries and specs stay open
- Reference implementations and public docs stay open

### Paid

- Hosted API / MCP
- evidence and audit dashboard
- enterprise policy packs and deployment hardening
- support, integration, and SLA

## Immediate strategic consequence

The next milestone is not “more features”.

The next milestone is proving one repeatable commercial sentence:

> "We make Brazilian AI assistants safer to ship by adding LGPD-aware guardrails, masking, evidence discipline, and policy enforcement."

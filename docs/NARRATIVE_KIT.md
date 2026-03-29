# EGOS Narrative Kit — 1-Page Pitch

> **SSOT Owner:** `egos/docs/NARRATIVE_KIT.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-117

---

## The 60-Second Pitch

**The problem:**
Brazilian organizations are deploying AI assistants in hospitals, law enforcement, courts, and banks. Generic AI safety tools miss Brazilian PII entirely (CPF, MASP, REDS), don't understand PT-BR compliance patterns, and provide no audit trail for LGPD accountability.

**What we built:**
`@egos/guard-brasil` — a drop-in SDK that intercepts AI outputs before they reach users, masks Brazilian personal identifiers, validates ethical claims via ATRiAN scoring, and generates a tamper-evident evidence chain per response.

**The proof:**
br-acc (EGOS-Inteligência) runs it in production for police and judicial AI systems. 15 unit tests. Zero false negatives on CPF/MASP/REDS patterns.

**The ask / the offer:**
`npm install @egos/guard-brasil` — free, MIT. If you need the hosted API with compliance dashboard and audit logs, that's R$199/mo.

---

## Architecture Map (text)

```
Your LLM response
       ↓
@egos/guard-brasil
   ├── ATRiAN — scores for absolute claims, fabricated citations, false promises (0–100)
   ├── PII Scanner BR — detects CPF, RG, MASP, REDS, placa, processo, phone, email
   ├── Public Guard — masks or blocks, generates LGPD disclosure
   └── Evidence Chain — attaches sources to claims, produces audit hash
       ↓
Safe output + LGPD disclosure + audit hash
```

---

## Proof Checklist

Before any demo or meeting, verify these are true:

- [ ] `bun test packages/guard-brasil/src/guard.test.ts` — 15/15 pass
- [ ] `bun run packages/guard-brasil/src/demo.ts` — clean output
- [ ] Package version in `packages/guard-brasil/package.json` is current
- [ ] README example code is runnable (copy-paste test)
- [ ] br-acc reference: can explain what it does in 1 sentence

---

## FAQ — Pre-emptive answers

**"How is this different from AWS Comprehend?"**
AWS misses MASP, REDS, CASP entirely. We were built for Brazilian government systems. Plus we validate ethical claims — Comprehend doesn't.

**"Can I self-host?"**
Yes — the entire SDK is MIT. Install from npm, no phone-home, no API key required for the core.

**"What does the paid tier add?"**
REST API endpoint, compliance dashboard, audit log retention, SLA. Core SDK is always free.

**"Is it production-ready?"**
br-acc runs it in police AI systems today. The SDK has 15 tests with 100% pass rate.

**"What if my AI isn't in PT-BR?"**
ATRiAN's PII scanner works on mixed-language text. English responses with Brazilian identifiers still get caught.

---

## Competitive Landscape (one-liner each)

| Competitor | Why we win |
|-----------|-----------|
| AWS Comprehend PII | Misses Brazilian gov IDs; no ethics layer |
| Azure Content Safety | Harm detection, not compliance + evidence |
| LangChain parsers | Structure, not LGPD + audit accountability |
| Homegrown regex | Unmaintained, no ethics, no evidence chain |
| Doing nothing | LGPD fines up to 2% revenue, R$50M cap |

---

## Contact / Distribution

- **npm:** `npm install @egos/guard-brasil` (free, MIT)
- **Docs:** github.com/enioxt/egos/tree/main/packages/guard-brasil
- **Demo:** `bun run packages/guard-brasil/src/demo.ts`
- **Enio Rocha:** enio@egos.ia.br

---

*Maintained by: EGOS Kernel*
*Related: EGOS-117, docs/PRESENTATION_SYSTEM.md, docs/strategy/FLAGSHIP_BRIEF.md*

# Quorum Decision: CLAUDE.md v4.0 Refactor
> **Date:** 2026-04-10 | **Topic:** Global CLAUDE.md restructure
> **LLMs consulted:** Gemini, Grok, GPT-4o, Perplexity
> **Human:** Enio Rocha (approved)
> **Orchestrator:** Claude Opus 4.6

## Consensus (4/4 agree)
1. File was obese (772 lines) — cut to ~400 target
2. Mixed hard rules with philosophy — separate into tiers
3. §6 Response Quality, §10 Useful Repos, §22 Chatbot Everywhere — eliminate
4. §12/28/29 redundant — merge or eliminate
5. §17 Snapshot Versioning — aspirational, eliminate
6. §15 Autonomy vs §3 Edit Safety tension — needs precedence rule
7. Missing: rollback protocol, cost control, rule precedence

## Key divergences
- §16 Challenge Mode: Grok=A (essential), Gemini/Perplexity=D/E. Resolution: merged into §10 Posture (2 lines).
- §24 Enio Profile: Grok=A, Gemini=D. Resolution: compressed to 6 lines in §12.
- §33 Evidence-First: ChatGPT noted "half rule, half intention". Resolution: kept core rule, moved history to docs.

## Execution
- 772 → 263 lines (66% reduction)
- 14 tiers → 5 tiers with explicit precedence (T0>T1>T2>T3>T4)
- Eliminated: §6-old, §10-old, §16-old, §17-old, §18-old, §22-old, §28, §29
- Added: Rule Precedence (header), Rollback Protocol (§10), Cost Control (§6), Quorum Protocol (§9)
- Recovered from archived: vocabulary_learner speech patterns → §11

## Backup
`~/.claude/CLAUDE_MD_v3.3_pre_refactor_backup.md` (772 lines, full git history available)

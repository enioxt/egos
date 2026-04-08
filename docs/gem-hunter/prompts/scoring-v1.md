# Gem Hunter — Scoring Prompts v1.0
# SSOT: extracted from gem-hunter.ts 2026-04-08
# Version: 1.0.0 | Edit this file → redeploy gem-hunter to apply
# Related tasks: GH-089 (extraction), GH-091 (Qwen-based general scoring), GH-097 (evolver)

---

## 1. Executive Synthesis Prompt (gem-hunter.ts:1642)

Used to summarize top gems for the weekly digest.

```
You are a senior tech lead evaluating tools discovered via an automated scout agent for the EGOS lab. 
EGOS is an advanced, rules-based, agentic TypeScript/Python ecosystem that values zero-dependency, 
mathematical rigor (Sacred Math), and topological software resilience (like VRCP).

Analyze the following top discovered gems and write a concise, bulleted Executive Synthesis (max 300 words) 
explaining *why* these specific tools, frameworks, or papers matter for our architecture, and which 1-2 
we should prioritize adopting or reading:

{topGems}
```

---

## 2. Paper Abstract Triage Prompt (gem-hunter.ts:2274 — GH-056)

Used for papers-with-code and research gems. Scores 0-100.

```
Score this research paper abstract for relevance to an EGOS multi-agent TypeScript platform that does: 
orchestration, governance-as-code, crypto gem hunting, and Brazilian compliance. 
Reply ONLY with a JSON object: {"score": 0-100, "reason": "one sentence"}.

Title: {paper.name}
Abstract: {paper.description.slice(0, 400)}
```

---

## 3. scoreGem() Heuristic Logic (gem-hunter.ts:1778 — NOT LLM-based)

Current scoring is deterministic. Key rules:

| Rule | Points |
|------|--------|
| relevance=high (base) | +50 |
| relevance=medium (base) | +30 |
| relevance=low (base) | +10 |
| stars (log scale, max 20) | +0..20 |
| downloads (log scale, max 12) | +0..12 |
| updated ≤30 days | +14 |
| updated ≤90 days | +8 |
| arXiv citation in text | +18 |
| paper-backed signals | +12 |
| research structure | +10 |
| low-star (<20) + research signals | +15 ("hidden gem bonus") |
| papers-with-code source | +12 |
| github/npm source | +5 |
| YouTube/Medium/LinkedIn URL | -15 |
| CJK majority text | -30 |
| X signal not relevant | -20 |
| X signal relevant | +18 |
| Official strategic source (github/modelcontextprotocol) | +12 |
| Strategic noise (medium/linkedin) | -10 |
| abstractScore ≥70 (LLM paper score) | +(abstractScore-69)/3 |
| structureBonus (validation pass) | variable |
| crossSourceBonus (PWC+arXiv cross-validation) | variable |

### isXSignalRelevant() criteria
Returns true if post matches early warning signals OR general tech AND not a profile:
```
isEarlyWarning: /harness|lightweight|pure python|minimal agent|initial commit|v0\.1|44x|3% of|claude code alternative|.../
isGeneral: /github|open source|release|crawler|scraper|browser|agent/
reject: /posts \/ x|profile|account/
```

---

## 4. GAP: Low-Visibility Gem Category (GH-091 — TODO)

**Problem:** Engineers from big-tech (Meta, Google, OpenAI) posting real code with few likes are NOT captured.
Current scoring relies on stars/downloads/arXiv — misses:
- Verified tech employee (company in bio) posting production code snippet
- Novel approach without academic framing
- Tool solving a niche problem (few likes but exactly what EGOS needs)

**Proposed addition to scoreGem():**
```typescript
// GH-091: Low-visibility big-tech engineer gem
// Big-tech company in author bio + code content + no follower-bait language
const bigTechBio = /(meta|google|openai|anthropic|deepmind|apple|microsoft|amazon|nvidia)\s*(researcher|engineer|swe|ml|ai)/i.test(gem.authorBio ?? "");
const hasCodeContent = /```|github\.com|npm install|pip install|const |function |def |class /.test(gem.description);
const isFollowerBait = /(retweet|follow me|like if|thread [↓⬇])/i.test(gem.description);
if (bigTechBio && hasCodeContent && !isFollowerBait) {
  score += 25; // "low-visibility engineering gem" — these ARE the gems we want
}
```

---

## 5. Few-Shot Examples (XRB-002 — from 8 posts analyzed 2026-04-08)

### GEMS (score up)
- **@vacacafe**: Research into agentic patterns, novel framing, no hype
- **@MrCl0wnLab**: Security tooling, real code, niche use case
- **@PreyWebthree**: Web3 + ethics + AI intersection (rare triple signal)
- **@zhuokaiz**: Meta engineer posting real implementation code, few stars but genuine value
- **@TFTC21**: Bitcoin/crypto research signal, verifiable technical content

### REJECT (score down)
- **@hasantoxr**: Repetitive content, low interaction margin, seen before
- **@LOWTAXALT**: Correctly rejected by current scoring — noise, not signal
- **@claudeai (official)**: Anthropic official account announcing features = PR, not discovery gem

### Scoring principle derived:
> "A gem is a signal BEFORE it's popular. Official announcements are never gems — they're already known."

---

## 6. News-Post Detector (XRB-004 — TODO)

**Proposed rule:** If author is official account (verified big-tech brand) + post contains announcement language → heavy penalty.

```typescript
const isOfficialCorporateAccount = /(claudeai|openai|anthropic|googledeepmind|metaai|microsoft)/i.test(gem.authorHandle ?? "");
const isAnnouncementPost = /(announcing|introducing|launching|we're excited|new feature|now available|rolling out)/i.test(gem.description);
if (isOfficialCorporateAccount && isAnnouncementPost) {
  score -= 40; // "corporate PR penalty" — not a discovery gem
}
```

---

## Versioning

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-04-08 | Extracted from gem-hunter.ts — baseline documentation |
| v1.1 | pending | Add GH-091 low-visibility big-tech engineer gem rule |
| v1.2 | pending | Add XRB-004 news-post detector |
| v2.0 | pending | GH-097: full LLM-based scoring (Qwen replaces heuristics) |

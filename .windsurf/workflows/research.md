---
description: "Universal Research Protocol — Multi-modal intelligence gathering before implementation"
---

# /research — Universal Research Protocol (Agnostic v2.0)

> **Works in:** ANY repo | **When:** Before implementing anything unfamiliar

---

## Step 1: Define Research Scope

```
⚠️  AI AGENT: Before researching, answer these:

1. WHAT am I researching? [topic/technology/pattern]
2. WHY do I need this? [what decision depends on it]
3. WHERE should I look? [docs, web, codebase, KIs]
4. HOW DEEP? [surface scan / deep dive / comprehensive]
```

## Step 2: Check Existing Knowledge // turbo

```bash
printf "═══════════════════════════════════════════════════════════\n"
printf "🔍 CHECKING EXISTING KNOWLEDGE\n"
printf "═══════════════════════════════════════════════════════════\n\n"

# Check project docs
ROOT="$PWD"; CUR="$ROOT"
while [ "$CUR" != "/" ] && [ ! -e "$CUR/.git" ]; do CUR="$(dirname "$CUR")"; done
[ -e "$CUR/.git" ] && ROOT="$CUR"

printf "📂 Project docs:\n"
find "$ROOT/docs" -name "*.md" -maxdepth 2 2>/dev/null | head -15
printf "\n"

printf "📋 Shared knowledge:\n"
ls ~/.egos/guarani/*.md 2>/dev/null
printf "\n"
```

## Step 3: Multi-Modal Search

```
⚠️  AI AGENT: Use ALL available sources in this order:

1. 🧠 Memory MCP — search_nodes for prior knowledge
2. 📚 Knowledge Items — check KI summaries
3. 🔍 Codebase — grep_search for existing patterns
4. 🌐 Web — search_web or Exa for external info
5. 📖 Docs — official documentation of libraries/APIs
```

## Step 4: Synthesize & Document

```
⚠️  AI AGENT: After researching, produce:

1. Summary of findings (2-4 paragraphs)
2. Decision recommendation (with pros/cons)
3. Save to Knowledge Base if reusable:
   - Memory MCP: create_entities for key concepts
   - Or: save_web_knowledge for external findings
```

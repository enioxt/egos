---
description: "Collect and interpret all project governance rules (SSOT)"
---

# /regras — Governance Rules Collector (Agnostic v2.0)

> **Works in:** ANY repo | **When:** Need to understand all active rules

---

## Process // turbo

```bash
printf "═══════════════════════════════════════════════════════════\n"
printf "📜 EGOS RULES COLLECTOR\n"
printf "═══════════════════════════════════════════════════════════\n\n"

ROOT="$PWD"; CUR="$ROOT"
while [ "$CUR" != "/" ] && [ ! -e "$CUR/.git" ]; do CUR="$(dirname "$CUR")"; done
[ -e "$CUR/.git" ] && ROOT="$CUR"

REPO_NAME=$(basename "$ROOT")
printf "📂 Scanning rules for: %s\n\n" "$REPO_NAME"

# Layer 1: Shared EGOS
printf "🌐 Layer 1 — Shared EGOS (~/.egos/):\n"
for f in ~/.egos/guarani/*.md; do
  [ -f "$f" ] && printf "   📄 %s\n" "$(basename "$f")"
done
printf "\n"

# Layer 2: Local overrides
printf "📂 Layer 2 — Local Overrides (.guarani/):\n"
if [ -d "$ROOT/.guarani" ]; then
  for f in "$ROOT"/.guarani/*.md; do
    [ -f "$f" ] && printf "   📄 %s\n" "$(basename "$f")"
  done
else
  printf "   ℹ️  No local .guarani/\n"
fi
printf "\n"

# Layer 3: Agent rules
printf "🤖 Layer 3 — Agent Rules:\n"
[ -f "$ROOT/.windsurfrules" ] && printf "   📄 .windsurfrules (Windsurf)\n"
[ -f "$ROOT/.cursorrules" ] && printf "   📄 .cursorrules (Cursor)\n"
[ -f "$ROOT/AGENTS.md" ] && printf "   📄 AGENTS.md\n"
printf "\n"

# Layer 4: Workflows
printf "⚡ Layer 4 — Workflows:\n"
SHARED_WF=$(ls ~/.egos/workflows/*.md 2>/dev/null | wc -l)
LOCAL_WF=$(ls "$ROOT"/.windsurf/workflows/*.md "$ROOT"/.agent/workflows/*.md 2>/dev/null | wc -l)
printf "   Shared: %s workflows\n" "$SHARED_WF"
printf "   Local:  %s workflows\n\n" "$LOCAL_WF"

printf "Precedence: Local .guarani/ > Shared .egos/ > Agent rules > Workflows\n"
printf "═══════════════════════════════════════════════════════════\n"

printf "\n⚠️  AI AGENT: Read ALL files listed above and synthesize into a rules summary.\n"
```

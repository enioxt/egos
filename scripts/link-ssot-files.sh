#!/bin/sh
set -e

MODE="${1:---dry}"
TARGET_REPO="${2:-$HOME/egos-lab}"
EGOS_HOME="${EGOS_HOME:-$HOME/.egos}"

GUARANI_FILES="
DESIGN_IDENTITY.md
ENGINEERING_STANDARDS_2026.md
SEPARATION_POLICY.md
orchestration/DOMAIN_RULES.md
orchestration/GATES.md
orchestration/PIPELINE.md
orchestration/QUESTION_BANK.md
philosophy/TSUN_CHA_PROTOCOL.md
preprocessor.md
prompts/PROMPT_SYSTEM.md
prompts/meta/brainet-collective.md
prompts/meta/mycelium-orchestrator.md
prompts/meta/universal-strategist.md
prompts/triggers.json
refinery/README.md
refinery/classifier.md
refinery/compiler.md
refinery/interrogators/bug.md
refinery/interrogators/feature.md
refinery/interrogators/knowledge.md
refinery/interrogators/refactor.md
refinery/vocabulary_learner.md
security/SEC-001_PHONE_BRIDGE.md
security/SEC-002_VPS_HARDENING.md
standards/MCP_TOOL_QUALITY_FRAMEWORK.md
tools/code-health-monitor.ts
tools/privacy-scanner.ts
"

WORKFLOW_FILES="prompt.md regras.md research.md start.md pre.md end.md disseminate.md"

link_if_exact() {
  src="$1"
  dst="$2"
  kind="$3"
  if [ ! -f "$src" ] || [ ! -e "$dst" ]; then return; fi
  if [ -L "$dst" ]; then echo "OK   $kind $dst"; return; fi
  if ! cmp -s "$src" "$dst"; then echo "SKIP $kind $dst (drift)"; return; fi
  if [ "$MODE" = "--exec" ]; then
    rm "$dst"
    ln -s "$src" "$dst"
    echo "LINK $kind $dst"
  else
    echo "DRY  $kind $dst"
  fi
}

echo "SSOT linker"
echo "Mode: $MODE"
echo "Repo: $TARGET_REPO"

for rel in $GUARANI_FILES; do
  link_if_exact "$EGOS_HOME/guarani/$rel" "$TARGET_REPO/.guarani/$rel" "guarani"
done

for rel in $WORKFLOW_FILES; do
  link_if_exact "$EGOS_HOME/workflows/$rel" "$TARGET_REPO/.windsurf/workflows/$rel" "windsurf"
  link_if_exact "$EGOS_HOME/workflows/$rel" "$TARGET_REPO/.agent/workflows/$rel" "agent"
done

echo "Done. Drifted files were intentionally skipped."

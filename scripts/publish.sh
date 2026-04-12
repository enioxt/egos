#!/usr/bin/env bash
# publish.sh — TL-003 Manual article trigger + approval
#
# Usage:
#   bash scripts/publish.sh "topic about the commit"                  # generate draft from HEAD
#   bash scripts/publish.sh "topic about the commit" <commit-hash>    # generate draft from commit
#   bash scripts/publish.sh "topic about the commit" --dry-run        # preview only
#   bash scripts/publish.sh --approve <draft-id>                      # approve → publish + KB sync
#   bash scripts/publish.sh --approve-all                             # publish all approved drafts
#
# If no hash provided: uses HEAD.
# Prints draft ID and review link on success.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Quick-approve shortcut ──────────────────────────────────────────────────

if [[ "${1:-}" == "--approve" ]]; then
  DRAFT_ID="${2:-}"
  if [[ -z "${DRAFT_ID}" ]]; then
    echo "❌ Usage: bash scripts/publish.sh --approve <draft-id>"
    exit 1
  fi
  echo "🚀 Approving and publishing draft: ${DRAFT_ID}"
  bun run "${REPO_ROOT}/agents/agents/article-writer.ts" --publish "${DRAFT_ID}"
  exit $?
fi

if [[ "${1:-}" == "--approve-all" ]]; then
  echo "🚀 Publishing all approved drafts..."
  bun run "${REPO_ROOT}/agents/agents/article-writer.ts" --publish-all
  exit $?
fi

# ── Parse args ──────────────────────────────────────────────────────────────

TOPIC="${1:-}"
COMMIT_HASH="HEAD"
DRY_RUN=""

if [[ -z "${TOPIC}" ]]; then
  echo "❌ Usage: bash scripts/publish.sh \"topic about the commit\" [commit-hash] [--dry-run]"
  echo "   Examples:"
  echo "     bash scripts/publish.sh \"Hermes decommission\""
  echo "     bash scripts/publish.sh \"Hermes decommission\" ae7b9ad"
  echo "     bash scripts/publish.sh \"test article\" --dry-run"
  echo "     bash scripts/publish.sh --approve <draft-id>"
  exit 1
fi

# Shift past the topic arg and parse remaining args
shift
for arg in "$@"; do
  if [[ "${arg}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
  elif [[ "${arg}" != -* ]]; then
    COMMIT_HASH="${arg}"
  fi
done

# ── Run article writer ───────────────────────────────────────────────────────

echo "📝 Publishing article for commit ${COMMIT_HASH}"
echo "   Topic: ${TOPIC}"
if [[ -n "${DRY_RUN}" ]]; then
  echo "   Mode: DRY-RUN"
fi
echo ""

CMD="bun run ${REPO_ROOT}/agents/agents/article-writer.ts --commit ${COMMIT_HASH} --topic \"${TOPIC}\""
if [[ -n "${DRY_RUN}" ]]; then
  CMD="${CMD} --dry-run"
fi

# Capture output and extract draft ID
OUTPUT=$(eval "${CMD}" 2>&1)
echo "${OUTPUT}"

# Extract draft ID from output (article-writer prints DRAFT_ID=xxx on last line when LIVE)
DRAFT_ID=$(echo "${OUTPUT}" | grep "^DRAFT_ID=" | tail -1 | cut -d= -f2 || true)

echo ""
if [[ -n "${DRAFT_ID}" && -z "${DRY_RUN}" ]]; then
  echo "✅ Draft created: ${DRAFT_ID}"
  echo "   Review at: https://hq.egos.ia.br/timeline/pending"
elif [[ -n "${DRY_RUN}" ]]; then
  echo "✅ Dry-run complete — no draft inserted."
else
  echo "ℹ️  Review at: https://hq.egos.ia.br/timeline/pending"
fi

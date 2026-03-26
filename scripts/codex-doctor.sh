#!/usr/bin/env bash
set -euo pipefail

printf "EGOS Codex Doctor\n"
printf "=================\n"
printf "Date (UTC): %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf "Repo: %s\n\n" "$(pwd)"

printf "[1/5] Environment\n"
if command -v bun >/dev/null 2>&1; then
  printf "  ✅ bun: %s\n" "$(bun --version)"
else
  printf "  ❌ bun not found\n"
fi
if command -v git >/dev/null 2>&1; then
  printf "  ✅ git: %s\n" "$(git --version)"
else
  printf "  ❌ git not found\n"
fi

printf "\n[2/5] Governance baseline\n"
if [ -f .windsurfrules ] && [ -f AGENTS.md ] && [ -f TASKS.md ]; then
  printf "  ✅ Core SSOT files present\n"
else
  printf "  ❌ Missing one or more SSOT files (.windsurfrules, AGENTS.md, TASKS.md)\n"
fi

printf "\n[3/5] Network check\n"
if curl -sSfL --max-time 10 https://api.github.com/repos/SynkraAI/aiox-core >/dev/null; then
  printf "  ✅ External GitHub API reachable\n"
else
  printf "  ⚠️ GitHub API unreachable (network or rate-limit)\n"
fi

printf "\n[4/5] Codex lane limitations (MANDATORY DISCLOSURE)\n"
printf "  - This session runs in Codex terminal lane (non-interactive by default).\n"
printf "  - Browser/UI actions may be unavailable unless a dedicated browser tool is exposed.\n"
printf "  - Home-level governance sync state may reset between runs in ephemeral environments.\n"
printf "  - Push/deploy actions are not assumed; explicit repo remote actions still require operator decision.\n"

printf "\n[5/5] Recommended next commands\n"
printf "  - bun run agent:lint\n"
printf "  - bun run typecheck\n"
printf "  - bun test\n"
printf "  - bun run governance:sync:exec && bun run governance:check\n"

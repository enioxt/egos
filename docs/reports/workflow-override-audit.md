# Workflow Override Audit — EGOS-016

> **Date:** 2026-03-13 | **Auditor:** Cascade
> **Kernel versions:** start v5.4, end v5.3, disseminate v5.3, mycelium v1.0

## Summary

- **1 legitimate override** (egos-lab mycelium.md — richer lab-specific surfaces)
- **9 stale overrides** across br-acc, forja, egos-self (old v5.0/v5.1 copies)

## Detail

| Repo | File | Local Ver | Kernel Ver | Verdict |
|------|------|-----------|------------|---------|
| egos-lab | mycelium.md | 98 lines (custom) | 46 lines | LEGITIMATE — lab has session:guard, gem-hunter, worker surfaces |
| br-acc | start.md | v5.1 | v5.4 | STALE — missing capability registry, chatbot SSOT dispatch, mycelium/chatbot triggers |
| br-acc | end.md | v5.0 | v5.3 | STALE — missing repo-role-aware phase, old formatting |
| br-acc | disseminate.md | v5.0 | v5.3 | STALE — missing capability registry update, Codex/Alibaba recording |
| forja | start.md | v5.1 | v5.4 | STALE — same as br-acc |
| forja | end.md | v5.0 | v5.3 | STALE — same as br-acc |
| forja | disseminate.md | v5.0 | v5.3 | STALE — same as br-acc |
| egos-self | start.md | v5.1 | v5.4 | STALE — same as br-acc |
| egos-self | end.md | v5.0 | v5.3 | STALE — same as br-acc |
| egos-self | disseminate.md | v5.0 | v5.3 | STALE — same as br-acc |

## What Stale Overrides Miss

The kernel v5.3/v5.4 workflows added:
1. Capability registry in core load order
2. Chatbot SSOT conditional dispatch
3. Mycelium trigger keywords
4. Repo-role-aware session:guard/gem-hunter/report-generator
5. Codex + Alibaba tooling checks
6. `ask_user_question` preference for setup/auth tasks
7. Capability registry update phase in /disseminate

## Remediation

For each stale repo, delete the local override so the kernel version takes effect:

```bash
# br-acc
rm /home/enio/br-acc/.windsurf/workflows/{start,end,disseminate}.md
~/.egos/sync.sh  # re-syncs kernel versions

# forja
rm /home/enio/forja/.windsurf/workflows/{start,end,disseminate}.md
~/.egos/sync.sh

# egos-self
rm /home/enio/egos-self/.windsurf/workflows/{start,end,disseminate}.md
~/.egos/sync.sh
```

The egos-lab mycelium.md override should be preserved as a legitimate local extension.

## Prevention

The kernel's `governance-sync.sh` already detects drift. To prevent future stale overrides:
- Run `bun run governance:check` in the kernel regularly
- `~/.egos/sync.sh` respects local overrides by design (safety feature)
- Document intentional overrides in each repo's AGENTS.md

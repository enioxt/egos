# Agent Message Signature Contract (Kernel)

> **Version:** 1.0.0  
> **Updated:** 2026-03-23  
> **Scope:** EGOS kernel + synced leaf governance

## Objective

Guarantee message provenance across multi-agent lanes (Windsurf, Codex, Claude Code, Antigravity, Alibaba/OpenRouter orchestrated agents).

Every agent-facing delivery MUST include a signature footer so operators can trace origin and execution context.

## Mandatory Footer Format

Use this exact block at the end of operational messages:

```text
---
Agent-Signature: <agent_id_or_tool>
Session-ID: <session_or_chat_id_or_n/a>
Mode: <dry|exec|analysis|review>
Source-Env: <codex|windsurf|claude|antigravity|google-ai-studio|api>
Timestamp-UTC: <ISO-8601 UTC>
Git-Repo: <owner/repo_or_local_path_or_n/a>
Git-Branch: <branch_or_n/a>
Git-Commit: <sha_or_n/a>
Git-Push-Remote: <remote_or_n/a>
---
```

## Required Fields

- `Agent-Signature`: stable identifier of the emitter (`codex`, `cascade`, `claude_code`, `orchestrator`, etc.)
- `Session-ID`: traceable session/chat id (or `n/a` if not available)
- `Mode`: execution posture
- `Source-Env`: environment/lane of origin
- `Timestamp-UTC`: UTC proof of emission
- `Git-Repo`: where changes were committed
- `Git-Branch`: branch used for commit/push
- `Git-Commit`: latest relevant commit SHA
- `Git-Push-Remote`: target remote for push (or `n/a`)

## Activation Rules

1. New sessions MUST load this contract during `/start`.
2. Any message without signature is **non-compliant** for governance-grade outputs.
3. For cross-repo propagation, run:
   - `bun run governance:sync:exec`
   - `bun run governance:check`
4. Leaf repos MAY add fields, but MUST keep all required fields.
5. If the message includes code changes, commit, or push status, Git fields are mandatory.

## Rollout Instruction to Other Agents

When delegating to other agents/tools, include this command:

> "Activate `AGENT_MESSAGE_SIGNATURE_CONTRACT.md` locally and enforce signature footer on every operational reply."

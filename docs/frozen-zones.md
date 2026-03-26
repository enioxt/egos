# Frozen Zones — EGOS Framework Core

> **Version:** 1.0.0 | **Updated:** 2026-03-13

## Rules

1. **Never edit** a frozen file without explicit user approval + proof-of-work.
2. Pre-commit hook enforces this automatically via checksum validation.
3. If a frozen file must change, document WHY in the commit message.

## Frozen Files

| File | Reason | Checksum Validated |
|------|--------|--------------------|
| `agents/runtime/runner.ts` | Core agent execution engine | Yes |
| `agents/runtime/event-bus.ts` | Core inter-agent communication | Yes |
| `.husky/pre-commit` | Enforcement gate — must not be weakened | Yes |
| `.guarani/orchestration/PIPELINE.md` | Master 7-phase protocol | Yes |
| `.guarani/orchestration/GATES.md` | Quality gate definitions | Yes |

## How to Request a Change

1. Open an issue or explicitly request in the IDE session.
2. Provide proof-of-work: why the change is necessary.
3. The change must pass all existing tests.
4. Codex review is mandatory for frozen zone changes.

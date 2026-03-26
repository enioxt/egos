---
description: "Google Stitch-first UI flow: prompt generation -> external creation -> zip intake"
---

# /stitch — Google Stitch UI Workflow (v1.0)

> **Policy:** All new screens MUST pass through Google Stitch before implementation.

## Objective

Generate a high-quality Stitch prompt in-chat, let the operator create UI externally in Stitch, then ingest the returned `.zip` into the target repo with traceability.

## Operating Model

1. **Agent generates prompt pack** (desktop + mobile + states + constraints).
2. **Operator runs Stitch externally** (`stitch.withgoogle.com`) and exports artifacts.
3. **Operator returns `.zip`** to this lane.
4. **Agent imports + maps** files to target codebase and opens integration tasks.

## Prompt Pack Template (Agent Output)

Use this exact structure:

```md
# Stitch Prompt Pack

## Product context
- Product:
- Screen name:
- Primary persona:
- Primary job-to-be-done:

## UX objective
- Outcome in one sentence:
- Success metric:

## Functional requirements
- Must-have blocks:
- Primary actions:
- Empty/loading/error states:

## Visual/system constraints
- Brand tone:
- Colors/typography:
- Accessibility baseline (contrast/focus/keyboard):
- Responsive behavior (mobile/tablet/desktop):

## Data realism
- Realistic sample entities/values:
- Localization/currency/date assumptions:

## Export instructions
- Export targets: HTML/CSS and/or Figma
- Include component naming consistency
```

## Zip Intake Contract

When `.zip` returns, agent MUST:

1. Create intake note in PR/task with source date + owner.
2. Extract and classify files (`design`, `assets`, `code`, `tokens`).
3. Map each file to destination path in target repo.
4. Open follow-up tasks for adaptation gaps (routing/state/data wiring/accessibility).
5. Keep raw export under a deterministic path like `design/stitch/<screen>/<yyyymmdd>/` (or target-repo equivalent).

## Definition of Done

- Stitch prompt pack generated and approved.
- `.zip` received and mapped.
- Integration tasks created with owner + priority.
- Evidence linked in PR/task (prompt used, zip hash/path, mapping table).


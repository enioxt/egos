# Spec-Pipeline Workflow Contract

> **Version:** 1.0.0 | **Status:** ACTIVE | **Updated:** 2026-03-26
> **Sacred Code:** 111.111.369.963.1618
> **Governance:** EGOS Kernel | **Enforcement:** pr:gate + GitHub Actions

---

## Purpose

Define the canonical workflow for specification and architectural review through a multi-stage pipeline:

```
analyst → pm → architect → sm
```

This contract ensures:
- **Role-based access control (RBAC)** per stage
- **Explicit handoff format** with mandatory evidence
- **Approval gates** (minimum 2 reviewers per stage)
- **Automatic task routing** to appropriate reviewers
- **SLA tracking** (24-hour approval window per stage)

---

## Overview

The spec-pipeline is a **sequential workflow** where each stage builds on the previous stage's evidence and approvals. It is triggered by adding the `spec-pipeline` label to a pull request.

### Workflow Stages

| Stage | Role | Duration | Gate |
|-------|------|----------|------|
| **1. Specification** | Analyst | Max 24h | 2 approvals required |
| **2. Product Review** | PM | Max 24h | 2 approvals required |
| **3. Architecture Review** | Architect | Max 24h | 2 approvals required |
| **4. Stakeholder Markup** | SM (Scrum Master) | Max 24h | 1 approval (final gate) |

### Core Principles

1. **Evidence-First:** Every stage must have proof before advancement
2. **Handoff Format:** Mandatory fields ensure clarity between stages
3. **Parallel Reviews:** Multiple reviewers can review simultaneously within a stage
4. **Transparency:** SLA tracking is visible on the PR
5. **No Backsliding:** Once approved by a stage, cannot regress to previous stage

---

## Roles & Permissions

### 1. Analyst

**Responsibility:** Define what needs to be built and why

**Mandatory Deliverables:**
- Problem statement (max 200 words)
- Success metric (measurable, time-bound)
- Acceptance criteria (min 3 items)
- User story/use case (if applicable)

**Permissions:**
- Can initiate spec-pipeline
- Can modify spec before PM approval
- Cannot approve architectural decisions
- Cannot change PM/Architect/SM approvals

**Required Approvals to Advance:**
- 2 reviewers from `CODEOWNERS.analyst`

---

### 2. Product Manager (PM)

**Responsibility:** Validate business value and feasibility

**Mandatory Deliverables:**
- Business impact assessment (link to OKRs or roadmap)
- Go/no-go decision (explicit recommendation)
- Risk assessment (market, timing, dependency risks)
- Scope confirmation or recommended scope cut

**Permissions:**
- Can request changes to spec from analyst
- Can modify product review before architect approval
- Cannot approve architecture
- Cannot override analyst evidence

**Required Approvals to Advance:**
- 2 reviewers from `CODEOWNERS.pm`

---

### 3. Architect

**Responsibility:** Validate technical feasibility and quality

**Mandatory Deliverables:**
- Architecture diagram or reference (link to docs/architecture/)
- Technical risks and mitigations (performance, scalability, debt)
- API/schema changes (if applicable)
- Implementation complexity assessment (T-shirt size: XS, S, M, L, XL)
- Dependency audit (new external deps, versions)

**Permissions:**
- Can request changes to PM review
- Can request spec clarifications (escalates to analyst)
- Can modify architecture before SM approval
- Cannot approve business decisions

**Required Approvals to Advance:**
- 2 reviewers from `CODEOWNERS.architect`

---

### 4. Stakeholder Manager (SM)

**Responsibility:** Final approval and signoff for implementation readiness

**Mandatory Deliverables:**
- Resource allocation confirmation
- Timeline and milestone mapping
- Communication plan (when/how teams are notified)
- Final readiness checklist

**Permissions:**
- Can request changes to architect review
- Can escalate to PM or analyst if issues found
- Final approval authority
- Can approve transition to implementation

**Required Approvals to Advance:**
- 1 approval from `CODEOWNERS.sm` (final gate)

---

## Handoff Format

Each stage transition MUST include a handoff comment in the PR with this format:

```markdown
## [STAGE_NAME] Handoff — [DATE/TIME]

### Status
- [ ] Evidence present and complete
- [ ] Approval gates met (min 2 reviewers)
- [ ] SLA within limit (< 24h)

### Summary
[1-2 sentence recap of what was reviewed and approved]

### Evidence Links
- Link to specification: [URL]
- Link to product review: [URL]
- Link to architecture docs: [URL]

### Next Stage Prepared
[Stage name] review is ready. Assign to `@[CODEOWNER_TEAM]`

### Reviewer Attribution
- Approved by @reviewer1, @reviewer2
- Decision timestamp: [ISO 8601]
```

### Mandatory Fields by Stage

**Analyst → PM Handoff:**
- Problem statement finalized ✅
- Success metric defined ✅
- Acceptance criteria locked ✅
- User story/use case documented ✅

**PM → Architect Handoff:**
- Business impact validated ✅
- Go/no-go decision recorded ✅
- Risk assessment completed ✅
- Scope confirmed (no scope creep risk) ✅

**Architect → SM Handoff:**
- Architecture diagram linked ✅
- Technical risks + mitigations ✅
- Implementation complexity sized ✅
- Dependency audit completed ✅

**SM → Implementation Ready:**
- Resource allocation confirmed ✅
- Timeline mapped ✅
- Communication plan drafted ✅
- Final readiness checklist green ✅

---

## Evidence Requirements

All stages must include **concrete proof**, not assumptions:

### Specification Stage

| Evidence Type | Requirement | Example |
|---------------|-------------|---------|
| **Screenshot** | User story mockup or current state | Link to Figma/screenshot |
| **Link** | Reference to docs, roadmap, or requirement | GH issue, Linear ticket, Google Doc |
| **Timestamp** | Decision made on [date/time] | ISO 8601 format |
| **Data** | Metrics or numbers backing the claim | "80% of users currently do X" |

### Product Review Stage

| Evidence Type | Requirement | Example |
|---------------|-------------|---------|
| **Link** | OKR or roadmap reference | e.g., "Q2 2026 roadmap: improve user onboarding" |
| **Risk Log** | 3+ identified risks with severity | "HIGH: New dependency on external API (failure mode: degraded UX)" |
| **Market Data** | Competitive analysis or user feedback | "3 customer requests for this feature in the past month" |
| **Timeline Estimate** | Rough estimate of execution time | "2-week effort based on architect input" |

### Architecture Review Stage

| Evidence Type | Requirement | Example |
|---------------|-------------|---------|
| **Diagram** | Architecture or flow diagram | Link to `/docs/architecture/` or embedded mermaid |
| **Code Reference** | Link to existing pattern or library | "Uses existing cache layer: `packages/cache/redis-client.ts`" |
| **Performance Impact** | Load testing or benchmarking (if applicable) | "Query time: 50ms → 100ms (acceptable)" |
| **Debt Assessment** | Any technical debt introduced | "Deferred: Migrate auth to OAuth 2.0 (Q3 2026)" |
| **Dependency List** | New external deps with version pins | "axios@1.6.0, zod@3.22.0" |

### SM Review Stage

| Evidence Type | Requirement | Example |
|---------------|-------------|---------|
| **Allocation** | Team/people assigned with hours | "Frontend: 2 engineers, 40 hours; Backend: 1 engineer, 30 hours" |
| **Milestones** | Week-by-week or sprint breakdown | "Sprint 1: API spec + tests; Sprint 2: Frontend integration" |
| **Comms Plan** | Stakeholder notification strategy | "Email to #eng-announcements once merged; announce in standup" |
| **Acceptance Checklist** | All gates are green | `[x] All approvals met [x] No blocker issues [x] Dependencies resolved` |

---

## Approval Workflow

### Approval Gate Logic

```
ANALYST APPROVAL (2 required)
├─ All mandatory fields present? ✅
├─ Evidence linked and accessible? ✅
├─ No contradictions in requirements? ✅
└─ SLA < 24h? ✅
   → ADVANCE to PM

PM APPROVAL (2 required)
├─ Business case justified? ✅
├─ Scope consistent with spec? ✅
├─ Risk assessment complete? ✅
└─ SLA < 24h? ✅
   → ADVANCE to Architect

ARCHITECT APPROVAL (2 required)
├─ Architecture documented? ✅
├─ Technical risks identified? ✅
├─ Complexity assessment reasonable? ✅
└─ SLA < 24h? ✅
   → ADVANCE to SM

SM APPROVAL (1 required)
├─ Resources available? ✅
├─ Timeline realistic? ✅
├─ No blockers identified? ✅
└─ SLA < 24h? ✅
   → READY FOR IMPLEMENTATION
```

### Blocking Criteria

A stage **BLOCKS** advancement if:

1. **Missing Evidence:** One or more mandatory fields are incomplete
2. **SLA Violation:** Stage has been open > 24 hours without approval
3. **Approval Shortfall:** Fewer than required reviewers have approved
4. **Contradiction:** New stage findings contradict previous stage
5. **Explicit Rejection:** A reviewer has requested changes and not approved

### Reviewer Assignment

The GitHub Actions workflow automatically:
1. Tags reviewers from `CODEOWNERS` file
2. Sets stage-specific labels (e.g., `spec-stage:analyst`, `spec-stage:pm`)
3. Creates a GitHub check for each stage
4. Tracks SLA in PR status

Example `CODEOWNERS` entry:
```
# Spec-Pipeline Roles
.github/workflows/spec-pipeline.yml @egos/analysts @egos/pms @egos/architects @egos/scrum-masters
```

---

## SLA Tracking

### SLA Definition

Each stage has a **hard limit of 24 hours** from stage start to approval.

### SLA Calculation

```
Stage Start: When previous stage approved + handoff posted
Stage End: When all required approvals received
SLA Status: (End - Start) < 24h → GREEN
           (End - Start) >= 24h → RED (still counts, blocks nothing, but flagged)
```

### SLA Visibility

- PR comment with running status (updated every 1 hour)
- PR check status shows SLA per stage
- Summary at PR merge time

Example PR comment:
```
## SLA Status (Updated 2026-03-26 14:30 UTC)

| Stage | Started | Current | Approved | Status |
|-------|---------|---------|----------|--------|
| Analyst | 2026-03-26 09:00 | 2026-03-26 14:30 | 2/2 ✅ | COMPLETE (5h 30m) |
| PM | 2026-03-26 14:30 | 2026-03-26 14:30 | 0/2 ⏳ | IN PROGRESS |
| Architect | — | — | — | PENDING |
| SM | — | — | — | PENDING |
```

---

## Examples

### Example 1: Complete E2E Workflow

**PR Title:** `spec: Add two-factor authentication (2FA) to user accounts`

**Stage 1: Analyst Approval (2026-03-26 09:00 - 11:00)**

Analyst posts:
```markdown
## SPECIFICATION HANDOFF — 2026-03-26 11:00 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (2 approvals)
- [x] SLA within limit (2h < 24h)

### Summary
User 2FA requirement validated. Three acceptance criteria locked: email codes, TOTP support, backup codes. Success metric: < 2% support tickets related to 2FA friction by end of Q2 2026.

### Evidence Links
- User research: https://github.com/egos/issues/42
- Acceptance criteria: See PR description (5 items)
- Compliance requirement: SOC 2 Type II control AC-2.2

### Next Stage Prepared
Product review is ready. Assigning to @egos/pms for business impact assessment.

### Reviewer Attribution
- Approved by @alice (analyst lead)
- Approved by @bob (security analyst)
- Decision timestamp: 2026-03-26T11:00:00Z
```

**Stage 2: PM Approval (2026-03-26 11:00 - 14:30)**

PM posts:
```markdown
## PRODUCT REVIEW HANDOFF — 2026-03-26 14:30 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (2 approvals)
- [x] SLA within limit (3.5h < 24h)

### Summary
Business case strong. 2FA is Q2 OKR item for "reduce security incidents by 50%". Scoped to email + TOTP (no SMS initially per cost). No scope creep risk identified.

### Evidence Links
- Q2 Roadmap reference: https://docs.google.com/document/.../roadmap
- Market risk: Low (2FA standard in industry)
- Estimated effort: 2 weeks (per architect input)
- Customer impact: Positive (4 customer requests noted in CRM)

### Next Stage Prepared
Architecture review ready. Assigning to @egos/architects for technical validation.

### Reviewer Attribution
- Approved by @carol (product lead)
- Approved by @dave (product strategy)
- Decision timestamp: 2026-03-26T14:30:00Z
```

**Stage 3: Architect Approval (2026-03-26 14:30 - 18:00)**

Architect posts:
```markdown
## ARCHITECTURE REVIEW HANDOFF — 2026-03-26 18:00 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (2 approvals)
- [x] SLA within limit (3.5h < 24h)

### Summary
Architecture is sound. Uses existing JWT infrastructure for code validation. New dependency: speakeasy (TOTP lib, v2.4.1). No performance impact (< 1ms per code generation). Database migration: Add `totp_secret` column to `users` table.

### Evidence Links
- Architecture diagram: https://docs.google.com/drawings/.../auth-2fa
- Code reference: `packages/auth/totp-client.ts` (existing pattern)
- Performance impact: Negligible (measured via load test)
- Dependencies: speakeasy@2.4.1, qrcode@1.5.0
- Technical debt: None introduced

### Next Stage Prepared
Scrum Master review ready. Assigning to @egos/scrum-masters for resource and timeline confirmation.

### Reviewer Attribution
- Approved by @eve (lead architect)
- Approved by @frank (infrastructure lead)
- Decision timestamp: 2026-03-26T18:00:00Z
```

**Stage 4: SM Approval (2026-03-26 18:00 - 20:00)**

SM posts:
```markdown
## STAKEHOLDER MARKUP HANDOFF — 2026-03-26 20:00 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (1 approval)
- [x] SLA within limit (2h < 24h)

### Summary
Resources allocated and timeline confirmed. Ready to transition to implementation phase. All blockers cleared. Communication plan: Notify #engineering channel on merge, include in next sprint kickoff.

### Evidence Links
- Resource allocation: Backend: 1 FTE (Grace, 2 weeks); Frontend: 1 FTE (Henry, 2 weeks); QA: 0.5 FTE (Iris, 1 week)
- Timeline: Sprint 1 (April 2-13): API + DB; Sprint 2 (April 16-27): Frontend + tests
- Communication plan: Email to #product on merge; announce in team standup
- Acceptance checklist: [x] All approvals met [x] No blockers [x] Dependencies in place

### READY FOR IMPLEMENTATION ✅
This specification is approved and ready for implementation. Next: Assign to engineering team and create task tickets in Linear/GitHub Issues.

### Reviewer Attribution
- Approved by @grace (scrum master)
- Decision timestamp: 2026-03-26T20:00:00Z
```

**PR Merges:** Once SM approves, the PR can merge. A final summary is posted:

```markdown
## SPEC-PIPELINE COMPLETE ✅

**Total Time:** 11 hours (well within 96-hour window)
**Status:** All stages approved and completed
**Ready for:** Implementation (assign to sprint, create implementation tasks)

### Final Approvals
- Analyst: ✅ 2/2 (alice, bob) — 2h
- PM: ✅ 2/2 (carol, dave) — 3.5h
- Architect: ✅ 2/2 (eve, frank) — 3.5h
- SM: ✅ 1/1 (grace) — 2h

### Next Steps
1. Create implementation Epic in GitHub Issues with this spec as reference
2. Decompose into smaller tasks (T-shirt size: S/M/L per task)
3. Assign to sprint and notify @engineering on Slack
4. Link spec PR to implementation PR via "Closes #XXX" reference
```

---

### Example 2: Blocked Workflow (Missing Evidence)

**Stage: Analyst** — PM requests changes

Reviewer @bob comments on PR:
```
@alice I see the acceptance criteria, but I don't see the user research or data backing the "< 2% support tickets" claim. Can you add a link to the user feedback or support ticket analysis? This is a blocking requirement for analyst approval.
```

Analyst updates PR description, adds evidence link. Reviewers re-approve.

**Stage: PM** — SLA violation flag (no action required, just tracking)

After 24h without PM approval, the GitHub check updates:
```
SPEC PIPELINE STAGE: PM REVIEW
Status: ⏱️ SLA EXCEEDED (25 hours elapsed)
Required Approvals: 0/2 remaining
Action: Waiting for @egos/pms to review

This stage exceeded the 24-hour SLA. No blockers triggered, but this is tracked for accountability.
```

PM finally approves at 28 hours. Comment is added:
```
⚠️ SLA VIOLATION RECORDED: PM stage exceeded 24h limit (28h elapsed)
Reason: [PM notes brief explanation]
Impact: No merge block, but flagged for retrospective
```

---

## Task Routing (Automation)

The `spec-router` agent handles automatic task routing.

### Routing Rules

1. **Label Detection:** When `spec-pipeline` label is added to PR:
   - Remove any previous stage labels (`spec-stage:*`)
   - Add `spec-stage:analyst` label
   - Create GitHub check for analyst stage

2. **Stage Progression:** When 2 approvals received for current stage:
   - Remove current stage label
   - Add next stage label
   - Assign CODEOWNERS from next stage
   - Post handoff comment template (requestor must fill in)

3. **SLA Tracking:** Every 1 hour:
   - Check elapsed time since stage start
   - If > 24h, add SLA violation comment (non-blocking)
   - Update PR check with SLA status

4. **Final Approval:** When SM approves:
   - Remove all stage labels
   - Add `spec-complete` label
   - Add `ready-to-merge` label
   - Post final summary comment

### No Automatic Merge

The spec-pipeline does NOT automatically merge. The PR author or designated implementer manually merges once SM approval is received. This ensures intentionality and allows for one final review before implementation begins.

---

## Integration with Other Contracts

### Dependency: pr:gate Contract

The `spec-pipeline` contract is **compatible** with the `pr:gate` contract. When a spec-pipeline PR is merged, it transitions to implementation, which follows the standard `pr:gate` workflow.

### Relationship to SSOT

- **SSOT Location:** This document (`.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md`)
- **Canonical Reviewer List:** `CODEOWNERS` file
- **Role Registry:** `.guarani/ROLES_REGISTRY.md` (if exists)
- **Freshness:** Updated when role/SLA/approval criteria change
- **Sync:** Disseminate changes to all repos via `/disseminate` workflow

---

## Implementation Notes

### GitHub Actions Implementation

The `spec-pipeline.yml` workflow handles:
1. Trigger detection (`spec-pipeline` label)
2. Mandatory field validation (analyzer checks PR description)
3. Reviewer assignment (from CODEOWNERS)
4. SLA tracking (cron job every 1 hour)
5. Stage progression (automated label/assignment updates)
6. Final summary generation

### Local Development (Testing)

To test the workflow:

```bash
# Create a test PR with spec-pipeline label
gh pr create \
  --title "test: Spec pipeline demo" \
  --body "$(cat spec_example.md)" \
  --label spec-pipeline

# Approve as analyst
gh pr review <PR_NUMBER> --approve

# Check workflow progress
gh pr view <PR_NUMBER> --json checks
```

---

## FAQ

### Q: Can we skip a stage?
**A:** No. All stages must be completed in order. This ensures alignment across product, architecture, and resource planning.

### Q: What if SM doesn't approve within 24h?
**A:** The spec is still valid but flagged as "SLA exceeded". No automatic escalation; team culture and daily standup should identify delays.

### Q: Can analyst go back and change spec after PM approval?
**A:** No. Once PM approves, the spec is locked. Any changes require a new spec-pipeline PR.

### Q: What if architect finds a blocker?
**A:** Architect explicitly requests changes (via GitHub review). Spec returns to analyst for clarification. Process repeats from analyst stage.

### Q: Do we need all roles in every repo?
**A:** The spec-pipeline is designed for repositories that have these roles. Smaller repos can adapt by combining roles (e.g., PM + SM = one person, analyst omitted for infrastructure).

### Q: How do we handle urgent specs?
**A:** Urgent specs can be escalated via an issue comment `@egos/urgent-spec-bypass`. This requires explicit sign-off from all 4 roles but collapses the 24h windows to 4h per stage.

---

## Related Documents

- **Worktree Contract:** `.guarani/orchestration/WORKTREE_CONTRACT.md` (EGOS-110)
- **PR Gate Contract:** `docs/pr:gate-contract.md` (if exists)
- **Roles Registry:** `.guarani/ROLES_REGISTRY.md`
- **Approval Workflow:** `.guarani/orchestration/GATES.md`

---

**Authorship:** EGOS Kernel Governance | **Maintenance:** @egos/architects | **Enforcement:** spec-router agent + GitHub Actions

*"Evidence first, then execution. Clear handoffs prevent rework."*

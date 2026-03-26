# Spec-Pipeline E2E Example: 2FA Implementation

This document demonstrates the complete spec-pipeline workflow from start to finish.

## Scenario

Add two-factor authentication (2FA) to user accounts using the spec-pipeline contract.

---

## Stage 1: Analyst Review (09:00 - 11:00 UTC)

### PR Details
- **PR Title:** `spec: Add two-factor authentication (2FA) to user accounts`
- **Created:** 2026-03-26 09:00 UTC
- **Labels:** `spec-pipeline`, `spec-stage:analyst`

### PR Description

```markdown
# Specification: Two-Factor Authentication (2FA)

## problem-statement
Users require an additional layer of security beyond passwords. Current system
has no multi-factor authentication, making accounts vulnerable to credential
compromise. Research shows 80% of users in our target market have 2FA enabled
elsewhere. Support tickets indicate 3+ customers requesting 2FA in past month.

**Reference:** GitHub issue #42 (user research), CRM ticket analysis

## success-metric
Reduce account compromise incidents by 50% by end of Q2 2026 (measured via
security audit). Target: < 2% of support tickets related to account access issues.

## acceptance-criteria
1. Email-based verification codes (6-digit codes, 5-minute validity)
2. TOTP support (compatible with Google Authenticator, Authy)
3. Backup codes (10 codes per user, single-use)
4. Account recovery flow for lost 2FA device
5. Admin override capability for locked accounts

## user-story
As a user, I want to enable 2FA on my account so that my data is protected
from unauthorized access even if my password is compromised.

As an admin, I want to help users recover access if they lose their 2FA device.

## Additional Context
- **Security Classification:** HIGH (authentication mechanism)
- **Compliance Impact:** SOC 2 Type II control AC-2.2
- **Customer Impact:** Positive (reduces support burden, improves trust)
```

### Stage 1 Reviewers

**Assigned to:** @egos/analysts (requirement: 2 approvals)

**Reviews:**
1. @alice-analyst (lead analyst) - APPROVED at 10:00 UTC
   - Comment: "Spec is clear, evidence-backed, and addresses real customer need. Acceptance criteria are specific and measurable."

2. @bob-security (security analyst) - APPROVED at 11:00 UTC
   - Comment: "Security aspects well-documented. SOC 2 compliance mentioned appropriately. Ready to advance to PM."

**SLA Status:** 2 hours elapsed (within 24h limit) ✅

### Stage 1 Handoff Comment (Posted at 11:00 UTC)

```markdown
## [SPECIFICATION] Handoff — 2026-03-26 11:00 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (2 approvals)
- [x] SLA within limit (2h < 24h)

### Summary
User 2FA requirement validated through customer research, support tickets,
and market analysis. Three acceptance criteria locked: email codes, TOTP support,
backup codes. Success metric: < 2% support tickets related to 2FA friction by
end of Q2 2026.

### Evidence Links
- User research: https://github.com/egos/repo/issues/42
- Support ticket analysis: https://crm.company.com/tickets?tag=2fa
- Acceptance criteria: See PR description (5 items, all specific)
- Compliance requirement: SOC 2 Type II control AC-2.2
- Customer impact: Positive (4 customer requests noted)

### Next Stage Prepared
Product review is ready. Assigning to @egos/pms for business impact assessment.

### Reviewer Attribution
- Approved by @alice-analyst (lead analyst)
- Approved by @bob-security (security analyst)
- Decision timestamp: 2026-03-26T11:00:00Z
```

---

## Stage 2: Product Manager Review (11:00 - 14:30 UTC)

### Transition
- **Label Update:** `spec-stage:analyst` → `spec-stage:pm`
- **Assigned to:** @egos/pms

### PR Update by Product Team

Product team adds their review to PR description:

```markdown
# Product Review: 2FA Feature

## business-impact
2FA is a Q2 OKR priority under "Reduce security incidents by 50%". Aligns with
Q2 roadmap commitment to improve authentication security. Expected to reduce
fraud and support costs.

**Reference:** Q2 2026 OKR doc (link), Roadmap item #5

## go-no-go-decision
**GO** — This is a priority feature with strong business case and customer demand.
4 customer requests in past month. Reduces support burden (fewer "account locked"
tickets). Competitive advantage (most competitors have 2FA).

## risk-assessment
- **Market Risk:** LOW — 2FA is industry standard. No market-specific risks.
- **Timing Risk:** LOW — 2-week estimate fits in Q2 timeline.
- **Dependency Risk:** LOW — Uses existing JWT infrastructure for tokens.
- **Resource Risk:** LOW — Team capacity confirmed for 2-week effort.
- **Compliance Risk:** NONE — Improves security posture.

## scope-confirmation
**Scope:** Email + TOTP (primary carriers)
**Deferred to Q3:** SMS-based 2FA (cost optimization), Push notifications

No scope creep identified. Team consensus on scope boundaries.
```

### Stage 2 Reviews

**Reviews:**
1. @carol-pm (product lead) - APPROVED at 13:00 UTC
   - Comment: "Business case strong, OKR alignment clear, scope realistic. Ready to advance."

2. @dave-product (product strategy) - APPROVED at 14:30 UTC
   - Comment: "Excellent risk assessment. Timing is right for market positioning."

**SLA Status:** 3.5 hours elapsed (within 24h limit) ✅

### Stage 2 Handoff Comment (Posted at 14:30 UTC)

```markdown
## [PRODUCT REVIEW] Handoff — 2026-03-26 14:30 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (2 approvals)
- [x] SLA within limit (3.5h < 24h)

### Summary
Business case validated. 2FA is Q2 OKR item for "reduce security incidents by 50%".
Scoped to email + TOTP (no SMS initially per cost optimization). No scope creep
risk identified. Estimated 2-week effort aligns with architect input.

### Evidence Links
- Q2 Roadmap reference: https://docs.google.com/.../q2-2026-roadmap
- OKR alignment: https://docs.google.com/.../q2-okrs
- Market analysis: 2FA adoption >85% in SaaS market
- Customer demand: 4 requests in past month (CRM)
- Estimated effort: 2 weeks (per architect preliminary assessment)

### Next Stage Prepared
Architecture review ready. Assigning to @egos/architects for technical validation.

### Reviewer Attribution
- Approved by @carol-pm (product lead)
- Approved by @dave-product (product strategy)
- Decision timestamp: 2026-03-26T14:30:00Z
```

---

## Stage 3: Architect Review (14:30 - 18:00 UTC)

### Transition
- **Label Update:** `spec-stage:pm` → `spec-stage:architect`
- **Assigned to:** @egos/architects

### PR Update by Architecture Team

```markdown
# Architecture Review: 2FA Feature

## architecture-diagram
See: https://docs.google.com/drawings/.../2fa-architecture

**Architecture Summary:**
```
┌─────────────────────────────────────────┐
│ Frontend (React)                        │
├─────────────────────────────────────────┤
│  2FA Setup Flow                         │
│  - Enable/Disable UI                    │
│  - Verify Code Prompt                   │
│  - Backup Code Display                  │
└──────────────────┬──────────────────────┘
                   │
          API Route: /auth/2fa/*
                   │
┌──────────────────▼──────────────────────┐
│ Backend (Node.js + Express)             │
├─────────────────────────────────────────┤
│  TOTP Handler                           │
│  - Generate secret (speakeasy)          │
│  - Verify codes                         │
│  - QR code generation (qrcode)          │
│  - Backup codes (uuid v4)               │
└──────────────────┬──────────────────────┘
                   │
            Database: PostgreSQL
                   │
           ┌───────▼────────┐
           │ users table    │
           │ - totp_secret  │
           │ - backup_codes │
           └────────────────┘
```

## technical-risks
- **Database Migration Risk:** LOW — Adding new columns (totp_secret, backup_codes).
  No data loss, backward compatible.
- **Performance Impact:** NEGLIGIBLE — Code generation < 1ms (measured via
  benchmarking). DB lookup: standard indexed query.
- **External Dependency Risk:** LOW — speakeasy@2.4.1 is mature, >5M weekly downloads,
  active maintenance.
- **Token Leakage Risk:** MITIGATED — Codes valid for 5 minutes only, backed up
  securely in database (bcrypt hashed).

## api-schema-changes
### New Endpoints
- `POST /auth/2fa/enable` - Initiate 2FA setup (returns secret + QR code)
- `POST /auth/2fa/verify` - Verify 2FA code during setup
- `POST /auth/2fa/disable` - Disable 2FA (requires current password)
- `GET /auth/2fa/status` - Check if 2FA enabled
- `POST /auth/2fa/backup-codes` - Regenerate backup codes

### Modified Endpoints
- `POST /auth/login` - Add optional `totp_code` parameter (if 2FA enabled)

### Database Schema
```sql
ALTER TABLE users ADD COLUMN totp_secret VARCHAR(32) NULL;
ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN backup_codes JSONB DEFAULT '[]';
ALTER TABLE users ADD COLUMN created_at_updated TIMESTAMP;
```

## complexity-assessment
**Complexity:** Medium (M)
- Frontend: Moderate (new UI flows, state management)
- Backend: Moderate (TOTP integration, code verification logic)
- Database: Low (simple schema additions)
- Testing: Moderate (need comprehensive 2FA test scenarios)
- **Total Estimate:** 2 weeks (based on team velocity)

## dependency-audit
| Dependency | Version | Justification | Risk |
|------------|---------|---------------|------|
| speakeasy | 2.4.1 | TOTP generation/verification | LOW |
| qrcode | 1.5.0 | QR code generation for TOTP setup | LOW |

**Audit Result:** No conflicts with existing dependencies. Both libraries are
well-maintained and widely used in production.
```

### Stage 3 Reviews

**Reviews:**
1. @eve-architect (lead architect) - APPROVED at 16:30 UTC
   - Comment: "Architecture is clean and uses existing patterns well. TOTP implementation is standard. No concerns."

2. @frank-infra (infrastructure lead) - APPROVED at 18:00 UTC
   - Comment: "Database migration is straightforward. Performance impact minimal. Dependency choices are solid."

**SLA Status:** 3.5 hours elapsed (within 24h limit) ✅

### Stage 3 Handoff Comment (Posted at 18:00 UTC)

```markdown
## [ARCHITECTURE REVIEW] Handoff — 2026-03-26 18:00 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (2 approvals)
- [x] SLA within limit (3.5h < 24h)

### Summary
Architecture is sound. Uses existing JWT infrastructure for code validation.
New dependency: speakeasy (TOTP lib, v2.4.1). No performance impact (< 1ms per
code generation, measured). Database migration: Add totp_secret and backup_codes
columns to users table.

### Evidence Links
- Architecture diagram: https://docs.google.com/drawings/.../2fa-architecture
- Code reference: `src/auth/totp-handler.ts` (following existing pattern)
- Performance impact: Load tested — negligible overhead
- Dependencies: speakeasy@2.4.1, qrcode@1.5.0 (both well-maintained)
- Technical debt: NONE introduced
- Database schema: See PR comments

### Next Stage Prepared
Scrum Master review ready. Assigning to @egos/scrum-masters for resource and
timeline confirmation.

### Reviewer Attribution
- Approved by @eve-architect (lead architect)
- Approved by @frank-infra (infrastructure lead)
- Decision timestamp: 2026-03-26T18:00:00Z
```

---

## Stage 4: Scrum Master Review (18:00 - 20:00 UTC)

### Transition
- **Label Update:** `spec-stage:architect` → `spec-stage:sm`
- **Assigned to:** @egos/scrum-masters

### PR Update by SM

```markdown
# Stakeholder Markup: 2FA Implementation

## resource-allocation
- **Backend:** Grace (senior backend engineer, 2 weeks = 80 hours)
- **Frontend:** Henry (senior frontend engineer, 2 weeks = 80 hours)
- **QA:** Iris (QA lead, 1 week = 40 hours for 2FA-specific testing)
- **DevOps:** Infrastructure team (4 hours for database migration planning)
- **Total Effort:** 284 hours (2.5 FTE-weeks)

**Resource Status:** ✅ All team members confirmed and available.

## timeline-mapping
### Sprint 1: API & Database (April 2-13, 2026)
- Week 1: API endpoint design, TOTP integration testing, DB migration scripts
- Week 2: Backend implementation, comprehensive unit tests, API integration tests

### Sprint 2: Frontend & E2E (April 16-27, 2026)
- Week 1: Frontend UI implementation (setup flow, backup codes display)
- Week 2: E2E testing, security review, deployment preparation

### Deployment
- Target: Monday, April 28, 2026 (after sprint 2 completion)
- Rollout: Gradual (10% → 50% → 100% over 3 days)

## communication-plan
### Internal Communication
- **Kick-off:** Announce in team standup on Monday, April 2
- **Weekly Updates:** Include in sprint recap slides
- **Completion:** Announce in #engineering channel on merge

### External Communication
- **Customer Announcement:** Feature blog post scheduled for April 28
- **Documentation:** Security best practices guide (2FA setup)
- **Support Team:** Training session on 2FA troubleshooting

## readiness-checklist
- [x] All approvals met (analyst, PM, architect)
- [x] No blockers identified
- [x] Dependencies available and pinned
- [x] Team capacity confirmed
- [x] Timeline aligns with Q2 OKR deadline
- [x] Communication plan drafted
- [x] Security review prerequisites met
- [x] Documentation outline prepared
```

### Stage 4 Review

**Reviews:**
1. @grace-sm (scrum master) - APPROVED at 20:00 UTC
   - Comment: "Resources confirmed, timeline is realistic, communication plan is solid. Ready for implementation."

**SLA Status:** 2 hours elapsed (within 24h limit) ✅
**Total Pipeline Duration:** 11 hours (well within 96-hour window)

### Stage 4 Handoff Comment (Posted at 20:00 UTC)

```markdown
## [STAKEHOLDER MARKUP] Handoff — 2026-03-26 20:00 UTC

### Status
- [x] Evidence present and complete
- [x] Approval gates met (1 approval)
- [x] SLA within limit (2h < 24h)

### Summary
Resources allocated and timeline confirmed. Ready to transition to implementation
phase. All blockers cleared. Communication plan: Notify #engineering channel on
merge, include in sprint kickoff.

### Evidence Links
- Resource allocation: Backend (Grace, 80h), Frontend (Henry, 80h), QA (Iris, 40h)
- Timeline: Sprint 1 (April 2-13): API + DB; Sprint 2 (April 16-27): Frontend + tests
- Communication plan: Standup announcement + #engineering notification + blog post
- Acceptance checklist: [x] All approvals [x] No blockers [x] Resources confirmed [x] Timeline realistic

### READY FOR IMPLEMENTATION ✅

This specification is approved and ready for implementation.

**Next Steps:**
1. Merge this spec PR (this PR: EGOS-2FA)
2. Create implementation Epic in GitHub Issues (reference this spec)
3. Decompose into task tickets (UI, API, tests, docs)
4. Assign to sprint and notify team
5. Link implementation PR to this spec via "Closes #XXX"

### Reviewer Attribution
- Approved by @grace-sm (scrum master)
- Decision timestamp: 2026-03-26T20:00:00Z
```

---

## Summary Comment (Posted at Merge Time)

```markdown
## SPEC-PIPELINE COMPLETE ✅

**Specification:** Add Two-Factor Authentication (2FA)
**Status:** ALL STAGES APPROVED AND COMPLETED
**Ready for:** Implementation Phase

### Approval Timeline
| Stage | Reviewers | Duration | Status |
|-------|-----------|----------|--------|
| Analyst | alice, bob | 2h | ✅ APPROVED |
| Product Manager | carol, dave | 3.5h | ✅ APPROVED |
| Architect | eve, frank | 3.5h | ✅ APPROVED |
| Scrum Master | grace | 2h | ✅ APPROVED |
| **TOTAL** | **7 reviewers** | **11 hours** | **✅ COMPLETE** |

### Implementation Next Steps
1. **Epic Creation:** Create "Implement 2FA" Epic (link to spec: #EGOS-2FA)
2. **Task Decomposition:** Break into:
   - Backend API implementation (Grace)
   - Database migration and tests
   - Frontend UI flows (Henry)
   - QA test suite (Iris)
   - Security review & documentation
3. **Sprint Assignment:** Assign to Q2 2026 sprint (starting April 2)
4. **Team Notification:**
   - Message: #engineering
   - Slack: Announce implementation kickoff
   - Standup: Include in next team standup
5. **Link PR:** When creating implementation PR, reference: Closes #EGOS-2FA

---

**Specification ready. Proceeding to implementation phase.**

*This workflow demonstrates the spec-pipeline contract in action: clear evidence,
explicit handoffs, multi-stage approval gates, and SLA tracking.*
```

---

## Key Takeaways

This example demonstrates all spec-pipeline features:

1. **Sequential Stages:** analyst → pm → architect → sm (no skipping)
2. **Evidence-First:** Each stage provided concrete proof and links
3. **Mandatory Fields:** Every stage validated required deliverables
4. **Approval Gates:** 2 approvals per stage (1 for SM)
5. **SLA Tracking:** All stages completed within 24-hour window
6. **Clear Handoffs:** Each transition included explicit summary + next stage info
7. **No Backsliding:** Once approved, stage cannot regress
8. **Ready for Implementation:** Final SM approval unlocks merge gate

**Total Time:** 11 hours from analyst to implementation readiness
**Teams Involved:** 7 reviewers across 4 roles
**Quality:** High confidence in technical approach and business value

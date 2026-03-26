/**
 * Spec-Pipeline End-to-End Tests
 *
 * Test scenarios:
 * 1. Complete workflow: analyst → pm → architect → sm
 * 2. Validation blocks merge when evidence missing
 * 3. SLA tracking works correctly
 */

import { describe, it, expect } from 'bun:test';
import runSpecRouter from '../agents/agents/spec-router';

describe('Spec-Pipeline Contract', () => {
  // ============ Test 1: Complete E2E Workflow ============

  describe('E2E Workflow: analyst → pm → architect → sm', () => {
    it('analyst stage: validates mandatory fields and passes', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 1,
          title: 'spec: Add two-factor authentication',
          body: `
## Specification
### problem-statement
Users need secure authentication with 2FA support.

### success-metric
Reduce account compromise incidents by 50% by Q2 2026.

### acceptance-criteria
1. Email-based verification codes
2. TOTP support (Google Authenticator, Authy)
3. Backup codes for account recovery

### user-story
As a user, I want to enable 2FA on my account so that my data is protected from unauthorized access.
          `,
          labels: ['spec-pipeline', 'spec-stage:analyst'],
          draft: false,
          created_at: '2026-03-26T09:00:00Z',
          updated_at: '2026-03-26T09:30:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      expect(findings).toBeDefined();
      expect(findings.length).toBeGreaterThan(0);

      const validationFinding = findings.find(
        (f) => f.message.includes('validation passed')
      );
      expect(validationFinding).toBeDefined();
      expect(validationFinding?.severity).toBe('info');
    });

    it('pm stage: validates business impact and risk assessment', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 1,
          title: 'spec: Add 2FA',
          body: `
## Product Review

### business-impact
Q2 OKR item for "reduce security incidents by 50%". Scoped to email + TOTP.
Reference: https://docs.google.com/document/d/.../roadmap

### go-no-go-decision
GO - Priority feature. 4 customer requests in past month.

### risk-assessment
- Market risk: LOW (2FA standard in industry)
- Timing risk: LOW (2-week estimate, aligned with sprint)
- Dependency risk: LOW (uses existing auth infrastructure)

### scope-confirmation
Email + TOTP only. SMS deferred to Q3 2026 (cost optimization).
          `,
          labels: ['spec-pipeline', 'spec-stage:pm'],
          draft: false,
          created_at: '2026-03-26T11:00:00Z',
          updated_at: '2026-03-26T14:30:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const validationFinding = findings.find(
        (f) => f.message.includes('validation passed')
      );
      expect(validationFinding).toBeDefined();
    });

    it('architect stage: validates architecture diagram and technical risks', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 1,
          title: 'spec: Add 2FA',
          body: `
## Architecture Review

### architecture-diagram
See: https://docs.google.com/drawings/.../auth-2fa
Uses existing JWT infrastructure for code validation.

### technical-risks
- Performance impact: 1ms per code generation (acceptable)
- Database migration: Add totp_secret column to users (low risk)
- External dependency: speakeasy@2.4.1 (well-maintained library)

### api-schema-changes
POST /auth/2fa/enable - Enable 2FA
POST /auth/2fa/verify - Verify code
POST /auth/2fa/disable - Disable 2FA
PUT /users/:id/totp_secret - Store secret

### complexity-assessment
Medium (M) - 2 weeks estimated, uses existing patterns

### dependency-audit
- speakeasy@2.4.1 (TOTP library)
- qrcode@1.5.0 (QR code generation for TOTP)
No breaking changes or conflicts.
          `,
          labels: ['spec-pipeline', 'spec-stage:architect'],
          draft: false,
          created_at: '2026-03-26T14:30:00Z',
          updated_at: '2026-03-26T18:00:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const validationFinding = findings.find(
        (f) => f.message.includes('validation passed')
      );
      expect(validationFinding).toBeDefined();
    });

    it('sm stage: validates resource allocation and timeline', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 1,
          title: 'spec: Add 2FA',
          body: `
## Stakeholder Markup

### resource-allocation
- Backend: 1 FTE (Grace, 2 weeks)
- Frontend: 1 FTE (Henry, 2 weeks)
- QA: 0.5 FTE (Iris, 1 week)

### timeline-mapping
- Sprint 1 (April 2-13): API spec, database migration, backend tests
- Sprint 2 (April 16-27): Frontend UI, TOTP integration, end-to-end tests

### communication-plan
- Merge notification: Email to #product
- Standup announcement: Week 1 of implementation
- Documentation update: Link in API docs

### readiness-checklist
[x] All approvals met
[x] No blockers identified
[x] Dependencies available
[x] Team capacity confirmed
          `,
          labels: ['spec-pipeline', 'spec-stage:sm'],
          draft: false,
          created_at: '2026-03-26T18:00:00Z',
          updated_at: '2026-03-26T20:00:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const validationFinding = findings.find(
        (f) => f.message.includes('validation passed')
      );
      expect(validationFinding).toBeDefined();
    });
  });

  // ============ Test 2: Validation Blocks Merge ============

  describe('Validation: Blocks merge when evidence missing', () => {
    it('analyst stage: missing problem-statement blocks validation', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 2,
          title: 'spec: Incomplete spec',
          body: `
## Specification
### success-metric
Some metric here

### acceptance-criteria
1. Criterion 1
2. Criterion 2

### user-story
User story text
          `,
          labels: ['spec-pipeline', 'spec-stage:analyst'],
          draft: false,
          created_at: '2026-03-26T09:00:00Z',
          updated_at: '2026-03-26T09:30:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const errorFinding = findings.find((f) => f.severity === 'error');
      expect(errorFinding).toBeDefined();
      expect(errorFinding?.message).toContain(
        'validation failed'
      );
      expect(errorFinding?.message).toContain('problem-statement');

      // Check that merge block reason is generated in suggestion
      if (errorFinding?.suggestion) {
        expect(errorFinding.suggestion).toContain('Missing mandatory evidence fields');
        expect(errorFinding.suggestion).toContain('problem-statement');
      }
    });

    it('pm stage: missing go-no-go-decision blocks validation', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 3,
          title: 'spec: Incomplete PM review',
          body: `
## Product Review

### business-impact
Business case text here

### risk-assessment
Risk text here

### scope-confirmation
Scope text here
          `,
          labels: ['spec-pipeline', 'spec-stage:pm'],
          draft: false,
          created_at: '2026-03-26T11:00:00Z',
          updated_at: '2026-03-26T14:30:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const errorFinding = findings.find((f) => f.severity === 'error');
      expect(errorFinding).toBeDefined();
      expect(errorFinding?.message).toContain('go-no-go-decision');
    });

    it('architect stage: missing complexity-assessment blocks validation', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 4,
          title: 'spec: Incomplete architecture review',
          body: `
## Architecture Review

### architecture-diagram
Diagram link

### technical-risks
Risk text

### api-schema-changes
API changes text

### dependency-audit
Dependencies text
          `,
          labels: ['spec-pipeline', 'spec-stage:architect'],
          draft: false,
          created_at: '2026-03-26T14:30:00Z',
          updated_at: '2026-03-26T18:00:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const errorFinding = findings.find((f) => f.severity === 'error');
      expect(errorFinding).toBeDefined();
      expect(errorFinding?.message).toContain('complexity-assessment');
    });

    it('sm stage: missing timeline-mapping blocks validation', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 5,
          title: 'spec: Incomplete SM review',
          body: `
## Stakeholder Markup

### resource-allocation
Resource text

### communication-plan
Communication text

### readiness-checklist
[x] All done
          `,
          labels: ['spec-pipeline', 'spec-stage:sm'],
          draft: false,
          created_at: '2026-03-26T18:00:00Z',
          updated_at: '2026-03-26T20:00:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      const errorFinding = findings.find((f) => f.severity === 'error');
      expect(errorFinding).toBeDefined();
      expect(errorFinding?.message).toContain('timeline-mapping');
    });
  });

  // ============ Test 3: SLA Tracking ============

  describe('SLA Tracking: 24-hour per stage limit', () => {
    it('sla-check: stage within 24 hours returns OK status', async () => {
      const stageStartTime = new Date(Date.now() - 5 * 60 * 60 * 1000); // 5 hours ago

      const prContext = JSON.stringify({
        pull_request: {
          number: 6,
          title: 'spec: SLA test',
          body: `
## Specification
### problem-statement
Test problem statement

### success-metric
Test metric

### acceptance-criteria
1. Test criterion

### user-story
Test user story
          `,
          labels: ['spec-pipeline', 'spec-stage:analyst'],
          draft: false,
          created_at: stageStartTime.toISOString(),
          updated_at: new Date().toISOString(),
        },
      });

      const findings = await runSpecRouter(prContext, 'sla-check');

      expect(findings).toBeDefined();
      expect(findings.length).toBeGreaterThan(0);

      const slaFinding = findings.find((f) => f.message.includes('SLA'));
      expect(slaFinding).toBeDefined();

      // Should be OK status (not warning or exceeded)
      // SLA message is in the main message field
      expect(slaFinding?.message).toContain('✅ SLA OK');
    });

    it('sla-check: stage exceeding 24 hours returns EXCEEDED status', async () => {
      const stageStartTime = new Date(Date.now() - 28 * 60 * 60 * 1000); // 28 hours ago

      const prContext = JSON.stringify({
        pull_request: {
          number: 7,
          title: 'spec: SLA overdue',
          body: `
## Specification
### problem-statement
Problem statement

### success-metric
Metric

### acceptance-criteria
1. Criterion

### user-story
Story
          `,
          labels: ['spec-pipeline', 'spec-stage:pm'],
          draft: false,
          created_at: stageStartTime.toISOString(),
          updated_at: new Date().toISOString(),
        },
      });

      const findings = await runSpecRouter(prContext, 'sla-check');

      const slaFinding = findings.find(
        (f) => f.severity === 'warning' && f.message.includes('SLA')
      );
      expect(slaFinding).toBeDefined();
      expect(slaFinding?.message).toContain('exceeded');

      // SLA message is in the main message field
      expect(slaFinding?.message).toContain('SLA EXCEEDED');
      expect(slaFinding?.message).toContain('28h');
    });

    it('sla-check: approaching 24h limit returns WARNING status', async () => {
      const stageStartTime = new Date(Date.now() - 22 * 60 * 60 * 1000); // 22 hours ago

      const prContext = JSON.stringify({
        pull_request: {
          number: 8,
          title: 'spec: SLA warning',
          body: `
## Specification
### problem-statement
Problem

### success-metric
Metric

### acceptance-criteria
1. Criterion

### user-story
Story
          `,
          labels: ['spec-pipeline', 'spec-stage:architect'],
          draft: false,
          created_at: stageStartTime.toISOString(),
          updated_at: new Date().toISOString(),
        },
      });

      const findings = await runSpecRouter(prContext, 'sla-check');

      const slaFinding = findings.find((f) =>
        f.message.includes('SLA')
      );
      expect(slaFinding).toBeDefined();

      // SLA message is in the main message field
      expect(slaFinding?.message).toContain('⚠️ SLA WARNING');
      expect(slaFinding?.message).toContain('2h remaining');
    });
  });

  // ============ Test 4: Stage Routing ============

  describe('Automatic Stage Routing', () => {
    it('route: detects current stage and provides next stage info', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 9,
          title: 'spec: Routing test',
          body: 'Full spec with all fields',
          labels: ['spec-pipeline', 'spec-stage:analyst'],
          draft: false,
          created_at: '2026-03-26T09:00:00Z',
          updated_at: '2026-03-26T11:00:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'route');

      expect(findings).toBeDefined();

      const routeFinding = findings.find(
        (f) => f.message.includes('next stage') ||
          f.message.includes('Routing')
      );
      expect(routeFinding).toBeDefined();

      // Check that next stage is mentioned in message
      expect(routeFinding?.message).toContain('pm');
      expect(routeFinding?.message).toContain('@egos/pms');
    });

    it('route: final stage (SM) indicates spec is complete', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 10,
          title: 'spec: Final stage',
          body: 'Complete spec',
          labels: ['spec-pipeline', 'spec-stage:sm'],
          draft: false,
          created_at: '2026-03-26T18:00:00Z',
          updated_at: '2026-03-26T20:00:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'route');

      const completeFinding = findings.find(
        (f) => f.message.includes('complete') ||
          f.message.includes('No further')
      );
      expect(completeFinding).toBeDefined();
      expect(completeFinding?.message).toContain(
        'ready for implementation'
      );
    });
  });

  // ============ Test 5: Edge Cases ============

  describe('Edge Cases', () => {
    it('handles PR without spec-pipeline label gracefully', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 11,
          title: 'regular: Some feature',
          body: 'Regular PR without spec-pipeline',
          labels: ['feature'],
          draft: false,
          created_at: '2026-03-26T09:00:00Z',
          updated_at: '2026-03-26T09:30:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');

      expect(findings).toBeDefined();
      expect(findings.length).toBeGreaterThan(0);

      const infoFinding = findings.find((f) =>
        f.message.includes('Skipping')
      );
      expect(infoFinding).toBeDefined();
      expect(infoFinding?.severity).toBe('info');
    });

    it('handles draft PRs in spec-pipeline', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 12,
          title: 'spec: Draft spec',
          body: 'Draft specification',
          labels: ['spec-pipeline', 'spec-stage:analyst'],
          draft: true,
          created_at: '2026-03-26T09:00:00Z',
          updated_at: '2026-03-26T09:30:00Z',
        },
      });

      // Should still process even if draft
      const findings = await runSpecRouter(prContext, 'validate');
      expect(findings).toBeDefined();
    });

    it('handles multiple stage labels (should pick first one)', async () => {
      const prContext = JSON.stringify({
        pull_request: {
          number: 13,
          title: 'spec: Multiple labels',
          body: 'Spec',
          labels: [
            'spec-pipeline',
            'spec-stage:analyst',
            'spec-stage:pm',
          ],
          draft: false,
          created_at: '2026-03-26T09:00:00Z',
          updated_at: '2026-03-26T09:30:00Z',
        },
      });

      const findings = await runSpecRouter(prContext, 'validate');
      expect(findings).toBeDefined();
      // Should detect analyst as current stage (first in order)
    });
  });
});

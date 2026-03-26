/**
 * Spec-Pipeline Router Agent
 *
 * Orchestrates the multi-stage specification review workflow:
 * analyst → pm → architect → sm
 *
 * Responsibilities:
 * - Detect spec-pipeline labeled PRs
 * - Validate mandatory fields per stage
 * - Route tasks to appropriate reviewers (CODEOWNERS)
 * - Track SLA (24h per stage)
 * - Block merge if evidence missing
 * - Auto-update status and labels
 *
 * Triggers:
 * - PR labeled with `spec-pipeline`
 * - PR review submitted (approval/changes)
 * - Scheduled SLA check (every 1 hour)
 *
 * Output:
 * - PR label updates (stage progression)
 * - Reviewer assignments
 * - SLA tracking comments
 * - Merge block if evidence missing
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import type { Finding } from '../runtime/runner';

// --- Configuration ---

const SPEC_PIPELINE_LABEL = 'spec-pipeline';
const STAGE_LABELS = {
  analyst: 'spec-stage:analyst',
  pm: 'spec-stage:pm',
  architect: 'spec-stage:architect',
  sm: 'spec-stage:sm',
};

const APPROVAL_REQUIREMENTS = {
  analyst: 2,
  pm: 2,
  architect: 2,
  sm: 1,
};

const SLA_HOURS = 24;

interface StageConfig {
  name: string;
  label: string;
  requiredApprovals: number;
  codeowner: string;
  mandatoryFields: string[];
}

const STAGES: Record<string, StageConfig> = {
  analyst: {
    name: 'Specification',
    label: STAGE_LABELS.analyst,
    requiredApprovals: APPROVAL_REQUIREMENTS.analyst,
    codeowner: '@egos/analysts',
    mandatoryFields: [
      'problem-statement',
      'success-metric',
      'acceptance-criteria',
      'user-story',
    ],
  },
  pm: {
    name: 'Product Review',
    label: STAGE_LABELS.pm,
    requiredApprovals: APPROVAL_REQUIREMENTS.pm,
    codeowner: '@egos/pms',
    mandatoryFields: [
      'business-impact',
      'go-no-go-decision',
      'risk-assessment',
      'scope-confirmation',
    ],
  },
  architect: {
    name: 'Architecture Review',
    label: STAGE_LABELS.architect,
    requiredApprovals: APPROVAL_REQUIREMENTS.architect,
    codeowner: '@egos/architects',
    mandatoryFields: [
      'architecture-diagram',
      'technical-risks',
      'api-schema-changes',
      'complexity-assessment',
      'dependency-audit',
    ],
  },
  sm: {
    name: 'Stakeholder Markup',
    label: STAGE_LABELS.sm,
    requiredApprovals: APPROVAL_REQUIREMENTS.sm,
    codeowner: '@egos/scrum-masters',
    mandatoryFields: [
      'resource-allocation',
      'timeline-mapping',
      'communication-plan',
      'readiness-checklist',
    ],
  },
};

// --- Helpers ---

interface PRContext {
  prNumber: number;
  title: string;
  body: string;
  labels: string[];
  approvals: Map<string, number>; // role -> count
  currentStage: string | null;
  stagedAt?: string;
  isDraft: boolean;
}

interface ValidationResult {
  valid: boolean;
  missingFields: string[];
  evidence: Record<string, string | null>;
}

function parseGitHubEvent(eventStr: string): PRContext | null {
  try {
    // In real implementation, this parses webhook or API response
    // For demo purposes, we accept a structure like:
    const event = JSON.parse(eventStr);
    if (!event.pull_request) {
      return null;
    }

    const pr = event.pull_request;
    const labels = pr.labels?.map((l: any) => l.name) || [];

    return {
      prNumber: pr.number,
      title: pr.title,
      body: pr.body || '',
      labels,
      approvals: new Map(),
      currentStage: detectCurrentStage(labels),
      isDraft: pr.draft || false,
    };
  } catch (e) {
    console.error(`Failed to parse GitHub event: ${e}`);
    return null;
  }
}

function detectCurrentStage(labels: string[]): string | null {
  for (const [stage, config] of Object.entries(STAGES)) {
    if (labels.includes(config.label)) {
      return stage;
    }
  }
  return null;
}

function validateMandatoryFields(
  body: string,
  fields: string[]
): ValidationResult {
  const evidence: Record<string, string | null> = {};
  const missingFields: string[] = [];

  for (const field of fields) {
    // Look for markdown headers or explicit field markers
    const patterns = [
      new RegExp(`### ${field}.*?\n(.*?)(?=###|$)`, 'is'),
      new RegExp(`## ${field}.*?\n(.*?)(?=##|###|$)`, 'is'),
      new RegExp(`\\*\\*${field}\\*\\*:?.*?\n(.*?)(?=\\*\\*|##|###|$)`, 'is'),
    ];

    let found = false;
    for (const pattern of patterns) {
      const match = body.match(pattern);
      if (match && match[1]?.trim()) {
        evidence[field] = match[1].trim().substring(0, 100); // First 100 chars
        found = true;
        break;
      }
    }

    if (!found) {
      missingFields.push(field);
    }
  }

  return {
    valid: missingFields.length === 0,
    missingFields,
    evidence,
  };
}

function formatSLAStatus(
  stageStartTime: string,
  currentTime: string,
  approvals: number,
  required: number
): { exceeded: boolean; remaining: number; message: string } {
  const start = new Date(stageStartTime);
  const now = new Date(currentTime);
  const hours = (now.getTime() - start.getTime()) / (1000 * 60 * 60);
  const exceeded = hours > SLA_HOURS;
  const remaining = Math.ceil(SLA_HOURS - hours);

  let message = '';
  if (exceeded) {
    message = `⏱️ SLA EXCEEDED (${Math.ceil(hours)}h elapsed, limit: ${SLA_HOURS}h)`;
  } else if (remaining <= 4) {
    message = `⚠️ SLA WARNING (${remaining}h remaining)`;
  } else {
    message = `✅ SLA OK (${remaining}h remaining)`;
  }

  return { exceeded, remaining, message };
}

function formatHandoffTemplate(stage: string, nextStage: string | null): string {
  const stageConfig = STAGES[stage];
  if (!stageConfig) return '';

  const nextConfig = nextStage ? STAGES[nextStage] : null;

  return `## [${stageConfig.name.toUpperCase()}] Handoff — \`AUTO-GENERATED\`

### Status
- [ ] Evidence present and complete
- [ ] Approval gates met (${stageConfig.requiredApprovals} reviewers)
- [ ] SLA within limit (< ${SLA_HOURS}h)

### Summary
[Summarize what was reviewed and approved in the ${stageConfig.name} stage]

### Evidence Links
${stageConfig.mandatoryFields.map((f) => `- ${f}: [LINK_TO_EVIDENCE]`).join('\n')}

### Next Stage Prepared
${nextConfig ? `${nextConfig.name} review is ready. Assigning to \`${nextConfig.codeowner}\`` : 'This spec is COMPLETE and ready for implementation.'}

### Reviewer Attribution
- Approved by @[reviewer1], @[reviewer2]
- Decision timestamp: \`[ISO_8601_TIMESTAMP]\`
`;
}

function generateMergeBlockReason(missingFields: string[], stage: string): string {
  return `
## 🚫 Merge Blocked — Spec-Pipeline Incomplete

**Current Stage:** ${STAGES[stage]?.name || stage}
**Blocking Reason:** Missing mandatory evidence fields

### Missing Evidence Fields
${missingFields.map((f) => `- [ ] ${f}`).join('\n')}

### Action Required
1. Add the missing fields to the PR description
2. Include concrete links (screenshots, docs, data)
3. Request approval again from reviewers

### Approval Gate Status
- Required approvals: ${APPROVAL_REQUIREMENTS[stage as keyof typeof APPROVAL_REQUIREMENTS] || 1}
- Current approvals: Pending mandatory field validation

The spec-pipeline contract requires all evidence before advancement.
See: \`.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md\`
`;
}

// --- Main Agent Logic ---

export async function runSpecRouter(
  prContext: string,
  mode: 'validate' | 'route' | 'sla-check' | 'advance' = 'validate'
): Promise<Finding[]> {
  const findings: Finding[] = [];

  // Parse input
  const pr = parseGitHubEvent(prContext);
  if (!pr) {
    findings.push({
      severity: 'info',
      category: 'spec-pipeline',
      message: 'No PR context or spec-pipeline label detected. Skipping.',
    });
    return findings;
  }

  // Check if spec-pipeline enabled
  if (!pr.labels.includes(SPEC_PIPELINE_LABEL)) {
    findings.push({
      severity: 'info',
      category: 'spec-pipeline',
      message: `PR #${pr.prNumber} does not have '${SPEC_PIPELINE_LABEL}' label. Skipping.`,
    });
    return findings;
  }

  // Determine current stage
  const currentStage = pr.currentStage || 'analyst';
  const stageConfig = STAGES[currentStage];

  if (!stageConfig) {
    findings.push({
      severity: 'error',
      category: 'spec-pipeline',
      message: `Unknown stage: ${currentStage}`,
    });
    return findings;
  }

  console.log(`Spec-Router: Processing PR #${pr.prNumber} (stage: ${currentStage})`);

  // Mode: Validate mandatory fields
  if (mode === 'validate') {
    const validation = validateMandatoryFields(pr.body, stageConfig.mandatoryFields);

    if (!validation.valid) {
      const blockReason = generateMergeBlockReason(validation.missingFields, currentStage);
      findings.push({
        severity: 'error',
        category: 'spec-pipeline:validation',
        message: `Spec-Pipeline validation failed: missing fields: ${validation.missingFields.join(', ')}`,
        file: `PR #${pr.prNumber}`,
        suggestion: blockReason,
      });

      // In real impl: Set GitHub check to "fail" and block merge
    } else {
      findings.push({
        severity: 'info',
        category: 'spec-pipeline:validation',
        message: `✅ Spec-Pipeline validation passed for stage: ${currentStage}`,
        file: `PR #${pr.prNumber}`,
      });
    }
  }

  // Mode: Route to next stage
  if (mode === 'route') {
    const stageOrder = ['analyst', 'pm', 'architect', 'sm'];
    const currentIndex = stageOrder.indexOf(currentStage);
    const nextIndex = currentIndex + 1;

    if (nextIndex >= stageOrder.length) {
      findings.push({
        severity: 'info',
        category: 'spec-pipeline:route',
        message: `Spec-Pipeline complete. No further stages. PR ready for implementation.`,
        file: `PR #${pr.prNumber}`,
      });
      return findings;
    }

    const nextStage = stageOrder[nextIndex];
    const nextConfig = STAGES[nextStage];
    const handoffTemplate = formatHandoffTemplate(currentStage, nextStage);

    findings.push({
      severity: 'info',
      category: 'spec-pipeline:route',
      message: `Routing to next stage: ${nextConfig.name} (assign to ${nextConfig.codeowner})`,
      file: `PR #${pr.prNumber}`,
      suggestion: `Handoff template:\n\n${handoffTemplate}`,
    });

    // In real impl: Remove current label, add next label, assign reviewers
  }

  // Mode: SLA check
  if (mode === 'sla-check') {
    const now = new Date().toISOString();
    const stageStartTime = pr.stagedAt || now;

    const slaStatus = formatSLAStatus(stageStartTime, now, 0, stageConfig.requiredApprovals);

    if (slaStatus.exceeded) {
      findings.push({
        severity: 'warning',
        category: 'spec-pipeline:sla',
        message: slaStatus.message,
        file: `PR #${pr.prNumber}`,
      });
    } else {
      findings.push({
        severity: 'info',
        category: 'spec-pipeline:sla',
        message: slaStatus.message,
        file: `PR #${pr.prNumber}`,
      });
    }

    // In real impl: Post SLA comment on PR (every 1 hour)
  }

  return findings;
}

// --- CLI Entry Point ---

async function main() {
  const args = process.argv.slice(2);
  const mode = (args[0] as any) || 'validate';
  const prContextPath = args[1];

  if (!prContextPath || !existsSync(prContextPath)) {
    console.error(`Usage: spec-router <mode> <pr_context.json>`);
    console.error(`Modes: validate | route | sla-check | advance`);
    process.exit(1);
  }

  const contextStr = readFileSync(prContextPath, 'utf-8');
  const findings = await runSpecRouter(contextStr, mode as any);

  // Output findings
  for (const finding of findings) {
    const prefix =
      finding.severity === 'error'
        ? '❌'
        : finding.severity === 'warning'
          ? '⚠️'
          : '✅';
    console.log(`${prefix} [${finding.severity.toUpperCase()}] ${finding.message}`);

    if (finding.suggestion) {
      console.log(`\nSuggestion:\n${finding.suggestion}`);
    }
  }

  // Exit with error code if validation failed
  const hasErrors = findings.some((f) => f.severity === 'error');
  process.exit(hasErrors ? 1 : 0);
}

if (require.main === module) {
  main().catch(console.error);
}

export default runSpecRouter;

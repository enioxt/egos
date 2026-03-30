import { getPRIGate, type PRIDecision, type PRIRequest, type PRIStrategy } from '../../../packages/core/src/guards/pri.js';

const SUPPORTED_PII_TYPES = new Set(['cpf', 'rg', 'masp', 'placa', 'email', 'phone', 'processo', 'pix_key']);

type FindingLike = { category: string };

export interface PRIOptions {
  piiTypes?: string[];
  strategy?: PRIStrategy;
  context?: PRIRequest['context'];
}

function normalizeType(value: string): string | null {
  const normalized = value.toLowerCase().replace(/-/g, '_');
  if (normalized === 'telefone') return 'phone';
  if (normalized === 'placa_veiculo') return 'placa';
  return SUPPORTED_PII_TYPES.has(normalized) ? normalized : null;
}

function derivePIITypes(explicit: string[] = [], findings: FindingLike[] = []) {
  const types = new Set<string>();

  for (const value of explicit) {
    const normalized = normalizeType(value);
    if (normalized) types.add(normalized);
  }

  for (const finding of findings) {
    const normalized = normalizeType(finding.category);
    if (normalized) types.add(normalized);
  }

  return [...types];
}

export async function evaluatePRI(text: string, options: PRIOptions, findings: FindingLike[] = []): Promise<PRIDecision | null> {
  const pii_types = derivePIITypes(options.piiTypes, findings);
  const hasContext = Boolean(options.context?.impacts_fundamental_rights || options.context?.is_admin_action);

  if (pii_types.length === 0 && !hasContext) return null;

  return getPRIGate(options.strategy).evaluate({
    text,
    pii_types,
    strategy: options.strategy,
    context: options.context,
  });
}

export function shouldBlockOnPRI(decision: PRIDecision | null, explicitPIITypes?: string[]) {
  return Boolean(decision && decision.output === 'BLOCK' && explicitPIITypes?.length);
}

export function requiresManualReview(decision: PRIDecision | null) {
  return decision?.output === 'DEFER' || decision?.output === 'ESCALATE' || decision?.output === 'STUDY';
}

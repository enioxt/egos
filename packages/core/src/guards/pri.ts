/**
 * PRI — Protocolo de Recuo por Ignorância (Protocol of Retreat by Ignorance)
 * Safety gate for Guard Brasil API
 *
 * Core: "Ignorância não é permissão. Ignorância é gatilho de pausa."
 * When confidence is low, escalate. Never default to ALLOW on uncertainty.
 */

import { createHash } from 'crypto';

// ── Types ──────────────────────────────────────────────────────

export type PRIOutput = 'ALLOW' | 'BLOCK' | 'DEFER' | 'ESCALATE' | 'STUDY';

export type PRIStrategy = 'paranoid' | 'balanced' | 'permissive';

export interface PRIDecision {
  output: PRIOutput;
  confidence: number; // 0-100
  reasoning: string;
  missing_signals: string[];
  classifiers_consulted: string[];
  timestamp: string;
  audit_hash: string;
}

export interface PRIRequest {
  text: string;
  pii_types?: string[];
  atrian_validation?: boolean;
  strategy?: PRIStrategy;
  context?: {
    impacts_fundamental_rights?: boolean;
    is_admin_action?: boolean;
    user_id?: string;
  };
}

export interface PRIAuditEvent {
  event_id: string;
  timestamp: string;
  request_hash: string;
  decision: PRIDecision;
  classifiers: {
    name: string;
    result: string;
    confidence: number;
    latency_ms: number;
  }[];
  user_id?: string;
  cost_usd: number;
  signature?: string;
}

// ── Configuration by Strategy ──────────────────────────────────

const THRESHOLDS: Record<PRIStrategy, Record<PRIOutput, number>> = {
  paranoid: {
    ALLOW: 95,
    BLOCK: 90,
    DEFER: 60,
    ESCALATE: 40,
    STUDY: 0,
  },
  balanced: {
    ALLOW: 90,
    BLOCK: 85,
    DEFER: 60,
    ESCALATE: 40,
    STUDY: 0,
  },
  permissive: {
    ALLOW: 80,
    BLOCK: 70,
    DEFER: 50,
    ESCALATE: 30,
    STUDY: 0,
  },
};

// ── Layer 1: Fast Path (Regex + Pattern Matching) ──────────────

const PII_PATTERNS: Record<string, RegExp> = {
  cpf: /\d{3}\.\d{3}\.\d{3}-\d{2}/,
  rg: /\d{1,2}\.?\d{3}\.?\d{3}[-/]?\d{1,2}/,
  masp: /\d{7}[-/]\d{1}/,
  placa: /[A-Z]{3}-?\d{4}|[A-Z]{3}\d{1}[A-Z]{1}\d{2}/,
  email: /\S+@\S+\.\S+/,
  phone: /\(?\d{2}\)?[\s-]?\d{4,5}[-\s]?\d{4}/,
  processo: /\d{7}-?\d{2}\.?\d{4}\.?\d{1}\.?\d{2}/,
  pix_key: /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/,
};

function layerOne(text: string, pii_types: string[]): { output: PRIOutput; confidence: number; reasoning: string; classifiers: string[] } {
  const classifiers: string[] = [];

  for (const pii_type of pii_types) {
    const pattern = PII_PATTERNS[pii_type];
    if (!pattern) {
      classifiers.push(`unknown_pattern:${pii_type}`);
      continue;
    }
    if (pattern.test(text)) {
      classifiers.push(`regex:${pii_type}:match`);
      return {
        output: 'ALLOW',
        confidence: 95,
        reasoning: `Explicit ${pii_type} pattern matched`,
        classifiers,
      };
    }
    classifiers.push(`regex:${pii_type}:nomatch`);
  }

  // No regex match → continue to layer 2
  return {
    output: 'DEFER', // will be updated by layer 2
    confidence: 0,
    reasoning: 'No regex match found for requested PII types',
    classifiers,
  };
}

// ── Layer 2: Semantic Check (Heuristics + Context) ──────────────

const BIAS_SIGNALS = [
  'favela',
  'periférico',
  'comunidade',
  'criminalidade',
  'risco social',
  'raça',
  'gênero',
  'orientação sexual',
  'deficiência',
  'religião',
];

const FALSE_POSITIVE_PATTERNS = [
  /^test|^demo|^example/i, // test data
];

function layerTwo(text: string, context?: any): { output: PRIOutput; confidence: number; reasoning: string; classifiers: string[] } {
  const classifiers: string[] = [];

  // Check for false positive patterns
  for (const pattern of FALSE_POSITIVE_PATTERNS) {
    if (pattern.test(text)) {
      classifiers.push('false_positive_pattern');
      return {
        output: 'BLOCK',
        confidence: 85,
        reasoning: 'Matches test/demo pattern, likely not real PII',
        classifiers,
      };
    }
  }

  // Check for bias signals (LGPD compliance)
  if (context?.impacts_fundamental_rights) {
    const hasBiasSignal = BIAS_SIGNALS.some((signal) => text.toLowerCase().includes(signal));
    if (hasBiasSignal) {
      classifiers.push('bias_signal_detected');
      return {
        output: 'ESCALATE',
        confidence: 85,
        reasoning: 'Text contains protected characteristic — human review required (LGPD Art. 9)',
        classifiers,
      };
    }
  }

  // Ambiguous: pure numbers without context
  if (/^\d+$/.test(text.trim())) {
    classifiers.push('ambiguous_number');
    return {
      output: 'DEFER',
      confidence: 45,
      reasoning: 'Numeric sequence — could be CPF, phone, ID. Need more context.',
      classifiers,
    };
  }

  // No heuristic match → continue to layer 3
  return {
    output: 'DEFER',
    confidence: 0,
    reasoning: 'No heuristic decision',
    classifiers,
  };
}

// ── Layer 3: LLM Evaluation (Qwen-plus) ──────────────────────────

// Mock implementation (would call actual LLM in production)
async function layerThree(text: string, pii_types: string[]): Promise<{ output: PRIOutput; confidence: number; reasoning: string; classifiers: string[] }> {
  // In production: call Qwen API or Gemini
  // For now: simple heuristic as placeholder

  const classifiers: string[] = ['llm_mock'];

  // If text contains common PII prefixes
  if (/cpf|rg|masp|placa|email|phone|processo/i.test(text)) {
    return {
      output: 'ALLOW',
      confidence: 90,
      reasoning: 'LLM confirmed PII context',
      classifiers,
    };
  }

  // Suspicious patterns
  if (/SELECT|INSERT|DELETE|DROP/i.test(text)) {
    return {
      output: 'BLOCK',
      confidence: 90,
      reasoning: 'SQL injection pattern detected',
      classifiers,
    };
  }

  // Default: cannot determine
  return {
    output: 'STUDY',
    confidence: 30,
    reasoning: 'LLM could not classify pattern',
    classifiers,
  };
}

// ── Layer 4: Admin Override ────────────────────────────────────

function layerFour(context?: any): { output: PRIOutput; confidence: number; reasoning: string } | null {
  if (context?.is_admin_action) {
    // In production: verify signature, audit log
    return {
      output: 'ALLOW',
      confidence: 100,
      reasoning: 'Admin override with audit log',
    };
  }
  return null;
}

// ── Main PRI Evaluator ─────────────────────────────────────────

export class PRIGate {
  private strategy: PRIStrategy = 'balanced';
  private auditLog: PRIAuditEvent[] = [];

  constructor(strategy?: PRIStrategy) {
    if (strategy) this.strategy = strategy;
  }

  async evaluate(request: PRIRequest): Promise<PRIDecision> {
    const startTime = Date.now();
    const pii_types = request.pii_types || [];
    const strategy = request.strategy || this.strategy;

    try {
      // Layer 4: Admin override (instant, no other layers)
      const adminResult = layerFour(request.context);
      if (adminResult) {
        return this.finalizeDecision(adminResult, [], 'admin_override', Date.now() - startTime);
      }

      // Layer 1: Fast path (regex + patterns)
      const l1_result = layerOne(request.text, pii_types);
      if (l1_result.output !== 'DEFER') {
        return this.finalizeDecision(l1_result, l1_result.classifiers, 'layer_1', Date.now() - startTime);
      }

      // Layer 2: Semantic check (heuristics)
      const l2_result = layerTwo(request.text, request.context);
      if (l2_result.output !== 'DEFER' || l2_result.confidence > 0) {
        return this.finalizeDecision(l2_result, l2_result.classifiers, 'layer_2', Date.now() - startTime);
      }

      // Layer 3: LLM evaluation (if needed)
      if (l2_result.confidence < 60) {
        const l3_result = await layerThree(request.text, pii_types);
        return this.finalizeDecision(l3_result, l3_result.classifiers, 'layer_3', Date.now() - startTime);
      }

      // Default: Cannot determine, use strategy thresholds
      const thresholds = THRESHOLDS[strategy];
      const conf = l2_result.confidence;
      let output: PRIOutput = 'STUDY';

      if (conf >= thresholds.ALLOW) output = 'ALLOW';
      else if (conf >= thresholds.BLOCK) output = 'BLOCK';
      else if (conf >= thresholds.DEFER) output = 'DEFER';
      else if (conf >= thresholds.ESCALATE) output = 'ESCALATE';

      return this.finalizeDecision(
        { output, confidence: conf, reasoning: 'Strategy-based fallback' },
        l2_result.classifiers,
        'strategy_fallback',
        Date.now() - startTime,
      );
    } catch (error) {
      // System error: conservative default
      const context = request.context;
      const fallbackOutput = context?.impacts_fundamental_rights ? 'ESCALATE' : 'BLOCK';

      return this.finalizeDecision(
        {
          output: fallbackOutput,
          confidence: 0,
          reasoning: `System error: ${(error as any).message} — safe default applied`,
        },
        ['system_error'],
        'error_handler',
        Date.now() - startTime,
      );
    }
  }

  private finalizeDecision(
    decision: { output: PRIOutput; confidence: number; reasoning: string },
    classifiers: string[],
    source: string,
    duration_ms: number,
  ): PRIDecision {
    const timestamp = new Date().toISOString();
    const request_hash = createHash('sha256').update(Math.random().toString()).digest('hex').slice(0, 8);
    const audit_hash = createHash('sha256')
      .update(`${timestamp}:${decision.output}:${request_hash}`)
      .digest('hex');

    const result: PRIDecision = {
      output: decision.output,
      confidence: decision.confidence,
      reasoning: decision.reasoning,
      missing_signals:
        decision.output === 'DEFER' ? ['more_context', 'semantic_clarity'] : decision.output === 'STUDY' ? ['pattern_definition', 'training_data'] : [],
      classifiers_consulted: classifiers,
      timestamp,
      audit_hash,
    };

    // Log audit event
    this.auditLog.push({
      event_id: `pri-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp,
      request_hash,
      decision: result,
      classifiers: classifiers.map((c) => ({
        name: c,
        result: decision.output,
        confidence: decision.confidence,
        latency_ms: duration_ms,
      })),
      cost_usd: 0.00001, // placeholder
    });

    return result;
  }

  getAuditLog(filter?: { output?: PRIOutput; since?: Date }): PRIAuditEvent[] {
    return this.auditLog.filter((event) => {
      if (filter?.output && event.decision.output !== filter.output) return false;
      if (filter?.since && new Date(event.timestamp) < filter.since) return false;
      return true;
    });
  }

  getMetrics() {
    const total = this.auditLog.length;
    if (total === 0) return { total: 0, distribution: {}, avg_confidence: 0 };

    const distribution: Record<PRIOutput, number> = {
      ALLOW: 0,
      BLOCK: 0,
      DEFER: 0,
      ESCALATE: 0,
      STUDY: 0,
    };

    let totalConfidence = 0;

    for (const event of this.auditLog) {
      distribution[event.decision.output]++;
      totalConfidence += event.decision.confidence;
    }

    return {
      total,
      distribution,
      avg_confidence: Math.round(totalConfidence / total),
      percentages: {
        ALLOW: Math.round((distribution.ALLOW / total) * 100),
        BLOCK: Math.round((distribution.BLOCK / total) * 100),
        DEFER: Math.round((distribution.DEFER / total) * 100),
        ESCALATE: Math.round((distribution.ESCALATE / total) * 100),
        STUDY: Math.round((distribution.STUDY / total) * 100),
      },
    };
  }
}

// ── Singleton Instance ─────────────────────────────────────────

let priInstance: PRIGate | null = null;

export function getPRIGate(strategy?: PRIStrategy): PRIGate {
  if (!priInstance) {
    priInstance = new PRIGate(strategy);
  }
  return priInstance;
}

// ── Export for testing ─────────────────────────────────────────

export { layerOne, layerTwo, layerThree, layerFour };

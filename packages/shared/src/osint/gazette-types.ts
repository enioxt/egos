/**
 * gazette-types.ts — @egos/shared/osint
 *
 * Canonical type definitions for Brazilian public gazette (Diário Oficial)
 * data structures and opportunity records.
 *
 * Used by:
 * - egos-lab/apps/eagle-eye — primary consumer
 * - Any kernel agent that processes gazette data
 *
 * LGPD note: All gazette content is public government data (no PII handling needed at this layer).
 */

// ─── Gazette Source ───────────────────────────────────────────────────────────

export type GazetteScope = 'federal' | 'estadual' | 'municipal';
export type GazetteSection = 'licitacoes' | 'contratos' | 'atos_normativos' | 'pessoal' | 'comunicados' | 'outros';

export interface GazetteSource {
  /** IBGE municipality code or state abbreviation */
  territory: string;
  scope: GazetteScope;
  /** Official gazette name, e.g. "Diário Oficial do Estado de Minas Gerais" */
  name: string;
  /** Base URL for fetching */
  baseUrl: string;
  /** API provider, e.g. "querido-diario" | "diario-oficial" | "custom" */
  provider: 'querido-diario' | 'diario-oficial' | 'custom';
}

// ─── Gazette Record ───────────────────────────────────────────────────────────

export interface GazetteRecord {
  id: string;
  source: GazetteSource;
  /** ISO date string */
  publishedAt: string;
  fetchedAt: string;
  section: GazetteSection;
  /** Raw extracted text */
  rawText: string;
  /** URL to original document */
  sourceUrl: string;
  /** Optional: PDF page number */
  page?: number;
}

// ─── Opportunity ──────────────────────────────────────────────────────────────

export type OpportunityCategory =
  | 'licitacao'       // Public tender
  | 'chamada_publica' // Public call
  | 'parceria_ong'    // NGO partnership
  | 'evento'          // Local event / fair / festival
  | 'turismo'         // Tourism-related opportunity
  | 'infraestrutura'  // Infrastructure contract
  | 'tecnologia'      // IT / tech contract
  | 'saude'           // Healthcare
  | 'educacao'        // Education
  | 'outro';

export type OpportunityStatus = 'open' | 'closing_soon' | 'closed' | 'awarded' | 'cancelled';

export interface OpportunityRecord {
  id: string;
  /** Reference to originating gazette record */
  gazetteId: string;
  category: OpportunityCategory;
  status: OpportunityStatus;
  title: string;
  description: string;
  /** IBGE territory code */
  territory: string;
  /** Estimated or stated value in BRL */
  valueBrl?: number;
  /** ISO deadline date */
  deadline?: string;
  /** Issuing organization */
  issuingOrg: string;
  /** Contact information (public only — no PII) */
  contactPublic?: string;
  /** When this record was first extracted */
  extractedAt: string;
  /** Source URL for verification */
  sourceUrl: string;
}

// ─── Viability Score ─────────────────────────────────────────────────────────

export interface ViabilityScore {
  opportunityId: string;
  /** 0–100 composite score */
  overall: number;
  breakdown: {
    /** How well the opportunity fits the operator's profile */
    profileFit: number;       // 0–25
    /** Market size and demand signal */
    marketSize: number;       // 0–25
    /** How competitive the opportunity is (lower competition = higher score) */
    competitiveness: number;  // 0–25
    /** Urgency / closing timeline */
    urgency: number;          // 0–25
  };
  reasoning: string;
  scoredAt: string;
  /** Model used for scoring */
  model: string;
  /** ATRiAN ethical validation score (0–100) — required for AI-generated assessments */
  atrianScore?: number;
}

// ─── Batch Scan ───────────────────────────────────────────────────────────────

export interface ScanRequest {
  sources: GazetteSource[];
  /** ISO start date */
  fromDate: string;
  /** ISO end date */
  toDate: string;
  categories?: OpportunityCategory[];
  maxResults?: number;
  /** Minimum viability score to include */
  minScore?: number;
}

export interface ScanResult {
  requestId: string;
  startedAt: string;
  completedAt: string;
  sourcesScanned: number;
  recordsFound: number;
  opportunitiesExtracted: number;
  opportunities: OpportunityRecord[];
  scores: ViabilityScore[];
  errors: Array<{ source: string; error: string }>;
}

export type PIICategory = 'cpf' | 'rg' | 'masp' | 'phone' | 'email' | 'reds' | 'process_number' | 'name' | 'address' | 'plate' | 'date_of_birth';
export interface PIIFinding { category: PIICategory; label: string; matched: string; start: number; end: number; suggestion: string; }
export interface PIIPatternDefinition { category: PIICategory; label: string; pattern: RegExp; suggestion: string; }

export const DEFAULT_PII_PATTERNS: PIIPatternDefinition[] = [
  { category: 'cpf', label: 'CPF', pattern: /\b\d{3}[.\s-]?\d{3}[.\s-]?\d{3}[.\s/-]?\d{2}\b/g, suggestion: '[CPF REMOVIDO]' },
  { category: 'rg', label: 'RG', pattern: /\b(?:RG|rg|Rg)[:\s]*\d{1,2}[.\s]?\d{3}[.\s]?\d{3}[.\s-]?\d?\b/gi, suggestion: '[RG REMOVIDO]' },
  { category: 'masp', label: 'MASP', pattern: /\b(?:MASP|masp|Masp)[:\s]*\d{4,8}[.\s-]?\d{0,2}\b/gi, suggestion: '[MASP REMOVIDO]' },
  { category: 'phone', label: 'Telefone', pattern: /\b(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}[-.\s]?\d{4}\b/g, suggestion: '[TELEFONE REMOVIDO]' },
  { category: 'email', label: 'Email', pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, suggestion: '[EMAIL REMOVIDO]' },
  { category: 'reds', label: 'REDS', pattern: /\b(?:REDS|reds|Reds)[:\s]*\d{4,}[-./]?\d{0,}\b/gi, suggestion: '[REDS REMOVIDO]' },
  { category: 'process_number', label: 'Processo', pattern: /\b\d{7}[-.]?\d{2}[.]?\d{4}[.]?\d[.]?\d{2}[.]?\d{4}\b/g, suggestion: '[PROCESSO REMOVIDO]' },
  { category: 'plate', label: 'Placa', pattern: /\b[A-Z]{3}[-\s]?\d[A-Z0-9]\d{2}\b/gi, suggestion: '[PLACA REMOVIDA]' },
  { category: 'date_of_birth', label: 'Data de Nascimento', pattern: /\b(?:nascido|nascimento|nasc\.?|DN|dn)[:\s]*\d{1,2}[\/.-]\d{1,2}[\/.-]\d{2,4}\b/gi, suggestion: '[DATA REMOVIDA]' },
];

const DEFAULT_NAME_PATTERN = /\b(?:delegad[oa]|chefe|colega|servidor|investigador|escriv[aã]o?|comissário|perito|agente)\s+([A-ZÁÉÍÓÚÃÕÂÊÎÔÛ][a-záéíóúãõâêîôû]+(?:\s+[A-ZÁÉÍÓÚÃÕÂÊÎÔÛ][a-záéíóúãõâêîôû]+){1,4})\b/g;
const clonePattern = (pattern: RegExp) => new RegExp(pattern.source, pattern.flags.includes('g') ? pattern.flags : `${pattern.flags}g`);

export function scanForPII(text: string, options?: { patterns?: PIIPatternDefinition[]; namePattern?: RegExp }): PIIFinding[] {
  const findings: PIIFinding[] = [];
  const patterns = options?.patterns ?? DEFAULT_PII_PATTERNS;
  for (const { category, label, suggestion, pattern } of patterns) {
    const activePattern = clonePattern(pattern);
    let match: RegExpExecArray | null;
    while ((match = activePattern.exec(text)) !== null) findings.push({ category, label, matched: match[0], start: match.index, end: match.index + match[0].length, suggestion });
  }
  const namePattern = clonePattern(options?.namePattern ?? DEFAULT_NAME_PATTERN);
  let nameMatch: RegExpExecArray | null;
  while ((nameMatch = namePattern.exec(text)) !== null) {
    const name = nameMatch[1];
    if (name && name.length > 3) findings.push({ category: 'name', label: 'Possível nome', matched: name, start: nameMatch.index + nameMatch[0].indexOf(name), end: nameMatch.index + nameMatch[0].indexOf(name) + name.length, suggestion: '[NOME REMOVIDO]' });
  }
  return deduplicateFindings(findings.sort((a, b) => a.start - b.start));
}

export function sanitizeText(text: string, findings: PIIFinding[]): string {
  let result = text;
  for (const finding of [...findings].sort((a, b) => b.start - a.start)) result = result.slice(0, finding.start) + finding.suggestion + result.slice(finding.end);
  return result;
}

export function getPIISummary(findings: PIIFinding[]): string {
  if (findings.length === 0) return 'Nenhum dado sensível detectado.';
  return `Detectamos ${findings.length} dado(s) sensível(is): ${[...new Set(findings.map((finding) => finding.label))].join(', ')}.`;
}

function deduplicateFindings(findings: PIIFinding[]) {
  const result: PIIFinding[] = [];
  let lastEnd = -1;
  for (const finding of findings) if (finding.start >= lastEnd) { result.push(finding); lastEnd = finding.end; }
  return result;
}

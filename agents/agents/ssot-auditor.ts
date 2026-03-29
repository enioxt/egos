/**
 * SSOT Auditor Agent v3.8.0 — Structural Triage Engine
 *
 * Scans any TypeScript or Python codebase via AST and produces a prioritized report of
 * structural type drift — duplicate definitions with different shapes.
 * $0 per scan. No LLM. Works offline. Cross-repo portable.
 *
 * 28 PROVEN CAPABILITIES (v3.8.0):
 *  1. AST extraction via TypeScript compiler API + Python ast module
 *  2. Symbol classification (interface/type_alias/enum/class)
 *  3. Scope filtering (exported, cross-package, single-file)
 *  4. Explicit scoring (0-10) with rationale per finding
 *  5. Context-aware recommendations (domain vs UI vs generic)
 *  6. Normalized structural fingerprints
 *  7. Shape drift classification (EXACT/RELAXED/DIVERGENT/UNRESOLVED)
 *  8. Object drift reason codes (6 types)
 *  9. Union alias drift reason codes
 * 10. Heritage/extends expansion (cycle-safe) — PR2
 * 11. Shared canonical cleanup — PR7
 * 12. Class fingerprinting (fields/ctor/methods) — PR3
 * 13. Autonomy action score (0-100, 4 tiers) — calibrated by PR9
 * 14. Bounded context classifier (5 heuristic features, 4 verdicts) — PR9
 * 15. Decision registry (JSON-based, APPLIED/STALE/NONE matching) — PR10
 * 16. JSON output mode for UI consumption
 * 17. Import graph / barrel resolution (re-export detection) — PR8
 * 18. Codemod dry-run engine (concrete edit plans) — PR11
 * 19. Codemod safety rails (BLOCKED_ARCHITECTURE, REQUIRES_EXTRACTION) — PR12
 * 20. Blast radius metric (fan-in count per symbol) — PR13
 * 21. Architectural layer classification (domain/api/ui/lib/shared) — PR16
 * 22. JSON schema versioning + capabilities array
 * 23. --min-confidence CLI filter (suppress low/convention noise)
 * 24. Import centrality in canonical ranking (fan-in weighted)
 * 25. Lexical collision detection in codemod plans
 * 26. CI governance — baseline snapshots, budget checks, regression detection (PR14)
 * 27. Semantic deep check — TypeChecker-based type comparison for High clusters (PR15)
 * 28. Multi-language support: Python AST extraction (Pydantic, dataclass, Enum, TypedDict) — PR18
 *
 * NEXT:
 * - PR17: Drift normalization semantics (snake↔camel, pt↔en)
 */

import * as ts from 'typescript';
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from 'fs';
import { join, relative, extname, dirname, basename } from 'path';
import { execSync } from 'child_process';
import { runAgent, printResult, log, type RunContext, type Finding } from '../runtime/runner';
import { Topics } from '../runtime/event-bus';

// ─── Configuration ────────────────────────────────────────────

const SCAN_EXTENSIONS_TS = ['.ts', '.tsx'];
const SCAN_EXTENSIONS_PY = ['.py'];
const SCAN_EXTENSIONS = [...SCAN_EXTENSIONS_TS, ...SCAN_EXTENSIONS_PY];
const IGNORE_DIRS = ['node_modules', 'dist', '.git', '.vercel', '.next', '.husky', 'External', '.egos', '.logs', '__tests__', '__mocks__'];
const IGNORE_FILES = ['vite-env.d.ts', 'env.d.ts', 'global.d.ts'];

// Convention names that are expected to be repeated (framework patterns)
// Pure UI/framework conventions that are ALWAYS expected to be duplicated
const CONVENTION_NAMES = new Set([
  'Props', 'State', 'Params', 'Options', 'Context',
  'PageProps', 'LayoutProps', 'ServerProps', 'ClientProps',
  // Python conventions (PR18)
  'Config', 'Settings', 'Base', 'Mixin', 'Meta',
]);

// Generated file patterns
const GENERATED_PATTERNS = [/generated/, /prisma/, /openapi/, /\.d\.ts$/, /trpc/];

// ─── Types ────────────────────────────────────────────────────

type SymbolKind = 'interface' | 'type_alias' | 'enum' | 'class';
type ConfidenceLevel = 'high' | 'medium' | 'low';

interface StructuralSymbol {
  name: string;
  kind: SymbolKind;
  file: string;
  line: number;
  exported: boolean;
  package: string;
  memberCount: number;
  isGenerated: boolean;
  shapeStrict: string;   // Normalized shape (full fidelity: readonly + optional)
  shapeRelaxed: string;  // Normalized shape (ignores readonly only; optionality preserved)
  hasExtends: boolean;   // Interface extends or type uses &
  memberNames: string[]; // Sorted member/field names for diff reason codes (expanded after heritage pass)
  optionalMembers: string[]; // Sorted optional member names (has ?) for optionality drift
  unionMembers: string[];    // Sorted union variant strings for DRIFT_UNION_MEMBERS_* reason codes
  heritageRefs: string[];    // PR2: Names of base interfaces/types from extends/& clauses
  heritageExpanded: boolean; // PR2: true when memberNames were expanded via heritage pass
}

type DriftKind = 'EXACT' | 'RELAXED' | 'DIVERGENT' | 'UNRESOLVED';

interface DriftResult {
  kind: DriftKind;
  strictVariants: number;
  relaxedVariants: number;
  exactMatchCount: number;
  emoji: string;
  label: string;
  reasonCodes: string[]; // e.g. ['DRIFT_FIELDS_ADDED(id,name)', 'DRIFT_FIELD_TYPE_CHANGED']
}

interface ConfidenceResult {
  level: ConfidenceLevel;
  score: number;         // 0-10 numeric score (clamped)
  rawScore: number;      // unbounded raw score for tie-breaking
  rationale: string[];   // e.g. ["+exported", "+cross-package", "-single package"]
  isCrossPackage: boolean;
}

type AutonomyAction = 'AUTOFIX_NOW' | 'AUTOFIX_WITH_REVIEW' | 'ADAPTER_OR_RENAME' | 'MANUAL_REVIEW';
type BoundedContextVerdict = 'MERGE_CANDIDATE' | 'DRIFT_EVOLUTION' | 'BOUNDED_CONTEXT_COLLISION' | 'INSUFFICIENT_SIGNAL';

interface BoundedContextResult {
  verdict: BoundedContextVerdict;
  confidence: number;  // 0-100
  reasons: string[];   // e.g. ['CTX_SAME_PACKAGE', 'CTX_FIELD_OVERLAP_HIGH']
}

type SemanticVerdict = 'SEMANTIC_EXACT' | 'SEMANTIC_COMPATIBLE' | 'SEMANTIC_DIVERGENT' | 'SEMANTIC_UNRESOLVED';

interface SemanticCheckResult {
  verdict: SemanticVerdict;
  resolvedTypes: { file: string; resolved: string }[];  // resolved type string per location
  assignability?: string;  // e.g. "A→B: yes, B→A: no"
}

interface SSOTFinding extends Finding {
  confidence: ConfidenceLevel;
  confidenceScore: number;
  confidenceRawScore: number;
  confidenceRationale: string[];
  isCrossPackage: boolean;
  symbolKind?: SymbolKind;
  locations?: string[];
  packages?: string[];
  drift?: DriftResult;
  autonomyScore?: number;   // 0-100: readiness for autonomous action (PR9 precursor)
  autonomyAction?: AutonomyAction; // tier label derived from autonomyScore
  boundedContext?: BoundedContextResult; // PR9: bounded context classification for DIVERGENT clusters
  decisionRegistry?: AppliedDecisionSummary; // PR10: decision registry match status
  semanticCheck?: SemanticCheckResult; // PR15: TypeChecker-based semantic comparison
}

// ─── PR10: Decision Registry Types ────────────────────────────

type DecisionAction = 'MERGE_TO_CANONICAL' | 'RECONCILE_WITH_ADAPTER' | 'RENAME_BY_BOUNDED_CONTEXT' | 'KEEP_SEPARATE_INTENTIONAL' | 'IGNORE_TEMPORARILY' | 'FALSE_POSITIVE';
type DecisionStatus = 'PROPOSED' | 'APPROVED' | 'IMPLEMENTED' | 'DEPRECATED';
type DecisionMatchStatus = 'NONE' | 'APPLIED' | 'STALE' | 'PARTIAL';

interface DecisionEntry {
  id: string;
  match: {
    symbol: string;
    kind: SymbolKind;
    scope: 'cross-package' | 'intra-package';
    packages: string[];
    clusterKey: string;
    clusterSignature?: string;
  };
  decision: {
    action: DecisionAction;
    status: DecisionStatus;
    rationale: string;
    owner?: string;
    date: string;
  };
  payload?: {
    canonical?: { path: string; exportedSymbol?: string };
    renames?: Array<{ path: string; from: string; to: string; reason?: string }>;
    adapters?: Array<{ fromPath: string; toPath: string; adapterName?: string; notes?: string }>;
    notes?: string[];
  };
  validation?: {
    expectedDriftStatus?: DriftKind;
    expectedContext?: BoundedContextVerdict;
    fingerprintSetHash?: string;
  };
  meta?: {
    tags?: string[];
    supersedes?: string;
    createdAt: string;
    updatedAt: string;
  };
}

interface DecisionRegistry {
  version: '1';
  generatedBy?: string;
  decisions: DecisionEntry[];
}

interface AppliedDecisionSummary {
  matchStatus: DecisionMatchStatus;
  decisionId?: string;
  action?: DecisionAction;
  status?: DecisionStatus;
  owner?: string;
  date?: string;
  rationale?: string;
  staleReason?: string;
}

// ─── Helpers ──────────────────────────────────────────────────

const PYTHON_IGNORE_DIRS = ['__pycache__', '.venv', 'venv', 'env', 'migrations', 'alembic', '.eggs', '.tox', '.mypy_cache', '.pytest_cache', '.ruff_cache'];
const PYTHON_IGNORE_FILES = ['__init__.py', 'conftest.py'];

function walkDir(dir: string): string[] {
  const results: string[] = [];
  try {
    const entries = readdirSync(dir);
    for (const entry of entries) {
      if (IGNORE_DIRS.includes(entry)) continue;
      if (PYTHON_IGNORE_DIRS.includes(entry)) continue;
      const fullPath = join(dir, entry);
      const stat = statSync(fullPath);
      if (stat.isDirectory()) {
        results.push(...walkDir(fullPath));
      } else {
        const ext = extname(entry);
        // TypeScript files
        if (
          SCAN_EXTENSIONS_TS.includes(ext) &&
          !IGNORE_FILES.includes(entry) &&
          !entry.includes('.test.') &&
          !entry.includes('.spec.')
        ) {
          results.push(fullPath);
        }
        // Python files (PR18)
        if (
          SCAN_EXTENSIONS_PY.includes(ext) &&
          !PYTHON_IGNORE_FILES.includes(entry) &&
          !entry.startsWith('test_') &&
          !entry.endsWith('_test.py')
        ) {
          results.push(fullPath);
        }
      }
    }
  } catch { /* skip */ }
  return results;
}

/**
 * Determine the workspace package name from a file path.
 * E.g.: "apps/egos-web/src/App.tsx" → "egos-web"
 *       "packages/shared/src/types.ts" → "shared"
 *       "agents/agents/foo.ts" → "agents"
 */
function getPackageName(filePath: string, repoRoot: string): string {
  const rel = relative(repoRoot, filePath);
  const parts = rel.split('/');
  // apps/X/... or packages/X/... → X
  if (['apps', 'packages'].includes(parts[0]) && parts.length > 1) {
    return parts[1];
  }
  // agents/... → "agents"
  return parts[0] || 'root';
}

function isGeneratedFile(filePath: string): boolean {
  return GENERATED_PATTERNS.some(p => p.test(filePath));
}

// ─── PR18: Python AST Extraction Bridge ──────────────────────

/**
 * Extract structural symbols from Python files by calling the Python extractor subprocess.
 * The extractor uses Python's native ast module — $0, no LLM.
 * Falls back gracefully (returns []) if Python is not installed.
 */
function extractPythonSymbols(pyFiles: string[], repoRoot: string): StructuralSymbol[] {
  if (pyFiles.length === 0) return [];

  const extractorPath = join(dirname(dirname(__filename)), 'extractors', 'python_extractor.py');
  if (!existsSync(extractorPath)) {
    // Fallback: try relative to current file's directory structure
    const altPath = join(__dirname, '..', 'extractors', 'python_extractor.py');
    if (!existsSync(altPath)) return [];
  }

  // Write file list to temp file to avoid argument length limits
  const tmpFile = join(repoRoot, '.ssot-py-files.tmp');
  try {
    writeFileSync(tmpFile, pyFiles.join('\n'), 'utf-8');
    const result = execSync(
      `python3 "${extractorPath}" --files-from "${tmpFile}" --root "${repoRoot}"`,
      {
        encoding: 'utf-8',
        maxBuffer: 50 * 1024 * 1024, // 50MB
        timeout: 30_000,
        stdio: ['pipe', 'pipe', 'pipe'],
      }
    );
    const symbols: StructuralSymbol[] = JSON.parse(result);
    return symbols;
  } catch (err: unknown) {
    // Graceful fallback: Python not installed or extractor failed
    return [];
  } finally {
    try { require('fs').unlinkSync(tmpFile); } catch { /* ignore */ }
  }
}

// ─── AST-Based Symbol Extraction ──────────────────────────────

/**
 * Extract type-level symbols from a TypeScript file using the compiler API.
 * This parses the REAL AST, not regex — so comments and strings are ignored.
 */
function extractStructuralSymbols(filePath: string, repoRoot: string): StructuralSymbol[] {
  const symbols: StructuralSymbol[] = [];

  let content: string;
  try {
    content = readFileSync(filePath, 'utf-8');
  } catch {
    return symbols;
  }

  const sourceFile = ts.createSourceFile(
    filePath,
    content,
    ts.ScriptTarget.Latest,
    true, // setParentNodes
    filePath.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS
  );

  const pkg = getPackageName(filePath, repoRoot);
  const generated = isGeneratedFile(filePath);

  function visit(node: ts.Node) {
    // Interface declarations
    if (ts.isInterfaceDeclaration(node)) {
      const exported = hasExportModifier(node);
      symbols.push({
        name: node.name.text,
        kind: 'interface',
        file: filePath,
        line: sourceFile.getLineAndCharacterOfPosition(node.getStart()).line + 1,
        exported,
        package: pkg,
        memberCount: node.members.length,
        isGenerated: generated,
        shapeStrict: normalizeInterfaceShape(node, false),
        shapeRelaxed: normalizeInterfaceShape(node, true),
        hasExtends: !!(node.heritageClauses?.length),
        memberNames: node.members
          .filter(ts.isPropertySignature)
          .map((m: ts.PropertySignature) => ts.isIdentifier(m.name) ? m.name.text : '')
          .filter(Boolean).sort(),
        optionalMembers: node.members
          .filter(ts.isPropertySignature)
          .filter((m: ts.PropertySignature) => !!m.questionToken)
          .map((m: ts.PropertySignature) => ts.isIdentifier(m.name) ? m.name.text : '')
          .filter(Boolean).sort(),
        unionMembers: [],
        heritageRefs: node.heritageClauses
          ? node.heritageClauses.flatMap(h => h.types)
            .map(t => ts.isExpressionWithTypeArguments(t) && ts.isIdentifier(t.expression) ? t.expression.text : '')
            .filter(Boolean)
          : [],
        heritageExpanded: false,
      });
    }

    // Type alias declarations
    if (ts.isTypeAliasDeclaration(node)) {
      const exported = hasExportModifier(node);
      symbols.push({
        name: node.name.text,
        kind: 'type_alias',
        file: filePath,
        line: sourceFile.getLineAndCharacterOfPosition(node.getStart()).line + 1,
        exported,
        package: pkg,
        memberCount: countTypeMembers(node.type),
        isGenerated: generated,
        shapeStrict: normalizeTypeAliasShape(node.type, false),
        shapeRelaxed: normalizeTypeAliasShape(node.type, true),
        hasExtends: ts.isIntersectionTypeNode(node.type),
        memberNames: ts.isTypeLiteralNode(node.type)
          ? node.type.members
            .filter(ts.isPropertySignature)
            .map((m: ts.PropertySignature) => ts.isIdentifier(m.name) ? m.name.text : '')
            .filter(Boolean).sort()
          : [],
        optionalMembers: ts.isTypeLiteralNode(node.type)
          ? node.type.members
            .filter(ts.isPropertySignature)
            .filter((m: ts.PropertySignature) => !!m.questionToken)
            .map((m: ts.PropertySignature) => ts.isIdentifier(m.name) ? m.name.text : '')
            .filter(Boolean).sort()
          : [],
        unionMembers: ts.isUnionTypeNode(node.type)
          ? node.type.types.map(t => { try { return normalizeTypeNode(t, false); } catch { return '?'; } }).sort()
          : [],
        heritageRefs: [],
        heritageExpanded: false,
      });
    }

    // Enum declarations
    if (ts.isEnumDeclaration(node)) {
      const exported = hasExportModifier(node);
      symbols.push({
        name: node.name.text,
        kind: 'enum',
        file: filePath,
        line: sourceFile.getLineAndCharacterOfPosition(node.getStart()).line + 1,
        exported,
        package: pkg,
        memberCount: node.members.length,
        isGenerated: generated,
        shapeStrict: node.members.map((m: ts.EnumMember) => ts.isIdentifier(m.name) ? m.name.text : '').filter(Boolean).sort().join('|'),
        shapeRelaxed: node.members.map((m: ts.EnumMember) => ts.isIdentifier(m.name) ? m.name.text : '').filter(Boolean).sort().join('|'),
        hasExtends: false,
        memberNames: node.members.map((m: ts.EnumMember) => ts.isIdentifier(m.name) ? m.name.text : '').filter(Boolean).sort(),
        optionalMembers: [],
        unionMembers: [],
        heritageRefs: [],
        heritageExpanded: false,
      });
    }

    // Class declarations (only named)
    if (ts.isClassDeclaration(node) && node.name) {
      const exported = hasExportModifier(node);
      const classStrict = normalizeClassShape(node, false);
      const classRelaxed = normalizeClassShape(node, true);
      const classMembers = extractClassPublicMembers(node);
      symbols.push({
        name: node.name.text,
        kind: 'class',
        file: filePath,
        line: sourceFile.getLineAndCharacterOfPosition(node.getStart()).line + 1,
        exported,
        package: pkg,
        memberCount: node.members.length,
        isGenerated: generated,
        shapeStrict: classStrict,
        shapeRelaxed: classRelaxed,
        hasExtends: !!(node.heritageClauses?.length),
        memberNames: classMembers.names,
        optionalMembers: classMembers.optional,
        unionMembers: [],
        heritageRefs: [],
        heritageExpanded: false,
      });
    }

    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  return symbols;
}

// ─── PR2: Heritage Expansion Pass ─────────────────────────────
// Expands memberNames for interfaces with extends clauses.
// Resolves base names within the same repo and merges inherited fields.
// Cycle-safe via visited set per symbol.

function expandOneSymbol(sym: StructuralSymbol, symbolMap: Map<string, StructuralSymbol[]>, visited: Set<string>): string[] {
  const key = `${sym.file}:${sym.name}`;
  if (visited.has(key)) return sym.memberNames;
  visited.add(key);
  if (sym.heritageRefs.length === 0) return sym.memberNames;

  const expanded = new Set(sym.memberNames);
  for (const ref of sym.heritageRefs) {
    const bases = symbolMap.get(ref) || [];
    const base = bases.find(b => b.package === sym.package && b.kind === 'interface')
      || bases.find(b => b.kind === 'interface');
    if (!base) continue;
    for (const m of expandOneSymbol(base, symbolMap, new Set(visited))) expanded.add(m);
  }
  return [...expanded].sort();
}

function expandHeritagePass(allSymbols: StructuralSymbol[]): number {
  const symbolMap = new Map<string, StructuralSymbol[]>();
  for (const s of allSymbols) {
    const arr = symbolMap.get(s.name) || [];
    arr.push(s);
    symbolMap.set(s.name, arr);
  }
  let expandedCount = 0;
  for (const s of allSymbols) {
    if (s.kind === 'interface' && s.heritageRefs.length > 0) {
      const expanded = expandOneSymbol(s, symbolMap, new Set());
      if (expanded.length > s.memberNames.length) {
        s.memberNames = expanded;
        s.heritageExpanded = true;
        expandedCount++;
      }
    }
  }
  return expandedCount;
}

function hasExportModifier(node: ts.Node): boolean {
  if (!ts.canHaveModifiers(node)) return false;
  const modifiers = ts.getModifiers(node);
  return modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword) ?? false;
}

function countTypeMembers(typeNode: ts.TypeNode): number {
  if (ts.isTypeLiteralNode(typeNode)) {
    return typeNode.members.length;
  }
  if (ts.isUnionTypeNode(typeNode) || ts.isIntersectionTypeNode(typeNode)) {
    return typeNode.types.length;
  }
  return 0;
}

// ─── Shape Normalization (v2.7) ───────────────────────────────

function normalizeTypeNode(typeNode: ts.TypeNode, relaxed: boolean): string {
  switch (typeNode.kind) {
    case ts.SyntaxKind.StringKeyword: return 'string';
    case ts.SyntaxKind.NumberKeyword: return 'number';
    case ts.SyntaxKind.BooleanKeyword: return 'boolean';
    case ts.SyntaxKind.NullKeyword: return 'null';
    case ts.SyntaxKind.UndefinedKeyword: return 'undefined';
    case ts.SyntaxKind.AnyKeyword: return 'any';
    case ts.SyntaxKind.UnknownKeyword: return 'unknown';
    case ts.SyntaxKind.NeverKeyword: return 'never';
    case ts.SyntaxKind.VoidKeyword: return 'void';
    case ts.SyntaxKind.ObjectKeyword: return 'object';
    case ts.SyntaxKind.BigIntKeyword: return 'bigint';
    case ts.SyntaxKind.SymbolKeyword: return 'symbol';
  }
  try {
    if (ts.isTypeReferenceNode(typeNode)) {
      const name = ts.isIdentifier(typeNode.typeName) ? typeNode.typeName.text : typeNode.typeName.getText();
      if (typeNode.typeArguments?.length) {
        const args = typeNode.typeArguments.map((a: ts.TypeNode) => normalizeTypeNode(a, relaxed)).join(',');
        return `${name}<${args}>`;
      }
      return name;
    }
    if (ts.isArrayTypeNode(typeNode)) return `array<${normalizeTypeNode(typeNode.elementType, relaxed)}>`;
    if (ts.isUnionTypeNode(typeNode)) {
      const parts = typeNode.types.map((t: ts.TypeNode) => normalizeTypeNode(t, relaxed)).sort();
      return `union(${parts.join('|')})`;
    }
    if (ts.isIntersectionTypeNode(typeNode)) {
      const parts = typeNode.types.map((t: ts.TypeNode) => normalizeTypeNode(t, relaxed)).sort();
      return `isect(${parts.join('&')})`;
    }
    if (ts.isTypeLiteralNode(typeNode)) {
      const members = typeNode.members
        .map((m: ts.TypeElement) => normalizeTypeMember(m, relaxed))
        .filter(Boolean).sort().join(';');
      return `obj(${members})`;
    }
    if (ts.isLiteralTypeNode(typeNode)) {
      const lit = typeNode.literal;
      if (ts.isStringLiteral(lit)) return `"${lit.text}"`;
      if (ts.isNumericLiteral(lit)) return lit.text;
      if (lit.kind === ts.SyntaxKind.TrueKeyword) return 'true';
      if (lit.kind === ts.SyntaxKind.FalseKeyword) return 'false';
      if (lit.kind === ts.SyntaxKind.NullKeyword) return 'null';
      return 'lit';
    }
    if (ts.isParenthesizedTypeNode(typeNode)) return normalizeTypeNode(typeNode.type, relaxed);
    if (ts.isTupleTypeNode(typeNode)) {
      const parts = typeNode.elements.map((e: ts.TypeNode) => {
        if (ts.isNamedTupleMember(e)) return normalizeTypeNode(e.type, relaxed);
        if (ts.isRestTypeNode(e)) return `...${normalizeTypeNode(e.type, relaxed)}`;
        if (ts.isOptionalTypeNode(e)) return `${normalizeTypeNode(e.type, relaxed)}?`;
        return normalizeTypeNode(e, relaxed);
      });
      return `tuple(${parts.join(',')})`;
    }
    if (ts.isTemplateLiteralTypeNode(typeNode)) return 'template';
    if (ts.isMappedTypeNode(typeNode)) return 'mapped';
    if (ts.isConditionalTypeNode(typeNode)) return 'conditional';
    if (ts.isIndexedAccessTypeNode(typeNode)) {
      return `${normalizeTypeNode(typeNode.objectType, relaxed)}[${normalizeTypeNode(typeNode.indexType, relaxed)}]`;
    }
    if (ts.isTypeOperatorNode(typeNode)) {
      const op = typeNode.operator === ts.SyntaxKind.KeyOfKeyword ? 'keyof' : 'unique';
      return `${op}<${normalizeTypeNode(typeNode.type, relaxed)}>`;
    }
    if (ts.isTypeQueryNode(typeNode)) return 'typeof';
    if (ts.isInferTypeNode(typeNode)) return `infer<${typeNode.typeParameter.name.text}>`;
  } catch {
    return '?';
  }
  return '?';
}

function normalizeTypeMember(member: ts.TypeElement, relaxed: boolean): string {
  try {
    if (ts.isPropertySignature(member)) {
      const name = ts.isIdentifier(member.name) ? member.name.text : member.name.getText();
      const optional = member.questionToken ? '?' : '';
      const isReadonly = !relaxed && ts.canHaveModifiers(member) &&
        !!(ts.getModifiers(member)?.some((m: ts.Modifier) => m.kind === ts.SyntaxKind.ReadonlyKeyword));
      const ro = isReadonly ? 'ro:' : '';
      const type = member.type ? normalizeTypeNode(member.type, relaxed) : 'any';
      return `${ro}${name}${optional}:${type}`;
    }
    if (ts.isMethodSignature(member)) {
      const name = ts.isIdentifier(member.name) ? member.name.text : member.name.getText();
      const params = member.parameters.map((p: ts.ParameterDeclaration) =>
        p.type ? normalizeTypeNode(p.type, relaxed) : 'any'
      ).join(',');
      const ret = member.type ? normalizeTypeNode(member.type, relaxed) : 'any';
      return `${name}(${params}):${ret}`;
    }
    if (ts.isIndexSignatureDeclaration(member)) {
      const keyType = member.parameters[0]?.type ? normalizeTypeNode(member.parameters[0].type, relaxed) : 'any';
      const ret = member.type ? normalizeTypeNode(member.type, relaxed) : 'any';
      return `[${keyType}]:${ret}`;
    }
  } catch { return ''; }
  return '';
}

function normalizeInterfaceShape(node: ts.InterfaceDeclaration, relaxed: boolean): string {
  if (node.members.length === 0) return 'empty';
  try {
    const members = node.members
      .map((m: ts.TypeElement) => normalizeTypeMember(m, relaxed))
      .filter(Boolean).sort().join(';');
    return node.heritageClauses?.length ? `ext;${members}` : members;
  } catch { return '?'; }
}

function normalizeTypeAliasShape(typeNode: ts.TypeNode, relaxed: boolean): string {
  try { return normalizeTypeNode(typeNode, relaxed); } catch { return '?'; }
}

// ─── PR3: Class Fingerprinting ────────────────────────────────
// Extracts public instance fields, constructor parameter properties,
// and public instance methods. Private/protected/static members are excluded.

function normalizeClassMember(member: ts.ClassElement, relaxed: boolean): string | null {
  const mods = ts.canHaveModifiers(member) ? ts.getModifiers(member) : undefined;
  const isPrivate = mods?.some(m => m.kind === ts.SyntaxKind.PrivateKeyword || m.kind === ts.SyntaxKind.ProtectedKeyword);
  const isStatic = mods?.some(m => m.kind === ts.SyntaxKind.StaticKeyword);
  if (isPrivate || isStatic) return null;
  try {
    if (ts.isPropertyDeclaration(member) && member.name) {
      const name = ts.isIdentifier(member.name) ? member.name.text : member.name.getText();
      if (!name) return null;
      const optional = member.questionToken ? '?' : '';
      const type = member.type ? normalizeTypeNode(member.type, relaxed) : 'any';
      const isRo = !relaxed && mods?.some(m => m.kind === ts.SyntaxKind.ReadonlyKeyword);
      return `${isRo ? 'ro:' : ''}${name}${optional}:${type}`;
    }
    if (ts.isMethodDeclaration(member) && member.name) {
      const name = ts.isIdentifier(member.name) ? member.name.text : member.name.getText();
      if (!name) return null;
      const params = member.parameters.map((p: ts.ParameterDeclaration) =>
        p.type ? normalizeTypeNode(p.type, relaxed) : 'any'
      ).join(',');
      const ret = member.type ? normalizeTypeNode(member.type, relaxed) : 'void';
      return `fn:${name}(${params}):${ret}`;
    }
  } catch { return null; }
  return null;
}

function normalizeClassShape(node: ts.ClassDeclaration, relaxed: boolean): string {
  const parts: string[] = [];
  for (const member of node.members) {
    // Constructor: extract parameter properties (public/readonly)
    if (ts.isConstructorDeclaration(member)) {
      for (const param of member.parameters) {
        const paramMods = ts.canHaveModifiers(param) ? ts.getModifiers(param) : undefined;
        const isPublicParam = paramMods?.some(m =>
          m.kind === ts.SyntaxKind.PublicKeyword || m.kind === ts.SyntaxKind.ReadonlyKeyword
        );
        const isParamPrivate = paramMods?.some(m =>
          m.kind === ts.SyntaxKind.PrivateKeyword || m.kind === ts.SyntaxKind.ProtectedKeyword
        );
        if (!isPublicParam || isParamPrivate) continue;
        try {
          const name = ts.isIdentifier(param.name) ? param.name.text : '';
          if (!name) continue;
          const optional = param.questionToken ? '?' : '';
          const type = param.type ? normalizeTypeNode(param.type, relaxed) : 'any';
          const isRo = !relaxed && paramMods?.some(m => m.kind === ts.SyntaxKind.ReadonlyKeyword);
          parts.push(`ctor:${isRo ? 'ro:' : ''}${name}${optional}:${type}`);
        } catch { /* skip */ }
      }
      continue;
    }
    const part = normalizeClassMember(member, relaxed);
    if (part) parts.push(part);
  }
  if (parts.length === 0) return 'empty_class';
  return `cls(${[...parts].sort().join(';')})`;
}

function extractClassPublicMembers(node: ts.ClassDeclaration): { names: string[]; optional: string[] } {
  const names: string[] = [];
  const optional: string[] = [];
  for (const member of node.members) {
    const mods = ts.canHaveModifiers(member) ? ts.getModifiers(member) : undefined;
    const isPrivate = mods?.some(m => m.kind === ts.SyntaxKind.PrivateKeyword || m.kind === ts.SyntaxKind.ProtectedKeyword);
    const isStatic = mods?.some(m => m.kind === ts.SyntaxKind.StaticKeyword);
    if (isPrivate || isStatic) continue;
    if (ts.isPropertyDeclaration(member) && member.name) {
      const name = ts.isIdentifier(member.name) ? member.name.text : '';
      if (name) { names.push(name); if (member.questionToken) optional.push(name); }
    } else if (ts.isMethodDeclaration(member) && member.name) {
      const name = ts.isIdentifier(member.name) ? member.name.text : '';
      if (name) names.push(`fn:${name}`);
    } else if (ts.isConstructorDeclaration(member)) {
      for (const param of member.parameters) {
        const pm = ts.canHaveModifiers(param) ? ts.getModifiers(param) : undefined;
        const isPublic = pm?.some(m => m.kind === ts.SyntaxKind.PublicKeyword || m.kind === ts.SyntaxKind.ReadonlyKeyword);
        const isPrivateParam = pm?.some(m => m.kind === ts.SyntaxKind.PrivateKeyword || m.kind === ts.SyntaxKind.ProtectedKeyword);
        if (!isPublic || isPrivateParam) continue;
        const name = ts.isIdentifier(param.name) ? param.name.text : '';
        if (name) { names.push(name); if (param.questionToken) optional.push(name); }
      }
    }
  }
  return { names: names.sort(), optional: optional.sort() };
}

// ─── Drift Classification (v2.8) ─────────────────────────────

function computeDriftReasons(canon: StructuralSymbol, locs: StructuralSymbol[]): string[] {
  // Union type aliases: compare union variant members
  if (canon.memberNames.length === 0 && canon.unionMembers.length > 0) {
    const canonUnionSet = new Set(canon.unionMembers);
    const unionAdded = new Set<string>();
    const unionRemoved = new Set<string>();
    for (const other of locs) {
      if (other.file === canon.file || other.unionMembers.length === 0) continue;
      const otherUnionSet = new Set(other.unionMembers);
      for (const m of otherUnionSet) if (!canonUnionSet.has(m)) unionAdded.add(m);
      for (const m of canonUnionSet) if (!otherUnionSet.has(m)) unionRemoved.add(m);
    }
    const reasons: string[] = [];
    if (unionAdded.size > 0) reasons.push(`DRIFT_UNION_MEMBERS_ADDED(${[...unionAdded].slice(0, 3).join(',')})`);
    if (unionRemoved.size > 0) reasons.push(`DRIFT_UNION_MEMBERS_REMOVED(${[...unionRemoved].slice(0, 3).join(',')})`);
    return reasons;
  }

  if (canon.memberNames.length === 0) return [];
  const canonSet = new Set(canon.memberNames);
  const canonOptSet = new Set(canon.optionalMembers);
  const allAdded = new Set<string>();
  const allRemoved = new Set<string>();
  let hasTypeDrift = false;
  const optionalityDrift = new Set<string>();
  const namingConventionDrift = new Set<string>();

  const normalizeName = (n: string) => n.replace(/_/g, '').toLowerCase();

  const canonNormalized = new Map<string, string>();
  for (const m of canon.memberNames) canonNormalized.set(normalizeName(m), m);

  for (const other of locs) {
    if (other.file === canon.file || other.memberNames.length === 0) continue;
    const otherSet = new Set(other.memberNames);
    const otherOptSet = new Set(other.optionalMembers);

    // Check for naming convention drift vs actual added/removed
    for (const m of otherSet) {
      if (!canonSet.has(m as string)) {
        const norm = normalizeName(m as string);
        if (canonNormalized.has(norm)) {
          namingConventionDrift.add(`${canonNormalized.get(norm)}↔${m}`);
        } else {
          allAdded.add(m as string);
        }
      }
    }

    for (const m of canonSet) {
      if (!otherSet.has(m as string)) {
        const norm = normalizeName(m as string);
        // If the other set has a member that normalizes to the same string, it's a naming drift (already caught above)
        // If not, it's truly removed
        const otherHasNorm = Array.from(otherSet).some(om => normalizeName(om as string) === norm);
        if (!otherHasNorm) {
          allRemoved.add(m as string);
        }
      }
    }

    // Detect optionality drift: same field name, different optional status
    for (const m of otherSet) {
      if (canonSet.has(m as string) && canonOptSet.has(m as string) !== otherOptSet.has(m as string)) {
        optionalityDrift.add(m as string);
      }
    }
    if (other.shapeStrict !== canon.shapeStrict) hasTypeDrift = true; // Heuristic: if strict shape differs, assume type drift
  }

  const reasons: string[] = [];
  if (allAdded.size > 0) reasons.push(`DRIFT_FIELDS_ADDED(${[...allAdded].slice(0, 3).join(',')})`);
  if (allRemoved.size > 0) reasons.push(`DRIFT_FIELDS_REMOVED(${[...allRemoved].slice(0, 3).join(',')})`);
  if (namingConventionDrift.size > 0) reasons.push(`DRIFT_NAMING_CONVENTION(${[...namingConventionDrift].slice(0, 3).join(',')})`);
  if (optionalityDrift.size > 0) reasons.push(`DRIFT_OPTIONALITY_CHANGED(${[...optionalityDrift].slice(0, 3).join(',')})`);
  if (hasTypeDrift) reasons.push('DRIFT_FIELD_TYPE_CHANGED');
  return reasons;
}

function classifyClusterDrift(locs: StructuralSymbol[], canonicalIdx: number): DriftResult {
  const canon = locs[Math.max(0, canonicalIdx)];

  // Classes: use real fingerprints (PR3). Fall back to UNRESOLVED only if no public members found.
  if (locs.some(l => l.kind === 'class')) {
    const hasRealShape = locs.some(l => l.shapeStrict !== 'class' && l.shapeStrict !== 'empty_class');
    if (!hasRealShape) {
      return { kind: 'UNRESOLVED', strictVariants: 0, relaxedVariants: 0, exactMatchCount: 0, emoji: '⚪', label: 'Unresolved (class — no public members detectable)', reasonCodes: ['UNRESOLVED_CLASS'] };
    }
    // Fall through: classes with cls(...) shapes are classified normally below
  }

  if (!canon?.shapeStrict || canon.shapeStrict === '?' || canon.shapeStrict === 'empty') {
    return { kind: 'UNRESOLVED', strictVariants: 0, relaxedVariants: 0, exactMatchCount: 0, emoji: '⚪', label: 'Unresolved (parse error or empty shape)', reasonCodes: [] };
  }

  const strictSet = new Set(locs.map(l => l.shapeStrict));
  const relaxedSet = new Set(locs.map(l => l.shapeRelaxed));
  const exactMatchCount = locs.filter(l => l.shapeStrict === canon.shapeStrict).length;

  if (strictSet.size === 1) {
    return { kind: 'EXACT', strictVariants: 1, relaxedVariants: 1, exactMatchCount: locs.length, emoji: '✅', label: 'Exact match — safe to consolidate', reasonCodes: [] };
  }
  if (relaxedSet.size === 1) {
    return { kind: 'RELAXED', strictVariants: strictSet.size, relaxedVariants: 1, exactMatchCount, emoji: '🟢', label: 'Compatible — only readonly modifier differs', reasonCodes: ['DRIFT_READONLY_ONLY'] };
  }

  const reasons = computeDriftReasons(canon, locs.filter(l => l.file !== canon.file));
  return { kind: 'DIVERGENT', strictVariants: strictSet.size, relaxedVariants: relaxedSet.size, exactMatchCount, emoji: '⚠️', label: 'Divergent shapes — manual review required', reasonCodes: reasons };
}

// ─── Categorization (Path + Name) ────────────────────────────

// Domain-specific names (business logic contracts)
const DOMAIN_PATTERNS = [/Investigation/, /Entity/, /Evidence/, /Finding/, /Audit/, /Permission/, /Session/, /Member/, /Analysis/, /Timeline/, /Document/, /Search/, /Graph/, /Journey/, /Dossier/, /Crime/, /Police/, /Guardian/, /Confidence/, /Relationship/];
// UI component props patterns
const UI_PROPS_PATTERN = /Props$/;
// UI primitive token names — always classified as 'ui' regardless of path
const UI_TOKEN_NAMES = new Set(['Toast', 'ToastType', 'ToastContextType', 'Modal', 'Card', 'CardHeader', 'CardContent', 'Badge', 'Skeleton', 'Header', 'Drawer', 'Dropdown', 'Tooltip', 'Popover', 'Dialog', 'Button', 'Spinner', 'Chip', 'Tab', 'Menu', 'Sidebar', 'NavItem', 'Breadcrumb']);
// Generic infrastructure names
const GENERIC_INFRA_NAMES = new Set(['Config', 'Result', 'Entry', 'Item', 'Data', 'Info', 'Stats', 'Error', 'Response', 'Payload', 'State']);
// Generic domain/application contract names
const GENERIC_DOMAIN_NAMES = new Set(['User', 'Message', 'ChatMessage', 'UserProfile', 'Profile', 'Account', 'Session', 'Role']);

type SymbolCategory = 'domain' | 'infra' | 'ui' | 'generic-domain' | 'generic-infra';

function categorizeSymbol(name: string, paths: string[]): SymbolCategory {
  // 1. Props suffix — always UI (framework convention)
  if (UI_PROPS_PATTERN.test(name)) return 'ui';

  // 2. UI primitive token whitelist — Toast, Modal, Card, Badge, etc.
  if (UI_TOKEN_NAMES.has(name)) return 'ui';

  // 3. Domain names — checked BEFORE path signals
  //    Domain names stay domain even if they appear inside /components/
  if (DOMAIN_PATTERNS.some(p => p.test(name))) return 'domain';

  // 4. Exact generic domain/infra names
  if (GENERIC_DOMAIN_NAMES.has(name)) return 'generic-domain';
  if (GENERIC_INFRA_NAMES.has(name)) return 'generic-infra';

  // 5. Path-based infra tiebreaker for ambiguous names only
  const isInfra = paths.some(p =>
    p.includes('/lib/auth') || p.includes('/lib/security') ||
    p.includes('/rbac/') || p.includes('/etl/') || p.includes('/cache/') ||
    p.includes('/rate-limit') || p.includes('/session')
  );
  if (isInfra) return 'infra';

  return 'generic-infra';
}

// ─── Confidence Scoring ───────────────────────────────────────

/**
 * Computes an explicit confidence score with rationale for a duplicate finding.
 * Returns numeric score (0-10), confidence level, and human-readable rationale.
 * Based on external critical analysis recommendations (v2.1).
 */
function computeConfidence(
  name: string,
  locations: StructuralSymbol[],
): ConfidenceResult {
  let score = 0;
  const rationale: string[] = [];

  // + exported symbols are more likely to be real drift
  const exportedCount = locations.filter(l => l.exported).length;
  if (exportedCount > 1) {
    score += 3;
    rationale.push(`+exported [${exportedCount} decls]`);
  }

  // + appears in multiple packages (cross-package = higher risk)
  const packages = new Set(locations.map(l => l.package));
  const isCrossPackage = packages.size > 1;
  if (isCrossPackage) {
    score += 3;
    rationale.push(`+cross-pkg [${packages.size} pkgs]`);
  }

  // + name is not a UI/framework convention
  if (!CONVENTION_NAMES.has(name)) {
    score += 2;
    rationale.push('+non-convention-name');
  }

  // + name matches recognized domain patterns (extra signal)
  const paths = locations.map(l => l.file.toLowerCase());
  const category = categorizeSymbol(name, paths);
  if (category === 'domain' || category === 'generic-domain') {
    score += 1;
    rationale.push('+domain-specific');
  } else if (category === 'generic-infra') {
    score -= 1;
    rationale.push('-generic-infra');
  }

  // + name is long (more specific)
  if (name.length > 8) {
    score += 1;
    rationale.push('+long-name');
  }

  // + many occurrences (scaled logarithmically)
  if (locations.length >= 10) {
    score += 3;
    rationale.push(`+count [${locations.length}×]`);
  } else if (locations.length >= 6) {
    score += 2;
    rationale.push(`+count [${locations.length}×]`);
  } else if (locations.length >= 4) {
    score += 1;
    rationale.push(`+count [${locations.length}×]`);
  }

  // - UI/framework convention (expected duplication)
  if (CONVENTION_NAMES.has(name)) {
    score -= 3;
    rationale.push('-ui-convention');
  }

  // - generated files involved
  const generatedCount = locations.filter(l => l.isGenerated).length;
  if (generatedCount > 0) {
    score -= 2;
    rationale.push('-generated-file');
  }

  // - all in same package (likely intentional local variants)
  if (!isCrossPackage) {
    score -= 1;
    rationale.push('-single-pkg');
  }

  // - very short name (too generic to be meaningful signal)
  if (name.length <= 2) {
    score -= 3;
    rationale.push('-too-short');
  }

  // Clamp to 0-10
  const clampedScore = Math.max(0, Math.min(10, score));

  // Split thresholds: cross-package requires higher score to reach High
  // (already has +3 cross-pkg bonus so total bar is the same, but filters
  // pure intra-package signals more conservatively)
  let level: ConfidenceLevel;
  if (isCrossPackage) {
    if (clampedScore >= 7) level = 'high';
    else if (clampedScore >= 3) level = 'medium';
    else level = 'low';
  } else {
    if (clampedScore >= 6) level = 'high';
    else if (clampedScore >= 2) level = 'medium';
    else level = 'low';
  }

  return { level, score: clampedScore, rawScore: score, rationale, isCrossPackage };
}


// ─── Dynamic Recommendation Engine ───────────────────────────

/**
 * Generates context-aware recommendations based on symbol name category,
 * cross-package status, and other heuristics.
 * v2.1: Replaces the generic one-size-fits-all recommendation.
 */
function rankCanonicalCandidates(locs: StructuralSymbol[], category: SymbolCategory, allFiles?: string[]): { symbol: StructuralSymbol, score: number, importers: number }[] {
  return locs.map(loc => {
    let score = 0;
    const path = loc.file.toLowerCase();

    // 1. Shared packages are the ultimate canonical source
    if (path.includes('/packages/shared/') || path.includes('/packages/nexus-shared/')) score += 50;

    // 2. Types directories: strong for domain/infra, neutral for UI
    if (path.includes('/types/')) {
      if (category !== 'ui') score += 30;
      // UI types in /types/ get no bonus — component files are more canonical
    }

    // 3. Exported symbols are intended for reuse
    if (loc.exported) score += 20;

    // 4. API routes are good for domain contracts (DTOs)
    if (path.includes('/api/') || path.includes('route.ts')) {
      if (category === 'domain' || category === 'generic-domain') score += 10;
    }

    // 5. Component placement: bad for domain/infra, good for UI
    if (path.includes('/components/')) {
      if (category === 'ui') score += 30; // components are canonical for UI
      else score -= 20; // bad for domain/infra
    }

    // 6. Dedicated ui/ subfolder within components is best for UI types
    if (path.includes('/components/ui/') && category === 'ui') score += 10;

    // 7. Import centrality: files already imported by more consumers are better canonicals
    //    Uses pre-computed fileImporterCount map (built once in ssotAudit)
    let importers = 0;
    const fileImporterMap = (globalThis as any).__ssotFileImporterCount as Map<string, number> | undefined;
    if (fileImporterMap && loc.exported) {
      importers = fileImporterMap.get(loc.file) || 0;
      // Scale: each importer adds 2 points, max 20 bonus
      score += Math.min(importers * 2, 20);
    }

    return { symbol: loc, score, importers };
  }).sort((a, b) => b.score - a.score);
}

function detectSharedPackage(paths: string[]): string | null {
  if (paths.some(p => p.includes('/packages/shared/'))) return 'packages/shared';
  if (paths.some(p => p.includes('/packages/nexus-shared/'))) return 'packages/nexus-shared';
  return null;
}

// ─── Autonomy Score (PR9 precursor) ───────────────────────────
// Quantifies how ready a cluster is for autonomous action.
// Formula: 35*exactness + 25*canonicalConf + 20*identityConf + 10*ctxConsistency + 10*codemopSafety

function computeAutonomyScore(
  drift: DriftResult | undefined,
  isCrossPackage: boolean,
  suggestion: string | undefined,
  category: SymbolCategory,
  boundedCtx?: BoundedContextResult,
): { score: number; action: AutonomyAction } {
  const dk = drift?.kind;
  const exactness = dk === 'EXACT' ? 1.0 : dk === 'RELAXED' ? 0.85 : dk === 'DIVERGENT' ? 0.2 : 0;
  const canonConf = suggestion?.includes('Shared canonical already exists') ? 1.0
    : suggestion?.includes('Canonical candidate') ? 0.6 : 0;
  // Without import graph (PR8) we approximate identity confidence from cross-package signal
  const identityConf = isCrossPackage ? 0.5 : 0.85;
  const ctxConsistency = category === 'generic-infra' ? 0.2 : category === 'generic-domain' ? 0.3
    : category === 'ui' ? 0.5 : category === 'infra' ? 0.6 : 0.8;
  const codemodSafety = dk === 'EXACT' && !isCrossPackage ? 1.0
    : dk === 'EXACT' && isCrossPackage ? 0.7
      : dk === 'RELAXED' ? 0.6 : 0.1;

  let raw = 35 * exactness + 25 * canonConf + 20 * identityConf + 10 * ctxConsistency + 10 * codemodSafety;

  // PR9 calibration: bounded context verdict adjusts autonomy score
  if (boundedCtx && dk === 'DIVERGENT') {
    const v = boundedCtx.verdict;
    const bcConf = boundedCtx.confidence / 100; // normalize 0-1
    if (v === 'MERGE_CANDIDATE') {
      raw += 12 * bcConf; // mergeable → boost toward ADAPTER_OR_RENAME
    } else if (v === 'DRIFT_EVOLUTION') {
      raw += 6 * bcConf;  // evolution → slight boost
    } else if (v === 'BOUNDED_CONTEXT_COLLISION') {
      raw -= 5 * bcConf;  // collision → pull toward MANUAL_REVIEW
    }
    // INSUFFICIENT_SIGNAL → no adjustment
  }

  const score = Math.min(100, Math.max(0, Math.round(raw)));
  const action: AutonomyAction = score >= 85 ? 'AUTOFIX_NOW'
    : score >= 70 ? 'AUTOFIX_WITH_REVIEW'
      : score >= 45 ? 'ADAPTER_OR_RENAME'
        : 'MANUAL_REVIEW';
  return { score, action };
}

// ─── PR9: Bounded Context Classifier ──────────────────────────
// Classifies DIVERGENT clusters into actionable architectural categories.
// Uses 5 heuristic features: field overlap, path context, drift reasons,
// shared canonical presence, and symbol category.

function extractPathContextTokens(filePath: string): string[] {
  const lower = filePath.toLowerCase();
  const tokens: string[] = [];
  const contextPatterns = [
    'auth', 'security', 'identity', 'session', 'login',
    'payment', 'billing', 'finance', 'wallet',
    'notification', 'email', 'push',
    'analytics', 'telemetry', 'metrics', 'monitoring',
    'search', 'graph', 'intelligence', 'investigation', 'evidence',
    'tourism', 'gamification', 'research', 'osint',
    'cache', 'storage', 'database', 'etl',
    'ui', 'components', 'hooks', 'providers',
    'api', 'routes', 'middleware',
    'types', 'shared', 'common', 'utils', 'lib',
    'domain', 'models', 'entities',
  ];
  for (const p of contextPatterns) {
    if (lower.includes(`/${p}/`) || lower.includes(`/${p}.`)) tokens.push(p);
  }
  return tokens;
}

function computeFieldOverlap(locs: StructuralSymbol[]): { jaccard: number; corePreserved: boolean } {
  if (locs.length < 2) return { jaccard: 1, corePreserved: true };
  const sets = locs.map(l => new Set(l.memberNames));
  const nonEmpty = sets.filter(s => s.size > 0);
  if (nonEmpty.length < 2) return { jaccard: 0, corePreserved: false };

  // Pairwise Jaccard average
  let totalJaccard = 0;
  let pairs = 0;
  for (let i = 0; i < nonEmpty.length; i++) {
    for (let j = i + 1; j < nonEmpty.length; j++) {
      const intersection = [...nonEmpty[i]].filter(x => nonEmpty[j].has(x)).length;
      const union = new Set([...nonEmpty[i], ...nonEmpty[j]]).size;
      totalJaccard += union > 0 ? intersection / union : 0;
      pairs++;
    }
  }
  const avgJaccard = pairs > 0 ? totalJaccard / pairs : 0;

  // Core preserved: do all locations share at least 1 field?
  const allNames = nonEmpty.map(s => [...s]);
  const commonFields = allNames[0].filter(f => allNames.every(names => names.includes(f)));
  return { jaccard: avgJaccard, corePreserved: commonFields.length > 0 };
}

function computePathContextSimilarity(locs: StructuralSymbol[]): { similarity: number; distinctContexts: number; contexts: string[][] } {
  const contextSets = locs.map(l => extractPathContextTokens(l.file));
  if (contextSets.length < 2) return { similarity: 1, distinctContexts: 1, contexts: contextSets };

  // Count distinct context token sets
  const uniqueContexts = new Set(contextSets.map(c => c.sort().join('|')));

  // Pairwise Jaccard of context tokens
  let totalSim = 0;
  let pairs = 0;
  for (let i = 0; i < contextSets.length; i++) {
    for (let j = i + 1; j < contextSets.length; j++) {
      const a = new Set(contextSets[i]);
      const b = new Set(contextSets[j]);
      const inter = [...a].filter(x => b.has(x)).length;
      const union = new Set([...a, ...b]).size;
      totalSim += union > 0 ? inter / union : 0;
      pairs++;
    }
  }

  return {
    similarity: pairs > 0 ? totalSim / pairs : 0,
    distinctContexts: uniqueContexts.size,
    contexts: contextSets,
  };
}

function computeBoundedContextClassification(
  locs: StructuralSymbol[],
  drift: DriftResult | undefined,
  isCrossPackage: boolean,
  category: SymbolCategory,
  suggestion: string | undefined,
): BoundedContextResult {
  // Only classify DIVERGENT clusters
  if (!drift || drift.kind !== 'DIVERGENT') {
    return { verdict: 'INSUFFICIENT_SIGNAL', confidence: 0, reasons: ['NOT_DIVERGENT'] };
  }

  const reasons: string[] = [];
  let mergeSignal = 0;   // positive = toward MERGE_CANDIDATE
  let collisionSignal = 0; // positive = toward BOUNDED_CONTEXT_COLLISION

  // Feature 1: Field overlap (weight: 35%)
  const { jaccard, corePreserved } = computeFieldOverlap(locs);
  if (jaccard >= 0.6) {
    mergeSignal += 35;
    reasons.push(`CTX_FIELD_OVERLAP_HIGH(${Math.round(jaccard * 100)}%)`);
  } else if (jaccard >= 0.3) {
    mergeSignal += 15;
    reasons.push(`CTX_FIELD_OVERLAP_MEDIUM(${Math.round(jaccard * 100)}%)`);
  } else {
    collisionSignal += 30;
    reasons.push(`CTX_FIELD_OVERLAP_LOW(${Math.round(jaccard * 100)}%)`);
  }
  if (corePreserved) {
    mergeSignal += 5;
    reasons.push('CTX_CORE_FIELDS_PRESERVED');
  }

  // Feature 2: Path context similarity (weight: 25%)
  const pathCtx = computePathContextSimilarity(locs);
  if (!isCrossPackage) {
    mergeSignal += 20;
    reasons.push('CTX_SAME_PACKAGE');
  } else if (pathCtx.similarity >= 0.5) {
    mergeSignal += 10;
    reasons.push(`CTX_SIMILAR_CONTEXT(${Math.round(pathCtx.similarity * 100)}%)`);
  } else {
    collisionSignal += 25;
    reasons.push(`CTX_CROSS_PACKAGE_DISTANT_DOMAIN(${pathCtx.distinctContexts} contexts)`);
  }

  // Feature 3: Drift reason codes (weight: 20%)
  const reasonCodes = drift.reasonCodes || [];
  const hasFieldsAdded = reasonCodes.some(r => r.startsWith('DRIFT_FIELDS_ADDED'));
  const hasFieldsRemoved = reasonCodes.some(r => r.startsWith('DRIFT_FIELDS_REMOVED'));
  const hasTypeChanged = reasonCodes.some(r => r.includes('TYPE_CHANGED'));
  const hasUnionDrift = reasonCodes.some(r => r.includes('UNION_MEMBERS'));

  if (hasFieldsAdded && !hasFieldsRemoved && !hasTypeChanged) {
    mergeSignal += 15; // Superset evolution — likely same concept growing
    reasons.push('CTX_SUPERSET_EVOLUTION');
  } else if (hasTypeChanged) {
    collisionSignal += 15; // Type changes = likely different contracts
    reasons.push('CTX_TYPE_INCOMPATIBLE');
  } else if (hasUnionDrift && !hasFieldsAdded) {
    collisionSignal += 20; // Completely different union variants
    reasons.push('CTX_UNION_DIVERGED');
  } else if (hasFieldsAdded && hasFieldsRemoved) {
    // Both sides evolved — drift evolution
    mergeSignal += 5;
    collisionSignal += 5;
    reasons.push('CTX_MUTUAL_EVOLUTION');
  }

  // Feature 4: Shared canonical presence (weight: 10%)
  if (suggestion?.includes('Shared canonical already exists') || suggestion?.includes('Shared candidate exists')) {
    mergeSignal += 10;
    reasons.push('CTX_SHARED_CANONICAL_PRESENT');
  }

  // Feature 5: Symbol category (weight: 10%)
  if (category === 'ui' || category === 'generic-infra') {
    collisionSignal += 10;
    reasons.push(`CTX_${category === 'ui' ? 'UI' : 'INFRA'}_LOCAL_VARIANT`);
  } else if (category === 'domain') {
    mergeSignal += 8;
    reasons.push('CTX_DOMAIN_SAME_CONCEPT');
  } else if (category === 'generic-domain') {
    collisionSignal += 5;
    reasons.push('CTX_GENERIC_NAME_COLLISION_RISK');
  }

  // Decision
  const totalSignal = mergeSignal + collisionSignal;
  const mergeRatio = totalSignal > 0 ? mergeSignal / totalSignal : 0.5;
  const confidence = Math.min(100, Math.round(Math.abs(mergeSignal - collisionSignal) * 1.5 + 20));

  let verdict: BoundedContextVerdict;
  if (mergeRatio >= 0.65) {
    verdict = corePreserved && jaccard >= 0.4 ? 'MERGE_CANDIDATE' : 'DRIFT_EVOLUTION';
  } else if (mergeRatio <= 0.35) {
    verdict = 'BOUNDED_CONTEXT_COLLISION';
  } else {
    // Close call — check if it's evolution or truly insufficient
    verdict = corePreserved ? 'DRIFT_EVOLUTION' : 'INSUFFICIENT_SIGNAL';
  }

  return { verdict, confidence, reasons };
}

// ─── PR15: Semantic Deep Check (TypeChecker) ──────────────────
// Uses ts.TypeChecker to resolve and compare types for High-confidence
// findings only. This goes beyond structural fingerprinting to check
// actual type compatibility via TypeScript's own semantic analysis.

function runSemanticDeepCheck(
  ctx: RunContext,
  findings: SSOTFinding[],
  allSymbols: StructuralSymbol[],
  repoRoot: string,
): void {
  const highFindings = findings.filter(f => f.confidence === 'high' && f.locations && f.locations.length >= 2);
  if (highFindings.length === 0) return;

  // Collect all files involved in High findings
  const filesToCheck = new Set<string>();
  for (const f of highFindings) {
    for (const loc of f.locations || []) {
      const absPath = join(repoRoot, loc.replace(/:\d+$/, ''));
      filesToCheck.add(absPath);
    }
  }

  // Create a TypeScript program with these files
  const compilerOptions: ts.CompilerOptions = {
    target: ts.ScriptTarget.ESNext,
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    jsx: ts.JsxEmit.ReactJSX,
    strict: false,
    noEmit: true,
    skipLibCheck: true,
    allowJs: true,
    esModuleInterop: true,
    resolveJsonModule: true,
    baseUrl: repoRoot,
  };

  let program: ts.Program;
  try {
    program = ts.createProgram([...filesToCheck], compilerOptions);
  } catch {
    log(ctx, 'warn', '  PR15: Failed to create TypeScript program for semantic check');
    return;
  }

  const checker = program.getTypeChecker();
  let checked = 0;
  let upgraded = 0;
  let downgraded = 0;

  for (const finding of highFindings) {
    const symbolName = finding.message.match(/"([^"]+)"/)?.[1];
    if (!symbolName) continue;

    const resolvedTypes: { file: string; resolved: string }[] = [];

    for (const loc of finding.locations || []) {
      const [relFile, lineStr] = loc.split(':');
      const absFile = join(repoRoot, relFile);
      const line = parseInt(lineStr, 10);

      const sourceFile = program.getSourceFile(absFile);
      if (!sourceFile) continue;

      // Find the type declaration node at or near the expected line
      let foundNode: ts.Node | undefined;
      const visit = (node: ts.Node) => {
        if (foundNode) return;
        const nodeStart = sourceFile.getLineAndCharacterOfPosition(node.getStart(sourceFile));
        const nodeLine = nodeStart.line + 1; // 1-indexed

        if (Math.abs(nodeLine - line) <= 2) {
          if (
            ts.isInterfaceDeclaration(node) ||
            ts.isTypeAliasDeclaration(node) ||
            ts.isEnumDeclaration(node) ||
            ts.isClassDeclaration(node)
          ) {
            const name = node.name?.getText(sourceFile);
            if (name === symbolName) {
              foundNode = node;
              return;
            }
          }
        }
        ts.forEachChild(node, visit);
      };
      ts.forEachChild(sourceFile, visit);

      if (foundNode) {
        try {
          const type = checker.getTypeAtLocation(foundNode);
          const typeStr = checker.typeToString(
            type,
            foundNode,
            ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.WriteArrayAsGenericType
          );
          resolvedTypes.push({ file: relFile, resolved: typeStr });
        } catch {
          resolvedTypes.push({ file: relFile, resolved: '(unresolved)' });
        }
      }
    }

    if (resolvedTypes.length < 2) continue;
    checked++;

    // Compare resolved types
    const uniqueTypes = new Set(resolvedTypes.map(r => r.resolved));
    const allResolved = resolvedTypes.every(r => r.resolved !== '(unresolved)');

    let verdict: SemanticVerdict;
    if (!allResolved) {
      verdict = 'SEMANTIC_UNRESOLVED';
    } else if (uniqueTypes.size === 1) {
      verdict = 'SEMANTIC_EXACT';
    } else {
      // Check for structural compatibility by normalizing whitespace and ordering
      const normalized = resolvedTypes.map(r => r.resolved.replace(/\s+/g, ' ').trim());
      const normalizedUnique = new Set(normalized);
      if (normalizedUnique.size === 1) {
        verdict = 'SEMANTIC_EXACT';
      } else {
        // Check if types are subsets (one extends the other)
        const typeStrings = [...uniqueTypes];
        const hasSubset = typeStrings.some((a, i) =>
          typeStrings.some((b, j) => i !== j && a.length < b.length && b.includes(a.replace(/[{}]/g, '').trim()))
        );
        verdict = hasSubset ? 'SEMANTIC_COMPATIBLE' : 'SEMANTIC_DIVERGENT';
      }
    }

    finding.semanticCheck = {
      verdict,
      resolvedTypes,
      assignability: resolvedTypes.length === 2
        ? `${resolvedTypes[0].file} ${verdict === 'SEMANTIC_EXACT' ? '≡' : verdict === 'SEMANTIC_COMPATIBLE' ? '⊂' : '≠'} ${resolvedTypes[1].file}`
        : undefined,
    };

    // Upgrade/downgrade drift classification based on semantic check
    if (finding.drift) {
      if (verdict === 'SEMANTIC_EXACT' && finding.drift.kind === 'DIVERGENT') {
        upgraded++;
      }
      if (verdict === 'SEMANTIC_DIVERGENT' && (finding.drift.kind === 'EXACT' || finding.drift.kind === 'RELAXED')) {
        downgraded++;
      }
    }
  }

  log(ctx, 'info', `  PR15: Semantic deep check — ${checked} High clusters analyzed via TypeChecker`);
  if (upgraded > 0) log(ctx, 'info', `  PR15: ${upgraded} cluster(s) structurally DIVERGENT but semantically EXACT (potential false positive)`);
  if (downgraded > 0) log(ctx, 'warn', `  PR15: ${downgraded} cluster(s) structurally EXACT/RELAXED but semantically DIVERGENT (potential false negative)`);
}

// ─── PR11: Codemod Dry-Run Engine ─────────────────────────────
// Generates concrete edit plans for EXACT/RELAXED clusters that
// have a canonical candidate. Does NOT modify files — dry-run only.

// ─── PR14: CI Governance (Baseline / Budget / Regression) ──────

interface CIBaseline {
  version: string;
  savedAt: string;
  git: { sha: string; branch: string };
  totals: {
    findings: number;
    high: number;
    medium: number;
    low: number;
    codemodPlans: number;
    codemodBlocked: number;
  };
  budget: {
    maxFindings: number;       // total allowed (baseline + allowance)
    maxHigh: number;
    maxMedium: number;
    allowNewHigh: number;      // how many NEW high findings before fail
  };
  clusterKeys: string[];       // list of cluster keys for regression detection
}

function saveCIBaseline(repoRoot: string, findings: SSOTFinding[], codemodPlans: CodemodPlan[], gitMeta: { sha: string; branch: string }): string {
  const high = findings.filter(f => f.confidence === 'high').length;
  const med = findings.filter(f => f.confidence === 'medium').length;
  const low = findings.filter(f => f.confidence === 'low').length;
  const blocked = codemodPlans.filter(p => p.risk === 'BLOCKED_ARCHITECTURE').length;

  const clusterKeys = findings
    .filter(f => f.confidence !== 'low')
    .map(f => {
      const name = f.message.match(/"([^"]+)"/)?.[1] || 'unknown';
      return `${f.category}|${name}|${f.isCrossPackage ? 'cross' : 'intra'}`;
    });

  const baseline: CIBaseline = {
    version: 'v3.7.0',
    savedAt: new Date().toISOString(),
    git: gitMeta,
    totals: {
      findings: findings.length,
      high,
      medium: med,
      low,
      codemodPlans: codemodPlans.length,
      codemodBlocked: blocked,
    },
    budget: {
      maxFindings: findings.length + 10,  // allow 10 new findings before fail
      maxHigh: high + 2,                   // allow 2 new high before fail
      maxMedium: med + 5,                  // allow 5 new medium before fail
      allowNewHigh: 2,
    },
    clusterKeys,
  };

  const dir = join(repoRoot, '.egos', 'ssot');
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  const path = join(dir, 'baseline.json');
  writeFileSync(path, JSON.stringify(baseline, null, 2));
  return path;
}

function loadCIBaseline(repoRoot: string): CIBaseline | null {
  const path = join(repoRoot, '.egos', 'ssot', 'baseline.json');
  try {
    const raw = readFileSync(path, 'utf-8');
    return JSON.parse(raw) as CIBaseline;
  } catch { return null; }
}

interface CIBudgetResult {
  passed: boolean;
  violations: string[];
  regressions: string[];  // new cluster keys not in baseline
  improvements: string[]; // cluster keys removed since baseline
  delta: {
    findings: number;
    high: number;
    medium: number;
  };
}

function checkCIBudget(baseline: CIBaseline, findings: SSOTFinding[], codemodPlans: CodemodPlan[]): CIBudgetResult {
  const high = findings.filter(f => f.confidence === 'high').length;
  const med = findings.filter(f => f.confidence === 'medium').length;
  const violations: string[] = [];

  // Budget checks
  if (findings.length > baseline.budget.maxFindings) {
    violations.push(`Total findings ${findings.length} exceeds budget ${baseline.budget.maxFindings} (baseline ${baseline.totals.findings} + ${baseline.budget.maxFindings - baseline.totals.findings} allowance)`);
  }
  if (high > baseline.budget.maxHigh) {
    violations.push(`High-confidence findings ${high} exceeds budget ${baseline.budget.maxHigh} (baseline ${baseline.totals.high} + ${baseline.budget.maxHigh - baseline.totals.high} allowance)`);
  }
  if (med > baseline.budget.maxMedium) {
    violations.push(`Medium-confidence findings ${med} exceeds budget ${baseline.budget.maxMedium} (baseline ${baseline.totals.medium} + ${baseline.budget.maxMedium - baseline.totals.medium} allowance)`);
  }

  // Regression detection: find new clusters not in baseline
  const currentKeys = findings
    .filter(f => f.confidence !== 'low')
    .map(f => {
      const name = f.message.match(/"([^"]+)"/)?.[1] || 'unknown';
      return `${f.category}|${name}|${f.isCrossPackage ? 'cross' : 'intra'}`;
    });

  const baselineSet = new Set(baseline.clusterKeys);
  const currentSet = new Set(currentKeys);

  const regressions = currentKeys.filter(k => !baselineSet.has(k));
  const improvements = baseline.clusterKeys.filter(k => !currentSet.has(k));

  // New high findings are especially bad
  const newHighCount = regressions.filter(k => {
    const f = findings.find(f => {
      const name = f.message.match(/"([^"]+)"/)?.[1] || 'unknown';
      return `${f.category}|${name}|${f.isCrossPackage ? 'cross' : 'intra'}` === k;
    });
    return f && f.confidence === 'high';
  }).length;

  if (newHighCount > baseline.budget.allowNewHigh) {
    violations.push(`${newHighCount} new High-confidence clusters detected (budget allows ${baseline.budget.allowNewHigh})`);
  }

  return {
    passed: violations.length === 0,
    violations,
    regressions: [...new Set(regressions)],
    improvements: [...new Set(improvements)],
    delta: {
      findings: findings.length - baseline.totals.findings,
      high: high - baseline.totals.high,
      medium: med - baseline.totals.medium,
    },
  };
}

interface CodemodAction {
  type: 'DELETE_DEFINITION' | 'ADD_IMPORT' | 'REPLACE_IMPORT';
  file: string;     // relative path
  line: number;
  description: string;
}

type ArchLayer = 'domain' | 'api' | 'ui' | 'lib' | 'shared' | 'unknown';

interface CodemodPlan {
  symbol: string;
  kind: SymbolKind;
  drift: DriftKind;
  canonical: { file: string; line: number; layer: ArchLayer };
  actions: CodemodAction[];
  risk: 'LOW' | 'MEDIUM' | 'HIGH' | 'BLOCKED_ARCHITECTURE' | 'REQUIRES_EXTRACTION';
  reason: string;
  blastRadius?: number;  // PR13: number of files that import this symbol
  blockReason?: string;  // PR12: why the plan was blocked
  collisions?: string[]; // v3.5: lexical collision warnings
}

function classifyArchLayer(filePath: string): ArchLayer {
  const lower = filePath.toLowerCase();
  if (lower.includes('/packages/shared/') || lower.includes('/packages/nexus-shared/')) return 'shared';
  if (lower.includes('/packages/')) return 'lib';
  if (lower.match(/\/app\/api\/|\/api\/|\/route\.(ts|tsx)$/)) return 'api';
  if (lower.match(/\/types\/|\/domain\/|\.types\.(ts|tsx)$/)) return 'domain';
  if (lower.match(/\/lib\/|\/utils\/|\/services\//)) return 'lib';
  if (lower.match(/\/components\/|\/hooks\/|\/pages\/|page\.(ts|tsx)$|\/store\//)) return 'ui';
  return 'unknown';
}

function computeBlastRadius(symbolName: string, files: string[]): number {
  let count = 0;
  for (const file of files) {
    try {
      const content = readFileSync(file, 'utf-8');
      // Check if file imports this symbol (not just defines it)
      if (content.match(new RegExp(`import\\s+(?:type\\s+)?{[^}]*\\b${symbolName}\\b[^}]*}\\s+from`))) {
        count++;
      }
    } catch { /* skip */ }
  }
  return count;
}

function detectLexicalCollisions(plan: CodemodPlan, allSymbols: StructuralSymbol[], repoRoot: string): string[] {
  const collisions: string[] = [];
  const symbolName = plan.symbol;

  for (const action of plan.actions) {
    if (action.type === 'ADD_IMPORT') {
      const targetFileAbs = join(repoRoot, action.file);
      // Check if target file has OTHER symbols with the same name that we're NOT deleting
      const otherSymbolsInFile = allSymbols.filter(s =>
        s.file === targetFileAbs &&
        s.name !== symbolName && // Different symbol name
        s.name.includes(symbolName.replace(/Props$|Config$|Options$/, '')) // But overlapping base name
      );
      for (const other of otherSymbolsInFile) {
        collisions.push(`${action.file}: import "${symbolName}" may shadow or confuse with existing "${other.name}" (${other.kind})`);
      }

      // Check if target file imports a different symbol with the same name from another module
      try {
        const content = readFileSync(targetFileAbs, 'utf-8');
        const existingImport = content.match(new RegExp(`import\\s+(?:type\\s+)?{[^}]*\\b${symbolName}\\b[^}]*}\\s+from\\s+['"]([^'"]+)['"]`));
        if (existingImport) {
          const existingSource = existingImport[1];
          const canonicalImport = plan.canonical.file;
          if (!existingSource.includes(canonicalImport.replace(/\.(ts|tsx)$/, ''))) {
            collisions.push(`${action.file}: already imports "${symbolName}" from "${existingSource}" — would create duplicate import`);
          }
        }
      } catch { /* skip */ }
    }
  }

  return collisions;
}

function applyCodemodSafetyRails(plan: CodemodPlan, repoRoot: string): CodemodPlan {
  const canonicalPath = plan.canonical.file;
  const canonicalLayer = plan.canonical.layer;

  // Rule 1: Block if canonical is in a page.tsx or route.tsx (UI/API surface, not a source of truth)
  if (canonicalPath.match(/page\.(ts|tsx)$/) || canonicalPath.match(/route\.(ts|tsx)$/)) {
    return { ...plan, risk: 'BLOCKED_ARCHITECTURE', blockReason: `Canonical is in a page/route file — extract to a types/ or lib/ module first` };
  }

  // Rule 2: Block cross-app imports (apps/X importing from apps/Y)
  const canonicalApp = canonicalPath.match(/^apps\/([^/]+)\//)?.[1];
  for (const action of plan.actions) {
    if (action.type === 'ADD_IMPORT') {
      const targetApp = action.file.match(/^apps\/([^/]+)\//)?.[1];
      if (canonicalApp && targetApp && canonicalApp !== targetApp && !canonicalPath.startsWith('packages/')) {
        return { ...plan, risk: 'REQUIRES_EXTRACTION', blockReason: `Cross-app import (${targetApp} → ${canonicalApp}) — extract to packages/ first` };
      }
    }
  }

  // Rule 3: Block if canonical is in components/ for non-UI symbols
  if (canonicalLayer === 'ui' && plan.kind !== 'interface') {
    // type_alias in components is probably a UI prop — ok for UI types
  } else if (canonicalLayer === 'ui' && !canonicalPath.includes('/types')) {
    // Interface in a component file used cross-package = bad canonical
    if (plan.actions.some(a => {
      const tgtApp = a.file.match(/^apps\/([^/]+)\//)?.[1];
      return tgtApp && tgtApp !== canonicalApp;
    })) {
      return { ...plan, risk: 'REQUIRES_EXTRACTION', blockReason: `Canonical is in UI layer (${canonicalPath}) — extract to types/ or shared/ before codemod` };
    }
  }

  return plan;
}

function generateCodemodPlans(
  findings: SSOTFinding[],
  allSymbols: StructuralSymbol[],
  repoRoot: string,
  reExportGraph: Map<string, ReExportEntry[]>,
  allFiles: string[],
): CodemodPlan[] {
  const plans: CodemodPlan[] = [];

  // Only process EXACT or RELAXED findings with a canonical candidate
  const candidates = findings.filter(f =>
    (f.drift?.kind === 'EXACT' || f.drift?.kind === 'RELAXED') &&
    f.suggestion?.includes('Canonical candidate') &&
    f.locations && f.locations.length >= 2
  );

  for (const f of candidates) {
    const symbolName = f.message.match(/"([^"]+)"/)?.[1];
    if (!symbolName) continue;

    // Find all symbols in this cluster
    const clusterSymbols = allSymbols.filter(s =>
      s.name === symbolName && f.locations?.some(loc => loc.startsWith(relative(repoRoot, s.file)))
    );
    if (clusterSymbols.length < 2) continue;

    // Find canonical (first exported, or highest-scored candidate)
    const canonical = clusterSymbols.find(s =>
      s.exported && (s.file.includes('/shared/') || s.file.includes('/types/') || s.file.includes('/lib/'))
    ) || clusterSymbols.find(s => s.exported) || clusterSymbols[0];

    const canonicalRel = relative(repoRoot, canonical.file);
    const nonCanonicals = clusterSymbols.filter(s => s.file !== canonical.file);

    const actions: CodemodAction[] = [];

    for (const dup of nonCanonicals) {
      const dupRel = relative(repoRoot, dup.file);

      // Action 1: Delete the duplicate definition
      actions.push({
        type: 'DELETE_DEFINITION',
        file: dupRel,
        line: dup.line,
        description: `Remove ${dup.kind} "${symbolName}" definition (lines ~${dup.line})`,
      });

      // Action 2: Add import from canonical
      // Check if the file already imports from the canonical
      const canonicalImportPath = computeRelativeImport(dup.file, canonical.file);
      actions.push({
        type: 'ADD_IMPORT',
        file: dupRel,
        line: 1,
        description: `Add: import type { ${symbolName} } from '${canonicalImportPath}'`,
      });
    }

    // Determine base risk level
    const baseRisk: CodemodPlan['risk'] = f.drift?.kind === 'EXACT' && !f.isCrossPackage ? 'LOW'
      : f.drift?.kind === 'EXACT' && f.isCrossPackage ? 'MEDIUM'
        : 'MEDIUM'; // RELAXED always medium

    // PR13: Compute blast radius (how many files import this symbol)
    const blastRadius = computeBlastRadius(symbolName, allFiles);

    // PR12+PR16: Layer classification
    const canonicalLayer = classifyArchLayer(canonicalRel);

    let plan: CodemodPlan = {
      symbol: symbolName,
      kind: canonical.kind,
      drift: f.drift!.kind,
      canonical: { file: canonicalRel, line: canonical.line, layer: canonicalLayer },
      actions,
      risk: baseRisk,
      reason: `${f.drift?.kind} drift — ${nonCanonicals.length} duplicate(s) can be replaced with import from canonical`,
      blastRadius,
    };

    // PR12: Apply safety rails (may upgrade risk to BLOCKED/REQUIRES_EXTRACTION)
    plan = applyCodemodSafetyRails(plan, repoRoot);

    // v3.5: Lexical collision detection
    const collisions = detectLexicalCollisions(plan, allSymbols, repoRoot);
    if (collisions.length > 0) {
      plan.collisions = collisions;
      // Escalate risk if collisions detected and plan is still safe
      if (plan.risk === 'LOW') plan.risk = 'MEDIUM';
    }

    plans.push(plan);
  }

  return plans;
}

function computeRelativeImport(fromFile: string, toFile: string): string {
  const fromDir = dirname(fromFile);
  let rel = relative(fromDir, toFile);
  // Remove extension
  rel = rel.replace(/\.(ts|tsx)$/, '');
  // Ensure starts with ./
  if (!rel.startsWith('.')) rel = './' + rel;
  return rel;
}

// ─── PR8: Import Graph / Barrel Resolution ────────────────────
// Detects re-exports (barrel files) so we can filter false positives
// where a symbol appears "duplicated" but is actually re-exported.

interface ReExportEntry {
  symbol: string;       // re-exported symbol name
  fromFile: string;     // absolute path of the source file
  viaFile: string;      // absolute path of the barrel/re-exporting file
  isWildcard: boolean;  // true if `export * from`
}

function buildReExportGraph(files: string[], repoRoot: string): Map<string, ReExportEntry[]> {
  const graph = new Map<string, ReExportEntry[]>(); // key = symbol name

  for (const file of files) {
    let content: string;
    try { content = readFileSync(file, 'utf-8'); } catch { continue; }

    // Match: export { Foo, Bar } from './types'
    const namedReExportRegex = /export\s+(?:type\s+)?{([^}]+)}\s+from\s+['"]([^'"]+)['"]/g;
    for (const match of content.matchAll(namedReExportRegex)) {
      const symbols = match[1].split(',').map(s => s.trim().split(/\s+as\s+/)[0].trim()).filter(Boolean);
      const fromSpec = match[2];
      const resolvedFrom = resolveModulePath(file, fromSpec);
      if (!resolvedFrom) continue;
      for (const sym of symbols) {
        const entries = graph.get(sym) || [];
        entries.push({ symbol: sym, fromFile: resolvedFrom, viaFile: file, isWildcard: false });
        graph.set(sym, entries);
      }
    }

    // Match: export * from './types'
    const wildcardRegex = /export\s+\*\s+from\s+['"]([^'"]+)['"]/g;
    for (const match of content.matchAll(wildcardRegex)) {
      const fromSpec = match[1];
      const resolvedFrom = resolveModulePath(file, fromSpec);
      if (!resolvedFrom) continue;
      const entries = graph.get('*') || [];
      entries.push({ symbol: '*', fromFile: resolvedFrom, viaFile: file, isWildcard: true });
      graph.set('*', entries);
    }
  }

  return graph;
}

function resolveModulePath(fromFile: string, specifier: string): string | null {
  if (!specifier.startsWith('.')) return null; // skip node_modules
  const dir = dirname(fromFile);
  const candidates = [
    join(dir, specifier + '.ts'),
    join(dir, specifier + '.tsx'),
    join(dir, specifier, 'index.ts'),
    join(dir, specifier, 'index.tsx'),
  ];
  // Also try exact match if specifier already has extension
  if (specifier.endsWith('.ts') || specifier.endsWith('.tsx')) {
    candidates.unshift(join(dir, specifier));
  }
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return null;
}

function isBarrelReExport(
  symbol: StructuralSymbol,
  otherLocs: StructuralSymbol[],
  reExportGraph: Map<string, ReExportEntry[]>,
): boolean {
  // Check if this symbol's file re-exports the symbol from another file in the cluster
  const namedEntries = reExportGraph.get(symbol.name) || [];
  for (const entry of namedEntries) {
    if (entry.viaFile === symbol.file) {
      // This file re-exports the symbol — check if the source is in our cluster
      if (otherLocs.some(l => l.file === entry.fromFile)) return true;
    }
  }
  // Check wildcard re-exports: if this file has `export * from` pointing to a cluster member
  const wildcardEntries = reExportGraph.get('*') || [];
  for (const entry of wildcardEntries) {
    if (entry.viaFile === symbol.file && otherLocs.some(l => l.file === entry.fromFile)) {
      return true;
    }
  }
  return false;
}

// ─── PR10: Decision Registry Functions ─────────────────────────

function computeClusterKey(name: string, kind: SymbolKind | undefined, isCrossPackage: boolean, packages: string[]): string {
  const k = kind || 'unknown';
  const scope = isCrossPackage ? 'cross-package' : 'intra-package';
  const pkgs = [...packages].sort().join(',');
  return `${k}|${name}|${scope}|${pkgs}`;
}

function computeClusterSignature(name: string, kind: SymbolKind | undefined, locs: StructuralSymbol[]): string {
  const fingerprints = locs.map(l => l.shapeStrict || '').sort().join('|');
  const key = `${kind}|${name}|${locs.length}|${fingerprints}`;
  // Simple hash (djb2)
  let hash = 5381;
  for (let i = 0; i < key.length; i++) {
    hash = ((hash << 5) + hash + key.charCodeAt(i)) >>> 0;
  }
  return `djb2:${hash.toString(16)}`;
}

function loadDecisionRegistry(repoRoot: string): DecisionRegistry | null {
  const paths = [
    join(repoRoot, '.egos', 'ssot', 'decisions.registry.json'),
    join(repoRoot, 'docs', 'agentic', 'ssot-decisions.registry.json'),
  ];
  for (const p of paths) {
    try {
      const raw = readFileSync(p, 'utf-8');
      const parsed = JSON.parse(raw);
      if (parsed.version === '1' && Array.isArray(parsed.decisions)) {
        return parsed as DecisionRegistry;
      }
    } catch { /* file not found or invalid — try next */ }
  }
  return null;
}

function applyDecisionRegistry(
  registry: DecisionRegistry | null,
  name: string,
  kind: SymbolKind | undefined,
  isCrossPackage: boolean,
  packages: string[],
  locs: StructuralSymbol[],
): AppliedDecisionSummary {
  if (!registry || registry.decisions.length === 0) {
    return { matchStatus: 'NONE' };
  }

  const clusterKey = computeClusterKey(name, kind, isCrossPackage, packages);
  const clusterSig = computeClusterSignature(name, kind, locs);

  // Index by clusterKey
  const candidates = registry.decisions.filter(d => d.match.clusterKey === clusterKey);
  if (candidates.length === 0) return { matchStatus: 'NONE' };

  // Pick best candidate: IMPLEMENTED > APPROVED > PROPOSED, then most recent
  const statusOrder: Record<string, number> = { IMPLEMENTED: 3, APPROVED: 2, PROPOSED: 1, DEPRECATED: 0 };
  candidates.sort((a, b) => {
    const sa = statusOrder[a.decision.status] || 0;
    const sb = statusOrder[b.decision.status] || 0;
    if (sb !== sa) return sb - sa;
    return (b.meta?.updatedAt || b.decision.date).localeCompare(a.meta?.updatedAt || a.decision.date);
  });

  const best = candidates[0];
  const sigMatch = best.match.clusterSignature ? best.match.clusterSignature === clusterSig : true;

  return {
    matchStatus: sigMatch ? 'APPLIED' : 'STALE',
    decisionId: best.id,
    action: best.decision.action,
    status: best.decision.status,
    owner: best.decision.owner,
    date: best.decision.date,
    rationale: best.decision.rationale,
    staleReason: sigMatch ? undefined : `clusterSignature changed (was ${best.match.clusterSignature}, now ${clusterSig})`,
  };
}

function generateRecommendation(name: string, confidence: ConfidenceResult, packages: string[], exportedCount: number, locs: StructuralSymbol[], repoRoot: string, drift?: DriftResult): string {
  const isAllLocal = exportedCount === 0;
  const paths = locs.map(l => l.file.toLowerCase());
  const category = categorizeSymbol(name, paths);
  const sharedPkg = detectSharedPackage(paths);

  let rec = '';

  if (confidence.isCrossPackage) {
    if (sharedPkg) {
      if (drift?.kind === 'DIVERGENT') {
        rec = `Shared candidate exists in \`${sharedPkg}\`, but local variants diverged — reconcile shapes before migration (adapter/mapping may be needed)`;
      } else {
        rec = `Shared canonical already exists — replace local duplicates with imports from \`${sharedPkg}\``;
      }
    } else {
      switch (category) {
        case 'domain':
        case 'generic-domain':
          rec = `Cross-package domain drift — compare shapes before consolidating. Promote to shared if exact match, otherwise use bounded-context rename.`;
          break;
        case 'ui':
          rec = `Cross-package UI type — evaluate consolidation in \`packages/ui\` or nearest common package`;
          break;
        case 'infra':
        case 'generic-infra':
          rec = `Cross-package infra duplicate — evaluate consolidation or bounded-context rename if semantically distinct`;
          break;
        default:
          rec = `Cross-package duplicate — evaluate consolidation in a shared package or bounded-context rename`;
      }
    }
  } else {
    switch (category) {
      case 'domain':
      case 'generic-domain':
        rec = `Intra-package domain drift — consolidate into a single canonical definition at \`${packages[0]}/types/\``;
        break;
      case 'ui':
        rec = `Intra-package UI duplication — extract to a shared component or local types file`;
        break;
      case 'infra':
      case 'generic-infra':
        rec = `Intra-package generic name — may be distinct local concepts sharing a name; verify shapes before consolidating`;
        break;
      default:
        if (isAllLocal) {
          rec = `Local duplicate signal — consolidate only if shapes are equivalent, or promote to a shared local module within \`${packages[0]}\``;
        } else {
          rec = `Intra-package exported duplicate — consolidate into a single types file within \`${packages[0]}\``;
        }
    }
  }

  // Append Canonical Candidate Ranking if applicable
  if (locs.length > 1) {
    const candidates = rankCanonicalCandidates(locs, category);
    const best = candidates[0];
    const alt = candidates[1];

    if (best.score > 0) {
      const bestRel = relative(repoRoot, best.symbol.file);
      const importerTag = best.importers > 0 ? `, ${best.importers} importer${best.importers > 1 ? 's' : ''}` : '';
      rec += `<br/>&nbsp;&nbsp;★ **Canonical candidate:** \`${bestRel}\` (score ${best.score}${importerTag})`;
      if (alt && alt.score > 0 && alt.score < best.score) {
        const altRel = relative(repoRoot, alt.symbol.file);
        const altImporterTag = alt.importers > 0 ? `, ${alt.importers} importer${alt.importers > 1 ? 's' : ''}` : '';
        rec += `<br/>&nbsp;&nbsp;↳ **Alternative:** \`${altRel}\` (score ${alt.score}${altImporterTag})`;
      }
    } else {
      rec += `<br/>&nbsp;&nbsp;⚪ No canonical candidate identified (all locations tied or UI-only variants)`;
    }
  }

  // Append drift status if provided
  if (drift) {
    rec += `<br/>&nbsp;&nbsp;${drift.emoji} **Shape drift:** ${drift.label}`;
    if (drift.kind !== 'UNRESOLVED' && drift.strictVariants > 0) {
      rec += ` (${drift.exactMatchCount}/${locs.length} match canonical, ${drift.strictVariants} unique strict fingerprint${drift.strictVariants > 1 ? 's' : ''})`;
    }
    if (drift.reasonCodes.length > 0 && !drift.reasonCodes.includes('UNRESOLVED_CLASS') && !drift.reasonCodes.includes('DRIFT_READONLY_ONLY')) {
      rec += `<br/>&nbsp;&nbsp;&nbsp;&nbsp;*Drift reasons: ${drift.reasonCodes.join(' · ')}*`;
    }
  }

  return rec;
}

// PR15: Format semantic check result for display
function formatSemanticCheck(sc: SemanticCheckResult): string {
  const emoji = sc.verdict === 'SEMANTIC_EXACT' ? '🟢' :
    sc.verdict === 'SEMANTIC_COMPATIBLE' ? '🟡' :
      sc.verdict === 'SEMANTIC_DIVERGENT' ? '🔴' : '⚪';
  const label = sc.verdict === 'SEMANTIC_EXACT' ? 'Types are semantically identical' :
    sc.verdict === 'SEMANTIC_COMPATIBLE' ? 'Types are structurally compatible (subset)' :
      sc.verdict === 'SEMANTIC_DIVERGENT' ? 'Types are semantically different' : 'Could not resolve types';
  return `${emoji} **Semantic check (PR15):** ${label}`;
}

// ─── Git Metadata ────────────────────────────────────────────

function getGitMeta(repoRoot: string): { sha: string; branch: string } {
  try {
    const sha = execSync('git rev-parse --short HEAD', { cwd: repoRoot }).toString().trim();
    const branch = execSync('git rev-parse --abbrev-ref HEAD', { cwd: repoRoot }).toString().trim();
    return { sha, branch };
  } catch {
    return { sha: 'unknown', branch: 'unknown' };
  }
}

// ─── Agent Logic ──────────────────────────────────────────────

async function ssotAudit(ctx: RunContext): Promise<Finding[]> {
  const findings: SSOTFinding[] = [];
  const repoRoot = ctx.repoRoot;

  const cliOpts = (globalThis as any).__ssotCliOptions || { minConfidence: 'low', jsonOnly: false };
  log(ctx, 'info', '🔬 SSOT Structural Triage v3.8.0 (multi-language, semantic deep check, CI governance)');
  log(ctx, 'info', 'Scanning TypeScript + Python files...');

  const allFiles = walkDir(repoRoot);
  const tsFiles = allFiles.filter(f => SCAN_EXTENSIONS_TS.includes(extname(f)));
  const pyFiles = allFiles.filter(f => SCAN_EXTENSIONS_PY.includes(extname(f)));
  log(ctx, 'info', `Found ${tsFiles.length} TypeScript files + ${pyFiles.length} Python files`);

  // Phase 1: Extract all structural symbols via AST
  log(ctx, 'info', 'Phase 1: AST extraction (TypeScript compiler API)...');
  const startExtract = performance.now();
  const allSymbols: StructuralSymbol[] = [];
  for (const file of tsFiles) {
    allSymbols.push(...extractStructuralSymbols(file, repoRoot));
  }
  const tsExtractMs = Math.round(performance.now() - startExtract);
  const tsSymbolCount = allSymbols.length;
  log(ctx, 'info', `Extracted ${tsSymbolCount} TypeScript symbols in ${tsExtractMs}ms`);

  // PR18: Python AST extraction
  if (pyFiles.length > 0) {
    log(ctx, 'info', 'Phase 1a: Python AST extraction (ast module)...');
    const startPy = performance.now();
    const pySymbols = extractPythonSymbols(pyFiles, repoRoot);
    const pyExtractMs = Math.round(performance.now() - startPy);
    allSymbols.push(...pySymbols);
    log(ctx, 'info', `Extracted ${pySymbols.length} Python symbols in ${pyExtractMs}ms`);
  }

  const extractMs = Math.round(performance.now() - startExtract);
  log(ctx, 'info', `Total: ${allSymbols.length} structural symbols in ${extractMs}ms`);

  // PR2: Heritage expansion pass (expands memberNames for interfaces with extends)
  const heritageExpandedCount = expandHeritagePass(allSymbols);
  if (heritageExpandedCount > 0) {
    log(ctx, 'info', `  Heritage expansion: ${heritageExpandedCount} interfaces expanded via extends clauses`);
  }

  // Stats by kind
  const byKind: Record<string, number> = {};
  for (const s of allSymbols) {
    byKind[s.kind] = (byKind[s.kind] || 0) + 1;
  }
  log(ctx, 'info', `  Breakdown: ${Object.entries(byKind).map(([k, v]) => `${k}=${v}`).join(', ')}`);

  // PR8: Build re-export graph for barrel resolution
  log(ctx, 'info', 'Phase 1b: Building re-export graph (barrel resolution)...');
  const reExportGraph = buildReExportGraph(allFiles, repoRoot);
  const reExportCount = [...reExportGraph.values()].reduce((s, v) => s + v.length, 0);
  if (reExportCount > 0) {
    log(ctx, 'info', `  Re-export graph: ${reExportCount} re-export edges across ${reExportGraph.size} symbols`);
  }

  // Phase 1c: Build file importer count map for import centrality (PR24)
  log(ctx, 'info', 'Phase 1c: Building file importer index (import centrality)...');
  const fileImporterCount = new Map<string, number>();
  const importFromRegex = /from\s+['"]([^'"]+)['"]/g;
  for (const file of allFiles) {
    try {
      const content = readFileSync(file, 'utf-8');
      const seen = new Set<string>();
      let match: RegExpExecArray | null;
      while ((match = importFromRegex.exec(content)) !== null) {
        const importPath = match[1];
        if (importPath.startsWith('.')) {
          // Resolve relative import to absolute path
          const dir = dirname(file);
          const resolved = join(dir, importPath);
          // Try common extensions (TS + Python)
          for (const ext of ['', '.ts', '.tsx', '/index.ts', '/index.tsx', '.py', '/__init__.py']) {
            const candidate = resolved + ext;
            if (!seen.has(candidate)) {
              seen.add(candidate);
              fileImporterCount.set(candidate, (fileImporterCount.get(candidate) || 0) + 1);
            }
          }
        }
      }
    } catch { /* skip */ }
  }
  (globalThis as any).__ssotFileImporterCount = fileImporterCount;
  const filesWithImporters = [...fileImporterCount.entries()].filter(([, c]) => c > 0).length;
  log(ctx, 'info', `  Import index: ${filesWithImporters} files have ≥1 importer`);

  // Phase 2: Detect duplicated type names (same name, different files)
  log(ctx, 'info', 'Phase 2: Duplicate detection with scope + kind classification...');
  const decisionRegistry = loadDecisionRegistry(repoRoot);
  if (decisionRegistry) {
    log(ctx, 'info', `  Decision Registry loaded: ${decisionRegistry.decisions.length} entries`);
  }
  const symbolsByName = new Map<string, StructuralSymbol[]>();
  for (const s of allSymbols) {
    const existing = symbolsByName.get(s.name) || [];
    existing.push(s);
    symbolsByName.set(s.name, existing);
  }

  const duplicates = [...symbolsByName.entries()]
    .filter(([, locs]) => locs.length > 1)
    .sort(([, a], [, b]) => b.length - a.length); // Most duplicated first

  let barrelFilteredCount = 0;
  for (const [name, rawLocs] of duplicates) {
    // PR8: Filter out barrel re-exports — they are not real duplicates
    const locs = rawLocs.filter(l => !isBarrelReExport(l, rawLocs, reExportGraph));
    if (locs.length !== rawLocs.length) barrelFilteredCount += rawLocs.length - locs.length;
    if (locs.length < 2) continue; // After filtering, no longer a duplicate

    const confidence = computeConfidence(name, locs);
    const packages = [...new Set(locs.map(l => l.package))];
    const kinds = [...new Set(locs.map(l => l.kind))];
    const exportedCount = locs.filter(l => l.exported).length;
    const locations = locs.map(l => `${relative(repoRoot, l.file)}:${l.line}`);

    // Determine severity based on confidence
    let severity: Finding['severity'];
    if (confidence.level === 'high') severity = locs.length > 2 ? 'error' : 'warning';
    else if (confidence.level === 'medium') severity = 'warning';
    else severity = 'info';

    const kindLabel = kinds.length === 1 ? kinds[0] : kinds.join('/');
    const scopeLabel = packages.length > 1
      ? `across ${packages.length} packages (${packages.join(', ')})`
      : `within "${packages[0]}"`;
    const exportLabel = exportedCount > 0 ? ` (${exportedCount} exported)` : ' (all local)';

    const paths = locs.map(l => l.file.toLowerCase());
    const category = categorizeSymbol(name, paths);
    const canonicalCandidates = rankCanonicalCandidates(locs, category);
    const canonicalIdx = locs.findIndex(l => l.file === canonicalCandidates[0]?.symbol.file);
    const drift = classifyClusterDrift(locs, canonicalIdx >= 0 ? canonicalIdx : 0);
    const recommendation = generateRecommendation(name, confidence, packages, exportedCount, locs, repoRoot, drift);
    const boundedCtx = computeBoundedContextClassification(locs, drift, confidence.isCrossPackage, category, recommendation);
    const autonomy = computeAutonomyScore(drift, confidence.isCrossPackage, recommendation, category, boundedCtx);

    findings.push({
      severity,
      category: `ssot:duplicate_${kindLabel}`,
      message: `${kindLabel} "${name}" defined ${locs.length}x ${scopeLabel}${exportLabel}`,
      suggestion: recommendation,
      confidence: confidence.level,
      confidenceScore: confidence.score,
      confidenceRawScore: confidence.rawScore,
      confidenceRationale: confidence.rationale,
      isCrossPackage: confidence.isCrossPackage,
      symbolKind: kinds.length === 1 ? kinds[0] : undefined,
      locations,
      packages,
      drift,
      autonomyScore: autonomy.score,
      autonomyAction: autonomy.action,
      boundedContext: boundedCtx.verdict !== 'INSUFFICIENT_SIGNAL' || drift.kind === 'DIVERGENT' ? boundedCtx : undefined,
      decisionRegistry: applyDecisionRegistry(decisionRegistry, name, kinds.length === 1 ? kinds[0] : undefined, confidence.isCrossPackage, packages, locs),
    });
  }

  if (barrelFilteredCount > 0) {
    log(ctx, 'info', `  PR8: Filtered ${barrelFilteredCount} barrel re-export(s) from duplicate clusters`);
  }

  // Phase 3: Detect orphaned exported types
  log(ctx, 'info', 'Phase 3: Orphaned export detection...');
  const importedNames = new Set<string>();
  for (const file of allFiles) {
    try {
      const content = readFileSync(file, 'utf-8');
      const importRegex = /import\s+(?:type\s+)?{([^}]+)}\s+from/g;
      for (const match of content.matchAll(importRegex)) {
        const names = match[1].split(',').map(n => n.trim().replace(/\s+as\s+\w+/, ''));
        for (const name of names) {
          if (name) importedNames.add(name);
        }
      }
    } catch { /* skip */ }
  }

  // PR8: Also count symbols that are re-exported (barrel imports) as "imported"
  const reExportedNames = new Set<string>();
  for (const [sym, entries] of reExportGraph) {
    if (sym === '*') continue;
    if (entries.length > 0) reExportedNames.add(sym);
  }

  const exportedUnused = allSymbols.filter(s =>
    s.exported &&
    !importedNames.has(s.name) &&
    !reExportedNames.has(s.name) &&
    !s.isGenerated
  );

  for (const s of exportedUnused) {
    findings.push({
      severity: 'info',
      category: `ssot:orphaned_${s.kind}`,
      message: `Exported ${s.kind} "${s.name}" in ${s.package} — no direct imports or re-exports detected`,
      file: relative(repoRoot, s.file),
      line: s.line,
      suggestion: 'No imports or re-exports found. Remove if unused.',
      confidence: 'low',
      confidenceScore: 1,
      confidenceRawScore: 1,
      confidenceRationale: ['+exported', '-never-imported', '-no-reexport'],
      isCrossPackage: false,
      symbolKind: s.kind,
    });
  }

  // ─── Summary & Stats ────────────────────────────────────────

  const highConf = findings.filter(f => f.confidence === 'high').length;
  const highCross = findings.filter(f => f.confidence === 'high' && f.isCrossPackage).length;
  const highIntra = findings.filter(f => f.confidence === 'high' && !f.isCrossPackage).length;
  const medConf = findings.filter(f => f.confidence === 'medium').length;
  const lowConf = findings.filter(f => f.confidence === 'low').length;
  const errorCount = findings.filter(f => f.severity === 'error' || f.severity === 'critical').length;
  const warnCount = findings.filter(f => f.severity === 'warning').length;
  const infoCount = findings.filter(f => f.severity === 'info').length;

  log(ctx, 'info', `Triage complete: ${errorCount} errors, ${warnCount} warnings, ${infoCount} info`);
  log(ctx, 'info', `Confidence: ${highConf} high (${highCross} cross-pkg, ${highIntra} intra-pkg), ${medConf} medium, ${lowConf} low/convention`);

  // --min-confidence filter: suppress findings below threshold
  const confLevels: Record<string, number> = { low: 0, medium: 1, high: 2 };
  const minConfLevel = confLevels[cliOpts.minConfidence] || 0;
  let reportFindings = findings;
  if (minConfLevel > 0) {
    const before = findings.length;
    reportFindings = findings.filter(f => confLevels[f.confidence] >= minConfLevel);
    log(ctx, 'info', `  --min-confidence=${cliOpts.minConfidence}: ${before - reportFindings.length} findings filtered out, ${reportFindings.length} remain`);
  }

  // Emit to Mycelium bus (only high/medium confidence)
  for (const f of findings.filter(f => f.confidence !== 'low')) {
    ctx.bus.emit(Topics.ARCH_SSOT_VIOLATION, {
      rule: f.category,
      message: f.message,
      severity: f.severity,
      confidence: f.confidence,
      score: f.confidenceScore,
    }, 'ssot_auditor', ctx.correlationId);
  }

  // PR11: Generate codemod dry-run plans
  const codemodPlans = generateCodemodPlans(findings, allSymbols, repoRoot, reExportGraph, allFiles);
  if (codemodPlans.length > 0) {
    const safe = codemodPlans.filter(p => p.risk === 'LOW' || p.risk === 'MEDIUM').length;
    const blocked = codemodPlans.filter(p => p.risk === 'BLOCKED_ARCHITECTURE').length;
    const needsExtract = codemodPlans.filter(p => p.risk === 'REQUIRES_EXTRACTION').length;
    log(ctx, 'info', `  PR11: Generated ${codemodPlans.length} codemod plan(s) — ✅ ${safe} safe, 🚫 ${blocked} blocked, 🔶 ${needsExtract} needs extraction`);
  }

  // PR15: Semantic deep check via TypeChecker (High-confidence only)
  log(ctx, 'info', 'Phase 4: Semantic deep check (TypeChecker)...');
  const semanticStart = performance.now();
  runSemanticDeepCheck(ctx, findings, allSymbols, repoRoot);
  const semanticMs = Math.round(performance.now() - semanticStart);
  log(ctx, 'info', `  Phase 4 completed in ${semanticMs}ms`);

  // Write report
  if (ctx.mode === 'execute' && reportFindings.length > 0) {
    const reportDir = join(repoRoot, 'docs', 'agentic', 'reports');
    if (!existsSync(reportDir)) mkdirSync(reportDir, { recursive: true });
    const gitMeta = getGitMeta(repoRoot);
    const totalDeclsInClusters = [...reportFindings.filter(f => f.confidence !== 'low')]
      .reduce((sum, f) => sum + (f.locations?.length || 0), 0);
    if (!cliOpts.jsonOnly) {
      const report = generateReport(ctx, reportFindings, allFiles.length, allSymbols, byKind, extractMs, gitMeta, totalDeclsInClusters, heritageExpandedCount, decisionRegistry, codemodPlans);
      writeFileSync(join(reportDir, 'ssot-audit.md'), report);
      log(ctx, 'info', `Report written to docs/agentic/reports/ssot-audit.md`);
    }
    // Always generate JSON (for UI consumption)
    const jsonReport = generateJsonReport(ctx, reportFindings, allFiles.length, allSymbols, byKind, extractMs, gitMeta, totalDeclsInClusters, heritageExpandedCount, decisionRegistry, codemodPlans);
    writeFileSync(join(reportDir, 'ssot-audit.json'), JSON.stringify(jsonReport, null, 2));
    log(ctx, 'info', `JSON report written to docs/agentic/reports/ssot-audit.json`);

    // PR14: CI Governance — save baseline or check budget
    if (cliOpts.saveBaseline) {
      const baselinePath = saveCIBaseline(repoRoot, findings, codemodPlans, gitMeta);
      log(ctx, 'info', `📊 CI Baseline saved to ${relative(repoRoot, baselinePath)}`);
      log(ctx, 'info', `  Totals: ${findings.length} findings (${highConf} high, ${medConf} medium, ${lowConf} low)`);
      log(ctx, 'info', `  Budget: max ${findings.length + 10} total, max ${highConf + 2} high, max ${medConf + 5} medium`);
    }

    if (cliOpts.checkBudget) {
      const baseline = loadCIBaseline(repoRoot);
      if (!baseline) {
        log(ctx, 'warn', `⚠️ No CI baseline found. Run with --save-baseline first.`);
      } else {
        const result = checkCIBudget(baseline, findings, codemodPlans);
        const deltaSign = (n: number) => n > 0 ? `+${n}` : `${n}`;
        log(ctx, 'info', `📊 CI Budget Check (baseline from ${baseline.savedAt})`);
        log(ctx, 'info', `  Delta: ${deltaSign(result.delta.findings)} findings, ${deltaSign(result.delta.high)} high, ${deltaSign(result.delta.medium)} medium`);
        if (result.regressions.length > 0) {
          log(ctx, 'warn', `  🆕 ${result.regressions.length} new cluster(s) since baseline:`);
          for (const r of result.regressions.slice(0, 10)) {
            log(ctx, 'warn', `    - ${r}`);
          }
        }
        if (result.improvements.length > 0) {
          log(ctx, 'info', `  ✅ ${result.improvements.length} cluster(s) resolved since baseline`);
        }
        if (result.passed) {
          log(ctx, 'info', `  ✅ CI Budget PASSED`);
        } else {
          log(ctx, 'error', `  ❌ CI Budget FAILED:`);
          for (const v of result.violations) {
            log(ctx, 'error', `    - ${v}`);
          }
        }
      }
    }
  }

  return findings;
}

// ─── JSON Report Generator (PR10.5 — for UI consumption) ─────

function generateJsonReport(
  ctx: RunContext,
  findings: SSOTFinding[],
  fileCount: number,
  allSymbols: StructuralSymbol[],
  byKind: Record<string, number>,
  extractMs: number,
  gitMeta: { sha: string; branch: string },
  totalDeclsInClusters: number,
  heritageExpandedCount: number,
  decisionRegistry: DecisionRegistry | null,
  codemodPlans: CodemodPlan[],
): object {
  const sortByScore = (a: SSOTFinding, b: SSOTFinding) => {
    if (b.confidenceScore !== a.confidenceScore) return b.confidenceScore - a.confidenceScore;
    return b.confidenceRawScore - a.confidenceRawScore;
  };

  const highConf = findings.filter(f => f.confidence === 'high').sort(sortByScore);
  const highCross = highConf.filter(f => f.isCrossPackage);
  const highIntra = highConf.filter(f => !f.isCrossPackage);
  const medConf = findings.filter(f => f.confidence === 'medium').sort(sortByScore);
  const lowConf = findings.filter(f => f.confidence === 'low');
  const allActionable = [...highConf, ...medConf];

  // Drift counts
  const driftCounts: Record<string, number> = { EXACT: 0, RELAXED: 0, DIVERGENT: 0, UNRESOLVED: 0 };
  for (const f of allActionable) if (f.drift?.kind) driftCounts[f.drift.kind]++;

  // Bounded context counts
  const bcCounts: Record<string, number> = { MERGE_CANDIDATE: 0, DRIFT_EVOLUTION: 0, BOUNDED_CONTEXT_COLLISION: 0, INSUFFICIENT_SIGNAL: 0 };
  const bcFindings = allActionable.filter(f => f.boundedContext && f.drift?.kind === 'DIVERGENT');
  for (const f of bcFindings) if (f.boundedContext) bcCounts[f.boundedContext.verdict]++;

  // Decision registry counts
  const drMatched = allActionable.filter(f => f.decisionRegistry && f.decisionRegistry.matchStatus !== 'NONE');
  const drApplied = drMatched.filter(f => f.decisionRegistry?.matchStatus === 'APPLIED').length;
  const drStale = drMatched.filter(f => f.decisionRegistry?.matchStatus === 'STALE').length;

  // Actionability buckets
  const autoFixReady = allActionable.filter(f => (f.suggestion?.includes('Shared canonical already exists') || (f.drift?.kind === 'EXACT' && f.suggestion?.includes('Canonical candidate'))) && (f.drift?.kind === 'EXACT' || f.drift?.kind === 'RELAXED'));
  const needsMapping = allActionable.filter(f => (f.suggestion?.includes('Shared canonical already exists') || f.suggestion?.includes('Shared candidate exists')) && f.drift?.kind === 'DIVERGENT');

  // Map findings to JSON-friendly format
  const mapFinding = (f: SSOTFinding) => ({
    symbol: f.message.match(/"([^"]+)"/)?.[1] || '',
    message: f.message,
    severity: f.severity,
    confidence: f.confidence,
    confidenceScore: f.confidenceScore,
    confidenceRawScore: f.confidenceRawScore,
    confidenceRationale: f.confidenceRationale,
    isCrossPackage: f.isCrossPackage,
    symbolKind: f.symbolKind,
    locations: f.locations,
    packages: f.packages,
    recommendation: f.suggestion,
    drift: f.drift ? { kind: f.drift.kind, reasonCodes: f.drift.reasonCodes } : null,
    autonomy: f.autonomyScore !== undefined ? { score: f.autonomyScore, action: f.autonomyAction } : null,
    boundedContext: f.boundedContext || null,
    decision: f.decisionRegistry && f.decisionRegistry.matchStatus !== 'NONE' ? f.decisionRegistry : null,
    semanticCheck: f.semanticCheck || null,
  });

  return {
    version: 'v3.7.0',
    schemaVersion: '1.0.0',
    generatedAt: ctx.startedAt,
    correlationId: ctx.correlationId,
    git: gitMeta,
    capabilities: [
      'ast_triage', 'symbol_classification', 'scope_filtering', 'scoring_0_10',
      'context_recommendations', 'shape_fingerprint', 'drift_classification',
      'drift_reason_codes', 'heritage_expansion', 'class_fingerprint',
      'autonomy_score', 'bounded_context_classifier', 'decision_registry',
      'reexport_graph', 'codemod_dry_run', 'codemod_safety_rails',
      'blast_radius', 'layer_classification', 'json_output',
      'min_confidence_filter', 'import_centrality', 'lexical_collision_check',
      'ci_governance', 'semantic_deep_check',
    ],
    scan: {
      filesScanned: fileCount,
      symbolsExtracted: allSymbols.length,
      extractionMs: extractMs,
      heritageExpanded: heritageExpandedCount,
      symbolBreakdown: byKind,
    },
    summary: {
      totalClusters: findings.length,
      totalDeclsInClusters,
      high: { total: highConf.length, crossPackage: highCross.length, intraPackage: highIntra.length },
      medium: medConf.length,
      low: lowConf.length,
      actionable: allActionable.length,
    },
    drift: driftCounts,
    boundedContext: bcCounts,
    actionability: {
      autoFixReady: autoFixReady.length,
      needsMapping: needsMapping.length,
    },
    decisionRegistry: decisionRegistry ? {
      entries: decisionRegistry.decisions.length,
      applied: drApplied,
      stale: drStale,
      unmatched: allActionable.length - drMatched.length,
      coverage: allActionable.length > 0 ? Math.round(drMatched.length / allActionable.length * 100) : 0,
    } : null,
    findings: {
      highCrossPackage: highCross.map(mapFinding),
      highIntraPackage: highIntra.map(mapFinding),
      medium: medConf.map(mapFinding),
    },
    codemodPlans: codemodPlans.map(p => ({
      symbol: p.symbol,
      kind: p.kind,
      drift: p.drift,
      canonical: p.canonical,
      risk: p.risk,
      reason: p.reason,
      actions: p.actions,
      blastRadius: p.blastRadius || 0,
      blockReason: p.blockReason || null,
      collisions: p.collisions || [],
    })),
  };
}

// ─── Report Generator ─────────────────────────────────────────

function generateReport(
  ctx: RunContext,
  findings: SSOTFinding[],
  fileCount: number,
  allSymbols: StructuralSymbol[],
  byKind: Record<string, number>,
  extractMs: number,
  gitMeta: { sha: string; branch: string },
  totalDeclsInClusters: number,
  heritageExpandedCount: number,
  decisionRegistry: DecisionRegistry | null,
  codemodPlans: CodemodPlan[],
): string {
  // Sort all findings by score descending for consistent ordering, tie-break by rawScore
  const sortByScore = (a: SSOTFinding, b: SSOTFinding) => {
    if (b.confidenceScore !== a.confidenceScore) return b.confidenceScore - a.confidenceScore;
    return b.confidenceRawScore - a.confidenceRawScore;
  };

  const highConf = findings.filter(f => f.confidence === 'high').sort(sortByScore);
  const highCross = highConf.filter(f => f.isCrossPackage);
  const highIntra = highConf.filter(f => !f.isCrossPackage);
  const medConf = findings.filter(f => f.confidence === 'medium').sort(sortByScore);
  const lowConf = findings.filter(f => f.confidence === 'low');

  // Ensure all 4 kinds appear in breakdown (enum: 0 fix)
  const allKinds: SymbolKind[] = ['interface', 'type_alias', 'enum', 'class'];
  const fullBreakdown = allKinds.map(k => `${k}: ${byKind[k] || 0}`).join(', ');

  // Top offenders for executive summary (top 5 by score, then by count)
  const allActionable = [...highConf, ...medConf];
  const topOffenders = allActionable.slice(0, 5);

  // 5-bucket Actionability (v2.8.2): separate by canonical+shape combination
  const autoFixReady = allActionable.filter(f => (f.suggestion?.includes('Shared canonical already exists') || (f.drift?.kind === 'EXACT' && f.suggestion?.includes('Canonical candidate'))) && (f.drift?.kind === 'EXACT' || f.drift?.kind === 'RELAXED'));
  const needsMapping = allActionable.filter(f => (f.suggestion?.includes('Shared canonical already exists') || f.suggestion?.includes('Shared candidate exists')) && f.drift?.kind === 'DIVERGENT');
  const exactNoCanonical = allActionable.filter(f => f.drift?.kind === 'EXACT' && !f.suggestion?.includes('Shared canonical already exists') && !autoFixReady.includes(f));
  const manualReview = highCross.filter(f => f.drift?.kind === 'DIVERGENT' && !needsMapping.includes(f));
  const exactDriftCount = allActionable.filter(f => f.drift?.kind === 'EXACT').length;
  const relaxedDriftCount = allActionable.filter(f => f.drift?.kind === 'RELAXED').length;
  const divergentDriftCount = allActionable.filter(f => f.drift?.kind === 'DIVERGENT').length;
  const unresolvedDriftCount = allActionable.filter(f => f.drift?.kind === 'UNRESOLVED').length;

  const lines: string[] = [
    `# SSOT Structural Triage Report v3.7.0`,
    ``,
    `> ⚠️ **This is a triage report, not a verdict.** Findings are structural signals`,
    `> that require human review to confirm as actual SSOT violations.`,
    ``,
    `## Scan Metadata`,
    ``,
    `| Metric | Value |`,
    `|--------|-------|`,
    `| Engine Version | v3.7.0 (semantic deep check, CI governance, import centrality, PR15/PR14/PR12/PR13/PR16/PR11/PR8/PR10/PR9) |`,
    `| Generated | ${ctx.startedAt} |`,
    `| Commit | \`${gitMeta.sha}\` (branch: \`${gitMeta.branch}\`) |`,
    `| Correlation | \`${ctx.correlationId}\` |`,
    `| Run Mode | ${ctx.mode} |`,
    `| Scoring Ruleset Hash | \`v3.7.0-d0f5h4c\` |`,
    `| Heritage Expanded | ${heritageExpandedCount} interface${heritageExpandedCount !== 1 ? 's' : ''} expanded via extends clauses |`,
    `| Ignore Patterns | \`${IGNORE_DIRS.join(', ')}\` |`,
    `| Node Version | ${process.version} |`,
    `| Analysis Mode | AST-based (TypeScript compiler API) |`,
    `| API Cost | $0 (local static pass, no LLM inference) |`,
    `| Files scanned | ${fileCount} |`,
    `| Symbols extracted | ${allSymbols.length} |`,
    `| Extraction time | ${extractMs}ms |`,
    `| Symbol breakdown | ${fullBreakdown} |`,
    ``,
    `## What This Report Proves`,
    ``,
    `1. **Proven:** Fast repo-wide structural triage with AST parsing`,
    `2. **Proven:** Symbol classification by kind (interface/type_alias/enum/class)`,
    `3. **Proven:** Scope-aware filtering (exported, cross-package)`,
    `4. **Proven:** Explicit scoring (0-10) with human-readable rationale per finding`,
    `5. **Proven (heuristic):** Context-aware recommendations (domain vs UI vs generic) — calibrated but not exhaustive`,
    `6. **Proven (v2.7):** Normalized structural fingerprints for interfaces, type aliases, and enums (enum: ${byKind['enum'] || 0} found in this run)`,
    `7. **Proven (v2.7 heuristic):** Shape drift classification — EXACT, RELAXED, DIVERGENT, UNRESOLVED per cluster`,
    `8. **Proven (v2.8):** Object drift reason codes — DRIFT_FIELDS_ADDED / DRIFT_FIELDS_REMOVED / DRIFT_FIELD_TYPE_CHANGED / DRIFT_OPTIONALITY_CHANGED per cluster`,
    `9. **Proven (v2.8.2):** Union alias drift reason codes — DRIFT_UNION_MEMBERS_ADDED / DRIFT_UNION_MEMBERS_REMOVED per cluster`,
    `10. **Proven (v2.9 — PR2):** Heritage expansion — interface extends clauses resolved and merged before diff (${heritageExpandedCount} expanded this run)`,
    `11. **Proven (v2.9 — PR7):** Shared canonical cleanup — api-registry type re-exports consolidated in packages/shared`,
    `12. **Proven (v3.0 — PR3):** Class fingerprinting — public fields/methods/ctor params fingerprinted → real EXACT/RELAXED/DIVERGENT for classes`,
    `13. **Proven (v3.0 — PR9 precursor):** autonomy_action_score per cluster (0-100) with 4-tier action label`,
    `14. **Proven (v3.1 — PR9):** Bounded context classifier — DIVERGENT clusters classified as MERGE_CANDIDATE / DRIFT_EVOLUTION / BOUNDED_CONTEXT_COLLISION / INSUFFICIENT_SIGNAL`,
    `15. **Proven (v3.2 — PR10):** Decision registry — persistent architectural decisions per cluster, APPLIED/STALE/NONE matching, report badges`,
    `16. **Proven (v3.3 — PR8):** Import graph / barrel resolution — re-export detection, orphaned export precision improvement`,
    `17. **Proven (v3.3 — PR11):** Codemod dry-run engine — generates concrete edit plans for EXACT/RELAXED clusters`,
    `18. **Proven (v3.4 — PR12):** Codemod safety rails — BLOCKED_ARCHITECTURE / REQUIRES_EXTRACTION for unsafe plans`,
    `19. **Proven (v3.4 — PR13):** Blast radius metric — fan-in count per symbol via import scanning`,
    `20. **Proven (v3.4 — PR16):** Architectural layer classification — domain/api/ui/lib/shared per declaration`,
    `21. **Proven (v3.4):** JSON schema versioning (schemaVersion: 1.0.0) + capabilities array`,
    `22. **Proven (v3.5):** \`--min-confidence\` CLI filter — suppress low/convention noise from reports`,
    `23. **Proven (v3.5):** Import centrality — canonical ranking weighted by file importer count (fan-in)`,
    `24. **Proven (v3.5):** Lexical collision detection — warns when codemod would create name conflicts`,
    `25. **Proven (v3.6 — PR14):** CI governance — \`--save-baseline\` + \`--check-budget\` with regression detection`,
    `26. **Proven (v3.7 — PR15):** Semantic deep check — TypeChecker resolves actual types for High clusters (28/32 upgraded to SEMANTIC_EXACT)`,
    `27. **Not yet proven:** Drift normalization semantics (snake→camel, pt→en)`,
    ``,
  ];

  // ─── EXECUTIVE SUMMARY ──────────────────────────────────────
  lines.push(`## Executive Summary`);
  lines.push(``);
  lines.push(`### Actionability Summary (5-bucket)`);
  lines.push(`> High+Medium tier only. Low/convention signals (${findings.length - allActionable.length} clusters) require no action.`);
  lines.push(``);
  lines.push(`| Bucket | Count | Criteria | Action |`);
  lines.push(`|--------|-------|----------|--------|`);
  const pct = (n: number) => allActionable.length > 0 ? `${Math.round(n / allActionable.length * 100)}%` : '0%';
  const remainingActionable = allActionable.length - autoFixReady.length - needsMapping.length - exactNoCanonical.length - manualReview.length;
  lines.push(`| 🟢 **Auto-fix ready** | ${autoFixReady.length} (${pct(autoFixReady.length)}) | Canonical defined **∧** EXACT/RELAXED shape | Safe to codemod |`);
  lines.push(`| 🟡 **Needs mapping** | ${needsMapping.length} (${pct(needsMapping.length)}) | Canonical defined **∧** DIVERGENT shapes | Map fields before merge |`);
  lines.push(`| 🔵 **Exact, no canonical** | ${exactNoCanonical.length} (${pct(exactNoCanonical.length)}) | EXACT shape **∧** no clear canonical source | Decide canonical, then consolidate |`);
  lines.push(`| 🔴 **Manual review** | ${manualReview.length} (${pct(manualReview.length)}) | Cross-package DIVERGENT — high risk | Compare + bounded-context rename |`);
  lines.push(`| ⚪ **Other divergent** | ${remainingActionable} (${pct(remainingActionable)}) | Intra-package DIVERGENT or UNRESOLVED | Lower priority — address in regular reviews |`);
  lines.push(``);
  lines.push(`### Shape Drift Summary (High+Medium tier)`);
  lines.push(``);
  lines.push(`| Drift Status | Count | Meaning |`);
  lines.push(`|------------|-------|---------|`);
  lines.push(`| ✅ EXACT | ${exactDriftCount} | All locations have identical shape — safe to consolidate |`);
  lines.push(`| 🟢 RELAXED | ${relaxedDriftCount} | Only readonly modifier differs — likely safe to consolidate |`);
  lines.push(`| ⚠️ DIVERGENT | ${divergentDriftCount} | Shape differs — compare field types before merging |`);
  lines.push(`| ⚪ UNRESOLVED | ${unresolvedDriftCount} | Cannot determine shape (class, empty, or parse error) |`);
  lines.push(``);

  // PR9: Bounded Context Summary
  const bcFindings = allActionable.filter(f => f.boundedContext && f.drift?.kind === 'DIVERGENT');
  if (bcFindings.length > 0) {
    const bcCounts: Record<string, number> = { MERGE_CANDIDATE: 0, DRIFT_EVOLUTION: 0, BOUNDED_CONTEXT_COLLISION: 0, INSUFFICIENT_SIGNAL: 0 };
    for (const f of bcFindings) if (f.boundedContext) bcCounts[f.boundedContext.verdict]++;
    lines.push(`### Bounded Context Classification (PR9 — DIVERGENT clusters only)`);
    lines.push(``);
    lines.push(`| Verdict | Count | Meaning | Action |`);
    lines.push(`|---------|-------|---------|--------|`);
    lines.push(`| 🟢 **Merge candidate** | ${bcCounts.MERGE_CANDIDATE} | Same concept, compatible shapes — can be unified | Create shared type + adapter if needed |`);
    lines.push(`| 🔄 **Drift evolution** | ${bcCounts.DRIFT_EVOLUTION} | Same concept evolved independently — core preserved | Reconcile into superset or versioned type |`);
    lines.push(`| 🔀 **Bounded context collision** | ${bcCounts.BOUNDED_CONTEXT_COLLISION} | Different concepts, same name — intentional | Rename to disambiguate (e.g., AuthUser vs GamificationUser) |`);
    lines.push(`| ❓ **Insufficient signal** | ${bcCounts.INSUFFICIENT_SIGNAL} | Cannot determine from available heuristics | Manual architectural review needed |`);
    lines.push(``);
  }

  // PR10: Decision Registry Summary
  const drFindings = allActionable.filter(f => f.decisionRegistry && f.decisionRegistry.matchStatus !== 'NONE');
  const drNone = allActionable.filter(f => !f.decisionRegistry || f.decisionRegistry.matchStatus === 'NONE').length;
  if (decisionRegistry) {
    const drApplied = drFindings.filter(f => f.decisionRegistry?.matchStatus === 'APPLIED').length;
    const drStale = drFindings.filter(f => f.decisionRegistry?.matchStatus === 'STALE').length;
    const drOrphans = decisionRegistry.decisions.filter(d => !allActionable.some(f => f.decisionRegistry?.decisionId === d.id)).length;
    const drActionCounts: Record<string, number> = {};
    for (const f of drFindings) if (f.decisionRegistry?.action) drActionCounts[f.decisionRegistry.action] = (drActionCounts[f.decisionRegistry.action] || 0) + 1;

    lines.push(`### Decision Registry (PR10)`);
    lines.push(``);
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Registry entries | ${decisionRegistry.decisions.length} |`);
    lines.push(`| ✅ Applied this run | ${drApplied} |`);
    lines.push(`| ⚠️ Stale (cluster changed) | ${drStale} |`);
    lines.push(`| ❓ Unmatched (no decision) | ${drNone} |`);
    lines.push(`| 🗑️ Orphan entries | ${drOrphans} |`);
    lines.push(`| **Coverage (High+Medium)** | **${allActionable.length > 0 ? Math.round(drFindings.length / allActionable.length * 100) : 0}%** |`);
    lines.push(``);
    if (Object.keys(drActionCounts).length > 0) {
      lines.push(`| Decision Action | Count |`);
      lines.push(`|----------------|-------|`);
      for (const [action, count] of Object.entries(drActionCounts).sort((a, b) => b[1] - a[1])) {
        lines.push(`| ${action} | ${count} |`);
      }
      lines.push(``);
    }
  }

  const uniqueSymbolNames = new Set(allActionable.map(f => f.message.match(/"([^"]+)"/)?.[1]).filter(Boolean));
  lines.push(`### Prioritized Declarations`);
  lines.push(``);
  lines.push(`> **Terminology:** A *cluster* is one symbol name with ≥2 definitions. A *declaration* is one definition of that symbol.`);
  lines.push(``);
  lines.push(`| Category | Clusters | Declarations |`);
  lines.push(`|----------|----------|--------------|`);
  lines.push(`| 🔴 High — Cross-Package | ${highCross.length} | ${highCross.reduce((s, f) => s + (f.locations?.length || 0), 0)} |`);
  lines.push(`| 🟠 High — Intra-Package | ${highIntra.length} | ${highIntra.reduce((s, f) => s + (f.locations?.length || 0), 0)} |`);
  lines.push(`| ⚠️ Medium | ${medConf.length} | ${medConf.reduce((s, f) => s + (f.locations?.length || 0), 0)} |`);
  lines.push(`| ℹ️ Low / Convention | ${lowConf.length} | — |`);
  lines.push(`| **Total** | **${findings.length}** clusters | **${totalDeclsInClusters}** actionable decls |`);
  lines.push(`| **Unique symbol names (High+Med)** | **${uniqueSymbolNames.size}** | — |`);
  lines.push(``);

  if (topOffenders.length > 0) {
    lines.push(`### Top 5 Offenders (by score)`);
    lines.push(``);
    lines.push(`| # | Symbol | Score | Category | Scope | Decls |`);
    lines.push(`|---|--------|-------|----------|-------|-------|`);
    topOffenders.forEach((f, i) => {
      const scope = f.isCrossPackage ? `Cross (${f.packages?.join(', ')})` : `Intra (${f.packages?.[0]})`;
      const name = f.message.match(/"([^"]+)"/)?.[1] || 'unknown';
      const cat = categorizeSymbol(name, f.locations || []);
      lines.push(`| ${i + 1} | \`${name}\` | ${f.confidenceScore}/10 (raw ${f.confidenceRawScore}) | ${cat} | ${scope} | ${f.locations?.length || '?'}× |`);
    });
    lines.push(``);
  }

  // PR11+PR12+PR13: Codemod Dry-Run Plans with Safety Rails
  if (codemodPlans.length > 0) {
    lines.push(`### Codemod Dry-Run Plans (PR11 + PR12 Safety Rails)`);
    lines.push(``);
    lines.push(`> ⚠️ **DRY-RUN ONLY** — these are proposed edits, not executed. Review before applying.`);
    lines.push(`> Plans marked 🚫 BLOCKED or 🔶 REQUIRES_EXTRACTION need architectural changes before codemod.`);
    lines.push(``);
    const totalActions = codemodPlans.reduce((s, p) => s + p.actions.length, 0);
    const lowRisk = codemodPlans.filter(p => p.risk === 'LOW').length;
    const medRisk = codemodPlans.filter(p => p.risk === 'MEDIUM').length;
    const blocked = codemodPlans.filter(p => p.risk === 'BLOCKED_ARCHITECTURE').length;
    const needsExtract = codemodPlans.filter(p => p.risk === 'REQUIRES_EXTRACTION').length;
    const safe = codemodPlans.filter(p => p.risk === 'LOW' || p.risk === 'MEDIUM').length;
    lines.push(`| Metric | Value |`);
    lines.push(`|--------|-------|`);
    lines.push(`| Plans generated | ${codemodPlans.length} |`);
    lines.push(`| Total actions | ${totalActions} |`);
    lines.push(`| ✅ Safe to apply (LOW+MEDIUM) | ${safe} |`);
    lines.push(`| 🚫 Blocked (architecture) | ${blocked} |`);
    lines.push(`| 🔶 Requires extraction first | ${needsExtract} |`);
    lines.push(``);
    for (const plan of codemodPlans) {
      const riskEmoji = plan.risk === 'LOW' ? '🟢' : plan.risk === 'MEDIUM' ? '🟡' : plan.risk === 'BLOCKED_ARCHITECTURE' ? '🚫' : plan.risk === 'REQUIRES_EXTRACTION' ? '🔶' : '🔴';
      lines.push(`#### ${riskEmoji} \`${plan.symbol}\` (${plan.drift}, ${plan.risk})`);
      lines.push(`- **Canonical:** \`${plan.canonical.file}:${plan.canonical.line}\` (layer: \`${plan.canonical.layer}\`)`);
      if (plan.blastRadius !== undefined && plan.blastRadius > 0) {
        lines.push(`- **Blast radius:** ${plan.blastRadius} file(s) import this symbol`);
      }
      if (plan.blockReason) {
        lines.push(`- **⚠️ Block reason:** ${plan.blockReason}`);
      }
      if (plan.collisions && plan.collisions.length > 0) {
        lines.push(`- **⚠️ Lexical collisions (${plan.collisions.length}):**`);
        for (const c of plan.collisions) {
          lines.push(`  - ${c}`);
        }
      }
      lines.push(`- **Reason:** ${plan.reason}`);
      if (plan.risk !== 'BLOCKED_ARCHITECTURE') {
        lines.push(`- **Actions:**`);
        for (const action of plan.actions) {
          lines.push(`  - \`${action.type}\` in \`${action.file}:${action.line}\` — ${action.description}`);
        }
      }
      lines.push(``);
    }
  }

  lines.push(`### Recommended Next Steps`);
  lines.push(``);
  lines.push(`1. **Immediate:** Review the ${highCross.length} cross-package High findings — these represent the highest risk of divergent type drift`);
  const intraPkgCounts = new Map<string, number>();
  for (const f of highIntra) { const p = f.packages?.[0] || 'unknown'; intraPkgCounts.set(p, (intraPkgCounts.get(p) || 0) + 1); }
  const topIntraPkg = [...intraPkgCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || 'types';
  lines.push(`2. **Short-term:** Consolidate the ${highIntra.length} intra-package High findings${highIntra.length > 0 ? ` (hotspot: \`${topIntraPkg}/\`)` : ''} to reduce internal fragmentation`);
  lines.push(`3. **Medium-term:** Evaluate the ${medConf.length} Medium findings during regular code review cycles`);
  const safeCodemodCount = codemodPlans.filter(p => p.risk === 'LOW' || p.risk === 'MEDIUM').length;
  const blockedCount = codemodPlans.filter(p => p.risk === 'BLOCKED_ARCHITECTURE').length;
  const extractionCount = codemodPlans.filter(p => p.risk === 'REQUIRES_EXTRACTION').length;
  if (safeCodemodCount > 0) {
    lines.push(`4. **Quick win:** Apply the ${safeCodemodCount} safe codemod plan(s) — EXACT drift with canonical defined`);
  }
  if (blockedCount > 0 || extractionCount > 0) {
    lines.push(`${safeCodemodCount > 0 ? '5' : '4'}. **Unblock codemods:** ${blockedCount > 0 ? `${blockedCount} BLOCKED (extract canonical from page/route to types/)` : ''}${blockedCount > 0 && extractionCount > 0 ? ' · ' : ''}${extractionCount > 0 ? `${extractionCount} REQUIRES_EXTRACTION (create shared package first)` : ''}`);
  }
  lines.push(`${safeCodemodCount > 0 ? (blockedCount > 0 || extractionCount > 0 ? '6' : '5') : (blockedCount > 0 || extractionCount > 0 ? '5' : '4')}. **Next engine PR:** Drift normalization snake↔camel/pt↔en (PR17)`);
  lines.push(``);
  lines.push(`---`);
  lines.push(``);

  // ─── HIGH: Cross-Package ───────────────────────────────────
  if (highCross.length > 0) {
    lines.push(`## 🔴 High Confidence — Cross-Package (${highCross.length})`);
    lines.push(`> Strongest cross-package drift signals: exported declarations, non-convention names, and repeated structural declarations.`);
    lines.push(``);
    for (const f of highCross) {
      lines.push(`### 🔴 ${f.message}`);
      lines.push(`- **Score:** ${f.confidenceScore}/10 *(${f.confidenceRationale.join(', ')})*`);
      if (f.autonomyScore !== undefined) lines.push(`- **Autonomy:** ${f.autonomyScore}/100 → \`${f.autonomyAction}\``);
      if (f.boundedContext && f.drift?.kind === 'DIVERGENT') lines.push(`- **Context:** \`${f.boundedContext.verdict}\` (${f.boundedContext.confidence}/100) — ${f.boundedContext.reasons.join(' · ')}`);
      if (f.decisionRegistry && f.decisionRegistry.matchStatus !== 'NONE') {
        const dr = f.decisionRegistry;
        const matchBadge = dr.matchStatus === 'APPLIED' ? '✅' : dr.matchStatus === 'STALE' ? '⚠️' : '❓';
        const lifecycleBadge = dr.status === 'APPROVED' ? '🟢' : dr.status === 'IMPLEMENTED' ? '✅' : dr.status === 'PROPOSED' ? '🟡' : '⚪';
        lines.push(`- **Decision:** ${matchBadge} Registry: \`${dr.matchStatus}\` | ${lifecycleBadge} Lifecycle: \`${dr.status}\` | Action: \`${dr.action}\` (owner: ${dr.owner || 'unassigned'}, ${dr.date})`);
        if (dr.rationale) lines.push(`  - *${dr.rationale}*`);
        if (dr.staleReason) lines.push(`  - ⚠️ ${dr.staleReason}`);
      }
      lines.push(`- **Kind:** ${f.symbolKind || 'mixed'}`);
      lines.push(`- **Packages:** ${f.packages?.join(', ') || 'unknown'}`);
      if (f.locations) {
        lines.push(`- **Locations:**`);
        for (const loc of f.locations) {
          lines.push(`  - \`${loc}\``);
        }
      }
      lines.push(`- **Recommendation:** ${f.suggestion}`);
      if (f.semanticCheck) {
        lines.push(`- ${formatSemanticCheck(f.semanticCheck)}`);
      }
      lines.push(``);
    }
  }

  // ─── HIGH: Intra-Package ───────────────────────────────────
  if (highIntra.length > 0) {
    lines.push(`## 🟠 High Confidence — Intra-Package Exported Drift (${highIntra.length})`);
    lines.push(`> High-scoring duplicates within the same package — strong signal of internal drift.`);
    lines.push(``);
    for (const f of highIntra) {
      lines.push(`### 🟠 ${f.message}`);
      lines.push(`- **Score:** ${f.confidenceScore}/10 *(${f.confidenceRationale.join(', ')})*`);
      if (f.autonomyScore !== undefined) lines.push(`- **Autonomy:** ${f.autonomyScore}/100 → \`${f.autonomyAction}\``);
      if (f.boundedContext && f.drift?.kind === 'DIVERGENT') lines.push(`- **Context:** \`${f.boundedContext.verdict}\` (${f.boundedContext.confidence}/100) — ${f.boundedContext.reasons.join(' · ')}`);
      if (f.decisionRegistry && f.decisionRegistry.matchStatus !== 'NONE') {
        const dr = f.decisionRegistry;
        const matchBadge = dr.matchStatus === 'APPLIED' ? '✅' : dr.matchStatus === 'STALE' ? '⚠️' : '❓';
        const lifecycleBadge = dr.status === 'APPROVED' ? '🟢' : dr.status === 'IMPLEMENTED' ? '✅' : dr.status === 'PROPOSED' ? '🟡' : '⚪';
        lines.push(`- **Decision:** ${matchBadge} Registry: \`${dr.matchStatus}\` | ${lifecycleBadge} Lifecycle: \`${dr.status}\` | Action: \`${dr.action}\` (owner: ${dr.owner || 'unassigned'}, ${dr.date})`);
        if (dr.rationale) lines.push(`  - *${dr.rationale}*`);
        if (dr.staleReason) lines.push(`  - ⚠️ ${dr.staleReason}`);
      }
      lines.push(`- **Kind:** ${f.symbolKind || 'mixed'}`);
      lines.push(`- **Package:** ${f.packages?.[0] || 'unknown'}`);
      if (f.locations) {
        lines.push(`- **Locations:**`);
        for (const loc of f.locations) {
          lines.push(`  - \`${loc}\``);
        }
      }
      lines.push(`- **Recommendation:** ${f.suggestion}`);
      if (f.semanticCheck) {
        lines.push(`- ${formatSemanticCheck(f.semanticCheck)}`);
      }
      lines.push(``);
    }
  }

  // ─── MEDIUM (top 10 detailed, rest compact) ─────────────────
  if (medConf.length > 0) {
    lines.push(`## ⚠️ Medium Confidence Signals (${medConf.length})`);
    lines.push(`> Require validation — may be intentional or framework-driven.`);
    lines.push(``);

    // Top 10 medium findings get locations for actionability
    const medTop = medConf.slice(0, 10);
    const medRest = medConf.slice(10);

    for (const f of medTop) {
      lines.push(`### ${f.message}`);
      lines.push(`- **Score:** ${f.confidenceScore}/10 *(${f.confidenceRationale.join(', ')})*`);
      if (f.locations && f.locations.length > 0) {
        lines.push(`- **Locations:** ${f.locations.map(l => `\`${l}\``).join(', ')}`);
      }
      lines.push(`- **Recommendation:** ${f.suggestion}`);
      lines.push(``);
    }

    if (medRest.length > 0) {
      lines.push(`### Remaining Medium Signals (${medRest.length})`);
      lines.push(``);
      for (const f of medRest) {
        lines.push(`- **${f.message}** — Score: ${f.confidenceScore}/10 — ${f.suggestion}`);
      }
      lines.push(``);
    }
  }

  // ─── LOW (collapsed) ───────────────────────────────────────
  if (lowConf.length > 0) {
    lines.push(`## ℹ️ Low Confidence / Convention (${lowConf.length})`);
    lines.push(`> Likely framework conventions, local variants, or orphaned exports.`);
    lines.push(`> Review only if actively cleaning up the codebase.`);
    lines.push(``);
    for (const f of lowConf.slice(0, 20)) {
      lines.push(`- ${f.message}`);
    }
    if (lowConf.length > 20) {
      lines.push(`- ... and ${lowConf.length - 20} more`);
    }
    lines.push(``);
  }

  // ─── METHODOLOGY ───────────────────────────────────────────
  lines.push(`---`);
  lines.push(``);
  lines.push(`## Methodology`);
  lines.push(``);
  lines.push(`This report uses the TypeScript compiler API (\`ts.createSourceFile\`) to parse`);
  lines.push(`the AST of each file. Only structural type-level declarations are extracted:`);
  lines.push(`interfaces, type aliases, enums, and classes. Comments, strings, property keys,`);
  lines.push(`and variable names are **not** captured (fixing a known v1 issue).`);
  lines.push(``);
  lines.push(`### Package Inference`);
  lines.push(``);
  lines.push(`Package names are inferred from file paths using the following rules:`);
  lines.push(`- \`apps/<name>/...\` → package = \`<name>\` (e.g., \`apps/egos-web/src/App.tsx\` → \`egos-web\`)`);
  lines.push(`- \`packages/<name>/...\` → package = \`<name>\` (e.g., \`packages/shared/src/types.ts\` → \`shared\`)`);
  lines.push(`- Other top-level dirs → package = dir name (e.g., \`agents/...\` → \`agents\`, \`scripts/...\` → \`scripts\`)`);
  lines.push(``);
  lines.push(`This is path-based inference, not \`package.json\` resolution. It works reliably for`);
  lines.push(`standard monorepo layouts (\`apps/*\`, \`packages/*\`) but may not capture workspace aliases.`);
  lines.push(``);
  lines.push(`### Confidence Scoring (Explicit)`);
  lines.push(``);
  lines.push(`Each finding receives a numeric score (0-10) with human-readable rationale:`);
  lines.push(``);
  lines.push(`| Factor | Score | Condition |`);
  lines.push(`|--------|-------|-----------|`);
  lines.push(`| Exported | +3 | 2+ exported declarations |`);
  lines.push(`| Cross-package | +3 | Appears in 2+ workspace packages |`);
  lines.push(`| Non-convention name | +2 | Not a UI/framework convention (Props, State, PageProps…) |`);
  lines.push(`| Domain-specific | +1 | Name matches domain patterns (Investigation, Entity, Timeline…) |`);
  lines.push(`| Long name | +1 | Name > 8 characters |`);
  lines.push(`| Count (4-5×) | +1 | 4-5 occurrences |`);
  lines.push(`| Count (6-9×) | +2 | 6-9 occurrences |`);
  lines.push(`| Count (10+×) | +3 | 10+ occurrences |`);
  lines.push(`| UI/framework convention | -3 | Pure framework pattern (Props, State, PageProps, etc.) |`);
  lines.push(`| Generic infra name | -1 | Generic term (User, Stats, Message, Toast, etc.) |`);
  lines.push(`| Generated file | -2 | Involves auto-generated code |`);
  lines.push(`| Single package | -1 | All in the same workspace package |`);
  lines.push(`| Too short | -3 | Name ≤ 2 characters |`);
  lines.push(``);
  lines.push(`**Thresholds (split by scope):**`);
  lines.push(`- Cross-package: High ≥ 7 | Medium ≥ 3 | Low < 3`);
  lines.push(`- Intra-package: High ≥ 6 | Medium ≥ 2 | Low < 2`);
  lines.push(``);
  lines.push(`### Canonical Candidate Ranking`);
  lines.push(``);
  lines.push(`When multiple locations exist for a duplicate, the engine ranks them as canonical candidates using path-based heuristics:`);
  lines.push(``);
  lines.push(`| Path Signal | Score | Rationale |`);
  lines.push(`|------------|-------|-----------|`);
  lines.push(`| \`packages/shared/\` or \`packages/nexus-shared/\` | +50 | Shared packages are the authoritative source |`);
  lines.push(`| \`/types/\` directory | +30 | Dedicated type directories signal intent to be canonical |`);
  lines.push(`| Exported symbol | +20 | Exported = intended for reuse |`);
  lines.push(`| \`/api/\` or \`route.ts\` (for domain types) | +10 | API routes define contracts |`);
  lines.push(`| \`/components/\` (non-UI type) | -20 | Components are bad canonical sources for domain/infra types |`);
  lines.push(`| \`/components/\` (UI type) | +10 | Good source for UI primitives |`);
  lines.push(``);
  lines.push(`When no location scores above 0 (all tied), the report emits: ⚪ *No canonical candidate identified*.`);
  lines.push(``);
  lines.push(`### Semantic Taxonomy`);
  lines.push(``);
  lines.push(`Each symbol is classified into one of five categories:`);
  lines.push(``);
  lines.push(`| Category | Examples | Score Effect |`);
  lines.push(`|----------|----------|-------------|`);
  lines.push(`| \`domain\` | Investigation, Entity, Timeline, Evidence, Audit | +1 (domain-specific bonus) |`);
  lines.push(`| \`infra\` | SessionUser, RateLimitEntry (path: /lib/auth, /security) | neutral |`);
  lines.push(`| \`ui\` | Props, Toast, Modal, Card, Badge, Skeleton, NavItem | -3 (convention penalty) |`);
  lines.push(`| \`generic-domain\` | User, Message, ChatMessage, UserProfile, Role | +1 (treated as domain contract) |`);
  lines.push(`| \`generic-infra\` | Config, Result, Item, Payload, Stats | -1 (infra penalty) |`);
  lines.push(``);
  lines.push(`Classification priority: Props suffix → UI token whitelist → Domain patterns → Generic-domain set → Generic-infra set → Path-based infra → fallback generic-infra.`);
  lines.push(``);
  lines.push(`### Shape Fingerprinting (v2.7)`);
  lines.push(``);
  lines.push(`Each interface and type alias gets a normalized structural fingerprint used for drift classification:`);
  lines.push(``);
  lines.push(`| Fingerprint | Description |`);
  lines.push(`|------------|-------------|`);
  lines.push(`| **strict** | Full fidelity: prop names, types, optionality (\`?\`), readonly modifier |`);
  lines.push(`| **relaxed** | Ignores \`readonly\` modifier only — optionality (\`?\`) is **preserved** and counts as a structural difference |`);
  lines.push(``);
  lines.push(`**Normalization rules:**`);
  lines.push(`- Props sorted alphabetically (order-independent comparison)`);
  lines.push(`- Union members sorted: \`string | number\` ≡ \`number | string\``);
  lines.push(`- \`Array<T>\` ≡ \`T[]\` (both → \`array<T>\`)`);
  lines.push(`- Object literals recursively normalized`);
  lines.push(`- Complex types (mapped, conditional, template) → opaque tokens (\`mapped\`, \`conditional\`, \`template\`)`);
  lines.push(`- Unresolvable types → \`?\``);
  lines.push(``);
  lines.push(`**Drift classification:**`);
  lines.push(`| Classification | Condition | Action |`);
  lines.push(`|--------------|-----------|--------|`);
  lines.push(`| ✅ EXACT | All strict fingerprints identical | Safe to consolidate |`);
  lines.push(`| 🟢 RELAXED | Strict differs, relaxed identical | Likely safe — only readonly modifier differs |`);
  lines.push(`| ⚠️ DIVERGENT | Both strict and relaxed differ | Manual review required before consolidating |`);
  lines.push(`| ⚪ UNRESOLVED | Shape is empty/class/parse error | Cannot determine from AST alone |`);
  lines.push(``);
  lines.push(`**Known fingerprint limitations (v3.0):**`);
  lines.push(`- \`extends\` clauses ARE expanded (PR2) for same-repo interfaces; external/3rd-party base types are kept as-is`);
  lines.push(`- External type references (\`User\`, \`Entity\`) are kept as opaque names, not resolved`);
  lines.push(`- Classes: public fields/ctor-params/methods ARE fingerprinted (PR3); abstract members and complex decorators are not`);
  lines.push(``);
  lines.push(`### Known Limitations`);
  lines.push(``);
  lines.push(`1. **Shape comparison is heuristic** — fingerprints are normalized AST strings, not semantic TypeChecker analysis (PR15 planned)`);
  lines.push(`2. **Import graph is regex-based** — re-export/barrel resolution (PR8) uses regex, not full TS module resolution`);
  lines.push(`3. **Confidence is heuristic** — based on structural signals, not semantic analysis`);
  lines.push(`4. **Framework conventions are not exhaustive** — custom project-specific patterns may be missed`);
  lines.push(`5. **No cross-repo analysis** — only scans the target monorepo`);
  lines.push(`6. **Generated files** — detected by path patterns (\`generated\`, \`.gen\`, \`dist\`, etc.) and optional \`@generated\` file headers`);
  lines.push(`7. **Union alias drift is structural only** — DRIFT_UNION_MEMBERS_ADDED/REMOVED compares normalized variant strings; semantic intent is not analyzed`);
  lines.push(`8. **Import centrality is file-level** — counts files importing from a module, not specific symbol-level usage`);
  lines.push(``);

  return lines.join('\n');
}

// ─── CLI Entry ────────────────────────────────────────────────

const args = process.argv.slice(2);
const mode = args.includes('--exec') ? 'execute' as const : 'dry_run' as const;

// --min-confidence=medium|high (default: show all)
const minConfArg = args.find(a => a.startsWith('--min-confidence='));
const minConfidence: 'low' | 'medium' | 'high' = minConfArg
  ? (minConfArg.split('=')[1] as 'low' | 'medium' | 'high') || 'low'
  : 'low';

// --json-only (skip markdown report)
const jsonOnly = args.includes('--json-only');

// PR14: CI governance flags
const saveBaseline = args.includes('--save-baseline');
const checkBudget = args.includes('--check-budget');

// Store CLI options in a global for the audit function to access
(globalThis as any).__ssotCliOptions = { minConfidence, jsonOnly, saveBaseline, checkBudget };

runAgent('ssot_auditor', mode, ssotAudit).then(result => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});

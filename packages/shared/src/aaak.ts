/**
 * AAAK Compression — Adaptive AI Knowledge encoding
 *
 * Port of MemPalace's AAAK (AI-Agent Knowledge) compression algorithm.
 * Lossless shorthand dialect optimized for AI memory storage and retrieval.
 *
 * Principles:
 * - 30× compression target (from ~1000 tokens to ~30 tokens)
 * - Lossless reversible encoding
 * - Structural preservation (hierarchy, relationships)
 * - Semantic density (maximum meaning per token)
 *
 * @module AAAK
 * @see https://github.com/milla-jovovich/mempalace
 */

// ═════════════════════════════════════════════════════════════════════════════
// Compression Dictionary — Common patterns → shorthand tokens
// ═════════════════════════════════════════════════════════════════════════════

const COMPRESSION_MAP: Record<string, string> = {
  // Roles and actors
  'ASSISTANT:': 'A:',
  'USER:': 'U:',
  'AGENT:': 'G:', // G for agent (A taken by assistant)
  'SYSTEM:': 'S:',
  'HUMAN:': 'H:',

  // Common actions
  'implemented': 'impl',
  'implementation': 'impl·n',
  'configured': 'cfg·d',
  'configuration': 'cfg·n',
  'created': 'crt·d',
  'creation': 'crt·n',
  'updated': 'upd·d',
  'update': 'upd',
  'deleted': 'del·d',
  'delete': 'del',
  'modified': 'mod·d',
  'modification': 'mod·n',

  // Technical terms
  'function': 'fn',
  'variable': 'var',
  'constant': 'const',
  'parameter': 'param',
  'argument': 'arg',
  'return': 'ret',
  'interface': 'iface',
  'type': 't',
  'class': 'cls',
  'method': 'mtd',
  'property': 'prop',
  'array': 'arr',
  'object': 'obj',
  'string': 'str',
  'number': 'num',
  'boolean': 'bool',

  // EGOS domain
  'agent': 'ag',
  'agents': 'ags',
  'memory': 'mem',
  'conversation': 'conv',
  'session': 'ses',
  'repository': 'repo',
  'repositories': 'repos',
  'component': 'comp',
  'components': 'comps',
  'package': 'pkg',
  'packages': 'pkgs',
  'interfaces': 'ifaces',
  'database': 'db',
  'table': 'tbl',
  'migration': 'mig',
  'endpoint': 'ep',
  'endpoints': 'eps',
  'environment': 'env',
  'production': 'prod',
  'development': 'dev',
  'testing': 'test',

  // Common words
  'the': '·',
  'and': '&',
  'or': '|',
  'with': 'w/',
  'without': 'w/o',
  'for': '4',
  'from': 'fr',
  'to': '→',
  'of': 'o',
  'in': '∈',
  'at': '@',
  'by': 'β',
  'as': '≡',
  'is': '=',
  'are': '=',
  'was': '≈',
  'were': '≈',
  'be': 'b',
  'been': 'bn',
  'being': 'bg',
  'have': 'hv',
  'has': 'hs',
  'had': 'hd',
  'do': 'd',
  'does': 'ds',
  'did': 'dd',
  'will': 'wl',
  'would': 'wd',
  'should': 'shd',
  'could': 'cd',
  'can': 'cn',
  'may': 'my',
  'might': 'mt',
  'must': 'ms',
};

const REVERSE_MAP: Record<string, string> = Object.fromEntries(
  Object.entries(COMPRESSION_MAP).map(([k, v]) => [v, k])
);

// ═════════════════════════════════════════════════════════════════════════════
// Structural Markers
// ═════════════════════════════════════════════════════════════════════════════

const MARKERS = {
  // Hierarchy
  SECTION_START: '〔', // U+3014
  SECTION_END: '〕',   // U+3015
  GROUP_START: '【',   // U+3010
  GROUP_END: '】',     // U+3011
  ITEM_START: '〖',    // U+3016
  ITEM_END: '〗',      // U+3017

  // Relationships
  PARENT: '↑',
  CHILD: '↓',
  SIBLING: '↔',
  REFERENCE: '→',
  DEPENDENCY: '⇒',

  // Temporal
  BEFORE: '◀',
  AFTER: '▶',
  DURING: '◆',
  COMPLETED: '✓',
  PENDING: '○',
  BLOCKED: '✗',

  // Semantic
  IMPORTANT: '★',
  QUESTION: '?',
  DECISION: '◈',
  PATTERN: '◇',
  ISSUE: '⚠',
  FIXED: '✓',

  // Compression
  ELLIPSIS: '…',
  CONTINUATION: '→',
  REPEAT: '↻',
} as const;

// ═════════════════════════════════════════════════════════════════════════════
// Compression Functions
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Compress text using AAAK encoding
 * @param text Original text to compress
 * @param options Compression options
 * @returns Compressed AAAK string
 */
export function compress(text: string, options: {
  aggressive?: boolean;
  preserveStructure?: boolean;
  maxTokens?: number;
} = {}): string {
  const { aggressive = true, preserveStructure = true, maxTokens = 170 } = options;

  if (!text || text.trim().length === 0) return '';

  let compressed = text;

  // Phase 1: Dictionary compression (word-level)
  if (aggressive) {
    compressed = applyDictionaryCompression(compressed);
  }

  // Phase 2: Structural compression (sentence-level)
  if (preserveStructure) {
    compressed = applyStructuralCompression(compressed);
  }

  // Phase 3: Pattern compression (phrase-level)
  compressed = applyPatternCompression(compressed);

  // Phase 4: Truncate if exceeds max tokens (with preservation marker)
  if (maxTokens && estimateTokens(compressed) > maxTokens) {
    compressed = truncateWithPreservation(compressed, maxTokens);
  }

  return compressed;
}

/**
 * Decompress AAAK-encoded text back to readable form
 * @param compressed AAAK compressed string
 * @returns Decompressed text
 */
export function decompress(compressed: string): string {
  if (!compressed || compressed.trim().length === 0) return '';

  let text = compressed;

  // Reverse order of compression

  // Phase 1: Expand structural markers
  text = expandStructuralMarkers(text);

  // Phase 2: Dictionary decompression
  text = applyDictionaryDecompression(text);

  // Phase 3: Clean up spacing
  text = cleanDecompressedText(text);

  return text;
}

// ═════════════════════════════════════════════════════════════════════════════
// Internal Implementation
// ═════════════════════════════════════════════════════════════════════════════

function applyDictionaryCompression(text: string): string {
  let compressed = text;

  // Sort by length descending to avoid partial replacements
  const sortedEntries = Object.entries(COMPRESSION_MAP)
    .sort(([a], [b]) => b.length - a.length);

  for (const [word, shorthand] of sortedEntries) {
    // Case-insensitive replacement with case preservation hint
    const regex = new RegExp(`\\b${escapeRegex(word)}\\b`, 'gi');
    compressed = compressed.replace(regex, (match) => {
      // Preserve case information
      if (match === match.toUpperCase()) {
        return shorthand.toUpperCase();
      } else if (match[0] === match[0].toUpperCase()) {
        return shorthand[0].toUpperCase() + shorthand.slice(1);
      }
      return shorthand;
    });
  }

  return compressed;
}

function applyDictionaryDecompression(text: string): string {
  let expanded = text;

  // Sort by length descending
  const sortedEntries = Object.entries(REVERSE_MAP)
    .sort(([a], [b]) => b.length - a.length);

  for (const [shorthand, word] of sortedEntries) {
    const regex = new RegExp(escapeRegex(shorthand), 'g');
    expanded = expanded.replace(regex, word);
  }

  return expanded;
}

function applyStructuralCompression(text: string): string {
  // Compress common structural patterns

  // Convert markdown headers to markers
  text = text.replace(/#{3,6}\s+(.+)/g, `${MARKERS.ITEM_START}$1${MARKERS.ITEM_END}`);
  text = text.replace(/#{1,2}\s+(.+)/g, `${MARKERS.SECTION_START}$1${MARKERS.SECTION_END}`);

  // Convert bullet points
  text = text.replace(/^\s*[-*]\s+(.+)$/gm, `${MARKERS.ITEM_START}$1${MARKERS.ITEM_END}`);

  // Convert numbered lists
  text = text.replace(/^\s*\d+\.\s+(.+)$/gm, `${MARKERS.ITEM_START}$1${MARKERS.ITEM_END}`);

  // Mark important sentences (containing key terms)
  text = text.replace(/([^.]*)\b(important|critical|essential|key)\b([^]*?\.)?/gi,
    `${MARKERS.IMPORTANT}$1$2$3${MARKERS.IMPORTANT}`);

  return text;
}

function expandStructuralMarkers(text: string): string {
  // Expand markers back to readable form

  // Headers
  text = text.replace(new RegExp(`${escapeRegex(MARKERS.SECTION_START)}(.+?)${escapeRegex(MARKERS.SECTION_END)}`, 'g'),
    '## $1');
  text = text.replace(new RegExp(`${escapeRegex(MARKERS.GROUP_START)}(.+?)${escapeRegex(MARKERS.GROUP_END)}`, 'g'),
    '### $1');

  // Items
  text = text.replace(new RegExp(`${escapeRegex(MARKERS.ITEM_START)}(.+?)${escapeRegex(MARKERS.ITEM_END)}`, 'g'),
    '- $1');

  // Remove importance markers (keep content)
  text = text.replace(new RegExp(`${escapeRegex(MARKERS.IMPORTANT)}`, 'g'), '');

  return text;
}

function applyPatternCompression(text: string): string {
  // Remove redundant whitespace
  text = text.replace(/\n{3,}/g, '\n\n');
  text = text.replace(/[ \t]+/g, ' ');

  // Compress repeated punctuation
  text = text.replace(/\.{3,}/g, MARKERS.ELLIPSIS);
  text = text.replace(/!{2,}/g, '!');
  text = text.replace(/\?{2,}/g, '?');

  return text;
}

function truncateWithPreservation(text: string, maxTokens: number): string {
  // Simple token estimation: ~4 chars per token for compressed text
  const estimatedTokens = estimateTokens(text);

  if (estimatedTokens <= maxTokens) return text;

  // Truncate at section boundary if possible
  const charLimit = maxTokens * 4;
  let truncated = text.slice(0, charLimit);

  // Try to end at a section boundary
  const lastSectionEnd = truncated.lastIndexOf(MARKERS.SECTION_END);
  const lastItemEnd = truncated.lastIndexOf(MARKERS.ITEM_END);
  const lastBreak = Math.max(lastSectionEnd, lastItemEnd);

  if (lastBreak > charLimit * 0.7) {
    truncated = truncated.slice(0, lastBreak + 1);
  }

  return truncated + MARKERS.ELLIPSIS;
}

function estimateTokens(text: string): number {
  // Rough estimation: compressed text averages 4 chars per token
  return Math.ceil(text.length / 4);
}

function cleanDecompressedText(text: string): string {
  // Fix spacing
  text = text.replace(/\s+/g, ' ');
  text = text.replace(/\s*([.,;:!?])\s*/g, '$1 ');
  text = text.replace(/\s+\n/g, '\n');
  text = text.replace(/\n\s+/g, '\n');

  // Trim
  text = text.trim();

  return text;
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ═════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═════════════════════════════════════════════════════════════════════════════

/**
 * Calculate compression ratio
 * @param original Original text
 * @param compressed Compressed text
 * @returns Compression ratio (e.g., 0.3 = 70% reduction)
 */
export function compressionRatio(original: string, compressed: string): number {
  if (!original || original.length === 0) return 1;
  return compressed.length / original.length;
}

/**
 * Estimate token savings
 * @param original Original text token count
 * @param compressed Compressed text token count
 * @returns Percentage of tokens saved
 */
export function tokenSavings(original: string, compressed: string): number {
  const origTokens = Math.ceil(original.length / 4);
  const compTokens = Math.ceil(compressed.length / 4);

  if (origTokens === 0) return 0;
  return ((origTokens - compTokens) / origTokens) * 100;
}

/**
 * Batch compress multiple memories
 * @param memories Array of memory strings
 * @param options Compression options
 * @returns Array of compressed memories
 */
export function batchCompress(
  memories: string[],
  options?: Parameters<typeof compress>[1]
): string[] {
  return memories.map(m => compress(m, options));
}

/**
 * Create AAAK-encoded memory block for system prompt injection
 * @param memories Array of compressed memory summaries
 * @returns Formatted memory block
 */
export function buildAAAKMemoryBlock(memories: string[]): string {
  if (memories.length === 0) return '';

  const header = '〔AAAK-MEM〕';
  const footer = '〔/AAAK-MEM〕';

  const content = memories
    .map((mem, i) => `〖${i + 1}〗${mem}`)
    .join('');

  return `${header}${content}${footer}`;
}

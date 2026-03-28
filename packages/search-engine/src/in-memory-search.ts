import type { Atom } from '@egos/types/atom';
import type { SearchQuery } from '@egos/core/contracts';

export interface SearchResult {
  atom: Atom;
  score: number;
  reasons: string[];
}

function scoreAtom(atom: Atom, query: string): SearchResult {
  const normalizedQuery = query.toLowerCase().trim();
  const text = atom.normalizedContent;

  let score = 0;
  const reasons: string[] = [];

  if (text.includes(normalizedQuery)) {
    score += 10;
    reasons.push('exact-substring');
  }

  const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
  const matchedTokens = tokens.filter((token) => text.includes(token)).length;

  if (tokens.length > 0) {
    score += (matchedTokens / tokens.length) * 5;
    if (matchedTokens > 0) reasons.push('token-overlap');
  }

  score += atom.confidence;

  return {
    atom,
    score,
    reasons,
  };
}

export class InMemorySearchEngine {
  private readonly atoms: Atom[] = [];

  async index(atoms: Atom[]): Promise<void> {
    this.atoms.push(...atoms);
  }

  async search(query: SearchQuery): Promise<SearchResult[]> {
    const limit = query.limit ?? 10;

    return this.atoms
      .map((atom) => scoreAtom(atom, query.text))
      .filter((result) => result.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }

  async suggest(prefix: string): Promise<string[]> {
    const normalizedPrefix = prefix.toLowerCase().trim();
    if (!normalizedPrefix) return [];

    const suggestions = new Set<string>();

    for (const atom of this.atoms) {
      if (atom.normalizedContent.startsWith(normalizedPrefix)) {
        suggestions.add(atom.content.slice(0, 120));
      }
      if (suggestions.size >= 8) break;
    }

    return [...suggestions];
  }
}

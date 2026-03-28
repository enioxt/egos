import crypto from 'node:crypto';
import type { Atom } from '@egos/types/atom';

export interface AtomizeInput {
  sourceId: string;
  sourceType: string;
  content: string;
  authorId?: string;
  metadata?: Record<string, unknown>;
}

function normalize(text: string): string {
  return text
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
}

function sentenceSplit(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function makeId(seed: string): string {
  return crypto.createHash('sha256').update(seed).digest('hex').slice(0, 24);
}

export class DefaultAtomizer {
  async atomize(input: AtomizeInput): Promise<Atom[]> {
    const now = new Date().toISOString();
    const sentences = sentenceSplit(input.content);

    return sentences.map((sentence, index) => ({
      id: makeId(`${input.sourceId}:${index}:${sentence}`),
      kind: 'text',
      content: sentence,
      normalizedContent: normalize(sentence),
      sourceId: input.sourceId,
      sourceType: input.sourceType,
      authorId: input.authorId,
      tags: [],
      entities: [],
      claims: [],
      relations: [],
      permissions: [],
      version: 1,
      lineage: [],
      confidence: 0.5,
      metadata: {
        ...input.metadata,
        sentenceIndex: index,
      },
      createdAt: now,
      updatedAt: now,
    }));
  }
}

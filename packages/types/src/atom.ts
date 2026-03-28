export type AtomKind =
  | 'text'
  | 'claim'
  | 'entity'
  | 'relation'
  | 'rule'
  | 'prompt'
  | 'policy'
  | 'workflow'
  | 'integration'
  | 'event'
  | 'insight';

export interface AtomRelation {
  type: string;
  targetAtomId: string;
  weight?: number;
  metadata?: Record<string, unknown>;
}

export interface Atom {
  id: string;
  kind: AtomKind;
  content: string;
  normalizedContent: string;
  sourceId: string;
  sourceType: string;
  authorId?: string;
  tags: string[];
  entities: string[];
  claims: string[];
  relations: AtomRelation[];
  permissions: string[];
  version: number;
  lineage: string[];
  confidence: number;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
  embedding?: number[];
}

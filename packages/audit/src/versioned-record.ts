export interface VersionedRecord<T> {
  id: string;
  canonicalId: string;
  version: number;
  authorId: string;
  createdAt: string;
  supersedes?: string;
  disputeOf?: string;
  justification?: string;
  content: T;
  status: 'active' | 'contested' | 'archived';
}

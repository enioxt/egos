/**
 * Agent Signature & Action Ledger — INC-001 mitigation
 *
 * Cryptographically signs every meaningful action an agent takes and
 * appends it to a tamper-evident Merkle chain stored in Supabase.
 *
 * This is the action-provenance layer that complements:
 *   - provenance.ts        → data provenance (raw_line_hash, source_*)
 *   - evidence-chain.ts    → claim provenance (AI claims + tool calls)
 *   - PRI (pri.md)         → decision gates (ALLOW/BLOCK/DEFER/ESCALATE/STUDY)
 *
 * Design (born from INC-001 — 2026-04-06 force-push by parallel agent):
 *
 * 1. Each agent has an Ed25519 keypair. Public key stored in
 *    `agent_keys` table; private key stored in Supabase Vault.
 *
 * 2. Every meaningful action (commit, push, merge, deploy, release,
 *    config_change, message_send, etc.) goes through `signAndAppend()`
 *    which:
 *      a) builds br-acc-style audit fields via provenance.ts
 *      b) computes prev_hash → hash chain link
 *      c) signs `hash` with the agent's private key
 *      d) inserts into `agent_actions_ledger`
 *      e) returns the row including the signature
 *
 * 3. Each action declares an `approval_level`:
 *      L0 = autonomous (just log)
 *      L1 = notify (log + ping a human channel)
 *      L2 = approval (don't execute until a human marks `approved_by`)
 *
 * 4. Verifying chain integrity is a single SELECT on the
 *    `agent_ledger_integrity` view (returns broken links).
 *
 * 5. Verifying any individual action: anyone can fetch the agent's
 *    public key + the action row, recompute the hash from the chain,
 *    and verify the Ed25519 signature. No central trust.
 */

import { createSign, createVerify, generateKeyPairSync, createPublicKey, sign as edSign, verify as edVerify } from 'node:crypto';
import { buildAuditFields, sha256Text, type AuditFields } from './provenance.ts';

export type ApprovalLevel = 'L0' | 'L1' | 'L2';

export type ActionType =
  | 'commit' | 'push' | 'merge' | 'release' | 'deploy' | 'config_change'
  | 'message_send' | 'task_create' | 'task_update' | 'file_write' | 'file_delete'
  | 'api_call' | 'tool_use' | 'merge_pr' | 'merge_branch' | 'rebase'
  | 'schedule_run' | 'governance_check' | 'audit_run'
  | 'fetch_source' | 'parse_response' | 'enrich_node' | 'graph_write'
  | 'other';

/**
 * Default approval levels per action type. Risky actions default to L2
 * so they wait for human approval. Safe read-only actions default to L0.
 *
 * Override per call via `signAndAppend({ approvalLevel: ... })`.
 */
export const DEFAULT_APPROVAL_LEVELS: Record<ActionType, ApprovalLevel> = {
  // L2 — risky, requires human approval before execution
  push: 'L2',
  merge: 'L2',
  merge_pr: 'L2',
  merge_branch: 'L2',
  release: 'L2',
  deploy: 'L2',
  config_change: 'L2',
  rebase: 'L2',
  file_delete: 'L2',

  // L1 — notify a human, then proceed
  commit: 'L1',
  message_send: 'L1',
  task_create: 'L1',
  task_update: 'L1',
  file_write: 'L1',

  // L0 — autonomous, just log
  api_call: 'L0',
  tool_use: 'L0',
  schedule_run: 'L0',
  governance_check: 'L0',
  audit_run: 'L0',
  fetch_source: 'L0',
  parse_response: 'L0',
  enrich_node: 'L0',
  graph_write: 'L0',
  other: 'L0',
};

export interface AgentKeyPair {
  agentId: string;
  publicKeyBase64Url: string;
  privateKeyPem: string; // PKCS#8 PEM (store in Supabase Vault, NOT git)
}

export interface SignedAction extends AuditFields {
  id?: string;
  ts: string;
  agent_id: string;
  action_type: ActionType;
  approval_level: ApprovalLevel;
  payload: Record<string, unknown>;
  prev_hash: string | null;
  hash: string;
  signature: string;
  signing_key_id?: string;
  approved_by?: string | null;
  approval_evidence?: Record<string, unknown> | null;
  correlation_id?: string;
}

export interface SignAndAppendOptions {
  agentId: string;
  privateKeyPem: string;
  actionType: ActionType;
  payload: Record<string, unknown>;
  sourceUrl: string;     // file://, https://, ccr://, gha://, local://...
  sourceMethod: string;  // 'git_commit', 'http_get', 'ccr_scheduled', etc.
  approvalLevel?: ApprovalLevel;
  prevHash?: string | null;
  correlationId?: string;
  ts?: string;
}

// ─── key management ─────────────────────────────────────────────────────

/**
 * Generate a new Ed25519 keypair for an agent. Call this ONCE per agent
 * and store the private key in Supabase Vault. The public key goes into
 * the `agent_keys` table.
 */
export function generateAgentKeyPair(agentId: string): AgentKeyPair {
  const { publicKey, privateKey } = generateKeyPairSync('ed25519');
  const pubRaw = publicKey.export({ format: 'der', type: 'spki' });
  // SPKI Ed25519 has a fixed 12-byte prefix; the actual key is the last 32 bytes
  const pubBytes = pubRaw.subarray(pubRaw.length - 32);
  return {
    agentId,
    publicKeyBase64Url: bufToBase64Url(pubBytes),
    privateKeyPem: privateKey.export({ format: 'pem', type: 'pkcs8' }) as string,
  };
}

// ─── canonical action serialization ─────────────────────────────────────

/**
 * Compute the deterministic hash for an action row. This is what gets
 * signed. Including prev_hash makes the chain Merkle-linked: rewriting
 * any past row breaks all subsequent hashes.
 */
export function computeActionHash(args: {
  prevHash: string | null;
  ts: string;
  agentId: string;
  actionType: ActionType;
  rawLineHash: string;
  sourceFingerprint: string;
}): string {
  const parts = [
    args.prevHash ?? '',
    args.ts,
    args.agentId,
    args.actionType,
    args.rawLineHash,
    args.sourceFingerprint,
  ];
  return sha256Text(parts.join('|'));
}

// ─── signing + verification ─────────────────────────────────────────────

export function signHash(hashHex: string, privateKeyPem: string): string {
  // Ed25519 signs raw bytes (no pre-hash). We sign the hex string directly
  // so that verifiers only need the hex hash (which is in the row).
  const sig = edSign(null, Buffer.from(hashHex, 'utf8'), privateKeyPem);
  return bufToBase64Url(sig);
}

export function verifySignature(
  hashHex: string,
  signatureBase64Url: string,
  publicKeyBase64Url: string,
): boolean {
  const sigBytes = base64UrlToBuf(signatureBase64Url);
  const pubBytes = base64UrlToBuf(publicKeyBase64Url);
  // Reconstruct an Ed25519 SPKI key from raw 32-byte public key
  const spkiPrefix = Buffer.from([
    0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65,
    0x70, 0x03, 0x21, 0x00,
  ]);
  const spki = Buffer.concat([spkiPrefix, pubBytes]);
  const pubKey = createPublicKey({
    key: spki,
    format: 'der',
    type: 'spki',
  });
  return edVerify(null, Buffer.from(hashHex, 'utf8'), pubKey, sigBytes);
}

// ─── high-level helper ──────────────────────────────────────────────────

/**
 * Build a fully signed SignedAction row, ready to insert into
 * `agent_actions_ledger`. Does NOT do the insert (to keep this lib
 * Supabase-agnostic). Caller wraps with their own DB client.
 *
 * Approval level defaults to DEFAULT_APPROVAL_LEVELS[actionType] but
 * can be overridden. L2 actions return with `approved_by: null` —
 * they should be inserted but treated as PROPOSED, not executed,
 * until a human sets approved_by.
 */
export function buildSignedAction(opts: SignAndAppendOptions): SignedAction {
  const ts = opts.ts ?? new Date().toISOString().replace(/\.\d{3}Z$/, 'Z');
  const audit = buildAuditFields({
    rawRow: opts.payload,
    sourceUrl: opts.sourceUrl,
    method: opts.sourceMethod,
    collectedAt: ts,
  });
  const hash = computeActionHash({
    prevHash: opts.prevHash ?? null,
    ts,
    agentId: opts.agentId,
    actionType: opts.actionType,
    rawLineHash: audit.raw_line_hash,
    sourceFingerprint: audit.source_fingerprint,
  });
  const signature = signHash(hash, opts.privateKeyPem);
  const approvalLevel = opts.approvalLevel ?? DEFAULT_APPROVAL_LEVELS[opts.actionType];
  return {
    ...audit,
    ts,
    agent_id: opts.agentId,
    action_type: opts.actionType,
    approval_level: approvalLevel,
    payload: opts.payload,
    prev_hash: opts.prevHash ?? null,
    hash,
    signature,
    approved_by: approvalLevel === 'L2' ? null : opts.agentId,
    correlation_id: opts.correlationId,
  };
}

/**
 * Verify a SignedAction's hash chain link AND signature.
 *
 * - Recomputes the hash from the row's fields and the supplied prev_hash
 * - Verifies the Ed25519 signature against the agent's public key
 *
 * Returns true only if BOTH check out.
 */
export function verifySignedAction(
  action: SignedAction,
  publicKeyBase64Url: string,
): boolean {
  const expectedHash = computeActionHash({
    prevHash: action.prev_hash,
    ts: action.ts,
    agentId: action.agent_id,
    actionType: action.action_type,
    rawLineHash: action.raw_line_hash,
    sourceFingerprint: action.source_fingerprint,
  });
  if (expectedHash !== action.hash) return false;
  return verifySignature(action.hash, action.signature, publicKeyBase64Url);
}

// ─── helpers ────────────────────────────────────────────────────────────

function bufToBase64Url(buf: Buffer | Uint8Array): string {
  return Buffer.from(buf)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function base64UrlToBuf(s: string): Buffer {
  const pad = s.length % 4 === 0 ? '' : '='.repeat(4 - (s.length % 4));
  return Buffer.from(s.replace(/-/g, '+').replace(/_/g, '/') + pad, 'base64');
}

// silence unused-import warning if a consumer doesn't tree-shake
export { createSign, createVerify };

/**
 * Provenance — non-repudiation metadata for ETL pipelines.
 * Ported from br-acc/etl/src/bracc_etl/provenance.py (BRACC-001).
 *
 * Provides SHA-256 based proof-of-research hashes for data rows
 * and deterministic source fingerprints.
 */

import { createHash } from "crypto";

type JsonPrimitive = string | number | boolean | null;
type JsonValue = JsonPrimitive | JsonObject | JsonArray;
type JsonObject = { [key: string]: JsonValue };
type JsonArray = JsonValue[];

/** Normalize a value into a deterministic JSON-serializable structure. */
function normalize(value: unknown): JsonValue {
  if (value === null || value === undefined) return null;
  if (value instanceof Date) {
    return value.toISOString().replace("+00:00", "Z");
  }
  if (Array.isArray(value)) {
    return value.map(normalize);
  }
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    return Object.fromEntries(
      Object.entries(obj)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => [k, normalize(v)])
    );
  }
  return value as JsonPrimitive;
}

/** Return stable JSON representation for hashing raw rows. */
export function canonicalRowJson(row: Record<string, unknown>): string {
  return JSON.stringify(normalize(row), null, 0);
}

/** Return hex SHA-256 for a text value. */
export function sha256Text(value: string): string {
  return createHash("sha256").update(value, "utf8").digest("hex");
}

/** Compute a non-repudiation hash for a raw row payload. */
export function rawRowHash(row: Record<string, unknown>): string {
  return sha256Text(canonicalRowJson(row));
}

/** Compute deterministic fingerprint for a data source snapshot. */
export function sourceFingerprint(sourceUrl: string, method: string, collectedAt: string): string {
  const payload = `${sourceUrl.trim()}|${method.trim()}|${collectedAt.trim()}`;
  return sha256Text(payload);
}

export interface AuditFields {
  raw_line_hash: string;
  source_url: string;
  source_method: string;
  verified_at: string;
  audit_status: "verified";
  source_fingerprint: string;
}

/**
 * Build audit metadata to attach to transformed nodes/relationships.
 * Drop-in compatible with the Python version's output shape.
 */
export function buildAuditFields(params: {
  rawRow: Record<string, unknown>;
  sourceUrl: string;
  method: string;
  collectedAt?: string;
}): AuditFields {
  const verifiedAt =
    params.collectedAt ?? new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
  return {
    raw_line_hash: rawRowHash(params.rawRow),
    source_url: params.sourceUrl.trim(),
    source_method: params.method.trim() || "unknown",
    verified_at: verifiedAt,
    audit_status: "verified",
    source_fingerprint: sourceFingerprint(params.sourceUrl, params.method, verifiedAt),
  };
}

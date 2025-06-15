---
title: Validator Audit Logging
status: Draft
version: 0.1.0
---

@references:
  - docs/validator/AUDIT_LOGGING.md

## SQLite Schema
```sql
CREATE TABLE validator_runs (
  validation_id TEXT PRIMARY KEY,
  timestamp_utc TEXT,
  passed INTEGER,
  overall_score REAL,
  request_json TEXT,
  response_json TEXT
);
```
Retention: 90 days → cron job purges older.

## Dashboard Query Example
```sql
SELECT strftime('%Y-%m-%d', timestamp_utc) AS day,
       COUNT(*) AS runs,
       SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) AS fails
FROM validator_runs GROUP BY day ORDER BY day DESC LIMIT 30;
```
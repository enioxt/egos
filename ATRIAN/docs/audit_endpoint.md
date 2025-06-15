@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - ATRIAN/docs/audit_endpoint.md

# ATRiAN EaaS API - Audit Endpoint Documentation

## Overview

The `/ethics/audit` endpoint provides a comprehensive auditing capability for the ATRiAN Ethics as a Service (EaaS) API. This endpoint allows authorized users to retrieve detailed logs of all API operations, supporting filtering and pagination to efficiently access the information needed.

This documentation aligns with the ATRiAN EaaS API v0.3.0 and follows the EGOS documentation standards.

## Endpoint Details

- **URL**: `/ethics/audit`
- **Method**: GET
- **Response Model**: `EthicsAuditResponse`
- **Tags**: Audit

## Request Parameters

| Parameter   | Type                | Required | Default | Description                                                    |
|-------------|---------------------|----------|---------|----------------------------------------------------------------|
| start_date  | datetime (ISO 8601) | No       | None    | Filter logs from this date/time                                |
| end_date    | datetime (ISO 8601) | No       | None    | Filter logs until this date/time                               |
| action_type | string              | No       | None    | Filter by action type (e.g., evaluate, explain, suggest)       |
| user_id     | string              | No       | None    | Filter by user ID                                              |
| limit       | integer             | No       | 100     | Maximum number of logs to return                               |
| offset      | integer             | No       | 0       | Number of logs to skip for pagination                          |

## Response Structure

The endpoint returns an `EthicsAuditResponse` object with the following fields:

| Field       | Type                | Description                                                 |
|-------------|---------------------|-------------------------------------------------------------|
| logs        | array of AuditLogEntry | The audit log entries matching the query parameters      |
| total_count | integer             | The total number of logs in the current response            |
| page        | integer             | The current page number (calculated from offset and limit)  |
| page_size   | integer             | The number of items per page (same as the limit parameter)  |
| has_more    | boolean             | Indicates if there are more logs beyond the current response|

### AuditLogEntry Structure

Each audit log entry contains:

| Field            | Type                | Description                                          |
|------------------|---------------------|------------------------------------------------------|
| log_id           | string              | Unique identifier for the log entry                  |
| timestamp        | datetime (ISO 8601) | When the action occurred                             |
| action_type      | string              | Type of action (e.g., evaluate, explain, suggest)    |
| endpoint_called  | string              | The API endpoint that was called                      |
| user_id          | string              | Identifier of the user who performed the action      |
| request_summary  | object              | Summary of the request parameters                    |
| response_summary | object              | Summary of the response                              |
| resource_id      | string (optional)   | ID of the resource being accessed (if applicable)    |
| metadata         | object (optional)   | Additional contextual information                    |

## Meta-Auditing

An important feature of the audit endpoint is that it logs its own usage. When the `/ethics/audit` endpoint is called, it creates a new audit log entry with:
- `action_type`: "retrieve_audit_logs"
- `endpoint_called`: "/ethics/audit"
- `request_summary`: Contains all filter parameters used

This ensures complete traceability of who accessed audit information and what filters they applied.

## Pagination

The audit endpoint supports pagination through the `limit` and `offset` parameters:

- `limit`: Controls how many log entries to return in a single response
- `offset`: Specifies how many log entries to skip before starting to return results

The response includes:
- `page`: Calculated as `(offset // limit) + 1`
- `page_size`: Same as the `limit` parameter
- `has_more`: `true` if the number of returned logs equals the limit (indicating there may be more logs to retrieve)

## Usage Examples

### Basic Retrieval

```http
GET /ethics/audit
```

Retrieves the most recent 100 audit log entries.

### Filtered Retrieval

```http
GET /ethics/audit?action_type=evaluate_ethics&limit=10&offset=0
```

Retrieves the 10 most recent audit logs for ethical evaluations.

### Date Range Filtering

```http
GET /ethics/audit?start_date=2025-05-01T00:00:00Z&end_date=2025-05-31T23:59:59Z
```

Retrieves audit logs from May 2025.

## Implementation Notes

- The audit endpoint is implemented in `eaas_api.py` and uses the `EaasPersistenceManager` to retrieve logs.
- Logs are stored in the location specified by the `ATRIAN_DATA_DIR` environment variable (default: `C:/EGOS/ATRiAN/data`).
- The endpoint handles exceptions gracefully, returning appropriate HTTP error codes and messages.

## Security Considerations

- In the current implementation, user authentication is mocked as "anonymous".
- In a production environment, this endpoint should be secured with proper authentication and authorization.
- Access to audit logs should be restricted to authorized personnel only.

## Testing

The audit endpoint can be tested using the `test_all_endpoints.ps1` script, which includes specific tests for the audit functionality with various filtering parameters.

---

*This documentation follows the EGOS documentation standards and aligns with the ATRiAN Ethics as a Service (EaaS) API v0.3.0.*
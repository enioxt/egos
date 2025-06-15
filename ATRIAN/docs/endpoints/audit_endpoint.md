@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - ATRIAN/docs/api_overview.md
  - ATRIAN/docs/architecture/audit_system.md
  - ATRIAN/docs/operations/performance_monitoring.md







  - ATRIAN/docs/endpoints/audit_endpoint.md

# ATRiAN EaaS API: Audit Endpoint Documentation

## Overview

The `/ethics/audit` endpoint provides access to the ATRiAN Ethics as a Service (EaaS) audit log system. This endpoint allows authorized users to retrieve, filter, and paginate through audit logs that track all actions performed within the ATRiAN system.

## Endpoint Details

- **URL**: `/ethics/audit`
- **Method**: `GET`
- **Base URL**: `http://127.0.0.1:8000` (development environment)
- **Authentication**: Required (implementation details to be added)

## Query Parameters

| Parameter    | Type    | Required | Default | Description |
|--------------|---------|----------|---------|-------------|
| `limit`      | integer | No       | 100     | Maximum number of records to return (1-1000) |
| `offset`     | integer | No       | 0       | Number of records to skip for pagination |
| `user_id`    | string  | No       | None    | Filter logs by user identifier |
| `action_type`| string  | No       | None    | Filter logs by action type (e.g., "retrieve_audit_logs", "framework_evaluation") |
| `start_date` | string  | No       | None    | Filter logs with timestamp after this date (ISO format: YYYY-MM-DD) |
| `end_date`   | string  | No       | None    | Filter logs with timestamp before this date (ISO format: YYYY-MM-DD) |

## Response Format

```json
{
  "status": "success",
  "total_count": 235,
  "returned_count": 100,
  "offset": 0,
  "limit": 100,
  "logs": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "timestamp": "2025-06-01T14:23:45.123456",
      "user_id": "user_12345",
      "action_type": "framework_evaluation",
      "details": {
        "framework_id": "ethics_framework_1",
        "input_text": "Should AI systems be allowed to make autonomous decisions?",
        "score": 0.85
      },
      "metadata": {
        "client_ip": "127.0.0.1",
        "user_agent": "Mozilla/5.0 ..."
      }
    },
    // Additional log entries...
  ]
}
```

## Response Fields

| Field           | Type    | Description |
|-----------------|---------|-------------|
| `status`        | string  | Response status ("success" or "error") |
| `total_count`   | integer | Total number of logs matching the query |
| `returned_count`| integer | Number of logs returned in this response |
| `offset`        | integer | Current offset value used |
| `limit`         | integer | Current limit value used |
| `logs`          | array   | Array of audit log entries |

### Log Entry Fields

| Field        | Type    | Description |
|--------------|---------|-------------|
| `id`         | string  | Unique identifier for the log entry (UUID) |
| `timestamp`  | string  | ISO 8601 formatted date and time when the action occurred |
| `user_id`    | string  | Identifier of the user who performed the action |
| `action_type`| string  | Type of action performed |
| `details`    | object  | Action-specific details (varies by action_type) |
| `metadata`   | object  | Additional contextual information about the request |

## Common Action Types

- `retrieve_audit_logs`: Access to audit logs was requested
- `framework_evaluation`: An ethics framework evaluation was performed
- `framework_update`: An ethics framework was updated
- `user_authentication`: User login or authentication event
- `permission_change`: User permissions were modified
- `system_error`: System encountered an error during operation

## Error Responses

### Invalid Parameters

```json
{
  "status": "error",
  "error": "invalid_parameters",
  "message": "Invalid limit value. Must be between 1 and 1000.",
  "details": {
    "parameter": "limit",
    "value": "2000",
    "constraint": "1-1000"
  }
}
```

### Server Error

```json
{
  "status": "error",
  "error": "server_error",
  "message": "An unexpected error occurred while processing your request."
}
```

## Performance Considerations

- Response times increase with larger `limit` values
- Filtering by `action_type` and `user_id` provides the most efficient queries
- Date range filtering (`start_date` and `end_date`) may impact performance with large date ranges
- For optimal performance, use a combination of filters and reasonable pagination values

## Examples

### Basic Request

```
GET /ethics/audit
```

### Pagination Example

```
GET /ethics/audit?limit=50&offset=100
```

### Filtering by User and Action Type

```
GET /ethics/audit?user_id=admin_user&action_type=framework_update
```

### Date Range Filtering

```
GET /ethics/audit?start_date=2025-05-01&end_date=2025-05-31
```

### Combined Filtering with Pagination

```
GET /ethics/audit?limit=25&offset=50&action_type=framework_evaluation&start_date=2025-06-01
```

## Testing

The audit endpoint has been thoroughly tested using automated scripts:

1. **Basic Functionality Tests**: `test_audit_endpoint.ps1` in the `tests` directory verifies basic functionality, parameter handling, and response formatting.

2. **Performance Monitoring**: `audit_performance_monitor.py` in the `tools` directory provides detailed performance metrics and recommendations.

## Known Issues and Limitations

- Some audit log files may be corrupted, resulting in JSON decode errors (under investigation)
- Response times may be high (~2100ms) for queries with large result sets
- Maximum limit value is capped at 1000 records per request

## Future Enhancements

- Implementation of response caching for improved performance
- Addition of more granular filtering options
- Support for sorting by different fields
- Implementation of audit log compression for older entries

## Related Documentation

- [ATRiAN EaaS API Overview](../api_overview.md)
- [Audit System Architecture](../architecture/audit_system.md)
- [Performance Monitoring Guide](../operations/performance_monitoring.md)

---

*Last Updated: 2025-06-03*  
*Document Version: 1.0*
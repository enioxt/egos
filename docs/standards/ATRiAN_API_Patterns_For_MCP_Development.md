---
title: "ATRiAN API Patterns for MCP Development"
version: "1.0.0"
date: "2025-06-02"
author: "Cascade (AI Assistant)"
status: "Draft"
tags: ["API", "MCP", "ATRiAN", "standards", "patterns", "FastAPI", "EaaS"]
references: [
  "C:\\EGOS\\ATRiAN\\eaas_api.py",
  "C:\\EGOS\\ATRiAN\\eaas_models.py",
  "C:\\EGOS\\ATRiAN\\eaas_persistence.py",
  "C:\\EGOS\\docs\\guides\\MCP_CREATION_GUIDE.md",
  "C:\\EGOS\\EGOS_Framework\\docs\\standards\\EGOS_MCP_Standardization_Guidelines.md",
  "C:\\EGOS\\docs\\core_materials\\standards\\MCP_Testing_Framework.md",
  "C:\\EGOS\\EGOS_Framework\\docs\\03_MCP_Subsystem.md"
]
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - docs/standards/ATRiAN_API_Patterns_For_MCP_Development.md

# ATRiAN API Patterns for MCP Development

## 1. Executive Summary

This document identifies and standardizes the successful API development patterns used in the ATRiAN Ethics as a Service (EaaS) API implementation. These patterns align with EGOS Model-Context-Protocol (MCP) standards and can be reused across other EGOS subsystems to ensure consistency, quality, and interoperability. By leveraging the ATRiAN API approach, future MCP implementations can benefit from a proven, functional architecture that embodies EGOS principles.

## 2. Core Architectural Patterns

### 2.1. Three-Tier Architecture

The ATRiAN EaaS API implements a clear three-tier architecture that separates concerns and promotes maintainability:

1. **API Layer** (`eaas_api.py`):
   - Defines endpoints and routing
   - Handles HTTP requests/responses
   - Implements input validation
   - Manages error handling
   - Documents API behavior

2. **Data Model Layer** (`eaas_models.py`):
   - Defines Pydantic models for requests and responses
   - Implements data validation
   - Provides clear type annotations
   - Establishes the data contract between clients and the API

3. **Persistence Layer** (`eaas_persistence.py`):
   - Manages data storage and retrieval
   - Abstracts storage implementation details
   - Handles data format conversions
   - Implements logging and audit trails

This separation allows each layer to evolve independently while maintaining clear interfaces between them.

### 2.2. Technology Stack

The ATRiAN EaaS API uses a modern, efficient technology stack that can be replicated for MCP development:

| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | FastAPI | High-performance API with automatic OpenAPI documentation |
| Data Validation | Pydantic | Type-safe request/response validation |
| Data Storage | JSON/YAML files | Simple, human-readable data persistence |
| Documentation | OpenAPI/Swagger | Interactive API documentation |
| Testing | pytest, PowerShell scripts | Comprehensive test coverage |
| Monitoring | Dash/Plotly | Performance visualization and analysis |

### 2.3. Dependency Injection Pattern

The ATRiAN API makes extensive use of FastAPI's dependency injection system, particularly for the persistence manager:

```python
# Define a dependency
def get_persistence():
    persistence_mgr = EaasPersistenceManager(DATA_DIR)
    return persistence_mgr

# Use the dependency in endpoints
@app.get("/ethics/audit", response_model=EthicsAuditResponse)
def get_audit_logs(
    persistence_mgr: EaasPersistenceManager = Depends(get_persistence)
):
    # Use persistence_mgr within the endpoint
```

This pattern promotes:
- Testability through mocking
- Separation of concerns
- Consistent resource management
- Reduced code duplication

## 3. API Design Patterns

### 3.1. Request/Response Model Pattern

The ATRiAN API defines clear Pydantic models for all requests and responses:

1. **Request Models:**
   - Explicit field definitions with type annotations
   - Field descriptions for documentation
   - Default values where appropriate
   - Validation rules

2. **Response Models:**
   - Consistent structure
   - Clear typing for all fields
   - Optional fields marked appropriately
   - Nested models for complex data

Example from `eaas_models.py`:

```python
class EthicsEvaluationRequest(BaseModel):
    action: str = Field(..., description="The action to be evaluated.")
    context: EthicsEvaluationRequestContext = Field(..., description="Contextual information.")
    options: Optional[EthicsEvaluationOptions] = Field(None, description="Evaluation options.")

class EthicsEvaluationResult(BaseModel):
    evaluation_id: Optional[str] = Field(None, description="Unique ID for this evaluation.")
    ethical_score: Optional[float] = Field(None, description="An overall ethical score, if applicable.")
    compliant: bool = Field(..., description="Whether the action is deemed compliant.")
    concerns: List[EthicalConcern] = Field(..., description="List of identified ethical concerns.")
    recommendations: List[EthicalRecommendation] = Field(..., description="List of recommendations.")
```

### 3.2. Endpoint Organization Pattern

The ATRiAN API groups endpoints by function, following RESTful principles:

1. **Evaluation Endpoints**:
   - `/ethics/evaluate` - Evaluate ethical implications
   - `/ethics/explain` - Explain evaluation results
   - `/ethics/suggest` - Suggest ethical alternatives

2. **Framework Management Endpoints**:
   - `/frameworks` - List, create frameworks
   - `/frameworks/{framework_id}` - Get, update, delete specific frameworks

3. **Audit Endpoints**:
   - `/ethics/audit` - Access audit logs with filtering

Each endpoint includes:
- Clear route definitions
- Appropriate HTTP methods (GET, POST, PUT, DELETE)
- Comprehensive parameter documentation
- Proper response status codes
- Error handling

### 3.3. Error Handling Pattern

The ATRiAN API implements consistent error handling:

```python
try:
    # Operation that might fail
    result = persistence_mgr.get_evaluation(evaluation_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation with ID {evaluation_id} not found"
        )
    
    # Process successful result
    return result
    
except Exception as e:
    logger.error(f"Error retrieving evaluation: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(e)}"
    )
```

Key aspects:
- HTTP status codes match error types
- Detailed error messages for debugging
- Logging of errors for monitoring
- Custom error types where needed

## 4. Persistence Patterns

### 4.1. Manager Class Pattern

The `EaasPersistenceManager` class encapsulates all data operations:

```python
class EaasPersistenceManager:
    """Manages persistence for the Ethics as a Service (EaaS) API."""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.frameworks_dir = os.path.join(data_dir, "frameworks")
        self.evaluations_dir = os.path.join(data_dir, "evaluations")
        self.audit_dir = os.path.join(data_dir, "audit")
        # Ensure directories exist
        os.makedirs(self.frameworks_dir, exist_ok=True)
        os.makedirs(self.evaluations_dir, exist_ok=True)
        os.makedirs(self.audit_dir, exist_ok=True)
```

Benefits:
- Centralizes data access logic
- Simplifies testing through mocking
- Provides consistent error handling
- Enables future storage backend changes

### 4.2. File-Based Storage Pattern

For simplicity and human readability, ATRiAN uses file-based storage:

```python
def save_evaluation(self, evaluation: EthicsEvaluationResult) -> None:
    """Save an evaluation result to persistent storage."""
    evaluation_id = evaluation.evaluation_id
    file_path = os.path.join(self.evaluations_dir, f"{evaluation_id}.json")
    
    with open(file_path, 'w') as f:
        f.write(evaluation.json(indent=2))
```

This approach:
- Maintains human-readable data
- Simplifies debugging and inspection
- Avoids database setup complexity
- Works well for development and testing

### 4.3. Audit Logging Pattern

Comprehensive audit logging is implemented:

```python
def log_audit_entry(self, entry: AuditLogEntry) -> None:
    """Add an audit log entry to the audit log."""
    # Generate a timestamp-based filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(self.audit_dir, f"audit_log_{date_str}.json")
    
    # Append to existing log or create new
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
                logs.append(entry.dict())
        else:
            logs = [entry.dict()]
            
        with open(log_file, 'w') as f:
            json.dump(logs, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error logging audit entry: {str(e)}")
```

Features:
- Date-based log files for organization
- Structured JSON format for machine processing
- Comprehensive entry details
- Error handling to prevent lost audit events

## 5. Testing Patterns

### 5.1. Multi-Level Testing Approach

The ATRiAN API implements testing at multiple levels:

1. **Unit Tests** (Python pytest):
   - Test individual functions and methods
   - Mock dependencies for isolation
   - Focus on specific functionality

2. **Integration Tests** (Python pytest):
   - Test API endpoints with simulated requests
   - Verify correct interaction between components
   - Test error handling paths

3. **End-to-End Tests** (PowerShell scripts):
   - Test the full system through the HTTP interface
   - Verify expected responses to real requests
   - Test performance and reliability

### 5.2. Test Fixtures and Factories

Test data is managed through fixtures:

```python
@pytest.fixture
def sample_evaluation_request():
    """Create a sample evaluation request for testing."""
    return {
        "action": "Deploy a facial recognition system in a public space",
        "context": {
            "domain": "surveillance",
            "purpose": "Security monitoring",
            "stakeholders": ["public", "security personnel", "government"]
        },
        "options": {
            "detail_level": "comprehensive",
            "include_alternatives": True
        }
    }
```

This provides:
- Consistent test data
- Reusability across tests
- Clear test case definitions
- Easy modification of test scenarios

### 5.3. Performance Monitoring Pattern

Performance testing and monitoring uses Dash/Plotly:

```python
def run_performance_test(endpoint, test_case, iterations=100):
    """Run a performance test against the specified endpoint."""
    results = []
    for i in range(iterations):
        start_time = time.time()
        response = requests.post(f"http://localhost:8000{endpoint}", json=test_case)
        end_time = time.time()
        
        results.append({
            "iteration": i,
            "status_code": response.status_code,
            "response_time": (end_time - start_time) * 1000,  # ms
            "success": response.status_code == 200
        })
    
    return results
```

This approach:
- Measures response times
- Tracks success rates
- Identifies performance issues
- Provides visualizations for analysis

## 6. Documentation Patterns

### 6.1. Code Documentation Pattern

ATRiAN uses comprehensive docstrings:

```python
@app.post("/ethics/evaluate", response_model=EthicsEvaluationResult)
def evaluate_ethics(
    request: EthicsEvaluationRequest,
    persistence_mgr: EaasPersistenceManager = Depends(get_persistence)
):
    """
    Evaluates the ethical implications of a given action or decision.
    
    Parameters:
    - request: The evaluation request containing the action and context
    
    Returns:
    - EthicsEvaluationResult containing the ethical assessment
    
    Raises:
    - HTTPException(400): If the request is invalid
    - HTTPException(500): If there's a server error during evaluation
    """
```

Key aspects:
- Purpose description
- Parameter documentation
- Return value specification
- Exception documentation
- Usage examples where appropriate

### 6.2. OpenAPI Integration Pattern

FastAPI automatically generates OpenAPI documentation:

```python
# Initialize FastAPI app with metadata for documentation
app = FastAPI(
    title="ATRiAN Ethics as a Service API",
    description="API for ethical evaluation, explanation, and suggestions",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

This provides:
- Interactive Swagger UI
- ReDoc alternative documentation
- Machine-readable API schema
- Automatic request/response validation

## 7. Alignment with MCP Standards

The ATRiAN API patterns align well with EGOS MCP Standardization Guidelines:

| MCP Standard | ATRiAN Implementation |
|--------------|----------------------|
| OpenAPI Specification | Automatic generation via FastAPI |
| Comprehensive `info` Object | Metadata in FastAPI initialization |
| Detailed `paths` and `operations` | Well-documented routes and handlers |
| Precise `parameters` Definition | Pydantic models with Field descriptions |
| Well-Defined `requestBody` | Type-annotated request models |
| Comprehensive `responses` | Explicit response models and status codes |
| Reusable `components` | Shared Pydantic models |
| Authentication/Authorization | Basic implementation with tokens |
| Error Standardization | Consistent HTTPException usage |
| Logging & Monitoring | Built-in logging and audit system |
| ETHIK Compliance | Ethics-focused API with audit capability |

## 8. Implementation Guide for New MCPs

To create a new MCP following the ATRiAN patterns:

### 8.1. Project Structure

```
/my_mcp/
  ├── mcp_api.py           # FastAPI application and endpoints
  ├── mcp_models.py        # Pydantic models for requests/responses
  ├── mcp_persistence.py   # Data persistence layer
  ├── requirements.txt     # Dependencies
  ├── README.md            # Documentation
  ├── /tests/              # Test files
  │    ├── test_api.py     # API tests
  │    ├── test_models.py  # Model tests
  │    └── fixtures/       # Test data
  ├── /data/               # Data storage
  │    ├── /audit/         # Audit logs
  │    └── /resources/     # Other resources
  └── /tools/              # Utility tools and scripts
       ├── performance_monitor.py
       └── data_repair.py
```

### 8.2. Implementation Steps

1. **Define Models**:
   - Create Pydantic models for all requests and responses
   - Document fields with descriptions
   - Define validation rules

2. **Implement Persistence**:
   - Create a manager class for data operations
   - Define storage locations and formats
   - Implement CRUD operations
   - Add audit logging

3. **Create API Endpoints**:
   - Initialize FastAPI application
   - Define routes with appropriate HTTP methods
   - Implement request validation
   - Use dependency injection for persistence
   - Document with comprehensive docstrings

4. **Develop Tests**:
   - Create test fixtures
   - Write unit tests for each component
   - Implement integration tests
   - Create end-to-end tests

5. **Add Documentation**:
   - Update README.md with usage instructions
   - Document API endpoints and models
   - Include examples

6. **Create Utility Tools**:
   - Add performance monitoring
   - Create data repair tools if needed
   - Implement admin utilities

## 9. Conclusion

The ATRiAN EaaS API implementation provides a robust, proven pattern for developing MCPs within the EGOS ecosystem. By following these patterns, teams can create consistent, maintainable, and well-documented MCPs that align with EGOS standards and principles. This approach promotes code reuse, reduces development time, and ensures a high quality standard across all EGOS subsystems.

---

## Appendix A: Key Technologies

| Technology | Version | Purpose | Documentation |
|------------|---------|---------|---------------|
| FastAPI | 0.95.0+ | Web framework for APIs | [FastAPI Docs](https://fastapi.tiangolo.com/) |
| Pydantic | 1.10.0+ | Data validation and settings management | [Pydantic Docs](https://docs.pydantic.dev/) |
| Uvicorn | 0.17.0+ | ASGI server for FastAPI | [Uvicorn Docs](https://www.uvicorn.org/) |
| pytest | 7.0.0+ | Testing framework | [pytest Docs](https://docs.pytest.org/) |
| Dash/Plotly | 2.5.0+ | Interactive visualization | [Dash Docs](https://dash.plotly.com/) |
| PowerShell | 7.0+ | Scripting for E2E testing | [PowerShell Docs](https://docs.microsoft.com/en-us/powershell/) |

## Appendix B: Example Code Templates

### B.1. Basic MCP API Template

```python
# mcp_api.py
from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
import logging
from datetime import datetime

# Import models and persistence
from mcp_models import RequestModel, ResponseModel, ErrorResponse
from mcp_persistence import MCPPersistenceManager

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Initialize FastAPI app
app = FastAPI(
    title="My MCP Server",
    description="Description of the MCP server's purpose and capabilities",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Data directory
DATA_DIR = "./data"

# Dependency for persistence
def get_persistence():
    persistence_mgr = MCPPersistenceManager(DATA_DIR)
    return persistence_mgr

@app.post("/execute", response_model=ResponseModel)
def execute_operation(
    request: RequestModel,
    persistence_mgr: MCPPersistenceManager = Depends(get_persistence)
):
    """
    Execute the primary operation of this MCP.
    
    Parameters:
    - request: The operation request
    
    Returns:
    - ResponseModel containing the operation result
    """
    try:
        # Log the request
        persistence_mgr.log_request(request)
        
        # Process the request
        # ...
        
        # Create response
        response = ResponseModel(
            id="operation-123",
            result="Operation completed successfully",
            timestamp=datetime.now()
        )
        
        # Log the response
        persistence_mgr.log_response(response)
        
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/status")
def get_status():
    """Get the current status of the MCP server."""
    return {
        "status": "operational",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### B.2. Models Template

```python
# mcp_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RequestModel(BaseModel):
    """Model for the main operation request."""
    operation: str = Field(..., description="The operation to perform.")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the operation.")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context.")

class ResponseModel(BaseModel):
    """Model for the operation response."""
    id: str = Field(..., description="Unique identifier for this operation.")
    result: Any = Field(..., description="Result of the operation.")
    timestamp: datetime = Field(..., description="When the operation was performed.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata.")

class ErrorResponse(BaseModel):
    """Model for error responses."""
    error_code: str = Field(..., description="Error code.")
    message: str = Field(..., description="Error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details.")
```

### B.3. Persistence Template

```python
# mcp_persistence.py
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MCPPersistenceManager:
    """Manages persistence for the MCP server."""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.logs_dir = os.path.join(data_dir, "logs")
        self.resources_dir = os.path.join(data_dir, "resources")
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.resources_dir, exist_ok=True)
    
    def log_request(self, request):
        """Log an incoming request."""
        self._log_entry("request", request.dict())
    
    def log_response(self, response):
        """Log an outgoing response."""
        self._log_entry("response", response.dict())
    
    def _log_entry(self, entry_type, data):
        """Internal method to log an entry."""
        try:
            # Generate a timestamp-based filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.logs_dir, f"{entry_type}_log_{date_str}.json")
            
            # Prepare log entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": entry_type,
                "data": data
            }
            
            # Append to existing log or create new
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    logs.append(entry)
            else:
                logs = [entry]
                
            with open(log_file, 'w') as f:
                json.dump(logs, indent=2, default=str, f)
        except Exception as e:
            logger.error(f"Error logging {entry_type}: {str(e)}")
```
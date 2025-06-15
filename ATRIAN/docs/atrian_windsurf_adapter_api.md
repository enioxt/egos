---
title: ATRiANWindsurfAdapter API Reference
description: Detailed API documentation for the ATRiANWindsurfAdapter class
created: 2025-05-27
updated: 2025-05-27
author: EGOS Development Team
version: 1.0
status: Active
tags: atrian, windsurf, integration, api, reference, adapter
---

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - ATRIAN/WORK_2025-05-27_ATRiAN_Windsurf_Integration.md
  - ATRIAN/docs/windsurf_integration_guide.md
  - ATRiAN/ATRiAN.md








  - ATRIAN/docs/atrian_windsurf_adapter_api.md

# ATRiANWindsurfAdapter API Reference

**Version:** 1.0  
**Last Updated:** 2025-05-27  
**Primary References:**
- [ATRiAN Module - The Silent Guide](../../ATRiAN/ATRiAN.md)
- [ATRiAN Windsurf Integration Guide](./windsurf_integration_guide.md)
- [WORK_2025-05-27_ATRiAN_Windsurf_Integration.md](../WORK_2025-05-27_ATRiAN_Windsurf_Integration.md)
- [Master Quantum Prompt (MQP.md)](../../MQP.md)

## 1. Overview

The `ATRiANWindsurfAdapter` class serves as the primary integration point between ATRiAN ethical intelligence components and the Windsurf IDE. It provides methods for operation evaluation, notification generation, and adaptive interface recommendations.

This adapter follows the EGOS principles of Conscious Modularity (CM) by creating a clean separation between ATRiAN's internal implementation and Windsurf's integration points.

## 2. Class Definition

```python
class ATRiANWindsurfAdapter:
    """
    Adapter for integrating ATRiAN ethical intelligence with Windsurf IDE.
    
    This class provides methods for evaluating Windsurf operations for ethical
    considerations, generating appropriate notifications, and recommending
    adaptive interface changes based on trust levels.
    
    Attributes:
        ethical_compass (EthicalCompass): The ethical compass component
        trust_weaver (WeaverOfTrust): The trust weaver component
        ethics_trust (EthicsTrustIntegration): Integration of ethics and trust
        silent_guide (SilentGuide): The silent guide component
    """
```

## 3. Constructor

```python
def __init__(self, config_path: Optional[str] = None):
    """
    Initialize the ATRiANWindsurfAdapter.
    
    Args:
        config_path (str, optional): Path to configuration file.
            If not provided, defaults to standard location.
    
    Raises:
        FileNotFoundError: If the config file cannot be found
        ValueError: If the config file contains invalid settings
    """
```

## 4. Public Methods

### 4.1 evaluate_operation

```python
def evaluate_operation(self, operation_type: WindsurfOperationType, 
                      context: Dict[str, Any], user_id: str = "User") -> Dict[str, Any]:
    """
    Evaluate a Windsurf operation using ATRiAN components.
    
    This method evaluates the ethical implications and trust boundaries
    of a Windsurf operation, providing guidance and determining if the
    operation should be allowed.
    
    Args:
        operation_type (WindsurfOperationType): Type of operation being performed
        context (Dict[str, Any]): Context information about the operation
        user_id (str, optional): Identifier for the user performing the operation
    
    Returns:
        Dict[str, Any]: Evaluation results containing:
            - operation_id (str): Unique identifier for this operation
            - user_id (str): User who performed the operation
            - operation_type (str): Type of operation performed
            - timestamp (str): ISO 8601 timestamp
            - allowed (bool): Whether the operation is allowed
            - trust_score (float): Current trust score for the user
            - ethical_evaluation (Dict): Details of ethical evaluation
            - contains_sensitive_data (bool): Whether sensitive data was detected
            - detected_keywords (List[str]): Detected privacy-sensitive keywords
            - should_notify (bool): Whether notification should be shown
    
    Raises:
        ValueError: If operation_type is not a valid WindsurfOperationType
        RuntimeError: If evaluation components fail
    """
```

### 4.2 generate_notification

```python
def generate_notification(self, operation_id: str) -> Dict[str, Any]:
    """
    Generate a notification for a previously evaluated operation.
    
    This method creates a user-facing notification based on the ethical
    evaluation and trust assessment of a previously processed operation.
    
    Args:
        operation_id (str): ID of the operation to generate notification for
    
    Returns:
        Dict[str, Any]: Notification information containing:
            - notification_id (str): Unique identifier for this notification
            - type (str): Notification type (info, warning, critical)
            - title (str): Notification title
            - message (str): Detailed notification message
            - operation_id (str): ID of the related operation
            - timestamp (str): ISO 8601 timestamp
    
    Raises:
        KeyError: If operation_id is not found
        ValueError: If notification cannot be generated
    """
```

### 4.3 generate_adaptive_interface

```python
def generate_adaptive_interface(self, user_id: str) -> Dict[str, Any]:
    """
    Generate adaptive interface recommendations based on user trust level.
    
    This method provides recommendations for adapting the Windsurf UI
    based on the user's current trust level and past interactions.
    
    Args:
        user_id (str): User identifier
    
    Returns:
        Dict[str, Any]: Interface recommendations containing:
            - user_id (str): User identifier
            - trust_level (str): Trust level category (low, medium, high)
            - interface_elements (Dict): Recommended UI element adjustments
            - validation_level (str): Recommended validation strictness
            - recommended_guidance_frequency (str): How often to show guidance
    
    Raises:
        ValueError: If user_id is invalid
        RuntimeError: If recommendations cannot be generated
    """
```

### 4.4 store_trust_score

```python
def store_trust_score(self, user_id: str, score: float) -> None:
    """
    Store a trust score in the persistence system.
    
    Args:
        user_id (str): User identifier
        score (float): Trust score to store (0.0 to 1.0)
    
    Raises:
        ValueError: If score is outside valid range
        RuntimeError: If storage fails
    """
```

### 4.5 retrieve_trust_score

```python
def retrieve_trust_score(self, user_id: str) -> float:
    """
    Retrieve a trust score from the persistence system.
    
    Args:
        user_id (str): User identifier
    
    Returns:
        float: Retrieved trust score, or default if not found
    
    Raises:
        RuntimeError: If retrieval fails
    """
```

### 4.6 clear_sensitive_data

```python
def clear_sensitive_data(self, user_id: str, data_type: Optional[str] = None) -> int:
    """
    Clear sensitive data from memory.
    
    This method implements Sacred Privacy (SP) by removing sensitive
    data from memory when it's no longer needed.
    
    Args:
        user_id (str): User identifier
        data_type (str, optional): Type of data to clear.
            If None, clears all sensitive data for the user.
    
    Returns:
        int: Number of items cleared
    
    Raises:
        RuntimeError: If clearing fails
    """
```

### 4.7 process_ethical_event

```python
def process_ethical_event(self, user_id: str, event_type: str, 
                         event_description: str, magnitude: float = 0.1) -> Dict[str, Any]:
    """
    Process an ethical event that affects trust.
    
    This method allows external components to report ethical events
    that should influence a user's trust score.
    
    Args:
        user_id (str): User identifier
        event_type (str): Type of ethical event
        event_description (str): Description of the event
        magnitude (float, optional): Magnitude of impact (0.0 to 1.0)
    
    Returns:
        Dict[str, Any]: Event processing results containing:
            - user_id (str): User identifier
            - previous_trust (float): Trust score before event
            - current_trust (float): Trust score after event
            - event_type (str): Type of event processed
            - timestamp (str): ISO 8601 timestamp
    
    Raises:
        ValueError: If magnitude is outside valid range
        RuntimeError: If processing fails
    """
```

## 5. WindsurfOperationType Enum

```python
class WindsurfOperationType(Enum):
    """
    Enum defining the types of operations that can be performed in Windsurf.
    
    These operation types are used to categorize actions for ethical evaluation
    and trust assessment.
    """
    
    FILE_CREATION = "file_creation"
    FILE_MODIFICATION = "file_modification"
    CODE_GENERATION = "code_generation"
    CODE_EDITING = "code_editing"
    SYSTEM_CONFIG = "system_config"
    AUTHENTICATION = "authentication"
    DATA_ACCESS = "data_access"
    EXTERNAL_API_CALL = "external_api_call"
    USER_INTERACTION = "user_interaction"
    GENERAL = "general"
```

## 6. Operation Context Examples

Different operation types require different context information:

### 6.1 FILE_CREATION

```python
context = {
    "file_path": "/path/to/file.py",
    "content": "def process_data(user_info):\n    pass",
    "file_type": "python",
    "user_intent": "create data processing module"
}
```

### 6.2 CODE_GENERATION

```python
context = {
    "purpose": "authentication function",
    "language": "python",
    "code_context": "class UserAuth:\n    def __init__(self):\n        self.users = {}\n",
    "prompt": "Create a secure login method",
    "generated_code": "def login(self, username, password):\n    if username in self.users and self.check_password(password, self.users[username]):\n        return True\n    return False"
}
```

### 6.3 AUTHENTICATION

```python
context = {
    "operation": "user_login",
    "authentication_method": "password",
    "stores_credentials": True,
    "remember_user": False
}
```

### 6.4 DATA_ACCESS

```python
context = {
    "resource": "user_database",
    "query": "SELECT name, email FROM users WHERE id = 123",
    "purpose": "user profile display",
    "data_categories": ["basic_profile"]
}
```

## 7. Response Structure Examples

### 7.1 Operation Evaluation Response

```python
{
    "operation_id": "file_creation_20250527184522",
    "user_id": "developer_alice",
    "operation_type": "file_creation",
    "timestamp": "2025-05-27T18:45:22.123Z",
    "allowed": True,
    "trust_score": 0.85,
    "ethical_evaluation": {
        "allowed": True,
        "warnings": ["Operation involves handling of personal data"],
        "guidance": "Ensure proper consent and data minimization practices are followed"
    },
    "contains_sensitive_data": True,
    "detected_keywords": ["personal", "email", "user_info"],
    "should_notify": True
}
```

### 7.2 Notification Response

```python
{
    "notification_id": "notification_20250527184530",
    "type": "warning",
    "title": "Privacy Consideration",
    "message": "The code you're creating appears to handle personal user information. Please ensure you're following data protection best practices including data minimization and appropriate security measures.",
    "operation_id": "file_creation_20250527184522",
    "timestamp": "2025-05-27T18:45:30.456Z"
}
```

### 7.3 Adaptive Interface Response

```python
{
    "user_id": "developer_alice",
    "trust_level": "high",
    "interface_elements": {
        "simplify_options": True,
        "show_advanced_features": True,
        "highlight_security_options": False,
        "recommended_tools": ["code_scanner", "security_checker"]
    },
    "validation_level": "standard",
    "recommended_guidance_frequency": "low"
}
```

## 8. Error Handling

The adapter uses standard Python exceptions for error handling:

- `ValueError`: Invalid parameter values
- `KeyError`: Missing required keys in data structures
- `FileNotFoundError`: Configuration or resource files not found
- `RuntimeError`: General operational failures
- `TypeError`: Incorrect data types provided

Example error handling:

```python
try:
    result = adapter.evaluate_operation(operation_type, context, user_id)
except ValueError as e:
    logger.error(f"Invalid parameter: {e}")
    # Handle parameter error
except RuntimeError as e:
    logger.error(f"Operation evaluation failed: {e}")
    # Handle runtime error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## 9. Thread Safety

The `ATRiANWindsurfAdapter` is designed to be thread-safe for concurrent operation evaluations. However, methods that modify shared state (like `store_trust_score`) should be protected with appropriate synchronization mechanisms in multi-threaded environments.

## 10. Performance Considerations

- Operation evaluation typically completes in under 50ms
- For large code contexts (>1000 lines), consider chunking the evaluation
- Memory usage scales with the number of active users and operation history
- Trust score calculations are cached to improve performance

## 11. Implementation Notes

- The adapter uses dependency injection to allow for flexible component composition
- Ethics rules are loaded dynamically and can be updated without restarting
- Trust scores use a bounded calculation to prevent excessive inflation/deflation
- All timestamps use ISO 8601 format with UTC timezone
- The adapter implements graceful degradation when components are unavailable

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
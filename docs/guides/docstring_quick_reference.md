---
title: docstring_quick_reference
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: docstring_quick_reference
tags: [documentation]
---
---
title: docstring_quick_reference
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: docstring_quick_reference
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

<!-- 
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/governance/cross_reference_best_practices.md





  - [MQP](../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Process Documentation:
  - [cross_reference_best_practices](../governance/cross_reference_best_practices.md)
  - docs/guides/docstring_quick_reference.md




This quick reference guide provides concise examples of EGOS docstring standards for different code elements. Refer to the complete standards in MEMORY[05e5435b...] for detailed requirements.

## Module Docstrings

```python
"""
EGOS - [Subsystem] [Component Name]
===================================

Brief description of the module's purpose and functionality.
Additional details about usage, context, or implementation notes.

Version: X.Y.Z ([Status])
"""
```

**Key Requirements**:
- Must be the first statement in the file (except for shebang or encoding declarations)
- Include subsystem name and component identifier
- Use standardized header underline format
- Include version and status

## Class Docstrings

```python
class ClassName:
    """Brief description of the class purpose and functionality.
    
    More detailed explanation if needed, including usage examples,
    implementation details, or design patterns used.
    
    Attributes:
        attr_name (type): Description of the attribute.
        another_attr (type): Description of another attribute.
    
    Methods:
        method_name: Brief description of method purpose.
        another_method: Brief description of another method.
    """
```

**Key Requirements**:
- Include an `Attributes:` section when the class has attributes
- Include a `Methods:` section when the class has public methods
- Describe the class purpose and usage patterns

## Method/Function Docstrings

```python
def function_name(param1, param2, *args, **kwargs):
    """Brief description of the function purpose.
    
    More detailed explanation if needed.
    
    Args:
        param1 (type): Description of first parameter.
        param2 (type): Description of second parameter.
        *args: Variable length argument list description.
        **kwargs: Arbitrary keyword arguments description.
    
    Returns:
        type: Description of return value.
        
    Raises:
        ExceptionType: When and why this exception is raised.
    """
```

**Key Requirements**:
- Include an `Args:` section when the function takes parameters
- Include a `Returns:` section when the function returns a value
- Include a `Raises:` section when the function raises exceptions
- Align with the type hints used in the function signature

## Special Patterns

### Mycelium Message Handlers

```python
@mycelium_client.subscribe(Topic("topic_name"))
async def handle_message(message: Message):
    """Handle incoming messages on topic_name.
    
    Processes messages containing X and updates Y state.
    
    Args:
        message: Mycelium message containing the request data.
            Expected format: {"key": value_type, ...}
    """
```

### EGOS Subsystem Classes

```python
class SubsystemCore:
    """Core implementation for the [Subsystem] subsystem.
    
    Responsible for [primary functionality] and [secondary functionality].
    Integrates with [related subsystems] through [integration method].
    
    Attributes:
        logger: Logger instance for tracking subsystem operations.
        config: Configuration dictionary loaded from config file.
        client: Reference to the Mycelium client for messaging.
        
    Methods:
        initialize: Set up the subsystem and connect to dependencies.
        process_event: Handle incoming events from other subsystems.
        generate_report: Create reports based on internal state.
    """
```

## Docstring Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `docstring_checker.py` | Check docstring compliance | `python scripts/maintenance/code_health/docstring_checker.py --root-dir subsystems/[SUBSYSTEM]` |
| `docstring_autofixer.py` | Fix structural issues | `python scripts/maintenance/code_health/docstring_autofixer.py --report-path [REPORT_PATH]` |
| `docstring_workflow.py` | Run complete workflow | `python scripts/maintenance/code_health/docstring_workflow.py --target-dir subsystems/[SUBSYSTEM]` |
| `docstring_content_generator.py` | Generate meaningful content | `python scripts/maintenance/code_health/docstring_content_generator.py --file-path [FILE_PATH]` |
| `docstring_metrics.py` | Measure documentation quality | `python scripts/maintenance/code_health/docstring_metrics.py --scan-dir subsystems/[SUBSYSTEM]` |

## VS Code Integration

For interactive docstring generation during development:

1. Use the provided snippets for quick generation:
   - `egosmod` - Module docstring
   - `egoscls` - Class docstring
   - `egosfn` - Function docstring
   - `egosmethod` - Method docstring
   - `egoshandler` - Mycelium handler docstring

2. Install recommended extensions:
   - **QuantumDoc**: AI-powered Google-style docstring generator
   - **autoDocstring**: Template-based docstring generator

## Examples of High-Quality Docstrings

### Module Example

```python
"""
EGOS - NEXUS Core
=================

Core implementation for the NEXUS subsystem, providing central data
management and cross-system communication services. Implements the
central registry for all EGOS subsystem connections.

Version: 1.2.0 (Active)
"""
```

### Class Example

```python
class NexusConnection:
    """Handle connections between EGOS subsystems through the NEXUS.
    
    Manages the lifecycle of subsystem connections, including
    initialization, health monitoring, and graceful shutdown.
    Provides robust error handling and recovery mechanisms.
    
    Attributes:
        client_id (str): Unique identifier for the connection.
        state (ConnectionState): Current state of the connection.
        logger (KoiosLogger): Logger instance for this connection.
    
    Methods:
        connect: Establish connection to the NEXUS system.
        send_message: Send data to another subsystem.
        disconnect: Close connection and perform cleanup.
    """
```

### Function Example

```python
def validate_message(message: Dict[str, Any], schema: Schema) -> Tuple[bool, Optional[str]]:
    """Validate a message against a schema definition.
    
    Performs structural and content validation of message objects
    before they are transmitted through the system.
    
    Args:
        message: The message dictionary to validate.
        schema: Schema object that defines the expected structure.
    
    Returns:
        Tuple containing:
            - Boolean indicating if validation passed
            - Error message if validation failed, None otherwise
    
    Raises:
        ValidationError: If schema itself is invalid or corrupted.
    """
```
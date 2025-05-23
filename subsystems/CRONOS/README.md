# CRONOS Subsystem Documentation

## Overview

CRONOS is the backup and state preservation subsystem of the EGOS project. It provides robust functionality for creating, managing, and restoring backups of the entire project or specific modules.

## Role in Dynamic Roadmap Sync & EGOS Interconnection

CRONOS is responsible for:
- Logging all roadmap sync events and preserving the evolutionary history of roadmap and subsystem changes.
- Ensuring that all changes and sync actions are auditable and traceable.
- Collaborating with MYCELIUM, KOIOS, and SYNC to guarantee state integrity and historical record.

Cross-reference: See ROADMAP.md sections "Dynamic Roadmap Sync & Mycelium Interconnection" and "Technical Implementation Plan: Dynamic Roadmap Sync (Phase 1)".

## Core Components

### BackupManager

The `BackupManager` class is responsible for handling backup operations:

- Creating backups of project state
- Listing available backups
- Restoring from backups using different strategies
- Managing backup retention and cleanup

### CronosService

The `CronosService` provides a Mycelium-based interface for backup operations:

- Handling backup requests
- Managing restore operations
- Providing backup status information
- Coordinating with other subsystems

## Features

### Backup Creation
- Automatic backup scheduling
- Manual backup triggers
- Configurable backup retention
- Backup metadata preservation

### Backup Listing
- List available backups
- Sort by date/time
- Filter by type or content
- Metadata inspection

### Backup Restoration
- Multiple restore strategies:
  - `replace`: Complete replacement of target directory
  - `merge`: Selective merge of backup contents
- Restore validation
- Error handling and rollback
- Progress tracking

## Usage

CRONOS functionality can be accessed either directly via the `BackupManager` class or through the Mycelium network using `CronosService`.

### Direct Usage (`BackupManager`)

Provides fine-grained control over backup operations. See `docs/procedures.md` for full details.

```python
# Conceptual Example - Requires proper initialization and async handling
from pathlib import Path
from subsystems.CRONOS.core.backup_manager import BackupManager

# Assuming project_root is defined (e.g., Path(".").resolve())
# BackupManager initialization might require config, logger, etc.
manager = BackupManager(project_root=project_root)

# List backups (currently synchronous)
backups = manager.list_backups()
print("Available Backups:", backups)

# Create a backup (asynchronous)
# backup_path = await manager.create_backup(name="manual_snapshot")
# print("Backup created:", backup_path)
```

### Service Usage (`CronosService` via Mycelium)

Handles requests and responses over the Mycelium network.

#### Creating a Backup

```python
from cronos.service import CronosService

service = CronosService() # Assumes Mycelium client is configured/running
# target_modules limits backup scope (optional)
await service.create_backup(
    target_modules=["ETHIK", "ATLAS"],
    metadata={"description": "Pre-deployment backup"}
)
```

#### Listing Backups

```python
backups = await service.list_backups()
for backup in backups:
    # Backup details format depends on service implementation
    print(f"Backup: {backup}")
```

#### Restoring from Backup

```python
# backup_identifier can be filename, timestamp, or name_timestamp
# strategy controls how restore is applied ('new_location', 'overwrite')
await service.restore_backup(
    backup_identifier="backup_20250401_001.zip", # Example ID
    restore_target_path="/path/to/restore", # Often used with 'new_location'
    strategy="overwrite" # Use 'overwrite' with caution
)
```

## Configuration

The CRONOS subsystem can be configured through environment variables or configuration files:

```yaml
CRONOS_BACKUP_DIR: /path/to/backups
CRONOS_RETENTION_DAYS: 30
CRONOS_MAX_BACKUPS: 100
```

## Error Handling

CRONOS implements comprehensive error handling:

- Validation of backup files
- Integrity checks during restore
- Rollback capabilities
- Detailed error reporting

## Integration with Other Subsystems

CRONOS integrates with:

- ETHIK for validation of backup/restore operations
- ATLAS for backup metadata mapping
- NEXUS for module dependency tracking
- KoiosLogger for operation logging

## Testing

Run the test suite:

```bash
cd subsystems/CRONOS
pytest tests/
```

## Best Practices

1. Regular Backups
   - Schedule automatic backups
   - Maintain multiple backup points
   - Document significant changes

2. Restore Testing
   - Regularly test restore functionality
   - Validate restored state
   - Document restore procedures

3. Backup Management
   - Monitor backup storage usage
   - Clean old backups regularly
   - Verify backup integrity

## Troubleshooting

Common issues and solutions:

1. Backup Creation Fails
   - Check disk space
   - Verify write permissions
   - Check file locks

2. Restore Fails
   - Verify backup file exists
   - Check target directory permissions
   - Validate backup file integrity

3. Performance Issues
   - Monitor backup size
   - Check compression settings
   - Review backup frequency

## Contributing

Contributions should focus on improving state management, backup strategies, and context preservation mechanisms. Refer to the main <!-- TO_BE_REPLACED --> when working within this subsystem.

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧

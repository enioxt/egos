---
title: Directory Structure Manager
description: A generic utility class for managing directory structures. Provides methods for creating, deleting, ...
date: 2025-05-21
lastmod: 2025-05-22
draft: false
images: []
categories: [Utility]
tags: [utility, directory, structure, management]
toc: true
---

# Directory Structure Manager

**Status**: ACTIVE

**Path**: `scripts/maintenance/directory_structure/directory_structure_manager.py`

**Category**: Utility

**Maintainer**: EGOS Development Team

## Description

A generic utility class for managing directory structures. Provides methods for creating, deleting, listing, and ensuring the existence of directories. Adheres to EGOS principles for modularity and reusability.

## Examples

### Example 1: Creating a directory

```bash
manager = DirectoryStructureManager()
manager.create_directory(Path('path/to/new/directory'))
```

**Output**:

```
True (if successful)
```

### Example 2: Listing directory contents

```bash
manager = DirectoryStructureManager()
contents = manager.list_directory_contents(Path('path/to/directory'))
```

**Output**:

```
List of DirectoryItem objects with details about each item
```

## Documentation

- **guide**: [docs/guides/directory_management.md](docs/guides/directory_management.md)

## Tags

- #utility
- #directory
- #structure
- #management


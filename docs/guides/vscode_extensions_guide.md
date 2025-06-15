---
title: vscode_extensions_guide
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: vscode_extensions_guide
tags: [documentation]
---
---
title: vscode_extensions_guide
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
title: vscode_extensions_guide
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
title: EGOS VS Code Extensions Configuration Guide
version: 1.0.0
status: Active
date: 2025-04-25
tags: [development, tools, vscode, windsurf, koios]
@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- CROSSREF_STANDARD.md

@references(level=1):
  - docs/guides/code_health_tools_guide.md






  - [MQP](../core/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP](../governance/migrations/processed/pt/ROADMAP.md) - Project roadmap and planning
- Standards:
  - [code_health_tools_guide](code_health_tools_guide.md)
---
  - docs/guides/vscode_extensions_guide.md

# EGOS VS Code Extensions Configuration Guide

**Document ID:** KOIOS-GUIDE-003  
**Version:** 1.0  
**Last Updated:** 2025-04-25  
**Status:** ⚡ Active  

## 1. Introduction

This guide provides detailed instructions for configuring VS Code extensions to enhance code quality and development efficiency in the EGOS project. These extensions complement our custom code health tools and help catch issues early in the development process.

## 2. Recommended Extensions

### 2.1 Core Extensions

| Extension | Purpose | Install Command |
|-----------|---------|----------------|
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Python language support, linting, debugging | `ext install ms-python.python` |
| [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) | Fast Python linter with auto-fixes | `ext install charliermarsh.ruff` |
| [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) | Python code formatting | `ext install ms-python.black-formatter` |
| [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) | Generate Python docstrings | `ext install njpwerner.autodocstring` |

### 2.2 Code Health Extensions

| Extension | Purpose | Install Command |
|-----------|---------|----------------|
| [Remove Comments](https://marketplace.visualstudio.com/items?itemName=rioj7.vscode-remove-comments) | Delete comment blocks | `ext install rioj7.vscode-remove-comments` |
| [DeepSource Autofix™ AI](https://marketplace.visualstudio.com/items?itemName=DeepSourceCorp.deepsource-vscode) | AI-based code health & auto-fix | `ext install DeepSourceCorp.deepsource-vscode` |
| [Comment Remover](https://marketplace.visualstudio.com/items?itemName=manny1.commentremover) | Remove all types of comments | `ext install manny1.commentremover` |
| [Error Lens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens) | Highlight errors and warnings | `ext install usernamehw.errorlens` |

### 2.3 Windsurf-Specific Extensions

| Extension | Purpose | Install Command |
|-----------|---------|----------------|
| [Windsurf AI](https://marketplace.visualstudio.com/items?itemName=windsurf.windsurf-vscode) | Windsurf integration | `ext install windsurf.windsurf-vscode` |
| [Windsurf Linting](https://marketplace.visualstudio.com/items?itemName=windsurf.windsurf-linting) | Windsurf-specific linting rules | `ext install windsurf.windsurf-linting` |

## 3. Installation

### 3.1 Bulk Installation

To install all recommended extensions at once, run the following commands in your terminal:

```bash
# Core Extensions
code --install-extension ms-python.python
code --install-extension charliermarsh.ruff
code --install-extension ms-python.black-formatter
code --install-extension njpwerner.autodocstring

# Code Health Extensions
code --install-extension rioj7.vscode-remove-comments
code --install-extension DeepSourceCorp.deepsource-vscode
code --install-extension manny1.commentremover
code --install-extension usernamehw.errorlens

# Windsurf-Specific Extensions
code --install-extension windsurf.windsurf-vscode
code --install-extension windsurf.windsurf-linting
```

### 3.2 Installation Script

Alternatively, you can use the provided installation script:

```bash
python scripts/maintenance/setup/install_vscode_extensions.py
```

## 4. Configuration

### 4.1 settings.json

Add the following configuration to your VS Code `settings.json` file:

```json
{
  // Python settings
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    }
  },
  
  // Docstring settings
  "autoDocstring.docstringFormat": "google",
  "autoDocstring.startOnNewLine": true,
  "autoDocstring.includeExtendedSummary": true,
  
  // Error Lens settings
  "errorLens.enabledDiagnosticLevels": [
    "error",
    "warning",
    "info"
  ],
  "errorLens.excludeBySource": [
    "cSpell"
  ],
  
  // Comment Remover settings
  "commentRemover.entireLine": true,
  "commentRemover.includeHTML": true,
  
  // Windsurf settings
  "windsurf.linting.enableOnSave": true,
  "windsurf.linting.runAfterFormat": true
}
```

### 4.2 Workspace Settings

For project-wide settings, create or update `.vscode/settings.json` in your project root:

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.ruffPath": "${workspaceFolder}/.venv/bin/ruff",
  "python.formatting.blackPath": "${workspaceFolder}/.venv/bin/black",
  "python.analysis.extraPaths": [
    "${workspaceFolder}"
  ],
  "python.envFile": "${workspaceFolder}/.env",
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python"
}
```

## 5. Extension-Specific Configuration

### 5.1 Ruff Configuration

Ruff is configured through `pyproject.toml`. Our project already includes the necessary configuration:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "D", "I"]
ignore = ["D203", "D213"]

[tool.ruff.pydocstyle]
convention = "google"
```

### 5.2 Black Configuration

Black is also configured in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ["py310"]
include = '\.pyi?$'
```

### 5.3 autoDocstring Configuration

Configure autoDocstring to generate Google-style docstrings by adding to your `settings.json`:

```json
{
  "autoDocstring.docstringFormat": "google",
  "autoDocstring.generateDocstringOnEnter": true,
  "autoDocstring.includeExtendedSummary": true,
  "autoDocstring.includeName": false,
  "autoDocstring.startOnNewLine": true
}
```

## 6. Usage Guidelines

### 6.1 Fixing HTML Comments

To fix HTML comments in a file:

1. Open the file in VS Code
2. Right-click and select "Remove Comments" or use the keyboard shortcut
3. Select "Remove HTML Comments"
4. Save the file

### 6.2 Fixing Unbalanced Triple Quotes

To fix unbalanced triple quotes:

1. Enable Error Lens to highlight syntax errors
2. Look for highlighted errors indicating unbalanced quotes
3. Manually add the missing closing quotes
4. Alternatively, run the comprehensive code health tool:
   ```bash
   python scripts/maintenance/code_health/comprehensive_code_health.py --triple-quotes --fix <file_path>
   ```

### 6.3 Automated Formatting on Save

With the provided configuration, VS Code will automatically:

1. Format your code with Black when you save a file
2. Run Ruff to check for linting issues
3. Apply auto-fixes for simple issues
4. Highlight any remaining issues that need manual intervention

## 7. Troubleshooting

### 7.1 Extension Conflicts

If you experience conflicts between extensions:

1. Disable extensions one by one to identify the conflict
2. Check for overlapping settings in `settings.json`
3. Prioritize Ruff over other linters for Python files

### 7.2 Performance Issues

If VS Code becomes slow with all extensions enabled:

1. Disable extensions you're not actively using
2. Limit linting to opened files only
3. Add large directories to the `files.watcherExclude` setting

### 7.3 Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Black not found" | Ensure Black is installed in your environment and the path is correctly set |
| "Ruff not found" | Verify Ruff is installed and the path is correctly configured |
| Formatting not working on save | Check that `editor.formatOnSave` is enabled for Python files |
| Extensions not detecting project settings | Reload VS Code window after configuration changes |

## 8. Conclusion

By configuring these VS Code extensions, you'll significantly improve code quality and development efficiency in the EGOS project. The extensions work together with our custom code health tools to provide a comprehensive solution for maintaining high-quality code.

For questions or feedback about this guide, please contact the KOIOS documentation team.

---

✧༺❀༻∞ EGOS ∞༺❀༻✧
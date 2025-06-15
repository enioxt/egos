---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: readme
tags: [documentation]
---
---
title: README
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
title: README
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

@references:
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- CROSSREF_STANDARD.md

  - <!-- TO_BE_REPLACED --> - Project roadmap and planning
  - [MQP](..\..\..\reference\MQP.md) - Master Quantum Prompt defining EGOS principles
- Other:
  - [MQP](..\..\..\reference\MQP.md)
  - scripts/mcp_management/README.md




# OpenRouter MCP Server for Roocode

This directory contains configuration files and scripts to set up the OpenRouter MCP server for use with Roocode.

## Overview

The OpenRouter MCP server provides intelligent model selection and cost optimization through the OpenRouter API, with a focus on prioritizing free models by default.

## Setup Instructions

Follow these steps to set up the OpenRouter MCP server for Roocode:

### 1. Install Dependencies

First, run the dependency installation script:

```
.cursor/install_dependencies.bat
```

This will install the required Node.js packages:
- axios: For making HTTP requests to the OpenRouter API
- uuid: For generating unique identifiers
- ws: For WebSocket communication

### 2. Start the OpenRouter MCP Server

Start the server using:

```
.roo/start_openrouter_mcp.bat
```

This will:
- Set the necessary environment variables
- Create log directories if they don't exist
- Start the server in the foreground
- Show all output directly in the console

**Important**: Keep this terminal window open while using the server.

### 3. Configure Roocode to Connect to the Server

Run the following script to configure Roocode to connect to the MCP server:

```
.roo/force_mcp_connection.bat
```

This will:
- Create a configuration file at `%APPDATA%\Roo\mcp_config.json`
- Configure Roocode to connect to the MCP server on localhost:38001

### 4. Restart Roocode

Close and reopen Roocode to apply the changes.

### 5. Verify the Connection

After restarting Roocode, check if "openrouter" appears in the "Connected MCP Servers" section at the bottom of the chat window.

## Using the OpenRouter MCP Server

Once connected, you can use the OpenRouter MCP server through the following tools:

1. **`openrouter_chat`**: General chat completion with automatic model selection
2. **`openrouter_code`**: Code-specific completion using appropriate models
3. **`openrouter_analyze`**: Analysis with context-appropriate models
4. **`openrouter_select_model`**: Manual model selection override
5. **`openrouter_toggle_free_models`**: Toggle between prioritizing free models and using optimal models
6. **`openrouter_status`**: Get status information about available models

Example usage:

```
<use_mcp_tool>
<server_name>openrouter</server_name>
<tool_name>openrouter_status</tool_name>
<arguments>
{}
</arguments>
</use_mcp_tool>
```

## Free Models

The following free models are available:

- **Gemini 2.5 Flash**: General tasks with medium-large contexts
- **Llama 3 70B**: General tasks with medium complexity and code tasks
- **Phi-3 Mini**: Simple tasks, quick responses, minimal context

These models are set as the defaults for different types of tasks:
- **Default model** (general tasks): `phi-3-mini-128k`
- **Code model** (code tasks): `llama-3-70b-instruct`
- **Long context model** (large contexts): `gemini-1.5-flash`

## Troubleshooting

If you encounter issues with the OpenRouter MCP server:

1. Make sure the server is running:
   - Check if the terminal window running `.roo/start_openrouter_mcp.bat` is still open
   - If not, restart the server

2. Check if Roocode is configured to connect to the server:
   - Run `.roo/force_mcp_connection.bat` again
   - Restart Roocode

3. Check the logs:
   - Server log: `C:/Eva Guarani EGOS/logs/mcp/openrouter.log`

4. Make sure Node.js is installed and working correctly:
   - Run `node --version` in a terminal

✧༺❀༻∞ EVA & GUARANI ∞༺❀༻✧
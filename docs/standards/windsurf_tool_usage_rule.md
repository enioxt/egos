@references:
  - docs/standards/windsurf_tool_usage_rule.md

# Windsurf Tool Usage Rule

## RULE-DEV-WINDSURF-01: Tool Fallback Strategy for File Edits

**ID:** `RULE-DEV-WINDSURF-01`  
**Type:** Development Standard  
**Applies To:** All AI Assistants (Cascade)  
**Priority:** High  
**Status:** Proposed  

### Description
When making edits to files using Windsurf AI tools, always follow this fallback strategy to ensure reliable and accurate file modifications:

1. **Primary Strategy - Read Before Edit:**
   - Before using any file edit tool (MCP filesystem tools or Windsurf native tools), always read the exact content of the target file section first.
   - Use `view_line_range`, `view_file_outline`, or `mcp*_read_file` to get the precise content that will be modified.
   - Ensure the "oldText" or "TargetContent" parameter exactly matches what exists in the file.

2. **Fallback Strategy - Tool Selection:**
   - If MCP filesystem tools (`mcp*_edit_file`) fail, immediately fall back to using Windsurf's native `replace_file_content` tool.
   - The `replace_file_content` tool is often more robust for complex edits and should be preferred when MCP tools encounter errors.

3. **Error Recovery:**
   - If an edit fails due to content mismatch, do not retry with the same parameters.
   - Re-read the current file content and adjust your edit parameters accordingly.
   - For large edits, consider breaking them into smaller, more manageable chunks.

### Rationale
This rule ensures consistent and reliable file modifications across the EGOS codebase, reducing errors caused by content mismatches and improving the efficiency of AI-assisted development workflows.

### Cross-References
- `RULE-CODE-STD-01` (Code Quality Standards)
- `RULE-DEV-PROCESS-02` (Development Process Standards)
- `MQP_INT` (Master Quantum Prompt Integration)
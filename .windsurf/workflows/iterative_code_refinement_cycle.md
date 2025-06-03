---
description: A structured process for progressively improving code quality, functionality, and performance using AI-assisted feedback loops and automated checks
---

Iterative Code Refinement Cycle

Objective: To systematically enhance code through repeated cycles of AI-assisted analysis, developer implementation, automated testing, and review, leading to robust and maintainable software.

Phases & Steps:

1. Phase 1: Baseline & Initial Analysis
   - Step 1.1: Code Submission/Selection: Identify the codebase or specific module for refinement.
   - Step 1.2: Create Backup of Target Files: **MANDATORY** Create dated backups of all files that will be modified before making any changes.
     - EGOS PRINCIPLE: Evolutionary_Preservation - Ensure recoverability if changes cause unexpected issues.
     - EGOS TOOL SUGGESTION: run_command to execute backup scripts or copy commands.
     - Example: `copy path\to\file.ext path\to\file_backup_YYYYMMDD.ext`
   - Step 1.3: Establish Baseline Metrics: Measure current code quality, performance, test coverage.
   - Step 1.4: Verify Functionality: Test the current code to ensure it functions correctly and establish a baseline for post-modification testing.
   - Step 1.5: Initial AI Code Analysis:
     - Run static analysis tools, linters.
     - Employ AI models for identifying code smells, potential bugs, and areas for improvement (e.g., complexity, readability).
     - EGOS TOOL SUGGESTION: codebase_search for context, potential custom AI review scripts via run_command.

2. Phase 2: AI-Assisted Suggestion & Developer Action
   - Step 2.1: Review AI-Generated Suggestions: AI provides specific, actionable recommendations for refactoring, optimization, or bug fixing.
   - Step 2.2: Risk Assessment: Evaluate potential risks of implementing changes, particularly for critical components.
   - Step 2.3: Developer Prioritization & Implementation: Developer reviews suggestions, prioritizes, and implements changes.
     - EGOS PRINCIPLE: Human In The Loop - Developer makes final decisions.
     - EGOS TOOL SUGGESTION: mcp2_edit_file, replace_file_content.
   - Step 2.4: Post-Implementation Validation: **MANDATORY** Run basic validation checks immediately after implementation to catch critical errors before proceeding.

3. Phase 3: Automated Testing & Validation
   - Step 3.1: Execute Existing Test Suite: **MANDATORY** Ensure no regressions are introduced.
     - EGOS TOOL SUGGESTION: run_command to trigger test scripts.
     - If failures occur, analyze root cause and fix or revert to backup if necessary.
   - Step 3.2: Functionality Verification: **MANDATORY** Verify that the code performs its intended function correctly after changes.
     - Test both happy path and edge cases.
   - Step 3.3: AI-Assisted Test Case Generation: AI suggests new test cases for improved coverage, especially for modified code sections.
   - Step 3.4: Performance Profiling (AI-Guided): If performance is a focus, use AI to pinpoint bottlenecks post-refinement.

4. Phase 4: Review & Feedback Integration
   - Step 4.1: AI Co-Review / Peer Review: Submit refined code for another round of AI analysis or human peer review.
   - Step 4.2: Integrate Feedback: Incorporate valid feedback into the codebase.
   - Step 4.3: Documentation Update (AI-Assisted): AI helps draft updates to comments, docstrings, or external documentation based on changes.
     - EGOS WORKFLOW: Dynamic Documentation Update From Code Changes can be triggered.

5. Phase 5: Iteration & Monitoring
   - Step 5.1: Measure Improvement: Compare new metrics against the baseline.
   - Step 5.2: Decide on Next Cycle: Determine if further refinement is needed or if the code meets quality targets.
   - Step 5.3: Continuous Monitoring (Optional): Implement ongoing AI-driven monitoring for quality and performance in production.
     - EGOS PRINCIPLE: Evolutionary Preservation

Best Practices:
- **ALWAYS create dated backups** of all files before modification (mandatory safety measure).
- **ALWAYS test code functionality** before and after changes to verify improvements and catch regressions.
- **Document all changes** including what was modified and why.
- Integrate this cycle into the CI/CD pipeline.
- Start with small, manageable code sections.
- Customize AI models and rules to project-specific standards.
- Maintain version control and track changes meticulously.
- Balance AI suggestions with developer expertise and project context.

Safety Protocol:
1. Never skip the backup step, even for seemingly minor changes.
2. If modified code fails testing, immediately investigate or restore from backup.
3. Keep backups for a reasonable duration (at least until the next stable release).
4. For critical systems, consider maintaining a rollback plan for each significant change.
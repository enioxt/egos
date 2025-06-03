---
description: Leverages AI to gather, process, and synthesize information for research tasks, enhancing efficiency and depth of insights
---

AI Assisted Research And Synthesis

Objective: To systematically conduct research by employing AI tools for information gathering, analysis, and synthesis, culminating in a well-supported output.

Phases & Steps:

1. Phase 1: Define & Plan
   - Step 1.1: Define Research Question/Objective: Clearly articulate the core research question, scope, and desired outcomes.
     - EGOS TOOL SUGGESTION: mcp8_sequentialthinking for breaking down complex questions.
   - Step 1.2: Identify Key Concepts & Keywords: Determine relevant terms for searching.
   - Step 1.3: Select Information Sources: Identify databases, journals, web domains, or internal knowledge bases.
     - EGOS PRINCIPLE: Systemic Cartography - Map relevant knowledge domains.

2. Phase 2: Gather Information (AI-Assisted)
   - Step 2.1: Execute Search Queries: Use AI-powered search tools across selected sources.
     - EGOS TOOL SUGGESTION: search_web, codebase_search (if internal code/docs).
   - Step 2.2: Filter & Prioritize Results: AI assists in ranking relevance and filtering noise.
   - Step 2.3: Extract Raw Data/Text: Gather relevant documents, snippets, or data points.
     - EGOS TOOL SUGGESTION: read_url_content, view_file.

3. Phase 3: Process & Analyze (AI-Enhanced)
   - Step 3.1: Data Cleaning & Preprocessing: Standardize formats, remove duplicates (AI can assist).
   - Step 3.2: Information Extraction: AI identifies key entities, relationships, and summaries from text.
   - Step 3.3: Thematic Analysis & Pattern Recognition: AI helps uncover trends, correlations, or anomalies.
     - EGOS TOOL SUGGESTION: mcp6_search_nodes if data is in EGOS knowledge graph.

4. Phase 4: Synthesize & Generate Insights (AI-Supported)
   - Step 4.1: Draft Synthesis: AI generates initial summaries or structured outlines based on analyzed data.
   - Step 4.2: Identify Gaps & Contradictions: AI can flag inconsistencies or areas needing more research.
   - Step 4.3: Create Backups of Target Files: **MANDATORY** If the research output will modify existing code or documentation files, create dated backups of all files that will be changed.
     - EGOS PRINCIPLE: Evolutionary_Preservation - Ensure recoverability if changes cause unexpected issues.
     - EGOS TOOL SUGGESTION: run_command to execute backup scripts or copy commands.
     - Example: `copy path\to\file.ext path\to\file_backup_YYYYMMDD.ext`
   - Step 4.4: Iterative Refinement: Human expert refines AI-generated synthesis, adding critical thinking and domain expertise.
     - EGOS PRINCIPLE: AI Augmentation - Human expertise guides AI.

5. Phase 5: Validate & Report
   - Step 5.1: Fact-Checking & Source Verification: Human oversight is critical, AI can assist in cross-referencing.
   - Step 5.2: Generate Report/Output: Compile findings into the desired format (report, presentation, knowledge base article). AI can assist with drafting and formatting.
   - Step 5.3: **MANDATORY** Validation Testing: If research findings will inform code changes or technical documentation, validate that:
     - Any code examples or snippets are functional and produce expected results
     - Technical procedures are accurate and can be followed successfully
     - References to APIs, libraries, or external resources are current and accurate
   - Step 5.4: Peer/Stakeholder Review: Obtain feedback on the research output.
     - EGOS PROCESS: Evolutionary Refinement Cycle

Best Practices:
- **ALWAYS create dated backups** of any existing files that will be modified based on research findings (mandatory safety measure).
- **ALWAYS validate technical content** by testing procedures, code examples, and technical recommendations.
- Maintain a clear audit trail of sources and AI tool usage.
- Critically evaluate AI-generated content; do not accept it blindly.
- Use iterative cycles of AI assistance and human review.
- Clearly define the role and limitations of AI in each step.

Safety Protocol:
1. Never skip the backup step when research will lead to modifications of existing content.
2. For research informing critical systems or procedures, create a rollback plan before implementation.
3. Keep backups for a reasonable duration (at least until the next stable release or publication).
4. When research will impact system behavior, validate findings in a test environment before applying to production.
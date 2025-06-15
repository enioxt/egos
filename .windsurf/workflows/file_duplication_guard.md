---
description: guard against duplicate or hidden artefacts when adding new files or directories
categories: [maintenance, governance, automation]
requires: [Mycelium]
---
# FILE DUPLICATION GUARD WORKFLOW (EGOS × WINDSURF)

> “Search twice, create once.”

Invoke with `/file_duplication_guard <proposed_path>` to verify that a new file or directory truly needs to be created and won’t duplicate existing artefacts.

---
## 1. INPUT
* **`<proposed_path>`** – absolute or workspace-relative path you intend to create (file or directory).

---
## 2. PRE-CHECKS  // turbo
1. Fail fast if `<proposed_path>` already exists.  
   ```powershell
   Test-Path <proposed_path>
   ```
2. Ensure `.windsurfrules` & Rule-Ops checklist pass.

---
## 3. GLOBAL SEARCH  // turbo
Run a content & metadata search to detect potential duplicates:
```python
results = codebase_search(Query=Path.GetFileName(<proposed_path>), TargetDirectories=["C:/EGOS"])  # adjust scope if needed
```
Also grep for semantic keywords (e.g., `incident generator`, `ai_incident_db`) related to the new artefact.

### 3.1 Scoring & Report
* If >0 high-similarity hits (same purpose or naming), show summary list (path, similarity, last modified). 
* Suggest reuse/refactor instead of creation.

---
## 4. CONTEXT REVIEW
* Cross-reference Mycelium knowledge graph for links to similar artefacts.
* Display backlink count; flag orphaned docs (no incoming links) – candidate for consolidation rather than new file.

---
## 5. DECISION
* **Create** – proceed if no conflicts or if superseding obsolete artefact (attach ADR).  
* **Amend** – modify existing file if same concern already covered.  
* **Abort** – cancel creation; document rationale in work log.

Record decision in `plan.md` or relevant work log and add cross-references.

---
## 6. POST-ACTION  // turbo
If artefact is created:
1. Run `/dynamic_documentation_update_from_code_changes` to sync links.
2. Trigger Mycelium ingestion for new file metadata.
3. Optionally create ADR entry if replacing legacy structure.

---
### WORKFLOW META
* Keep file <6 k chars.  
* Update `description` YAML header if renamed.  
* Maintainers: EGOS Core Devs.

---
## Cross-References & Related Workflows
| Phase      | Workflow                                  |
|------------|-------------------------------------------|
| Pre-checks | /tdd_based_dev_workflow (prerequisites)   |
| Search     | /ai_assisted_research_and_synthesis       |
| Decision   | /project_handover_procedure              |
| Docs sync  | /dynamic_documentation_update_from_code_changes |

*EOF*

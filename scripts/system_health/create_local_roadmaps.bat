@echo off
REM Create Local Roadmaps
REM Author: EGOS Development Team
REM Date: 2025-05-18
REM Description: Creates standardized local roadmaps for key directories with proper cross-references

echo Creating local roadmaps for key directories...

REM Define directories that need roadmaps
set DIRS=C:\EGOS\docs C:\EGOS\scripts C:\EGOS\subsystems C:\EGOS\subsystems\KOIOS C:\EGOS\subsystems\ATLAS C:\EGOS\subsystems\MYCELIUM C:\EGOS\subsystems\NEXUS C:\EGOS\subsystems\CORUJA

REM Get current date in YYYY-MM-DD format
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set CURRENT_DATE=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

REM Create roadmaps for each directory
for %%D in (%DIRS%) do (
    set DIR_PATH=%%D
    set ROADMAP_PATH=%%D\roadmap.md
    
    echo Processing %%D...
    
    REM Skip if roadmap already exists
    if exist "!ROADMAP_PATH!" (
        echo Roadmap already exists at !ROADMAP_PATH!. Skipping.
    ) else (
        REM Extract directory name for title
        for %%I in ("%%D") do set DIR_NAME=%%~nxI
        
        echo Creating roadmap for !DIR_NAME!...
        
        REM Create roadmap file with proper metadata and cross-references
        (
            echo ---
            echo title: !DIR_NAME! Roadmap
            echo version: 1.0.0
            echo status: Active
            echo date_created: %CURRENT_DATE%
            echo date_modified: %CURRENT_DATE%
            echo authors: [EGOS Development Team]
            echo description: Development roadmap for !DIR_NAME!
            echo file_type: documentation
            echo scope: directory-specific
            echo primary_entity_type: roadmap
            echo primary_entity_name: !DIR_NAME!_roadmap
            echo tags: [documentation, roadmap, planning, !DIR_NAME!]
            echo ---
            echo.
            echo ## Cross References
            echo.
            echo - [EGOS ROADMAP](../../ROADMAP.md^)
            echo - [Roadmap Hierarchy](../../docs/governance/roadmap_hierarchy.md^)
            echo - [Roadmap Standardization](../../docs/governance/roadmap_standardization.md^)
            echo - [Development Standards](../../docs/governance/development_standards.md^)
            echo.
            echo # !DIR_NAME! Roadmap
            echo.
            echo ## Overview
            echo.
            echo [Brief description of this directory/subsystem and its purpose within EGOS]
            echo.
            echo ## Status Legend
            echo.
            echo ^| Status ^| Description ^|
            echo ^|--------|-------------|
            echo ^| 🔄 Backlog ^| Planned but not started ^|
            echo ^| ⏳ In Progress ^| Work has begun ^|
            echo ^| 🔍 Review ^| Ready for review ^|
            echo ^| ✅ Done ^| Complete ^|
            echo ^| 🔜 Deferred ^| Postponed ^|
            echo ^| ⛔ Blocked ^| Cannot proceed due to dependency ^|
            echo.
            echo ## Current Priorities
            echo.
            echo [Brief summary of current focus areas and priorities]
            echo.
            echo ## Tasks
            echo.
            echo ### [EGOS-EPIC-XXX-YY] Task Title
            echo.
            echo **Parent Epic:** [EGOS-EPIC-XXX](../../ROADMAP.md#egos-epic-xxx-epic-title^)  
            echo **Status:** 🔄 Backlog  
            echo **Priority:** [High/Medium/Low]  
            echo **Owner:** [Team/Individual]  
            echo **Estimated Effort:** [Hours or Story Points]  
            echo.
            echo **Description:**  
            echo [Detailed description of the task]
            echo.
            echo **Tasks:**
            echo - [ ] Subtask 1
            echo - [ ] Subtask 2
            echo - [ ] Subtask 3
            echo.
            echo **References:**
            echo - [Related Document 1](path/to/document1.md^)
            echo - [Related Document 2](path/to/document2.md^)
            echo.
            echo **Acceptance Criteria:**
            echo 1. Criterion 1
            echo 2. Criterion 2
            echo 3. Criterion 3
            echo.
            echo ## Completed Tasks
            echo.
            echo ### [EGOS-EPIC-XXX-YY] Completed Task Title
            echo.
            echo **Parent Epic:** [EGOS-EPIC-XXX](../../ROADMAP.md#egos-epic-xxx-epic-title^)  
            echo **Status:** ✅ Done  
            echo **Completion Date:** YYYY-MM-DD  
            echo.
            echo **Description:**  
            echo [Brief description of the completed task]
            echo.
            echo **Key Achievements:**
            echo - Achievement 1
            echo - Achievement 2
            echo - Achievement 3
            echo.
            echo ## Dependencies
            echo.
            echo ^| Task ID ^| Depends On ^| Status ^|
            echo ^|---------|------------|--------|
            echo ^| EGOS-EPIC-XXX-YY ^| EGOS-EPIC-ZZZ-WW ^| [Status] ^|
            echo ^| EGOS-EPIC-XXX-YY ^| External Dependency ^| [Status] ^|
        ) > "!ROADMAP_PATH!"
        
        echo Created roadmap at !ROADMAP_PATH!
    )
)

echo.
echo Local roadmap creation completed.
echo.
echo Next steps:
echo 1. Review and customize each roadmap for its specific directory
echo 2. Update the main ROADMAP.md to reference these local roadmaps
echo 3. Run the roadmap synchronization tool to verify proper hierarchy
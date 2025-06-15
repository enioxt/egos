---
description: Nightly cross-reference refresh & hygiene
categories: [maintenance, documentation, devops]
requires: [AutoCrossRef]
---
This workflow keeps EGOS’ automatic reference graph healthy.  It should be run
once per day (nightly CI) **or** manually with the slash-command
`/cross_reference_maintenance` inside Windsurf.

Steps
-----
// turbo-all
1. Remove stray self-references (Level-0 hygiene)
   run: python scripts/remove_self_crossref.py

2. Re-generate Level-1 cross-reference blocks for all documents
   run: python scripts/build_level1_xrefs.py

3. Stage & commit any changes (if present)
   run: |
        git add -A
        if git diff --cached --quiet; then
          echo "No cross-reference changes to commit.";
        else
          git commit -m "chore: nightly x-ref refresh"
        fi

4. Trigger dynamic documentation update
   run: /dynamic_documentation_update_from_code_changes

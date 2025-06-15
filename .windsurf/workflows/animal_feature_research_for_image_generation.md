---
# DO NOT EDIT FRONTMATTER DESCRIPTION LENGTH > 250 CHARS
# Keep whole workflow < 12 000 chars (current ~7 k)
# Version 2.0 – "ZooPrompt" expansion – 2025-06-13

description: Workflow for researching animal morphology and behaviours to craft accurate, high-fidelity image-generation prompts, then iteratively refining outputs and saving best prompts to PromptVault.
categories: [research, image_generation, prompt]
requires: [KOIOS]
---

# ANIMAL FEATURE RESEARCH FOR IMAGE GENERATION (EGOS × WINDSURF)

> “Science first, aesthetics second—truthful visuals every time.”

Invoke with `/animal_feature_research_for_image_generation`.

---
## TABLE OF CONTENTS
1. Prerequisites & Environment  
2. Phase 1 – Select Target Species  
3. Phase 2 – Scientific Research  
4. Phase 3 – Prompt Drafting  
5. Phase 4 – Image Generation & Review  
6. Phase 5 – PromptVault Submission  
7. Annex A – Accuracy Checklist  
8. Annex B – Free Image API Index  

---
## 1. PREREQUISITES & ENVIRONMENT // turbo
| ✔ | Item | Command |
|---|------|---------|
|   | search_web API key (`WSF_SEARCH_KEY`) | `echo %WSF_SEARCH_KEY%` |
|   | Craiyon/StableDiffusion endpoint reachable | `curl http://localhost:7860` |
|   | Backup script ready | `scripts/backup_modified_files.ps1` |

Abort if any check fails.

---
## 2. PHASE 1 – SELECT TARGET SPECIES
### 1.1 Name & Taxonomy
Record common + scientific name, class, order.

### 1.2 Purpose
State why the species is needed (game character, poster, etc.). Determines detail level.

---
## 3. PHASE 2 – SCIENTIFIC RESEARCH (AI-ASSISTED)
### 2.1 Anatomy & Key Traits // turbo-all
```python
results = search_web(f"{scientific_name} morphology distinctive features", max_results=15)
```
### 2.2 Behaviour & Habitat
Gather info on posture, locomotion, seasonal colours.

### 2.3 Accuracy Table
Fill `docs/animals/<name>_traits.md`:
```
|Body part|Trait|Source|
|Snout|Elongated tubular|[1]|
```
### 2.4 Expert Cross-check
Optional: consult zoologist or reputable database (Encyclopedia of Life, IUCN).

---
## 4. PHASE 3 – PROMPT DRAFTING
### 3.1 Draft in EGOS Style
Combine scientific facts with EGOS visual language (see Style Guides).

### 3.2 Peer Review
Quick review by design team; ensure no anthropomorphic errors unless intended.

### 3.3 Tech Metadata
Include resolution, aspect ratio, colour palette tags.

---
## 5. PHASE 4 – IMAGE GENERATION & REVIEW
### 4.1 Generate Variants // turbo
```bash
python scripts/generate_image.py --prompt "<draft>" --count 4
```
### 4.2 Visual Accuracy Checklist (see Annex A)
Flag issues: limb count, scale texture, colour.

### 4.3 Iterative Refinement Loop
Adjust prompt → regenerate until ≥ 90 % checklist pass.

### 4.4 Ethical & Licence Check
Confirm generated art is free of copyrighted material; store licence in YAML header.

---
## 6. PHASE 5 – PROMPTVAULT SUBMISSION
### 5.1 QuantumPrompt JSON
Use `/distill_and_vault_prompt` to create entry linking to trait table and final image.

### 5.2 Tagging
Add tags: `animal`, habitat, “egos-tech-twist”.

---
## 7. ANNEX A – VISUAL ACCURACY CHECKLIST
1. Correct number & placement of limbs / fins / wings  
2. Accurate texture (scales, fur, feathers)  
3. Authentic coloration / patterns (unless stylised—note deviation)  
4. Anatomically plausible posture  
5. Proportional head-to-body ratio  
6. Distinctive features present (e.g., Stegosaurus plates)  
7. Environmental coherence (habitat fits species)

---
## 8. ANNEX B – FREE IMAGE API INDEX
| Service | URL | Notes |
|---------|-----|-------|
| Unsplash API | https://unsplash.com/developers | Reference photos |
| Wikimedia Commons | https://commons.wikimedia.org | Public domain images |
| GBIF | https://api.gbif.org | Species occurrence photos |

---
### WORKFLOW META
* `// turbo` designates safe auto-runs; obey RULE-OPS-CHECKLIST-001.  
* Keep file < 12 000 chars; bump version header on edits.

---
## Cross-References & Related Workflows

- /ai_assisted_research_and_synthesis – Use for systematic info gathering about animal morphology before image prompt crafting.
- /atrian_ethics_evaluation – Validate generated prompts and images for ethical compliance.
- /dynamic_documentation_update_from_code_changes – Auto-sync prompt vault docs after updates.
- /project_handover_procedure – Transfer refined prompt collections to other teams.

*EOF*
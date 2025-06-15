# Neural Relation-Extraction Service – Implementation Plan

**Status:** In Progress – v0.2 (2025-06-15) – Basic spaCy entity-pair extractor live

## 1 Goal
Provide a micro-service that extracts relations (entity1, relation, entity2) from incident text (title + description + report snippets) to power the graph view in the ATRiAN dashboard.

## 2 Scope (MVP)
1. Input: list of strings OR Parquet dataframe row with `description` field.
2. Output: list of triples with offsets + confidence.
3. REST-like local endpoint (`/extract`) plus Python function for batch runs.
4. Model: spaCy `en_core_web_trf` + `spacy-projects` relation extraction config fine-tuned on the MITRE CRE dataset (public) – chosen for permissive license.
5. Packaging: Dockerfile for GPU/CPU, poetry dependencies.
6. Tests: unit (mock small text → known triples), integration (service endpoint), performance (<150 ms per document on CPU).

## 3 Architecture
```
+-------------------+
|  Dashboard Graph  | <-- HTTP JSON --> /extract
+-------------------+
        ^
        |
+-------------------+
| relation_service  |  (FastAPI + spaCy pipeline)
+-------------------+
```

## 4 Dependencies
* Python ≥3.11
* spaCy 3.7 + `en_core_web_trf`
* FastAPI + Uvicorn
* pydantic for schema

## 5 Tasks
| # | Task | Owner | Workflow |
|---|------|-------|----------|
|1|Design pydantic schemas|AI|/tdd_based_dev_workflow|
|2|Scaffold FastAPI service + healthcheck|AI|/tdd_based_dev_workflow|
|3|Load vanilla `en_core_web_trf` + test extractor stub|AI|/tdd_based_dev_workflow|
|4|Implement rule-based seed extractor (org → incident) as fallback|AI|/tdd_based_dev_workflow|
|5|Prepare fine-tune script with MITRE CRE|AI|/ai_assisted_research_and_synthesis|
|6|Containerize service|AI|N/A|
|7|Write unit & integration tests|AI|/tdd_based_dev_workflow|
|8|Hook dashboard call to endpoint|AI|iterative_code_refinement|

## 6 Cross-References
* `docs/datasets/ai_incident_db/README.md` – will supply text for extraction.
* `incident_pattern_dashboard.py` – placeholder for graph view.
* Workflow `/file_duplication_guard` used before creating any new module.

## 7 Risks & Mitigations
* **Model size** ▶ 500 MB – use lazy loading, allow CPU.
* **Latency** ▶ initial >300 ms – consider distil model or caching.
* **Licensing** ▶ verify MITRE CRE license (BSD-3) OK.

## 8 Timeline (MVP)
1. Scaffold + stub extractor – today
2. Basic rule-based + tests – today
3. Fine-tune script + Docker – +2 days
4. Dashboard wired – +3 days

---
*Created via `/ai_assisted_research_and_synthesis` + `/tdd_based_dev_workflow`.*
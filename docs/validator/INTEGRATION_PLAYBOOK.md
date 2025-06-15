---
title: Validator Integration Playbook
description: How to connect the Constitution Validator to CI, website, dashboard, and NATS events
status: Draft
version: 0.1.0
owner: DevOps & Integration Squad
last_updated: 2025-06-13
---

@references:
  - docs/validator/INTEGRATION_PLAYBOOK.md

> Cross-Refs:  
> • `ROADMAP.md#validator---compliance-track-2025-q3`  
> • `docs/validator/REST_API_SPEC.md`  
> • `brain/d113eca5-c9b2-44ca-accd-09beeb37a5fa/plan.md`

## 1. Local Development
1. `poetry install` in `ATRIAN/` (ensures FastAPI deps).  
2. Run:
```bash
uvicorn atrian.eaas_api:app --reload
```
3. Navigate to `http://localhost:8000/docs` for Swagger UI.

## 2. CI Pipeline Hook
```yaml
- name: Constitution Compliance Check
  run: |
    curl -X POST http://validator:8000/validate \
      -H "Content-Type: application/json" \
      -d '{"constitutions": ["base.yaml"], "prompt": "${{ secrets.TEST_PROMPT }}"}' |
      jq '.passed' | grep true
```
Fail pipeline if grep != true.

## 3. Website Embedding (Next.js)
```ts
const res = await fetch('/api/validator-proxy', {method: 'POST', body: JSON.stringify(payload)});
```
Proxy route lives in `website/src/pages/api/validator-proxy.ts`.

## 4. Real-time Dashboard Updates
* Subject: `validator.run.completed`  
* Payload: `{ validation_id, passed, overall_score, timestamp }`

Publish via:
```python
import nats
await nc.publish('validator.run.completed', json.dumps(event).encode())
```
`egos_dashboard` subscribes and updates “Validator Runs” card.
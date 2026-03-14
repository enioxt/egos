---
description: "Saves new knowledge and patterns to Memory MCP, documentation, and social channels."
---

# /disseminate — Knowledge Dissemination

> **Works in:** ANY EGOS repo
> **When to Use:** After implementing a feature, fixing a bug, making an architectural decision, or completing a milestone.
> **Repo-role:** Check `egos.config.json` for `role` and `surfaces`. If absent, assume `leaf` and skip surfaces like gem-hunter, report-generator, session:guard, and activation:check.

---

## 1. Identify New Knowledge

What was created or changed?

- **Infrastructure**: Docker, caching, ETL, deployment?
- **Feature**: New component, API endpoint, agent?
- **Architecture**: Design pattern, data flow, integration?
- **Bug fix**: Root cause, prevention mechanism?
- **Governance**: Security policy, workflow, meta-prompt?

## 2. Save to Cascade Memory

```ts
create_memory({
  Title: "Session — [description]",
  Content: "Detailed markdown with files, decisions, gotchas...",
  CorpusNames: ["enioxt/REPO_NAME"],
  Tags: ["relevant", "tags"],
  Action: "create"
})
```

## 3. Check Meta-Prompt Triggers

```text
Read .guarani/prompts/triggers.json
- Did any trigger apply this session?
- Should a new trigger be added?
- Was a meta-prompt useful? Document the outcome.
```

## 4. Update Documentation

- `docs/knowledge/HARVEST.md` — Add patterns, gotchas, learnings
- `TASKS.md` — Mark completed, add discovered tasks
- `.guarani/` — If architecture decisions were made
- Record Codex usage: availability, mode used (`review`, `read-only`, `cloud`), suggestions applied/rejected
- Record Alibaba orchestration status and whether the repo's readiness surface (`session:guard` when present, otherwise local activation checks) was updated
- If mesh, agents, workflows, or event-bus reality changed, include a `/mycelium` snapshot with maturity, connected systems, and drift notes

## 5. Post on Social Channels (if milestone)

Use `/postar` workflow for unified posting:

- **Telegram** (@ethikin): Full markdown, up to 4096 chars
- **Discord**: Markdown, up to 2000 chars
- **X.com** (@anoineim): 280 chars max + link

## 6. Update Bot/AI System Prompts (if applicable)

If new data sources, tools, or capabilities were added, update relevant system prompts.

## 7. Update Capability Registry (if applicable)

If a new capability was created, improved, or adopted:

- Update `egos/docs/CAPABILITY_REGISTRY.md` — add/modify capability entry with SSOT ref, quality rating, adoption status
- If chatbot-related, verify compliance with `egos/docs/modules/CHATBOT_SSOT.md`
- If a module was ported to `packages/shared/`, update the SSOT column in the registry

---

## Checklist

- [ ] Cascade Memory updated (create_memory)
- [ ] Meta-prompt triggers reviewed
- [ ] Codex usage recorded (or explicit reason why not used)
- [ ] TASKS.md updated
- [ ] Documentation updated (HARVEST.md, .guarani/)
- [ ] Capability Registry updated (if new capability created/adopted)
- [ ] Social channels posted (if milestone)

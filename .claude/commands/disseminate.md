# /disseminate — Knowledge Dissemination (EGOS v5.5)

> Use after: feature, bug fix, architecture decision, CVE mitigation, milestone

## 1. Identify New Knowledge
What was created or changed?
- Infrastructure, Feature, Architecture, Bug fix, Governance, SecOps?

## 2. Update HARVEST.md
Add patterns, gotchas, learnings to `docs/knowledge/HARVEST.md`

## 3. Check Meta-Prompt Triggers
```bash
cat .guarani/prompts/triggers.json 2>/dev/null | jq '.triggers | keys'
```
- Did any trigger apply this session?
- Should a new trigger be added?

## 4. Update TASKS.md
- Mark completed tasks
- Add newly discovered tasks

## 5. Update Capability Registry
If new capability created: update `docs/CAPABILITY_REGISTRY.md`

## 6. Save to Memory
Create memory file in `~/.claude/projects/-home-enio-egos/memory/` with key learnings

## 7. Social Channels (if milestone)
- Telegram: @ethikin (full markdown, up to 4096 chars)
- Discord: (markdown, up to 2000 chars)
- X.com: @anoineim (280 chars + link)

## Checklist
- [ ] HARVEST.md updated
- [ ] Meta-prompt triggers reviewed
- [ ] TASKS.md updated
- [ ] Capability Registry updated (if applicable)
- [ ] Memory saved
- [ ] Social posted (if milestone)

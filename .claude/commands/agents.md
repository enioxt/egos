# /agents — Agent Orchestration

## List all registered agents

```
claude /agents list
```

Returns: All agents from agents/registry/agents.json with status

## Run a specific agent

```
claude /agents run {agentId} --dry
claude /agents run {agentId} --exec
```

## Get agent info

```
claude /agents info {agentId}
```

## Check agent status

```
claude /agents status
```

## View agent logs

```
claude /agents logs {agentId}
```

---

**See Also:** `/start` (session activation), `/end` (cleanup)

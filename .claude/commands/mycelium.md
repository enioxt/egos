# /mycelium — Kernel Reality Check (EGOS)

Validate Mycelium mesh reality, references, and maturity.

## Steps:

1. **Check VPS Agents**
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no \
  "pm2 list && docker ps --format '{{.Names}}: {{.Status}}'"
```

2. **Check EGOS Kernel Sync**
```bash
bash /home/enio/egos/scripts/sync-all-leaf-repos.sh --check 2>/dev/null | tail -20
```

3. **Check Neo4j (Graph/Memory)**
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no \
  "docker exec bracc-neo4j cypher-shell -u neo4j 'MATCH (n) RETURN count(n) as nodes'"
```

4. **Maturity Table**
Output a maturity table:
| Layer | Status | Last verified | Notes |
|-------|--------|---------------|-------|
| PM2 Agents (Telegram/Discord) | ? | Now | - |
| Docker Services | ? | Now | - |
| Neo4j Graph | ? | Now | - |
| EGOS Kernel | ? | Now | - |
| Leaf Repos (11) | ? | Now | Drift |

5. **Drift Summary**
List any repos with governance drift and recommended action.

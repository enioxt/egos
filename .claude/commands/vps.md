# /vps — Connect & Manage Contabo VPS

Connect to VPS and inspect/manage agents.

## Quick Connect
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no
```

## Agents Overview

### PM2 Agents (via egos-lab)
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no "pm2 list"
```

| Agent | Path | Status | Purpose |
|-------|------|--------|---------|
| egos-telegram | /opt/egos-lab/apps/telegram-bot/src/index.ts | Online | Telegram bot |
| egos-discord | /opt/egos-lab/packages/shared/src/social/discord-bot.ts | Online | Discord bot |

### Docker Services
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no \
  "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

| Service | Port | Purpose |
|---------|------|---------|
| 852-app | :3001 (internal) | Chatbot |
| egos-media-web-1 | :3015 | Media nginx |
| waha-santiago | :3002 | WhatsApp API |
| infra-api-1 | :8000 (internal) | Main API |
| infra-frontend-1 | :3000 (internal) | Frontend |
| bracc-neo4j | :7474/:7687 (internal) | Neo4j/Mycelium |
| infra-caddy-1 | :80/:443 | Reverse proxy |
| infra-redis-1 | :6379 (internal) | Redis cache |

## Common Operations

### Restart PM2 agent
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no "pm2 restart egos-telegram"
```

### Check logs
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no \
  "pm2 logs egos-telegram --lines 20 --nostream"
```

### Docker service logs
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no \
  "docker logs 852-app --tail 20"
```

### Disk/RAM check
```bash
ssh -p 22 root@217.216.95.126 -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no \
  "df -h / && free -h"
```

## VPS Specs
- **IP:** 217.216.95.126
- **RAM:** 48 GB
- **Disk:** 484 GB (157 GB used, 33%)
- **OS:** Ubuntu 24.04 LTS (kernel 6.8)
- **Node:** v20.20.1

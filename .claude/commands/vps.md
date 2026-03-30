# /vps — Connect & Manage Hetzner VPS

Connect to VPS and inspect/manage agents.

> **IMPORTANTE:** Migração Contabo → Hetzner concluída em 2026-03-28.
> Novo IP: 204.168.217.125 | SSH key: ~/.ssh/hetzner_ed25519
> Contabo (217.216.95.126) — DESATIVADO

## Quick Connect
```bash
ssh root@hetzner -i ~/.ssh/hetzner_ed25519
# ou direto:
ssh root@204.168.217.125 -i ~/.ssh/hetzner_ed25519
```

## Agents Overview

### PM2 Agents (via egos-lab)
```bash
ssh root@hetzner "pm2 list"
```

| Agent | Path | Status | Purpose |
|-------|------|--------|---------|
| egos-telegram | /opt/egos-lab/apps/telegram-bot/src/index.ts | Online | Telegram bot |
| egos-discord | /opt/egos-lab/packages/shared/src/social/discord-bot.ts | Online | Discord bot |

### Docker Services
```bash
ssh root@hetzner "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

| Service | Port | Purpose |
|---------|------|---------|
| 852-app | :3001 (internal) | Chatbot |
| egos-media-web-1 | :3015 | Media nginx |
| waha-santiago | :3002 | WhatsApp API |
| infra-api-1 | :8000 (internal) | Main API |
| infra-frontend-1 | :3000 (internal) | Frontend |
| bracc-neo4j | :7474/:7687 (internal) | Neo4j/br-acc (OSINT graph — NOT part of Mycelium layer) |
| infra-caddy-1 | :80/:443 | Reverse proxy |
| infra-redis-1 | :6379 (internal) | Redis cache |

## Common Operations

### Restart PM2 agent
```bash
ssh root@hetzner "pm2 restart egos-telegram"
```

### Check logs
```bash
ssh root@hetzner "pm2 logs egos-telegram --lines 20 --nostream"
```

### Docker service logs
```bash
ssh root@hetzner "docker logs 852-app --tail 20"
```

### Disk/RAM check
```bash
ssh root@hetzner "df -h / && free -h"
```

## VPS Specs
- **IP:** 204.168.217.125
- **Provider:** Hetzner (migrado de Contabo em 2026-03-28)
- **RAM:** 24 GB
- **Disk:** 484 GB
- **OS:** Ubuntu 24.04 LTS
- **Node:** v20.20.1
- **SSH Key:** ~/.ssh/hetzner_ed25519

## Backup
Backups locais em: `/home/enio/vps-backup-hetzner/`
- `neo4j-data-20260327.tar.gz` (~1GB) — Neo4j dump
- `caddy-data.tar.gz` — SSL certs
- `852.env`, `bracc.env` — credenciais de prod
- `Caddyfile`, `docker-compose-*.yml`

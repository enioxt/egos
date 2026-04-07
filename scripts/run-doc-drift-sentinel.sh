#!/bin/bash
# EGOS Doc-Drift Sentinel — cron wrapper
set -e
cd /home/enio/egos
exec /usr/bin/bun agents/agents/doc-drift-sentinel.ts "$@"

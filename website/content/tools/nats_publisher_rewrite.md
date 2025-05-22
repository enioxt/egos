---
title: NATS Publisher Tool for EGOS
description: This script simulates various EGOS subsystems publishing events to NATS topics.
It can be used to te...
date: 2025-05-22
lastmod: 2025-05-22
draft: false
images: []
categories: [Utility]
toc: true
---

# NATS Publisher Tool for EGOS

**Status**: INACTIVE

**Path**: `tools/nats_publisher_rewrite.py`

**Category**: Utility

**Maintainer**: EGOS Development Team

## Description

This script simulates various EGOS subsystems publishing events to NATS topics.
It can be used to test the dashboard live data functionality without requiring
the actual subsystems to be running.
Usage:
python nats_publisher.py --topic egos.sparc.tasks --count 5 --interval 2
python nats_publisher.py --topic egos.llm.logs --count 3
python nats_publisher.py --topic egos.propagation.log --count 2 --interval 5
Topics:
- egos.sparc.tasks: SPARC task events
- egos.llm.logs: LLM interaction logs
- egos.propagation.log: System propagation events
@references:
- Core References:
- [MQP.md](mdc:../../MQP.md) - Master Quantum Prompt defining EGOS principles
- [ROADMAP.md](mdc:../../ROADMAP.md) - Project roadmap and planning


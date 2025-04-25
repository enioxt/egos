"""TODO: Module docstring for __init__.py"""
# EGOS Import Resilience: see docs/process/dynamic_import_resilience.md
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
EGOS Mycelium Network
---------------------
The central communication infrastructure for EGOS subsystems.

The Mycelium Network provides standardized, decentralized messaging between
all EGOS subsystems while maintaining observability, reliability, and security.

EGOS Principles Applied:
- Conscious Modularity: Well-defined interfaces between components
- Systemic Cartography: Tracing message flows across the system
- Reciprocal Trust: Reliable message delivery with acknowledgments
- Sacred Privacy: Protecting message integrity and privacy
"""

__version__ = "1.0.0"
__author__ = "EGOS Development Team"

from subsystems.MYCELIUM.core.message import (
    MyceliumMessage,
    MyceliumRequestMessage,
    create_direct_message,
    create_topic_message,
    create_request_message,
    create_broadcast_message
)
from subsystems.MYCELIUM.core.client import (
    MyceliumClient,
    ClientStatus,
    ClientConfig,
    create_client,
    SubscriptionId
)
from subsystems.MYCELIUM.core.broker import (
    MyceliumBroker,
    BrokerConfig,
    ConnectionStatus,
    create_broker
)

__all__ = [
    # Message module
    "MyceliumMessage",
    "MyceliumRequestMessage",
    "create_direct_message",
    "create_topic_message",
    "create_request_message",
    "create_broadcast_message",

    # Client module
    "MyceliumClient",
    "ClientStatus",
    "ClientConfig",
    "create_client",
    "SubscriptionId",

    # Broker module
    "MyceliumBroker",
    "BrokerConfig",
    "ConnectionStatus",
    "create_broker"
]
"""Blocos A2A (Agent2Agent 1.0) dos serviços de IA. Requer o extra `a2a`."""

from ai_lib.a2a.card import Skill, build_agent_card
from ai_lib.a2a.client import DelegationError, DelegationResult, delegate
from ai_lib.a2a.executor import (
    TurnExecutor,
    TurnReply,
    TurnRequest,
    bearer_token,
    persona_of,
)
from ai_lib.a2a.server import mount_a2a

__all__ = [
    "DelegationError",
    "DelegationResult",
    "Skill",
    "TurnExecutor",
    "TurnReply",
    "TurnRequest",
    "bearer_token",
    "build_agent_card",
    "delegate",
    "mount_a2a",
    "persona_of",
]

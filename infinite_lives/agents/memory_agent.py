from __future__ import annotations

from uuid import uuid4

from infinite_lives.agents.base import BaseAgent
from infinite_lives.domain.models import AgentProposal, EpisodicMemoryEntry, MemoryWriteCommand, TurnContext


class MemoryAgent(BaseAgent):
    agent_id = "memory-agent"
    agent_name = "MemoryAgent"

    async def on_turn_start(self, context: TurnContext) -> list[AgentProposal]:
        entry = EpisodicMemoryEntry(
            entry_id=str(uuid4()),
            turn_id=0,
            event_summary="A new turn began.",
            importance_score=0.2,
            entities_involved=["player"],
            emotional_valence=0.0,
            is_long_term=False,
        )
        return [
            AgentProposal(
                agent_id=self.agent_id,
                proposed_commands=[MemoryWriteCommand(entry=entry)],
                confidence=0.7,
                touched_entities=["memory"],
                reasoning="Record episodic trace.",
            )
        ]

    async def on_event(self, event):
        return []

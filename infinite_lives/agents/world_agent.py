from __future__ import annotations

from infinite_lives.agents.base import BaseAgent
from infinite_lives.domain.models import AgentProposal, TurnContext, WorldAdvanceCommand


class WorldAgent(BaseAgent):
    agent_id = "world-agent"
    agent_name = "WorldAgent"

    async def on_turn_start(self, context: TurnContext) -> list[AgentProposal]:
        cmd = WorldAdvanceCommand(turns=1, reason="turn progression")
        return [AgentProposal(agent_id=self.agent_id, proposed_commands=[cmd], confidence=0.95, touched_entities=["world"], reasoning="Advance world time.")]

    async def on_event(self, event):
        return []

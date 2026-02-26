from __future__ import annotations

from infinite_lives.agents.base import BaseAgent
from infinite_lives.domain.models import AgentProposal, NPCBehaviorCommand, TurnContext


class CharacterAgent(BaseAgent):
    def __init__(self, npc_id: str) -> None:
        self.npc_id = npc_id
        self.agent_id = f"character-agent-{npc_id}"
        self.agent_name = "CharacterAgent"

    async def on_turn_start(self, context: TurnContext) -> list[AgentProposal]:
        cmd = NPCBehaviorCommand(npc_id=self.npc_id, action_type="observe", target="player")
        return [AgentProposal(agent_id=self.agent_id, proposed_commands=[cmd], confidence=0.6, touched_entities=[self.npc_id], reasoning="Routine autonomous behavior.")]

    async def on_event(self, event):
        return []

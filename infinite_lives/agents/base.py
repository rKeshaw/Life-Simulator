from __future__ import annotations

from infinite_lives.domain.models import AgentProposal, AgentStatus, SimulationEvent, TurnContext


class BaseAgent:
    agent_id: str
    agent_name: str

    async def on_turn_start(self, context: TurnContext) -> list[AgentProposal]:
        raise NotImplementedError

    async def on_event(self, event: SimulationEvent) -> list[AgentProposal]:
        raise NotImplementedError

    async def get_status(self) -> AgentStatus:
        return AgentStatus(agent_id=self.agent_id, agent_name=self.agent_name, healthy=True)

from __future__ import annotations

from infinite_lives.agents.base import BaseAgent
from infinite_lives.domain.models import AgentProposal, WorldFactAssertCommand


class ConsistencyAgent(BaseAgent):
    agent_id = "consistency-agent"
    agent_name = "ConsistencyAgent"

    async def on_turn_start(self, context):
        return []

    async def on_event(self, event):
        return []

    def proposal_allowed(self, proposal: AgentProposal, facts: list[tuple[str, str, str]]) -> bool:
        for command in proposal.proposed_commands:
            if isinstance(command, WorldFactAssertCommand):
                for subject, predicate, obj in facts:
                    if (
                        command.fact.subject == subject
                        and command.fact.predicate == predicate
                        and command.fact.object != obj
                    ):
                        return False
        return True

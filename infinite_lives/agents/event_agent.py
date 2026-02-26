from __future__ import annotations

from infinite_lives.agents.base import BaseAgent


class EventAgent(BaseAgent):
    agent_id = "event-agent"
    agent_name = "EventAgent"

    async def on_turn_start(self, context):
        return []

    async def on_event(self, event):
        return []

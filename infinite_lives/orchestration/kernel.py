from __future__ import annotations

import asyncio
from uuid import uuid4

from infinite_lives.agents.character_agent import CharacterAgent
from infinite_lives.agents.consistency_agent import ConsistencyAgent
from infinite_lives.agents.event_agent import EventAgent
from infinite_lives.agents.memory_agent import MemoryAgent
from infinite_lives.agents.narrator_agent import NarratorAgent
from infinite_lives.agents.world_agent import WorldAgent
from infinite_lives.core.commands import validate_command
from infinite_lives.core.event_store import EventStore
from infinite_lives.core.projections import project_npcs, project_player_state, project_world_state
from infinite_lives.domain.models import (
    AgentProposal,
    NarratorContext,
    PlayerActionCommand,
    SimulationEvent,
    SimulationEventKind,
    TurnContext,
    WorldFact,
)
from infinite_lives.logging_setup import log_event


class OrchestrationKernel:
    def __init__(self, session_id: str, logger, narrator: NarratorAgent, event_store: EventStore) -> None:
        self.session_id = session_id
        self.logger = logger
        self.narrator = narrator
        self.event_store = event_store
        self.turn_id = 1
        self.facts: list[WorldFact] = []
        self.world_agent = WorldAgent()
        self.event_agent = EventAgent()
        self.memory_agent = MemoryAgent()
        self.consistency_agent = ConsistencyAgent()
        self.character_agents = [CharacterAgent("npc-1")]

    async def _build_context(self) -> TurnContext:
        events = await self.event_store.all_events()
        return TurnContext(
            player_state=project_player_state(events),
            world_state=project_world_state(events),
            active_npcs=project_npcs(events),
            recent_memories=[],
            relevant_world_facts=self.facts,
        )

    async def run_turn(self, raw_input: str) -> str:
        player_command = PlayerActionCommand(raw_input=raw_input, turn_id=self.turn_id, session_id=self.session_id)
        validate_command(player_command, self.facts)
        context = await self._build_context()
        log_event(self.logger, "player_action", self.turn_id, {"input": raw_input})

        relevant_agents = [self.world_agent, self.event_agent, self.memory_agent, *self.character_agents]
        proposals = await self._collect_proposals(relevant_agents, context)
        committed = self._resolve_conflicts(proposals)

        committed_events = [
            SimulationEvent(
                event_id=str(uuid4()),
                event_type=SimulationEventKind.TRIGGERED,
                description=f"Player action: {raw_input}",
                causal_source="player_action",
                affected_entities=["player"],
                turn_id=self.turn_id,
                payload={"player": {"current_location": context.world_state.location}},
            )
        ]
        for proposal in committed:
            for command in proposal.proposed_commands:
                committed_events.append(
                    SimulationEvent(
                        event_id=str(uuid4()),
                        event_type=SimulationEventKind.TRIGGERED,
                        description=f"{proposal.agent_id} committed {command.__class__.__name__}",
                        causal_source=proposal.agent_id,
                        affected_entities=proposal.touched_entities,
                        turn_id=self.turn_id,
                        payload={},
                    )
                )

        for event in committed_events:
            await self.event_store.append(event)
            log_event(self.logger, "world_state_update", self.turn_id, {"event": event.model_dump(mode='json')})

        narrated = await self.narrator.narrate(
            NarratorContext(
                committed_delta=committed_events,
                world_state=context.world_state,
                sensory_perspective=f"Turn {self.turn_id}: {raw_input}",
            )
        )
        self.turn_id += 1
        return narrated

    async def _collect_proposals(self, agents, context: TurnContext) -> list[AgentProposal]:
        async def call(agent):
            try:
                return await asyncio.wait_for(agent.on_turn_start(context), timeout=8)
            except TimeoutError:
                log_event(self.logger, "agent_timeout", self.turn_id, {"agent_id": agent.agent_id})
                return []

        proposal_lists = await asyncio.gather(*(call(agent) for agent in agents))
        return [proposal for proposals in proposal_lists for proposal in proposals]

    def _resolve_conflicts(self, proposals: list[AgentProposal]) -> list[AgentProposal]:
        allowed: list[AgentProposal] = []
        fact_tuples = [(fact.subject, fact.predicate, fact.object) for fact in self.facts]
        touched = set()
        for proposal in sorted(proposals, key=lambda p: p.confidence, reverse=True):
            if not self.consistency_agent.proposal_allowed(proposal, fact_tuples):
                log_event(self.logger, "consistency_violation", self.turn_id, {"proposal": proposal.model_dump(mode='json')})
                continue
            key = tuple(sorted(proposal.touched_entities))
            if key in touched:
                continue
            touched.add(key)
            allowed.append(proposal)
        return allowed

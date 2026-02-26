from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class FactConfidence(str, Enum):
    CERTAIN = "certain"
    INFERRED = "inferred"
    RUMORED = "rumored"


class SimulationEventKind(str, Enum):
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"
    EMERGENT = "emergent"


class PlayerState(BaseModel):
    identity: str = "Wanderer"
    energy: int = 100
    stress: int = 0
    reputation: int = 50
    age: int = 18
    health: int = 100
    active_abilities: list[str] = Field(default_factory=list)
    current_location: str = "Unknown"
    era: str = "Present"
    world_rules_declared_at_start: list[str] = Field(default_factory=list)


class WorldState(BaseModel):
    era: str = "Present"
    location: str = "Unknown"
    active_physical_laws: list[str] = Field(default_factory=lambda: ["causality"])
    societal_rules: list[str] = Field(default_factory=list)
    weather: str = "clear"
    time_of_day: str = "day"
    calendar_date: str = "0001-01-01"


class NPCProfile(BaseModel):
    npc_id: str
    name: str
    age: int = 30
    personality_traits: list[str] = Field(default_factory=list)
    current_goals: list[str] = Field(default_factory=list)
    emotional_state: str = "neutral"
    relationship_to_player_scalar: float = 0.0
    relationship_to_player_descriptor: str = "stranger"
    memory_summary: str = ""


class SimulationEvent(BaseModel):
    event_id: str
    event_type: SimulationEventKind
    description: str
    causal_source: str
    affected_entities: list[str] = Field(default_factory=list)
    turn_id: int
    payload: dict[str, Any] = Field(default_factory=dict)


class EpisodicMemoryEntry(BaseModel):
    entry_id: str
    turn_id: int
    event_summary: str
    importance_score: float = Field(ge=0.0, le=1.0)
    entities_involved: list[str] = Field(default_factory=list)
    emotional_valence: float = Field(ge=-1.0, le=1.0, default=0.0)
    is_long_term: bool = False


class WorldFact(BaseModel):
    fact_id: str
    subject: str
    predicate: str
    object: str
    established_on_turn: int
    confidence: FactConfidence = FactConfidence.CERTAIN


class SoulState(BaseModel):
    lives_lived: int = 0
    total_turns: int = 0
    understanding_score: float = Field(default=0.0, ge=0.0, le=1.0)
    themes_encountered: list[str] = Field(default_factory=list)
    nirvana_reached: bool = False


class PlayerActionCommand(BaseModel):
    raw_input: str
    turn_id: int
    session_id: str


class WorldAdvanceCommand(BaseModel):
    turns: int
    reason: str


class NPCBehaviorCommand(BaseModel):
    npc_id: str
    action_type: str
    target: str


class MemoryWriteCommand(BaseModel):
    entry: EpisodicMemoryEntry


class WorldFactAssertCommand(BaseModel):
    fact: WorldFact


Command = PlayerActionCommand | WorldAdvanceCommand | NPCBehaviorCommand | MemoryWriteCommand | WorldFactAssertCommand


class AgentProposal(BaseModel):
    agent_id: str
    proposed_commands: list[Command]
    confidence: float = Field(ge=0.0, le=1.0)
    touched_entities: list[str] = Field(default_factory=list)
    reasoning: str


class AgentStatus(BaseModel):
    agent_id: str
    agent_name: str
    healthy: bool
    detail: str = ""


class TurnContext(BaseModel):
    player_state: PlayerState
    world_state: WorldState
    active_npcs: list[NPCProfile] = Field(default_factory=list)
    recent_memories: list[EpisodicMemoryEntry] = Field(default_factory=list)
    relevant_world_facts: list[WorldFact] = Field(default_factory=list)


class NarratorContext(BaseModel):
    committed_delta: list[SimulationEvent]
    world_state: WorldState
    sensory_perspective: str


class LLMUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0


class LLMResponse(BaseModel):
    content: str
    usage: LLMUsage
    model: str
    prompt_type: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

from __future__ import annotations

from infinite_lives.domain.models import NPCProfile, PlayerState, SimulationEvent, WorldState


def project_player_state(events: list[SimulationEvent]) -> PlayerState:
    state = PlayerState()
    for event in events:
        payload = event.payload
        if event.causal_source == "player_action":
            state.energy = max(0, state.energy - 1)
        if "player" in payload:
            state = state.model_copy(update=payload["player"])
    return state


def project_world_state(events: list[SimulationEvent]) -> WorldState:
    state = WorldState()
    for event in events:
        payload = event.payload
        if "world" in payload:
            state = state.model_copy(update=payload["world"])
    return state


def project_npcs(events: list[SimulationEvent]) -> list[NPCProfile]:
    npc_map: dict[str, NPCProfile] = {}
    for event in events:
        payload = event.payload
        if "npc" in payload:
            npc = NPCProfile.model_validate(payload["npc"])
            npc_map[npc.npc_id] = npc
    return list(npc_map.values())

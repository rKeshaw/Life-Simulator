from infinite_lives.core.projections import project_player_state, project_world_state
from infinite_lives.domain.models import SimulationEvent, SimulationEventKind


def test_projections_player_and_world_state():
    events = [
        SimulationEvent(
            event_id="1",
            event_type=SimulationEventKind.TRIGGERED,
            description="player moved",
            causal_source="player_action",
            affected_entities=["player"],
            turn_id=1,
            payload={"player": {"current_location": "Market"}, "world": {"weather": "rain"}},
        )
    ]
    player = project_player_state(events)
    world = project_world_state(events)

    assert player.current_location == "Market"
    assert player.energy == 99
    assert world.weather == "rain"

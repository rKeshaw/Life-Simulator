import pytest

from infinite_lives.core.event_store import EventStore
from infinite_lives.domain.models import SimulationEvent, SimulationEventKind


@pytest.mark.asyncio
async def test_event_store_append_and_replay(tmp_path):
    db = tmp_path / "events.db"
    store = EventStore(str(db))
    await store.init()

    event = SimulationEvent(
        event_id="e1",
        event_type=SimulationEventKind.TRIGGERED,
        description="something happened",
        causal_source="test",
        affected_entities=["player"],
        turn_id=1,
        payload={"x": 1},
    )
    await store.append(event)

    replayed = await store.replay_from(1)
    assert len(replayed) == 1
    assert replayed[0].event_id == "e1"

from infinite_lives.agents.witness_agent import WitnessAgent
from infinite_lives.domain.models import EpisodicMemoryEntry, SoulState


def test_witness_increases_understanding_score():
    witness = WitnessAgent()
    soul = SoulState(understanding_score=0.1)
    memories = [
        EpisodicMemoryEntry(
            entry_id="m1",
            turn_id=1,
            event_summary="A profound act of compassion",
            importance_score=0.9,
            entities_involved=["player", "npc"],
            emotional_valence=0.8,
            is_long_term=True,
        )
    ]

    _, updated = witness.reflect(memories, soul)
    assert updated.understanding_score > soul.understanding_score

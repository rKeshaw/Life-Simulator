from __future__ import annotations

from infinite_lives.domain.models import EpisodicMemoryEntry, SoulState


class WitnessAgent:
    def reflect(self, memories: list[EpisodicMemoryEntry], soul_state: SoulState, nirvana_threshold: float = 0.85) -> tuple[str, SoulState]:
        if memories:
            delta = sum(m.importance_score for m in memories) / len(memories)
        else:
            delta = 0.0
        updated = soul_state.model_copy()
        updated.lives_lived += 1
        updated.total_turns += len(memories)
        updated.understanding_score = min(1.0, updated.understanding_score + delta * 0.1)
        updated.nirvana_reached = updated.understanding_score >= nirvana_threshold
        summary = "Your life echoes across the soul."
        if updated.nirvana_reached:
            summary += " A profound stillness settles: Nirvana is reached."
        return summary, updated

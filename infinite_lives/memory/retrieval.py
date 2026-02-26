from __future__ import annotations

from rank_bm25 import BM25Okapi

from infinite_lives.domain.models import EpisodicMemoryEntry


class MemoryRetriever:
    def __init__(self, entries: list[EpisodicMemoryEntry]) -> None:
        self.entries = entries
        corpus = [entry.event_summary.lower().split() for entry in entries] or [["empty"]]
        self.bm25 = BM25Okapi(corpus)

    def get_relevant(self, query: str, top_k: int) -> list[EpisodicMemoryEntry]:
        if not self.entries:
            return []
        scores = self.bm25.get_scores(query.lower().split())
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        return [self.entries[idx] for idx, _ in ranked[:top_k]]

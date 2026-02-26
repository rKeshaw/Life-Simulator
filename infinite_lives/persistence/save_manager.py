from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
from typing import Any

from infinite_lives.domain.models import SimulationEvent, SoulState, WorldFact


class SaveManager:
    schema_version = "1.0.0"

    def save_snapshot(
        self,
        path: str,
        session_id: str,
        soul_state: SoulState,
        event_store_snapshot: list[SimulationEvent],
        world_facts: list[WorldFact],
    ) -> None:
        payload = {
            "schema_version": self.schema_version,
            "session_id": session_id,
            "soul_state": soul_state.model_dump(),
            "event_store_snapshot": [e.model_dump(mode="json") for e in event_store_snapshot],
            "world_facts": [f.model_dump(mode="json") for f in world_facts],
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    def load_snapshot(self, path: str) -> dict[str, Any]:
        if path.endswith(".pkl"):
            return self._migrate_pickle(path)
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    def _migrate_pickle(self, path: str) -> dict[str, Any]:
        with open(path, "rb") as fh:
            legacy = pickle.load(fh)
        migrated = {
            "schema_version": self.schema_version,
            "session_id": legacy.get("session_id", "legacy-session"),
            "soul_state": SoulState().model_dump(),
            "event_store_snapshot": [],
            "world_facts": [],
            "legacy_payload": legacy,
        }
        migrated_path = str(Path(path).with_suffix(".json"))
        with open(migrated_path, "w", encoding="utf-8") as fh:
            json.dump(migrated, fh, indent=2)
        return migrated

    def save_soul_state(self, player_id: str, soul_state: SoulState) -> str:
        path = f"saves/soul_{player_id}.json"
        Path("saves").mkdir(exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(soul_state.model_dump(mode="json"), fh, indent=2)
        return path

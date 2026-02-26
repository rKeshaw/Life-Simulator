from __future__ import annotations

import json

import aiosqlite

from infinite_lives.domain.models import SimulationEvent


class EventStore:
    def __init__(self, db_path: str = "saves/event_store.db") -> None:
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_events (
                    idx INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    causal_source TEXT NOT NULL,
                    affected_entities TEXT NOT NULL,
                    turn_id INTEGER NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def append(self, event: SimulationEvent) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO simulation_events (
                    event_id, event_type, description, causal_source,
                    affected_entities, turn_id, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type.value,
                    event.description,
                    event.causal_source,
                    json.dumps(event.affected_entities),
                    event.turn_id,
                    json.dumps(event.payload),
                ),
            )
            await db.commit()

    async def _query(self, sql: str, params: tuple = ()) -> list[SimulationEvent]:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(sql, params)
            rows = await cur.fetchall()
        return [
            SimulationEvent(
                event_id=r[0],
                event_type=r[1],
                description=r[2],
                causal_source=r[3],
                affected_entities=json.loads(r[4]),
                turn_id=r[5],
                payload=json.loads(r[6]),
            )
            for r in rows
        ]

    async def get_since(self, turn_id: int) -> list[SimulationEvent]:
        return await self._query(
            """
            SELECT event_id, event_type, description, causal_source, affected_entities, turn_id, payload
            FROM simulation_events WHERE turn_id >= ? ORDER BY idx ASC
            """,
            (turn_id,),
        )

    async def get_by_type(self, event_type: str) -> list[SimulationEvent]:
        return await self._query(
            """
            SELECT event_id, event_type, description, causal_source, affected_entities, turn_id, payload
            FROM simulation_events WHERE event_type = ? ORDER BY idx ASC
            """,
            (event_type,),
        )

    async def replay_from(self, turn_id: int) -> list[SimulationEvent]:
        return await self.get_since(turn_id)

    async def all_events(self) -> list[SimulationEvent]:
        return await self._query(
            """
            SELECT event_id, event_type, description, causal_source, affected_entities, turn_id, payload
            FROM simulation_events ORDER BY idx ASC
            """
        )

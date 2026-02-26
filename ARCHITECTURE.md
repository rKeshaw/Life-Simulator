# Legacy Architecture Reverse Engineering (Pre-Agentic)

This document captures the existing prototype architecture before the migration to the new agent-native Infinite Lives core.

## Component map

- `game.py` (`IntelligentLifeSim`)
  - Central owner of all runtime state (player stats, world variables, NPC relationships, memories, API client, loop controls).
  - Owns game loop, command parsing, world updates, and rendering orchestration.
- `ai_response.py`
  - Prompt construction and response generation via direct LLM calls.
- `memory.py`
  - Short/long-term memory composition, memory retrieval from local/cloud context.
- `npc.py`, `behavior_tree.py`
  - NPC definitions, behavior choices, and ad hoc autonomous interactions.
- `environment.py`
  - Environment type inference, flora/fauna/weather setup.
- `idle.py`
  - Idle-time simulation and skip-forward world updates.
- `save_load.py`
  - Local pickle save/load and save metadata generation.
- `cloud_memory.py`, `auth_system.py`
  - Supabase-backed authentication and cloud persistence fallback.
- `gui.py`
  - Tkinter UI using the same core game object.

## Data flow

1. Player enters text input.
2. `IntelligentLifeSim` parses command and mutates internal dict/list state.
3. Memory/NPC/environment systems are called as helper modules, but all read/write through `self.game` references.
4. LLM prompts are assembled in multiple modules and sent directly to `self.game.client.chat.completions.create`.
5. Response text is printed to terminal/GUI.
6. Save/load writes or reads pickle snapshots of mixed mutable state.

## State ownership

The `IntelligentLifeSim` class owns almost every meaningful state variable:

- Player metrics: energy/stress/reputation/day/action counters.
- World metrics: weather/economy/environment type/flora/fauna/events.
- Memory: short-term deque, long-term list, world facts list, relationships dict.
- Temporal tools: undo/temporal energy/save states.
- NPC runtime data and social parameters.
- Personality style and mood adaptation.

Subsystem modules do not encapsulate independent state stores; they mutate the central object.

## LLM call points

Direct model invocations are spread across:

- `ai_response.py`
- `memory.py`
- `npc.py`
- `idle.py`
- `save_load.py`

All currently bypass a unified gateway, and instrumentation/typed errors are not centralized.

## Save/load behavior

- Local saves are pickle files (`lifesim_*.pkl`) with ad hoc dictionaries.
- Cloud saves are mediated via Supabase memory records.
- No schema-versioned snapshot format and no event-log replay mechanism.

## Runtime topology summary

- One central orchestrator class.
- Many helper systems sharing mutable state by reference.
- No command/event boundary.
- No append-only event store.
- No deterministic projection model.
- No autonomous agent proposal + veto + commit flow.

## Bottlenecks and risks

1. **Scalability bottleneck**: monolithic class with tightly coupled responsibilities.
2. **State consistency risk**: direct mutation across modules; no transactional boundary.
3. **Debuggability gap**: no structured event logs with turn/session IDs.
4. **Reliability gap**: broad `except Exception` usage; no typed LLM exceptions.
5. **Persistence fragility**: pickle snapshots not ideal for evolvable schema/versioning.
6. **Agentic limitations**: no domain ownership model or proposal-based orchestration.
7. **Replay limitations**: cannot reliably reconstruct state from first principles.


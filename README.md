# Infinite Lives

**Vision**: simulate any life possible, for any being, at any point in time.

Infinite Lives is an agent-native life simulation platform prototype. The player does not interact with an assistant—they experience a coherent world whose domains are managed by autonomous agents and committed through an event-sourced kernel.

## Architecture (high level)

```
Player Input
   |
   v
OrchestrationKernel
   |-- routes turn context to agents asynchronously
   |-- collects AgentProposals
   |-- applies ConsistencyAgent veto + conflict resolution
   |-- commits SimulationEvents to EventStore (SQLite)
   v
State Projections (deterministic)
   |
   v
NarratorAgent (read-only)
   |
   v
Terminal Experience
```

### Agent Domains
- WorldAgent: world/time/rule progression
- CharacterAgent: autonomous NPC behavior
- EventAgent: scheduling/triggering/emergence scaffolding
- MemoryAgent: episodic writes and retrieval interface
- ConsistencyAgent: hard coherence veto
- NarratorAgent: read-only experiential narration
- WitnessAgent: life-boundary reflection and soul progression

## Run the game

```bash
python -m infinite_lives.main
```

## Run tests

```bash
pytest -q
```

## Notes

This repository is the **text-based foundation** for a future 3D world-model-driven platform.

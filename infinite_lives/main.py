from __future__ import annotations

import asyncio
import uuid

from infinite_lives.agents.narrator_agent import NarratorAgent
from infinite_lives.core.event_store import EventStore
from infinite_lives.llm.gateway import LLMGateway
from infinite_lives.logging_setup import configure_logging
from infinite_lives.orchestration.kernel import OrchestrationKernel


async def run_game() -> None:
    session_id = str(uuid.uuid4())
    logger = configure_logging(session_id)
    event_store = EventStore()
    await event_store.init()
    narrator = NarratorAgent(LLMGateway(logger=logger))
    kernel = OrchestrationKernel(session_id=session_id, logger=logger, narrator=narrator, event_store=event_store)

    print("\n🌌 Infinite Lives (Agentic Core Prototype)")
    print("Type actions. Use 'quit' to end.\n")

    while True:
        raw_input_text = input("> ").strip()
        if raw_input_text.lower() in {"quit", "q"}:
            print("The life pauses at the edge of another beginning.")
            break
        if not raw_input_text:
            continue
        narration = await kernel.run_turn(raw_input_text)
        print(narration)


if __name__ == "__main__":
    asyncio.run(run_game())

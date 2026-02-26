from __future__ import annotations

from infinite_lives.domain.models import NarratorContext
from infinite_lives.llm.gateway import LLMGateway


class NarratorAgent:
    def __init__(self, gateway: LLMGateway) -> None:
        self.gateway = gateway

    async def narrate(self, context: NarratorContext) -> str:
        response = await self.gateway.llm_call(
            prompt_type="narration",
            messages=[{"role": "system", "content": "Narrate committed state only."}],
            model="local-prototype",
            metadata={
                "turn_id": context.committed_delta[-1].turn_id if context.committed_delta else 0,
                "fallback_content": f"\033[96m{context.sensory_perspective}\033[0m",
            },
        )
        return response.content

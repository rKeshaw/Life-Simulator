from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from infinite_lives.domain.models import LLMResponse, LLMUsage
from infinite_lives.logging_setup import log_event


class LLMCallError(RuntimeError):
    pass


@dataclass
class LLMGateway:
    logger: Any

    async def llm_call(
        self,
        prompt_type: str,
        messages: list[dict[str, str]],
        model: str,
        metadata: dict[str, Any],
    ) -> LLMResponse:
        start = time.perf_counter()
        try:
            # Placeholder deterministic response for the prototype migration stage.
            content = metadata.get("fallback_content", "The world shifts quietly around you.")
            input_tokens = sum(len(m.get("content", "").split()) for m in messages)
            output_tokens = len(content.split())
            latency_ms = (time.perf_counter() - start) * 1000
            usage = LLMUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                estimated_cost_usd=round((input_tokens + output_tokens) * 0.000001, 6),
            )
            log_event(
                self.logger,
                event_type="llm_call",
                turn_id=metadata.get("turn_id", 0),
                payload={
                    "prompt_type": prompt_type,
                    "model": model,
                    "usage": usage.model_dump(),
                },
            )
            return LLMResponse(content=content, usage=usage, model=model, prompt_type=prompt_type)
        except (TypeError, ValueError) as exc:
            raise LLMCallError(f"LLM call failed: {exc}") from exc

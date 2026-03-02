from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm


class ReviewResult(BaseModel):
    verdict: Literal["pass", "fail"]
    issues: List[str] = Field(default_factory=list)
    tone_alignment_score: float = Field(ge=0.0, le=1.0)
    structure_ok: bool


SYSTEM = """You are a strict but fair email reviewer.

Evaluate the draft for:
1) Tone adherence to tone_contract
2) Structure: greeting/context/body/sign-off (CTA depends on intent)
3) Unfounded claims (anything not supported by parsed_request or metadata)

Intent-specific rules:
- follow_up / meeting_request / outreach / escalation: MUST include a clear CTA (what you want + timeframe if available).
- thank_you: CTA is OPTIONAL. A soft closing like 'Happy to help if you need anything' is fine.
- status_update: CTA optional unless user explicitly asked for an action.

Tone rules:
- Do NOT flag professional gratitude phrases (e.g., 'sincere gratitude') as casual.
- Only flag tone issues when they clearly contradict the tone_contract (e.g., slang in formal tone).

If issues exist, provide clear bullet issues and set verdict=fail.
"""


def review_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.0)

    draft = state.get("draft") or {}
    parsed = state.get("parsed_request") or {}
    metadata = state.get("metadata") or {}
    tone_contract = state.get("tone_contract") or {}
    intent = state.get("intent") or {}

    model = llm.with_structured_output(ReviewResult)

    payload = {
        "draft": draft,
        "parsed_request": parsed,
        "metadata": metadata,
        "tone_contract": tone_contract,
        "intent": intent,
    }

    review: ReviewResult = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"Review this email draft:\n{payload}"),
        ]
    )
    attempt = state.get("retries", 0) + 1

    trace = state.get("trace", [])
    trace.append(f"✅ Review: {review.verdict.upper()} (tone_score={review.tone_alignment_score:.2f})")

    review_history = state.get("review_history", [])
    review_history.append({"attempt": attempt, **review.model_dump()})

    return {"trace": trace, "review": review.model_dump(), "review_history": review_history}
from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm


class ReviewResult(BaseModel):
    verdict: Literal["pass", "fail"]
    issues: List[str] = Field(default_factory=list)
    tone_alignment_score: float = Field(ge=0.0, le=1.0)
    structure_ok: bool


SYSTEM = """You are a strict email reviewer.
Evaluate the draft for:
1) Tone adherence to tone_contract
2) Structure: greeting/context/ask/CTA/sign-off
3) Unfounded claims (anything not supported by parsed_request or metadata)
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

    trace = state.get("trace", [])
    trace.append(f"✅ Review: {review.verdict.upper()} (tone_score={review.tone_alignment_score:.2f})")

    return {"trace": trace, "review": review.model_dump()}
from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm
from src.mcp.mcp_server import mcp


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

Intent-specific CTA rules:
- follow_up / meeting_request / outreach / escalation: MUST include a clear CTA (what you want + timeframe if available).
- thank_you: CTA is OPTIONAL. A soft line like 'Please feel free to share feedback' or 'Happy to help' is enough.
- status_update: CTA optional unless user explicitly asked for an action.

Tone rules (important):
- Do NOT fail an email simply because it is warm, appreciative, or uses gratitude language.
- Only mark tone as FAIL if it contains clearly casual/unprofessional elements.
- If tone is slightly off but still professional, prefer PASS.

If issues exist, provide clear bullet issues and set verdict=fail.
"""


def review_node(state: Dict[str, Any]) -> Dict[str, Any]:

    llm = get_llm(temperature=0.0)

    draft = state.get("draft") or {}
    parsed = state.get("parsed_request") or {}
    metadata = state.get("metadata") or {}
    tone_contract = state.get("tone_contract") or {}
    intent_obj = state.get("intent") or {}

    intent = intent_obj.get("intent")

    draft_body = draft.get("body", "")

    model = llm.with_structured_output(ReviewResult)

    payload = {
        "draft": draft,
        "parsed_request": parsed,
        "metadata": metadata,
        "tone_contract": tone_contract,
        "intent": intent_obj,
    }

    # ---------------------------
    # LLM Review
    # ---------------------------
    review: ReviewResult = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"Review this email draft:\n{payload}"),
        ]
    )

    issues = list(review.issues)

    # ---------------------------
    # MCP Policy Validation
    # ---------------------------
    try:

        policy_result = mcp.call(
            "policy.check",
            {
                "email_text": draft_body,
                "intent": intent,
            },
        )

        if not policy_result.get("pass", True):

            issues.extend(policy_result.get("issues", []))

    except Exception:
        # MCP failure should not break review
        pass

    # ---------------------------
    # Final Verdict Adjustment
    # ---------------------------
    final_verdict = review.verdict

    if issues:
        final_verdict = "fail"

    # ---------------------------
    # Trace + History
    # ---------------------------
    attempt = state.get("retries", 0) + 1

    trace = state.get("trace", [])
    trace.append(
        f"✅ Review: {final_verdict.upper()} (tone_score={review.tone_alignment_score:.2f})"
    )

    review_history = state.get("review_history", [])

    review_history.append(
        {
            "attempt": attempt,
            "verdict": final_verdict,
            "issues": issues,
            "tone_alignment_score": review.tone_alignment_score,
            "structure_ok": review.structure_ok,
        }
    )

    return {
        "trace": trace,
        "review": {
            "verdict": final_verdict,
            "issues": issues,
            "tone_alignment_score": review.tone_alignment_score,
            "structure_ok": review.structure_ok,
        },
        "review_history": review_history,
    }
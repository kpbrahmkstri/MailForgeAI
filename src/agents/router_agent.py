from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class RouterDecision(BaseModel):
    next_step: Literal["final", "revise", "ask_user"]
    reason: str
    clarification_question: Optional[str] = None


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    review = state.get("review") or {}
    missing = state.get("missing_info") or []
    retries = state.get("retries", 0)
    max_retries = state.get("max_retries", 1)

    verdict = review.get("verdict", "pass")

    # If critical missing info exists AND the draft likely depends on it, ask user.
    # For MVP: if more than 2 missing fields, we ask the user instead of guessing.
    if len(missing) >= 3:
        decision = RouterDecision(
            next_step="ask_user",
            reason="Too much critical information is missing to draft confidently.",
            clarification_question=f"I can draft this, but I’m missing: {', '.join(missing)}. What should I use?",
        )
    elif verdict == "fail" and retries < max_retries:
        # Retry once: send back to DraftWriter with reviewer issues already in state["review"]
        decision = RouterDecision(
            next_step="revise",
            reason="Draft failed review; retrying with reviewer feedback.",
        )
        state["retries"] = retries + 1
    else:
        # Finalize
        draft = state.get("draft") or {}
        subject = (draft.get("subject") or "").strip()
        body = (draft.get("body") or "").strip()

        final = ""
        if subject:
            final += f"Subject: {subject}\n\n"
        final += body

        decision = RouterDecision(next_step="final", reason="Draft is ready to deliver.")
        state["final_output"] = final

    trace = state.get("trace", [])
    trace.append(f"✅ Router: next_step={decision.next_step} (retries={state.get('retries', retries)}/{max_retries})")

    return {
        "trace": trace,
        "router": decision.model_dump(),
        "clarification_question": decision.clarification_question,
        "final_output": state.get("final_output"),
        "retries": state.get("retries", retries),
    }
from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


class RouterDecision(BaseModel):
    next_step: Literal["final", "revise", "ask_user"]
    reason: str
    clarification_question: Optional[str] = None


def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # --- Pull state ---
    parsed = state.get("parsed_request") or {}
    intent_obj = state.get("intent") or {}
    intent = (intent_obj.get("intent") or "").strip()

    review = state.get("review") or {}
    verdict = review.get("verdict", "pass")

    missing = state.get("missing_info") or []
    retries = state.get("retries", 0)
    max_retries = state.get("max_retries", 1)

    # --- Critical fields we should not placeholder for certain intents ---
    recipient_name = (parsed.get("recipient_name") or "").strip()
    # Recipient name is critical only for these intents
    critical_intents = {"follow_up", "outreach", "meeting_request", "escalation"}

    if intent in critical_intents and not recipient_name:
        decision = RouterDecision(
            next_step="ask_user",
            reason="Recipient name is required for this intent to avoid placeholders.",
            clarification_question=(
                "Who is the recipient (name) and what’s the desired response/timeframe?\n"
                "Example: 'Kinjal; please review and reply by Friday.'"
            ),
        )
        trace = state.get("trace", [])
        trace.append(f"✅ Router: next_step={decision.next_step} (critical missing recipient_name)")
        return {
            "trace": trace,
            "router": decision.model_dump(),
            "clarification_question": decision.clarification_question,
            "final_output": None,
            "retries": retries,
        }

    # --- Generic missing info threshold ---
    if len(missing) >= 3:
        decision = RouterDecision(
            next_step="ask_user",
            reason="Too much critical information is missing to draft confidently.",
            clarification_question=f"I can draft this, but I’m missing: {', '.join(missing)}. What should I use?",
        )
        trace = state.get("trace", [])
        trace.append(f"✅ Router: next_step={decision.next_step} (missing_info >= 3)")
        return {
            "trace": trace,
            "router": decision.model_dump(),
            "clarification_question": decision.clarification_question,
            "final_output": None,
            "retries": retries,
        }

    # --- Retry on review failure if we still have retries left ---
    if verdict == "fail" and retries < max_retries:
        decision = RouterDecision(
            next_step="revise",
            reason="Draft failed review; retrying with reviewer feedback.",
        )
        state["retries"] = retries + 1
        trace = state.get("trace", [])
        trace.append(f"✅ Router: next_step={decision.next_step} (retries={state['retries']}/{max_retries})")
        return {
            "trace": trace,
            "router": decision.model_dump(),
            "clarification_question": None,
            "final_output": None,
            "retries": state["retries"],
        }

    # --- Step 6.2: If still FAIL after retries, ask user instead of finalizing a failed draft ---
    if verdict == "fail":
        issues = review.get("issues", [])
        issue_text = "; ".join(issues[:3]) if issues else "quality checks failed"

        # Intent-aware clarification prompt
        if intent == "thank_you":
            clarification = (
                "One quick detail can make this thank-you email more personal:\n"
                "Do you want to mention any specific outcome (e.g., how many friends, or what they said)?\n"
                f"(Reason: {issue_text})"
            )
        else:
            clarification = (
                "One detail will help me fix this fast:\n"
                "What exactly should the recipient do next (CTA) and by when?\n"
                f"(Reason: {issue_text})"
            )

        decision = RouterDecision(
            next_step="ask_user",
            reason="Draft still failing validation after retries.",
            clarification_question=clarification,
        )
        trace = state.get("trace", [])
        trace.append(f"✅ Router: next_step={decision.next_step} (fail after retries)")
        return {
            "trace": trace,
            "router": decision.model_dump(),
            "clarification_question": decision.clarification_question,
            "final_output": None,
            "retries": retries,
        }
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm


class IntentResult(BaseModel):
    intent: str = Field(description="One of: outreach, follow_up, apology, status_update, meeting_request, escalation, thank_you, other")
    confidence: float = Field(ge=0.0, le=1.0)
    template_hint: str = Field(description="Short guidance on structure/sections to include.")


SYSTEM = """You are an intent classifier for an email drafting assistant.
Choose the closest intent from the allowed set.
Output a template_hint that helps the writer structure the email.
"""


def intent_detection_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.0)

    intent_override = state.get("intent_override")
    if intent_override:
        trace = state.get("trace", [])
        trace.append(f"✅ IntentDetection: overridden by user -> {intent_override}")
        return {"trace": trace, "intent": {"intent": intent_override, "confidence": 1.0, "template_hint": "Use user-provided intent."}}

    parsed = state.get("parsed_request") or {}
    model = llm.with_structured_output(IntentResult)

    result: IntentResult = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"Parsed request:\n{parsed}"),
        ]
    )

    trace = state.get("trace", [])
    trace.append(f"✅ IntentDetection: {result.intent} (conf={result.confidence:.2f})")

    return {"trace": trace, "intent": result.model_dump()}
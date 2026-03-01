from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm


class DraftEmail(BaseModel):
    subject: str
    body: str
    assumptions_used: List[str] = Field(default_factory=list)


SYSTEM = """You are an expert email writer.
Write a complete email with:
- a strong subject line
- a clear body (greeting, context, ask, CTA, sign-off)
Rules:
- Follow the tone_contract strictly.
- Use parsed_request and user_profile fields; do not invent facts.
- If missing info exists, either (a) write with minimal assumptions or (b) phrase it as a question.
- Keep it professional and easy to scan.
"""


def draft_writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.4)

    parsed = state.get("parsed_request") or {}
    intent = state.get("intent") or {}
    tone_contract = state.get("tone_contract") or {}
    profile = state.get("user_profile") or {}
    metadata = state.get("metadata") or {}

    # If we are retrying after review, include reviewer notes to improve draft
    review = state.get("review") or {}
    reviewer_notes = review.get("issues", [])

    model = llm.with_structured_output(DraftEmail)

    prompt = {
        "parsed_request": parsed,
        "intent": intent,
        "tone_contract": tone_contract,
        "user_profile": profile,
        "metadata": metadata,
        "reviewer_notes_to_fix_if_any": reviewer_notes,
    }

    draft: DraftEmail = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"Draft the email from the following input:\n{prompt}"),
        ]
    )

    # append signature if not already present
    signature = (profile.get("signature") or "").strip()
    body = draft.body.strip()
    if signature and signature not in body:
        body = body.rstrip() + "\n\n" + signature

    trace = state.get("trace", [])
    attempt = state.get("retries", 0) + 1
    trace.append(f"✅ DraftWriter: produced draft (attempt {attempt})")

    return {
        "trace": trace,
        "draft": {
            "subject": draft.subject.strip(),
            "body": body,
            "assumptions_used": draft.assumptions_used,
        },
    }
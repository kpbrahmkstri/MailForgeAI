from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm
from src.utils.email_postprocess import enforce_single_signoff


class DraftEmail(BaseModel):
    subject: str
    subject_options: List[str] = Field(default_factory=list)
    body: str
    assumptions_used: List[str] = Field(default_factory=list)


SYSTEM = """You are an expert email writer.
Write a complete email with:
- a strong subject line
- 3 subject options (subject_options) and pick the best as subject
- a clear body (greeting, context, ask, CTA, sign-off)

Rules:
- Follow the tone_contract strictly.
- Use parsed_request and user_profile fields; do not invent facts.
- Use retrieved_templates as the primary structure when provided.
- If missing info exists, either (a) write with minimal assumptions or (b) phrase it as a question.
- Keep it professional and easy to scan.
- If the user_profile provides a signature, use it. Do not add multiple sign-offs.
- For follow_up intent: include an explicit CTA that asks for a concrete response (e.g., confirm receipt, provide feedback) and a timeframe if provided.
- If recipient_name is unknown, address the email generically (e.g., "Hello," or "Hi there,") instead of using placeholders like [Recipient's Name].
"""


def draft_writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.4)

    parsed = state.get("parsed_request") or {}
    intent_obj = state.get("intent") or {}
    tone_contract = state.get("tone_contract") or {}
    profile = state.get("user_profile") or {}
    style_prefs = profile.get("style_preferences") or {}
    metadata = state.get("metadata") or {}

    # RAG
    retrieved_templates = state.get("retrieved_templates", []) or []

    # If we are retrying after review, include reviewer notes to improve draft
    review = state.get("review") or {}
    reviewer_notes = review.get("issues", [])

    model = llm.with_structured_output(DraftEmail)

    prompt = {
        "parsed_request": parsed,
        "intent": intent_obj,
        "tone_contract": tone_contract,
        "user_profile": profile,
        "style_preferences": style_prefs,
        "metadata": metadata,
        "retrieved_templates": retrieved_templates,
        "rag_instruction": (
            "Use the retrieved_templates as the primary structure. "
            "Pick the single best matching template and adapt it. "
            "Do not copy placeholders literally; fill using parsed_request/metadata or ask questions naturally."
        ),
        "subject_instruction": (
            "Return 3 distinct subject options in subject_options and choose the best as subject."
        ),
        "reviewer_notes_to_fix_if_any": reviewer_notes,
    }

    draft: DraftEmail = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"Draft the email from the following input:\n{prompt}"),
        ]
    )

    # Enforce one and only one sign-off/signature block (testable utility)
    body = enforce_single_signoff(draft.body, tone_contract, profile)

    trace = state.get("trace", [])
    attempt = state.get("retries", 0) + 1
    trace.append(f"✅ DraftWriter: produced draft (attempt {attempt})")

    # Keep subject options tidy (max 3)
    subject_options = [s.strip() for s in (draft.subject_options or []) if s and s.strip()]
    subject = (draft.subject or "").strip()
    if subject and subject not in subject_options:
        subject_options = [subject] + subject_options
    subject_options = subject_options[:3]

    # Save history (for UI attempts panel)
    draft_history = state.get("draft_history", [])
    draft_history.append(
        {
            "attempt": attempt,
            "subject": subject,
            "subject_options": subject_options,
            "body": body,
            "assumptions_used": draft.assumptions_used,
        }
    )

    return {
        "trace": trace,
        "draft_history": draft_history,
        "draft": {
            "subject": subject,
            "subject_options": subject_options,
            "body": body,
            "assumptions_used": draft.assumptions_used,
        },
    }
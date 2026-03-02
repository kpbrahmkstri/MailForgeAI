from __future__ import annotations

import re
from typing import Any, Dict, List

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
- If the user_profile provides a signature, use it. Do not add multiple sign-offs.
"""


# --------------------------
# Sign-off utilities
# --------------------------
_CLOSING_PATTERNS = [
    r"^sincerely[,]?$",
    r"^best[,]?$",
    r"^best regards[,]?$",
    r"^regards[,]?$",
    r"^kind regards[,]?$",
    r"^warm regards[,]?$",
    r"^thanks[,]?$",
    r"^thank you[,]?$",
    r"^cordially[,]?$",
]

_PLACEHOLDER_PATTERNS = [
    r"\[your name\]",
    r"<your name>",
    r"\[name\]",
    r"\{your name\}",
]


def _normalize_lines(text: str) -> List[str]:
    return [ln.rstrip() for ln in text.strip().splitlines()]


def _has_signoff_near_end(text: str, tail_lines: int = 12) -> bool:
    """
    Detect whether there is a closing line near the end of the draft.
    Looks at the last N non-empty lines and checks against known closing patterns.
    """
    lines = [ln.strip() for ln in _normalize_lines(text) if ln.strip()]
    tail = lines[-tail_lines:]
    for ln in tail:
        l = ln.strip().lower()
        for pat in _CLOSING_PATTERNS:
            if re.match(pat, l):
                return True
    return False


def _find_placeholder_signoff_block(text: str) -> bool:
    """
    Detect placeholders like '[Your Name]' near the end.
    """
    lower = text.lower()
    return any(re.search(pat, lower) for pat in _PLACEHOLDER_PATTERNS)


def _remove_trailing_placeholder_block(text: str) -> str:
    """
    Remove obvious placeholder sign-off blocks at the very end, e.g.:
    'Sincerely, [Your Name]' or similar 1-3 line endings.
    """
    lines = _normalize_lines(text)
    # Work on last ~6 lines only to avoid accidentally removing mid-body content
    prefix = lines[:-6]
    tail = lines[-6:]

    # Join tail for pattern removal
    tail_text = "\n".join(tail)

    # Remove common placeholder patterns if they appear in tail
    # e.g., "Sincerely, [Your Name]" or "Best,\n[Your Name]"
    cleaned = tail_text
    cleaned = re.sub(r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*\n?\s*\[your name\]\s*$", "", cleaned).strip()
    cleaned = re.sub(r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*\[your name\]\s*$", "", cleaned).strip()

    # Also remove generic "<Your Name>" endings
    cleaned = re.sub(r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*\n?\s*<your name>\s*$", "", cleaned).strip()
    cleaned = re.sub(r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*<your name>\s*$", "", cleaned).strip()

    # Rebuild text
    rebuilt_tail = cleaned.strip()
    rebuilt_lines = prefix + ([rebuilt_tail] if rebuilt_tail else [])
    return "\n".join([ln for ln in rebuilt_lines if ln is not None]).strip()


def _compose_signoff_block(tone_contract: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """
    Build a single sign-off block. Priority:
    1) profile.signature (if present)
    2) tone_contract.signoff_style + profile.name (if name exists)
    3) fallback "Regards," + profile.name (if name exists)
    """
    profile_signature = (profile.get("signature") or "").strip()
    if profile_signature:
        return profile_signature

    closing = (tone_contract.get("signoff_style") or "").strip()
    name = (profile.get("name") or "").strip()

    if closing:
        # Ensure it ends with a comma for nicer formatting (optional)
        if not closing.endswith(","):
            closing = closing + ","
        if name:
            return f"{closing}\n{name}"
        return closing

    if name:
        return f"Regards,\n{name}"
    return "Regards,"


# --------------------------
# Main agent node
# --------------------------
def draft_writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.4)

    parsed = state.get("parsed_request") or {}
    intent = state.get("intent") or {}
    tone_contract = state.get("tone_contract") or {}
    profile = state.get("user_profile") or {}
    style_prefs = profile.get("style_preferences") or {}
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
        "style_preferences": style_prefs,
        "metadata": metadata,
        "reviewer_notes_to_fix_if_any": reviewer_notes,
    }

    draft: DraftEmail = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"Draft the email from the following input:\n{prompt}"),
        ]
    )

    body = draft.body.strip()

    # 1) If placeholders exist at the end, remove them (we will add our own correct signoff)
    if _find_placeholder_signoff_block(body):
        body = _remove_trailing_placeholder_block(body)

    # 2) If draft already has a closing/signature near the end, do NOT append another.
    #    This prevents duplicates like "Sincerely..." + "Best..."
    if not _has_signoff_near_end(body):
        signoff_block = _compose_signoff_block(tone_contract, profile)
        body = body.rstrip() + "\n\n" + signoff_block

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
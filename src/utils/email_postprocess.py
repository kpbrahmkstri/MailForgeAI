import re
from typing import Dict, Any, List


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


def has_signoff_near_end(text: str, tail_lines: int = 12) -> bool:
    lines = [ln.strip() for ln in _normalize_lines(text) if ln.strip()]
    tail = lines[-tail_lines:]
    for ln in tail:
        l = ln.strip().lower()
        for pat in _CLOSING_PATTERNS:
            if re.match(pat, l):
                return True
    return False


def has_placeholder_signoff(text: str) -> bool:
    lower = text.lower()
    return any(re.search(pat, lower) for pat in _PLACEHOLDER_PATTERNS)


def remove_trailing_placeholder_block(text: str) -> str:
    lines = _normalize_lines(text)
    prefix = lines[:-6]
    tail = lines[-6:]
    tail_text = "\n".join(tail)

    cleaned = tail_text
    cleaned = re.sub(
        r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*\n?\s*\[your name\]\s*$",
        "",
        cleaned,
    ).strip()
    cleaned = re.sub(
        r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*\[your name\]\s*$",
        "",
        cleaned,
    ).strip()

    cleaned = re.sub(
        r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*\n?\s*<your name>\s*$",
        "",
        cleaned,
    ).strip()
    cleaned = re.sub(
        r"(?is)\n?\s*(sincerely|best|best regards|regards|kind regards|warm regards|thanks|thank you)[,]?\s*<your name>\s*$",
        "",
        cleaned,
    ).strip()

    rebuilt_tail = cleaned.strip()
    rebuilt_lines = prefix + ([rebuilt_tail] if rebuilt_tail else [])
    return "\n".join([ln for ln in rebuilt_lines if ln is not None]).strip()


def compose_signoff_block(tone_contract: Dict[str, Any], profile: Dict[str, Any]) -> str:
    profile_signature = (profile.get("signature") or "").strip()
    if profile_signature:
        return profile_signature

    closing = (tone_contract.get("signoff_style") or "").strip()
    name = (profile.get("name") or "").strip()

    if closing:
        if not closing.endswith(","):
            closing = closing + ","
        if name:
            return f"{closing}\n{name}"
        return closing

    if name:
        return f"Regards,\n{name}"
    return "Regards,"


def enforce_single_signoff(body: str, tone_contract: Dict[str, Any], profile: Dict[str, Any]) -> str:
    body = body.strip()

    if has_placeholder_signoff(body):
        body = remove_trailing_placeholder_block(body)

    if not has_signoff_near_end(body):
        body = body.rstrip() + "\n\n" + compose_signoff_block(tone_contract, profile)

    return body
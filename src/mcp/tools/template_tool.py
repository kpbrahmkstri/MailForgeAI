from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

from src.mcp.registry import register_tool


TEMPLATE_PATH = Path("data/kb/templates")


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    cleaned = (
        text.lower()
        .replace("\n", " ")
        .replace("|", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace(":", " ")
        .replace(";", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("{", " ")
        .replace("}", " ")
        .replace("[", " ")
        .replace("]", " ")
        .replace("/", " ")
        .replace("-", " ")
    )
    return [tok.strip() for tok in cleaned.split() if tok.strip()]


def _extract_header_metadata(text: str) -> Dict[str, str]:
    """
    Expects first line like:
    # follow_up | formal
    """
    lines = text.splitlines()
    if not lines:
        return {"intent": "", "tone": ""}

    first = lines[0].strip().lower()
    if first.startswith("#"):
        first = first[1:].strip()

    if "|" in first:
        parts = [p.strip() for p in first.split("|", 1)]
        return {
            "intent": parts[0] if len(parts) > 0 else "",
            "tone": parts[1] if len(parts) > 1 else "",
        }

    return {"intent": first.strip(), "tone": ""}


def _score_template(
    template_text: str,
    template_name: str,
    query: str,
    intent: str | None,
    tone: str | None,
) -> int:
    score = 0
    text_lower = template_text.lower()
    name_lower = template_name.lower()

    meta = _extract_header_metadata(template_text)
    template_intent = meta.get("intent", "")
    template_tone = meta.get("tone", "")

    # Strong intent match
    if intent:
        intent = intent.lower().strip()
        if intent == template_intent:
            score += 10
        elif intent in text_lower or intent in name_lower:
            score += 6

    # Tone match
    if tone:
        tone = tone.lower().strip()
        if tone == template_tone:
            score += 5
        elif tone in text_lower or tone in name_lower:
            score += 2

    # Query token overlap
    query_tokens = _tokenize(query)
    stopwords = {
        "a", "an", "the", "to", "of", "for", "on", "in", "and", "or",
        "is", "are", "was", "were", "be", "as", "with", "about", "last",
        "week", "email", "write", "draft", "send", "please"
    }

    useful_tokens = [tok for tok in query_tokens if tok not in stopwords and len(tok) > 2]

    for tok in useful_tokens:
        if tok in text_lower:
            score += 2
        elif tok in name_lower:
            score += 1

    return score


def search_templates(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    MCP tool: templates.search

    payload:
    {
        "query": "...",
        "intent": "follow_up",
        "tone": "formal"
    }
    """
    query = (payload.get("query") or "").strip()
    intent = (payload.get("intent") or "").strip()
    tone = (payload.get("tone") or "").strip()

    if not TEMPLATE_PATH.exists():
        return []

    results: List[Dict[str, Any]] = []

    for f in TEMPLATE_PATH.glob("*.md"):
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue

        score = _score_template(
            template_text=text,
            template_name=f.name,
            query=query,
            intent=intent,
            tone=tone,
        )

        # Keep only somewhat relevant templates
        if score > 0:
            meta = _extract_header_metadata(text)
            results.append(
                {
                    "source": f.name,
                    "content": text,
                    "score": score,
                    "intent": meta.get("intent", ""),
                    "tone": meta.get("tone", ""),
                }
            )

    # Sort best first
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # Fallback: if nothing matched, return first 3 templates
    if not results:
        fallback = []
        for f in TEMPLATE_PATH.glob("*.md"):
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue

            meta = _extract_header_metadata(text)
            fallback.append(
                {
                    "source": f.name,
                    "content": text,
                    "score": 0,
                    "intent": meta.get("intent", ""),
                    "tone": meta.get("tone", ""),
                }
            )
        return fallback[:3]

    return results[:3]


register_tool("templates.search", search_templates)
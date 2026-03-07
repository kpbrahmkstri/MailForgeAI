from pathlib import Path
from src.mcp.registry import register_tool


TEMPLATE_PATH = Path("data/kb/templates")


def search_templates(payload: dict):
    query = payload.get("query", "").lower()
    intent = payload.get("intent")

    results = []

    for f in TEMPLATE_PATH.glob("*.md"):
        text = f.read_text()

        if intent and intent not in text.lower():
            continue

        if query and query not in text.lower():
            continue

        results.append({
            "source": f.name,
            "content": text
        })

    return results[:3]


register_tool("templates.search", search_templates)
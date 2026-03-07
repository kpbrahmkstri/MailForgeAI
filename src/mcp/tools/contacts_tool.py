import json
from pathlib import Path
from src.mcp.registry import register_tool


CONTACTS_FILE = Path("data/kb/contacts.json")


def lookup_contact(payload: dict):
    name = payload.get("name", "").lower()

    if not CONTACTS_FILE.exists():
        return None

    data = json.loads(CONTACTS_FILE.read_text())

    return data.get(name)


register_tool("contacts.lookup", lookup_contact)
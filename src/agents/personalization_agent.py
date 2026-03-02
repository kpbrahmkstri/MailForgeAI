from __future__ import annotations

import json
import os
from typing import Any, Dict
from src.memory.memory_store import get_profile

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "memory", "user_profiles.json")


def _load_profiles() -> Dict[str, Any]:
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def personalization_node(state: Dict[str, Any]) -> Dict[str, Any]:
    user_id = state.get("user_id", "default")
    profile = get_profile(user_id)

    trace = state.get("trace", [])
    trace.append("✅ Personalization: loaded user profile + learned preferences")

    return {"trace": trace, "user_profile": profile}
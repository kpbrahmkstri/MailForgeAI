import json
from pathlib import Path
from typing import Any, Dict, Optional

from src.utils.path_utils import get_user_profiles_path


MEMORY_PATH = get_user_profiles_path()


def load_profiles() -> Dict[str, Any]:
    if not MEMORY_PATH.exists():
        return {}
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(profiles: Dict[str, Any]) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)


def get_profile(user_id: str = "default") -> Dict[str, Any]:
    profiles = load_profiles()
    return profiles.get(user_id) or profiles.get("default") or {}


def _infer_length_pref(text: str) -> str:
    words = len(text.split())
    if words <= 90:
        return "short"
    if words <= 180:
        return "medium"
    return "long"


def _infer_format_pref(text: str) -> str:
    # crude but effective
    if "\n- " in text or "\n•" in text:
        return "bullets"
    return "paragraph"


def update_profile_from_edits(user_id: str, generated: str, edited: str) -> Dict[str, Any]:
    """
    Lightweight learning:
    - preferred length
    - preferred format (bullets vs paragraph)
    - preferred sign-off style (last 2 lines)
    """
    profiles = load_profiles()
    profile = profiles.get(user_id) or profiles.get("default") or {}

    style = profile.get("style_preferences") or {}
    style["length"] = _infer_length_pref(edited)
    style["format"] = _infer_format_pref(edited)

    # infer sign-off (last 2 non-empty lines)
    lines = [ln.strip() for ln in edited.splitlines() if ln.strip()]
    if len(lines) >= 2:
        signoff_guess = "\n".join(lines[-2:])
        # store only if it looks like a signoff (contains name-ish or common closing)
        common = ["thanks", "thank you", "best", "regards", "sincerely", "cheers"]
        if any(c in signoff_guess.lower() for c in common):
            profile["signature"] = signoff_guess

    profile["style_preferences"] = style
    profiles[user_id] = profile
    save_profiles(profiles)
    return profile
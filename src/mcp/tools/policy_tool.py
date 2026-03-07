from src.mcp.registry import register_tool


def policy_check(payload: dict):
    text = payload.get("email_text", "")
    intent = payload.get("intent")

    issues = []

    if intent == "follow_up":
        if "confirm" not in text.lower() and "reply" not in text.lower():
            issues.append("Follow-up email should request confirmation or reply.")

    if "[your name]" in text.lower():
        issues.append("Placeholder '[Your Name]' detected.")

    if text.lower().count("sincerely") > 1:
        issues.append("Duplicate sign-off detected.")

    if intent == "meeting_request":
        if "available" not in text.lower() and "schedule" not in text.lower():
            issues.append(
                "Meeting request should suggest availability or scheduling options."
            )

    return {
        "issues": issues,
        "pass": len(issues) == 0
    }


register_tool("policy.check", policy_check)
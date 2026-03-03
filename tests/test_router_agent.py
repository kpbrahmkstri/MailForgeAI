import pytest
from src.agents.router_agent import router_node


def base_state():
    return {
        "parsed_request": {},
        "intent": {"intent": "follow_up"},
        "review": {"verdict": "pass", "issues": []},
        "missing_info": [],
        "retries": 0,
        "max_retries": 1,
        "draft": {"subject": "Sub", "body": "Body"},
        "trace": [],
    }


def test_router_asks_user_when_recipient_missing_for_follow_up():
    state = base_state()
    state["parsed_request"] = {"recipient_name": ""}  # missing
    out = router_node(state)
    assert out["router"]["next_step"] == "ask_user"
    assert "recipient" in (out["clarification_question"] or "").lower()


def test_router_revises_when_review_fail_and_retries_remaining():
    state = base_state()
    state["parsed_request"] = {"recipient_name": "Kinjal"}
    state["review"] = {"verdict": "fail", "issues": ["Signoff mismatch"]}
    state["retries"] = 0
    state["max_retries"] = 1

    out = router_node(state)
    assert out["router"]["next_step"] == "revise"
    assert out["retries"] == 1


def test_router_asks_user_when_review_fail_after_retries_exhausted():
    state = base_state()
    state["parsed_request"] = {"recipient_name": "Kinjal"}
    state["review"] = {"verdict": "fail", "issues": ["CTA missing"]}
    state["retries"] = 1
    state["max_retries"] = 1

    out = router_node(state)
    assert out["router"]["next_step"] == "ask_user"
    assert "cta" in (out["clarification_question"] or "").lower() or "detail" in (out["clarification_question"] or "").lower()


def test_router_finalizes_only_when_pass():
    state = base_state()
    state["parsed_request"] = {"recipient_name": "Kinjal"}
    state["review"] = {"verdict": "pass", "issues": []}
    out = router_node(state)
    assert out["router"]["next_step"] == "final"
    assert "Subject:" in (out["final_output"] or "")
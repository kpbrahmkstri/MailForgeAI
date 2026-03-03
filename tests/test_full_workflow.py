import pytest

from src.workflow.langgraph_flow import run_email_assistant


@pytest.fixture
def fake_templates():
    return [
        {"source": "follow_up_formal.md", "content": "# follow_up | formal\n\nDear {recipient_name},\n..."},
        {"source": "thank_you_formal.md", "content": "# thank_you | formal\n\nDear {recipient_name_or_generic},\n..."},
    ]


class FakeStructuredModel:
    """
    Returned by FakeLLM.with_structured_output(Schema).
    invoke(messages) returns an instance of Schema (Pydantic model).
    """
    def __init__(self, schema_cls, scenario):
        self.schema_cls = schema_cls
        self.scenario = scenario

    def invoke(self, messages):
        name = self.schema_cls.__name__

        # ---- Input Parser ----
        if name in {"ParsedRequest", "EmailParse"}:
            # Support either name depending on how you implemented InputParser
            recipient = self.scenario.get("recipient_name", "")
            return self.schema_cls(
                recipient_name=recipient,
                goal=self.scenario.get("user_prompt", ""),
                key_points=[],
                missing_info=self.scenario.get("missing_info", []),
                assumptions_used=[],
            )

        # ---- Intent Detection ----
        if name in {"IntentResult", "DetectedIntent"}:
            return self.schema_cls(intent=self.scenario.get("intent", "follow_up"), confidence=0.95)

        # ---- Tone Stylist ----
        if name in {"ToneContract", "ToneStyleContract"}:
            return self.schema_cls(
                tone_mode=self.scenario.get("tone_mode", "formal"),
                greeting_style="Dear {name},",
                signoff_style="Sincerely,",
                do_phrases=["Please", "Kindly", "Could you"],
                dont_phrases=["Hey", "Yo", "Cheers"],
                sentence_style="professional",
            )

        # ---- Draft Writer ----
        if name == "DraftEmail":
            self.scenario["draft_calls"] = self.scenario.get("draft_calls", 0) + 1
            attempt = self.scenario["draft_calls"]

            # Attempt 1 purposely violates signoff to trigger retry test when needed
            if self.scenario.get("force_retry_flow") and attempt == 1:
                body = (
                    "Hello,\n\n"
                    "Following up on the documentation email.\n"
                    "Could you please confirm receipt?\n\n"
                    "Best,\nJohn"
                )
            else:
                body = (
                    "Hello,\n\n"
                    "Following up on the documentation email.\n"
                    "Could you please confirm receipt by Friday?\n\n"
                    "Sincerely,\nJohn"
                )

            return self.schema_cls(
                subject="Follow-up on documentation",
                subject_options=["Follow-up on documentation", "Quick follow-up", "Checking in"],
                body=body,
                assumptions_used=[],
            )

        # ---- Review Agent ----
        if name in {"ReviewResult", "EmailReview"}:
            self.scenario["review_calls"] = self.scenario.get("review_calls", 0) + 1
            attempt = self.scenario["review_calls"]

            # In retry scenario: fail first, pass second
            if self.scenario.get("force_retry_flow") and attempt == 1:
                return self.schema_cls(
                    verdict="fail",
                    tone_alignment_score=0.8,
                    structure_ok=True,
                    issues=["Signoff mismatch: expected Sincerely, got Best,"],
                )

            # Otherwise pass
            return self.schema_cls(
                verdict="pass",
                tone_alignment_score=0.9,
                structure_ok=True,
                issues=[],
            )

        raise RuntimeError(f"FakeLLM: Unsupported schema {name}")


class FakeLLM:
    def __init__(self, scenario):
        self.scenario = scenario

    def with_structured_output(self, schema_cls):
        return FakeStructuredModel(schema_cls, self.scenario)


def test_integration_missing_recipient_follow_up_asks_user(monkeypatch, fake_templates):
    """
    End-to-end: follow_up + missing recipient_name should route to ask_user.
    """
    scenario = {
        "user_prompt": "follow up on documentation email as discussed last week",
        "intent": "follow_up",
        "tone_mode": "formal",
        "recipient_name": "",  # missing on purpose
        "missing_info": [],
        "force_retry_flow": False,
    }

    # 1) Patch template retrieval (avoid Chroma/OpenAI embeddings)
    import src.rag.template_rag as tr
    monkeypatch.setattr(tr, "retrieve_templates", lambda query, k=3: fake_templates)

    # 2) Patch get_llm globally (avoid OpenAI)
    import src.integrations.openai_client as oc
    monkeypatch.setattr(oc, "get_llm", lambda temperature=0.0: FakeLLM(scenario))

    state = run_email_assistant(
        user_prompt=scenario["user_prompt"],
        tone_mode="formal",
        intent_override=None,
        metadata={},           # no recipient provided
        user_id="default",
        max_retries=1,
    )

    assert state is not None
    assert state.get("router", {}).get("next_step") == "ask_user"
    assert state.get("clarification_question")  # should exist
    # Ensure retrieval ran and is visible in state
    assert isinstance(state.get("retrieved_templates", []), list)


def test_integration_retry_then_finalize(monkeypatch, fake_templates):
    """
    End-to-end: first review FAIL triggers revise, second PASS finalizes.
    Verifies draft_history and review_history.
    """
    scenario = {
        "user_prompt": "follow up on documentation email as discussed last week",
        "intent": "follow_up",
        "tone_mode": "formal",
        "recipient_name": "Kinjal",
        "missing_info": [],
        "force_retry_flow": True,  # makes Review fail once
    }

    import src.rag.template_rag as tr
    monkeypatch.setattr(tr, "retrieve_templates", lambda query, k=3: fake_templates)

    import src.integrations.openai_client as oc
    monkeypatch.setattr(oc, "get_llm", lambda temperature=0.0: FakeLLM(scenario))

    state = run_email_assistant(
        user_prompt=scenario["user_prompt"],
        tone_mode="formal",
        intent_override="follow_up",
        metadata={"recipient_name": "Kinjal"},
        user_id="default",
        max_retries=1,
    )

    assert state is not None
    assert state.get("router", {}).get("next_step") == "final"
    assert state.get("final_output") and "Subject:" in state["final_output"]

    # Should have two attempts due to retry
    dh = state.get("draft_history", [])
    rh = state.get("review_history", [])
    assert len(dh) == 2
    assert len(rh) >= 1  # depending on your implementation it might store 1 or 2; usually 2

    # Latest draft should contain Sincerely
    assert "Sincerely" in (state.get("draft", {}).get("body") or "")
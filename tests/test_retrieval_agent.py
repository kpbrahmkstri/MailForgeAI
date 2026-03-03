from src.agents.retrieval_agent import retrieval_node


def test_retrieval_agent_adds_templates_and_trace(monkeypatch):
    # Monkeypatch retrieve_templates in retrieval_agent module
    import src.agents.retrieval_agent as ra

    def fake_retrieve_templates(query: str, k: int = 3):
        return [
            {"source": "follow_up_formal.md", "content": "TEMPLATE A"},
            {"source": "follow_up_formal_2.md", "content": "TEMPLATE B"},
        ]

    monkeypatch.setattr(ra, "retrieve_templates", fake_retrieve_templates)

    state = {
        "parsed_request": {"goal": "follow up on docs", "key_points": ["docs"]},
        "intent": {"intent": "follow_up"},
        "tone_contract": {"tone_mode": "formal"},
        "trace": [],
    }

    out = retrieval_node(state)
    assert "retrieved_templates" in out
    assert len(out["retrieved_templates"]) == 2
    assert any("RetrievalAgent" in t for t in out["trace"])
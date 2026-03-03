from typing import Any, Dict

from src.rag.template_rag import retrieve_templates


def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state.get("parsed_request") or {}
    intent_obj = state.get("intent") or {}
    intent = intent_obj.get("intent", "other")
    tone_contract = state.get("tone_contract") or {}
    tone_mode = tone_contract.get("tone_mode", state.get("tone_mode", "formal"))

    # RAG query = intent + tone + goal + key points
    goal = parsed.get("goal", "")
    key_points = parsed.get("key_points", [])
    query = f"email template intent={intent} tone={tone_mode} goal={goal} key_points={key_points}"

    templates = retrieve_templates(query, k=3)

    trace = state.get("trace", [])
    trace.append(f"✅ RetrievalAgent: retrieved {len(templates)} templates for intent={intent}, tone={tone_mode}")

    return {"trace": trace, "retrieved_templates": templates}
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict, Literal

from langgraph.graph import StateGraph, END

from src.agents.input_parser_agent import input_parser_node
from src.agents.intent_detection_agent import intent_detection_node
from src.agents.tone_stylist_agent import tone_stylist_node
from src.agents.personalization_agent import personalization_node
from src.agents.draft_writer_agent import draft_writer_node
from src.agents.review_agent import review_node
from src.agents.router_agent import router_node


class EmailState(TypedDict, total=False):
    # Inputs
    user_id: str
    user_prompt: str
    tone_mode: Literal["formal", "casual", "assertive"]
    intent_override: Optional[str]
    metadata: Dict[str, Any]  # recipient_name, recipient_company, relationship, deadline, etc.

    # Agent outputs / shared state
    trace: List[str]

    parsed_request: Dict[str, Any]
    missing_info: List[str]
    assumptions: List[str]

    intent: Dict[str, Any]
    tone_contract: Dict[str, Any]
    user_profile: Dict[str, Any]

    draft: Dict[str, Any]
    review: Dict[str, Any]

    draft_history: List[Dict[str, Any]]
    review_history: List[Dict[str, Any]]

    # Routing / final
    retries: int
    max_retries: int
    router: Dict[str, Any]
    final_output: str
    clarification_question: Optional[str]


def _trace(state: EmailState, msg: str) -> None:
    if "trace" not in state:
        state["trace"] = []
    state["trace"].append(msg)


def build_graph():
    g = StateGraph(EmailState)

    g.add_node("input_parser", input_parser_node)
    g.add_node("intent_detection", intent_detection_node)
    g.add_node("tone_stylist", tone_stylist_node)
    g.add_node("personalization", personalization_node)
    g.add_node("draft_writer", draft_writer_node)
    g.add_node("review", review_node)
    g.add_node("router", router_node)

    # Linear pipeline
    g.set_entry_point("input_parser")
    g.add_edge("input_parser", "intent_detection")
    g.add_edge("intent_detection", "tone_stylist")
    g.add_edge("tone_stylist", "personalization")
    g.add_edge("personalization", "draft_writer")
    g.add_edge("draft_writer", "review")
    g.add_edge("review", "router")

    # Conditional routing after router
    def route_next(state: EmailState) -> str:
        decision = (state.get("router") or {}).get("next_step", "final")
        if decision == "revise":
            return "draft_writer"
        if decision == "ask_user":
            return END
        return END

    g.add_conditional_edges("router", route_next, {
        "draft_writer": "draft_writer",
        END: END,
    })

    return g.compile()


GRAPH = build_graph()


def run_email_assistant(
    user_prompt: str,
    tone_mode: str = "formal",
    user_id: str = "default",
    intent_override: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    max_retries: int = 1,
) -> EmailState:
    """
    Executes the LangGraph workflow and returns the final state.
    """
    state: EmailState = {
        "user_id": user_id,
        "user_prompt": user_prompt,
        "tone_mode": tone_mode,  # formal/casual/assertive
        "intent_override": intent_override,
        "metadata": metadata or {},
        "retries": 0,
        "max_retries": max_retries,
        "draft_history": [],
        "review_history": [],
        "trace": [],
    }
    return GRAPH.invoke(state)
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm


class ParsedRequest(BaseModel):
    recipient_name: Optional[str] = Field(default=None)
    recipient_org: Optional[str] = Field(default=None)
    relationship: Optional[str] = Field(default=None, description="e.g., manager, recruiter, client, teammate, vendor")
    goal: str = Field(description="What the user wants to achieve with this email")
    key_points: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list, description="length, deadline, must include/avoid, etc.")
    missing_info: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


SYSTEM = """You are an expert email requirements extractor.
Your job is to convert a messy user request into a clean structured spec.
Be conservative: do NOT invent facts. If something is unknown, add it to missing_info.
If a reasonable assumption would let drafting proceed, add it to assumptions.
"""


def input_parser_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.0)

    user_prompt = state.get("user_prompt", "")
    metadata = state.get("metadata") or {}

    # Provide metadata to help parsing if present
    context_blob = f"""
USER PROMPT:
{user_prompt}

METADATA FIELDS (may be empty):
{metadata}
""".strip()

    model = llm.with_structured_output(ParsedRequest)
    parsed: ParsedRequest = model.invoke(
        [
            ("system", SYSTEM),
            ("user", context_blob),
        ]
    )

    trace = state.get("trace", [])
    trace.append("✅ InputParser: extracted requirements + missing info + assumptions")

    return {
        "trace": trace,
        "parsed_request": parsed.model_dump(),
        "missing_info": parsed.missing_info,
        "assumptions": parsed.assumptions,
    }
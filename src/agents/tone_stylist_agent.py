from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from src.integrations.openai_client import get_llm


class ToneContract(BaseModel):
    tone_mode: Literal["formal", "casual", "assertive"]
    greeting_style: str
    sentence_style: str
    politeness_level: str
    cta_style: str
    signoff_style: str
    taboo_phrases: List[str] = Field(default_factory=list)


SYSTEM = """You are a tone stylist. Convert tone_mode into a concrete writing contract.
Be specific and actionable (greeting, sentence style, CTA, sign-off).

IMPORTANT:
- For intent='thank_you', "formal" should still feel warm and appreciative, but professional.
  That means: no slang/emojis, but gratitude language IS encouraged.
- Do not output placeholders like [Your Name]. signoff_style should be only a closing phrase like "Sincerely," or "Regards,".

Output a contract that helps an email writer comply.
"""


def tone_stylist_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm(temperature=0.1)

    tone_mode = state.get("tone_mode", "formal")
    parsed = state.get("parsed_request") or {}
    intent = state.get("intent") or {}

    model = llm.with_structured_output(ToneContract)
    contract: ToneContract = model.invoke(
        [
            ("system", SYSTEM),
            ("user", f"tone_mode={tone_mode}\nintent={intent}\nparsed_request={parsed}"),
        ]
    )

    trace = state.get("trace", [])
    trace.append(f"✅ ToneStylist: generated style contract for {contract.tone_mode}")

    return {"trace": trace, "tone_contract": contract.model_dump()}
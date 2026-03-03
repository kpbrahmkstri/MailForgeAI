import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


@lru_cache(maxsize=1)
def get_llm(model: Optional[str] = None, temperature: float = 0.3) -> ChatOpenAI:
    """
    Centralized LLM factory.
    Works with environment variables (HF Spaces) and .env files (local development).
    """
    # First check environment variable (HF Spaces sets this directly)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found in environment, try loading from .env file (local development)
    if not api_key:
        load_dotenv(override=False)
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Add it to a .env file at project root or set it as an environment variable."
        )

    chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=chosen_model, temperature=temperature, api_key=api_key)
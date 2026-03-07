from typing import Dict, Callable

TOOLS: Dict[str, Callable] = {}

def register_tool(name: str, func: Callable):
    TOOLS[name] = func


def call_tool(name: str, payload: dict):
    if name not in TOOLS:
        raise ValueError(f"MCP tool not found: {name}")
    return TOOLS[name](payload)
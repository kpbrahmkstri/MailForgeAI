from src.mcp.mcp_server import mcp


def retrieval_node(state):

    query = state.get("user_prompt", "")
    intent = state.get("intent", {}).get("intent")

    templates = mcp.call(
        "templates.search",
        {
            "query": query,
            "intent": intent
        }
    )

    state["retrieved_templates"] = templates

    trace = state.get("trace", [])
    trace.append("✅ RetrievalAgent: templates retrieved via MCP")

    return {
        "retrieved_templates": templates,
        "trace": trace
    }
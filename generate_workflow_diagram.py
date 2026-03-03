#!/usr/bin/env python3
"""
Generate and visualize the LangGraph workflow diagram for MailForgeAI.
Supports both Mermaid diagram output and ASCII visualization.
"""

import json
from pathlib import Path
from src.workflow.langgraph_flow import GRAPH


def get_graph_mermaid() -> str:
    """
    Generate a Mermaid diagram representation of the workflow.
    This provides a visual representation that can be rendered in various tools.
    """
    mermaid_graph = """graph TD
    A["<b>INPUT PARSER</b><br/>Parse user prompt<br/>Extract intent hints"] --> B["<b>INTENT DETECTION</b><br/>Classify email type<br/>Analyze intent"]
    B --> C["<b>TONE STYLIST</b><br/>Determine tone<br/>Set writing style"]
    C --> D["<b>RETRIEVAL</b><br/>Fetch templates<br/>Get knowledge base"]
    D --> E["<b>PERSONALIZATION</b><br/>Add context<br/>User profile data"]
    E --> F["<b>DRAFT WRITER</b><br/>Generate email<br/>Create content"]
    F --> G["<b>REVIEW</b><br/>Check quality<br/>Validate output"]
    G --> H["<b>ROUTER</b><br/>Decision logic<br/>Route next step"]
    H -->|revise| F
    H -->|ask_user| END["<b>END</b><br/>Return to user"]
    H -->|final| END
    
    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff3e0
    style D fill:#f3e5f5
    style E fill:#e8f5e9
    style F fill:#fff3e0
    style G fill:#fce4ec
    style H fill:#f1f8e9
    style END fill:#c8e6c9"""
    
    return mermaid_graph


def get_graph_structure() -> dict:
    """
    Extract and return the graph structure as a dictionary.
    """
    structure = {
        "entry_point": "input_parser",
        "nodes": [
            {
                "id": "input_parser",
                "name": "Input Parser",
                "description": "Parse user prompt and extract intent hints",
                "type": "agent"
            },
            {
                "id": "intent_detection",
                "name": "Intent Detection",
                "description": "Classify email type and analyze intent",
                "type": "agent"
            },
            {
                "id": "tone_stylist",
                "name": "Tone Stylist",
                "description": "Determine tone and set writing style",
                "type": "agent"
            },
            {
                "id": "retrieval",
                "name": "Retrieval",
                "description": "Fetch templates and get knowledge base",
                "type": "agent"
            },
            {
                "id": "personalization",
                "name": "Personalization",
                "description": "Add context and user profile data",
                "type": "agent"
            },
            {
                "id": "draft_writer",
                "name": "Draft Writer",
                "description": "Generate email and create content",
                "type": "agent"
            },
            {
                "id": "review",
                "name": "Review",
                "description": "Check quality and validate output",
                "type": "agent"
            },
            {
                "id": "router",
                "name": "Router",
                "description": "Decision logic to route next step",
                "type": "router"
            }
        ],
        "edges": [
            {"from": "input_parser", "to": "intent_detection", "label": "default"},
            {"from": "intent_detection", "to": "tone_stylist", "label": "default"},
            {"from": "tone_stylist", "to": "retrieval", "label": "default"},
            {"from": "retrieval", "to": "personalization", "label": "default"},
            {"from": "personalization", "to": "draft_writer", "label": "default"},
            {"from": "draft_writer", "to": "review", "label": "default"},
            {"from": "review", "to": "router", "label": "default"},
            {"from": "router", "to": "draft_writer", "label": "revise"},
            {"from": "router", "to": "END", "label": "ask_user or final"}
        ],
        "conditional_routing": {
            "router": {
                "decisions": [
                    {"decision": "revise", "target": "draft_writer"},
                    {"decision": "ask_user", "target": "END"},
                    {"decision": "final", "target": "END"}
                ]
            }
        }
    }
    return structure


def print_workflow_summary():
    """Print a text-based summary of the workflow."""
    print("\n" + "="*70)
    print("MAILFORGEAI LANGGRAPH WORKFLOW STRUCTURE")
    print("="*70 + "\n")
    
    structure = get_graph_structure()
    
    print("📊 WORKFLOW NODES:")
    print("-" * 70)
    for i, node in enumerate(structure["nodes"], 1):
        print(f"{i:2d}. {node['name']:20s} → {node['description']}")
    
    print("\n📍 WORKFLOW PATH:")
    print("-" * 70)
    path = " → ".join([node["id"] for node in structure["nodes"]])
    path += " → [ROUTER DECISION]"
    print(path)
    
    print("\n🔄 CONDITIONAL ROUTES:")
    print("-" * 70)
    for decision in structure["conditional_routing"]["router"]["decisions"]:
        print(f"  • {decision['decision']:15s} → {decision['target']}")
    
    print("\n" + "="*70 + "\n")


def save_mermaid_diagram(output_path: str = "workflow_diagram.md"):
    """Save the Mermaid diagram to a markdown file."""
    mermaid_content = get_graph_mermaid()
    
    markdown_content = """# MailForgeAI Workflow Diagram

## Visual Workflow

```mermaid
""" + mermaid_content + """
```

## Workflow Description

The MailForgeAI system uses a LangGraph-based workflow that processes email generation through the following stages:

### 1. **Input Parser**
   - Parses the user's natural language prompt
   - Extracts initial intent hints and metadata
   - Prepares structured input for downstream agents

### 2. **Intent Detection**
   - Classifies the email type (e.g., meeting request, apology, follow-up)
   - Analyzes the underlying intent of the message
   - Sets expectations for tone and structure

### 3. **Tone Stylist**
   - Determines the appropriate writing tone (formal, casual, assertive)
   - Applies user preferences and context
   - Sets style guidelines for the draft

### 4. **Retrieval** (RAG Component)
   - Fetches relevant email templates from the knowledge base
   - Retrieves similar past emails for reference
   - Provides domain-specific guidance

### 5. **Personalization**
   - Incorporates user profile information
   - Adds contextual details about the recipient
   - Customizes content for the specific situation

### 6. **Draft Writer**
   - Generates the email content
   - Synthesizes information from all previous stages
   - Creates a complete, ready-to-send draft

### 7. **Review**
   - Validates grammar, clarity, and tone
   - Checks for consistency with user intent
   - Identifies any quality issues

### 8. **Router** (Conditional Decision Node)
   - Makes routing decisions based on review results
   - Three possible outcomes:
     - **revise**: Send back to Draft Writer for improvements
     - **ask_user**: Request clarification from the user
     - **final**: Complete and return the final email

## Graph Characteristics

- **Type**: DAG (Directed Acyclic Graph) with conditional loops
- **Entry Point**: input_parser
- **Exit Points**: END (from router)
- **Max Retries Loop**: Router can send back to draft_writer for revision
- **State Management**: Uses EmailState TypedDict for shared state across agents

## Running the Workflow

```python
from src.workflow.langgraph_flow import GRAPH

# Prepare input state
input_state = {
    "user_id": "user_123",
    "user_prompt": "Send a meeting request to John about Q1 planning",
    "tone_mode": "formal",
    "metadata": {
        "recipient_name": "John",
        "recipient_company": "Acme Corp",
        "relationship": "colleague"
    }
}

# Execute workflow
result = GRAPH.invoke(input_state)
print(result["final_output"])
```
"""
    
    with open(output_path, "w") as f:
        f.write(markdown_content)
    print(f"✅ Mermaid diagram saved to: {output_path}")


def save_graph_json(output_path: str = "workflow_structure.json"):
    """Save the graph structure as JSON."""
    structure = get_graph_structure()
    
    with open(output_path, "w") as f:
        json.dump(structure, f, indent=2)
    print(f"✅ Graph structure saved to: {output_path}")


def export_graph_ascii():
    """Export ASCII representation of the graph."""
    ascii_graph = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   MAILFORGEAI LANGGRAPH WORKFLOW                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

                                START
                                  │
                                  ▼
                        ┌──────────────────┐
                        │  INPUT PARSER    │
                        └──────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │  INTENT DETECTION        │
                    └──────────────────────────┘
                                  │
                                  ▼
                      ┌──────────────────────┐
                      │   TONE STYLIST       │
                      └──────────────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   RETRIEVAL (RAG)   │
                       └─────────────────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │  PERSONALIZATION      │
                     └────────────────────────┘
                                  │
                                  ▼
                      ┌──────────────────────┐
                      │   DRAFT WRITER       │ ◄─────────┐
                      └──────────────────────┘           │
                                  │                      │
                                  ▼                      │
                        ┌──────────────────┐             │
                        │     REVIEW       │             │
                        └──────────────────┘             │
                                  │                      │
                                  ▼                      │
                        ┌──────────────────┐             │
                        │     ROUTER       │─────────────┤
                        └──────────────────┘             │
                          │         │          │         │
                   ┌──────┴─────┬───┴─────┐    │ "revise"
                   │            │         │    └─────────┘
              "ask"/"final"     │         │
                   ▼            ▼         ▼
                  END          END       END

═══════════════════════════════════════════════════════════════════════════════
                          KEY WORKFLOW FEATURES
═══════════════════════════════════════════════════════════════════════════════

State Management:
  • EmailState: Shared state dictionary across all nodes
  • Trace: Audit log of agent decisions
  • History: Draft and review iteration history

Routing Logic:
  ✓ Linear pipeline through 7 main agents
  ✓ Conditional routing at final router node
  ✓ Feedback loop: revise drafts based on review
  ✓ End points: User clarification or final email

Agents & Responsibilities:
  1. input_parser         → Parse & validate user input
  2. intent_detection     → Classify email intent
  3. tone_stylist         → Apply writing tone
  4. retrieval            → Fetch templates (RAG)
  5. personalization      → Add user context
  6. draft_writer         → Generate content
  7. review               → Quality assurance
  8. router               → Make final decisions
"""
    print(ascii_graph)
    return ascii_graph


def main():
    """Main execution function."""
    # Print ASCII visualization
    export_graph_ascii()
    
    # Print text summary
    print_workflow_summary()
    
    # Save outputs
    save_mermaid_diagram("workflow_diagram.md")
    save_graph_json("workflow_structure.json")
    
    print("\n📁 Output files generated:")
    print("   • workflow_diagram.md (Mermaid visualization)")
    print("   • workflow_structure.json (JSON structure)")
    print("\nYou can view the Mermaid diagram in VS Code or on mermaid.live")


if __name__ == "__main__":
    main()

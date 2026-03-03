# MailForgeAI Workflow Diagram

## Visual Workflow

```mermaid
graph TD
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
    style END fill:#c8e6c9
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

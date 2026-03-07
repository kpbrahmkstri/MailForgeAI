# 📧 MailForgeAI — Multi-Agent Email Assistant

MailForgeAI is an intelligent email writing assistant powered by LangGraph and multiple AI agents. It helps you compose professional, personalized emails with intelligent intent detection, tone styling, and quality reviews.

## 🚀 Features

- **Multi-Agent Workflow**: 8 specialized agents working together
  - Input Parser: Understands your intent
  - Intent Detection: Classifies email type (follow-up, outreach, etc.)
  - Tone Stylist: Applies formal/casual/assertive tone
  - Personalization: Adds recipient-specific details
  - Retrieval Agent: Finds relevant templates using RAG
  - Draft Writer: Generates email content
  - Review Agent: Quality checks and tone alignment
  - Router Agent: Decides if revision is needed

- **Intelligent Clarification Loop**: Asks for missing information when needed
- **Draft History**: Tracks all attempts and revisions
- **Style Learning**: Learns from your edits to match your writing style
- **Template RAG**: Leverages existing email templates for quality
- **Workflow Visualization**: Generate visual diagrams of the agent pipeline

## 📋 Prerequisites

1. **Python 3.10+** - Download from https://www.python.org
2. **OpenAI API Key** - Get from https://platform.openai.com/api-keys
3. **Git** (optional) - For version control

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/MailForgeAI.git
cd MailForgeAI

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"
```

## 🚀 Quick Start

### Run the Streamlit App

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` and start writing emails!

### Generate Workflow Visualization

```bash
# Create a PNG diagram of the LangGraph workflow
python visualize_langgraph_workflow.py
```

This generates `workflow_diagram.png` showing all agents and connections.

**In Jupyter Notebooks:**
```python
from visualize_langgraph_workflow import display_workflow

# Display workflow inline
display_workflow()
```

### Use as Python Module

```python
from src.workflow.langgraph_flow import run_email_assistant

# Run the workflow
state = run_email_assistant(
    user_prompt="Write a follow-up to my recruiter after our interview",
    tone_mode="formal",
    metadata={
        "recipient_name": "Jane Recruiter",
        "recipient_org": "Tech Corp",
        "relationship": "recruiter",
    }
)

# Access results
print(state["draft"])  # Generated email
print(state["review"])  # Review findings
print(state["trace"])  # Agent execution trace
```

## 📊 Workflow Architecture

The application uses LangGraph to orchestrate a multi-agent pipeline:

```
Input Parser → Intent Detection → Tone Stylist → Retrieval (RAG)
    ↓
Personalization → Draft Writer → Review → Router
    ↑__________________|
    (Revision loop if needed)
```

Generate a visual diagram:
```bash
python visualize_langgraph_workflow.py
```

## 📁 Project Structure

```
MailForgeAI/
├── app.py                               # Main Streamlit app
├── visualize_langgraph_workflow.py      # Workflow visualization script
├── requirements.txt                     # Python dependencies
├── src/
│   ├── agents/                          # AI agent implementations
│   │   ├── input_parser_agent.py
│   │   ├── intent_detection_agent.py
│   │   ├── tone_stylist_agent.py
│   │   ├── personalization_agent.py
│   │   ├── draft_writer_agent.py
│   │   ├── review_agent.py
│   │   ├── router_agent.py
│   │   └── retrieval_agent.py
│   ├── workflow/
│   │   └── langgraph_flow.py            # LangGraph workflow definition
│   ├── rag/
│   │   └── template_rag.py              # Template retrieval system
│   ├── memory/
│   │   ├── memory_store.py              # User profile management
│   │   └── user_profiles.json
│   ├── integrations/
│   │   └── openai_client.py             # OpenAI API client
│   ├── utils/
│   │   └── path_utils.py                # Path management utilities
│   └── ui/
│       └── streamlit_app.py
├── data/
│   ├── kb/
│   │   └── templates/                   # Email templates
│   └── tone_samples/
└── tests/                               # Unit and integration tests

```

## 🔐 Environment Variables

Set these in your environment:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key |
| `OPENAI_MODEL` | ❌ No | Model name (default: `gpt-4o-mini`) |
| `PROJECT_ROOT` | ❌ No | Override project root path |

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
```

## 📊 Visualizing the Workflow

The project includes a visualization utility for understanding the multi-agent pipeline:

```bash
# Generate workflow diagram as PNG
python visualize_langgraph_workflow.py
```

**Output:** `workflow_diagram.png` showing:
- All 8 agent nodes and their connections
- Data flow between agents
- Conditional routing paths
- Entry and exit points

**For Jupyter/Notebooks:**
```python
from visualize_langgraph_workflow import display_workflow
display_workflow()  # Display inline in notebook
```

## 🧪 Testing

Run tests locally:

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_full_workflow.py -v
```

## 🌐 Hugging Face Spaces Deployment

MailForgeAI is fully configured for deployment on Hugging Face Spaces.

See [README_HF_DEPLOYMENT.md](README_HF_DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deploy Summary

1. Create a new Space on Hugging Face (Streamlit SDK)
2. Upload project files
3. Add `OPENAI_API_KEY` to Repository secrets
4. Space auto-deploys automatically!

Your app will be live at: `https://huggingface.co/spaces/<username>/<space-name>`

## 🔧 Configuration

### Tone Modes

- **formal**: Professional, structured language
- **casual**: Friendly, conversational tone  
- **assertive**: Direct, confident communication

### Intent Types

- `outreach` - Initial contact/prospecting
- `follow_up` - Following up on previous communication
- `apology` - Apologizing or addressing issues
- `status_update` - Providing progress updates
- `meeting_request` - Scheduling meetings
- `escalation` - Escalating issues formally
- `thank_you` - Expressing gratitude

### Adding Custom Templates

Add `.md` files to `data/kb/templates/`:

```markdown
# Follow-Up Template

Hi [RECIPIENT_NAME],

Thank you for [CONTEXT]. I wanted to follow up on [TOPIC].

[KEY_POINTS]

Best regards,
[SENDER_NAME]
```

## 🆘 Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

### API Key Issues
- Verify key at https://platform.openai.com/api-keys
- Check account has available credits
- Ensure key doesn't expire

### Path/File Errors
The `path_utils.py` module handles cross-platform path issues automatically. Ensure all file operations use the utility functions.

### Templates Not Loading
- Verify `data/kb/templates/` directory exists
- Check template files have `.md` extension
- Ensure files are readable by the application

## 📚 Documentation

- [Deployment Guide](README_HF_DEPLOYMENT.md) - Detailed HF Spaces deployment
- [Workflow Structure](workflow_structure.json) - JSON definition of agent pipeline
- [Workflow Diagram](workflow_diagram.md) - Mermaid diagram of the workflow

## 🤝 Contributing

Contributions are welcome! Please:
1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🎯 Roadmap

- [ ] Web UI (Vue.js frontend)
- [ ] Email sending integration (Gmail, Outlook)
- [ ] Advanced analytics and usage metrics
- [ ] Custom LLM support (Anthropic Claude, etc.)
- [ ] Multi-language support
- [ ] Template marketplace

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review workflow diagram for pipeline understanding

---

**Built with ❤️ using LangGraph, OpenAI, and Streamlit**

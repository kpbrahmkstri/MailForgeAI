from pathlib import Path
from typing import List, Dict, Any
import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.utils.path_utils import get_templates_dir, get_chroma_dir

# Ensure OPENAI_API_KEY is available (for local .env files)
if not os.getenv("OPENAI_API_KEY"):
    load_dotenv(override=False)


TEMPLATE_DIR = get_templates_dir()
CHROMA_DIR = get_chroma_dir()


# Fallback templates for Hugging Face Spaces (when template files are not deployed)
FALLBACK_TEMPLATES = {
    "formal_outreach.md": """# Formal Outreach Email Template

**Subject**: Professional Connection and Collaboration Opportunity

Dear [Recipient Name],

I hope this message finds you well. I am reaching out to you because I admire your work in [specific area/field].

I believe there may be a valuable opportunity for us to collaborate on [specific topic/project]. Your expertise in [relevant area] aligns well with [our goals/my objectives].

I would welcome the opportunity to discuss this further at your earliest convenience.

Best regards,
[Your Name]""",
    
    "formal_follow_up.md": """# Formal Follow-up Email Template

**Subject**: Follow-up: [Previous Conversation Topic]

Dear [Recipient Name],

I wanted to follow up on our conversation regarding [topic discussed]. 

As promised, [mention any action items or documents shared]. I believe this will be beneficial for [purpose/reason].

I would appreciate your feedback on [specific question/request]. Please let me know if you have any questions or would like to discuss further.

Thank you for your time and consideration.

Best regards,
[Your Name]""",

    "formal_meeting_request.md": """# Formal Meeting Request Email

**Subject**: Meeting Request: [Topic/Purpose]

Dear [Recipient Name],

I would like to schedule a meeting with you to discuss [topic/purpose of meeting].

I believe this discussion would be mutually beneficial as it relates to [relevant context]. I am flexible with my schedule and can accommodate your availability.

Would you have time for a [15/30/60]-minute meeting in the coming [week/two weeks]? 

Please let me know what works best for you.

Thank you for considering my request.

Best regards,
[Your Name]""",

    "formal_status_update.md": """# Formal Status Update Email

**Subject**: Project Status Update - [Project Name]

Dear [Recipient Name],

I wanted to provide you with an update on [project/initiative].

**Progress Summary**:
- [Completed item/milestone]
- [Completed item/milestone]
- [In progress item]

**Next Steps**:
- [Next action item]
- [Next action item]

**Timeline**: Expected completion [date].

Please let me know if you have any questions or need additional information.

Best regards,
[Your Name]""",

    "formal_thank_you.md": """# Formal Thank You Email

**Subject**: Thank You for [Meeting/Opportunity/Help]

Dear [Recipient Name],

I wanted to personally thank you for [specific action/meeting/help provided].

Your insights regarding [specific topic] were invaluable, and I appreciated the time you took to [action they performed]. 

[Optional: Mention any action you'll take as a result].

I look forward to [future collaboration/continued relationship].

Thank you again for your generosity and support.

Best regards,
[Your Name]""",

    "formal_escalation.md": """# Formal Escalation Email

**Subject**: [URGENT] Escalation: [Issue Description]

Dear [Recipient Name],

I am writing to formally escalate [issue/concern] that requires immediate attention.

**Issue Summary**: 
[Clear description of the problem]

**Impact**: 
[How this affects business/operations]

**Timeline**: 
This matter is time-sensitive and requires resolution by [date if applicable].

I would appreciate your urgent attention to this matter and would be available to discuss at your earliest convenience.

Thank you for your prompt action.

Best regards,
[Your Name]"""
}


def _load_template_docs() -> List[Document]:
    docs: List[Document] = []
    if not TEMPLATE_DIR.is_dir():
        return docs

    for fpath in TEMPLATE_DIR.glob("*.md"):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        # Store metadata for UI + filtering
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": fpath.name,
                    "path": str(fpath),
                },
            )
        )
    return docs


def _get_fallback_template_docs() -> List[Document]:
    """Create documents from fallback templates for Hugging Face Spaces."""
    docs: List[Document] = []
    for filename, content in FALLBACK_TEMPLATES.items():
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": filename,
                    "path": f"builtin://{filename}",
                },
            )
        )
    return docs


def get_template_retriever():
    """
    Creates/loads a persistent Chroma index for templates.
    Falls back to builtin templates if template files are not found (Hugging Face Spaces).
    """
    embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY env var

    # Create index if missing
    if not CHROMA_DIR.exists() or not list(CHROMA_DIR.iterdir()):
        docs = _load_template_docs()
        
        # Fallback to builtin templates if no template files found (e.g., HF Spaces)
        if not docs:
            docs = _get_fallback_template_docs()
        
        if not docs:
            raise RuntimeError(f"No templates found in {TEMPLATE_DIR} and no fallback templates available")
        
        vs = Chroma.from_documents(
            docs,
            embeddings,
            persist_directory=str(CHROMA_DIR),
            collection_name="mailforge_templates",
        )
        vs.persist()
        return vs.as_retriever(search_kwargs={"k": 3})

    # Load existing
    vs = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="mailforge_templates",
    )
    return vs.as_retriever(search_kwargs={"k": 3})


def retrieve_templates(query: str, k: int = 3) -> List[Dict[str, Any]]:
    retriever = get_template_retriever()

    # LangChain retrievers vary by version:
    # - Newer: retriever.invoke(query) -> List[Document]
    # - Older: retriever.get_relevant_documents(query)
    if hasattr(retriever, "invoke"):
        docs = retriever.invoke(query)
    else:
        docs = retriever.get_relevant_documents(query)

    results = []
    for d in (docs or [])[:k]:
        results.append(
            {
                "source": d.metadata.get("source"),
                "content": d.page_content,
            }
        )
    return results
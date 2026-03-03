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


def get_template_retriever():
    """
    Creates/loads a persistent Chroma index for templates.
    """
    embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY env var

    # Create index if missing
    if not CHROMA_DIR.exists() or not list(CHROMA_DIR.iterdir()):
        docs = _load_template_docs()
        if not docs:
            raise RuntimeError(f"No templates found in {TEMPLATE_DIR}")
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
import os
from typing import List, Dict, Any

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "kb", "templates")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_templates")


def _load_template_docs() -> List[Document]:
    docs: List[Document] = []
    if not os.path.isdir(TEMPLATE_DIR):
        return docs

    for fname in os.listdir(TEMPLATE_DIR):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(TEMPLATE_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Store metadata for UI + filtering
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": fname,
                    "path": path,
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
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        docs = _load_template_docs()
        if not docs:
            raise RuntimeError(f"No templates found in {TEMPLATE_DIR}")
        vs = Chroma.from_documents(
            docs,
            embedding=embeddings,
            persist_directory=CHROMA_DIR,
            collection_name="mailforge_templates",
        )
        vs.persist()
        return vs.as_retriever(search_kwargs={"k": 3})

    # Load existing
    vs = Chroma(
        persist_directory=CHROMA_DIR,
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
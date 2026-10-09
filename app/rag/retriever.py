
from functools import lru_cache
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_vector_store() -> FAISS:
    index_file = VECTOR_STORE_DIR / "index.faiss"
    metadata_file = VECTOR_STORE_DIR / "index.pkl"

    if not index_file.exists() or not metadata_file.exists():
        raise RuntimeError(
            "FAISS index not found. Run the ingestion script first."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # Only load indexes created locally from trusted source documents.
    return FAISS.load_local(
        str(VECTOR_STORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve_context(question: str, k: int = 3) -> str:
    store = get_vector_store()
    documents = store.similarity_search(question, k=k)

    if not documents:
        return ""

    return "\n\n".join(
        f"Source: {document.metadata.get('source', 'unknown')}\n"
        f"{document.page_content}"
        for document in documents
    )


from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "data" / "knowledge_base"
VECTOR_STORE_DIR = PROJECT_ROOT / "data" / "vector_store"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_vector_store() -> int:
    files = sorted(KNOWLEDGE_BASE_DIR.glob("*.txt"))

    if not files:
        raise FileNotFoundError(
            f"No .txt knowledge-base files found in {KNOWLEDGE_BASE_DIR}"
        )

    documents = []

    for file_path in files:
        loader = TextLoader(
            str(file_path),
            encoding="utf-8",
        )
        loaded_documents = loader.load()

        for document in loaded_documents:
            document.metadata["source"] = file_path.name

        documents.extend(loaded_documents)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No text chunks were generated.")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(VECTOR_STORE_DIR))

    return len(chunks)
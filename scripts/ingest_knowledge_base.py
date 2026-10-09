
from app.rag.ingestion import build_vector_store


def main():
    count = build_vector_store()
    print(f"Knowledge base indexed successfully: {count} chunks.")


if __name__ == "__main__":
    main()

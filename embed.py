"""
embed.py
--------
Stage 3 of the document pipeline: embed chunks and store them in a local
ChromaDB collection.

Loads documents via load_document.load_documents(), splits them with
chunking.chunk_documents(), embeds each chunk with sentence-transformers
all-MiniLM-L6-v2, and persists vectors + metadata under chroma_db/.

Re-running rebuilds the collection from scratch so chunks stay in sync with the
files on disk.
"""

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from load_document import load_documents
from chunking import chunk_documents

PROJECT_ROOT = Path(__file__).resolve().parent
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "cu_boulder_cs"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
BATCH = 256


def build_collection(reset: bool = True):
    docs = load_documents()
    chunks = chunk_documents(docs)
    print(f"Loaded {len(docs)} documents -> {len(chunks)} chunks")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    # cosine distance is the standard choice for normalized sentence-transformer
    # embeddings; BAAI/bge-small-en-v1.5 outputs are L2-normalized by default.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [str(c["chunk_id"]) for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {"source": c["source"], "url": c["url"] or ""} for c in chunks
    ]

    for i in range(0, len(ids), BATCH):
        end = min(i + BATCH, len(ids))
        collection.add(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end],
        )
        print(f"  embedded {end}/{len(ids)}")

    print(f"\nStored {collection.count()} chunks in {CHROMA_DIR}/ "
          f"(collection: {COLLECTION_NAME}, model: {EMBED_MODEL})")


if __name__ == "__main__":
    build_collection()

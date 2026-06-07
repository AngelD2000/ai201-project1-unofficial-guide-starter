"""
retrieve.py
-----------
Stage 4 of the document pipeline: query the ChromaDB collection for the top-k
chunks most relevant to a natural-language question.

Per planning.md: top-k = 10, embedding model = all-MiniLM-L6-v2.

Usage:
    python retrieve.py "Is CJ Herman's class difficult?"
    python retrieve.py "GPA for CU Boulder MS CS" -k 5
"""

import argparse
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = Path(__file__).resolve().parent
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "cu_boulder_cs"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 10


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    return client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)


def retrieve(query: str, k: int = TOP_K):
    """Return a list of hit dicts: {chunk_id, text, source, url, distance}."""
    collection = get_collection()
    res = collection.query(query_texts=[query], n_results=k)
    hits = []
    for i in range(len(res["ids"][0])):
        meta = res["metadatas"][0][i] or {}
        hits.append({
            "chunk_id": res["ids"][0][i],
            "text": res["documents"][0][i],
            "source": meta.get("source", ""),
            "url": meta.get("url", ""),
            "distance": res["distances"][0][i],
        })
    return hits


def _print_hit(rank: int, h: dict):
    print(f"[{rank}] dist={h['distance']:.4f}  chunk_id={h['chunk_id']}")
    print(f"    source: {h['source'][:80]}")
    if h["url"]:
        print(f"    url:    {h['url']}")
    snippet = h["text"].replace("\n", " ")
    if len(snippet) > 300:
        snippet = snippet[:300] + "..."
    print(f"    {snippet}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Query the ChromaDB collection")
    ap.add_argument("query", help="Question to retrieve chunks for")
    ap.add_argument("-k", type=int, default=TOP_K,
                    help=f"top-k chunks to retrieve (default {TOP_K})")
    args = ap.parse_args()

    hits = retrieve(args.query, args.k)
    print(f"Query: {args.query!r}")
    print(f"Top {len(hits)} matches:\n")
    for i, h in enumerate(hits, 1):
        _print_hit(i, h)

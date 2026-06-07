"""
chunking.py
-----------
Stage 2 of the document pipeline: split loaded documents into chunks.

Strategy (from planning.md):
  - chunk_size    = 512 characters
  - chunk_overlap = 100 characters
  - splitter      = RecursiveCharacterTextSplitter

Why these numbers (per the plan): over half the sources are short comments in the
~250-300 char range, while a few are long multi-point Reddit threads. 512 chars
holds a single point/paragraph of a long post without diluting it; 100 chars of
overlap (roughly one informal sentence) keeps a chunk tied to the point before it.

Implementation note:
  This module prefers LangChain's RecursiveCharacterTextSplitter. If LangChain is
  not installed, it falls back to a bundled port that reproduces LangChain's exact
  recursive split + merge-with-overlap algorithm, so output is identical for our
  parameters and the pipeline runs with zero hard dependencies.
"""

import re

CHUNK_SIZE = 512
CHUNK_OVERLAP = 100


# --------------------------------------------------------------------------- #
# Faithful fallback port of LangChain's RecursiveCharacterTextSplitter
# --------------------------------------------------------------------------- #
def _split_with_regex(text, separator, keep_separator=True):
    if separator:
        if keep_separator:
            parts = re.split(f"({separator})", text)
            splits = [parts[i] + parts[i + 1] for i in range(1, len(parts), 2)]
            if len(parts) % 2 == 0:
                splits += parts[-1:]
            splits = [parts[0]] + splits
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]


def _join_docs(docs, separator):
    text = separator.join(docs).strip()
    return text if text else None


def _merge_splits(splits, separator, chunk_size, chunk_overlap):
    sep_len = len(separator)
    docs, current, total = [], [], 0
    for d in splits:
        d_len = len(d)
        if total + d_len + (sep_len if current else 0) > chunk_size:
            if current:
                doc = _join_docs(current, separator)
                if doc is not None:
                    docs.append(doc)
                # shrink from the front until we're back under overlap / size
                while total > chunk_overlap or (
                    total + d_len + (sep_len if current else 0) > chunk_size and total > 0
                ):
                    total -= len(current[0]) + (sep_len if len(current) > 1 else 0)
                    current = current[1:]
        current.append(d)
        total += d_len + (sep_len if len(current) > 1 else 0)
    doc = _join_docs(current, separator)
    if doc is not None:
        docs.append(doc)
    return docs


def _recursive_split(text, separators, chunk_size, chunk_overlap):
    final = []
    separator = separators[-1]
    new_separators = []
    for i, s in enumerate(separators):
        if s == "":
            separator = s
            break
        if re.search(re.escape(s), text):
            separator = s
            new_separators = separators[i + 1:]
            break

    splits = _split_with_regex(text, re.escape(separator), keep_separator=True)
    good = []
    for s in splits:
        if len(s) < chunk_size:
            good.append(s)
        else:
            if good:
                final.extend(_merge_splits(good, "", chunk_size, chunk_overlap))
                good = []
            if not new_separators:
                final.append(s)
            else:
                final.extend(_recursive_split(s, new_separators, chunk_size, chunk_overlap))
    if good:
        final.extend(_merge_splits(good, "", chunk_size, chunk_overlap))
    return final


def _fallback_split(text, chunk_size, chunk_overlap):
    return _recursive_split(text, ["\n\n", "\n", " ", ""], chunk_size, chunk_overlap)


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def _get_splitter(chunk_size, chunk_overlap):
    """Return a callable(text)->list[str], preferring real LangChain."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
        except ImportError:
            return lambda t: _fallback_split(t, chunk_size, chunk_overlap)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text


def chunk_text(text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Split a single string into overlapping chunks."""
    return _get_splitter(chunk_size, chunk_overlap)(text)


def chunk_documents(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    """Chunk a list of loaded documents, preserving source metadata on each chunk.

    Returns list of dicts: {chunk_id, source, url, text, char_count}
    """
    splitter = _get_splitter(chunk_size, chunk_overlap)
    chunks = []
    for doc in documents:
        for piece in splitter(doc["text"]):
            chunks.append({
                "chunk_id": len(chunks),
                "source": doc["source"],
                "url": doc["url"],
                "text": piece,
                "char_count": len(piece),
            })
    return chunks


if __name__ == "__main__":
    from load_document import load_documents

    docs = load_documents()
    chunks = chunk_documents(docs)

    sizes = [c["char_count"] for c in chunks]
    print(f"{len(docs)} documents -> {len(chunks)} chunks")
    print(f"chunk size target: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP}")
    print(f"actual chunk chars: min={min(sizes)}, max={max(sizes)}, "
          f"avg={sum(sizes) // len(sizes)}\n")
    per_source = {}
    for c in chunks:
        per_source[c["source"][:40]] = per_source.get(c["source"][:40], 0) + 1
    for src, n in per_source.items():
        print(f"  {n:>3} chunks  | {src}")
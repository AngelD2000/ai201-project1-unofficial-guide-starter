"""
load_documents.py
-----------------
Stage 1 of the document pipeline: load raw .txt sources from disk into memory.

Each file in documents/ starts with a small metadata header (KEY: value lines),
a blank line, then the body text. We parse the header into structured metadata
and keep the body separate so that:
  - chunking operates only on real content (not boilerplate), and
  - every chunk can carry its source/url for grounding + citation later.
"""

import re
from pathlib import Path


def _clean_body(body: str) -> str:
    """Remove structural scaffolding so chunks contain only real content.

    - Drops lines that are purely section dividers, e.g. '--- REVIEWS ---'.
    - Drops my uppercase 'NOTE:' cleaning annotations (metadata about how the
      file was prepared), but KEEPS lowercase 'Note:' lines, which are real
      source content (e.g. a GradCafe applicant's own note).
    Collapses the blank lines left behind so paragraph boundaries stay intact.
    """
    kept = []
    for line in body.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"-{2,}.*-{2,}", stripped):      # divider line
            continue
        if stripped.startswith("NOTE:"):                  # my annotation
            continue
        kept.append(line)
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)           # collapse blank runs
    return cleaned.strip()


def _parse_header(raw: str):
    """Split a raw file into (metadata dict, body string).

    Header = consecutive 'KEY: value' lines at the top, ended by a blank line.
    Anything after that blank line is the body.
    """
    lines = raw.splitlines()
    metadata = {}
    body_start = 0

    for i, line in enumerate(lines):
        if line.strip() == "":
            body_start = i + 1
            break
        if ":" in line and line.split(":", 1)[0].isupper():
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
        else:
            # First non-KEY:value, non-blank line -> body starts here.
            body_start = i
            break

    body = "\n".join(lines[body_start:]).strip()
    return metadata, body


def load_documents(data_dir: str = "documents"):
    """Load every .txt file in data_dir.

    Returns a list of dicts: {source, url, type, text, char_count}
    """
    docs = []
    paths = sorted(Path(data_dir).glob("*.txt"))

    for path in paths:
        raw = path.read_text(encoding="utf-8")
        metadata, body = _parse_header(raw)
        body = _clean_body(body)
        docs.append({
            "filename": path.name,
            "source": metadata.get("source", path.stem),
            "url": metadata.get("url", ""),
            "type": metadata.get("type", ""),
            "text": body,
            "char_count": len(body),
        })

    return docs


if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} documents from documents/\n")
    for d in documents:
        print(f"  {d['filename']:<20} {d['char_count']:>6} chars  | {d['source'][:60]}")
    total = sum(d["char_count"] for d in documents)
    print(f"\nTotal body text: {total:,} characters")
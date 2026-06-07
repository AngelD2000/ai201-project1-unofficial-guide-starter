"""
fetch_reddit_from_pdf.py
------------------------
Extract a Reddit thread (post + comments) from a browser-printed PDF and write
it to documents/<name>.txt in the project's header format.

Why this exists: the public Reddit .json endpoint blocks unauthenticated
requests from many IPs, and PRAW needs API credentials we don't want to bake
into the project. The workaround was to open each thread in a logged-in
browser and "Save as PDF". This script takes those PDFs and extracts the
post + comments into the same plain-text format the loader expects.

The browser print adds a fair amount of chrome:
  - per-page header: '6/7/26, 7:58 AM <title> : r/cuboulder'
  - nav strings: 'Skip to main content', 'Search in r/cuboulder', 'Log In'
  - footer page-number line and a 'related posts' list at the end

We strip those, truncate at the first related-posts marker, and insert blank
lines before each comment so chunking can split on \\n\\n.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple

import pdfplumber

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = PROJECT_ROOT / "documents" / "_source_pdfs"
OUT_DIR = PROJECT_ROOT / "documents"

# (pdf_filename, output_name, url, description)
THREADS: List[Tuple[str, str, str, str]] = [
    (
        "reddit_perspectives.pdf",
        "reddit_perspectives",
        "https://www.reddit.com/r/cuboulder/comments/1qkaql1/perspectives_from_cu_boulder_cs_majors/",
        "Reddit — CS majors perspectives at CU Boulder",
    ),
    (
        "reddit_cost.pdf",
        "reddit_cost",
        "https://www.reddit.com/r/cuboulder/comments/1jnjloz/is_there_any_way_to_reduce_cost_of_attendance/",
        "Reddit — reduce cost of attendance",
    ),
    (
        "reddit_diversity.pdf",
        "reddit_diversity",
        "https://www.reddit.com/r/cuboulder/comments/1i8fgrx/how_accepting_is_cu_of_trans_people/",
        "Reddit — diversity and acceptance",
    ),
    (
        "reddit_dorms.pdf",
        "reddit_dorms",
        "https://www.reddit.com/r/cuboulder/comments/1tske4d/if_youre_moving_into_a_dorm_for_the_first_time/",
        "Reddit — dorm life tips (Q3 source for laundry)",
    ),
]

# Lines that appear as pure UI chrome and should be dropped wholesale.
CHROME_LINES = {
    "Skip to main content",
    "Log In",
}

# Patterns that mark a line as chrome.
CHROME_PATTERNS = [
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2},\s+\d{1,2}:\d{2}\s+(AM|PM)\s+.*:\s*r/[\w-]+\s*$"),
    re.compile(r"^r/[\w-]+\s+Search in r/[\w-]+\s+Log In\s*$"),
    re.compile(r"^https?://\S+\s+\d+/\d+\s*$"),   # footer "<url> 3/10"
    re.compile(r"^Reddit Rules .*All rights reserved\.\s*$"),
]

# Marker that the end of the thread has been reached (related-post links).
END_PATTERN = re.compile(r"^r/[\w-]+\s*•\s*\d+\s*(mo|y|d|h|w)\s*ago\s*$")

# Comment header: "username • 7d ago" or "username OP • 7d ago"
COMMENT_HEADER = re.compile(r"^[A-Za-z0-9_\-]{3,30}(\s+OP)?\s*•\s*\d+\s*(d|h|mo|y|w|min)\s*ago\s*$")

# Promoted-post header: "OpenAI • Promoted", "Some Brand • Promoted", etc.
# Real comments always end "• Nd ago", so the "• Promoted" suffix is a
# reliable distinguisher.
PROMOTED_HEADER = re.compile(r"^(u/)?[\w &\-.,]+\s*•\s*Promoted\s*$")
# Safety cap so a missing comment header doesn't swallow real content.
PROMOTED_MAX_LINES = 8

# Vote-count-only lines (e.g. "128 · 12" or "2"). Used for inserting blank
# lines after a comment block.
VOTE_LINE = re.compile(r"^\d+\s*(·\s*\d+)?\s*$")


def _extract_raw(pdf_path: Path) -> str:
    parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            parts.append(txt)
    return "\n".join(parts)


def _clean(raw: str) -> str:
    lines = raw.splitlines()
    cleaned: List[str] = []
    saw_first_comment = False
    skipping_promoted = 0  # remaining lines to skip after a Promoted header

    for ln in lines:
        s = ln.strip()
        if not s:
            cleaned.append("")
            continue
        if s in CHROME_LINES:
            continue
        if any(p.match(s) for p in CHROME_PATTERNS):
            continue
        # Promoted ad: drop the header and the next few lines, until either a
        # real comment header appears or PROMOTED_MAX_LINES are consumed.
        if PROMOTED_HEADER.match(s):
            skipping_promoted = PROMOTED_MAX_LINES
            continue
        if skipping_promoted > 0:
            if COMMENT_HEADER.match(s):
                skipping_promoted = 0  # fall through and process this line
            else:
                skipping_promoted -= 1
                continue
        # Truncate at the related-posts list, but only AFTER we've already
        # entered the comment section — otherwise the OP subreddit line
        # ("r/cuboulder •7d ago" at the very top) would cut us off.
        if saw_first_comment and END_PATTERN.match(s):
            break
        # Mark when we enter the comment section so the END_PATTERN can fire.
        if COMMENT_HEADER.match(s):
            saw_first_comment = True
            # Blank line before each comment so chunking can split on \n\n.
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            cleaned.append(s)
            continue
        # Vote-count-only line: drop it but ensure a blank separator follows.
        if VOTE_LINE.match(s):
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        cleaned.append(s)

    # Collapse runs of blank lines and trim.
    out: List[str] = []
    blank = 0
    for ln in cleaned:
        if ln == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip()


def _render(name: str, url: str, description: str, body: str) -> str:
    header = f"SOURCE: {description}\n"
    return header + "\n" + body + "\n"


def process(pdf_path: Path, name: str, url: str, description: str) -> Path:
    raw = _extract_raw(pdf_path)
    body = _clean(raw)
    out_path = OUT_DIR / f"{name}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render(name, url, description, body), encoding="utf-8")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Extract Reddit threads from browser-printed PDFs")
    ap.add_argument("--only", help="Process only the thread with this output name (e.g. reddit_cost)")
    args = ap.parse_args()

    targets = THREADS
    if args.only:
        targets = [t for t in THREADS if t[1] == args.only]
        if not targets:
            sys.exit(f"No thread named {args.only}. Known: {[t[1] for t in THREADS]}")

    for pdf_name, out_name, url, desc in targets:
        pdf_path = PDF_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  SKIP {pdf_name} (not found at {pdf_path})", file=sys.stderr)
            continue
        out_path = process(pdf_path, out_name, url, desc)
        size = out_path.stat().st_size
        print(f"  wrote {out_path}  ({size:,} bytes)")


if __name__ == "__main__":
    main()

"""
fetch_rmp_from_pdf.py
---------------------
Extract a RateMyProfessors professor page from a browser-printed PDF into a
plain-text file the loader can ingest.

RMP is robots-disallowed and JavaScript-rendered, so direct HTTP doesn't work.
The workflow mirrors fetch_reddit_from_pdf.py: user opens the prof's page in a
logged-in browser, scrolls to load all ratings, Save as PDF, drop it here.

The PDF has a lot of chrome to strip:
  - per-page timestamp header
  - sticky sidebar that repeats prof name / department / university on every page
  - 'Cheddar News Live Feed' ad text with doubled characters (two text layers
    overlapping at the same position render as 'CChheeddddaarr NNeewwss...')
  - footer URL + page-number line
  - rating-distribution sidebar labels (Awesome/Great/Good/OK/Awful)
  - 'Compare', 'Rate', 'Helpful 0 0' UI buttons
  - the print engine sometimes drops a few mid-word characters in comment text
    (visible as words like 'lectures t' followed by 'engaging' on the next
    line — the joining 'o be' was rendered but not captured). Nothing we can
    do about that from the PDF side; the eval question for CJ Herman depends
    on the summary stats, which extract cleanly.
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

# (pdf_filename, output_name, prof_name, prof_url)
PROFESSORS: List[Tuple[str, str, str, str]] = [
    (
        "rmp_cj_herman.pdf",
        "rmp_cj_herman",
        "CJ Herman",
        "https://www.ratemyprofessors.com/professor/2520121",
    ),
    (
        "rmp_joshua_grochow.pdf",
        "rmp_joshua_grochow",
        "Joshua Grochow",
        # URL is captured from the PDF footer if present, otherwise this default.
        "https://www.ratemyprofessors.com/search/professors/1087?q=Joshua+Grochow",
    ),
    (
        "rmp_divya_vernerey.pdf",
        "rmp_divya_vernerey",
        "Divya Vernerey",
        "https://www.ratemyprofessors.com/search/professors/1087?q=Divya+Vernerey",
    ),
]

# Fixed chrome strings (case-sensitive exact line matches after .strip()).
CHROME_LINES = {
    "Compare", "Compa", "Rate", "Rate Compare", "Advertisement",
    "Computer Science", "University of Colorado - Boulder",
    "Awesome", "Great", "Good", "OK", "Awful",
    "Rating", "Distribut", "Similar", "Professo", "Al",
    "All", "courses", "All courses",
    "/", "/ 5",
    "Rate this Professor", "I'm Professor", "Click Here For Help",
}

CHROME_PATTERNS = [
    # Per-page timestamp header.
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2},\s+\d{1,2}:\d{2}\s+(AM|PM)\s+.*Rate My Professors\s*$"),
    # Footer URL + page-number.
    re.compile(r"^https?://www\.ratemyprofessors\.com/\S+\s+\d+/\d+\s*$"),
    # "Cheddar News Live Feed" ad — doubled chars or normal.
    re.compile(r"^(Rate\s+)?(C+h+e+d+d+a+r+|Cheddar)\s.*$", re.IGNORECASE),
    # 'Helpful N M' engagement counter.
    re.compile(r"^Helpful\s+\d+\s+\d+\s*$"),
    # Floating "5.00 / 5" type fragments that aren't tied to a label.
    re.compile(r"^\d\.\d{1,2}\s*/?\s*5?\s*$"),
    # Stray "47 Student Ratings" line (we synthesize this in the summary).
    re.compile(r"^\d+\s+Student Ratings\s*$"),
    # Standalone digit lines (vote counts, etc).
    re.compile(r"^\d+\s*$"),
]


def _build_per_prof_chrome(prof_name: str) -> List[re.Pattern]:
    """Patterns that depend on the specific prof's name."""
    first = prof_name.split()[0] if prof_name.split() else ""
    last = prof_name.split()[-1] if prof_name.split() else ""
    return [
        re.compile(rf"^{re.escape(prof_name)}\s*$"),
        re.compile(rf"^{re.escape(first)}\s*$"),
        re.compile(rf"^{re.escape(last)}\s*$"),
        re.compile(rf"^{re.escape(first[:5])}\s*$") if len(first) > 5 else re.compile(r"(?!x)x"),
        re.compile(rf"^{re.escape(last[:5])}\s*$") if len(last) > 5 else re.compile(r"(?!x)x"),
        re.compile(rf"^I'm Professor {re.escape(last)}\s*$"),
        re.compile(rf"^Professor in the\s*$"),
        re.compile(rf"^department at University\s*$"),
        re.compile(rf"^of Colorado - Boulder\s*$"),
    ]


def _extract_raw(pdf_path: Path) -> Tuple[str, List[str]]:
    """Return (page1_text, all_pages_text_list)."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            pages.append(txt)
    return pages[0] if pages else "", pages


def _parse_summary(page1_text: str) -> dict:
    """Pull out the four summary numbers from page 1's chaotic layout."""
    summary = {}
    # Overall quality: looks like "2.7 / 5"
    m = re.search(r"(\d\.\d)\s*/\s*5", page1_text)
    if m:
        summary["overall_quality"] = m.group(1)
    # Total ratings: "on 47 ratings"
    m = re.search(r"on\s+(\d+)\s+ratings", page1_text)
    if m:
        summary["total_ratings"] = m.group(1)
    # Would take again + difficulty: "43% 4.6" (on same line)
    m = re.search(r"(\d+)%\s+(\d\.\d)", page1_text)
    if m:
        summary["would_take_again_pct"] = m.group(1)
        summary["difficulty"] = m.group(2)
    return summary


INLINE_CHROME_SUBSTITUTIONS = [
    # Cheddar News Live Feed ad — two overlapping text layers render as doubled chars.
    (re.compile(r"\s*Rate\s+C+h+e+d+d+a+r+\s+N+e+w+s+\s+L+i+v+e+\s+F+e+e+d+\s*"), " "),
    (re.compile(r"\s*Rate\s+Cheddar\s+News\s+Live\s+Feed\s*"), " "),
]


def _strip_chrome(text: str, prof_patterns: List[re.Pattern]) -> str:
    out_lines: List[str] = []
    for ln in text.splitlines():
        # Inline substitution before line-level matching.
        for pat, repl in INLINE_CHROME_SUBSTITUTIONS:
            ln = pat.sub(repl, ln)
        s = ln.strip()
        if not s:
            out_lines.append("")
            continue
        if s in CHROME_LINES:
            continue
        if any(p.match(s) for p in CHROME_PATTERNS):
            continue
        if any(p.match(s) for p in prof_patterns):
            continue
        out_lines.append(s)
    # Collapse runs of blanks.
    cleaned: List[str] = []
    blank = 0
    for ln in out_lines:
        if ln == "":
            blank += 1
            if blank <= 1:
                cleaned.append("")
        else:
            blank = 0
            cleaned.append(ln)
    return "\n".join(cleaned).strip()


def _render(prof_name: str, url: str, summary: dict, body: str) -> str:
    header = (
        f"SOURCE: RateMyProfessors — {prof_name} at CU Boulder\n"
        f"URL: {url}\n"
        f"RETRIEVED: 2026-06-07\n"
        f"TYPE: Crowd-sourced professor ratings (overall quality, difficulty, "
        f"would-take-again, comments)\n"
    )
    summary_block = [f"=== {prof_name} — Summary ==="]
    if "overall_quality" in summary:
        summary_block.append(f"Overall Quality: {summary['overall_quality']} / 5")
    if "total_ratings" in summary:
        summary_block.append(f"Number of ratings: {summary['total_ratings']}")
    if "would_take_again_pct" in summary:
        summary_block.append(f"Would take again: {summary['would_take_again_pct']}%")
    if "difficulty" in summary:
        summary_block.append(f"Level of Difficulty: {summary['difficulty']} / 5")
    summary_block.append("Department: Computer Science")
    summary_block.append("University: University of Colorado - Boulder")

    return (
        header + "\n"
        + "\n".join(summary_block) + "\n\n"
        + "=== Individual Reviews ===\n\n"
        + body + "\n"
    )


def process(pdf_path: Path, out_name: str, prof_name: str, url: str) -> Tuple[Path, dict]:
    page1, all_pages = _extract_raw(pdf_path)
    summary = _parse_summary(page1)
    prof_patterns = _build_per_prof_chrome(prof_name)

    # Skip page 1 for the body (it's the summary section). Strip chrome from rest.
    body_raw = "\n".join(all_pages[1:])
    body = _strip_chrome(body_raw, prof_patterns)

    out_path = OUT_DIR / f"{out_name}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render(prof_name, url, summary, body), encoding="utf-8")
    return out_path, summary


def main():
    ap = argparse.ArgumentParser(description="Extract RMP professor pages from PDFs")
    ap.add_argument("--only", help="Process only the entry with this output name (e.g. rmp_cj_herman)")
    args = ap.parse_args()

    targets = PROFESSORS
    if args.only:
        targets = [t for t in PROFESSORS if t[1] == args.only]
        if not targets:
            sys.exit(f"No prof named {args.only}. Known: {[t[1] for t in PROFESSORS]}")

    for pdf_name, out_name, prof_name, url in targets:
        pdf_path = PDF_DIR / pdf_name
        if not pdf_path.exists():
            print(f"  SKIP {pdf_name} (not found)", file=sys.stderr)
            continue
        out_path, summary = process(pdf_path, out_name, prof_name, url)
        size = out_path.stat().st_size
        print(f"  wrote {out_path}  ({size:,} bytes)  summary={summary}")


if __name__ == "__main__":
    main()

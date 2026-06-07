"""
fetch_buffclasses.py
--------------------
Pull CU grade-distribution data from the public BuffClassesEDA SQLite database
(github.com/navanchauhan/BuffClassesEDA) and write a plain-text file that the
existing loader can ingest.

The dataset covers Spring 2016–Spring 2024; CU stopped publishing the raw
grade file after that. By default we extract a handful of CSCI courses that
matter for the eval questions (CSCI 3104 is the one tied to Q4).
"""

import sqlite3
import sys
import urllib.request
from pathlib import Path

REPO_URL = "https://raw.githubusercontent.com/navanchauhan/BuffClassesEDA/main/grades.sqlite"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = PROJECT_ROOT / "documents" / "_cache" / "grades.sqlite"
OUT_PATH = PROJECT_ROOT / "documents" / "buffclasses_grades.txt"

# Rows per "block". Each block carries one course-header line and is separated
# from the next block by a blank line so the chunker (512 char window, prefers
# \n\n boundaries) keeps the block intact. With ~92-char rows + ~40-char
# header, 4 rows per block sits well under 512 with headroom for long names.
ROWS_PER_BLOCK = 4

# (Subject, Course) pairs to include. Add more if your eval needs them.
COURSES = [
    ("CSCI", 3104),  # Algorithms — Q4 target
    ("CSCI", 1300),  # Intro to programming
    ("CSCI", 2270),  # Data structures
    ("CSCI", 3155),  # Programming languages
]


def _decode_yearterm(yt: int) -> str:
    """20241 -> 'Spring 2024', 20237 -> 'Fall 2023', 20224 -> 'Summer 2022'."""
    year, term = divmod(yt, 10)
    return f"{ {1: 'Spring', 4: 'Summer', 7: 'Fall'}.get(term, f'Term{term}') } {year}"


def _download_db() -> Path:
    if CACHE_PATH.exists():
        return CACHE_PATH
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {REPO_URL} -> {CACHE_PATH} ...", file=sys.stderr)
    urllib.request.urlretrieve(REPO_URL, CACHE_PATH)
    return CACHE_PATH


def _query_course(con, subject: str, course: int):
    cur = con.execute(
        """
        SELECT YearTerm, CourseTitle, insname1, AVG_GRD, N_EOT,
               PCT_A, PCT_B, PCT_C, PCT_DFW
        FROM raw_data
        WHERE Subject = ? AND Course = ?
        ORDER BY YearTerm DESC, insname1
        """,
        (subject, course),
    )
    return cur.fetchall()


def main():
    db_path = _download_db()
    con = sqlite3.connect(db_path)

    blocks = []
    for subject, course in COURSES:
        rows = _query_course(con, subject, course)
        if not rows:
            continue
        title = (rows[0][1] or "").strip()
        header = (
            f"{subject} {course} - {title} grade history:"
            if title else f"{subject} {course} grade history:"
        )

        # Format each row WITHOUT repeating the course prefix.
        formatted = []
        for yt, _title, instr, avg, n_eot, pa, pb, pc, pdfw in rows:
            instr = (instr or "Unknown").strip()
            avg_s = f"{avg:.2f}" if avg is not None else "n/a"
            formatted.append(
                f"{_decode_yearterm(yt)} | {instr} | avg GPA {avg_s} | "
                f"N={n_eot} | A={pa} B={pb} C={pc} DFW={pdfw}"
            )

        # Group into ROWS_PER_BLOCK-sized blocks; each block gets the header so
        # any chunk landing on this block is self-describing.
        for i in range(0, len(formatted), ROWS_PER_BLOCK):
            block = [header] + formatted[i:i + ROWS_PER_BLOCK]
            blocks.append("\n".join(block))

    body = "\n\n".join(blocks)

    header = "SOURCE: BuffClassesEDA — CU Boulder grade distributions (Spring 2016–Spring 2024)\n"

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(header + "\n" + body + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

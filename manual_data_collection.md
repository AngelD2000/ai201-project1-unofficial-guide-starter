# Manual Data Collection — 7 remaining sources

Automated fetch got 3 of 10 sources (GradCafe, Niche, Indeed → in `data/raw/`).
The 7 below block scrapers and need manual copy. **4 of your 5 eval questions
depend on these**, so they're not optional.

Save each as a plain `.txt` file in `data/raw/` using the SAME header format as
the existing files (so the loader parses them). Minimal header:

```
SOURCE: <name>
URL: <url>
RETRIEVED: 2026-06-07
TYPE: <short description>

<paste the real content here>
```

---

## Priority 1 — eval-critical

### 01_rmp_cj_herman.txt  (RMP — Q1: "Is CJ Herman's class difficult?")
RMP is JavaScript-rendered and robots-disallowed. Easiest path:
1. Open the professor's RMP page in your browser.
2. Copy the overall quality score, the **difficulty score (your expected answer is
   4.6/5.0)**, would-take-again %, and ~10-15 individual rating comments.
3. Paste as plain text. One rating per line is fine.
Tip if copy is messy: browser DevTools → Network tab → look for the GraphQL
response (RMP loads ratings via a GraphQL POST) and copy the JSON, or just
select-all the visible page text.

### 02_reddit_perspectives.txt  (Reddit — CS majors perspectives)
### 06_reddit_cost.txt          (Reddit — Q2: reduce cost of attendance)
### 10_reddit_dorms.txt         (Reddit — Q3: dorm laundry tips)
### 07_reddit_diversity.txt     (Reddit — diversity/acceptance)
Fastest reliable trick for any Reddit thread — **append `.json` to the URL**:
`https://www.reddit.com/r/cuboulder/comments/<id>/<slug>/.json`
Open in browser (logged in), copy the JSON, and pull out the post `selftext`
plus each comment `body`. Or run PRAW with your API creds (cleaner for many
comments). Keep the post title + body as the first block, then one comment per
paragraph so chunking can split on `\n\n`.

### 08_coursicle_csci.txt  (Coursicle — Q4: CSCI 3104 algorithms prof)
Returned HTTP 429 (rate-limited). Wait a few minutes, open
`coursicle.com/colorado/courses/CSCI/`, and copy CSCI 3104's professor list +
ratings. Your expected answer centers on Joshua Grochow (caring, available,
heavy homework load); also capture Robby Green, Peter Ly, Benjamin Waggoner,
Mary Monroe.

## Priority 2

### 03_buffclasses_grades.txt  (CU grades database)
Query-driven app — the landing page has no data. Run a few searches on
`web.navan.dev/BuffClassesEDA/` (e.g. by class code `CSCI 3104`, `CSCI 1300`,
or by instructor) and paste the returned average-grade rows. Note: coverage is
Spring 2016–Spring 2024; CU disabled the public grade file after that. Raw data
also lives in the project's GitHub repo (navanchauhan/BuffClassesEDA) if you'd
rather pull a CSV.

---

After dropping these in `data/raw/`, just re-run the loader + chunker — no code
changes needed. We'll then re-inspect chunking on a long Reddit thread, since
that's the exact case your chunking strategy was designed around.
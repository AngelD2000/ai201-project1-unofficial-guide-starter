# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:** 259

**Sample chunks** (output of `.venv/bin/python chunking.py --show 5 96 120 140 256`):

```
(corpus: 259 chunks across 12 documents — valid id range 0..258)

--- chunk 5 (502 chars) | BuffClassesEDA — CU Boulder grade distributions (Spring 2016–Spring 2024) ---
Spring 2019 | RECKWERDT,ERIC ASHER | avg GPA 2.89 | N=24 | A=38% B=33% C=21% DFW=15%
Fall 2018 | CHEN, LIJUN | avg GPA 2.22 | N=49 | A=10% B=35% C=33% DFW=34%
Fall 2018 | HOENIGMAN, RHONDA OLCOTT | avg GPA 2.63 | N=63 | A=27% B=33% C=21% DFW=23%
Fall 2018 | HOENIGMAN, RHONDA OLCOTT | avg GPA 2.35 | N=80 | A=15% B=38% C=28% DFW=26%
Fall 2018 | RECKWERDT,ERIC ASHER | avg GPA 2.63 | N=12 | A=42% B=17% C=17% DFW=25%
Spring 2018 | CLAUSET, AARON JULIAN | avg GPA 3.01 | N=176 | A=45% B=31% C=11% DFW=24%

--- chunk 96 (242 chars) | Reddit — diversity and acceptance ---
Unknownjarman OP • 1y ago
Iʼm always on edge anywhere better safe than sorry. Also I play in a band maybe Iʼll find some new
bandmates there

Routine_Force8625 • 1y ago
i play guitar, and am into punk and french house. so holler

1 more reply

--- chunk 120 (487 chars) | Reddit — dorm life tips (Q3 source for laundry) ---
one that will be bright enough to fill the room, so you can come back at night, turn it on, and be in a
comfortable environment. I've had this one for all 6 years, and it's now happily in my apartment. Collapses
away and is packed easily.
- Shop fan.
A tall rotating one will be annoying during moves. I ended up opting for a proper shop fan, which can clamp
onto edges, be hung on the wall or magnetically stuck on the side of the microwave, and is quite powerful.
- Portable door lock.

--- chunk 140 (297 chars) | Reddit — CS majors perspectives at CU Boulder ---
However Iʼve heard mixed opinions on if CU is actually better than CSU/Mines or worth it tuition wise. Itʼs the
second most expensive school Iʼm looking at next to Purdue, but it also seems really impressive for an in state
school.
Any thoughts, perspectives, experiences, regrets?
Thanks so much!

--- chunk 256 (323 chars) | Niche — University of Colorado Boulder student reviews ---
[Junior, 5/5] CU Boulder has allowed me to delve into experimental learning with classes focused on applying conceptual understandings to real-world problems. The learning environment is empowering.

[Freshman, 5/5] I love the culture and the academics are very good. The campus life is good and it is easy to get involved.
```

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
`BAAI/bge-small-en-v1.5` via sentence-transformers, running locally. 384-dimensional embeddings stored in a local ChromaDB collection with cosine distance.

**Why this model (and why I swapped):**
My initial pick was `all-MiniLM-L6-v2` because it's the default sentence-transformers model and is fast on CPU. During testing it failed on course-specific questions because it didn't reliably distinguish course numbers (`CSCI 1300` and `CSCI 3104` embedded as very similar). For the eval question *"Who should I take CSCI 3104 with?"*, the top 40 retrieved chunks were 39× CSCI 1300/2270 grade rows and only 1× actually-CSCI-3104 content — even though my corpus has 19 Coursicle reviews and dedicated RMP pages for CSCI 3104 professors. The LLM correctly responded *"I don't have enough information on that"* because the retriever wasn't surfacing the right material.

I swapped in `BAAI/bge-small-en-v1.5`, which is trained with a retrieval-specific contrastive objective on MS MARCO-style query/passage pairs. On the same query and the same chunks, the top 10 became:

| rank | source | distance |
|------|--------|----------|
| 1 | Coursicle — Grochow review (CSCI 3104) | 0.237 |
| 2 | BuffClassesEDA — CSCI 3104 grade history | 0.246 |
| 3 | RMP — Joshua Grochow (CSCI 3104) | 0.249 |
| 4–6 | BuffClassesEDA — CSCI 3104 grade history | 0.251–0.256 |
| 7 | Coursicle — Grochow review (CSCI 3104) | 0.268 |
| 8–9 | Coursicle — Vernerey reviews (CSCI 3104) | 0.273–0.275 |
| 10 | BuffClassesEDA — CSCI 3104 grade history | 0.275 |

All 10 hits are about CSCI 3104, mixing professor reviews and the right grade data. The LLM now answers the question with a concrete recommendation (Grochow + Vernerey) backed by Coursicle + RMP sources.

The other fix I made alongside the model swap was restructuring `documents/buffclasses_grades.txt` so each chunk carries one course header (`CSCI 3104 - Algorithms grade history:`) at the top of a 4-row block instead of repeating the course prefix on every row. Without that, BuffClasses chunks were lexically dense in "CSCI" tokens and dominated retrieval. The model swap is what made retrieval semantically correct; the chunk restructure is what kept any one course from drowning out the others.

**Production tradeoff reflection:**
This system is sized for the CU Boulder CS student body (~38k enrolled across the university, far fewer CS students), so latency and faithfulness to original student reviews matter more than per-query cost. `bge-small-en-v1.5` is the right default at this scale: small enough to embed the corpus once on a laptop, accurate enough on noisy review text. If this scaled to all U.S. universities (~18M+ students), I'd weigh three trade-offs differently: (1) a larger model like `bge-large-en-v1.5` or `e5-large-v2` for accuracy on long Reddit threads where the relevant point is buried mid-post; (2) a hosted embedding API (Voyage, Cohere, OpenAI `text-embedding-3-large`) to avoid maintaining GPU inference for embedding refreshes, accepting per-query cost in exchange; (3) a re-ranker (cross-encoder) on the top 20–50 hits to fix borderline cases like the one above without retraining the whole index. Multilingual support isn't a priority for a U.S.-only student-review corpus, but context length would matter more — `bge-small` caps at 512 tokens, which clips long Reddit posts.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

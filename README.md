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


This is an unofficial collection of student perspectives on the CU Boulder Computer Science department, covering professors, courses, workload, grad admissions, campus culture, and cost of living. This knowledge helps students make informed decisions that official sources can't support — official channels only surface credentials, syllabi, and institutional messaging, with no incentive to publish negative feedback, difficulty warnings, or honest comparisons between instructors.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|-------------|-----------------|
| 1 | Rate my professor | Website that is commonly used to rate a professor for a specific university, their quality and difficulty of the class | https://www.ratemyprofessors.com/search/professors/1087?q=* |
| 2 | Reddit | Students describing their experiences and thoughts about cs department of CU Boulder | https://www.reddit.com/r/cuboulder/comments/1qkaql1/perspectives_from_cu_boulder_cs_majors/ |
| 3 | CUBoulderGradesDatabase  | Database on average grades in each class  | https://web.navan.dev/BuffClassesEDA/ |
| 4 | Niche | Overall review of cu boulder | https://www.niche.com/colleges/university-of-colorado-boulder/reviews/ |
| 5 | GradCafe | MS/PhD program application |https://www.thegradcafe.com/survey?q=University+of+Colorado+Boulder&program=Computer+Science |
| 6 | Reddit | Cost of attendance |https://www.reddit.com/r/cuboulder/comments/1jnjloz/is_there_any_way_to_reduce_cost_of_attendance/ |
| 7 | Reddit | Diversity and acceptance | https://www.reddit.com/r/cuboulder/comments/1i8fgrx/how_accepting_is_cu_of_trans_people/ |
| 8 | Coursicle| Course ratings |  https://www.coursicle.com/colorado/courses/CSCI/ |
| 9 | Indeed| TA, employee reviews | https://www.indeed.com/cmp/Univeristy-of-Colorado-Boulder-1/reviews |
| 10 | Reddit | Dorm life tips| https://www.reddit.com/r/cuboulder/comments/1tske4d/if_youre_moving_into_a_dorm_for_the_first_time/ |


---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->
**Chunk size:**
512 characters, there's a wide variety of data types some are one liner statistic data on the course and some are long discussion forumns from reddit. Even though the post itself is long, it is often split into multiple paragraphs or have different meanings.

**Overlap:**
100 characters. The average sentence is typically 15-20 words so around 75-100 characters. Given that these discussion posts are informal and often have multiple points in one post (with one overarching topic), 100 characters overlap should retain enough context to connect a chunk back to the broader point being made.

**Why these choices fit your documents:**
Over half of the sources are comments that fall within the 250 - 300 character range, but some of the sources are of long discussion posts with multiple points in an overarching topic. The 512 isn't going to be enough for the entire post but it should be relatively good for a single paragraph or point in these long posts. Paragraph splitting would have difficulties with the inline structure from reddit.

**Final chunk count:** 255

**Sample chunks** (output of `.venv/bin/python chunking.py --show 5 96 120 140 252  `):

```
(corpus: 255 chunks across 12 documents — valid id range 0..254)

--- chunk 5 (379 chars) | BuffClassesEDA — CU Boulder grade distributions (Spring 2016–Spring 2024) ---
CSCI 3104 - Algorithms grade history:
Fall 2019 | AGRAWAL,SHIVENDRA | avg GPA 2.05 | N=93 | A=15% B=25% C=31% DFW=40%
Fall 2019 | HOENIGMAN, RHONDA OLCOTT | avg GPA 2.09 | N=64 | A=27% B=23% C=11% DFW=47%
Fall 2019 | HOENIGMAN, RHONDA OLCOTT | avg GPA 2.33 | N=75 | A=28% B=17% C=32% DFW=33%
Spring 2019 | GROCHOW,JOSHUA ABRAHAM | avg GPA 3.08 | N=158 | A=56% B=18% C=13% DFW=27%

--- chunk 96 (253 chars) | Reddit — reduce cost of attendance ---
journey37• 1y ago
This is the way 100%

vseprviper • 1y ago
…as long as you confirm beforehand that CU will accept the transfer credits. That program
specifically is pretty elitist and very proud of its freshman weedout courses lmao Log In

1 more reply

--- chunk 120 (502 chars) | Reddit — dorm life tips (Q3 source for laundry) ---
- For storing toiletries and clothes, get these three items.
For toiletries, get one of these hanging roll-ups. I can't exaggerate how efficient it made everything. Hang it in
your closet or somewhere better, and use it for your place to put things like your body wash after showering.
Using coathangers or the provided drawers will limit your storage. Hanging shelves are your best bet. These
have survived me until now. There is also a trick for packing them. Instead of emptying out all your clothes

--- chunk 140 (161 chars) | Reddit — dorm life tips (Q3 source for laundry) ---
videos or family guy or something before bed together. Was never a pain to deal with, and since TVs are
so cheap nowadays we just donated it after a year of use.

--- chunk 252 (323 chars) | Niche — University of Colorado Boulder student reviews ---
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

SYSTEM_PROMPT = f"""You are an unofficial guide to the CU Boulder Computer Science department, drawing on student reviews, Reddit posts, course ratings, and grade data.

You MUST follow these rules without exception:

1. Answer ONLY using information found in the CONTEXT block of the latest user message. Do not use prior knowledge of CU Boulder, professors, courses, or any other fact not present in the CONTEXT.
2. If the CONTEXT does not contain enough information to answer the question, reply with EXACTLY this sentence and nothing else: "{NO_INFO_REPLY}"
3. Do not invent professors, courses, numbers, dates, grades, GPAs, or quotes. If a detail is not literally in the CONTEXT, leave it out.
4. Do NOT include a sources list, citations, footnotes, "[1]" markers, or URLs in your answer. The system appends sources automatically after your reply; do not duplicate them.
5. Keep your answer concise (roughly under 150 words) and paraphrase the retrieved snippets faithfully. Prefer direct, plain language.
"""

**How source attribution is surfaced in the response:**
The model is explicitly told not to write citations itself, sources are surfaced by _unique_sources, which builds the citation list in Python from the chunks that were already retrieved after the LLM has answered.


## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Is CJ Herman's class difficult? | Yes 4.6 out of 5.0 overall difficulty | According to the comments, CJ Herman's class is considered difficult. Many students have rated the difficulty as 5.0, with one student stating that the tests were "incredibly difficult" and another saying that the class requires a lot of work and can be overwhelming if taken in a heavy semester. However, some students also mention that the difficulty is due to the challenging material and assignments, rather than poor teaching. Overall, the consensus is that CJ Herman's class is demanding, but some students appreciate the challenge and feel that it helps them learn. | Relevant | Accurate |
| 2 |What are some options to reduce cost of attendance? | Use library's course reserves for some textbooks, RA, community college credits | To reduce the cost of attendance, some options include living off-campus in a shared apartment, eating cheaper food alternatives, and buying used supplies such as books and computers. Additionally, considering refurbished computers and looking for student discounts can also help save money. Other options mentioned include graduating in 3 or 3.5 years, attending a local community college before reapplying to CU Boulder, getting a job and working to give earnings to parents, and exploring need-based housing assignments | Relevant | Accurate |
| 3 | What are some tips for doing laundry in a CU Boulder dorm?| Based on the Reddit dorm tips thread, laundry is least crowded early in the week and most crowded on Sunday. Students should set a phone timer for their laundry so someone doesn't pull wet clothes out onto the floor to use the machine. Detergent sheets are recommended over tide pods after a bag popped open during a move. A hamper bag is also suggested over a basket since dorms often require climbing stairs to reach laundry machines.| To do laundry in a CU Boulder dorm, consider the following tips: do laundry early in the week as it is least crowded, and avoid Sundays when it is most crowded. Additionally, using ultralight towels instead of fluffy ones can be helpful as they dry faster and take up less space. There is also the option to shower at the campus gym or in some academic buildings, and using a compact towel can be convenient for this. | Partially Relevant |  Accurate|
| 4 | Who's a good professor for CSCI 3104 algorithms? | Based on Coursicle, Joshua Grochow is frequently recommended — students describe him as caring, very available at office hours, and responsive to emails. The tradeoff is an extremely heavy homework load. Known professors for this course include Grochow, Divya Vernerey and others.| Both Joshua Grochow and Divya Vernerey are considered good professors for CSCI 3104 Algorithms. Joshua Grochow is knowledgeable and good at explaining things, but the class can be hard and has a lot of homework. Divya Vernerey is described as clear, organized, and caring, with a great teaching style, and her lectures are helpful in breaking down the material.| Relevant| Accurate |
| 5 | What GPA do I need to get into the CU Boulder MS CS program? | Based on GradCafe Fall 2026 data, accepted MS students have GPAs around 3.70 (one confirmed acceptance at 3.70). PhD rejections are coming in across a wide GPA range including 3.65, 3.78, 3.81, 3.83, 3.87, 3.91, 3.98, and even 4.00 — suggesting PhD admissions is highly competitive beyond just GPA, with research experience and publications mattering significantly. | Based on the information provided, it appears that a GPA of around 3.70 may be sufficient to get into the CU Boulder MS CS program. This is according to the GradCafe source, which mentions that one of the confirmed Masters acceptances had a GPA of 3.70. However, it's worth noting that GPA is just one factor considered in the admissions process, and other factors such as research experience and fit may also be important.| Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

NOTE: For question 4 you'll see a discrepency of after **Known Professors** because when I constructed the expected answer originally I did not check how many of them are Univesrity of Colorado Boulder professors and have some comments, I landed on Joshua Grochow and Divya Vernerey after the fact.

### Sample Conversations
### Question 1: 

user: Is CJ Herman's class difficult?

assistant: According to the comments, CJ Herman's class is considered difficult. Many students have rated the difficulty as 5.0, with one student stating that the tests were "incredibly difficult" and another saying that the class requires a lot of work and can be overwhelming if taken in a heavy semester. However, some students also mention that the difficulty is due to the challenging material and assignments, rather than poor teaching. Overall, the consensus is that CJ Herman's class is demanding, but some students appreciate the challenge and feel that it helps them learn.

**Sources:**
- RateMyProfessors — CJ Herman at CU Boulder

user: What's he's score on rate my professor?

assistant: CJ Herman's overall quality score on RateMyProfessors is 2.7 out of 5, based on 47 ratings. His level of difficulty score is 4.6 out of 5.

**Sources:**
- RateMyProfessors — CJ Herman at CU Boulder


### Question 2
user: What are some options to reduce cost of attendance?

assistant: To reduce the cost of attendance, some options include living off-campus in a shared apartment, eating cheaper food alternatives, and buying used supplies such as books and computers. Additionally, considering refurbished computers and looking for student discounts can also help save money. Other options mentioned include graduating in 3 or 3.5 years, attending a local community college before reapplying to CU Boulder, getting a job and working to give earnings to parents, and exploring need-based housing assignments.

**Sources:**
- Reddit — reduce cost of attendance
- Niche — University of Colorado Boulder student reviews


### Question 3
user: What are some tips for doing laundry in a CU Boulder dorm?

assistant: To do laundry in a CU Boulder dorm, consider the following tips: do laundry early in the week as it is least crowded, and avoid Sundays when it is most crowded. Additionally, using ultralight towels instead of fluffy ones can be helpful as they dry faster and take up less space. There is also the option to shower at the campus gym or in some academic buildings, and using a compact towel can be convenient for this.

**Sources:**
- Reddit — dorm life tips (Q3 source for laundry)
- Niche — University of Colorado Boulder student reviews
- Reddit — reduce cost of attendance


### Question 4
user: Who's a good professor for CSCI 3104 algorithms?

assistant: Both Joshua Grochow and Divya Vernerey are considered good professors for CSCI 3104 Algorithms. Joshua Grochow is knowledgeable and good at explaining things, but the class can be hard and has a lot of homework. Divya Vernerey is described as clear, organized, and caring, with a great teaching style, and her lectures are helpful in breaking down the material.

**Sources:**
- Coursicle — CU Boulder CSCI 3104 (Algorithms) professor list
- RateMyProfessors — Joshua Grochow at CU Boulder
- BuffClassesEDA — CU Boulder grade distributions (Spring 2016–Spring 2024)

### Question 5
user: What GPA do I need to get into the CU Boulder MS CS program?

assistant: Based on the information provided, it appears that a GPA of around 3.70 may be sufficient to get into the CU Boulder MS CS program. This is according to the GradCafe source, which mentions that one of the confirmed Masters acceptances had a GPA of 3.70. However, it's worth noting that GPA is just one factor considered in the admissions process, and other factors such as research experience and fit may also be important.

**Sources:**
- Reddit — CS majors perspectives at CU Boulder
- GradCafe — CU Boulder Computer Science graduate admissions results
- RateMyProfessors — Divya Vernerey at CU Boulder
- Niche — University of Colorado Boulder student reviews
- RateMyProfessors — Joshua Grochow at CU Boulder
- BuffClassesEDA — CU Boulder grade distributions (Spring 2016–Spring 2024)
- RateMyProfessors — CJ Herman at CU Boulder
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
"What are some tips for doing laundry in a CU Boulder dorm?"

**What the system returned:**
"To do laundry in a CU Boulder dorm, consider the following tips: do laundry early in the week as it is least crowded, and avoid Sundays when it is most crowded. Additionally, using ultralight towels instead of fluffy ones can be helpful as they dry faster and take up less space. There is also the option to shower at the campus gym or in some academic buildings, and using a compact towel can be convenient for this."

**Root cause (tied to a specific pipeline stage):**
The failure happens at **chunking and retrieval**. The Reddit dorm tips thread covers many topics (laundry, towels, toiletries, showering) across one long post. Because chunks are split by character count rather than by topic, laundry-specific advice (phone timer so no one pulls your wet clothes out, detergent sheets over tide pods, hamper bag over a basket for stair-heavy dorms) ended up in different chunks than towel and shower tips. At retrieval, the towel and shower chunks scored high on cosine similarity to the query — they came from the same dorm tips document and share vocabulary like "dorm" and "CU Boulder." The result is that the model answered correctly on timing (early in the week, avoid Sundays) but replaced the most actionable laundry-specific tips with adjacent advice about towels and gym showers that wasn't relevant to the question.

**What you would change to fix it:**
Structure the dorm tips document with explicit topic headers (e.g., `## Laundry`, `## Toiletries`) before chunking so that related advice stays in the same chunk. This keeps laundry-specific tips together and prevents semantically adjacent but topically unrelated content from outranking them at retrieval.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Clear guidelines for the LLM to use after initial research on the injestion data. Allowed me to progress the assignment rather quickly after establishing the baseline.

**One way your implementation diverged from the spec, and why:**
Model usage, I originally went with the suggested embedding model but it was not able to distinguish class numbers like CSCI 1300 and CSCI 3104.

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
The resources that I'm using for injestion data, I asked if the AI could scrape any information before I went in manually.
- *What it produced:*
Documents such as buffclasses_grades.txt and code such as thta fetch_buffclasses.py
- *What I changed or overrode:*
I changed the structure of buffclasses_grades.txt afterwards because initially with how the document was setup we'd lose metadata on which row items belonged to which class due to chunking.

**Instance 2**
- *What I gave the AI:*
The specs for chunking and embedding that was determined previously
- *What it produced:*
Code that did exactly to the spec like chunking.py, embed.py, generate.py etc.
- *What I changed or overrode:*
Default k, it had set it to 5 for some reason but my baseline was 10.

# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **A writer submits text.** `POST /submit` receives JSON `{"text": "...", "creator_id": "..."}`.
2. **The route checks the input.** If `text` is missing, isn't a string, or is empty, it answers `400` and nothing gets scored.
3. **Signal one reads the text.** `detector.model_signal(text)` runs gpt2 locally and asks how predictable the text is. It returns a score from 0 to 1, where higher means more likely AI.
4. **Signal two measures the shape of the text.** `stylometry.style_signal(text)` looks at how much sentence lengths vary and how much punctuation is used. It returns a score from 0 to 1, where higher means more likely AI.
5. **The two scores become one.** `scoring.combine_signals(model_score, style_score)` combines them into a single score from 0 (confidently human) to 1 (confidently AI). Whichever signal reads more human gets 65% of the vote, so one signal can't produce an AI label on its own.
6. **The score becomes a label.** `scoring.score_to_label(score)` turns the number into one of three plain sentences: high-confidence human (0.35 or below), unsure (between), or high-confidence AI (0.65 or above).
7. **The decision is logged and returned.** `audit.log_decision(...)` appends a line to `logs/audit.jsonl` with a new `content_id`, the creator, both signal scores, the combined score, the guess, the label and status `decided`. The writer gets back `content_id`, `guess`, `confidence`, `label`, `model_score` and `style_score`.
8. **The writer can appeal.** If they disagree, they send that `content_id` and their reasoning to `POST /appeal`. The route checks the ID exists (`404` if not), then `audit.log_appeal(...)` appends an appeal entry with status `under_review` after the original decision, which stays unchanged, and confirms to the writer.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

`detector.py`, given to me. A local language model reads the text.

**What it measures:** How predictable the text is to a language model, measured as **perplexity**. gpt2 runs on my machine and checks, word by word, how surprised it is by what comes next. Low perplexity means "I could have guessed this". The perplexity is squashed onto 0 to 1 with a logistic curve centred on a perplexity of 45, which scores 0.5. **Low perplexity gives a high score, which means more likely AI.**

**Why that might differ between human and AI writing:** A language model writes by repeatedly choosing a likely next word, so its output tends to be text another model finds easy to predict. Human writing wanders more: odd word choices, sudden turns, specific details where a model would reach for typical ones.

**What it can't see:** Who actually wrote the text. Predictability isn't authorship. What this signal really rewards is **common words in short, ordinary sentences**, and plenty of people write that way: someone writing in a second language and sticking to words they're sure of, a younger writer, anyone writing plainly on purpose. Measured against gpt2, their writing scores about as machine-like as machine writing does. The reverse fails too. Dense prose full of rare words scores as human because rare words are exactly what the model can't predict, and AI can produce that prose on request. Other limits: gpt2 is a small, old model and not the one that wrote today's AI text, it reads only the first 400 tokens, and it can't score text under 3 tokens.

### Signal two — the style signal

`stylometry.py`, which I built. It measures the text as text, without reading it.

**What it measures:** The *shape* of the writing, with two measures:

- **Sentence length spread:** the standard deviation of words per sentence divided by the mean (the coefficient of variation), so long and short texts can be compared. It's rescaled so that 0.3 or below counts as fully AI-like and 1.0 or above as fully human-like.
- **Punctuation density:** commas, semicolons and opening parentheses per word, divided by 0.10 and capped at 1. Commas inside numbers like `1,000` aren't counted.

They're combined as `human = 0.6 × spread + 0.4 × punctuation`, and the signal returns `1 − human`, so **higher means more likely AI**. A third measure, the type-token ratio (unique words over total words, averaged over 50-word windows), is calculated but **weighted 0**. On my samples it pointed the wrong way (AI 0.91, human 0.81), and the gap was too small to trust in either direction.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-to-long sentences, because "most likely next word" produces average shapes. Human writing is lumpier: a three-word sentence next to a forty-word one. On punctuation, The Economist's 2026 analysis of 55,940 sentences (as reported by Fast Company) found LLMs use **fewer commas, semicolons and parentheses** than human writers, stringing long sentences together with "and". I left out em dashes because the same report found their use varies by model: Claude uses them more than humans, and ChatGPT now uses them least. On my three samples: clearly human **0.10**, clearly AI **0.73**, lightly-edited AI **0.56**.

**What it can't see:** The meaning. It has no idea what the text says, so anything that changes the shape without changing the substance moves the score: splitting or merging sentences, adding a few commas or parentheses, pasting in a quotation. That's cheap to do on purpose. My lightly-edited AI sample, which is the AI text rewritten casually with short sentences, a dash and a semicolon, already drifts to 0.56. It also misreads short texts. With fewer than two sentences there's no spread to measure, so a one-sentence submission currently reads as maximally AI-like. Most importantly, it shares signal one's blind spot. A plain human writer who uses even, short sentences and few commas looks AI-like to this signal **for the same reasons** signal one flags them, so the two signals don't cover for each other on the writer most likely to be wrongly accused.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** Whichever signal reads **more human** gets the bigger share of the vote. I don't weight by *which* signal it is (model or style). I weight by *which way it leans*: the lower of the two scores gets 65% and the higher gets 35%. Text only gets a confident AI label when **both** signals say AI, so one signal can never accuse a writer on its own. I chose this because a false positive, a person told their own writing looks machine-made, costs more than AI text slipping through as "unsure". The writer pays for a false positive, and an unsure label can still be appealed or reviewed.

**The numbers:**

```
combined = 0.65 × min(model_score, style_score) + 0.35 × max(model_score, style_score)
```

The weights live in `config.py` as `WEIGHT_LOWER_SIGNAL = 0.65` and `WEIGHT_HIGHER_SIGNAL = 0.35`. The labels use the thresholds `HUMAN_THRESHOLD = 0.35` and `AI_THRESHOLD = 0.65`. On my samples:

I tested with four deliberately chosen kinds of input, plus a second AI piece:

| Input | model_score | style_score | combined | label | Signals |
|---|---|---|---|---|---|
| clearly human (`samples/clearly_human.json`) | 0.44 | 0.10 | 0.22 | human | agree |
| clearly AI (`samples/clearly_ai.json`) | 0.75 | 0.73 | 0.74 | AI | agree |
| clearly AI (cat adoption paragraph) | 0.80 | 0.69 | 0.73 | AI | agree |
| technical human writing (forum answer about ML datasets) | 0.51 | **0.84** | 0.63 | unsure | **split** |
| lightly-edited AI (`samples/borderline.json`) | 0.35 | 0.56 | 0.42 | unsure | lean apart |

**Where they agree:** on the clear cases. Both AI texts get two high scores and the clearly human text gets two low ones.

**Where they disagree:** on the two inputs that matter most, the technical human writing and the lightly-edited AI. On both, the style signal is the one that's off.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** A human-written forum answer recommending a machine-learning textbook. The model signal is unsure about it (**0.51**). The style signal says AI (**0.84**). Printing the style measures separately showed why: the writer strings long clauses together with "and", "so" and "which", so the sentences are long and even (spread 0.34, almost the AI floor), and it has only 5 commas in 170 words (punctuation 0.29). That's the pattern the Economist report linked to AI, written by a person. My rule gives the more-human score 65% of the vote: 0.65 × 0.51 + 0.35 × 0.84 = **0.63**, so the label is **unsure**. A plain 50/50 average gives **0.675**, above the AI threshold of 0.65, which would have labelled a real person's writing as AI. This is the false positive the rule exists to prevent. It only cleared the threshold by 0.02, though, so it's a near miss, not a comfortable margin.

The same test exposed a weakness in my punctuation measure. The AI cat-adoption paragraph scores **0.78** on punctuation (human-like) because it's full of comma lists ("lifestyle, living space, and budget"). The human forum answer scores 0.29. On these two texts, comma count points the wrong way.

My lightly-edited AI sample is AI-written text rewritten casually: shorter sentences, a dash, a semicolon. The two signals disagree on it. The model signal reads it as human-ish (**0.35**) because the casual rewrite made the wording less predictable. The style signal leans AI (**0.56**) because the sentence lengths are still fairly even. My rule gives the more-human score 65% of the vote, which lands at **0.42**, so the label is **unsure**. It doesn't call it human, which would let it through, and it doesn't call it AI, which would be an accusation built on a weak signal.

The split where my rule matters most is one signal sure and the other on the fence, for example model **0.90** and style **0.50**. A plain 50/50 average gives 0.70, which is a confident AI label on the strength of one signal. My rule gives 0.65 × 0.50 + 0.35 × 0.90 = **0.64**, which stays unsure.

**What it costs:** AI text that fools just one signal, such as a light rewrite or some added punctuation, falls to "unsure" instead of being caught. It also **doesn't protect the plain human writer**. Both signals misread that writer the same way (common words, even sentences, few commas), so the two signals agree on "AI" and there's no more-human signal for the rule to lean on. Only the width of the unsure band can help that writer.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think this was probably written by a person. |
| unsure | 0.35 – 0.65 | We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it. |
| high-confidence AI | 0.65 – 1.00 | This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it. |

All three are reachable with real text: `samples/clearly_human.json` scored 0.22 (human), `samples/borderline.json` scored 0.42 (unsure), and `samples/clearly_ai.json` scored 0.74 (AI). The ranges leave no gap. `scoring.py::score_to_label` sends a score of 0.35 or below to human, 0.65 or above to AI, and everything in between to unsure.

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

The person reading "unsure" may have written every word themselves. My own forum answer about ML textbooks landed here, so this label has to work for an honest writer first. It says **we** can't tell, which puts the uncertainty on the tool and not on the writer. It explains *why* in plain words ("mixed results"). It says outright that this happens with a lot of genuine writing and **is not a finding against you**, because without that, "unsure" reads as "suspected". It ends with something the writer can do. I avoided "score", "confidence" and "threshold", and I never say "AI-generated" as a verdict.

The AI label is the one that does the most harm when it's wrong, so it says it's an estimate and not proof. It names the writers it misjudges most often (plain, even writing) and points straight to the appeal. The human label is short on purpose: it accuses no one, so it doesn't need caveats.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d @samples/borderline.json
```

```json
{
  "confidence": 0.4228,
  "content_id": "c_341353f86a75",
  "creator_id": "demo_instructor",
  "guess": "unsure",
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "model_score": 0.3489,
  "style_score": 0.56
}
```

**An appeal**

Using the real `content_id` from the submission above:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_341353f86a75", "reasoning": "I wrote this myself. I rewrote my notes on time management in my own casual style."}'
```

```json
{
  "content_id": "c_341353f86a75",
  "message": "Thanks. Your appeal has been recorded and a person will review this decision.",
  "status": "under_review"
}
```

An appeal for an ID that doesn't exist is refused with a `404` rather than silently "succeeding":

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_doesnotexist", "reasoning": "test"}'
```

```json
{
  "error": "not_found",
  "message": "No submission found with content_id 'c_doesnotexist'."
}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

The original decision for `c_341353f86a75` (status `decided`) is still there, unchanged. The appeal is appended after it with status `under_review`. The entry in between is another submission made in the same run.

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.4228,
      "content_id": "c_341353f86a75",
      "creator_id": "demo_instructor",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
      "model_score": 0.3489,
      "status": "decided",
      "style_score": 0.56,
      "timestamp": "2026-11-09T10:13:41+00:00"
    },
    {
      "combined_score": 0.738,
      "content_id": "c_f118a8a1b1f5",
      "creator_id": "demo_instructor",
      "guess": "ai",
      "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
      "model_score": 0.7544,
      "status": "decided",
      "style_score": 0.7291,
      "timestamp": "2026-11-09T10:13:41+00:00"
    },
    {
      "content_id": "c_341353f86a75",
      "creator_id": "demo_instructor",
      "event": "appeal",
      "reasoning": "I wrote this myself. I rewrote my notes on time management in my own casual style.",
      "status": "under_review",
      "timestamp": "2026-11-09T10:13:45+00:00"
    }
  ]
}
```

---

## How I Used AI

I used Claude Code throughout: to explain the starter code, to talk through designs before writing them, and to write and test code I had approved.

**Moment 1: designing `punctuation_density`**

- *What I asked for:* A punctuation measure that rewards punctuation humans commonly use and penalises punctuation AI commonly uses, then divides by the number of words. I also asked whether it's true that AI uses fewer commas than humans.
- *What came back:* Two lists: "AI-leaning" marks (em dash, semicolon, colon) and "human-leaning" marks (`!`, `?`, `...`, parentheses), with commas counted as neutral. Claude said it knew of no research on commas and that its impression was the *opposite*, that AI prose uses plenty of commas.
- *What I changed:* I found a Fast Company write-up of The Economist's 2026 analysis (55,940 sentences) that contradicted both points. LLMs use **fewer** commas, semicolons and parentheses than humans, and em dashes depend on the model. I gave it the article, and we dropped the two-list design. The measure now counts only commas, semicolons and opening parentheses per word, with no em dashes. I also chose to squash the result to 0–1 inside the function and to skip commas inside numbers like `1,000`. Lesson: the AI's "impression" was confidently wrong, and an outside source fixed it.

**Moment 2: wiring `/submit` and testing the signals on my own writing**

- *What I asked for:* An explanation of why my route returned `"content_id": "hardcoded"` even though it generated a real ID. Later, after I ran `stylometry.py` on a forum answer I wrote about ML textbooks, I asked for the two signals to be compared on it.
- *What came back:* It explained that `"hardcoded"` in quotes is a fixed string, while `content_id` without quotes is the variable. For my forum answer, it ran both signals and found they split: the model was unsure (0.51) and the style signal said AI (0.84), because my long, comma-light sentences look like the AI pattern.
- *What I changed:* I fixed `content_id` and `creator_id` in the response myself. The test on my own writing became the split case in my README. It showed my combining rule keeping me at "unsure" (0.63), where a plain average would have called me AI (0.675). It also showed that my punctuation measure points the wrong way on comma-list AI text. I wrote that down as a known weakness rather than tuning the weights to one example.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

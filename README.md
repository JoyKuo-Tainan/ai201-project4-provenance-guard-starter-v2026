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
5. **The two scores become one.** `scoring.combine_signals(model_score, style_score)` combines them into a single score from 0 (confidently human) to 1 (confidently AI).
6. **The score becomes a label.** `scoring.score_to_label(score)` picks one of three plain-language labels: high-confidence human, unsure, or high-confidence AI.
7. **The decision is logged and returned.** `audit.log_decision(...)` writes a `content_id`, both signal scores and the combined score to the audit log. The response carries `content_id`, `guess`, `confidence`, `label`, `model_score` and `style_score`. If the writer disagrees, they send that `content_id` to `POST /appeal`, which moves the item to `under_review`.


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

| Sample | model_score | style_score | combined | label |
|---|---|---|---|---|
| clearly human | 0.44 | 0.10 | 0.22 | human |
| clearly AI | 0.75 | 0.73 | 0.74 | AI |
| lightly-edited AI | 0.35 | 0.56 | 0.42 | unsure |

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:** My lightly-edited AI sample is AI-written text rewritten casually: shorter sentences, a dash, a semicolon. The two signals disagree on it. The model signal reads it as human-ish (**0.35**) because the casual rewrite made the wording less predictable. The style signal leans AI (**0.56**) because the sentence lengths are still fairly even. My rule gives the more-human score 65% of the vote, which lands at **0.42**, so the label is **unsure**. It doesn't call it human, which would let it through, and it doesn't call it AI, which would be an accusation built on a weak signal.

The split where my rule matters most is one signal sure and the other on the fence, for example model **0.90** and style **0.50**. A plain 50/50 average gives 0.70, which is a confident AI label on the strength of one signal. My rule gives 0.65 × 0.50 + 0.35 × 0.90 = **0.64**, which stays unsure.

**What it costs:** AI text that fools just one signal, such as a light rewrite or some added punctuation, falls to "unsure" instead of being caught. It also **doesn't protect the plain human writer**. Both signals misread that writer the same way (common words, even sentences, few commas), so the two signals agree on "AI" and there's no more-human signal for the rule to lean on. Only the width of the unsure band can help that writer.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



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
  -d @samples/clearly_ai.json
```

```json
{
  "confidence": 0.5,
  "content_id": "c_be5c7f2ded1e",
  "creator_id": "demo_instructor",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.7544,
  "style_score": null
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": null,
      "content_id": "c_bdd9324b153c",
      "creator_id": "demo_instructor",
      "guess": null,
      "label": null,
      "model_score": 0.7544,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-10-29T00:57:56+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_021e41e8f9f7",
      "creator_id": "demo_instructor",
      "guess": null,
      "label": null,
      "model_score": 0.7544,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-10-29T20:32:50+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_be5c7f2ded1e",
      "creator_id": "demo_instructor",
      "guess": "unsure",
      "label": null,
      "model_score": 0.7544,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-11-09T09:55:38+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

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

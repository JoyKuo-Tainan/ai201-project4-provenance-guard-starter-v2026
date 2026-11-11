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

**My limits:** 5 per minute, 50 per day

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
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Full run: [results/attack_run_2026-11-10_1635.md](results/attack_run_2026-11-10_1635.md) (56 attacks, every row marked).

| Family | Attacks | HELD | BROKE |
|---|---|---|---|
| evasion | 10 | 4 | 6 (EV01, 02, 05, 06, 07, 08: AI text came back `unsure`) |
| false_positive | 8 | 2 | 6 (FP01–FP06: human text called `ai`, 0.68–0.86) |
| prompt_injection | 6 | 5 | 1 (PI02: a fake "system" header came back `human`) |
| malformed | 20 | 12 | 8 (MF02, RQ07 crashed with 500; MF03–MF07 scored garbage; RQ06 logged an object as `creator_id`) |
| flood_same_creator | 12 | 12 | 0 (5 × 200, then 429) |
| **Total** | **56** | **35** | **21** |

Caveat: RQ10 and RQ11 came back 429 from the shared `unknown` bucket, so they never reached `/submit`. Form-encoded and wrong-content-type bodies are still untested.


**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

In order: FP03, FP02, FP04 (real writers accused); MF07 (Arabic called AI); MF06 (emoji called AI); MF03 (control characters called human); PI02 (injection got `human`); EV05, EV06 (evasion got through as `unsure`); RQ06 (object stored as creator_id); and one 429 rejection from the flood rows.

```json
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_24088e77726e", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.9758, "combined_score": 0.8648, "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_dc6d29aec193", "creator_id": "attacker_FP02", "guess": "ai", "model_score": 0.7387, "style_score": 0.9474, "combined_score": 0.8117, "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_eeb42183b4a8", "creator_id": "attacker_FP04", "guess": "ai", "model_score": 0.8329, "style_score": 0.884, "combined_score": 0.8508, "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:20+00:00", "content_id": "c_53b4acf051fb", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 1.0, "combined_score": 0.9392, "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_12ae5d3acb15", "creator_id": "attacker_MF06", "guess": "ai", "model_score": 0.9969, "style_score": 1.0, "combined_score": 0.998, "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_75ff6e901e65", "creator_id": "attacker_MF03", "guess": "human", "model_score": 0.0, "style_score": 1.0, "combined_score": 0.35, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_78993da8d5fd", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.6095, "combined_score": 0.3462, "label": "We think this was probably written by a person.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:18+00:00", "content_id": "c_0cbc1a135228", "creator_id": "attacker_EV05", "guess": "unsure", "model_score": 0.3212, "style_score": 0.4832, "combined_score": 0.3779, "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:19+00:00", "content_id": "c_0ba1deae9643", "creator_id": "attacker_EV06", "guess": "unsure", "model_score": 0.5727, "style_score": 0.2696, "combined_score": 0.3757, "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:20+00:00", "content_id": "c_2def8889a4e6", "creator_id": {"id": "x"}, "guess": "unsure", "model_score": 0.0492, "style_score": 1.0, "combined_score": 0.382, "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.", "status": "decided"}
{"timestamp": "2026-11-11T00:35:20+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP03 (`c_24088e77726e`): a non-native English speaker describing their first month in a new country was called AI at 0.865.** Both signals agreed strongly (model 0.805, style 0.976). Short, simple, grammatically careful sentences with few commas are exactly what my style signal reads as machine-like, and common vocabulary gives low perplexity. So the people most likely to write this way, language learners, are the ones my service accuses most confidently. The label says "this can be wrong", but 0.865 is high enough that a reviewer would likely trust it, and this writer is the one least able to argue back in English. MF07 (Arabic text called AI at 0.939) is the same problem at its extreme: my signals were built for English, and they don't abstain on anything else.


---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. False positives | Of 10 human pieces (≥3 plain), at most 1 labelled AI, every trial | My writing: 0 of 5 AI. Attack set FP01–FP08: **6 of 8 AI** | My writing: 0 of 5 AI | My writing: 0 of 5 AI | **MISSED** |
| 2. Score spread | 5 clearly-AI vs 5 clearly-human: no overlap, averages ≥0.35 apart | not run | not run | not run | **NOT RUN.** No scenario yet. With 1 text each: AI 0.738, human 0.222 |
| 3. Label coverage | All three labels reached by real text each trial; ≥3 of 5 lightly-edited AI on unsure/AI | ai 0.738 / human 0.222 / unsure 0.423 | same | same | **MET.** Part 2 also holds in the attack run: 10 of 10 evasion texts landed on unsure or AI |
| 4. Appeal path | 10/10 valid appeals recorded; 5/5 bad IDs get 4xx | not run | not run | not run | **NOT RUN** |
| 5. Bad input | 0 of 7 bad inputs give a 500; each gets 4xx + JSON error | Attack run: one-character text → **500**; 60,000 chars → **200**, not 4xx | — | — | **MISSED** |

Criteria 1 and 3 come from `results/run_2026-11-10_2340_before.md` (3 trials). The attack-set evidence for criteria 1, 3 and 5 comes from `results/attack_run_2026-11-10_1635.md` (1 run). One trial with a miss is enough to miss, because the target has to hold in every trial.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

`run_eval.py::main` → `app.py::submit`, scenario "label coverage", trial 1 (`results/run_2026-11-10_2340_before.md`):

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.738,
    "model_score": 0.7544,
    "style_score": 0.7291,
    "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2219,
    "model_score": 0.4445,
    "style_score": 0.1021,
    "label": "We think this was probably written by a person.",
    "sent": "I didn't sleep. Not properly, anyway \u2014 I lay there listening to the bo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4228,
    "model_score": 0.3489,
    "style_score": 0.56,
    "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
    "sent": "Time management matters more than people admit, especially now that wo"
  }
]
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

Two criteria missed and 21 attacks broke. They come down to **four problems**, not 23.

**Pattern A: plain writing fools both signals the same way, so my combining rule has nothing to protect with.** (Criterion 1 miss; FP01–FP06, 6 attacks)

Six real human texts were labelled AI, at 0.68–0.86. All six are plain, even, careful prose: a non-native speaker (FP03), a rubric essay (FP04), technical docs (FP05), a formal template (FP06). Signal one scores common words as predictable, so it reads them as AI. FP03 got a model score of 0.805. Signal two measures sentence-length spread and the rate of commas, semicolons and parentheses. Short, same-length sentences with few commas score near zero on both, so it read FP03 as 0.976, close to maximum AI. My combining rule (`scoring.py::combine_signals`) gives 0.65 of the vote to whichever signal reads more human. That only helps when the signals disagree. Here they agree: 0.65 × 0.805 + 0.35 × 0.976 = 0.865. **Stage: signal one and signal two together, with the combining rule as the safeguard that doesn't fire. Mechanism: both signals treat "plain" as "machine-like". They aren't independent witnesses on plain writing; they share one blind spot.** My own five pieces passed (0 of 5 AI) because they're informal, with typos and uneven sentences, which is exactly the writing that doesn't trigger this.

**Pattern B: signal two scores "nothing to measure" as maximum AI.** (MF03, MF04, MF05, MF06, MF07; 5 attacks)

In `stylometry.py::style_signal`, a text with fewer than two sentences has a spread of 0.0, and a text with no commas has a punctuation score of 0.0. Both mean "least human", so the style score is 1.0. Every one of these inputs got exactly 1.0: control characters, punctuation only, one long word, emoji, Arabic. Signal two isn't measuring them; it's defaulting to "AI". What happens next depends on signal one:
- **MF05, MF06, MF07:** signal one scored 0.91–0.998, because GPT-2 finds repeated characters and the UTF-8 byte pieces of Arabic script very predictable. Both signals were near 1.0, so they were called AI at 0.94–0.998. MF07 is the worst result in the run: an Arabic writer gets a near-certain AI label.
- **MF03:** signal one scored 0.0, because control characters are unpredictable. The rule gave 0.65 × 0.0 + 0.35 × 1.0 = **0.35**, which is exactly the human threshold. The label mapping counts `<= 0.35` as human, so it said "probably written by a person".
- **MF04:** landed on unsure at 0.357, but should never have been scored.

**Stage: signal two (and the route, for letting non-text through). Mechanism: absence of evidence is scored as evidence of AI.**

**Pattern C: knock down either signal and the combining rule hands that signal 65% of the vote.** (EV01, EV02, EV05, EV06, EV07, EV08, PI02; 7 attacks)

This is the cost I chose when I wrote the rule, and the attacks show how cheap it is to cash in:
- **EV01 (typos):** typos raised perplexity, so signal **one** fell to 0.16 while style stayed at 0.86. The result was 0.41, unsure. The typos fooled signal one, not signal two.
- **EV06 (one very long sentence and one very short):** spread jumped, so style fell to 0.27. Combined 0.376, unsure.
- **EV08 (text below the token window):** too few tokens for a stable perplexity, so the model score was 0.245. Style was 1.0 (Pattern B). Combined 0.51, unsure.
- **PI02:** the instructions in the fake "SYSTEM" header weren't obeyed; the scorer can't read them. But that header is odd, unpredictable token soup, so signal one fell to 0.204. Combined 0.346, which is 0.004 under the human threshold, so it got the human label.
- **EV02, EV07:** both signals came out moderate (0.53–0.60), which keeps the combined score inside the unsure band.
- **EV05 (heavy human editing):** both signals fell. It's arguable that unsure is the right answer here.

**Stage: the combining rule. Mechanism: weighting the lower signal at 0.65 means fooling either signal is enough, so the attacker only needs the cheapest trick.**

**Pattern D: the route checks one thing, so anything else gets through.** (Criterion 5 miss; MF02, RQ06, RQ07; 3 attacks)

`app.py::submit` checks only that `text` is a non-empty string. Four separate holes:
- **MF02:** `"a"` passes, then `detector.perplexity` raises `ValueError` on fewer than 3 tokens. The route doesn't catch it, so it returns a 500 and shows the Werkzeug debugger page.
- **RQ07:** a JSON array body skips the `or {}` fallback (a non-empty list isn't falsy), so `.get` on a list raises `AttributeError`, giving a 500.
- **RQ06:** `creator_id` is never type-checked, so `{"id": "x"}` is written into the audit log as an object.
- **MF08:** there's no length cap, so 60,000 characters returned 200 where criterion 5 requires a 4xx above 20,000. The detector also only reads the first 400 tokens, so the rest of a long text is never checked by signal one.

**Stage: the route. Mechanism: input validation stops at "is it a non-empty string".**

**What the patterns say about where to fix.**
- **Patterns D and B are one fix away.** If the route rejected bad bodies, non-string `creator_id`, text over 20,000 characters, and text without enough real words for both signals to measure, most of Pattern B would never reach signal two.
- **Pattern C is the trade-off I chose.** Moving it means accepting more false positives, which Pattern A says I can't afford.
- **Pattern A is the real problem.** It's the miss that hurts actual writers, and no reweighting fixes two signals that share one blind spot.

**Targets I'd tighten.**
- **Criterion 3 is too easy.** It counts unsure as a catch, so all six evasions that reached unsure still pass it, even though the attack run counts them as BROKE.
- **Criterion 1 needs a fixed test set.** It was only missed because the attack set supplied plain human writing. My own scenario (5 informal pieces) would have passed it. Criterion 1 should run on the 10 pieces it names, with the plain ones actually included.


---

## The Improvement

**What I changed:** input validation in `app.py::submit`, before either signal runs. Limits are in `config.py`. One change, five checks:
- the body must be a JSON object (a list or string gets a 400)
- `creator_id` must be a non-empty string
- `text` must be at most `MAX_TEXT_CHARS = 20,000` characters (criterion 5's own limit)
- `text` must have at least `MIN_WORDS = 20` English words across `MIN_SENTENCES = 2` sentences
- the detector's "too short" `ValueError` is caught and turned into a 400

A refused text gets this message: *"We can't check this — it needs at least 20 words of English across 2 or more sentences. This is not a finding about your writing; our checks only work on English prose."*

I did **not** change the weights, the thresholds or either signal.

**Which diagnosis pointed at it:** Patterns D and B.
- **Pattern D:** the route only checked "non-empty string", so MF02, RQ06 and RQ07 got through and MF08 got a 200.
- **Pattern B:** the style signal scores anything with fewer than two sentences or no commas as 1.0 (maximum AI). So text it can't measure was being *accused* instead of refused. The cleanest fix is to stop that text from reaching the signal.

I chose this over reweighting or moving thresholds because Pattern A (plain human writing called AI) has both signals agreeing. No weighting between two signals that agree can fix it. Raising `AI_THRESHOLD` to about 0.87 would clear FP01–FP06, but only by tuning to these six texts. It would also let EV03, EV04 and EV09 (0.69–0.70) drop to unsure.

### Attack Run — After

`run_attacks.py --set attack_set --label after` → `results/attack_run_2026-11-10_2359_after.md` (same 56 attacks, same format).

| Family | Before: HELD / BROKE | After: HELD / BROKE | What moved |
|---|---|---|---|
| evasion | 4 / 6 | **6 / 4** | EV07 (one 97-word "sentence") and EV08 (10 words) now get 400 instead of unsure |
| false_positive | 2 / 6 | 2 / 6 | FP01–FP06 unchanged, same scores to 3 decimals. FP08 now gets **400** instead of unsure |
| prompt_injection | 5 / 1 | 5 / 1 | PI02 still labelled human at 0.346 |
| malformed | 12 / 8 | **20 / 0** | MF02 and RQ07 went from 500 to 400. MF03–MF07 went from scored to 400. RQ06 now 400. MF08 went from 200 to 400 |
| flood_same_creator | 12 / 0 | 12 / 0 | Rows 1–5 now get 400 (the 9-word flood text is under 20 words); 429 still starts at row 6 |
| **Total** | **35 / 21** | **45 / 11** | |

| ID | Before | After |
|---|---|---|
| MF02 single character | **500** (Werkzeug debugger page) | 400 |
| RQ07 JSON array body | **500** `AttributeError` | 400 |
| MF07 Arabic text | 200, **ai 0.939** | 400 "our checks only work on English prose" |
| MF06 emoji only | 200, **ai 0.998** | 400 |
| MF03 control characters | 200, **human 0.350** | 400 |
| RQ06 creator_id is an object | 200, object written to audit log | 400 |
| MF08 60,000 characters | 200, ai 0.874 | 400 "limit is 20,000 characters" |
| EV07 punctuation padding | 200, unsure 0.591 | 400 |
| EV08 below the token window | 200, unsure 0.509 | 400 |
| FP08 short genuine human piece | 200, unsure 0.520 | **400** (new cost) |
| FP03 non-native speaker | 200, ai 0.865 | 200, ai 0.865 (unchanged) |
| PI02 fake system header | 200, human 0.346 | 200, human 0.346 (unchanged) |

### Run Log — After

`run_eval.py --label after` → `results/run_2026-11-10_2359_after.md`, 3 trials.

| Criterion | Before | After | Verdict before → after |
|---|---|---|---|
| 1. False positives | My writing 0 of 5 AI; attack set FP 6 of 8 AI | My writing 0 of 8 AI (3 new pieces, all unsure: 0.48, 0.41, 0.43); attack set FP still 6 of 8 AI | MISSED → **MISSED** |
| 2. Score spread | not run | not run | NOT RUN → NOT RUN |
| 3. Label coverage | ai 0.738 / human 0.222 / unsure 0.423, all 3 trials | identical | MET → **MET** |
| 4. Appeal path | not run | not run | NOT RUN → NOT RUN |
| 5. Bad input | one character → 500; 60,000 chars → 200 | one character → 400; 60,000 chars → 400; missing / whitespace / non-string text / empty body → 400 | MISSED → **MET in the attack run** (one run, not three) |

The five pieces of my own writing that were in both runs scored identically to four decimals, as did the label-coverage texts. That's expected: validation runs *before* the signals and doesn't change how anything is scored.

**Did it help, and how do I know:**

**Yes for crashes and garbage input. No for false positives, which is the problem that matters most.**

- **What it fixed.** Broken attacks went from 21 to 11. Every one of the 10 that moved was a malformed or unmeasurable input. There are no more 500s, so the Werkzeug debugger page is no longer reachable from `/submit`. Arabic, emoji and control characters are refused with an honest message instead of being called AI or human with near-certainty. Criterion 5 went from MISSED to met (in the single attack run).
- **What it didn't touch.** FP01–FP06 are scored exactly as before (0.677–0.865, all AI), so criterion 1 is still MISSED. Pattern A lives in the signals, and this change is upstream of them. PI02 and the four `unsure` evasions are also unchanged (Pattern C).
- **What it cost.**
  - **FP08, a short genuine human piece (8 words, 3 sentences), is now refused** because it's under `MIN_WORDS = 20`. Before, it got "unsure" and could ask for review. Now it gets a 400 and can't be checked at all. Any short real submission (a caption, a two-line reply) now gets no label instead of an uncertain one. I'd argue that's the honest answer, since neither signal can read 8 words, but the writer still gets nothing.
  - **Non-English writers are refused rather than accused.** That's better than a 0.94 AI label, but it's still "this service doesn't work for you".
  - **EV07 and EV08 "held" only because they're refused.** An attacker who adds one full stop or a few more words gets back into the scoring path, where Pattern C still applies.


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

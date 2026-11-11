# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. **False positives.**

<!-- Your criterion. It must name a number. -->

Of 10 pieces of human writing (at least 3 of them plainly written: short sentences, common words, few commas), **at most 1** is labelled high-confidence AI, in **each** of the three trials.

**Why this target:** A wrong accusation costs the writer far more than a missed detection costs the site, so this is the criterion I care about most. I include plainly written pieces on purpose. Both of my signals misread plain writing the same way, so a test set of only lively, comma-heavy human writing would make this target too easy to pass.


---

## 2. **Score spread.**

<!-- Your criterion. -->

 Across 5 clearly-AI and 5 clearly-human texts, the **lowest** clearly-AI combined score is above the **highest** clearly-human combined score (no overlap), and the two group averages are **at least 0.35 apart**, in each of the three trials.

**Why this target:** 0.35 is the width of my unsure band (0.35 to 0.65). If the clear cases aren't separated by at least that much, they can't land on opposite sides of it, and the labels would be deciding by luck. "No overlap" stops one good average from hiding a clearly-human text that scores like AI.


---

## 3. **Label coverage.**

<!-- Your criterion. -->

 All three labels (high-confidence human, unsure and high-confidence AI) are produced by **real submitted text** in each of the three trials. At least 1 submission lands on each label, and of 5 lightly-edited AI texts, **at least 3** land on unsure or AI rather than human.

**Why this target:** A label that no real text can reach is a gap in the ranges, and the combined score can only land between the two signals, so this has to be shown with real text, not assumed. The lightly-edited cases check that "unsure" actually does its job of catching the in-between cases, rather than only being reachable in theory.


---

## 4. **The appeal path.** 

<!-- Your criterion. -->

**10 of 10** appeals with a valid `content_id` return a confirmation, move the item to `under_review`, and add an appeal entry to the audit log. **5 of 5** appeals with an unknown or missing `content_id` return a 4xx error and change nothing.

**Why this target:** The appeal is the only thing standing between a wrong accusation and nothing at all, so anything below 100% means some writer was silently ignored. This part has no model in it, so it should behave the same every time and there's no reason to allow misses. The unknown-ID half matters because a typo that "succeeds" without being recorded looks like a working appeal that nobody will ever read.


---

## 5. **Bad input.** 

<!-- Your criterion. -->

Of these 7 inputs, **0** return a 500 or crash the service: no JSON body, `text` missing, `text` empty, `text` only whitespace, `text` not a string, `text` of one or two words, and `text` over 20,000 characters. Each gets a 4xx with a JSON `error` message within 10 seconds, in each of the three trials.

**Why this target:** A crash on malformed input is one of the most common real failures, and unit 8's attack set will send all of these. The one-or-two-word case is real for my service, because the detector raises an error on text under 3 tokens and my style signal can't measure spread in under two sentences. 20,000 characters is about 3,000 words, longer than any essay a writer would reasonably check, and it keeps one request from tying up the model.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

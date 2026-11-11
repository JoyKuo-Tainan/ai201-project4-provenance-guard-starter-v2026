# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-10 23:59
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_93a06490e751` | unsure | 0.407 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_e4664d733556` | unsure | 0.552 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_a44f658b720e` | ai | 0.700 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_b8058c65a898` | ai | 0.699 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_cc7159262ba4` | unsure | 0.378 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_b2a21da1a2c7` | unsure | 0.376 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 400 | `—` | — | — | HELD |
| EV08 | evasion | signal one: text below the token window | 400 | `—` | — | — | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_72fbf991a3c7` | ai | 0.686 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_7c4a8ac8f8ab` | ai | 0.940 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_872877cb29d5` | ai | 0.677 | BROKE |
| FP02 | false_positive | human writing in a formal register | 200 | `c_1fc85a3a971a` | ai | 0.812 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_fae91e4618b1` | ai | 0.865 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_1c27f57d4c5d` | ai | 0.851 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_244fa638362e` | ai | 0.830 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_a2d194de0508` | ai | 0.796 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_07a438922432` | unsure | 0.630 | HELD |
| FP08 | false_positive | very short genuine human submission | 400 | `—` | — | — | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_8fef5004caf3` | unsure | 0.542 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_2631d3b7f20e` | human | 0.346 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_30830d7688a0` | ai | 0.698 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_da6e304577ce` | unsure | 0.564 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_440a77725dd9` | unsure | 0.519 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_c819d54aa04f` | unsure | 0.644 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | `—` | — | — | HELD |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — | HELD |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 400 | `—` | — | — | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## My verdicts

| Family | HELD | BROKE |
|---|---|---|
| `evasion` | 6 | 4 |
| `false_positive` | 2 | 6 |
| `prompt_injection` | 5 | 1 |
| `malformed` | 20 | 0 |
| `flood_same_creator` | 12 | 0 |
| **Total** | **45** | **11** |

I judged with the same rules as the before run. A 400 counts as HELD: the input is refused with a message, not labelled. FP08 (a short genuine human piece) is HELD by that rule, but see the README: refusing a real writer is a new cost. RQ10/RQ11 still got 429 and never reached the route.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_93a06490e751",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.4069,
  "model_score": 0.1635,
  "style_score": 0.8588,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_e4664d733556",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.552,
  "model_score": 0.5943,
  "style_score": 0.5293,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_a44f658b720e",
  "creator_id": "attacker_EV03",
  "guess": "ai",
  "confidence": 0.7004,
  "model_score": 0.6662,
  "style_score": 0.7639,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_b8058c65a898",
  "creator_id": "attacker_EV04",
  "guess": "ai",
  "confidence": 0.6986,
  "model_score": 0.6114,
  "style_score": 0.8605,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_cc7159262ba4",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.3779,
  "model_score": 0.3212,
  "style_score": 0.4832,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_b2a21da1a2c7",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.3757,
  "model_score": 0.5727,
  "style_score": 0.2696,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_EV07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_EV08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_72fbf991a3c7",
  "creator_id": "attacker_EV09",
  "guess": "ai",
  "confidence": 0.686,
  "model_score": 0.7042,
  "style_score": 0.6762,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_7c4a8ac8f8ab",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9404,
  "model_score": 0.9792,
  "style_score": 0.9195,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_872877cb29d5",
  "creator_id": "attacker_FP01",
  "guess": "ai",
  "confidence": 0.6769,
  "model_score": 0.6175,
  "style_score": 0.7873,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_1fc85a3a971a",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.8117,
  "model_score": 0.7387,
  "style_score": 0.9474,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_fae91e4618b1",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.8648,
  "model_score": 0.8051,
  "style_score": 0.9758,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_1c27f57d4c5d",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.8508,
  "model_score": 0.8329,
  "style_score": 0.884,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_244fa638362e",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.8303,
  "model_score": 0.8005,
  "style_score": 0.8857,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_a2d194de0508",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7957,
  "model_score": 0.8814,
  "style_score": 0.7496,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_07a438922432",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.6304,
  "model_score": 0.8816,
  "style_score": 0.4951,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_FP08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_8fef5004caf3",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.5418,
  "model_score": 0.4625,
  "style_score": 0.6892,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_2631d3b7f20e",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.3462,
  "model_score": 0.2044,
  "style_score": 0.6095,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_30830d7688a0",
  "creator_id": "attacker_PI03",
  "guess": "ai",
  "confidence": 0.6979,
  "model_score": 0.5943,
  "style_score": 0.8904,
  "label": "This reads a lot like text produced by an AI writing tool. This is an automated estimate, not proof, and it can be wrong, especially with plain or very even writing. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_da6e304577ce",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.5635,
  "model_score": 0.4998,
  "style_score": 0.6818,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_440a77725dd9",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.5186,
  "model_score": 0.6401,
  "style_score": 0.4531,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_c819d54aa04f",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.6445,
  "model_score": 0.5583,
  "style_score": 0.8045,
  "label": "We can't tell whether this was written by a person or with help from AI. Our checks gave mixed results, which happens with a lot of genuine writing too, so this is not a finding against you. If you wrote it yourself, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

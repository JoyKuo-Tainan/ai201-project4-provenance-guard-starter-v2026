#!/usr/bin/env python3
"""
Provenance Guard — the web service.

    python app.py

Then, in another terminal:

    curl -X POST http://127.0.0.1:5000/ping \
    -H "Content-Type: application/json" \
    -d '{"message": "hello"}'

That's the example route. It works right now, before you've written anything.
**Leave it alone** — it's your control. When something breaks later, check that
`/ping` still answers: if it does, the problem is in your handler; if it
doesn't, it's the service itself.

Routes:

    POST /ping        the worked example. Already works. Don't edit it
    POST /submit      ← YOU BUILD THIS (Milestone 3, 4, 5)
    POST /appeal      ← YOU BUILD THIS (Milestone 5)
    GET  /log         the audit log. Already works
    GET  /health      is the service up, and is the model loaded
"""

import uuid

from flask import Flask, jsonify, request

import audit
import config

app = Flask(__name__)


# ── Rate limiting — UNIT 8 ────────────────────────────────────────────────────
# Off until you turn it on. In unit 8, Milestone 1:
#
#   1. Set RATE_LIMITING_ENABLED = True in config.py (or AI201_RATE_LIMITS=1)
#   2. Choose your numbers there
#   3. Uncomment the @limiter.limit(...) line on /submit below
#
# The order doesn't matter. While limiting is off, that decorator is a no-op
# that quietly does nothing, so uncommenting it early costs you nothing — but
# it also means no 429 until you've done step 1.
#
# The storage backend is preconfigured, which stops Flask-Limiter printing a
# warning on every start. In-memory is right for one laptop and wrong for
# anything real — a restart forgets every count.

class _LimiterOff:
    """
    Stands in for the real limiter while rate limiting is off.

    It makes @limiter.limit(...) a decorator that returns the route
    untouched, so uncommenting the line before you flip the setting is
    harmless instead of a crash on startup.
    """

    def limit(self, *args, **kwargs):
        return lambda view: view


limiter = _LimiterOff()
if config.RATE_LIMITING_ENABLED:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    def rate_limit_key():
        """
        Who a request counts against.

        Falling back to the caller's address is the easy version. Unit 8's
        stretch asks about per-creator limits instead — and the difference
        matters: one script can look like a thousand callers, and one household
        can look like one.
        """
        payload = request.get_json(silent=True)
        # A body that parses as JSON but isn't an object — a bare list or
        # string — has no .get. Without this guard the key function raises
        # BEFORE the route runs, and a malformed request becomes a 500 that
        # looks like your handler crashed when your handler never ran.
        if not isinstance(payload, dict):
            return get_remote_address()
        creator = payload.get("creator_id")
        return creator if isinstance(creator, str) and creator.strip() else get_remote_address()

    limiter = Limiter(
        key_func=rate_limit_key,
        app=app,
        storage_uri=config.RATE_LIMIT_STORAGE,
        default_limits=[],
    )

    @app.errorhandler(429)
    def rate_limited(exc):
        """
        A rejected request still leaves a trace.

        ⚠️ An attack that shows up only as an absence is one you'll never find.
        """
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        audit.log_rejection(
            creator_id=payload.get("creator_id", "unknown"),
            reason="rate_limited",
            limit=str(exc.description),
        )
        return jsonify({
            "error": "rate_limited",
            "message": "Too many submissions. Try again shortly.",
            "limit": str(exc.description),
        }), 429


# ── The worked example. Already works. Don't edit. ────────────────────────────

@app.post("/ping")
def ping():
    """
    Everything a route needs, in six lines.

    JSON arrives as a dict. You pull things out of it. You return a dict and
    the framework turns it into a response. That's the whole idea.
    """
    payload = request.get_json(silent=True) or {}
    return jsonify({
        "ok": True,
        "you_sent": payload.get("message"),
        "service": "provenance-guard",
    })


@app.get("/health")
def health():
    """Is the service up, and has the model been downloaded yet?"""
    import detector

    loaded = detector._model is not None
    return jsonify({
        "ok": True,
        "detector_model": config.DETECTOR_MODEL,
        "detector_loaded": loaded,
        "rate_limiting": config.RATE_LIMITING_ENABLED,
        "log_entries": len(audit.read_entries()),
    })


# ── YOU BUILD THIS ────────────────────────────────────────────────────────────

@app.post("/submit")
@limiter.limit(f"{config.RATE_LIMIT_PER_MINUTE}/minute;{config.RATE_LIMIT_PER_DAY}/day")
def submit():
    """
    Take a piece of text, decide about it, log the decision, answer.
    ← TODO — Milestones 3, 4 and 5

    Expects JSON:
        {"text": "...", "creator_id": "..."}

    Should return JSON with, at minimum:
        {"content_id": "...", "guess": "...", "confidence": 0.0, "label": "...",
        "model_score": 0.0, "style_score": 0.0}

    ⚠️ **Both signal scores go in the response, not just the log.** Unit 8's
    `run_attacks.py` and `run_eval.py` read `model_score` and `style_score`
    straight off this response and put them in your reports. Leave them out and
    every row of next unit's evidence says `null` — which is exactly the
    diagnostic you need to name a stage and a mechanism. You do not want to
    find that out after running the attack set.

    ─────────────────────────────────────────────────────────────────────────
    Build it in three passes. Do not skip ahead — the ordering is how you tell
    a broken route from a broken signal.

    **Milestone 3 — the route answers.**
    1. Return a hardcoded response. Confirm `curl` gets it back before you
        add any logic at all.
    2. Then pull `text` and `creator_id` out of the payload.
    3. Then call ONE signal — `detector.model_signal(text)` — and put the
        real number in. Leave confidence and label as placeholders.
    4. Log every submission with `audit.log_decision(...)`. The content_id
        matters: `/appeal` needs it, and a student who skips it rebuilds this
        whole flow later.

    **Milestone 4 — the second signal and the score.**
        5. Add `stylometry.style_signal(text)`.
        6. Combine them with `scoring.combine_signals(...)`.
        7. Log BOTH signal scores alongside the combined one, and put them in the
            response too. Next unit you can't diagnose anything without them.

    **Milestone 5 — the label.**
        8. `scoring.score_to_label(...)` and put the real label in the response.

    ─────────────────────────────────────────────────────────────────────────
    Worth deciding early, because unit 8's attack set will decide it for you:
    what should this do when `text` is missing, empty, or enormous? A crash on
    a malformed input is one of the most common real failures there is.
    """
    # curl -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d @samples/clearly_ai.json

    # Step 2 - check the input BEFORE either signal sees it. (Unit 8 improvement.)
    # Diagnosis Pattern D: the route only checked "non-empty string", so a list
    # body, a 1-character text and a non-string creator_id got through.
    # Diagnosis Pattern B: text the style signal can't measure (fewer than two
    # sentences, no English words) was scored as maximum AI instead of refused.
    import stylometry

    def bad_request(message):
        return jsonify({"error": "bad_request", "message": message}), 400

    payload = request.get_json(silent=True)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return bad_request("Send a JSON object like {\"text\": \"...\", \"creator_id\": \"...\"}.")

    text = payload.get("text")
    creator_id = payload.get("creator_id", "unknown")

    if not isinstance(creator_id, str) or not creator_id.strip():
        return bad_request("\"creator_id\" must be a non-empty string.")
    if not isinstance(text, str) or not text.strip():
        return bad_request("Send JSON with a non-empty \"text\".")
    if len(text) > config.MAX_TEXT_CHARS:
        return bad_request(
            f"Text is too long to check — the limit is {config.MAX_TEXT_CHARS:,} characters."
        )
    if (len(stylometry.words(text)) < config.MIN_WORDS
            or len(stylometry.sentences(text)) < config.MIN_SENTENCES):
        return bad_request(
            f"We can't check this — it needs at least {config.MIN_WORDS} words of "
            f"English across {config.MIN_SENTENCES} or more sentences. This is not "
            f"a finding about your writing; our checks only work on English prose."
        )

    # Step 3 - one real signal that we first tested from the terminal
    # python detector.py "some text"
    import detector
    try:
        model_score = detector.model_signal(text)
    except ValueError as exc:  # the detector refuses text under 3 tokens
        return bad_request(str(exc))

    # Step 5 - the second signal, and Step 6 - combine them into one score.
    import scoring
    style_score = round(stylometry.style_signal(text), 4)
    combined_score = round(scoring.combine_signals(model_score, style_score), 4)

    # Step 4/7 - log the decision with BOTH signal scores and the combined one.
    # The content_id is what /appeal needs later.
    content_id = f"c_{uuid.uuid4().hex[:12]}"

    # Step 8 - turn the combined score into the sentence a writer reads.
    guess, label = scoring.score_to_label(combined_score)
    audit.log_decision(
        content_id=content_id,
        creator_id=creator_id,
        guess=guess,
        model_score=model_score,
        style_score=style_score,
        combined_score=combined_score,
        label=label,
        status="decided",
    )

    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "guess": guess,
        "confidence": combined_score,
        "label": label,
        "model_score": model_score,
        "style_score": style_score,
        }), 200




@app.post("/appeal")
def appeal():
    """
    A writer says you got it wrong. ← TODO — Milestone 5

    Expects JSON:
        {"content_id": "...", "reasoning": "..."}

    Should:
    1. Check the content_id actually exists — `audit.entries_for(id)` tells
        you. A typo here fails silently and looks like a broken endpoint,
        which is the single most common way this milestone eats an hour.
    2. Record the appeal with `audit.log_appeal(...)`, which moves the item
        to `under_review`.
    3. Confirm to the writer. No automatic re-checking needed.

    This is the smallest endpoint in the project and the one that matters most
    to the person on the other end. It's the only thing standing between a
    wrong accusation and nothing at all.
    """
    # curl -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" -d '{"content_id": "c_...", "reasoning": "I wrote this myself."}'

    payload = request.get_json(silent=True) or {}
    content_id = payload.get("content_id")
    reasoning = payload.get("reasoning")

    if not isinstance(content_id, str) or not content_id.strip():
        return jsonify({"error": "bad_request", "message": "Send JSON with the \"content_id\" from your submission."}), 400
    if not isinstance(reasoning, str) or not reasoning.strip():
        return jsonify({"error": "bad_request", "message": "Tell us why you think the label is wrong in \"reasoning\"."}), 400

    # Step 1 - the content_id has to exist, or the appeal would vanish silently.
    entries = audit.entries_for(content_id)
    if not entries:
        return jsonify({"error": "not_found", "message": f"No submission found with content_id {content_id!r}."}), 404

    # Step 2 - record the appeal next to the original decision; status -> under_review.
    creator_id = entries[0].get("creator_id", "unknown")
    audit.log_appeal(content_id=content_id, creator_id=creator_id, reasoning=reasoning)

    # Step 3 - confirm to the writer.
    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Thanks. Your appeal has been recorded and a person will review this decision.",
    }), 200


# ── Already works ─────────────────────────────────────────────────────────────

@app.get("/log")
def get_log():
    """
    The audit log, most recent last.

        curl "http://127.0.0.1:5000/log?limit=10"

    You need this in unit 8 to paste entries into your README, and you need it
    now to see whether your logging is actually working.
    """
    limit = request.args.get("limit", type=int)
    entries = audit.read_entries(limit=limit)
    return jsonify({"count": len(entries), "entries": entries})


def main():
    print(f"Provenance Guard on http://{config.HOST}:{config.PORT}")
    print(f"  detector model:  {config.DETECTOR_MODEL}")
    print(f"  rate limiting:   {'ON' if config.RATE_LIMITING_ENABLED else 'off (unit 8)'}")
    print(f"  audit log:       {config.AUDIT_LOG}")
    print()
    print("Check it's alive:")
    print(f'  curl -X POST http://{config.HOST}:{config.PORT}/ping \\')
    print('    -H "Content-Type: application/json" \\')
    print("    -d '{\"message\": \"hello\"}'")
    print()
    # debug=True hands out an interactive debugger, so it's local-only — see config.py
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()

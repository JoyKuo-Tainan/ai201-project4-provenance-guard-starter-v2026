"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
            with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
            when the malformed request IS the point — empty text, no `text`
            field at all, something enormous. A bad-input criterion needs it,
            because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # ⚠️ PUT YOUR OWN WRITING HERE. Not AI text, not a sample from the web —
        # things you actually wrote. This is the criterion that matters most and
        # it's meaningless with someone else's prose.
        "texts": [
            "I dunno what will the stock market be tommorw. Why the unfaithful behavior of Nvedia CEO related to the stock price and our investors need to be pulish by this? THis is even not our falt. Maybe I should buy some options in this time, even though options are risky, a truly risky move, but the stock market is so bad and VIX is the highest among the history. So it could be a good chance, right?",
            "Last night, while I was watching TikTok, it push me a live calculus class! Can you believe it!? At around 12 am, and it chose this context for me. Also, I wonder what's in that dude mind that holding a calculus class on Tiktok at the midnight is a good ideal? That should be impossible he would have many audience at that timing.",
            "Have you tried the Trader Joe's new product the sesame mochi ice cream? It's so good, and I really like it and it is healthy for the hairs since it contains black sesame inside. However, little few people like this product. I hope you like it anyway!",
            "That ginger cat was meowing all night last night. We should ring our neighbor's door bell to check if that cat is ok. Poor little thing. Maybe it is hungry, but it couldn't get enough food or feel sick.",
            "Hello everyone, my name is Alice. Today, I would like to talk about the economics history of Argentino. This country was adapting a very special currency policy, and this was popular to control the exchange market back to that time...",
            "When 1958, there was the famous Cold War between the Soviet Union and the United States. Since a sense of tension during this period, public could not easily trust foreigners and even immigrants anymore. Because of the stressful stmosphere, to relive the tension in the country become the priority of Kennedy's task.",
            "The feedback that surprise me is I suppose to write a conclusion but I accidently forget this part. SInce we are seperated in groups depend on what kind of topics we have wrote, I find out that my partner and I have same problem on finding resources and this thing really pleases me.",
            "Stone's friend posted a photo on the Facebook and tagged her name, but some group of people thought this photo offended them. Thus, it turned out to be countless bad comments appeared below the post. The media even visited her home and created awful impressioin about her family. Thus, Stoe lost her job and stayed in a fearful corner for a long time.",
            "The Irish immigrants were usually described as people who looked angry. In addition, they are protential trouble-makers. For instance, drining a lof of wine, rude and insisting in traditional religion different from most Americans are their personalities usually drew as caricatures. (summary for a paragraph from a article talk about discrimination)",

        ],
    },
    {
        "name": "label coverage",
        "criterion": 2,
        # Inputs spread across your score range, so you can check all three
        # labels are actually reachable.
        "texts": [
            # AI-generated — samples/clearly_ai.json (scored 0.74, ai)
            "The importance of effective time management cannot be overstated in "
            "today's fast-paced work environment. Professionals who develop strong "
            "organizational habits are better positioned to meet deadlines and "
            "reduce stress. There are several key strategies that can help "
            "individuals improve their productivity. First, prioritization is "
            "essential. By identifying the most important tasks and addressing them "
            "first, workers can ensure that critical objectives are met. Second, "
            "minimizing distractions plays a significant role. Setting aside "
            "dedicated blocks of time for concentrated work is widely considered "
            "beneficial. Finally, regular breaks are important for maintaining "
            "performance.",
            # Human-written — samples/clearly_human.json (scored 0.22, human)
            "I didn't sleep. Not properly, anyway — I lay there listening to the "
            "boiler tick and thinking about the thing I'd said to Marcus at the pub, "
            "which was stupid, and which he will absolutely bring up again. Twice "
            "now. So: coffee, and the long way round to work, and a plan. The plan "
            "lasted until about ten past nine, when Priya asked how the weekend was "
            "and I said \"fine\" in the voice that means it wasn't, and she put her "
            "mug down and looked at me. That's the trouble with Priya. She notices.",
            # Borderline (lightly edited AI) — samples/borderline.json (scored 0.42, unsure)
            "Time management matters more than people admit, especially now that "
            "work moves as fast as it does. If you're organised you hit deadlines, "
            "and you're less frazzled doing it. A few things actually help. "
            "Prioritise — work out what genuinely matters and do that first. Cut "
            "the interruptions; notifications wreck focus and the damage is worse "
            "than it feels at the time. And take breaks, short ones, often.",
        ],
    },
    # A bad-input criterion looks like this. Uncomment and adjust if that's one
    # of your five — these are raw request bodies, sent exactly as written.
    #
    # {
    #     "name": "bad input",
    #     "criterion": 3,
    #     "bodies": [
    #         {"text": "", "creator_id": "eval_bad_empty"},
    #         {"creator_id": "eval_bad_missing"},          # no text field at all
    #         {"text": "word " * 50000, "creator_id": "eval_bad_huge"},
    #         {"text": None, "creator_id": "eval_bad_null"},
    #     ],
    # },

    # TODO: add what your remaining criteria need.
    #
    # A criterion about the appeal path can't be tested by sending text alone;
    # it needs a submission first and then an appeal against the content_id
    # that came back. You'll need to test that one by hand, or extend this file
    # and run_eval.py to do it. Saying which you did is part of the write-up.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems

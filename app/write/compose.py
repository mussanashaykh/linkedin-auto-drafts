import re, random

# ===== Helpers =====
def _clean(s: str) -> str:
    s = (s or "").strip()
    return re.sub(r"\s+", " ", s)

def _split_phrases(text: str) -> list:
    """Roughly extract key phrases from title/brief for use in sentences."""
    t = (text or "").lower()
    t = re.sub(r"https?://\S+", " ", t)
    toks = re.findall(r"[a-z0-9][a-z0-9_\-/]*", t)
    bad = set("""a about above after again against all am an and any are as at be because been
        before being below between both but by can could did do does doing down during each few
        for from further had has have having he her here hers herself him himself his how i if in
        into is it its itself let me more most my myself nor not of off on once only or other our
        ours ourselves out over own same she should so some such than that the their theirs them
        themselves then there these they this those through to too under until up very was we were
        what when where which while who whom why with would you your yours yourself yourselves""".split())
    toks = [t for t in toks if len(t) > 2 and t not in bad]
    # stitch some bi-grams for flavor
    pairs = []
    for i in range(len(toks) - 1):
        if toks[i] != toks[i+1]:
            pairs.append(toks[i] + " " + toks[i+1])
    ranked = list(dict.fromkeys(pairs + toks))  # keep order, de-dupe
    return ranked[:20]

def _sentenceize(phrases, tpl):
    """Fill a template with the best-available phrases."""
    p = (phrases + ["the fundamentals", "operational discipline", "measurable outcomes"])
    return tpl.format(a=p[0], b=p[1], c=p[2], d=p[3], e=p[4])

def _bullets_from(phrases, verbs, n=4):
    base = phrases[:]
    random.shuffle(base)
    base = base[:n]
    out = []
    for i, ph in enumerate(base):
        v = verbs[i % len(verbs)]
        ph = ph.replace("_"," ").replace("-"," ")
        out.append(f"{v} {ph}.")
    return out

def _cap(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit-1] + "…"

# ===== Core composer =====
def compose_post(title, url, brief):
    title = _clean(title)
    brief = _clean(brief)

    phrases = _split_phrases(title + " " + brief)
    if not phrases:
        phrases = ["oracle migrations", "performance and reliability", "cost and risk"]

    # Hook
    HOOKS = [
        "Field note: {a}",
        "What I’m seeing in real projects: {a}",
        "Hard truth: {a}",
        "If you care about uptime and sleep: {a}",
        "From recent migrations: {a}",
    ]
    hook = _sentenceize(phrases, random.choice(HOOKS))

    # Why it matters (context)
    context = _sentenceize(
        phrases,
        "This keeps showing up in the wild: teams push fast, complexity creeps in, and {a} becomes the bottleneck. "
        "When {b} isn’t explicit and {c} is assumed, outages and surprises follow."
    )

    # My take (opinionated)
    take = _sentenceize(
        phrases,
        "My take: fix {a} and {b} first, not the shiny knobs. Tools help, but outcomes come from designs that make "
        "{c} measurable, {d} repeatable, and {e} boring to operate."
    )

    # What to watch (short bullets)
    watch = _bullets_from(
        phrases,
        verbs=["Watch", "Baseline", "Alert on", "Track"],
        n=3
    )

    # Practical steps
    steps = _bullets_from(
        phrases,
        verbs=["Start with", "Automate", "Document", "Test"],
        n=4
    )

    # Pitfalls
    pitfalls_raw = [
        "Chasing parameters before fixing data flow",
        "Unowned runbooks and tribal knowledge",
        "No single source of truth for configs",
        "Skipping DR drills because 'we're busy'"
    ]
    pitfalls = [f"Avoid: {p}." for p in random.sample(pitfalls_raw, k=3)]

    # One prediction
    prediction = _sentenceize(
        phrases,
        "Prediction: within 12–18 months, {a} and {b} become table-stakes and most teams stop debating {c}."
    )

    # CTA
    cta = random.choice([
        "What would you add—or remove—from this list?",
        "Disagree with my take? Convince me.",
        "What’s the hidden gotcha I didn’t mention?",
        "If you’ve solved this cleanly, I want to learn from you.",
    ])

    # Assemble (moderately detailed; no links/attribution)
    body = (
        f"{hook}\n\n"
        f"{context}\n\n"
        f"My take:\n{take}\n\n"
        f"What to watch:\n" + "\n".join(f"• {b}" for b in watch) + "\n\n"
        f"Practical steps:\n" + "\n".join(f"• {b}" for b in steps) + "\n\n"
        f"Pitfalls:\n" + "\n".join(f"• {b}" for b in pitfalls) + "\n\n"
        f"{prediction}\n"
        f"{cta}"
    )

    # Highlights for banner (3 short bullets, no periods)
    highlights = [b.replace("• ","").rstrip(".") for b in (watch + steps)][:3]

    # LinkedIn hard cap ~3000 chars; keep comfortably below
    return _cap(body, 2200), highlights

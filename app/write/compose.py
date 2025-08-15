import re, random

def _clean(s: str) -> str:
    s = (s or "").strip()
    return re.sub(r"\s+", " ", s)

def _phrases(text: str, max_n: int = 12) -> list:
    t = re.sub(r"https?://\S+", " ", (text or "").lower())
    toks = re.findall(r"[a-z0-9][a-z0-9_\-/]*", t)
    stop = set("""a about above after again against all am an and any are as at be because been
    before being below between both but by can could did do does doing down during each few for from further had
    has have having he her here hers herself him himself his how i if in into is it its itself let me more most my
    myself nor not of off on once only or other our ours ourselves out over own same she should so some such than
    that the their theirs them themselves then there these they this those through to too under until up very was we
    were what when where which while who whom why with would you your yours yourself yourselves""".split())
    toks = [w.replace("_", " ").replace("-", " ") for w in toks if len(w) > 2 and w not in stop]
    # prefer bigrams for richer phrasing
    pairs = [f"{toks[i]} {toks[i+1]}" for i in range(len(toks)-1) if toks[i] != toks[i+1]]
    ordered = list(dict.fromkeys(pairs + toks))  # keep order, de-dupe
    return ordered[:max_n] or ["oracle migrations", "performance", "reliability"]

def _pick(xs): return random.choice(xs)

def compose_post(title, url, brief):
    title = _clean(title)
    brief = _clean(brief)
    phrases = _phrases(title + " " + brief)

    # Tone presets (lightly varied each run)
    openers = [
        "Quick field note:",
        "From recent work:",
        "What I’m seeing a lot:",
        "Hard-earned lesson:",
        "If you’re in the middle of this:"
    ]
    stances = [
        "The wins come from getting the basics right and repeating them.",
        "Most pain isn’t exotic—it’s small gaps that add up under load.",
        "You don’t need heroics; you need clarity, guardrails, and practice.",
        "The tool matters, but the design and runbooks matter more.",
        "Simple, observable paths beat clever, fragile ones."
    ]

    # First paragraph (hook + context) — natural, specific
    topic_hint = phrases[0]
    p1 = (
        f"{_pick(openers)} {title or topic_hint}. "
        f"In real projects, this shows up as unclear ownership, half-done configs, and invisible failure modes. "
        f"Fixing {phrases[0]} and {phrases[1] if len(phrases)>1 else 'the fundamentals'} early saves a lot of weekend work later."
    )

    # Second paragraph (my take) — opinionated but practical
    p2 = (
        f"My take: {_pick(stances)} Start with a crisp definition of done, make it repeatable, "
        f"and prove it under pressure. Treat {phrases[2] if len(phrases)>2 else 'risk'} and "
        f"{phrases[3] if len(phrases)>3 else 'cost'} as first-class signals, not afterthoughts."
    )

    # Decide if bullets are actually helpful this time
    use_bullets = (len(phrases) >= 6 and random.random() < 0.6)
    bullets = []
    if use_bullets:
        verbs = ["Define", "Automate", "Baseline", "Test", "Document", "Alert on"]
        picks = phrases[:6]
        random.shuffle(picks)
        for i, ph in enumerate(picks[:3]):  # max 3, short and useful
            v = verbs[i % len(verbs)]
            ph = ph.replace(".", "")
            bullets.append(f"{v} {ph} in plain language and make someone accountable.")

    # Gentle CTA (no link, no source)
    ctas = [
        "What would you do differently?",
        "Where have you seen this go wrong?",
        "If you’ve solved this cleanly, I want to learn from you.",
        "Disagree with my take? Tell me why."
    ]
    cta = _pick(ctas)

    # Assemble with natural flow: 2 short paragraphs, optional bullets, CTA
    parts = [p1, p2]
    if bullets:
        parts.append("\n".join(f"• {b}" for b in bullets))
    parts.append(cta)

    body = "\n\n".join(parts)

    # Highlights for banner (only if we used bullets; otherwise pull key phrases)
    if bullets:
        highlights = [b.replace("• ", "").rstrip(".") for b in bullets][:3]
    else:
        highlights = [w.title() for w in phrases[:3]]

    # Keep comfortably under LinkedIn’s cap
    return body[:1800], highlights

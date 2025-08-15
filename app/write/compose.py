import re, random

def _clean(s: str) -> str:
    s = (s or "").strip()
    return re.sub(r"\s+", " ", s)

def _phrases(text: str, max_n: int = 14) -> list:
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

    # Templates
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

    # Paragraph 1 — hook + context + observed patterns
    topic_hint = phrases[0]
    p1 = (
        f"{_pick(openers)} {title or topic_hint}. "
        f"I’ve watched multiple teams wrestle with this, and it usually starts the same way: "
        f"big goals, some quick wins, then creeping complexity. The early excitement fades when "
        f"small misalignments—like unclear ownership or half-finished configs—turn into recurring headaches. "
        f"Fixing {phrases[0]} and {phrases[1] if len(phrases)>1 else 'the fundamentals'} early is rarely flashy, "
        f"but it’s the difference between firefighting every week and sleeping well at night."
    )

    # Paragraph 2 — my take + what to focus on
    p2 = (
        f"My take: {_pick(stances)} The fastest way to improve outcomes is to make success measurable "
        f"and boring to repeat. That means clear definitions of done, tested recovery steps, and "
        f"visibility into the right signals—not just raw metrics. "
        f"Treat {phrases[2] if len(phrases)>2 else 'risk'} and "
        f"{phrases[3] if len(phrases)>3 else 'cost'} as design inputs from day one, not problems to patch later. "
        f"When the fundamentals are right, the advanced tuning actually sticks."
    )

    # Optional bullets for emphasis
    use_bullets = (len(phrases) >= 6 and random.random() < 0.7)
    bullets = []
    if use_bullets:
        verbs = ["Define", "Automate", "Baseline", "Test", "Document", "Alert on"]
        picks = phrases[:6]
        random.shuffle(picks)
        for i, ph in enumerate(picks[:3]):
            v = verbs[i % len(verbs)]
            bullets.append(f"{v} {ph} and make someone accountable.")

    # CTA
    ctas = [
        "What’s been your experience with this?",
        "Where have you seen this go wrong?",
        "If you’ve solved this cleanly, I’d love to hear how.",
        "Disagree with my take? Tell me why."
    ]
    cta = _pick(ctas)

    # Assemble
    parts = [p1, p2]
    if bullets:
        parts.append("\n".join(f"• {b}" for b in bullets))
    parts.append(cta)

    body = "\n\n".join(parts)

    # Highlights for banner
    if bullets:
        highlights = [b.replace("• ", "").rstrip(".") for b in bullets][:3]
    else:
        highlights = [w.title() for w in phrases[:3]]

    return body[:2200], highlights

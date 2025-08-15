import re, random, math

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before being below
between both but by can can't cannot could couldn't did didn't do does doesn't doing don't down during each few
for from further had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself
his how how's i i'd i'll i'm i've if in into is isn't it it's its itself let let's me more most mustn't my myself
no nor not of off on once only or other ought our ours ourselves out over own same shan't she she'd she'll she's should
shouldn't so some such than that that's the their theirs them themselves then there there's these they they'd they'll they're
they've this those through to too under until up very was wasn't we we'd we'll we're we've were weren't what what's when when's
where where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves
""".split())

def _clean(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '')).strip()

def _normalize(text: str) -> list:
    txt = (text or '').lower()
    # remove urls
    txt = re.sub(r'https?://\S+', ' ', txt)
    # keep words, numbers, slashes, hyphens
    words = re.findall(r"[a-z0-9][a-z0-9\-_/]*", txt)
    # filter stopwords / tiny tokens
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def _key_phrases(title: str, brief: str, top_n: int = 6) -> list:
    """Very simple keyword scorer (freq + title boost + position bonus)."""
    title = _clean(title)
    brief = _clean(brief)
    tokens = _normalize(title) + _normalize(brief)
    if not tokens:
        return []
    scores = {}
    # basic freq
    for i, tok in enumerate(tokens):
        scores[tok] = scores.get(tok, 0) + 1.0
        # earlier tokens get tiny bonus
        scores[tok] += 0.5 * max(0, (len(tokens) - i) / max(1, len(tokens)))
    # title terms get a boost
    for tok in _normalize(title):
        scores[tok] = scores.get(tok, 0) + 2.0
    # prefer multiword phrases by stitching neighbors that repeat
    # (simple heuristic)
    pairs = []
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i+1]
        if a != b and a not in STOPWORDS and b not in STOPWORDS:
            pairs.append(f"{a} {b}")
    for p in pairs:
        scores[p] = scores.get(p, 0) + 0.8

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    phrases = [k for k, _ in ranked if not k.isdigit()]
    # de-dup near-duplicates (keep first occurrence)
    uniq = []
    seen = set()
    for p in phrases:
        base = p.replace('-', ' ').replace('_', ' ')
        if base not in seen:
            uniq.append(base)
            seen.add(base)
        if len(uniq) >= top_n:
            break
    return uniq

STYLES = ["educational", "opinion", "prediction", "debate", "storytelling", "trendspotting", "mythbusting", "wishlist"]

def _style_pick():
    return random.choice(STYLES)

def _hook(style, title, phrases):
    t = title.strip()
    any_key = phrases[0] if phrases else ""
    if style == "educational":
        return f"📚 {t}"
    if style == "opinion":
        return f"💭 My take: {t}"
    if style == "prediction":
        year = random.choice(["2026","2027","the next 18 months"])
        return f"🔮 Prediction: {t} becomes standard by {year}"
    if style == "debate":
        return f"🔥 Hot take: {t} is overrated"
    if style == "storytelling":
        return f"🧳 From the road: {t}"
    if style == "trendspotting":
        return f"📈 I’m seeing a shift: {any_key or t}"
    if style == "mythbusting":
        return f"🧨 Myth: {t}"
    if style == "wishlist":
        return f"🛠️ If I could change one thing: {any_key or t}"
    return t

def _insight(style, title):
    if style == "educational":
        return "Here’s a concise playbook you can apply this week."
    if style == "opinion":
        return "Most teams miss the real bottleneck—and spend time in the wrong place."
    if style == "prediction":
        return "Signals are there: vendor roadmaps, customer asks, and what I see in the field."
    if style == "debate":
        return "I’ve watched teams pour months into this with little payoff."
    if style == "storytelling":
        return "This came up on a recent project—pressure, constraints, and a hard deadline."
    if style == "trendspotting":
        return "Across clients, this pattern is showing up more and more."
    if style == "mythbusting":
        return "Contrary to popular belief, the common advice here is backwards."
    if style == "wishlist":
        return "If vendors and teams nailed this, we’d save weeks and avoid painful rollbacks."
    return "Quick thoughts you can put to work."

def _bulletize(style, phrases):
    """Turn key phrases into 3–5 bullets tailored by style."""
    base = phrases[:5] if phrases else []
    if not base:
        base = ["make configs repeatable", "secure the path end-to-end", "measure what matters", "practice failover"]
    bullets = []

    if style == "educational":
        for p in base:
            bullets.append(f"Do this next: {p}.")
    elif style == "opinion":
        for p in base:
            bullets.append(f"Stop ignoring {p}—it costs real time.")
    elif style == "prediction":
        for p in base:
            bullets.append(f"Expect {p} to be automated or policy-enforced.")
    elif style == "debate":
        for p in base:
            bullets.append(f"{p.capitalize()} — useful only after fundamentals are solid.")
    elif style == "storytelling":
        for p in base:
            bullets.append(f"We nearly slipped until we fixed {p}.")
    elif style == "trendspotting":
        for p in base:
            bullets.append(f"Seeing this more: {p}.")
    elif style == "mythbusting":
        for p in base:
            bullets.append(f"Not true: you don’t always need {p}.")
    elif style == "wishlist":
        for p in base:
            bullets.append(f"I wish this were one-click: {p}.")
    else:
        for p in base:
            bullets.append(f"{p.capitalize()} matters.")
    # Cap to 4 bullets for LinkedIn readability
    return bullets[:4]

def _cta(style):
    options = [
        "Agree or disagree? Tell me why.",
        "What would you change here?",
        "Seen this in the wild? Drop your lesson.",
        "What should I test next?",
        "If you’ve solved this well, I want to learn from you.",
    ]
    # Make debate/prediction a bit spicier
    if style in ("debate","prediction","mythbusting"):
        options += [
            "Prove me wrong in the comments.",
            "What did I miss?",
        ]
    return random.choice(options)

def compose_post(title, url, brief):
    # Extract topic phrases
    phrases = _key_phrases(title or "", brief or "")
    style = _style_pick()

    hook = _hook(style, title or "Latest field note", phrases)
    insight = _insight(style, title or "")

    bullets = _bulletize(style, phrases)
    body = (
        f"{hook}\n\n"
        f"{insight}\n\n"
        + "\n".join([f"• {b}" for b in bullets]) +
        (f"\n\nMore context: {url}" if url else "") +
        f"\n{_cta(style)}"
    )
    highlights = bullets[:3]
    return body[:1300], highlights

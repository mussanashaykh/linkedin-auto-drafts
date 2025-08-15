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

STYLES = ["educational", "opinion", "prediction", "debate", "storytelling", "trendspotting]()

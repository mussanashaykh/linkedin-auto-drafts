import os, json, hashlib, random
from urllib.parse import urlparse

from sources.reddit import fetch_reddit
from sources.reddit_people import fetch_reddit_people   # make sure you added this earlier
from sources.rss import fetch_rss
from sources.qa import fetch_qa                          # and this one too
from write.summarize import score, clean                 # reuse your existing scoring

STATE_DIR = ".state"
STATE_PATH = os.path.join(STATE_DIR, "state.json")

DEFAULT_STATE = {
    "recent_ids": [],        # list of item ids we've posted recently
    "recent_domains": [],    # last few domains used (to rotate)
    "max_ids": 60,           # remember last 60 picks (~6 months if weekly)
    "max_domains": 5         # avoid repeating any of the last 5 domains
}

def _ensure_state():
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(STATE_PATH):
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_STATE, f)
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            data = DEFAULT_STATE
    # fill defaults if missing
    for k,v in DEFAULT_STATE.items():
        data.setdefault(k, v if not isinstance(v, list) else list(v))
    return data

def _save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def _canonical_id(item):
    base = item.get("url") or item.get("title") or ""
    h = hashlib.sha1(base.encode("utf-8", errors="ignore")).hexdigest()
    return h

def _domain(item):
    d = item.get("domain")
    if d: return d.lower()
    u = item.get("url") or ""
    try:
        return urlparse(u).netloc.lower()
    except Exception:
        return ""

def get_candidates():
    # Pull broadly; tune hours if you want a different window
    items = []
    items += fetch_reddit(hours=72)
    items += fetch_reddit_people(hours=168)
    items += fetch_rss(hours=168)
    items += fetch_qa(hours=168)

    # normalize & attach ids/domains
    for it in items:
        it["id"] = _canonical_id(it)
        it["domain"] = _domain(it)

    # de-dup by id
    dedup = {}
    for it in items:
        dedup[it["id"]] = it
    return list(dedup.values())

def pick_item(candidates):
    state = _ensure_state()
    used_ids = set(state.get("recent_ids", []))
    recent_domains = state.get("recent_domains", [])

    # filter out already used ids
    fresh = [c for c in candidates if c["id"] not in used_ids]

    if not fresh:
        # fallback: if everything is used, reset the memory (rare)
        fresh = candidates

    # rank by your existing score() then randomize among top N
    fresh.sort(key=score, reverse=True)
    top = fresh[:12] if len(fresh) >= 12 else fresh

    # try to avoid recent domains
    rotated = [c for c in top if c.get("domain") and c["domain"] not in recent_domains] or top

    pick = random.choice(rotated[:7] if len(rotated) >= 7 else rotated)

    # update state
    dom = pick.get("domain") or ""
    new_ids = [pick["id"]] + state.get("recent_ids", [])
    new_domains = ([dom] + recent_domains) if dom else recent_domains

    # trim
    state["recent_ids"] = new_ids[:state.get("max_ids", 60)]
    state["recent_domains"] = new_domains[:state.get("max_domains", 5)]

    _save_state(state)
    return pick

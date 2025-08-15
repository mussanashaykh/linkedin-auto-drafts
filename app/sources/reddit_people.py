import requests, time, re
from datetime import datetime, timedelta, timezone

SUBS = ["oracle", "oracledatabase", "OracleCloud", "aws", "devops", "Database", "databases"]
FIRST_PERSON = re.compile(r"\b(I|I'm|I’ve|I was|we|we’re|our|my|lesson|postmortem)\b", re.I)

def fetch_reddit_people(hours=168, per_sub=40):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    ua = {"User-Agent": "oracle-li-free/1.1"}
    items = []
    for sub in SUBS:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit={per_sub}"
        try:
            r = requests.get(url, headers=ua, timeout=20)
            r.raise_for_status()
        except Exception:
            continue
        for child in r.json().get("data", {}).get("children", []):
            d = child["data"]
            if d.get("stickied") or d.get("over_18"):
                continue
            created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
            if created < cutoff:
                continue
            txt = (d.get("selftext","") or "")
            title = (d.get("title","") or "").strip()
            blob = f"{title}\n{txt}"
            if not FIRST_PERSON.search(blob):
                continue
            items.append({
                "source": "reddit_people",
                "title": title,
                "url": "https://www.reddit.com" + d.get("permalink",""),
                "created": created,
                "score": int(d.get("score", 0)) + 2,  # slight boost
                "text": txt[:3000]
            })
    return items

import requests, time
from datetime import datetime, timedelta, timezone

SUBS = ["oracle", "oracledatabase", "OracleCloud", "aws", "devops"]

def fetch_reddit(hours=72, per_sub=30):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    ua = {"User-Agent": "oracle-li-free/1.0"}
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
            items.append({
                "source": "reddit",
                "subreddit": sub,
                "title": (d.get("title","") or "").strip(),
                "url": "https://www.reddit.com" + d.get("permalink",""),
                "score": int(d.get("score", 0)),
                "created": created,
                "text": (d.get("selftext","") or "")[:2000]
            })
    return items


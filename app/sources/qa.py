import feedparser, time, re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

SO_TAGS = [
  "oracle", "oracle-19c", "goldengate", "aws-dms", "rds", "ssl", "tls",
  "data-migration", "disaster-recovery", "performance"
]
HN_QUERIES = [
  "oracle database", "goldengate", "rds oracle", "aws dms", "disaster recovery database",
  "database performance", "cloud migration database"
]

def fetch_stackoverflow(hours=168):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out=[]
    for tag in SO_TAGS:
        url = f"https://stackoverflow.com/feeds/tag?tagnames={tag}&sort=newest"
        feed = feedparser.parse(url)
        for e in feed.entries:
            t = e.get("updated_parsed") or e.get("published_parsed")
            if not t: 
                continue
            published = datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
            if published < cutoff: 
                continue
            out.append({
                "source":"stackoverflow",
                "feed":url,
                "domain": urlparse(e.get("link","")).netloc.lower(),
                "title": (e.get("title","") or "").strip(),
                "url": e.get("link",""),
                "created": published,
                "text": (e.get("summary","") or "")[:2000]
            })
    return out

def fetch_hn(hours=168):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out=[]
    for q in HN_QUERIES:
        url = f"https://hnrss.org/newest?q={q.replace(' ','+')}"
        feed = feedparser.parse(url)
        for e in feed.entries:
            t = e.get("updated_parsed") or e.get("published_parsed")
            if not t:
                continue
            published = datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
            if published < cutoff:
                continue
            out.append({
                "source":"hackernews",
                "feed":url,
                "domain": urlparse(e.get("link","")).netloc.lower(),
                "title": (e.get("title","") or "").strip(),
                "url": e.get("link",""),
                "created": published,
                "text": (e.get("summary","") or "")[:2000]
            })
    return out

def fetch_qa(hours=168):
    return fetch_stackoverflow(hours) + fetch_hn(hours)

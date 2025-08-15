import feedparser, time
from datetime import datetime, timedelta, timezone
FEEDS = [
  "https://blogs.oracle.com/database/rss",
  "https://blogs.oracle.com/cloud-infrastructure/rss",
  "https://aws.amazon.com/blogs/database/feed/",
  "https://aws.amazon.com/architecture/feed/",
]

def get_rss_items(hours=168):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    out=[]
    for url in FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            # robust published parsing
            published = None
            for key in ("published_parsed","updated_parsed"):
                t = getattr(e, key, None)
                if t:
                    published = datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
                    break
            if not published or published < cutoff:
                continue
            out.append({
                "source":"rss",
                "feed":url,
                "title":e.title,
                "url":e.link,
                "created":published.isoformat(),
                "text": getattr(e, "summary", "")[:2000]
            })
    return out

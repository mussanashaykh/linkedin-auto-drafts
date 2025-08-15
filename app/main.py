import os, json
from datetime import datetime, timezone
from sources.reddit import fetch_reddit
from sources.reddit_people import fetch_reddit_people
from sources.rss import fetch_rss
from sources.qa import fetch_qa
from write.summarize import top_item, extractive_brief
from write.compose import compose_post
from images.banner import make_banner

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def run():
    items = []
    items += fetch_reddit(hours=72)            # general tech posts
    items += fetch_reddit_people(hours=168)    # first-person posts
    items += fetch_rss(hours=168)              # blogs (diverse)
    items += fetch_qa(hours=168)               # StackOverflow + HN

    pick = top_item(items)
    if not pick:
        print("No suitable items.")
        return 0

    brief = extractive_brief(pick)
    body, highlights = compose_post(pick["title"], pick.get("url"), brief)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outdir = os.path.join("out", stamp)
    ensure_dir(outdir)

    with open(os.path.join(outdir, "post.txt"), "w", encoding="utf-8") as f:
        f.write(body)

    with open(os.path.join(outdir, "source.json"), "w", encoding="utf-8") as f:
        json.dump(pick, f, default=str, indent=2)

    make_banner(pick["title"], highlights, os.path.join(outdir, "banner.png"))
    print("Draft created at", outdir)
    return 0

if __name__ == "__main__":
    raise SystemExit(run())

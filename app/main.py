import os, json
from datetime import datetime, timezone
from sources.reddit import fetch_reddit
from sources.rss import fetch_rss
from write.summarize import top_item, extractive_brief
from write.compose import compose_post
from images.banner import make_banner

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def run():
    items = fetch_reddit(hours=72) + fetch_rss(hours=168)
    pick = top_item(items)
    if not pick:
        print("No suitable items.")
        return 0

    brief = extractive_brief(pick)
    post = compose_post(pick["title"], pick["url"], brief)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outdir = os.path.join("out", stamp)
    ensure_dir(outdir)

    with open(os.path.join(outdir,"post.txt"), "w", encoding="utf-8") as f:
        f.write(post)
    with open(os.path.join(outdir,"source.json"), "w", encoding="utf-8") as f:
        json.dump(pick, f, default=str, indent=2)

    make_banner(pick["title"], os.path.join(outdir,"banner.png"))

    print("Draft created at", outdir)
    return 0

if __name__ == "__main__":
    raise SystemExit(run())


import os, json
from datetime import datetime, timezone

from fetch import get_candidates, pick_item
from write.summarize import extractive_brief
from write.compose import compose_post
from images.banner import make_banner

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def run():
    candidates = get_candidates()
    if not candidates:
        print("No candidates fetched.")
        return 0

    pick = pick_item(candidates)
    if not pick:
        print("No suitable item.")
        return 0

    brief = extractive_brief(pick)
    body, highlights = compose_post(pick.get("title",""), pick.get("url"), brief)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outdir = os.path.join("out", stamp)
    ensure_dir(outdir)

    with open(os.path.join(outdir, "post.txt"), "w", encoding="utf-8") as f:
        f.write(body)

    with open(os.path.join(outdir, "source.json"), "w", encoding="utf-8") as f:
        json.dump(pick, f, default=str, indent=2)

    make_banner(pick.get("title",""), highlights, os.path.join(outdir, "banner.png"))
    print("Draft created at", outdir)
    return 0

if __name__ == "__main__":
    raise SystemExit(run())

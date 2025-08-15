from bs4 import BeautifulSoup

KEYWORDS = ["oracle","goldengate","rds","dms","19c","dataguard","ssl","tls","wallet","performance","migration"]

def clean(text):
    soup = BeautifulSoup(text or "", "html.parser")
    t = soup.get_text(" ", strip=True)
    return " ".join(t.split())

def score(item):
    base = item.get("score", 5)
    title = (item.get("title","") + " " + item.get("text","")).lower()
    kscore = sum(1 for k in KEYWORDS if k in title)
    return base + kscore

def top_item(items):
    items = [i for i in items if i.get("title")]
    if not items: return None
    items.sort(key=score, reverse=True)
    return items[0]

def extractive_brief(item, max_len=400):
    text = clean(item.get("text",""))
    if not text:
        return ""
    parts = text.split(". ")
    out=[]
    for p in parts:
        if any(k in p.lower() for k in ["tip","checklist","migrate","secure","ssl","rds","goldengate","dms","19c"]):
            out.append(p)
        if sum(len(x) for x in out) > max_len:
            break
    if not out:
        out = parts[:3]
    return ". ".join(out)[:max_len]

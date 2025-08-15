from bs4 import BeautifulSoup
from urllib.parse import urlparse
import random, re

KEYWORDS = [
    "oracle","goldengate","rds","dms","19c","dataguard","ssl","tls","wallet",
    "performance","migration","database","dr","recovery","backup","encryption",
    "cost","finops","networking","dns","vpc","endpoint","terraform","devops",
    "observability","logging","metrics","kafka","postgres","mysql","gcp","azure","oci"
]
FIRST_PERSON = re.compile(r"\b(I|I'm|I’ve|I was|we|we’re|our|my|lesson|postmortem|retrospective)\b", re.I)

def clean(text):
    soup = BeautifulSoup(text or "", "html.parser")
    t = soup.get_text(" ", strip=True)
    return " ".join(t.split())

def score(item):
    base = item.get("score", 5)

    blob = (item.get("title","") + " " + item.get("text",""))
    blob_l = blob.lower()
    kscore = sum(1 for k in KEYWORDS if k in blob_l)

    # prefer first-person experiences
    ppl_bonus = 2 if FIRST_PERSON.search(blob) else 0

    # domain rotation (avoid AWS every time)
    domain = item.get("domain") or urlparse(item.get("url","")).netloc.lower()
    domain_bias = 0
    if "aws.amazon.com" in domain:
        domain_bias -= 3
    elif any(x in domain for x in ["oracle.com","cloudflare.com","percona.com","infoq.com","martinfowler.com","thoughtworks.com","microsoft.com","google.com","stackoverflow.com","news.ycombinator.com","reddit.com"]):
        domain_bias += 1

    jitter = random.uniform(-1.0, 1.0)
    return base + kscore + ppl_bonus + domain_bias + jitter

def top_item(items):
    items = [i for i in items if i.get("title")]
    if not items: 
        return None
    items.sort(key=score, reverse=True)
    # choose randomly among top 7 for variety
    return random.choice(items[:7])

def extractive_brief(item, max_len=400):
    text = clean(item.get("text",""))
    if not text:
        return ""
    parts = [p.strip() for p in text.split(". ") if p.strip()]
    out=[]
    for p in parts:
        if any(k in p.lower() for k in ["migrate","secure","performance","cost","dr","dns","oracle","goldengate","dms","rds","19c","tls","wallet","lesson","we " ,"i "]):
            out.append(p)
        if sum(len(x) for x in out) > max_len:
            break
    if not out:
        out = parts[:2]
    return ". ".join(out)[:max_len]

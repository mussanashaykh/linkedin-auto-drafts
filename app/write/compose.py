import re, random

# -----------------------
# Small helpers
# -----------------------
def _clean(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text

def _tokens(text: str) -> list:
    text = (text or "").lower()
    text = re.sub(r'https?://\S+', ' ', text)
    return re.findall(r"[a-z0-9][a-z0-9\-_/]*", text)

def _contains(text: str, words: list) -> bool:
    t = " " + (text or "").lower() + " "
    return any((" " + w.lower() + " ") in t for w in words)

# -----------------------
# Topic packs (broad, expandable)
# -----------------------
TOPIC_PACKS = [
    {
        "keys": ["dms","database migration service","cdc","column filter","parallel"],
        "name": "AWS DMS",
        "narratives": [
            "Teams hit CDC lag when one hot table dominates. Splitting the stream with stable filters can help, but only after you validate ordering and conflict behavior.",
            "Parallelism is useful, but correctness comes first. I only scale out after strict validation and baseline metrics."
        ],
        "bullets": [
            "Choose a stable filter (tenant_id / region / hash) to avoid collisions",
            "Start with 2–3 tasks per hot table; watch latency and CPU before scaling",
            "Validate row counts and conflicts; automate a post-cutover diff",
            "Track end-to-end lag; alert on trend, not single spikes"
        ],
    },
    {
        "keys": ["goldengate","ogg","trail","extract","replicat"],
        "name": "Oracle GoldenGate",
        "narratives": [
            "GoldenGate shines when initial load and CDC are treated as different beasts. Trail sizing, checkpoint hygiene, and cert rotation are uptime levers.",
            "Lag surprises usually trace back to I/O or network—not one magic parameter."
        ],
        "bullets": [
            "Separate initial load from CDC with different tunables and runbooks",
            "Size trail files conservatively; keep filesystem latency predictable",
            "Enable TLS; store wallets/keys as code with rotation on calendar",
            "Alert on lag drift from a baseline, not just absolute values"
        ],
    },
    {
        "keys": ["rds","19c","oracle rds","parameter group","option group"],
        "name": "RDS for Oracle",
        "narratives": [
            "Production setups stay sane when params, logs, and keys are treated as code. Rotation and failover should be boring, not heroics.",
            "Most trouble I see is shared parameter groups and ad-hoc tweaks nobody can reproduce."
        ],
        "bullets": [
            "Use dedicated parameter groups per environment; forbid manual drift",
            "Store credentials in Secrets Manager and rotate on a schedule",
            "Enable Performance Insights and CloudWatch Logs from day 0",
            "Set storage autoscaling guardrails; alert on IOPS/latency"
        ],
    },
    {
        "keys": ["dr","disaster","failover","pilot-light","recovery"],
        "name": "Disaster Recovery",
        "narratives": [
            "DR only works when you rehearse it. Pilot-light with scripted promotion beats glossy diagrams.",
            "People overestimate RTO until they measure it under stress."
        ],
        "bullets": [
            "Automate snapshot copy and KMS sharing between regions/accounts",
            "Script promotion and DNS cutover; record real RTO/RPO",
            "Test quarterly; log every surprise and fix it before the next drill",
            "Keep runbooks alongside dashboards for one-screen execution"
        ],
    },
    {
        "keys": ["kms","tls","ssl","wallet","keystore","encryption","mfa"],
        "name": "Security",
        "narratives": [
            "Enable TCPS early so wallet and DN issues show up before go-live. Security debt compounds when it’s postponed.",
            "Policy over heroics: lock TLS versions and ciphers; rotate before expiry."
        ],
        "bullets": [
            "Pin CA chains and verify DN matching on both ends",
            "Enforce TLS min version/ciphers via param groups or policies",
            "Document wallet paths, owners, and renewal steps",
            "Alert on cert expiry at 30/14/7 days"
        ],
    },
    {
        "keys": ["cost","spend","finops","budget"],
        "name": "Cost & FinOps",
        "narratives": [
            "Performance wins are great, but untracked cost growth erases them. Budgets need the same automation as deploys.",
            "Most teams don’t tag consistently—then wonder where the money went."
        ],
        "bullets": [
            "Tag consistently (owner, env, system, cost-center) and enforce with policy",
            "Alert on weekly spend deltas, not end-of-month surprises",
            "Right-size storage/IOPS by observed 95th percentile",
            "Archive logs/objects with lifecycle rules on day one"
        ],
    },
    {
        "keys": ["vpc","endpoint","dns","route 53","privatelink","transit","resolver"],
        "name": "Networking",
        "narratives": [
            "If DNS and routes aren’t crisp, everything feels random. Private endpoints and explicit forwarding rules keep diagnostics sane.",
            "I’ve seen more outages from DNS assumptions than from code bugs."
        ],
        "bullets": [
            "Define conditional forwarding for private zones explicitly",
            "Use interface endpoints for control planes; test from each subnet",
            "Document allowed egress and ephemeral port behavior",
            "Probe health paths continuously and alert on DNS drift"
        ],
    },
]

FALLBACK = {
    "name": "Architecture",
    "narratives": [
        "Under pressure, simple architectures outperform clever ones. Friction hides in hand-offs and implicit assumptions.",
        "Most outages aren’t exotic—they’re basics left implicit."
    ],
    "bullets": [
        "Write the happy-path and the fail-path as code",
        "Measure user-visible latency and error budget, not vanity metrics",
        "Automate config drift detection and close the loop",
        "Run small fire-drills until muscle memory forms"
    ],
}

STYLES = [
    "educational","opinion","prediction","debate",
    "storytelling","trendspotting","mythbusting","wishlist"
]

# -----------------------
# Core composition
# -----------------------
def _pick_pack(title: str, brief: str):
    t = (title + " " + brief).lower()
    for pack in TOPIC_PACKS:
        if any(k in t for k in pack["keys"]):
            return pack
    return FALLBACK

def _style():
    return random.choice(STYLES)

def _hook(style: str, title: str, topic_name: str):
    title = title.strip()
    if style == "educational":   return f"📚 {title}"
    if style == "opinion":       return f"💭 My take on {topic_name}: {title}"
    if style == "prediction":    return f"🔮 {topic_name} in 18 months: {title}"
    if style == "debate":        return f"🔥 Unpopular opinion: {title}"
    if style == "storytelling":  return f"🧳 From the field: {title}"
    if style == "trendspotting": return f"📈 I’m seeing a shift in {topic_name}: {title}"
    if style == "mythbusting":   return f"🧨 Myth in {topic_name}: {title}"
    if style == "wishlist":      return f"🛠️ I wish this were easier: {title}"
    return title

def _narrative(style: str, narratives: list):
    base = random.choice(narratives)
    if style == "opinion":
        return base + " This is where teams waste the most time."
    if style == "prediction":
        return base + " Roadmaps and customer asks point the same way."
    if style == "debate":
        return base + " Change my mind if you disagree."
    if style == "storytelling":
        return base + " We hit a wall, made a call, and shipped."
    if style == "trendspotting":
        return base + " I’m seeing it across clients and sizes."
    if style == "mythbusting":
        return base + " The common advice is backwards here."
    if style == "wishlist":
        return base + " If vendors nailed this, life would be easier."
    return base

def _bullets(style: str, bullets: list):
    # Full sentences with verbs; pick 3–4
    chosen = bullets[:]
    random.shuffle(chosen)
    chosen = chosen[: random.choice([3,3,4])]
    out = []
    for b in chosen:
        b = b.rstrip(".")
        if style == "debate":
            out.append(f"{b}. Prove value with data before investing more.")
        elif style == "prediction":
            out.append(f"{b}. Expect this to become table-stakes.")
        elif style == "opinion":
            out.append(f"{b}. Stop treating it as optional.")
        elif style == "wishlist":
            out.append(f"{b}. I want this to be one-click.")
        else:
            out.append(f"{b}.")
    return out

def _cta(style: str):
    pool = [
        "What would you do differently?",
        "Agree or disagree?",
        "Seen this in the wild?",
        "What’s the hidden gotcha here?",
        "If you’ve solved this cleanly, I want to learn from you."
    ]
    if style in ("debate","mythbusting","opinion","prediction"):
        pool += ["Convince me I’m wrong.", "What did I miss?"]
    return random.choice(pool)

def compose_post(title, url, brief):
    title = _clean(title)
    brief = _clean(brief)

    pack = _pick_pack(title, brief)
    style = _style()

    hook = _hook(style, title, pack["name"])
    narrative = _narrative(style, pack["narratives"])
    if not narrative or len(narrative.split()) < 8:
        narrative = "Quick context from recent work and conversations with teams running this in production."

    bullets = _bullets(style, pack["bullets"])

    body = (
        f"{hook}\n\n"
        f"{narrative}\n\n"
        + "\n".join([f"• {b}" for b in bullets]) +
        "\n" + _cta(style)
    )

    # highlights for banner (short, no periods)
    highlights = [b.replace(".", "") for b in bullets][:3]
    return body[:1300], highlights

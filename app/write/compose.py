def compose_post(title, url, brief):
    hook = f"Field note: {title.strip()}"
    insight = brief or "Quick takeaway for data folks working with Oracle in the cloud."
    bullets = [
        "Keep configs repeatable (IaC) and versioned.",
        "Prefer SSL/TLS everywhere; verify wallet/keystore early.",
        "Separate initial load (DMS) from CDC (GoldenGate) for sanity.",
        "Automate logs & metrics; test DR like you mean it."
    ]
    body = (
f"{hook}\n\n"
f"{insight}\n\n"
+ "\n".join([f"• {b}" for b in bullets[:4]]) +
f"\n\nMore context: {url}\n"
f"What’s one gotcha you’ve hit on Oracle migrations lately?"
    )
    return body[:1300]

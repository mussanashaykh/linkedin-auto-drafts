from PIL import Image, ImageDraw, ImageFont

def _font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def _wrap(text: str, max_chars: int = 32):
    words = (text or "").split()
    lines = []
    line = ""
    for w in words:
        trial = (line + " " + w).strip()
        if len(trial) <= max_chars:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def make_banner(title, highlights, out_path):
    # Canvas
    W, H = 1200, 675
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # Soft vertical gradient background
    for y in range(H):
        c1 = 246 - int(50 * y / H)
        c2 = 250 - int(35 * y / H)
        d.line([(0, y), (W, y)], fill=(c1, c1, c2))

    # Title (wrapped)
    title_text = (title or "")[:120]
    y = 80
    for ln in _wrap(title_text, max_chars=28)[:4]:
        d.text((80, y), ln, font=_font(52, bold=True), fill=(20, 22, 35))
        y += 64

    # Divider
    d.line([(80, y + 10), (W - 80, y + 10)], fill=(210, 214, 225), width=2)

    # Highlights (2–3 short bullets)
    y += 30
    for hl in (highlights or [])[:3]:
        d.text((100, y), f"• {hl}", font=_font(30, bold=False), fill=(35, 38, 55))
        y += 44

    # Footer tag (brand line — customize if you want)
    d.text((80, H - 70), "Oracle • Cloud • Migrations", font=_font(24, bold=False), fill=(90, 95, 120))

    img.save(out_path)
    return out_path

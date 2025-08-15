from PIL import Image, ImageDraw, ImageFont

def _font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def _wrap(text, max_chars=38):
    words = (text or "").split()
    lines=[]; line=""
    for w in words:
        test = (line + " " + w).strip()
        if len(test) <= max_chars:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

def make_banner(title, highlights, out_path):
    W, H = 1200, 675
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # soft gradient background
    for y in range(H):
        c = 245 - int(60 * y / H)   # light to slightly darker
        d.line([(0,y),(W,y)], fill=(c, c, 250 - int(40 * y / H)))

    # Title
    title_lines = _wrap((title or "")[:120], max_chars=28)
    y = 80
    for ln in title_lines[:4]:
        d.text((80, y), ln, font=_font(52, bold=True), fill=(20, 22, 35))
        y += 64

    # Divider
    d.line([(80, y+10), (W-80, y+10)], fill=(210, 214, 225), width=2)

    # Highlights bullets (2–3)
    y += 30
    for hl in (highlights or [])[:3]:
        d.text((100, y), f"• {hl}", font=_font(30), fill=(35, 38, 55))
        y += 44

    # Footer tag
    d.text((80, H-70), "Oracle • Cloud • Migrations", font=_font(24), fill=(90, 95, 120))

    img.save(out_path)
    return out_path

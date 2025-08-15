from PIL import Image, ImageDraw, ImageFont

def make_banner(text, out_path):
    W,H = 1200, 675
    img = Image.new("RGB", (W, H), (245,247,250))
    d = ImageDraw.Draw(img)
    title = (text or "")[:110]
    # Simple wrap at ~40 chars
    lines=[]; line=""
    for w in title.split():
        if len(line + " " + w) <= 40:
            line = (line + " " + w).strip()
        else:
            lines.append(line); line=w
    if line: lines.append(line)
    y = 220
    for ln in lines[:5]:
        d.text((80,y), ln, fill=(25,25,25))
        y += 54
    d.text((80, 80), "Oracle • Cloud • Migrations", fill=(90,90,90))
    img.save(out_path)
    return out_path

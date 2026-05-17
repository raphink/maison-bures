#!/usr/bin/env python3
"""Generate OG image (1200×630) for maison-bures.fr."""

from PIL import Image, ImageDraw, ImageFont
import math

# ── Config ─────────────────────────────────────────────────────────────────────
W, H        = 1200, 630
PHOTO       = "photos/jardin1.jpg"
OUT         = "photos/og.jpg"
FONT        = "/System/Library/Fonts/HelveticaNeue.ttc"
TITLE       = "Maison à vendre\nBures-sur-Yvette, Vallée de Chevreuse"
PRICE       = "436 800 € FAI"
STATS       = "6 pièces  ·  105 m²  ·  Jardin 489 m²"
DOMAIN      = "maison-bures.fr"
ACCENT      = (255, 210, 80)   # warm gold
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)

# ── Fonts ──────────────────────────────────────────────────────────────────────
f_price  = ImageFont.truetype(FONT, 42, index=1)   # Bold
f_stats  = ImageFont.truetype(FONT, 32, index=7)   # Light
f_domain = ImageFont.truetype(FONT, 26, index=7)   # Light

# ── Background photo ──────────────────────────────────────────────────────────
photo = Image.open(PHOTO).convert("RGB")
# Smart crop: resize so shortest side fills, center crop
pw, ph = photo.size
scale  = max(W / pw, H / ph)
nw, nh = int(pw * scale), int(ph * scale)
photo  = photo.resize((nw, nh), Image.LANCZOS)
left   = (nw - W) // 2
top    = (nh - H) // 2
photo  = photo.crop((left, top, left + W, top + H))

canvas = photo.copy()
draw   = ImageDraw.Draw(canvas)

# ── Gradient overlay (dark bottom, slight top vignette) ──────────────────────
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
odraw   = ImageDraw.Draw(overlay)

gradient_start = int(H * 0.28)   # gradient begins at 28% from top
for y in range(H):
    if y < gradient_start:
        # Soft top vignette
        t = y / gradient_start
        alpha = int(80 * (1 - t))
    else:
        # Bottom dark ramp
        t = (y - gradient_start) / (H - gradient_start)
        # Ease-in curve
        alpha = int(210 * (t ** 1.6))
    odraw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
draw   = ImageDraw.Draw(canvas)

# ── Domain pill (top center) ──────────────────────────────────────────────────
pill_pad_x, pill_pad_y = 22, 10
bbox = draw.textbbox((0, 0), DOMAIN, font=f_domain)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
pill_w = tw + pill_pad_x * 2
px = (W - pill_w) // 2
py = 36
pill_rect = [px, py, px + pill_w, py + th + pill_pad_y * 2]
draw.rounded_rectangle(pill_rect, radius=24, fill=(255, 255, 255), outline=None)
# Subtract bbox origin to correct for font bearing
draw.text((px + pill_pad_x - bbox[0], py + pill_pad_y - bbox[1]), DOMAIN, font=f_domain, fill=BLACK)

# ── Title (bottom-left, wrapped) ─────────────────────────────────────────────
MARGIN_L = 60
MARGIN_R = 60
MARGIN_B = 46
line_gap = 8
MAX_W    = W - MARGIN_L - MARGIN_R

# Auto-fit title font size so longest line fits
def fit_font(text_lines, font_path, index, max_w, start_size=68):
    size = start_size
    while size > 24:
        f = ImageFont.truetype(font_path, size, index=index)
        widths = [draw.textbbox((0,0), ln, font=f)[2] for ln in text_lines]
        if max(widths) <= max_w:
            return f, size
        size -= 2
    return ImageFont.truetype(font_path, size, index=index), size

f_title, _ = fit_font(TITLE.split("\n"), FONT, 1, MAX_W)

lines = TITLE.split("\n")
# measure block height
line_heights = []
for ln in lines:
    b = draw.textbbox((0, 0), ln, font=f_title)
    line_heights.append(b[3] - b[1])

stats_b    = draw.textbbox((0, 0), STATS, font=f_stats)
stats_h    = stats_b[3] - stats_b[1]
price_b    = draw.textbbox((0, 0), PRICE, font=f_price)
price_h    = price_b[3] - price_b[1]

block_h = (sum(line_heights)
           + line_gap * (len(lines) - 1)
           + 14 + price_h
           + 10 + stats_h)

y = H - MARGIN_B - block_h

# Stats (topmost in block)
draw.text((MARGIN_L, y), STATS, font=f_stats, fill=(220, 220, 220))
y += stats_h + 10

# Title lines
for i, ln in enumerate(lines):
    draw.text((MARGIN_L, y), ln, font=f_title, fill=WHITE)
    y += line_heights[i] + line_gap

y += 14
# Price in accent gold
draw.text((MARGIN_L, y), PRICE, font=f_price, fill=ACCENT)

# ── Save ──────────────────────────────────────────────────────────────────────
canvas.save(OUT, "JPEG", quality=92, optimize=True)
print(f"Saved → {OUT}  ({W}×{H})")

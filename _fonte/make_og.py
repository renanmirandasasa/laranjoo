"""Gera a imagem de prévia de link (1200x630) em entrega/laranjoo-site/og.jpg.
Uso: python3 -I make_og.py laranjoo.pages.dev"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_TEXT = sys.argv[1] if len(sys.argv) > 1 else "laranjoo.pages.dev"
W, H = 1200, 630

bg = Image.new("RGB", (W, H))
stops = [(0, (244, 56, 31)), (0.5, (246, 95, 29)), (1, (248, 129, 28))]
px = bg.load()
for y in range(H):
    for x in range(W):
        t = (x / W) * 0.7 + (y / H) * 0.3
        for i in range(len(stops) - 1):
            a, ca = stops[i]; b, cb = stops[i + 1]
            if a <= t <= b:
                k = (t - a) / (b - a)
                px[x, y] = tuple(int(ca[j] + (cb[j] - ca[j]) * k) for j in range(3))
                break
img = bg.convert("RGBA")
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
for (cx, cy, r, a) in [(1110, 40, 210, 40), (70, 600, 150, 32), (980, 560, 40, 52), (180, 90, 26, 48)]:
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, a))
img = Image.alpha_composite(img, ov)
cw, ch = 520, 360; cx0 = (W - cw) // 2; cy0 = 56
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((cx0, cy0 + 14, cx0 + cw, cy0 + ch + 14), 40, fill=(110, 25, 0, 90))
img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(18)))
card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(card).rounded_rectangle((cx0, cy0, cx0 + cw, cy0 + ch), 40, fill=(255, 255, 255, 255))
img = Image.alpha_composite(img, card)
logo = Image.open(os.path.join(ROOT, "brand", "logo.png")).convert("RGBA")
lh = 290; lw = int(logo.width * lh / logo.height)
logo = logo.resize((lw, lh), Image.LANCZOS)
img.alpha_composite(logo, ((W - lw) // 2, cy0 + (ch - lh) // 2))
dr = ImageDraw.Draw(img)
fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
fr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
t1 = "Gostou? Achou na Laranjoo!"
w1 = dr.textlength(t1, font=fb)
dr.text(((W - w1) / 2 + 2, 462 + 3), t1, font=fb, fill=(120, 30, 0, 110))
dr.text(((W - w1) / 2, 462), t1, font=fb, fill=(255, 255, 255, 255))
w2 = dr.textlength(SITE_TEXT, font=fr)
dr.text(((W - w2) / 2, 540), SITE_TEXT, font=fr, fill=(255, 255, 255, 225))
out = os.path.join(ROOT, "entrega", "laranjoo-site", "og.jpg")
img.convert("RGB").save(out, quality=88, optimize=True)
print("og.jpg gerado com", SITE_TEXT)

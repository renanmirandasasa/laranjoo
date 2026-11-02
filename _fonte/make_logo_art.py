"""Separa a logo (brand/logo.png) em sacola + letras e gera brand/logo-art.html,
um bloco com cada peça posicionada em % para animar separadamente sem mudar o desenho."""
import base64, io, os
from collections import deque
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(ROOT, "brand", "logo.png")).convert("RGBA")
rgba = np.asarray(im).copy()
A = rgba[..., 3]
H, W = A.shape

# linha vazia entre a sacola e o nome
rows = (A > 24).sum(axis=1)
split = next(y for y in range(int(H * 0.5), H) if rows[y] == 0)
WORD_TOP = split

# componentes conectados do nome (letras); o pingo do j junta com a letra abaixo
mask = A[WORD_TOP:, :] > 60
h, w = mask.shape
lab = np.zeros(mask.shape, int)
comps = []
n = 0
for y in range(h):
    for x in range(w):
        if mask[y, x] and not lab[y, x]:
            n += 1
            q = deque([(y, x)]); lab[y, x] = n; xs = []; ys = []
            while q:
                cy, cx = q.popleft(); xs.append(cx); ys.append(cy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; q.append((ny, nx))
            comps.append({"id": n, "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys), "size": len(xs)})
# junta componentes pequenos (pingo do j) ao componente cuja faixa de colunas contém o seu centro
big = [c for c in comps if c["size"] > 200]
small = [c for c in comps if c["size"] <= 200]
merge = {}
for s in small:
    cx = (s["x0"] + s["x1"]) / 2
    host = min(big, key=lambda b: 0 if b["x0"] <= cx <= b["x1"] else min(abs(cx - b["x0"]), abs(cx - b["x1"])))
    merge[s["id"]] = host["id"]
    host["x0"] = min(host["x0"], s["x0"]); host["x1"] = max(host["x1"], s["x1"])
for k, v in merge.items():
    lab[lab == k] = v
letters = sorted(big, key=lambda c: c["x0"])

# pixels semitransparentes da borda (antialias) vão para o rótulo mais próximo
word_alpha = A[WORD_TOP:, :] > 0
dist_lab = lab.copy()
q = deque([(y, x) for y in range(h) for x in range(w) if dist_lab[y, x]])
while q:
    cy, cx = q.popleft()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < h and 0 <= nx < w and word_alpha[ny, nx] and not dist_lab[ny, nx]:
            dist_lab[ny, nx] = dist_lab[cy, cx]; q.append((ny, nx))

def data_uri(arr):
    buf = io.BytesIO(); Image.fromarray(arr, "RGBA").save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def pct(v, total):
    return "%.4f%%" % (v / total * 100)

pieces = []
# sacola
bag = rgba[:WORD_TOP].copy()
ba = bag[..., 3] > 8
ys, xs = np.where(ba)
bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
pieces.append(("bag", bx0, by0, bx1 - bx0, by1 - by0, data_uri(bag[by0:by1, bx0:bx1])))
# letras (mesma faixa vertical para todas, assim a linha de base fica igual)
for i, c in enumerate(letters):
    sub = rgba[WORD_TOP:].copy()
    keep = dist_lab == c["id"]
    sub[..., 3] = np.where(keep, sub[..., 3], 0)
    x0, x1 = max(0, c["x0"] - 1), min(W, c["x1"] + 2)
    pieces.append(("ch", x0, WORD_TOP, x1 - x0, H - WORD_TOP, data_uri(sub[:, x0:x1])))

out = ['<span class="logo-art" role="img" aria-label="Laranjoo">']
li = 0
for kind, x, y, pw, ph, uri in pieces:
    style = "left:%s;top:%s;width:%s;height:%s" % (pct(x, W), pct(y, H), pct(pw, W), pct(ph, H))
    if kind == "bag":
        out.append('<img class="logo-bag" src="%s" alt="" style="%s">' % (uri, style))
    else:
        out.append('<img class="logo-ch" src="%s" alt="" style="%s;--i:%d">' % (uri, style, li))
        li += 1
out.append("</span>")
open(os.path.join(ROOT, "brand", "logo-art.html"), "w", encoding="utf-8").write("".join(out))
print("divisão na linha", WORD_TOP, "| letras:", li, "| tamanho %.0f KB" % (sum(len(p[5]) for p in pieces) / 1024))

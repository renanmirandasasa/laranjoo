import base64, glob, html, json, os, re, sys, unicodedata

D = sys.argv[1]      # pasta com products/*.json e config/site.json
IMG = sys.argv[2]    # pasta com as fotos <id>.jpg
TEMPLATE = sys.argv[3]
OUT = sys.argv[4]

HUES = [25, 215, 45, 335, 150, 265, 190, 10, 100, 300]

def slug(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "outros"

def js(obj):
    t = json.dumps(obj, ensure_ascii=False, indent=1)
    return t.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

prods = [json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(D, "products", "*.json"))]
prods.sort(key=lambda p: p.get("ordem", 0))

cfg_path = os.path.join(D, "config", "site.json")
cfg = json.load(open(cfg_path, encoding="utf-8")) if os.path.exists(cfg_path) else {}

cats, items, skipped = [], [], []
for p in prods:
    nome = (p.get("nome") or "").strip()
    link = (p.get("link") or "").strip()
    if not nome or not re.match(r"^https?://\S+$", link):
        skipped.append(nome or "(sem nome)")
        continue
    cname = (p.get("categoria") or "").strip() or "Outros"
    cid = slug(cname)
    if not any(c["id"] == cid for c in cats):
        cats.append({"id": cid, "nome": cname, "hue": HUES[len(cats) % len(HUES)]})
    img = None
    if p.get("imgId"):
        path = os.path.join(IMG, p["imgId"] + ".jpg")
        if os.path.exists(path):
            img = "data:image/jpeg;base64," + base64.b64encode(open(path, "rb").read()).decode()
    it = {"nome": nome, "completo": (p.get("completo") or nome).strip(), "cat": cid,
          "icon": p.get("icon") or "box", "destaque": bool(p.get("destaque")), "link": link}
    if isinstance(p.get("num"), (int, float)) and p["num"] > 0:
        it["num"] = int(p["num"])
    try:
        import datetime as _dt
        it["criado"] = int(_dt.datetime.fromisoformat(p["criadoEm"].replace("Z", "+00:00")).timestamp() * 1000)
    except Exception:
        pass
    if img:
        it["img"] = img
    items.append(it)

data = ("/* Gerado a partir do Painel do Catálogo. Para mudar produtos, edite no painel e peça ao Claude para publicar. */\n"
        "var CATEGORIES = " + js(cats) + ";\n"
        "var PRODUCTS = " + js(items) + ";\n"
        "var SOCIAL = " + js({"tiktok": (cfg.get("tiktok") or "").strip(), "instagram": (cfg.get("instagram") or "").strip()}) + ";\n\n")

s = open(TEMPLATE, encoding="utf-8").read()
s, n = re.subn(r"/\* ============ CONFIGURAÇÃO.*?(?=var GLYPHS)", lambda m: data, s, count=1, flags=re.S)
assert n == 1, "bloco de dados não encontrado"

bio = html.escape((cfg.get("bio") or "").strip())
if bio:
    s, n = re.subn(r'(<p class="bio" id="bio">).*?(</p>)', lambda m: m.group(1) + bio + m.group(2), s, count=1)
    assert n == 1

import datetime
def b64(path, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())
BRAND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand")
s = s.replace("__LOGO__", b64(os.path.join(BRAND, "logo.png"), "image/png"))
s = s.replace("__LOGOART__", open(os.path.join(BRAND, "logo-art.html"), encoding="utf-8").read())
s = s.replace("__TILE__", b64(os.path.join(BRAND, "tile.jpg"), "image/jpeg"))
s = s.replace("__UPDATED__", (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)).strftime("%d/%m/%Y"))
assert "__" not in re.sub(r"__[a-z]+__", "", s.replace("__LOGO__", "").replace("__TILE__", "").replace("__UPDATED__", "")) or True

open(OUT, "w", encoding="utf-8").write(s)
print("produtos:", len(items), "| com foto:", sum(1 for i in items if "img" in i),
      "| destaques:", sum(1 for i in items if i["destaque"]), "| categorias:", [c["nome"] for c in cats])
print("ignorados (sem nome ou link válido):", skipped)
print("tamanho do arquivo: %.0f KB" % (os.path.getsize(OUT) / 1024))

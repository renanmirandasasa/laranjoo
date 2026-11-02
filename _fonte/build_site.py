"""Gera a pasta e o zip para a Netlify a partir de catalogo.html (já construído).
Uso: python3 -I build_site.py
Imagens fixas (og.jpg, favicon.png, icon-192.png, apple-touch-icon.png) ficam em entrega/laranjoo-site/."""
import os, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "entrega", "laranjoo-site")
URL = "https://laranjoo.netlify.app/"
TITLE = "Laranjoo | Achados com link direto na Shopee"
DESC = "Gostou? Achou na Laranjoo! Os achados que aparecem nos vídeos, com link direto para a Shopee."

catalog = open(os.path.join(ROOT, "catalogo.html"), encoding="utf-8").read()
lines = catalog.split("\n")
assert lines[0].startswith("<title>") and "viewport-fit-sides" in lines[1], "início inesperado do catalogo.html"
body = "\n".join(lines[2:])

head = f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#F65F1D">
<link rel="canonical" href="{URL}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Laranjoo">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{URL}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{URL}og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Logo da Laranjoo com a frase Gostou? Achou na Laranjoo!">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{URL}og.jpg">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
'''
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(head + body + "\n</body>\n</html>\n")

zpath = os.path.join(ROOT, "entrega", "laranjoo-site.zip")
if os.path.exists(zpath):
    os.remove(zpath)
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(SITE)):
        z.write(os.path.join(SITE, f), "laranjoo-site/" + f)
print("site:", sorted(os.listdir(SITE)), "| zip: %d KB" % (os.path.getsize(zpath) // 1024))

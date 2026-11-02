# Fonte do catálogo Laranjoo

Arquivos usados para gerar o `index.html` da raiz. Não são publicados no site (bloqueados no `_redirects`).

- `catalogo.template.html`: modelo do catálogo (visual, animações, carrossel, busca por número, seção Siga, dúvidas).
- `build_catalogo.py`: monta o catálogo a partir dos dados do Painel do Catálogo
  (produtos em `products/*.json`, loja em `config/site.json`, fotos em `<imgId>.jpg`).
  Uso: `python3 -I build_catalogo.py <pasta-dados> <pasta-fotos> catalogo.template.html catalogo.html`
- `build_site.py`: acrescenta o cabeçalho (título, prévia de link, ícones) e gera `index.html`.
  Espera `catalogo.html` e `brand/` na mesma pasta, e as imagens fixas em `entrega/laranjoo-site/`.
- `make_og.py`: gera a imagem de prévia de link (`og.jpg`).
- `painel.html`: cópia do Painel do Catálogo (só funciona publicado no Claude, com banco de dados e fotos).
- `make_logo_art.py`: separa a logo em sacola + letras e gera `brand/logo-art.html` (usado pela animação de onda).
- `brand/`: logo sem fundo, ícone laranja e a logo separada em peças (`logo-art.html`).

Fluxo: cadastrar no painel → pedir ao Claude "publicar catálogo" → o Claude lê o painel, gera o
`index.html`, faz commit neste repositório e o Cloudflare Pages publica sozinho em laranjoo.pages.dev.

#!/usr/bin/env python3
"""Gera um artigo do blog e atualiza a lista do blog e o sitemap.
Uso (na raiz do repo): python3 ferramentas/publicar.py artigo.json
artigo.json = o campo "artigo" da entrega da mesa Blog & SEO (titulo, titulo_seo, descricao,
linha_fina, secao, leitura_min, palavra_chave, slug, corpo_html, faq). A data é a de hoje (São Paulo).
"""
import json, sys, os, re, datetime
sys.path.insert(0, os.path.dirname(__file__))
import gen

a = json.load(open(sys.argv[1]))
slug = re.sub(r"[^a-z0-9-]", "", (a.get("slug") or "").strip("/").split("/")[-1].lower())
if not slug:
    sys.exit("ERRO: artigo sem slug")
hoje = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)).date().isoformat()
p = dict(a, path=f"/blog/{slug}/", tipo="post", data=a.get("data") or hoje)
html = gen.gerar(p)
ruim = re.findall(r"\b(?:a|da|na|pela|à) Acelera Obra", re.sub(r"<[^>]+>", " ", p["corpo_html"]))
if ruim:
    sys.exit(f"ERRO: o texto usa {ruim[:3]} — o certo é 'o/do/no/pelo Acelera Obra'. Corrija antes de publicar.")
dest = f"conteudo/blog/{slug}/index.html"
novo = not os.path.exists(dest)
os.makedirs(os.path.dirname(dest), exist_ok=True)
open(dest, "w").write(html)

idx_path = "conteudo/blog/index.html"
idx = open(idx_path).read()
if f'href="/blog/{slug}/"' not in idx:
    card = f'''
        <li>
          <article class="cartao">
            <span class="cartao__categoria">{gen.esc(p.get("secao") or "Artigos")}</span>
            <h3 class="cartao__titulo"><a href="/blog/{slug}/">{gen.esc(p["titulo"])}</a></h3>
            <p class="cartao__resumo">{gen.esc(p.get("linha_fina") or p.get("descricao") or "")}</p>
            <p class="cartao__meta"><time datetime="{p["data"]}">{gen.data_br(p["data"])}</time> · {p.get("leitura_min", 5)} min de leitura</p>
          </article>
        </li>
'''
    marca = '<ul class="lista__grade">\n'
    assert marca in idx, "lista do blog não encontrada"
    idx = idx.replace(marca, marca + card, 1)
    open(idx_path, "w").write(idx)

sm_path = "conteudo/sitemap.xml"
sm = open(sm_path).read()
loc = f"https://aceleraobra.com.br/blog/{slug}/"
if loc not in sm:
    sm = sm.replace("</urlset>", f"  <url><loc>{loc}</loc><lastmod>{p['data']}</lastmod></url>\n</urlset>")
    sm = re.sub(r"(<loc>https://aceleraobra.com.br/blog/</loc><lastmod>)[^<]*", r"\g<1>" + p["data"], sm)
    open(sm_path, "w").write(sm)
print(json.dumps({"slug": slug, "url": loc, "arquivo": dest, "novo": novo, "data": p["data"]}))

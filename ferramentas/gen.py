#!/usr/bin/env python3
"""Gera páginas do blog da Acelera Obra no mesmo padrão do site (aceleraobra.com.br/blog/).
Uso: python3 gen.py pagina.json  -> grava out/<path>/index.html
JSON: {path:"/blog/slug/", tipo:"post"|"pilar", titulo, titulo_seo, descricao, linha_fina,
       secao (trilha), data:"AAAA-MM-DD", leitura_min, corpo_html, faq:[{p,r}], palavra_chave}
"""
import json, sys, os, html, datetime

BASE = "https://aceleraobra.com.br"
LOGO = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.svg")).read()
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
SETA = '<svg class="botao__seta" width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m0 0-6-6m6 6-6 6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'

ORG = {"@type": "ProfessionalService", "@id": BASE + "/#acelera-obra", "name": "Acelera Obra",
       "url": BASE + "/",
       "description": "Assessoria de marketing e vendas exclusiva para lojas de material de construção, lojas de tintas, home centers, material elétrico e hidráulico.",
       "areaServed": {"@type": "Country", "name": "Brasil"},
       "knowsAbout": ["marketing para loja de material de construção", "marketing para loja de tintas",
                      "tráfego pago para varejo de construção", "CRM para loja de material de construção",
                      "treinamento de vendedores de balcão", "calendário promocional do varejo de construção"],
       "slogan": "Feito por quem vive o balcão"}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def data_br(d):
    y, m, dd = map(int, d.split("-"))
    return f"{dd} de {MESES[m-1]} de {y}"


import re as _re

ESTILO_POST = """<style>
.post-hero{background:#212721;color:#fff;padding:56px 0 48px;position:relative;overflow:hidden}
.post-hero:after{content:"";position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(255,205,0,.22),rgba(255,205,0,0) 70%)}
.post-hero .post__coluna{position:relative;z-index:1}
.post-hero .trilha,.post-hero .trilha a{color:rgba(255,255,255,.65)}
.post-hero .post__titulo{color:#fff}
.post-hero .post__linha-fina{color:rgba(255,255,255,.82)}
.post-hero .post__meta{color:rgba(255,255,255,.6);border-color:rgba(255,255,255,.14)}
.post-hero .post__meta strong,.post-hero .post__meta b{color:#FFCD00}
.post-hero__selo{display:inline-block;background:#FFCD00;color:#212721;font-weight:800;font-size:12px;letter-spacing:.08em;text-transform:uppercase;padding:6px 12px;border-radius:999px;margin-bottom:18px}
.post--corpo{padding-top:40px}
.indice{background:#F6F5F1;border-radius:16px;padding:20px 22px;margin:0 0 32px}
.indice__rotulo{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#8a7400;margin:0 0 10px}
.indice ol{margin:0;padding-left:20px}.indice li{margin:6px 0}.indice a{color:#212721;text-decoration:none;border-bottom:1px solid #FFCD00}
.prosa h2{scroll-margin-top:90px}
.pergunta{border:1px solid #E7E5DE;border-radius:18px;padding:22px 22px 18px;margin:20px 0;background:#fff;box-shadow:0 2px 10px rgba(33,39,33,.05)}
.pergunta h3{display:flex;gap:14px;align-items:flex-start;margin:0 0 14px!important}
.pergunta__num{flex:0 0 38px;height:38px;border-radius:10px;background:#FFCD00;color:#212721;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:18px}
.pergunta__lados{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.lado{border-radius:12px;padding:12px 14px;font-size:15px;line-height:1.5}
.lado p{margin:0!important}
.lado__rot{display:block;font-size:11.5px;font-weight:800;letter-spacing:.07em;text-transform:uppercase;margin-bottom:4px}
.lado--ok{background:#EEF6EC}.lado--ok .lado__rot{color:#2E7D32}
.lado--alerta{background:#FDF0EC}.lado--alerta .lado__rot{color:#C0392B}
.comparativo{width:100%;border-collapse:separate;border-spacing:0;margin:20px 0;font-size:15px;border:1px solid #E7E5DE;border-radius:16px;overflow:hidden}
.comparativo th,.comparativo td{padding:12px 14px;text-align:left;vertical-align:top;border-bottom:1px solid #E7E5DE}
.comparativo tr:last-child td{border-bottom:0}
.comparativo thead th{background:#212721;color:#fff;font-size:13px;letter-spacing:.04em}
.comparativo thead th:last-child{background:#FFCD00;color:#212721}
.comparativo td:first-child{font-weight:700;background:#F6F5F1;width:24%}
.comparativo td:last-child{background:#FFFBEA}
.passos{list-style:none;padding:0!important;margin:20px 0;border-left:3px solid #FFCD00}
.passos li{position:relative;padding:4px 0 16px 22px;margin:0!important}
.passos li:before{content:"";position:absolute;left:-9px;top:9px;width:15px;height:15px;border-radius:50%;background:#212721;border:3px solid #FFCD00}
.passos strong{display:inline-block;background:#212721;color:#FFCD00;border-radius:999px;padding:2px 10px;font-size:13px;margin-right:6px}
.destaque{border:2px solid #FFCD00!important;background:#FFFBEA!important}
.faq-item{border:1px solid #E7E5DE;border-radius:14px;margin:10px 0;padding:0 18px;background:#fff}
.faq-item summary{cursor:pointer;font-weight:700;padding:16px 0;list-style:none;display:flex;justify-content:space-between;gap:12px}
.faq-item summary::-webkit-details-marker{display:none}
.faq-item summary:after{content:"+";font-weight:800;color:#212721;background:#FFCD00;border-radius:8px;min-width:26px;height:26px;display:flex;align-items:center;justify-content:center}
.faq-item[open] summary:after{content:"–"}
.faq-item p{margin:0 0 16px!important}
@media (max-width:640px){.pergunta__lados{grid-template-columns:1fr}.post-hero{padding:40px 0 34px}.comparativo{font-size:14px}.comparativo td:first-child{width:30%}}
</style>"""

def _slugid(t):
    import unicodedata
    t=unicodedata.normalize("NFKD",_re.sub("<[^>]+>","",t)).encode("ascii","ignore").decode().lower()
    return _re.sub("[^a-z0-9]+","-",t).strip("-")[:60]

def _cap(x):
    x=x.strip()
    return x[:1].upper()+x[1:] if x else x

def realcar(corpo):
    """Transforma padrões do texto em blocos visuais. Não muda o conteúdo."""
    # 1) Pergunta numerada + Preparo/Alerta -> cartão
    pat=_re.compile(r'<h3>(\d+)\.\s*(.*?)</h3>\s*<p><strong>([^<]*preparo[^<]*)</strong>\s*(.*?)</p>\s*<p><strong>([^<]*alerta[^<]*)</strong>\s*(.*?)</p>', _re.S|_re.I)
    def card(m):
        return (f'<div class="pergunta"><h3><span class="pergunta__num">{m.group(1)}</span><span>{m.group(2)}</span></h3>'
                f'<div class="pergunta__lados"><div class="lado lado--ok"><span class="lado__rot">✓ Resposta que mostra preparo</span><p>{_cap(m.group(4))}</p></div>'
                f'<div class="lado lado--alerta"><span class="lado__rot">⚠ Sinal de alerta</span><p>{_cap(m.group(6))}</p></div></div></div>')
    corpo=pat.sub(card,corpo)
    # 2) Lista "<strong>Item:</strong> a generalista ...; a de nicho ..." -> tabela
    def tabela(m):
        itens=_re.findall(r'<li><strong>(.*?):?</strong>:?\s*(.*?);\s*(.*?)</li>',m.group(1),_re.S)
        if len(itens)<3: return m.group(0)
        limpa=lambda x:_re.sub(r'^(a|o)\s+(generalista|de nicho|assessoria de nicho|agência generalista)\s*','',x.strip(),flags=_re.I)
        linhas="".join(f'<tr><td>{a.rstrip(":")}</td><td>{_cap(limpa(b)) or b}</td><td>{_cap(limpa(c)) or c}</td></tr>' for a,b,c in itens)
        return f'<table class="comparativo"><thead><tr><th></th><th>Agência generalista</th><th>Assessoria de nicho</th></tr></thead><tbody>{linhas}</tbody></table>'
    corpo=_re.sub(r'<ul>((?:\s*<li><strong>[^<]*</strong>[^<]*generalista[^;]*;[^<]*</li>)+\s*)</ul>',tabela,corpo,flags=_re.S|_re.I)
    # 3) Lista ordenada com "Minutos"/"Passo"/"Dia" -> linha do tempo
    corpo=_re.sub(r'<ol>(\s*<li><strong>(?:Minutos?|Passo|Dia|Semana|Etapa)[^<]*</strong>.*?)</ol>',lambda m:'<ol class="passos">'+m.group(1)+'</ol>',corpo,flags=_re.S)
    # 4) ids nos h2 + índice
    h2s=[]
    def ancora(m):
        i=_slugid(m.group(1)); h2s.append((i,_re.sub("<[^>]+>","",m.group(1))))
        return f'<h2 id="{i}">{m.group(1)}</h2>'
    corpo=_re.sub(r'<h2>(.*?)</h2>',ancora,corpo)
    indice=""
    if len(h2s)>=3:
        indice='<nav class="indice" aria-label="Neste artigo"><p class="indice__rotulo">Neste artigo</p><ol>'+"".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i,t in h2s)+'</ol></nav>'
    return indice+corpo


def gerar(p):
    url = BASE + p["path"]
    titulo = p["titulo"]
    seo = p.get("titulo_seo") or titulo
    desc = p["descricao"]
    data = p.get("data") or datetime.date.today().isoformat()
    pilar = p.get("tipo") == "pilar"
    trilha_nome = p.get("secao", "Artigos")
    graph = []
    if pilar:
        graph.append(ORG)
        graph.append({"@type": "WebPage", "@id": url, "url": url, "name": seo, "description": desc,
                      "inLanguage": "pt-BR", "about": {"@id": BASE + "/#acelera-obra"},
                      "dateModified": data})
        graph.append({"@type": "Service", "name": p.get("servico", titulo), "serviceType": p.get("servico", titulo),
                      "provider": {"@id": BASE + "/#acelera-obra"}, "areaServed": {"@type": "Country", "name": "Brasil"},
                      "audience": {"@type": "BusinessAudience", "audienceType": p.get("publico", "Donos de lojas de material de construção")},
                      "url": url, "description": desc})
    else:
        graph.append({"@type": "BlogPosting", "headline": titulo, "description": desc, "datePublished": data,
                      "dateModified": data, "inLanguage": "pt-BR", "mainEntityOfPage": url,
                      "keywords": p.get("palavra_chave", ""),
                      "author": {"@type": "Organization", "name": "Equipe Acelera Obra", "url": BASE},
                      "publisher": {"@type": "Organization", "name": "Acelera Obra", "url": BASE}})
    itens = [{"@type": "ListItem", "position": 1, "name": "Início", "item": BASE + "/"}]
    if not pilar:
        itens.append({"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + "/blog/"})
    itens.append({"@type": "ListItem", "position": len(itens) + 1, "name": titulo})
    graph.append({"@type": "BreadcrumbList", "itemListElement": itens})
    faq = p.get("faq") or []
    faq_html = ""
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["p"], "acceptedAnswer": {"@type": "Answer", "text": f["r"]}} for f in faq]})
        if pilar:
            faq_html = '\n          <h2 id="perguntas-frequentes">Perguntas frequentes</h2>\n' + "".join(
                f'          <h3>{esc(f["p"])}</h3>\n          <p>{esc(f["r"])}</p>\n' for f in faq)
        else:
            faq_html = '\n          <h2 id="perguntas-frequentes">Perguntas frequentes</h2>\n' + "".join(
                f'          <details class="faq-item"><summary>{esc(f["p"])}</summary><p>{esc(f["r"])}</p></details>\n' for f in faq)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    trilha = '<li><a href="/">Início</a></li>' + ('' if pilar else '<li><a href="/blog/">Blog</a></li>') + \
        f'<li><span aria-current="page">{esc(trilha_nome)}</span></li>'
    meta_linha = (f'<span>Por <strong>Equipe Acelera Obra</strong></span>\n          '
                  f'<span>{"Atualizado em " if pilar else ""}<time datetime="{data}">{data_br(data)}</time></span>\n          '
                  f'<span>{p.get("leitura_min", 5)} min de leitura</span>')
    _cab = f'''
        <nav aria-label="Você está em">
          <ol class="trilha">
            {trilha}
          </ol>
        </nav>
{"" if pilar else f'        <span class="post-hero__selo">{esc(trilha_nome)}</span>'}
        <h1 class="post__titulo">{esc(titulo)}</h1>
        <p class="post__linha-fina">{esc(p.get("linha_fina", ""))}</p>

        <p class="post__meta">
          {meta_linha}
        </p>
'''
    cabeca_pilar = _cab
    cabeca_post = "" if pilar else f'''  <section class="post-hero">
    <div class="envelope">
      <div class="post__coluna">
{_cab}
      </div>
    </div>
  </section>
'''
    voltar = '' if pilar else f'''
        <p class="post__voltar">
          <a href="/blog/">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M19 12H5m0 0 6 6m-6-6 6-6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            Ver todos os artigos
          </a>
        </p>
'''
    chamada = f'''
          <aside class="chamada" aria-label="Análise gratuita">
            <p class="chamada__titulo">{esc(p.get("chamada_titulo", "Quer ajuda para aplicar isso na sua loja?"))}</p>
            <p>{esc(p.get("chamada_texto", "Solicite uma análise gratuita. A gente olha a sua loja e mostra por onde começar."))}</p>
            <a class="botao botao--peq" href="/#diagnostico">
              Solicite sua análise gratuita
              {SETA}
            </a>
          </aside>
'''
    corpo = p["corpo_html"].replace("<!--CHAMADA-->", chamada)
    if "<!--CHAMADA-->" not in p["corpo_html"]:
        corpo += chamada
    if not pilar:
        corpo = realcar(corpo)
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

<title>{esc(seo)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#212721">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{url}">

<meta property="og:type" content="{"website" if pilar else "article"}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Acelera Obra">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(p.get("linha_fina") or desc)}">
<meta property="og:url" content="{url}">
{"" if pilar else f'<meta property="article:published_time" content="{data}">'}
<meta name="twitter:card" content="summary_large_image">

<link rel="preload" href="/assets/fonts/poppins-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/poppins-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/blog/estilo.css">
{"" if pilar else ESTILO_POST}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23212721'/%3E%3Cpath d='M7 26 L14.2 6 h3.6 L25 26 h-5.1 l-1.5-4.6 h-4.8 L12.1 26 Z M14.8 17.6 h2.4 L16 13.4 Z' fill='%23FFCD00'/%3E%3C/svg%3E">

<script type="application/ld+json">
{ld}
</script>

<!-- Meta Pixel Code — o mesmo da LP, para o blog entrar no remarketing -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '1337747291607929');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=1337747291607929&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
</head>
<body>

{LOGO}

<div class="progresso" aria-hidden="true"><div class="progresso__barra" id="progresso"></div></div>

<header class="cabecalho">
  <div class="envelope cabecalho__linha">
    <a class="cabecalho__marca" href="/" aria-label="Acelera Obra, página inicial">
      <svg class="cabecalho__logo" viewBox="0 0 600 153" role="img" aria-label="Acelera Obra"><use href="#logo"/></svg>
    </a>
    <div class="cabecalho__acoes">
      <a class="cabecalho__link" href="/blog/">Blog</a>
      <a class="botao botao--peq" href="/#diagnostico">
        <span class="cabecalho__cta-longo">Solicite sua análise gratuita</span>
        <span class="cabecalho__cta-curto">Análise gratuita</span>
        {SETA}
      </a>
    </div>
  </div>
</header>

<main>
{cabeca_post}  <article class="post{"" if pilar else " post--corpo"}">
    <div class="envelope">
      <div class="post__coluna">
{"" if not pilar else cabeca_pilar}
        <div class="prosa">
{corpo}{faq_html}
        </div>
{voltar}
      </div>
    </div>
  </article>

  <section class="fechamento">
    <div class="envelope">
      <p class="olho">Análise gratuita</p>
      <h2 class="titulo">Cresça com quem realmente vive o <span class="marca-texto">varejo de construção</span></h2>
      <p class="fechamento__corpo">A análise é gratuita e leva menos de 1 minuto pra solicitar. A gente olha a sua loja e mostra onde está o dinheiro parado.</p>
      <a class="botao" href="/#diagnostico">
        Solicite sua análise gratuita
        <svg class="botao__seta" width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m0 0-6-6m6 6-6 6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </a>
      <p class="fechamento__nota">Análise gratuita • sem compromisso</p>
    </div>
  </section>
</main>

<footer class="rodape">
  <div class="envelope">
    <div class="rodape__topo">
      <a class="rodape__marca" href="/" aria-label="Acelera Obra, página inicial">
        <svg class="rodape__logo" viewBox="0 0 600 153" role="img" aria-label="Acelera Obra"><use href="#logo"/></svg>
      </a>
      <nav class="rodape__nav" aria-label="Rodapé">
        <a class="rodape__link" href="/">Início</a>
        <a class="rodape__link" href="/blog/">Blog</a>
        <a class="rodape__link" href="/assessoria-de-marketing-para-loja-de-material-de-construcao/">Assessoria para material de construção</a>
        <a class="rodape__link" href="/marketing-para-loja-de-tintas/">Marketing para loja de tintas</a>
        <a class="rodape__link" href="/#diagnostico">Análise gratuita</a>
      </nav>
    </div>
    <div class="rodape__base">
      <span>© 2026 Acelera Obra. Todos os direitos reservados.</span>
      <a class="rodape__link" style="font-size:12.5px" href="/privacidade">Política de Privacidade</a>
    </div>
  </div>
</footer>

<script>
/* Barra de progresso de leitura */
(function () {{
  var barra = document.getElementById('progresso'), pendente = false;
  function aoRolar() {{
    var altura = document.documentElement.scrollHeight - window.innerHeight;
    barra.style.width = (altura > 0 ? window.scrollY / altura * 100 : 0).toFixed(2) + '%';
    pendente = false;
  }}
  window.addEventListener('scroll', function () {{
    if (!pendente) {{ pendente = true; requestAnimationFrame(aoRolar); }}
  }}, {{ passive: true }});
  aoRolar();
}})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    for f in sys.argv[1:]:
        p = json.load(open(f))
        dest = os.path.join(os.path.dirname(__file__), "out", p["path"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w").write(gerar(p))
        print("ok", dest)

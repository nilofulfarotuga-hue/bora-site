#!/usr/bin/env python3
"""Base do gerador do bora-site: dados do Supabase + peças de HTML.

Os renderizadores e o main vivem em `gerar_paginas.py`.

ORIGINAL:

Um parceiro novo entra no site correndo isto — não à mão.

O que faz:
  1. lê `restaurants` e `service_providers` aprovados (leitura pública)
  2. escreve `dados/parceiros.json` (a fonte que as páginas usam)
  3. gera `loja/<slug>.html` — uma por PARCEIRO REAL
  4. gera as páginas de categoria: viagens, entregas, beleza, festas, mais
  5. gera `ser-parceiro.html`

O que NÃO faz, de propósito:
  - não toca em `index.html`, `privacidade.html` nem `termos.html`
  - não inventa história, preço, horário nem avaliação. O que não estiver na
    base não aparece na página.

Chaves: SUPABASE_URL e SUPABASE_ANON_KEY do ambiente; se faltarem, lê o
`.dart_defines` do repo da app. A anon key é pública por desenho (vai no
bundle web), mas mesmo assim não fica escrita aqui.

Uso:
    python gerar_paginas.py            # gera tudo
    python gerar_paginas.py --so-dados # só o JSON, para inspecção
"""
import html
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
DEFINES_FALLBACK = os.path.join(
    RAIZ, "..", "projetosflutter", "bora_app", ".dart_defines")

SITE = "https://boraguarda.com"
APP = "https://app.boraguarda.com"
PLAY = "https://play.google.com/store/apps/details?id=pt.boraapp.bora"
EMAIL = "boraappbora@gmail.com"
TELEFONE = "+351937501673"

VERDE = "#16A34A"
LARANJA = "#F97316"

# Mini-sites já publicados (confirmados a 200 antes de entrarem na página).
MINISITES = {
    "barbearia ouro e prata": "https://ouroeprata.boraguarda.com/",
    "mr kebab & restaurant": "https://mrkebab.boraguarda.com/",
}

CATEGORIAS = {
    "viagens": {
        "titulo": "Bora Motorista",
        "chapeu": "Viagens",
        "frase": "Preço fechado antes de entrares no carro.",
        "emoji": "🚗",
    },
    "entregas": {
        "titulo": "Entregas",
        "chapeu": "Restaurantes e mercados",
        "frase": "Os supermercados e os restaurantes da cidade, à tua porta.",
        "emoji": "🛵",
    },
    "beleza": {
        "titulo": "Beleza e Serviços",
        "chapeu": "Marcações",
        "frase": "Marcas a tua hora e ela fica guardada.",
        "emoji": "✂️",
    },
    "festas": {
        "titulo": "Festas",
        "chapeu": "Em breve",
        "frase": "Bolos, salgados, docinhos e decoração, com data marcada.",
        "emoji": "🎂",
    },
    "mais": {
        "titulo": "E ainda",
        "chapeu": "Farmácia, lojas, limpeza e favores",
        "frase": "Quando não podes ir, alguém vai por ti.",
        "emoji": "🤝",
    },
}


# ───────────────────────── dados ─────────────────────────

def chaves():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if url and key:
        return url.rstrip("/"), key
    if os.path.exists(DEFINES_FALLBACK):
        d = {}
        with open(DEFINES_FALLBACK, encoding="utf-8-sig") as fh:
            for linha in fh:
                if "=" in linha and not linha.strip().startswith("#"):
                    k, v = linha.split("=", 1)
                    d[k.strip()] = v.strip().strip('"')
        if d.get("SUPABASE_URL") and d.get("SUPABASE_ANON_KEY"):
            return d["SUPABASE_URL"].rstrip("/"), d["SUPABASE_ANON_KEY"]
    sys.exit("Faltam SUPABASE_URL e SUPABASE_ANON_KEY (ambiente ou .dart_defines).")


URL, ANON = chaves()


def rest(caminho):
    req = urllib.request.Request(
        URL + "/rest/v1/" + caminho,
        headers={"apikey": ANON, "Authorization": "Bearer " + ANON})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def contar(caminho):
    """Total exato via PostgREST (Content-Range), sem trazer as linhas todas."""
    req = urllib.request.Request(
        URL + "/rest/v1/" + caminho,
        headers={"apikey": ANON, "Authorization": "Bearer " + ANON,
                 "Prefer": "count=exact"})
    with urllib.request.urlopen(req, timeout=120) as r:
        r.read()
        total = r.headers.get("Content-Range", "").split("/")[-1]
        return int(total) if total.isdigit() else 0


def slug(texto):
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "sem-nome"


def recolher():
    lojas = rest(
        "restaurants?approval_status=eq.approved&select=id,name,category,"
        "extra_categories,address,phone,whatsapp,photo_url,hero_image_url,"
        "about_text,social_instagram,social_facebook,coming_soon,"
        "coming_soon_text,is_partner,business_hours,lat,lng&order=name")
    provedores = rest(
        "service_providers?approval_status=eq.approved&select=id,name,category,"
        "description,address,phone,photo_url,hero_image_url,about_text,"
        "gallery_urls,social_instagram,social_facebook,coming_soon,"
        "coming_soon_text,business_hours,lat,lng&order=name")

    for p in provedores:
        p["servicos"] = rest(
            "provider_services?provider_id=eq.%s&is_active=eq.true"
            "&select=name,description,price_cents,duration_minutes&order=price_cents"
            % urllib.parse.quote(p["id"]))

    for l in lojas:
        l["n_produtos"] = contar(
            "products?restaurant_id=eq.%s&select=id&limit=1"
            % urllib.parse.quote(l["id"]))
        # amostra: só parceiros levam vitrine de produtos na página
        l["amostra"] = rest(
            "products?restaurant_id=eq.%s&is_available=eq.true"
            "&select=name,price,photo_url,category&order=name&limit=8"
            % urllib.parse.quote(l["id"])) if l.get("is_partner") else []
        l["slug"] = slug(l["name"])
    for p in provedores:
        p["slug"] = slug(p["name"])
    return {"lojas": lojas, "provedores": provedores}


# ───────────────────────── html ─────────────────────────

def e(t):
    return html.escape(str(t or ""), quote=True)


def cabeca(titulo, descricao, caminho, imagem=None, extra=""):
    """<head> completo, com cartão de partilha (é para WhatsApp que isto vai)."""
    # A história de um parceiro vem com quebras de linha; dentro de um
    # content="..." isso parte o atributo e o scraper perde a descrição.
    descricao = " ".join(str(descricao or "").split())
    titulo = " ".join(str(titulo or "").split())
    img = imagem or (SITE + "/assets/img/og-image.png")
    if not img.startswith("http"):
        img = SITE + "/" + img.lstrip("/")
    url = SITE + caminho
    return f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{e(url)}">
<meta name="theme-color" content="#0B0F0D">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_PT">
<meta property="og:site_name" content="Bora">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(img)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titulo)}">
<meta name="twitter:description" content="{e(descricao)}">
<meta name="twitter:image" content="{e(img)}">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/bora.css">
{extra}
</head>
<body>
"""


def topo():
    return f"""<header class="topo">
  <a class="marca" href="/">
    <img src="/assets/img/bora_logo.png" alt="Bora" width="40" height="40">
    <span>Bora</span>
  </a>
  <nav class="menu">
    <a href="/viagens">Viagens</a>
    <a href="/entregas">Entregas</a>
    <a href="/beleza">Beleza</a>
    <a href="/festas">Festas</a>
    <a href="/mais">E ainda</a>
    <a href="/ser-parceiro">Ser parceiro</a>
  </nav>
  <a class="btn btn-p pequeno" href="{PLAY}" rel="noopener">Instalar</a>
</header>
"""


def migalhas(itens):
    partes = []
    for i, (nome, href) in enumerate(itens):
        if href and i < len(itens) - 1:
            partes.append(f'<a href="{e(href)}">{e(nome)}</a>')
        else:
            partes.append(f"<span>{e(nome)}</span>")
    return '<nav class="migalhas">' + '<i>›</i>'.join(partes) + "</nav>"


def saidas(voltar_nome, voltar_href, cta_nome, cta_href):
    """Nunca um beco: ao fundo há sempre por onde ir."""
    return f"""<section class="saidas">
  <div class="wrap saidas-in">
    <a class="btn btn-s" href="{e(voltar_href)}">← {e(voltar_nome)}</a>
    <a class="btn btn-p" href="{e(cta_href)}" rel="noopener">{e(cta_nome)}</a>
  </div>
</section>
"""


def rodape():
    return f"""<footer class="rodape">
  <div class="wrap">
    <div class="rod-grelha">
      <div>
        <div class="rod-t">O que dá para pedir</div>
        <a href="/viagens">Viagens</a>
        <a href="/entregas">Entregas</a>
        <a href="/beleza">Beleza e serviços</a>
        <a href="/festas">Festas</a>
        <a href="/mais">Farmácia, limpeza, favores</a>
      </div>
      <div>
        <div class="rod-t">Trabalhar com o Bora</div>
        <a href="/ser-parceiro">Pôr o meu negócio</a>
        <a href="/parceiros.html">Parceiros</a>
        <a href="/estafetas.html">Estafetas</a>
      </div>
      <div>
        <div class="rod-t">Ajuda</div>
        <a href="/faq.html">Perguntas frequentes</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <a href="tel:{TELEFONE}">{TELEFONE}</a>
      </div>
      <div>
        <div class="rod-t">Legal</div>
        <a href="/privacidade.html">Privacidade</a>
        <a href="/termos.html">Termos</a>
      </div>
    </div>
    <div class="rod-fim">© 2026 Bora · Guarda, Portugal</div>
  </div>
</footer>
<script src="/assets/js/bora-anim.js" defer></script>
</body>
</html>
"""


def dois_botoes(tipo, ident, verbo):
    """Os dois caminhos, com o mesmo peso: quem tem a app e quem não tem."""
    destino = f"{APP}/#/{tipo}/{urllib.parse.quote(str(ident))}"
    return f"""<div class="pedir">
  <a class="btn btn-p" href="{e(destino)}" rel="noopener">Tenho a app · {e(verbo)}</a>
  <a class="btn btn-s" href="{PLAY}" rel="noopener">Não tenho · instalar</a>
  <p class="pedir-nota">ou <a href="{e(destino)}" rel="noopener">pede pelo site sem instalar nada</a></p>
</div>
"""

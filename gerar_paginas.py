#!/usr/bin/env python3
"""Gera as páginas do bora-site a partir do Supabase.

Um parceiro novo entra no site correndo isto — não à mão.

  1. lê `restaurants` e `service_providers` aprovados (leitura pública)
  2. escreve `dados/parceiros.json`
  3. gera `loja/<slug>.html` — uma por PARCEIRO REAL
  4. gera as categorias: viagens, entregas, beleza, festas, mais
  5. gera `ser-parceiro.html`

O que NÃO faz, de propósito:
  - não toca em `index.html`, `privacidade.html` nem `termos.html`
  - não inventa história, preço, horário nem avaliação. O que não estiver na
    base não aparece.

Uso:
    python gerar_paginas.py
    python gerar_paginas.py --so-dados
"""
import json
import os
import re
import sys
import urllib.parse

from site_base import (
    APP, CATEGORIAS, EMAIL, MINISITES, PLAY, RAIZ, SITE,
    cabeca, dois_botoes, e, migalhas, recolher, rodape, saidas, topo,
)


# ───────────────────────── peças ─────────────────────────

def bloco_foto(url, alt, classe="capa-img"):
    """Sem foto não se inventa: fica um espaço tratado, não uma imagem falsa."""
    if url:
        return f'<img class="{classe}" src="{e(url)}" alt="{e(alt)}" loading="lazy">'
    inicial = e((alt or "?")[:1].upper())
    return (f'<div class="{classe} sem-foto" role="img" aria-label="{e(alt)}">'
            f'<span>{inicial}</span></div>')


def selo_em_breve(item):
    if not item.get("coming_soon"):
        return ""
    txt = (item.get("coming_soon_text")
           or "Ainda não dá para pedir aqui — estamos a preparar com a casa.")
    return f'<div class="embreve"><span class="selo">Em breve</span><p>{e(txt)}</p></div>'


def redes(item):
    ig, fb = item.get("social_instagram"), item.get("social_facebook")
    if not ig and not fb:
        return ""
    out = ['<div class="redes">']
    if ig:
        href = ig if str(ig).startswith("http") else "https://instagram.com/" + str(ig).lstrip("@")
        out.append(f'<a href="{e(href)}" rel="noopener">Instagram</a>')
    if fb:
        href = fb if str(fb).startswith("http") else "https://facebook.com/" + str(fb)
        out.append(f'<a href="{e(href)}" rel="noopener">Facebook</a>')
    out.append("</div>")
    return "".join(out)


def horario(item):
    bh = item.get("business_hours")
    if not isinstance(bh, dict) or not bh:
        return ""
    dias = [("mon", "Segunda"), ("tue", "Terça"), ("wed", "Quarta"),
            ("thu", "Quinta"), ("fri", "Sexta"), ("sat", "Sábado"), ("sun", "Domingo")]
    linhas = []
    for chave, nome in dias:
        v = bh.get(chave) or bh.get(nome.lower())
        if not v:
            continue
        if isinstance(v, dict):
            ab = v.get("open") or v.get("from")
            fe = v.get("close") or v.get("to")
            if v.get("closed") or not ab or not fe:
                linhas.append(f"<li><b>{nome}</b><span>Fechado</span></li>")
            else:
                linhas.append(f"<li><b>{nome}</b><span>{e(ab)} – {e(fe)}</span></li>")
        elif isinstance(v, str):
            linhas.append(f"<li><b>{nome}</b><span>{e(v)}</span></li>")
    if not linhas:
        return ""
    return ('<div class="cartao"><h3>Horário</h3><ul class="horario">'
            + "".join(linhas) + "</ul></div>")


O_QUE = {"barbershop": "Barbearia", "beauty": "Beleza e estética",
         "restaurant": "Restaurante", "supermarket": "Supermercado",
         "store": "Loja", "pharmacy": "Farmácia"}


# ───────────────────────── página de parceiro ─────────────────────────

def pagina_parceiro(item, tipo):
    """tipo: 'loja' (restaurants) ou 'servico' (service_providers)."""
    nome = item["name"]
    verbo = "Marcar" if tipo == "servico" else "Pedir"
    cat_href = "/beleza" if tipo == "servico" else "/entregas"
    cat_nome = "Beleza e Serviços" if tipo == "servico" else "Entregas"
    foto = item.get("hero_image_url") or item.get("photo_url")
    o_que = O_QUE.get(item.get("category"), "")
    resumo = (item.get("about_text") or item.get("description")
              or f"{nome}, na Guarda. {verbo} pelo Bora.")

    p = [cabeca(f"{nome} — {o_que or 'no Bora'} na Guarda",
                resumo[:180], f"/loja/{item['slug']}", foto),
         topo(), "<main>", '<div class="wrap">',
         migalhas([("Início", "/"), (cat_nome, cat_href), (nome, None)]),
         "</div>"]

    chapeu = f'<div class="chapeu">{e(o_que)}</div>' if o_que else ""
    morada = f'<p class="morada">{e(item.get("address"))}</p>' if item.get("address") else ""
    p.append(f"""<section class="capa">
  <div class="wrap capa-in">
    <div class="capa-txt">
      {chapeu}
      <h1>{e(nome)}</h1>
      {morada}
      {selo_em_breve(item)}
      {dois_botoes(tipo, item['id'], verbo)}
    </div>
    <div class="capa-foto">{bloco_foto(foto, nome)}</div>
  </div>
</section>""")

    p.append('<div class="wrap conteudo">')

    sobre = (item.get("about_text") or "").strip()
    if len(sobre) > 20:
        paras = "".join(f"<p>{e(x.strip())}</p>" for x in sobre.split("\n") if x.strip())
        p.append(f'<section class="bloco"><h2>A história</h2><div class="prosa">{paras}</div></section>')
    elif (item.get("description") or "").strip():
        p.append('<section class="bloco"><h2>Sobre</h2><div class="prosa"><p>'
                 + e(item["description"].strip()) + "</p></div></section>")

    galeria = item.get("gallery_urls")
    if isinstance(galeria, list) and galeria:
        imgs = "".join(f'<img src="{e(u)}" alt="{e(nome)}" loading="lazy">' for u in galeria[:8])
        p.append(f'<section class="bloco"><h2>Fotos</h2><div class="galeria">{imgs}</div></section>')

    servicos = item.get("servicos") or []
    if servicos:
        linhas = []
        for s in servicos:
            preco = ("€%.2f" % (s["price_cents"] / 100.0)) if s.get("price_cents") else ""
            dur = ("%d min" % s["duration_minutes"]) if s.get("duration_minutes") else ""
            meta = " · ".join(x for x in (dur, preco) if x)
            desc = f'<span class="desc">{e(s.get("description"))}</span>' if s.get("description") else ""
            linhas.append(f'<li><div><b>{e(s["name"])}</b>{desc}</div>'
                          f'<span class="meta">{e(meta)}</span></li>')
        p.append('<section class="bloco"><h2>Serviços</h2><ul class="lista-precos">'
                 + "".join(linhas) + "</ul></section>")

    amostra = item.get("amostra") or []
    if amostra:
        cards = []
        for prod in amostra:
            preco = ("€%.2f" % float(prod["price"])) if prod.get("price") else ""
            cards.append(f"""<article class="prod">
  {bloco_foto(prod.get('photo_url'), prod['name'], 'prod-img')}
  <div class="prod-txt"><b>{e(prod['name'])}</b><span>{e(preco)}</span></div>
</article>""")
        total = item.get("n_produtos") or len(amostra)
        p.append(f'<section class="bloco"><h2>Alguns dos produtos</h2>'
                 f'<div class="prods">{"".join(cards)}</div>'
                 f'<p class="nota">São {total} no total — vê tudo na app.</p></section>')

    contactos = []
    if item.get("address"):
        mapa = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(item["address"])
        contactos.append(f'<li><b>Morada</b><a href="{e(mapa)}" rel="noopener">{e(item["address"])}</a></li>')
    if item.get("phone"):
        contactos.append(f'<li><b>Telefone</b><a href="tel:{e(item["phone"])}">{e(item["phone"])}</a></li>')
    if item.get("whatsapp"):
        w = re.sub(r"\D", "", str(item["whatsapp"]))
        contactos.append(f'<li><b>WhatsApp</b><a href="https://wa.me/{w}" rel="noopener">Falar</a></li>')
    if contactos:
        p.append('<section class="bloco"><h2>Onde fica</h2><div class="cartoes">'
                 '<div class="cartao"><ul class="contactos">' + "".join(contactos) + "</ul>"
                 + redes(item) + "</div>" + horario(item) + "</div></section>")

    mini = MINISITES.get(nome.strip().lower())
    if mini:
        p.append('<section class="bloco"><p class="minisite">'
                 f'<a href="{e(mini)}" rel="noopener">Ver o site da casa →</a></p></section>')

    artigo = "o" if tipo == "loja" else "a"
    p.append(f'<section class="bloco fecho-pedir"><h2>{e(verbo)} n{artigo} {e(nome)}</h2>'
             + dois_botoes(tipo, item["id"], verbo) + "</section>")
    p.append("</div></main>")
    p.append(saidas(f"Voltar a {cat_nome}", cat_href, "Instalar o Bora", PLAY))
    p.append(rodape())
    return "".join(p)


# ───────────────────────── cartões de listagem ─────────────────────────

def cartao_parceiro(item, tipo):
    foto = item.get("photo_url") or item.get("hero_image_url")
    o_que = O_QUE.get(item.get("category"), "")
    selo = '<span class="mini-selo">Em breve</span>' if item.get("coming_soon") else ""
    return f"""<a class="cartao-loja" href="/loja/{e(item['slug'])}">
  <div class="cartao-foto">{bloco_foto(foto, item['name'], 'cl-img')}{selo}</div>
  <div class="cartao-txt">
    <b>{e(item['name'])}</b>
    <span>{e(o_que)}</span>
  </div>
</a>"""


def cartao_cadeia(item):
    """Loja não-parceira: entra na lista porque dá mesmo para pedir, mas sem
    página própria — não é parceira e não se faz publicidade a marca alheia."""
    destino = f"{APP}/#/loja/{urllib.parse.quote(str(item['id']))}"
    n = item.get("n_produtos") or 0
    extra = f"{n} produtos" if n else O_QUE.get(item.get("category"), "")
    return (f'<a class="cadeia" href="{e(destino)}" rel="noopener">'
            f'<b>{e(item["name"])}</b><span>{e(extra)}</span></a>')


# ───────────────────────── páginas de categoria ─────────────────────────

def pagina_categoria(chave, dados):
    c = CATEGORIAS[chave]
    lojas = dados["lojas"]
    provedores = dados["provedores"]

    p = [cabeca(f"{c['titulo']} — Bora Guarda", c["frase"], "/" + chave),
         topo(), "<main>", '<div class="wrap">',
         migalhas([("Início", "/"), (c["titulo"], None)]), "</div>",
         f"""<section class="cat-topo">
  <div class="wrap">
    <div class="chapeu">{e(c['chapeu'])}</div>
    <h1>{e(c['titulo'])}</h1>
    <p class="lead">{e(c['frase'])}</p>
  </div>
</section>""",
         '<div class="wrap conteudo">']

    if chave == "viagens":
        p.append(_corpo_viagens())
    elif chave == "entregas":
        p.append(_corpo_entregas(lojas))
    elif chave == "beleza":
        p.append(_corpo_beleza(provedores))
    elif chave == "festas":
        p.append(_corpo_festas())
    else:
        p.append(_corpo_mais(lojas))

    p.append("</div></main>")
    p.append(saidas("Voltar ao início", "/", "Instalar o Bora", PLAY))
    p.append(rodape())
    return "".join(p)


def _pontos(itens):
    out = ['<div class="pontos">']
    for titulo, texto in itens:
        out.append(f'<div class="ponto"><b>{e(titulo)}</b><p>{e(texto)}</p></div>')
    out.append("</div>")
    return "".join(out)


def _corpo_viagens():
    return ('<section class="bloco">'
            + _pontos([
                ("Preço fechado antes de entrar",
                 "Escreves para onde vais e o preço aparece. É esse que pagas — sem multiplicador."),
                ("Marca para depois",
                 "Escolhes o dia e a hora, e o motorista fica avisado. Sem taxa de reserva."),
                ("Ida e volta com 20% menos",
                 "Pedes as duas de uma vez e o desconto cai nas duas viagens."),
                ("Paragem extra pelo caminho",
                 "Precisas de passar na farmácia antes de casa? Acrescentas ao pedido."),
                ("Dinheiro, cartão ou MB Way",
                 "Escolhes na hora de confirmar. Quem prefere notas continua a pagar com notas."),
            ])
            + f'<div class="pedir"><a class="btn btn-p" href="{APP}" rel="noopener">Pedir uma viagem</a>'
              f'<a class="btn btn-s" href="{PLAY}" rel="noopener">Instalar a app</a></div>'
            + "</section>")


def _corpo_entregas(lojas):
    parceiros = [l for l in lojas if l.get("is_partner")]
    cadeias = [l for l in lojas if not l.get("is_partner")]
    por_cat = {}
    for l in cadeias:
        por_cat.setdefault(l.get("category") or "outros", []).append(l)

    out = []
    if parceiros:
        out.append('<section class="bloco"><h2>Casas da Guarda</h2>'
                   '<p class="nota">Negócios daqui, com página própria.</p>'
                   '<div class="grelha-lojas">'
                   + "".join(cartao_parceiro(l, "loja") for l in parceiros)
                   + "</div></section>")
    nomes = {"supermarket": "Supermercados", "restaurant": "Restaurantes",
             "store": "Lojas", "pharmacy": "Farmácia"}
    for cat in ("supermarket", "restaurant", "store", "pharmacy"):
        if not por_cat.get(cat):
            continue
        out.append(f'<section class="bloco"><h2>{nomes[cat]}</h2>'
                   '<div class="cadeias">'
                   + "".join(cartao_cadeia(l) for l in sorted(por_cat[cat], key=lambda x: x["name"]))
                   + "</div></section>")
    out.append('<section class="bloco"><p class="nota">Entrega a partir de €2,50 até 4 km. '
               "Acompanhas o estafeta no mapa, do pedido até à porta.</p></section>")
    return "".join(out)


def _corpo_beleza(provedores):
    if not provedores:
        return '<section class="bloco"><p class="nota">Ainda não há casas de beleza no site.</p></section>'
    return ('<section class="bloco"><h2>Onde marcar</h2><div class="grelha-lojas">'
            + "".join(cartao_parceiro(x, "servico") for x in provedores)
            + "</div></section>"
            + '<section class="bloco">'
            + _pontos([
                ("Escolhes a hora", "Vês as horas que a casa tem mesmo livres e escolhes a tua."),
                ("Fica guardada", "A marcação fica na tua agenda e avisa-te antes da hora."),
            ]) + "</section>")


def _corpo_festas():
    return ("""<section class="bloco">
  <div class="embreve grande">
    <span class="selo">Em breve</span>
    <p>Ainda não dá para encomendar. Estamos a preparar isto com quem faz.</p>
  </div>
  <div class="festa-g">
    <div class="festa-i"><div class="ee">🎂</div><b>Bolos</b></div>
    <div class="festa-i"><div class="ee">🥟</div><b>Salgados</b></div>
    <div class="festa-i"><div class="ee">🍬</div><b>Docinhos</b></div>
    <div class="festa-i"><div class="ee">🎈</div><b>Decoração</b></div>
  </div>
  <p class="nota">Feitos por encomenda, para o dia certo.</p>
</section>"""
            + '<section class="bloco"><h2>Faz bolos ou salgados?</h2>'
              '<p class="nota">Estamos a falar com quem faz, aqui na Guarda.</p>'
              '<div class="pedir"><a class="btn btn-p" href="/ser-parceiro">Quero entrar</a></div>'
              "</section>")


def _corpo_mais(lojas):
    farmacias = [l for l in lojas if l.get("category") == "pharmacy"]
    out = ['<section class="bloco">'
           + _pontos([
               ("Lojas da cidade", "Do material de escritório à ração do gato, entregue em casa."),
               ("Farmácia", "Vamos buscar o que precisas."),
               ("Limpeza da casa", "Marcas a limpeza como marcas qualquer outro serviço."),
               ("Favores", "Levantar uma encomenda, pagar uma conta, entregar as chaves."),
           ]) + "</section>"]
    if farmacias:
        out.append('<section class="bloco"><h2>Farmácia</h2><div class="cadeias">'
                   + "".join(cartao_cadeia(l) for l in farmacias) + "</div></section>")
    out.append(f'<section class="bloco"><div class="pedir">'
               f'<a class="btn btn-p" href="{APP}" rel="noopener">Pedir pelo site</a>'
               f'<a class="btn btn-s" href="{PLAY}" rel="noopener">Instalar a app</a></div></section>')
    return "".join(out)



def _bloco_video_parceiros():
    """O vídeo só entra na página quando o ficheiro existe mesmo.

    A ordem é essa de propósito: o estúdio filma esta página, portanto ela tem
    de estar no ar ANTES do vídeo existir. Sem esta guarda, ficava aqui um
    <video> a apontar para um 404.
    """
    mp4 = os.path.join(RAIZ, "assets", "video", "bora-parceiros.mp4")
    if not os.path.exists(mp4):
        return ""
    return """<section class="bloco">
  <div class="video-caixa" data-nocapture>
    <video controls preload="none" poster="/assets/video/bora-parceiros-poster.jpg"
           width="1920" height="1080">
      <source src="/assets/video/bora-parceiros.mp4" type="video/mp4">
      O teu navegador não consegue mostrar este vídeo.
    </video>
  </div>
</section>"""


# ───────────────────────── ser parceiro ─────────────────────────

def pagina_ser_parceiro(dados):
    lojas = dados["lojas"]
    provedores = dados["provedores"]
    exemplos = [l for l in lojas if l.get("is_partner")] + provedores
    n_lojas = len(lojas) + len(provedores)
    n_cats = len({l.get("category") for l in lojas} | {p.get("category") for p in provedores})

    cards = "".join(cartao_parceiro(x, "servico" if x in provedores else "loja")
                    for x in exemplos)

    p = [cabeca("Pôr o meu negócio no Bora — Guarda",
                "Entra sem pagar nada. A Bora só ganha quando vendes. "
                "Montamos a tua loja e oferecemos o site do teu negócio.",
                "/ser-parceiro"),
         topo(), "<main>", '<div class="wrap">',
         migalhas([("Início", "/"), ("Ser parceiro", None)]), "</div>",
         f"""<section class="cat-topo" id="topo">
  <div class="wrap">
    <div class="chapeu">Para quem tem negócio na Guarda</div>
    <h1>O cliente já procura no telefone.<br>Falta lá estares.</h1>
    <p class="lead">Entras sem pagar nada. Montamos a tua loja. E o site do teu
    negócio vai de presente.</p>
  </div>
</section>""",
         '<div class="wrap conteudo">',
         _bloco_video_parceiros(),
         f"""<section class="bloco" id="numeros">
  <div class="numeros">
    <div><b>{n_lojas}</b><span>lojas e serviços já no Bora</span></div>
    <div><b>{n_cats}</b><span>tipos de negócio</span></div>
    <div><b>0€</b><span>para entrar</span></div>
  </div>
</section>""",
         '<section class="bloco" id="precos"><h2>O que a Bora cobra, com todas as letras</h2>'
         + _pontos([
             ("Não há mensalidade nem taxa de adesão", "Entrar não custa nada. Estar no Bora não custa nada."),
             ("A Bora só ganha quando vendes", "A comissão sai do que vendeste. Se não vendeste, não pagas."),
             ("Restaurantes e lojas parceiras", "10% de comissão sobre o pedido. Está escrito no contrato, sem letra pequena."),
             ("O cliente também paga a entrega", "A taxa de entrega é do cliente e vai para o estafeta — não sai do teu bolso."),
         ]) + "</section>",
         '<section class="bloco" id="passos"><h2>Como funciona, em 4 passos</h2>'
         + _pontos([
             ("1. Falamos", "Sentamos contigo, ouvimos como trabalhas e vemos o que faz sentido."),
             ("2. Montamos", "A tua loja é montada por nós, com os teus produtos e os teus preços."),
             ("3. Abres", "Os clientes começam a ver-te na app e no site."),
             ("4. Ajustamos", "O que não estiver bem, muda-se. Sem burocracia."),
         ]) + "</section>"]

    if cards:
        p.append('<section class="bloco" id="quem-ja-entrou"><h2>Quem já entrou</h2>'
                 f'<div class="grelha-lojas">{cards}</div></section>')

    p.append(f"""<section class="bloco fecho-pedir" id="falar">
  <h2>Bora pôr o teu negócio no mapa</h2>
  <div class="pedir">
    <a class="btn btn-p" href="https://wa.me/351937501673" rel="noopener">Falar por WhatsApp</a>
    <a class="btn btn-s" href="mailto:{EMAIL}?subject=Quero%20p%C3%B4r%20o%20meu%20neg%C3%B3cio%20no%20Bora">Escrever um email</a>
  </div>
  <p class="nota">Ou liga: <a href="tel:+351937501673">+351 937 501 673</a></p>
</section>""")
    p.append("</div></main>")
    p.append(saidas("Voltar ao início", "/", "Ver o que dá para pedir", "/entregas"))
    p.append(rodape())
    return "".join(p)


# ───────────────────────── main ─────────────────────────

def escrever(caminho, conteudo):
    destino = os.path.join(RAIZ, caminho)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(conteudo)
    print("  %-42s %6d bytes" % (caminho, len(conteudo.encode())))


def main():
    print("A ler do Supabase...")
    dados = recolher()
    lojas, provedores = dados["lojas"], dados["provedores"]
    print("  %d lojas (%d parceiras) · %d serviços"
          % (len(lojas), sum(1 for l in lojas if l.get("is_partner")), len(provedores)))

    escrever("dados/parceiros.json", json.dumps(dados, ensure_ascii=False, indent=1))
    if "--so-dados" in sys.argv:
        return

    print("\nPáginas de parceiro:")
    for l in lojas:
        if l.get("is_partner"):
            escrever("loja/%s.html" % l["slug"], pagina_parceiro(l, "loja"))
    for p in provedores:
        escrever("loja/%s.html" % p["slug"], pagina_parceiro(p, "servico"))

    print("\nCategorias:")
    for chave in CATEGORIAS:
        escrever("%s.html" % chave, pagina_categoria(chave, dados))

    print("\nRecrutamento:")
    escrever("ser-parceiro.html", pagina_ser_parceiro(dados))
    print("\nFeito. index.html, privacidade.html e termos.html não foram tocados.")


if __name__ == "__main__":
    main()

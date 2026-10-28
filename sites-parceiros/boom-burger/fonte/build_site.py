# -*- coding: utf-8 -*-
"""Gerador do site da Boom! Burger -> ../dist/

  python gerar_menu.py      # precos da app (ou "Preco na app" enquanto nao ha)
  python imagens_site.py    # so quando mudam fotos
  python video.py           # so quando muda o video
  python og.py              # imagem de partilha
  python build_site.py      # este: index.html, 404.html, robots, sitemap, _headers, vendor

Imagens e video ficam em assets/ (nunca base64: regra 8.3 e LCP). O CSS vai dentro do HTML
(critico, ~20 KB); o JS e o GSAP vao em ficheiros com defer.
"""
import html, json, os, re, shutil, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
DIST = os.path.join(B, 'dist')
A = os.path.join(DIST, 'assets')
URL = 'https://boomburger.boraguarda.com'
PEDIR = 'https://boraguarda.com/baixar?de=site-boomburger'
APP_LOJA = 'https://app.boraguarda.com/#/loja/boom-burger-guarda'
MAPS = 'https://maps.google.com/?cid=%d' % int('ad04313ae716a6eb', 16)
FACEBOOK = 'https://www.facebook.com/people/Boom-Burger-Hamburgueria-Artesanal/61571813637975/'
TEL, TEL_TXT = '+351923177918', '923 177 918'
NOTA, N_AVAL = '4,7', 114
SB = {'url': 'https://ojykpzwqrtusfeakzrna.supabase.co', 'loja': 'boom-burger-guarda'}
SB['chave'] = json.load(open(r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines', encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
assert SB['chave'].startswith('sb_publishable_'), 'so a chave PUBLICA pode ir para o HTML'

menu = json.load(open(os.path.join(AQUI, 'menu.json'), encoding='utf-8'))
imgs = json.load(open(os.path.join(AQUI, 'imagens.json'), encoding='utf-8'))
cam = json.load(open(os.path.join(B, 'media', 'camadas', 'portobello-v3', 'camadas.json'), encoding='utf-8'))
e = html.escape


def pic(nome, alt, sizes, cls='', eager=False, w_h=None):
    i = imgs[nome]
    ls = i['larguras']
    w, h = w_h or (ls[-1], round(i['h'] * ls[-1] / i['w']))
    av = ', '.join(f'assets/img/{nome}-{L}.avif {L}w' for L in ls)
    wb = ', '.join(f'assets/img/{nome}-{L}.webp {L}w' for L in ls)
    lz = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ''
    # a foto do heroi vai so em WebP: o AVIF descodifica devagar num processador fraco e atrasava o LCP
    fonte_avif = '' if nome == 'heroi' else f'<source type="image/avif" srcset="{av}" sizes="{sizes}">'
    return (f'<picture{c}>{fonte_avif}'
            f'<source type="image/webp" srcset="{wb}" sizes="{sizes}">'
            f'<img src="assets/img/{nome}-{ls[0]}.webp" alt="{e(alt)}" width="{w}" height="{h}" {lz}></picture>')


def preco_html(p, cls='preco'):
    if p['preco'] is None:
        return f'<span class="{cls} sem" data-id="{p["id"]}">Preço na app</span>'
    return f'<span class="{cls}" data-id="{p["id"]}">{p["preco"]:.2f} €</span>'.replace('.', ',', 1)


# ---------- logotipo inline (classes em vez de ids: aparece duas vezes na pagina) ----------
svg_partes = open(os.path.join(B, 'media', 'logo', 'boom-logo-partes.svg'), encoding='utf-8').read()
svg_marca = open(os.path.join(B, 'media', 'logo', 'boom-marca.svg'), encoding='utf-8').read()


def svg_inline(s, label, sem_rodape=False, vb=None):
    s = re.sub(r'<\?xml[^>]*>', '', s)
    s = re.sub(r'<title>.*?</title>', '', s, flags=re.S)
    s = re.sub(r'<g id="([a-z-]+)"', r'<g class="l-\1"', s)
    if sem_rodape:
        s = re.sub(r'<g class="l-rodape".*?</g>', '', s, flags=re.S)
    if vb:
        s = re.sub(r'viewBox="[^"]+"', f'viewBox="{vb}"', s, count=1)
    s = re.sub(r'aria-label="[^"]*"', f'aria-label="{e(label)}"', s, count=1)
    s = re.sub(r'(\d\.\d)\d+', r'\1', s)  # 1 casa decimal chega (0,1 unidade numa caixa de 392): HTML mais leve
    s = re.sub(r'>\s+<', '><', s)
    return s.strip()


ESTRONDO = ('<svg class="estrondo" viewBox="-100 -100 200 200" aria-hidden="true">' +
            ''.join(f'<line x1="0" y1="-62" x2="0" y2="-88" stroke="#DBB545" stroke-width="5" stroke-linecap="round" transform="rotate({a})"/>'
                    for a in range(0, 360, 30)) + '</svg>')
def logo_em_camadas(label, com_rodape):
    """O logotipo partido em SVGs empilhados (um por parte), para animar cada camada INTEIRA
    com transform/opacity no compositor — animar <g> dentro de um SVG redesenhava tudo no
    processador a cada fotograma e atrasava o desenho da foto do heroi (Lighthouse)."""
    s = svg_partes
    fim_defs = s.find('</defs>')
    defs = s[s.find('<defs>'):fim_defs + 7] if fim_defs > 0 else ''
    grupos = {n: (a, c) for n, a, c in re.findall(r'<g id="([a-z-]+)"([^>]*)>(.*?)</g>', s[fim_defs:], re.S)}
    vb = '225 45 392 510' if com_rodape else '225 45 392 452'
    camadas = [('pao-baixo', ['pao-baixo']), ('pao-cima', ['pao-cima']), ('sementes', ['sementes']),
               ('boom', ['boom', 'boom-pequeno']), ('burger', ['burger'])]
    if com_rodape:
        camadas.append(('rodape', ['rodape']))
    out = []
    for nome, gs in camadas:
        corpo = ''.join(f'<g{grupos[g][0]}>{grupos[g][1]}</g>' for g in gs)
        if nome == 'rodape':
            corpo = defs + corpo
        out.append(f'<svg class="lc l-{nome}" viewBox="{vb}" aria-hidden="true" focusable="false">{corpo}</svg>')
    html_ = ''.join(out)
    html_ = re.sub(r'(\d\.\d)\d+', r'\1', html_)
    html_ = re.sub(r'>\s+<', '><', html_)
    w, h = vb.split()[2:]
    return f'<div class="lm" role="img" aria-label="{e(label)}" style="aspect-ratio:{w}/{h}">{html_}</div>'


logo_heroi = logo_em_camadas('Boom! Burger', False)

# O momento so da Boom: as letras BOOM do PROPRIO logotipo (vetor do dono), em contorno gigante
_g = {n: c for n, a_, c in re.findall(r'<g id="([a-z-]+)"([^>]*)>(.*?)</g>', svg_partes[svg_partes.find('</defs>'):], re.S)}
_boom = re.sub(r'fill="#[0-9A-Fa-f]{6}"', 'fill="none" stroke="#DBB545" stroke-width="2.5" vector-effect="non-scaling-stroke"', _g['boom'])
BOOM_GIGANTE = re.sub(r'(\d\.\d)\d+', r'\1', f'<svg class="boom-gigante" viewBox="314 158 222 144" aria-hidden="true" focusable="false">{_boom}</svg>')
logo_rodape = logo_em_camadas('Boom! Burger — Hamburgueria Artesanal', True)
marca_cab = svg_inline(svg_marca, 'Boom! Burger — início')

SETA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.2 5.3a1 1 0 0 1 1.4 0l6 6a1 1 0 0 1 0 1.4l-6 6a1 1 0 1 1-1.4-1.4l4.3-4.3H4a1 1 0 1 1 0-2h13.5l-4.3-4.3a1 1 0 0 1 0-1.4z"/></svg>'
BTN = f'<a class="btn btn-pedir" href="{PEDIR}">Pedir pelo Bora {SETA}</a>'

# ---------- favoritos ----------
todos = {p['id']: p for c in menu['categorias'] for p in c['produtos']}
FAV = ['boom-duplo-smash', 'boom-bombastico', 'boom-brie-fan', 'boom-kamikaze', 'boom-portobello', 'boom-serra-da-estrela']
fav_html = []
for pid in FAV:
    p = todos[pid]
    et = ''  # 2.a ronda: 'Mais pedido' repetido em 3 cartoes nao diz nada; o titulo da seccao ja o diz
    desc = re.split(r'\.\s*(Inclui|Acompanha)', p['desc'])[0].rstrip('.') + '.'
    fav_html.append(
        f'<li class="revela"><article class="cartao">{et}<div class="cartao-foto">'
        f'{pic("c-" + pid, p["nome"], "(max-width:600px) 82vw, (max-width:900px) 46vw, 380px")}</div>'
        f'<div class="cartao-corpo"><h3>{e(p["nome"])}</h3><p>{e(desc)}</p>'
        f'<div class="cartao-pe">{preco_html(p)}<a class="pedir-link" href="{PEDIR}" aria-label="Pedir {e(p["nome"])} pelo Bora">Pedir {SETA}</a></div>'
        f'</div></article></li>')

# ---------- menu completo ----------
NOTAS = {
    'traquinas': 'Para os mais novos.',
    'cervejas': 'Só para maiores de 18.',
}
abas, cats = [], []
for c in menu['categorias']:
    abas.append(f'<a href="#{c["id"]}">{e(c["nome"].replace("Menu ", ""))}</a>')
    compacta = c['id'] in ('bebidas', 'cervejas')
    itens = []
    for p in c['produtos']:
        img = (f'<img src="assets/img/p-{p["id"]}-160.webp" srcset="assets/img/p-{p["id"]}-160.webp 160w, assets/img/p-{p["id"]}-320.webp 320w" '
               f'sizes="72px" alt="" width="72" height="72" loading="lazy" decoding="async">') if p['foto'] and f'p-{p["id"]}' in imgs else '<span></span>'
        idade = '<span class="marca-18" title="Só para maiores de 18">18+</span>' if p['alcool'] else ''
        desc = f'<p>{e(p["desc"])}</p>' if p['desc'] and not compacta else ''
        itens.append(f'<li class="item">{img}<div><h4>{e(p["nome"])}{idade}</h4>{desc}</div>{preco_html(p)}</li>')
    nota = f'<p class="nota">{e(NOTAS[c["id"]])}</p>' if c['id'] in NOTAS else ''
    cats.append(f'<section class="menu-cat" id="{c["id"]}" aria-labelledby="t-{c["id"]}"><h3 id="t-{c["id"]}">{e(c["nome"])}</h3>{nota}'
                f'<ul class="menu-lista{" compacta" if compacta else ""}">{"".join(itens)}</ul></section>')
aviso_precos = ('Preços iguais aos da app Bora.' if menu['com_precos'] else
                'Os preços aparecem aqui assim que a loja abrir na app Bora; são sempre os mesmos da app.')

# ---------- camadas ----------
LEG = ['Pão de feijão preto', 'Cogumelo portobello, cebola grelhada e molho de trufa negra',
       'Bacon e queijo provolone fumado', '160 g de carne de novilho e agrião', 'E o pão de baixo fecha.']
TAM_CENA = '(max-width:900px) 92vw, 560px'


def src_cam(f):
    return (f'src="assets/camadas/{f}" srcset="assets/camadas/{f.replace(".webp", "-450.webp")} 450w, '
            f'assets/camadas/{f} {cam["largura_px"]}w" sizes="{TAM_CENA}"')


camadas_html = ''.join(
    f'<img class="camada" {src_cam(c["ficheiro"])} alt="" style="top:{c["top_pct"]}%" '
    f'width="{cam["largura_px"]}" height="{round(cam["altura_px"] * c["altura_pct"] / 100)}" loading="lazy" decoding="async">'
    for c in cam['camadas'])
camadas_html += (f'<img class="solida" {src_cam(cam["solida"])} alt="" width="{cam["largura_px"]}" '
                 f'height="{cam["altura_px"]}" loading="lazy" decoding="async">')
legendas = ''.join(f'<li data-n="{i:02d}">{e(t)}</li>' for i, t in enumerate(LEG, 1))

# ---------- galeria ----------
gal = ''.join(f'<li class="revela">{pic(f"galeria-{i}", imgs[f"galeria-{i}"]["alt"], "(max-width:700px) 50vw, 25vw")}</li>' for i in range(1, 9))

# ---------- JSON-LD ----------
ld = {
    '@context': 'https://schema.org', '@type': 'Restaurant', 'name': 'Boom! Burger — Hamburgueria Artesanal',
    'url': URL + '/', 'image': [URL + '/assets/og-boomburger.jpg'], 'logo': URL + '/assets/logo/boom-logo-512.png',
    'telephone': TEL, 'servesCuisine': ['Hambúrgueres', 'Hamburgueria artesanal'], 'priceRange': '€€',
    'address': {'@type': 'PostalAddress', 'streetAddress': 'R. Jardim dos Castelos Velhos', 'postalCode': '6300-397',
                'addressLocality': 'Guarda', 'addressCountry': 'PT'},
    'geo': {'@type': 'GeoCoordinates', 'latitude': 40.5414484, 'longitude': -7.261693},
    'hasMap': MAPS, 'hasMenu': URL + '/#menu', 'acceptsReservations': False, 'sameAs': [FACEBOOK],
    'openingHoursSpecification': [
        {'@type': 'OpeningHoursSpecification', 'dayOfWeek': 'Monday', 'opens': '19:00', 'closes': '22:30'},
        {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 'opens': '12:00', 'closes': '14:30'},
        {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 'opens': '19:00', 'closes': '22:30'}],
    'aggregateRating': {'@type': 'AggregateRating', 'ratingValue': 4.7, 'bestRating': 5, 'reviewCount': N_AVAL},
}

fontes = open(os.path.join(AQUI, 'fontes.css'), encoding='utf-8').read()  # gerado por fontes.py (fontes locais)
fontes = re.sub(r'\s*\n\s*', '', fontes)
css = open(os.path.join(AQUI, 'site.css'), encoding='utf-8').read()
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
css = re.sub(r'\s*\n\s*', '', css)
css = re.sub(r'\s*([{};,>])\s*', r'\1', css).replace(';}', '}')

DESC = ('Boom! Burger, hamburgueria artesanal na Guarda: carne moída todas as manhãs, pão de forno a lenha. '
        'Menu completo e pedido pela app Bora.')
H = f'''<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Boom! Burger — Hamburgueria Artesanal na Guarda</title>
<meta name="description" content="{e(DESC)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{URL}/">
<meta name="theme-color" content="#121110">
<meta property="og:type" content="restaurant">
<meta property="og:locale" content="pt_PT">
<meta property="og:title" content="Boom! Burger — Hamburgueria Artesanal">
<meta property="og:description" content="Carne moída todas as manhãs. Pão de forno a lenha. Na Guarda — pede pelo Bora.">
<meta property="og:url" content="{URL}/">
<meta property="og:image" content="{URL}/assets/og-boomburger.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Hambúrguer Boom! Duplo Smash com cheddar e o logótipo da Boom! Burger">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/logo/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="assets/logo/boom-icone.svg">
<link rel="apple-touch-icon" href="assets/logo/boom-icone-180.png">
<link rel="manifest" href="manifest.webmanifest">
<link rel="preload" as="image" type="image/webp" imagesrcset="{', '.join(f'assets/img/heroi-{L}.webp {L}w' for L in imgs['heroi']['larguras'])}" imagesizes="(max-width:720px) 150vw, 100vw" fetchpriority="high">
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/bebas-neue-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="assets/fonts/inter-latin.woff2" crossorigin>
<style>{fontes}{css}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(',', ':'))}</script>
<link rel="preconnect" href="{SB['url']}" crossorigin>
<script>document.documentElement.classList.add('js');window.BOOM_SB={json.dumps(SB)};</script>
<script src="assets/site.js?v=__VERSAO__" defer></script>
</head>
<body>
<a class="salto" href="#menu">Saltar para o menu</a>
<header class="cab">
  <div class="caixa">
    <a class="cab-marca" href="#topo">{marca_cab}</a>
    <a class="cab-menu" href="#menu">Ver o menu</a>
    <nav aria-label="Secções"><a href="#favoritos">Favoritos</a><a href="#menu">Menu</a><a href="#casa">A casa</a><a href="#visita">Horário e morada</a></nav>
    {BTN.replace('class="btn btn-pedir"', 'class="btn btn-pedir btn-peq"')}
  </div>
</header>

<main id="topo">
<section class="heroi" aria-labelledby="t-heroi">
  {pic('heroi', 'Boom! Duplo Smash: pão brioche, dupla carne smash de novilho e molho de queijo cheddar a escorrer, com batata frita artesanal', '(max-width:720px) 150vw, 100vw', 'heroi-foto', eager=True)}
  <div class="caixa">
    <div class="heroi-conteudo">
      <p class="olho olho-heroi">Hamburgueria artesanal · Guarda</p>
      <div class="logo-monta">{logo_heroi}{ESTRONDO}</div>
      <h1 id="t-heroi"><span class="so-leitor">Boom! Burger — </span><span class="l">Carne moída</span> <span class="l">todas as manhãs.</span> <span class="l ouro">Pão de forno a lenha.</span></h1>
      <p class="heroi-sub">Hambúrgueres artesanais na Rua Jardim dos Castelos Velhos, Guarda.</p>
      <div class="heroi-acoes">{BTN}<a class="selo-google" href="{MAPS}" rel="noopener" target="_blank"><span class="estrelas" aria-hidden="true">★★★★★</span><span><b>{NOTA}</b> no Google · {N_AVAL} avaliações</span></a></div>
      <a class="link-sem-instalar" href="{APP_LOJA}">ou pede pelo site, sem instalar</a>
    </div>
  </div>
</section>

<section class="cena secao" id="camadas" aria-labelledby="t-cena">
  <div class="caixa cena-grelha">
    <div class="cena-texto">
      <p class="olho">O Portobello, por dentro</p>
      <h2 class="titulo" id="t-cena">Monta-se <em>camada</em> a camada.</h2>
      <ol class="cena-legendas">{legendas}</ol>
      <div class="cena-cta">{BTN}<span class="texto-2">Boom! Portobello · {preco_html(todos['boom-portobello'])}</span></div>
    </div>
    <div class="cena-visual">
      <div class="cena-palco" aria-hidden="true">{camadas_html}</div>
      <div class="cena-fecho">
        {pic('fecho-portobello', 'Boom! Portobello: pão de feijão preto, bacon, cogumelos, provolone fumado e agrião', '(max-width:900px) 92vw, 560px')}
      </div>
    </div>
  </div>
</section>

<section class="secao" id="favoritos" aria-labelledby="t-fav">
  <div class="caixa">
    <div class="fav-cab"><div><p class="olho">Favoritos da casa</p><h2 class="titulo" id="t-fav">Os que <em>mais saem</em>.</h2></div></div>
    <ul class="fav-lista">{''.join(fav_html)}</ul>
  </div>
</section>

<section class="momento" id="boom" aria-label="Boom!">
  <div class="caixa">
    <div class="momento-palco">{BOOM_GIGANTE}<picture><source type="image/webp" srcset="assets/img/momento-duplo-smash-500.webp 500w, assets/img/momento-duplo-smash-900.webp 900w" sizes="(max-width:700px) 72vw, 520px"><img src="assets/img/momento-duplo-smash-500.webp" alt="Boom! Duplo Smash, recortado: pão brioche, dupla carne smash e cheddar a escorrer" width="900" height="758" loading="lazy" decoding="async"></picture></div>
    <p class="momento-frase">Dupla carne smash, cheddar a escorrer. <a class="pedir-link" href="{PEDIR}">Pedir o Duplo Smash {SETA}</a></p>
  </div>
</section>

<section class="secao menu" id="menu" aria-labelledby="t-menu">
  <div class="caixa">
    <p class="olho">Menu completo</p>
    <h2 class="titulo" id="t-menu">Tudo o que sai <em>da chapa</em>.</h2>
    <nav class="menu-abas" aria-label="Categorias do menu">{''.join(abas)}</nav>
    {''.join(cats)}
    <div class="personaliza revela"><span class="ico" aria-hidden="true">+</span><p><strong>Personaliza o teu hambúrguer na app:</strong> troca o pão (brioche, sem glúten ou bolo do caco), troca a carne (peito de frango ou Veggie Beyond), junta mais 160 g de novilho, um ingrediente extra, maionese caseira ou de malagueta, ou troca a batata por batata doce. <strong>Alergias?</strong> Liga para a loja antes de pedir: <a href="tel:{TEL}">{TEL_TXT}</a>.</p></div>
    <p class="aviso-precos">{aviso_precos}</p>
  </div>
</section>

<section class="secao" id="casa" aria-labelledby="t-casa">
  <div class="caixa casa-grelha">
    <div class="revela">
      <p class="olho">A casa</p>
      <h2 class="titulo" id="t-casa">Artesanal <em>a sério</em>.</h2>
      <p class="casa-citacao">“Prezamos pela qualidade e frescura dos alimentos que utilizamos. O nosso pão é feito em padaria de forno a lenha, a carne é moída todos os dias pela manhã e os legumes e as frutas são frescos, todos os dias.”</p>
      <ul class="factos">
        <li><b>Forno a lenha</b><span>o pão, de padaria</span></li>
        <li><b>Todas as manhãs</b><span>a carne moída na hora</span></li>
        <li><b>Frescos</b><span>legumes e fruta, todos os dias</span></li>
      </ul>
      <p class="texto-2" style="margin-top:24px">Na sala há Wi-Fi grátis. E há o Boom! Serra da Estrela, com queijo da serra e chutney de abóbora.</p>
    </div>
    <div class="casa-foto revela">{pic('casa', 'Boom! Serra da Estrela com batata frita artesanal sobre mesa de madeira', '(max-width:900px) 92vw, 520px')}</div>
  </div>
</section>

<section class="secao" id="na-chapa" aria-labelledby="t-chapa">
  <div class="caixa">
    <h2 class="so-leitor" id="t-chapa">Na chapa</h2>
    <div class="chapa-video revela">
      <video muted loop playsinline autoplay preload="none" poster="assets/video/na-chapa-poster.webp" width="1280" height="720" aria-label="Vídeo curto, sem som: o Duplo Smash, o Portobello a montar-se, a batata gulosa e o Kamikaze">
        <source data-src="assets/video/na-chapa.mp4" type="video/mp4">
      </video>
      <span class="chapa-titulo" aria-hidden="true">Na chapa</span>
    </div>
  </div>
</section>

<section class="secao" id="galeria" aria-labelledby="t-gal">
  <div class="caixa">
    <p class="olho">Galeria</p>
    <h2 class="titulo" id="t-gal">Da cozinha <em>para a mesa</em>.</h2>
    <ul class="galeria">{gal}</ul>
  </div>
</section>

<section class="secao" id="como-pedir" aria-labelledby="t-como">
  <div class="caixa">
    <p class="olho">Como pedir</p>
    <h2 class="titulo" id="t-como">Três toques <em>e está</em>.</h2>
    <ol class="passos">
      <li class="revela"><span class="n">1</span><h3>Abre o Bora</h3><p>Descarrega grátis no iPhone ou no Android, ou usa no browser sem instalar.</p></li>
      <li class="revela"><span class="n">2</span><h3>Escolhe na Boom! Burger</h3><p>O menu é o mesmo desta página, com os mesmos preços.</p></li>
      <li class="revela"><span class="n">3</span><h3>Recebe ou levanta</h3><p>Em casa, pelos estafetas do Bora, ou levantas na loja.</p></li>
    </ol>
    <div class="heroi-acoes">{BTN}<a class="link-sem-instalar" href="{APP_LOJA}">ou pede pelo site, sem instalar</a></div>
  </div>
</section>

<section class="secao secao-google" aria-labelledby="t-google" style="padding-top:0">
  <div class="caixa">
    <div class="google revela">
      <span class="nota" aria-hidden="true">{NOTA}</span>
      <div><h2 class="olho" id="t-google" style="margin:0">Nota no Google</h2><span class="estrelas" aria-hidden="true">★★★★★</span><p>{NOTA} em 5, com {N_AVAL} avaliações no Google.</p></div>
      <a class="btn btn-linha" href="{MAPS}" target="_blank" rel="noopener">Ler as avaliações</a>
    </div>
  </div>
</section>

<section class="secao visita" id="visita" aria-labelledby="t-visita" style="padding-top:0">
  <div class="caixa visita-grelha">
    <div class="revela">
      <p class="olho">Visita-nos</p>
      <h2 class="titulo" id="t-visita">Na Guarda.</h2>
      <dl>
        <dt>Morada</dt><dd>R. Jardim dos Castelos Velhos<br>6300-397 Guarda</dd>
        <dt>Horário</dt>
        <dd><table class="horario"><caption class="so-leitor">Horário de funcionamento</caption><tbody>
          <tr data-dia="1"><th scope="row">Segunda</th><td>19:00–22:30</td></tr>
          <tr data-dia="2"><th scope="row">Terça</th><td>12:00–14:30 · 19:00–22:30</td></tr>
          <tr data-dia="3"><th scope="row">Quarta</th><td>12:00–14:30 · 19:00–22:30</td></tr>
          <tr data-dia="4"><th scope="row">Quinta</th><td>12:00–14:30 · 19:00–22:30</td></tr>
          <tr data-dia="5"><th scope="row">Sexta</th><td>12:00–14:30 · 19:00–22:30</td></tr>
          <tr data-dia="6"><th scope="row">Sábado</th><td>12:00–14:30 · 19:00–22:30</td></tr>
          <tr data-dia="0"><th scope="row">Domingo</th><td>Fechado</td></tr>
        </tbody></table>
        <span class="estado-agora" aria-live="polite"></span></dd>
        <dt>Telefone</dt><dd><a href="tel:{TEL}">{TEL_TXT}</a></dd>
      </dl>
    </div>
    <div class="visita-cartao revela">
      {pic('visita', 'Bolo do caco com manteiga de alho caseira, sobre mesa de madeira', '(max-width:900px) 92vw, 560px')}
      <div class="corpo"><a class="btn btn-linha" href="{MAPS}" target="_blank" rel="noopener">Abrir no Google Maps</a><a class="btn btn-linha" href="tel:{TEL}">Ligar {TEL_TXT}</a>{BTN}</div>
    </div>
  </div>
</section>
</main>

<footer class="rodape">
  <div class="caixa">
    <div class="logo-monta logo-rodape">{logo_rodape}</div>
    <div class="redes"><a href="{FACEBOOK}" target="_blank" rel="noopener"><svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M14 8V6.5c0-.7.5-1 1-1h2V2h-3c-3 0-4 2.2-4 4.3V8H8v3.5h2V22h4V11.5h2.7L17 8h-3z"/></svg>Facebook</a></div>
    <small>© 2026 Boom! Burger — Hamburgueria Artesanal · R. Jardim dos Castelos Velhos, Guarda</small>
    <p class="oferta"><a href="https://boraguarda.com/?de=site-boomburger">Site oferecido pelo <b>Bora</b></a> · pedidos, entregas e serviços na Guarda</p>
  </div>
</footer>
<div class="barra-pedir">{BTN}</div>
</body>
</html>
'''

# ---------- escrever dist ----------
os.makedirs(A, exist_ok=True)
js = open(os.path.join(AQUI, 'site.js'), encoding='utf-8').read()
open(os.path.join(A, 'site.js'), 'w', encoding='utf-8').write(js)
import hashlib
versao = hashlib.sha1(js.encode()).hexdigest()[:8]
H = H.replace('__VERSAO__', versao)
open(os.path.join(DIST, 'index.html'), 'w', encoding='utf-8').write(H)

# GSAP servido pelo proprio site (versao fixa, sem depender de CDN em tempo real)
V = os.path.join(A, 'vendor')
os.makedirs(V, exist_ok=True)
for f in ('gsap.min.js', 'ScrollTrigger.min.js'):
    dst = os.path.join(V, f)
    if not os.path.exists(dst):
        urllib.request.urlretrieve(f'https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/{f}', dst)

NAO_EXISTE = f'''<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página não encontrada — Boom! Burger</title><meta name="robots" content="noindex">
<link rel="icon" href="/assets/logo/favicon.ico">
<style>{fontes.replace('assets/fonts/', '/assets/fonts/')}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#121110;color:#F6F0E2;font:400 17px/1.6 Inter,system-ui,sans-serif;text-align:center;padding:24px}}
h1{{font:400 clamp(3rem,12vw,7rem)/.9 'Bebas Neue',Impact,sans-serif;margin:24px 0 8px;text-transform:uppercase}}p{{color:#BFB6A6}}
img{{width:180px;margin:0 auto}}a{{display:inline-flex;align-items:center;min-height:52px;padding:0 26px;margin:8px;border-radius:999px;font-weight:800;text-decoration:none}}
.a{{background:#F97316;color:#121110}}.b{{box-shadow:inset 0 0 0 1.5px #F6F0E2;color:#F6F0E2}}</style></head>
<body><main><img src="/assets/logo/boom-icone-512.png" alt="Boom! Burger" width="180" height="180">
<h1>Esta página saiu da chapa</h1><p>Não existe aqui. O menu e o pedido estão na página principal.</p>
<a class="a" href="{PEDIR}">Pedir pelo Bora</a><a class="b" href="/">Voltar ao início</a></main></body></html>
'''
open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(NAO_EXISTE)
# /demo/ — pagina do "telemovel 1" da demonstracao de 28/10 (so a conta Cliente Demonstracao pede, so na janela)
os.makedirs(os.path.join(DIST, 'demo'), exist_ok=True)
DEMO = open(os.path.join(AQUI, 'demo.html'), encoding='utf-8').read().replace(
    '<!--CONFIG_PUBLICA-->', f'<script>window.BOOM_SB={json.dumps(SB)};</script>')
assert 'window.BOOM_SB=' in DEMO and 'Danilo' not in DEMO
open(os.path.join(DIST, 'demo', 'index.html'), 'w', encoding='utf-8').write(DEMO)
open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8').write(
    f'# noindex ate o dono aprovar (meta robots em cada pagina)\nUser-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n')
open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8').write(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}/</loc>'
    f'<changefreq>weekly</changefreq></url></urlset>\n')
json.dump({'name': 'Boom! Burger', 'short_name': 'Boom!', 'start_url': '/', 'display': 'browser', 'background_color': '#121110',
           'theme_color': '#121110', 'icons': [{'src': 'assets/logo/boom-icone-192.png', 'sizes': '192x192', 'type': 'image/png'},
                                               {'src': 'assets/logo/boom-icone-512.png', 'sizes': '512x512', 'type': 'image/png'}]},
          open(os.path.join(DIST, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(DIST, '_headers'), 'w', encoding='utf-8', newline='\n').write(
    '/*\n  X-Robots-Tag: noindex\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n'
    '/assets/img/*\n  Cache-Control: public, max-age=31536000, immutable\n'
    '/assets/camadas/*\n  Cache-Control: public, max-age=2592000\n'
    '/assets/video/*\n  Cache-Control: public, max-age=2592000\n'
    '/assets/vendor/*\n  Cache-Control: public, max-age=31536000, immutable\n'
    '/assets/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n'
    '/assets/site.js\n  Cache-Control: public, max-age=31536000, immutable\n'
    '/assets/logo/*\n  Cache-Control: public, max-age=604800\n'
    '/assets/og-boomburger.jpg\n  Cache-Control: public, max-age=604800\n')

tam = os.path.getsize(os.path.join(DIST, 'index.html'))
print('index.html KB', tam // 1024, '| css KB', len(css) // 1024, '| versao js', versao, '| com_precos', menu['com_precos'])
# verificacoes baratas
assert 'glovo' not in H.lower(), 'nada da Glovo no site'
assert 'Danilo' not in H, 'o nome do dono do Bora nao aparece'
for f in re.findall(r'(?:src|href|poster)="(assets/[^"?]+)', H) + re.findall(r'(assets/[^ ,"]+\.(?:avif|webp)) ', H):
    assert os.path.exists(os.path.join(DIST, f)), 'falta ' + f
print('ok: todos os assets referidos existem')

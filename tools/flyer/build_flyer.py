# -*- coding: utf-8 -*-
"""
Flyer oficial do Bora App — A4, 300dpi, montado por script.

Porque e' montado por script e nao gerado por IA de imagem: tres tentativas com
o Gemini escreveram os nomes das marcas errados ("gaola" por Goola, CONTINENTE
torto, KIWOKO deformado, SOBREMESAS repetido). Aqui os logos sao os ficheiros
verdadeiros e os textos sao desenhados, nao "imaginados".

Refazer quando entrar loja nova:
    python download_logos.py     # so' se mudarem URLs/logos na base de dados
    python build_flyer.py
"""
import os, io, math, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import segno

from fundo import gerar_fundo

AQUI = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(AQUI, "assets", *p)
_DOWNLOADS_DANILO = r"C:\Users\danil\Downloads"
SAIDA = _DOWNLOADS_DANILO if os.path.isdir(_DOWNLOADS_DANILO) else os.path.join(
    os.path.expanduser("~"), "Downloads")

# ---------------------------------------------------------------- dimensoes
W, H = 2480, 3508          # A4 a 300dpi
BLEED = 95                 # margem branca de 8mm para a grafica
PAD = 90                   # menos aperto lateral (pedido do Danilo, v3)
CX0, CX1 = BLEED + PAD, W - BLEED - PAD
LARG = CX1 - CX0

VERDE = (22, 163, 74)
LARANJA = (249, 115, 22)
TINTA = (15, 23, 42)       # texto escuro sobre vidro claro
TINTA_SUAVE = (71, 85, 105)
BRANCO = (255, 255, 255)

QR_LADO = int(os.environ.get("QR_LADO", 500))
ALT_RODAPE = 700
QR_OFFSET_Y = 40      # do topo do cartao do rodape ate' ao topo do QR
QR_MARGEM_X = 54      # da margem do cartao ate' ao QR   # ver prova de leitura em verificar.py

PLAY_URL = "https://play.google.com/store/apps/details?id=pt.boraapp.bora"
WEB_URL = "https://app.boraguarda.com/#/registo-cliente"

# ------------------------------------------------------------------ fontes
_FONTE = A("fonts", "Inter-VariableFont.ttf")
_cache_fonte = {}


def fonte(tam, peso="Medium"):
    k = (tam, peso)
    if k not in _cache_fonte:
        f = ImageFont.truetype(_FONTE, tam)
        f.set_variation_by_name(peso)
        _cache_fonte[k] = f
    return _cache_fonte[k]


def larg_texto(d, txt, f):
    b = d.textbbox((0, 0), txt, font=f)
    return b[2] - b[0], b[3] - b[1]


def texto_centrado(d, cx, y, txt, f, cor, sombra=None):
    w, _ = larg_texto(d, txt, f)
    if sombra:
        d.text((cx - w / 2 + sombra[0], y + sombra[1]), txt, font=f, fill=sombra[2])
    d.text((cx - w / 2, y), txt, font=f, fill=cor)
    return w


def quebrar(d, txt, f, largura_max):
    palavras, linhas, atual = txt.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if larg_texto(d, teste, f)[0] <= largura_max or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


# ------------------------------------------------------------------ imagens
def recortar_fundo_branco(im, tol=18):
    """
    Torna transparente SO' o branco ligado a's bordas (flood fill dos cantos).
    Um recorte por cor global comeria o capacete branco e o "B" do logo.
    """
    import numpy as np
    im = im.convert("RGBA")
    w, h = im.size
    rgb = im.convert("RGB")
    marca = (255, 0, 255)
    for canto in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
                  (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(rgb.getpixel(canto)) > (255 * 3 - tol * 3):
            ImageDraw.floodfill(rgb, canto, marca, thresh=tol * 3)
    # numpy: uma imagem grande em listas de tuplos rebenta a RAM do PC (4GB)
    arr = np.asarray(rgb)
    fora = (arr[:, :, 0] == marca[0]) & (arr[:, :, 1] == marca[1]) & (arr[:, :, 2] == marca[2])
    a = np.array(im.getchannel("A"))
    a[fora] = 0
    im.putalpha(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.1)))
    return im


def aparar(im):
    """Remove margens vazias (transparentes ou brancas)."""
    im = im.convert("RGBA")
    if im.getchannel("A").getextrema()[0] < 250:
        bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    else:
        cinza = im.convert("L").point(lambda v: 0 if v > 244 else 255)
        bb = cinza.getbbox()
    return im.crop(bb) if bb else im


def por_area(im, area_alvo, cx_max, cy_max):
    """
    Escala pela AREA, nao pela altura: e' o que faz um logo largo (Pingo Doce)
    e um quadrado (KFC) parecerem do mesmo tamanho ao olho.
    """
    w, h = im.size
    s = math.sqrt(area_alvo / float(w * h))
    s = min(s, cx_max / w, cy_max / h)
    return im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)


def cantos_redondos(im, raio):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1],
                                        radius=raio, fill=255)
    out = im.convert("RGBA").copy()
    a = out.getchannel("A")
    out.putalpha(Image.composite(a, Image.new("L", im.size, 0), m))
    return out


def _compor(tela, cam, x, y):
    """
    Cola uma camada PEQUENA na tela, cortando o que sai fora.

    Existe porque desenhar cada sombra/borda numa camada do tamanho da pagina
    (2480x3508 = 35 MB cada) estourava a RAM do PC (4 GB) a meio do flyer.
    """
    x, y = int(round(x)), int(round(y))
    lw, lh = cam.size
    W_, H_ = tela.size
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(lw, W_ - x), min(lh, H_ - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return tela
    tela.alpha_composite(cam.crop((sx0, sy0, sx1, sy1)),
                         (max(0, x), max(0, y)))
    return tela


def camada(w, h):
    return Image.new("RGBA", (max(1, int(w)), max(1, int(h))), (0, 0, 0, 0))


def sombra(tela, caixa, raio, desfoque, opacidade, desloc=(0, 10)):
    x0, y0, x1, y1 = [int(round(v)) for v in caixa]
    pad = int(desfoque * 3) + 6
    cam = camada((x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad)
    ImageDraw.Draw(cam).rounded_rectangle(
        [pad, pad, pad + (x1 - x0), pad + (y1 - y0)],
        radius=raio, fill=(2, 10, 22, opacidade))
    cam = cam.filter(ImageFilter.GaussianBlur(desfoque))
    return _compor(tela, cam, x0 - pad + desloc[0], y0 - pad + desloc[1])


def _lerp_cor(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def escurecer_faixa(tela, y0, y1, alpha_pico):
    """
    Escurecimento suave (scrim) SO' atras do topo/rodape, para o texto ler bem
    seja qual for o fundo (script hoje; foto do Danilo no dia em que existir).
    """
    W_, H_ = tela.size
    col = Image.new("L", (1, H_), 0)
    px = col.load()
    alt = max(1, y1 - y0)
    for i in range(H_):
        if y0 <= i < y1:
            t = (i - y0) / alt
            px[0, i] = int(alpha_pico * math.sin(t * math.pi))
    faixa = col.resize((W_, H_), Image.NEAREST).filter(ImageFilter.GaussianBlur(34))
    overlay = Image.new("RGBA", (W_, H_), (4, 10, 20, 0))
    overlay.putalpha(faixa)
    return Image.alpha_composite(tela, overlay)


# ----------------------------------------------------------------- conteudo
# Ordem EXATA pedida. Cada nome aparece uma unica vez (conferido no fim).
BLOCOS = [
    dict(n=1, nome="RESTAURANTES", icone="cat_restaurantes.png", cor=(249, 115, 22),
         logos=["mcdonalds", "kfc", "burgerking", "goola"],
         nota="Em breve: Mr Kebab"),
    dict(n=2, nome="SUPERMERCADOS", icone="cat_supermercados.png", cor=(22, 163, 74),
         logos=["auchan", "continente", "intermarche", "pingodoce"],
         nota="Em breve: Sabores de Casa Açaí"),
    dict(n=3, nome="FARMÁCIA", icone="cat_farmacia.png", cor=(28, 110, 242),
         logos=["wells"]),
    dict(n=4, nome="LOJAS", icone="cat_lojas.png", cor=(69, 90, 100),
         logos=["worten", "leroymerlin", "kiwoko", "zippy"]),
    dict(n=5, nome="BELEZA", icone="cat_beleza.png", cor=(99, 102, 241),
         logos=["ouroprata"]),
    dict(n=6, nome="FESTAS", icone="cat_festas.png", cor=(219, 39, 119),
         logos=["saboresbrasil"], texto="Bolos e salgados por encomenda."),
    dict(n=7, nome="SOBREMESAS", icone="cat_sobremesas.png", cor=(109, 40, 217),
         logos=["goola"], texto="Açaí fresquinho à tua porta."),
    dict(n=8, nome="LIMPEZA", icone="cat_limpeza.png", cor=(2, 132, 199),
         texto="Profissional de limpeza em tua casa, à hora que marcares."),
    dict(n=9, nome="BORA MOTORISTA", icone="cat_motorista.png", cor=(67, 56, 202),
         texto="Motorista particular, na hora ou com viagem marcada."),
    dict(n=10, nome="LAVAGEM AUTO", icone="cat_lavagem_auto.png", cor=(6, 182, 212),
         texto="Lava-rápido leva-e-traz: buscamos sujo, devolvemos a brilhar."),
    dict(n=11, nome="FAVORES", icone="cat_favores.png", cor=(20, 184, 166),
         texto="Precisas de algo resolvido? A gente vai por ti."),
    dict(n=12, nome="LEVAR COMPRAS", icone="cat_compras.png", cor=(22, 163, 74),
         texto="Compraste e não tens como levar? A gente leva."),
    dict(n=13, nome="ENVIAR ENCOMENDA", icone="cat_encomenda.png", cor=(249, 115, 22),
         texto="Manda um pacote de ponta a ponta da cidade."),
]

# Layout: (indices dos blocos, peso de altura). A ordem de leitura e' 1 -> 13.
LINHAS = [([1], 1.42), ([2], 1.42), ([3, 4], 1.16),
          ([5, 6, 7], 1.22), ([8, 9, 10], 0.80), ([11, 12, 13], 0.80)]
LARGURAS = {3: [0.33, 0.67]}   # Farmacia estreita, Lojas larga (4 logos)

# Pastilha com cor propria: o unico logo que a marca so' publica em branco e' o
# do Worten (usa-o sobre o vermelho da casa). Vermelho lido do header de
# worten.pt a 2026-08-28: rgb(229, 27, 21).
FUNDO_PASTILHA = {"worten": (229, 27, 21)}

_cache_logo = {}


def logo(nome):
    if nome not in _cache_logo:
        _cache_logo[nome] = aparar(Image.open(A("logos", nome + ".png")))
    return _cache_logo[nome]


# ------------------------------------------------------------------ cartoes
def desenhar_cartao(tela, caixa, cor):
    """
    Cartao premium de cor cheia da categoria: degrade (claro em cima, escuro
    em baixo), borda luminosa e cantos bem redondos. Substitui o cartao de
    vidro branco do V2 — pedido do Danilo depois de ver o estilo do Gemini.
    """
    x0, y0, x1, y1 = [int(round(v)) for v in caixa]
    r = 64
    tela = sombra(tela, (x0, y0, x1, y1), r, 34, 165, (0, 18))

    w, h = x1 - x0, y1 - y0
    claro = _lerp_cor(cor, (255, 255, 255), 0.30)
    escuro = _lerp_cor(cor, (0, 0, 0), 0.30)
    col = Image.new("RGB", (1, h))
    px = col.load()
    for i in range(h):
        px[0, i] = _lerp_cor(claro, escuro, (i / max(1, h - 1)) ** 1.3)
    grad = col.resize((w, h), Image.NEAREST)
    masc = Image.new("L", (w, h), 0)
    ImageDraw.Draw(masc).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    grad_rgba = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad_rgba.paste(grad, (0, 0))
    grad_rgba.putalpha(masc)
    tela.alpha_composite(grad_rgba, (x0, y0))

    cam = camada(w, h)
    d = ImageDraw.Draw(cam)
    luminoso = _lerp_cor(cor, (255, 255, 255), 0.55)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, outline=luminoso + (235,), width=7)
    d.rounded_rectangle([10, 10, w - 11, h - 11], radius=r - 10,
                        outline=(255, 255, 255, 100), width=3)
    return _compor(tela, cam, x0, y0)


def desenhar_icone(tela, b, x, y_topo, lado):
    """Ladrilho cat_*.png grande, a sair do canto superior esquerdo do cartao."""
    ic = Image.open(A("icons", b["icone"])).convert("RGBA").resize(
        (lado, lado), Image.LANCZOS)
    ic = cantos_redondos(ic, int(lado * 0.26))
    cx, cy = int(x), int(y_topo - lado * 0.60)   # 60% ca' fora: salta mais
    tela = sombra(tela, (cx, cy, cx + lado, cy + lado), int(lado * 0.26), 18, 150, (0, 10))
    aro = camada(lado + 16, lado + 16)
    ImageDraw.Draw(aro).rounded_rectangle(
        [0, 0, lado + 15, lado + 15],
        radius=int(lado * 0.30), fill=(255, 255, 255, 250))
    tela = _compor(tela, aro, cx - 8, cy - 8)
    tela.alpha_composite(ic, (cx, cy))
    return tela


PASTILHA_MIN_H = 200  # px na tela A4 (2480x3508) — pedido do Danilo: logo grande e nitido


def desenhar_bloco(tela, b, caixa):
    x0, y0, x1, y1 = [int(round(v)) for v in caixa]
    caixa = (x0, y0, x1, y1)
    tela = desenhar_cartao(tela, caixa, b["cor"])
    lado_ic = int(min(132, (y1 - y0) * 0.30))
    inset = 20
    tela = desenhar_icone(tela, b, x0 + inset, y0, lado_ic)

    d = ImageDraw.Draw(tela)
    larg_i = x1 - x0
    # nome da categoria, a' direita do icone — branco em negrito, com sombra
    # (o cartao agora e' de cor cheia, texto escuro nao lia).
    tam = 46 if larg_i > 1400 else (40 if larg_i > 900 else 34)
    f_nome = fonte(tam, "Black")
    tx = x0 + inset + lado_ic + 26
    ty = y0 + int(lado_ic * 0.40) - tam // 2 + 4
    while larg_texto(d, b["nome"], f_nome)[0] > (x1 - 40) - tx and tam > 24:
        tam -= 2
        f_nome = fonte(tam, "Black")
    d.text((tx + 3, ty + 4), b["nome"], font=f_nome, fill=(2, 8, 16, 150))
    d.text((tx, ty), b["nome"], font=f_nome, fill=BRANCO)

    # "Em breve: ..." vai para o canto superior direito, na mesma faixa do nome.
    # Por baixo dos logos roubava 52px de altura e empurrava a pastilha para
    # cima do nome.
    if b.get("nota"):
        fn = fonte(28, "Black")
        wn = larg_texto(d, b["nota"], fn)[0]
        nw, nh = wn + 44, fn.size + 20
        nx, ny = x1 - 30 - nw, y0 + int(lado_ic * 0.40) - nh // 2 + 4
        pil = camada(nw, nh)
        ImageDraw.Draw(pil).rounded_rectangle([0, 0, nw - 1, nh - 1], radius=nh // 2,
                                              fill=(255, 255, 255, 240))
        tela = _compor(tela, pil, nx, ny)
        d = ImageDraw.Draw(tela)
        d.text((nx + 22, ny + 8), b["nota"], font=fn, fill=b["cor"])

    # a zona de conteudo comeca DEPOIS do nome — senao, nos blocos baixos, o
    # texto e os logos escrevem por cima do nome.
    y = max(y0 + lado_ic * 0.40 + 12, ty + tam + 18)
    zona_baixo = y1 - 22

    if b.get("logos"):
        n = len(b["logos"])
        alt_nota = 0        # a nota subiu para junto do nome
        alt_txt = 54 if b.get("texto") else 0
        disp_y = (zona_baixo - alt_nota - alt_txt) - y
        cel_w = (larg_i - 60) / n
        # Pastilha branca: altura MINIMA de 200px (pedido do Danilo — logos
        # pequenos era a queixa). So' cresce acima disso se houver espaco.
        ph = max(PASTILHA_MIN_H, disp_y * (0.98 if n == 1 else 0.97))
        if os.environ.get("DEBUG_FLYER"):
            print(f"bloco {b['n']:>2} {b['nome']:<14} disp_y={disp_y:6.1f} ph={ph:6.1f} "
                  f"{'OVERFLOW!' if ph > disp_y + 4 else 'ok'}")
        pad = 18
        util_h = ph - 2 * pad
        util_w = cel_w * 0.95 - 2 * pad
        for i, nome in enumerate(b["logos"]):
            # escala pela ALTURA (logo enche pelo menos ~70% da pastilha em pe'),
            # so' recua se a largura da celula nao deixar — nunca esticado.
            im0 = logo(nome)
            w0, h0 = im0.size
            alvo_h = util_h        # enche a area util toda (~85% da pastilha)
            esc = min(alvo_h / h0, util_w / w0)
            im = im0.resize((max(1, int(w0 * esc)), max(1, int(h0 * esc))), Image.LANCZOS)
            # a pastilha acompanha a largura do logo, mas a ALTURA e' igual para
            # todos — e' isso que alinha a fila.
            pw = min(max(im.width + 2 * pad, ph), cel_w * 0.98)
            cxp = x0 + 30 + cel_w * i + cel_w / 2
            cyp = y + disp_y / 2
            cor_pastilha = FUNDO_PASTILHA.get(nome, (255, 255, 255))
            orla = cor_pastilha if nome in FUNDO_PASTILHA else (226, 232, 240)
            tela = sombra(tela, (cxp - pw / 2, cyp - ph / 2, cxp + pw / 2, cyp + ph / 2),
                          24, 14, 90, (0, 6))
            pil = camada(pw, ph)
            ImageDraw.Draw(pil).rounded_rectangle(
                [0, 0, int(pw) - 1, int(ph) - 1],
                radius=24, fill=cor_pastilha + (255,), outline=orla + (255,), width=3)
            tela = _compor(tela, pil, cxp - pw / 2, cyp - ph / 2)
            tela.alpha_composite(im, (int(cxp - im.width / 2), int(cyp - im.height / 2)))
        d = ImageDraw.Draw(tela)
        y += disp_y

    if b.get("texto"):
        f = fonte(26 if larg_i < 900 else 30, "SemiBold")
        linhas = quebrar(d, b["texto"], f, larg_i - 88)
        alt = len(linhas) * (f.size + 9)
        yy = y + max(0, (zona_baixo - y - alt) / 2)
        for ln in linhas:
            texto_centrado(d, (x0 + x1) / 2, yy, ln, f, (255, 255, 255),
                           sombra=(0, 3, (2, 8, 16, 130)))
            yy += f.size + 9

    return tela


# ---------------------------------------------------------------------- QR
def fazer_qr(url, lado):
    """
    Correcao de erro M — com H os modulos ficam pequenos demais e o telemovel
    nao le em papel pequeno (licao dos flyers do Mr Kebab e da Ouro e Prata).
    """
    q = segno.make(url, error='m')
    buf = io.BytesIO()
    q.save(buf, kind="png", scale=20, border=2, dark="#0F172A", light="#FFFFFF")
    buf.seek(0)
    return Image.open(buf).convert("RGBA").resize((lado, lado), Image.NEAREST)


# ------------------------------------------------------------------ montar
def montar():
    tela = gerar_fundo(W, H).convert("RGBA")
    y_rodape = H - BLEED - ALT_RODAPE
    tela = escurecer_faixa(tela, BLEED, BLEED + 620, 100)
    tela = escurecer_faixa(tela, y_rodape - 60, H - BLEED, 70)
    d = ImageDraw.Draw(tela)

    # ---------------- topo
    y = BLEED + 30
    lg = aparar(recortar_fundo_branco(Image.open(A("brand", "bora_logo.png"))))
    lg_w = 470
    lg = lg.resize((lg_w, int(lg.height * lg_w / lg.width)), Image.LANCZOS)
    tela.alpha_composite(lg, ((W - lg_w) // 2, y))
    y += lg.height + 16

    # titulo BRANCO com sombra escura: o fundo passou a ser noturno (o verde
    # #16A34A so' lia quando havia um halo claro por tras)
    f_tit = fonte(116, "Black")
    texto_centrado(d, W / 2, y, "TUDO NUM APP SÓ", f_tit, BRANCO,
                   sombra=(0, 7, (2, 10, 20, 190)))
    y += 128

    f_sub = fonte(42, "Medium")
    texto_centrado(d, W / 2, y,
                   "Comida, mercado, motorista e limpeza —", f_sub, (223, 238, 230),
                   sombra=(0, 3, (2, 10, 20, 150)))
    y += 52
    texto_centrado(d, W / 2, y,
                   "o Bora App resolve com certeza.", f_sub, (223, 238, 230),
                   sombra=(0, 3, (2, 10, 20, 150)))
    y += 46

    # ---------------- corpo: 6 linhas, 13 blocos
    # (y_rodape ja' reservado no topo da funcao, antes do escurecimento)
    GAP_V, GAP_H = 52, 42
    disp = (y_rodape - 30) - y
    por_n = {b["n"]: b for b in BLOCOS}

    # Altura POR NECESSIDADE, nao por peso arbitrario: uma linha com logos tem
    # de caber cabecalho + pastilha de 200px + margens, senao a pastilha
    # transborda por cima do nome (era o que acontecia em 5 dos 13 blocos).
    def altura_minima(indices):
        pior = 0
        larg_col = LARG / len(indices)
        tam_nome = 46 if larg_col > 1400 else (40 if larg_col > 900 else 34)
        for idx in indices:
            b = por_n[idx]
            cab = 53 + tam_nome + 16                # icone dentro + nome + folga
            corpo = 0
            if b.get("logos"):
                corpo += PASTILHA_MIN_H + 16
            if b.get("texto"):
                corpo += 46 if b.get("logos") else 78
            pior = max(pior, cab + corpo + 22)
        return pior

    minimos = [altura_minima(ix) for ix, _ in LINHAS]
    folga = disp - sum(minimos) - GAP_V * (len(LINHAS) - 1)
    if folga < 0:                       # nao cabe: aperta os intervalos primeiro
        GAP_V = max(30, GAP_V + int(folga / (len(LINHAS) - 1)))
        folga = disp - sum(minimos) - GAP_V * (len(LINHAS) - 1)
    if os.environ.get("DEBUG_FLYER"):
        print(f"[layout] disp={disp:.0f} minimos={sum(minimos):.0f} "
              f"gap={GAP_V} folga={folga:.0f}")
    # o que sobra distribui-se pelas linhas com logos (e' onde faz diferenca)
    peso_folga = [2.0 if any(por_n[i].get("logos") for i in ix) else 1.0
                  for ix, _ in LINHAS]
    tot_pf = sum(peso_folga)
    alturas = [m + max(0, folga) * pf / tot_pf for m, pf in zip(minimos, peso_folga)]

    yy = y
    for li, (indices, _peso) in enumerate(LINHAS):
        alt = alturas[li]
        fracoes = LARGURAS.get(indices[0], [1.0 / len(indices)] * len(indices))
        xx = CX0
        for k, idx in enumerate(indices):
            w_bloco = LARG * fracoes[k] - (GAP_H * (len(indices) - 1) / len(indices))
            tela = desenhar_bloco(tela, por_n[idx],
                                  (xx, yy, xx + w_bloco, yy + alt))
            xx += w_bloco + GAP_H
        yy += alt + GAP_V

    # ---------------- rodape
    d = ImageDraw.Draw(tela)
    cx_r0, cx_r1 = CX0, CX1
    caixa_r = (cx_r0, y_rodape, cx_r1, H - BLEED - 24)
    tela = sombra(tela, caixa_r, 46, 26, 150, (0, 16))
    # rodape ESCURO, como no visual aprovado a 28/08 (era branco no V2)
    rw, rh = cx_r1 - cx_r0, (H - BLEED - 24) - y_rodape
    cam = camada(rw, rh)
    ImageDraw.Draw(cam).rounded_rectangle([0, 0, rw - 1, rh - 1], radius=46,
                                          fill=(18, 26, 32, 246),
                                          outline=VERDE + (235,), width=6)
    tela = _compor(tela, cam, cx_r0, y_rodape)
    d = ImageDraw.Draw(tela)

    # Tres colunas: QR | app | QR. Ganha-se pela LARGURA, o que deixa os QR
    # grandes (400px) sem roubar altura aos blocos. Com 268px os modulos ficavam
    # a ~2,3px na prova de leitura e o descodificador via-os mas nao os lia.
    qr_lado = QR_LADO
    qy = y_rodape + QR_OFFSET_Y
    f_et = fonte(36, "Black")
    f_et2 = fonte(28, "Medium")
    margem_qr = 22

    for i, (url, et, et2, cor) in enumerate([
            (PLAY_URL, "ANDROID", "Play Store", VERDE),
            (WEB_URL, "iPHONE / PC", "abre no browser", LARANJA)]):
        qx = (CX0 + QR_MARGEM_X) if i == 0 else (CX1 - QR_MARGEM_X - qr_lado)
        mw = qr_lado + 2 * margem_qr
        moldura = camada(mw, mw)
        ImageDraw.Draw(moldura).rounded_rectangle(
            [0, 0, mw - 1, mw - 1],
            radius=26, fill=(255, 255, 255, 255), outline=cor + (255,), width=5)
        tela = _compor(tela, moldura, qx - margem_qr, qy - margem_qr)
        tela.alpha_composite(fazer_qr(url, qr_lado), (int(qx), int(qy)))
        d = ImageDraw.Draw(tela)
        # etiquetas em claro: o rodape agora e' escuro
        texto_centrado(d, qx + qr_lado / 2, qy + qr_lado + 38, et, f_et,
                       _lerp_cor(cor, (255, 255, 255), 0.35))
        texto_centrado(d, qx + qr_lado / 2, qy + qr_lado + 84, et2, f_et2,
                       (176, 190, 200))

    # coluna do meio: icone do aplicativo + nome
    ic_lado = 190
    ic = cantos_redondos(Image.open(A("brand", "apple-touch-icon.png"))
                         .convert("RGBA").resize((ic_lado, ic_lado), Image.LANCZOS),
                         int(ic_lado * 0.24))
    cxm = W / 2
    iy = qy + 40
    tela = sombra(tela, (cxm - ic_lado / 2, iy, cxm + ic_lado / 2, iy + ic_lado),
                  int(ic_lado * 0.24), 16, 120, (0, 9))
    tela.alpha_composite(ic, (int(cxm - ic_lado / 2), int(iy)))
    d = ImageDraw.Draw(tela)
    f_app = fonte(54, "Black")
    f_app2 = fonte(37, "SemiBold")
    ty2 = iy + ic_lado + 26
    texto_centrado(d, cxm, ty2, "BORA APP", f_app, BRANCO)
    texto_centrado(d, cxm, ty2 + 64, "GUARDA", f_app,
                   _lerp_cor(VERDE, (255, 255, 255), 0.35))
    texto_centrado(d, cxm, ty2 + 134, "descarrega na Play Store", f_app2,
                   (186, 199, 208))

    # ---------------- margem branca da grafica (8mm)
    moldura = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    buraco = Image.new("L", (W, H), 0)
    ImageDraw.Draw(buraco).rounded_rectangle(
        [BLEED, BLEED, W - BLEED, H - BLEED], radius=34, fill=255)
    tela = Image.composite(tela, moldura, buraco)

    return tela.convert("RGB")


if __name__ == "__main__":
    im = montar()
    os.makedirs(SAIDA, exist_ok=True)
    p1 = os.path.join(SAIDA, "flyer-bora-app-A4-grafica.png")
    im.save(p1, dpi=(300, 300), optimize=True)
    p2 = os.path.join(SAIDA, "flyer-bora-app-whatsapp.jpg")
    im.resize((1080, 1620), Image.LANCZOS).convert("RGB").save(
        p2, quality=90, optimize=True, progressive=True)
    print("grafica :", p1, os.path.getsize(p1) // 1024, "KB")
    print("whatsapp:", p2, os.path.getsize(p2) // 1024, "KB")

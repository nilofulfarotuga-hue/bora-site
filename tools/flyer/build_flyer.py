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
SAIDA = os.path.join(os.path.expanduser("~"), "Downloads")

# ---------------------------------------------------------------- dimensoes
W, H = 2480, 3508          # A4 a 300dpi
BLEED = 95                 # margem branca de 8mm para a grafica
PAD = 72
CX0, CX1 = BLEED + PAD, W - BLEED - PAD
LARG = CX1 - CX0

VERDE = (22, 163, 74)
LARANJA = (249, 115, 22)
TINTA = (15, 23, 42)       # texto escuro sobre vidro claro
TINTA_SUAVE = (71, 85, 105)
BRANCO = (255, 255, 255)

QR_LADO = int(os.environ.get("QR_LADO", 500))
ALT_RODAPE = 736
QR_OFFSET_Y = 40      # do topo do cartao do rodape ate' ao topo do QR
QR_MARGEM_X = 54      # da margem do cartao ate' ao QR   # ver prova de leitura em verificar.py

PLAY_URL = "https://play.google.com/store/apps/details?id=pt.boraapp.bora"
WEB_URL = "https://bora-app-web.pages.dev/#/registo-cliente"

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


def sombra(tela, caixa, raio, desfoque, opacidade, desloc=(0, 10)):
    x0, y0, x1, y1 = caixa
    cam = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    ImageDraw.Draw(cam).rounded_rectangle(
        [x0 + desloc[0], y0 + desloc[1], x1 + desloc[0], y1 + desloc[1]],
        radius=raio, fill=(2, 10, 22, opacidade))
    return Image.alpha_composite(tela, cam.filter(ImageFilter.GaussianBlur(desfoque)))


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
    """Cartao de vidro: branco translucido, cantos redondos, orla da categoria."""
    x0, y0, x1, y1 = caixa
    r = 46
    tela = sombra(tela, caixa, r, 22, 120, (0, 14))
    cam = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    d.rounded_rectangle(caixa, radius=r, fill=(255, 255, 255, 240))
    d.rounded_rectangle(caixa, radius=r, outline=cor + (235,), width=5)
    d.rounded_rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], radius=r - 8,
                        outline=(255, 255, 255, 180), width=3)
    return Image.alpha_composite(tela, cam)


def desenhar_icone(tela, b, x, y_topo, lado):
    """Ladrilho cat_*.png a cavalgar a aresta de cima do cartao."""
    ic = Image.open(A("icons", b["icone"])).convert("RGBA").resize(
        (lado, lado), Image.LANCZOS)
    ic = cantos_redondos(ic, int(lado * 0.26))
    cx, cy = int(x), int(y_topo - lado // 2)
    tela = sombra(tela, (cx, cy, cx + lado, cy + lado), int(lado * 0.26), 16, 130, (0, 9))
    aro = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    ImageDraw.Draw(aro).rounded_rectangle(
        [cx - 7, cy - 7, cx + lado + 7, cy + lado + 7],
        radius=int(lado * 0.30), fill=(255, 255, 255, 250))
    tela = Image.alpha_composite(tela, aro)
    tela.alpha_composite(ic, (cx, cy))
    return tela


def desenhar_bloco(tela, b, caixa):
    x0, y0, x1, y1 = [int(round(v)) for v in caixa]
    caixa = (x0, y0, x1, y1)
    tela = desenhar_cartao(tela, caixa, b["cor"])
    lado_ic = int(min(104, (y1 - y0) * 0.34))
    tela = desenhar_icone(tela, b, x0 + 46, y0, lado_ic)

    d = ImageDraw.Draw(tela)
    larg_i = x1 - x0
    # nome da categoria, a' direita do icone
    tam = 46 if larg_i > 1400 else (40 if larg_i > 900 else 34)
    f_nome = fonte(tam, "Black")
    tx = x0 + 46 + lado_ic + 34
    ty = y0 + int(lado_ic * 0.5) - tam // 2 + 4
    while larg_texto(d, b["nome"], f_nome)[0] > (x1 - 40) - tx and tam > 24:
        tam -= 2
        f_nome = fonte(tam, "Black")
    d.text((tx, ty), b["nome"], font=f_nome, fill=TINTA)
    y_sublinhado = ty + tam + 14
    d.line([tx, y_sublinhado, min(tx + 120, x1 - 40), y_sublinhado],
           fill=b["cor"], width=6)

    # a zona de conteudo comeca DEPOIS do nome e do sublinhado — senao, nos
    # blocos baixos, o texto e os logos escrevem por cima do nome.
    y = max(y0 + lado_ic * 0.5 + 18, y_sublinhado + 16)
    zona_baixo = y1 - 26

    if b.get("logos"):
        n = len(b["logos"])
        # a nota "Em breve" tem faixa propria: nunca por cima dos logos
        alt_nota = 66 if b.get("nota") else 0
        alt_txt = 54 if b.get("texto") else 0
        disp_y = (zona_baixo - alt_nota - alt_txt) - y
        cel_w = (larg_i - 72) / n
        # Pastilhas TODAS do mesmo tamanho dentro do bloco — e' o que faz a fila
        # parecer arrumada. O logo e' que se ajusta por AREA la' dentro, para um
        # logo largo (Pingo Doce) e um quadrado (KFC) pesarem o mesmo ao olho.
        ph = disp_y * (0.98 if n == 1 else 0.96)
        pad = 24
        util_h = ph - 2 * pad
        util_w = cel_w * 0.92 - 2 * pad
        # area alvo em funcao da ALTURA util: um logo quadrado enche a pastilha
        # em altura; um logo largo fica mais baixo mas mais comprido, e os dois
        # acabam com o mesmo peso visual.
        area = util_h * util_h * 1.55
        for i, nome in enumerate(b["logos"]):
            im = por_area(logo(nome), area, util_w, util_h)
            # a pastilha acompanha a largura do logo, mas a ALTURA e' igual para
            # todos — e' isso que alinha a fila.
            pw = min(max(im.width + 2 * pad, ph), cel_w * 0.96)
            cxp = x0 + 36 + cel_w * i + cel_w / 2
            cyp = y + disp_y / 2
            cor_pastilha = FUNDO_PASTILHA.get(nome, (255, 255, 255))
            orla = cor_pastilha if nome in FUNDO_PASTILHA else (226, 232, 240)
            pil = Image.new("RGBA", tela.size, (0, 0, 0, 0))
            ImageDraw.Draw(pil).rounded_rectangle(
                [cxp - pw / 2, cyp - ph / 2, cxp + pw / 2, cyp + ph / 2],
                radius=24, fill=cor_pastilha + (255,), outline=orla + (255,), width=3)
            tela = Image.alpha_composite(tela, pil)
            tela.alpha_composite(im, (int(cxp - im.width / 2), int(cyp - im.height / 2)))
        d = ImageDraw.Draw(tela)
        y += disp_y

    if b.get("texto"):
        f = fonte(30 if larg_i < 900 else 34, "Medium")
        linhas = quebrar(d, b["texto"], f, larg_i - 96)
        alt = len(linhas) * (f.size + 12)
        yy = y + max(0, ((zona_baixo - (46 if b.get("nota") else 0)) - y - alt) / 2)
        for ln in linhas:
            texto_centrado(d, (x0 + x1) / 2, yy, ln, f, TINTA_SUAVE)
            yy += f.size + 12

    if b.get("nota"):
        f = fonte(31, "SemiBold")
        w_n, _ = larg_texto(d, b["nota"], f)
        cy = zona_baixo - 48
        pil = Image.new("RGBA", tela.size, (0, 0, 0, 0))
        ImageDraw.Draw(pil).rounded_rectangle(
            [(x0 + x1) / 2 - w_n / 2 - 26, cy - 10,
             (x0 + x1) / 2 + w_n / 2 + 26, cy + f.size + 14],
            radius=26, fill=b["cor"] + (32,), outline=b["cor"] + (140,), width=3)
        tela = Image.alpha_composite(tela, pil)
        d = ImageDraw.Draw(tela)
        texto_centrado(d, (x0 + x1) / 2, cy, b["nota"], f, b["cor"])

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
    d = ImageDraw.Draw(tela)

    # ---------------- topo
    y = BLEED + 44
    lg = aparar(recortar_fundo_branco(Image.open(A("brand", "bora_logo.png"))))
    lg_w = 620
    lg = lg.resize((lg_w, int(lg.height * lg_w / lg.width)), Image.LANCZOS)
    tela.alpha_composite(lg, ((W - lg_w) // 2, y))
    y += lg.height + 26

    f_tit = fonte(112, "Black")
    texto_centrado(d, W / 2, y, "TUDO NUM APP SÓ", f_tit, VERDE,
                   sombra=(0, 6, (255, 255, 255, 200)))
    y += 128

    f_sub = fonte(43, "Medium")
    texto_centrado(d, W / 2, y,
                   "Comida, mercado, motorista e limpeza —", f_sub, (226, 240, 232))
    y += 56
    texto_centrado(d, W / 2, y,
                   "o Bora App resolve com certeza.", f_sub, (226, 240, 232))
    y += 58

    # ---------------- rodape (reservado primeiro, para o corpo saber o limite)
    y_rodape = H - BLEED - ALT_RODAPE

    # ---------------- corpo: 6 linhas, 13 blocos
    GAP_V, GAP_H = 40, 30
    disp = (y_rodape - 30) - y
    soma = sum(p for _, p in LINHAS)
    unidade = (disp - GAP_V * (len(LINHAS) - 1)) / soma

    por_n = {b["n"]: b for b in BLOCOS}
    yy = y
    for indices, peso in LINHAS:
        alt = unidade * peso
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
    tela = sombra(tela, caixa_r, 46, 24, 130, (0, 14))
    cam = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    ImageDraw.Draw(cam).rounded_rectangle(caixa_r, radius=46,
                                          fill=(255, 255, 255, 245),
                                          outline=VERDE + (235,), width=5)
    tela = Image.alpha_composite(tela, cam)
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
        moldura = Image.new("RGBA", tela.size, (0, 0, 0, 0))
        ImageDraw.Draw(moldura).rounded_rectangle(
            [qx - margem_qr, qy - margem_qr,
             qx + qr_lado + margem_qr, qy + qr_lado + margem_qr],
            radius=26, fill=(255, 255, 255, 255), outline=cor + (255,), width=5)
        tela = Image.alpha_composite(tela, moldura)
        tela.alpha_composite(fazer_qr(url, qr_lado), (int(qx), int(qy)))
        d = ImageDraw.Draw(tela)
        texto_centrado(d, qx + qr_lado / 2, qy + qr_lado + 38, et, f_et, cor)
        texto_centrado(d, qx + qr_lado / 2, qy + qr_lado + 84, et2, f_et2, TINTA_SUAVE)

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
    texto_centrado(d, cxm, ty2, "BORA APP", f_app, TINTA)
    texto_centrado(d, cxm, ty2 + 64, "GUARDA", f_app, VERDE)
    texto_centrado(d, cxm, ty2 + 134, "descarrega na Play Store", f_app2, TINTA_SUAVE)

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

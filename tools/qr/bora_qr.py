#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O gerador de QR do Bora — UM SÓ, para o papel e para as redes.

Escrito a 2026-09-05 (missao `redes-tudo-05-09`, Bloco A). A logica do QR nao e'
nova: sai do `tools/flyer/build_flyer.py`, que ja' a tinha provada em papel. Foi
promovida a modulo para o flyer, as pecas das redes e os anuncios pagos usarem
EXACTAMENTE o mesmo codigo e o mesmo destino. Se um dia o destino mudar, muda
aqui e muda em todo o lado.

Porque e' que isto existe:
  A auditoria de 05/09 provou que as pecas publicadas no Facebook e no Instagram
  nao tinham QR nenhum, e que o endereco impresso nelas era `play.google.com/store`
  -- a loja generica, nao o Bora. Quem via so' a imagem nao chegava a' app.
  Com campanha paga a comecar, isso e' dinheiro deitado fora.

Correccao de erro M, e nao H:
  com H os modulos ficam pequenos demais e o telemovel nao le' em papel pequeno.
  Licao dos flyers do Mr Kebab e da Ouro e Prata, ja' registada no build_flyer.
"""
import io
import os

import segno
from PIL import Image

# ---------------------------------------------------------------- o destino

# A pagina de destino. NAO apontar o QR directamente a' Play Store: assim o
# telemovel do iPhone e o computador tambem tem caminho, e a origem fica medida.
BASE_DESTINO = "https://boraguarda.com/baixar"

# Onde a pagina de destino manda cada um. Aqui so' para quem precise do link cru.
LINK_PLAY = "https://play.google.com/store/apps/details?id=pt.boraapp.bora"
LINK_WEB = "https://app.boraguarda.com"

# As origens que existem. Uma peca so' pode declarar uma destas -- se inventar
# outra, o portao reprova, e e' de proposito: origem escrita a' mao nao se mede.
ORIGENS = {
    "qr-feed": "publicacao no feed (Facebook/Instagram)",
    "qr-story": "story",
    "qr-reel": "reel",
    "qr-carrossel": "carrossel",
    "qr-grupo": "publicacao em grupo do Facebook",
    "qr-flyer": "papel: flyer, cartaz, autocolante",
    "pago": "anuncio pago",
    "bio": "link da bio do Instagram / botao da pagina do Facebook",
    "site": "o QR da propria pagina /baixar, para quem esta no computador",
    "qr-site": "o QR da pagina inicial do site (boraguarda.com, bloco 'Descarrega o Bora agora')",
}


def link_destino(origem):
    """O endereco que vai dentro do QR e dentro do texto da peca."""
    if origem not in ORIGENS:
        raise ValueError(
            "origem desconhecida: %r. As que existem: %s"
            % (origem, ", ".join(sorted(ORIGENS)))
        )
    return "%s?de=%s" % (BASE_DESTINO, origem)


def endereco_curto():
    """O que se escreve por baixo do QR, para quem prefere teclar."""
    return "boraguarda.com/baixar"


# -------------------------------------------------------------------- o QR

def fazer_qr(url, lado, borda=2):
    """Devolve o QR como imagem RGBA de `lado` x `lado` pixeis.

    `borda=2` sao 2 modulos de margem branca -- o minimo que a norma pede e' 4,
    mas em peca digital 2 chega porque o QR e' colado sobre um cartao branco
    proprio (ver `qr_em_cartao`), que acrescenta a margem que falta.
    """
    q = segno.make(url, error="m")
    buf = io.BytesIO()
    q.save(buf, kind="png", scale=20, border=borda, dark="#0F172A", light="#FFFFFF")
    buf.seek(0)
    return Image.open(buf).convert("RGBA").resize((lado, lado), Image.NEAREST)


def qr_em_cartao(url, lado, margem=None, raio=None, logo=None):
    """O QR dentro de um cartao branco arredondado, como o resto da marca.

    O cartao NAO e' enfeite: e' a margem branca que faz o telemovel ler o codigo
    quando a peca por baixo e' uma fotografia escura. Sem ele, o QR sobre a foto
    perde o contraste da borda e deixa de ler a um metro.

    `logo` -- caminho para o logo do Bora, colado ao centro. A correccao M
    aguenta ~15% de area perdida; ficamos por 18% do lado (≈3.2% da area), com
    folga larga. Ao centro fica sempre dentro dessa folga.
    """
    from PIL import ImageDraw

    margem = int(lado * 0.09) if margem is None else margem
    raio = int(lado * 0.10) if raio is None else raio
    total = lado + 2 * margem

    cartao = Image.new("RGBA", (total, total), (0, 0, 0, 0))
    d = ImageDraw.Draw(cartao)
    d.rounded_rectangle([0, 0, total - 1, total - 1], radius=raio,
                        fill=(255, 255, 255, 255))

    qr = fazer_qr(url, lado)
    cartao.alpha_composite(qr, (margem, margem))

    if logo and os.path.exists(logo):
        alvo = int(lado * 0.18)
        lg = Image.open(logo).convert("RGBA")
        lg = lg.resize((alvo, int(lg.height * alvo / lg.width)), Image.LANCZOS)
        # fundo branco por tras do logo, senao o logo cai em cima dos modulos
        pad = int(alvo * 0.14)
        base = Image.new("RGBA", (lg.width + 2 * pad, lg.height + 2 * pad),
                         (255, 255, 255, 255))
        base.alpha_composite(lg, (pad, pad))
        cartao.alpha_composite(
            base, ((total - base.width) // 2, (total - base.height) // 2))

    return cartao


# -------------------------------------------------------- colar numa peca

# O logo, quando existe de cada lado. Na VPS das redes vive noutro sitio.
LOGOS = [
    "/opt/data/social/imagens/bora_logo.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "flyer", "assets", "brand", "bora_logo.png"),
]


def _logo_disponivel():
    for c in LOGOS:
        if os.path.exists(c):
            return c
    return None


def colar_qr(imagem, origem, fraccao=0.155, margem_frac=0.045, logo=True,
             canto="cima-direita"):
    """Cola o QR da `origem` na peca e devolve-a.

    UMA funcao para todos os moldes -- feed, story, reel e carrossel -- para o
    QR ficar sempre no mesmo sitio e do mesmo tamanho relativo. Se cada molde
    colasse o seu, mais tarde ou mais cedo um deles ficava por colar e ninguem
    dava por isso ate' a campanha ja' estar a correr.

    `fraccao` -- o lado do QR em fraccao da largura da peca. 0.155 de 1080 da'
    167 px, que se le' bem no telemovel a olhar para o ecra de outra pessoa e
    nao come a peca. Nao baixar de 0.12.

    `canto` -- "cima-direita" por defeito, e nao em baixo como e' habitual.
    Motivo, medido e nao suposto (2026-09-05): em baixo o QR tapava o fim do
    selo laranja -- "Codigo BEMVINDO no primeiro pedid[o]" ficava cortado. Em
    todos os moldes da casa o bloco de texto vive em baixo e o logo em cima a'
    esquerda, portanto o canto de cima a' direita e' o unico que esta' sempre
    livre. Uma peca com o QR por cima da chamada e' pior do que uma peca sem QR.
    """
    im = imagem.convert("RGBA") if imagem.mode != "RGBA" else imagem.copy()
    lado = max(96, int(im.width * fraccao))
    cartao = qr_em_cartao(link_destino(origem), lado,
                          logo=_logo_disponivel() if logo else None)
    m = int(im.width * margem_frac)
    if canto == "cima-direita":
        pos = (im.width - cartao.width - m, m)
    elif canto == "baixo-direita":
        pos = (im.width - cartao.width - m, im.height - cartao.height - m)
    elif canto == "cima-esquerda":
        pos = (m, m)
    else:
        raise ValueError("canto desconhecido: %r" % canto)
    im.alpha_composite(cartao, pos)
    return im


# ------------------------------------------------------------------- leitura

def ler_qr(imagem):
    """Descodifica os QR de uma imagem. Devolve o conjunto de textos lidos.

    Usa o detector do OpenCV, o mesmo que o `tools/flyer/verificar.py` ja' usava
    -- uma so' ferramenta de leitura em toda a casa, para uma peca nunca passar
    num verificador e falhar noutro.

    `imagem` pode ser um caminho ou uma imagem PIL.
    """
    import cv2
    import numpy as np

    if isinstance(imagem, str):
        imagem = Image.open(imagem)
    im = imagem.convert("RGB")

    lidos = set()
    det = cv2.QRCodeDetector()
    # Varias larguras: o telemovel nao le' sempre a' mesma distancia, e o
    # detector do OpenCV e' sensivel a escala. Se le' a alguma, le'.
    for largura in (im.width, 1400, 1080, 700, 500):
        if largura > im.width:
            continue
        alt = int(im.height * largura / im.width)
        arr = np.array(im.resize((largura, alt), Image.LANCZOS))
        try:
            ok, textos, _, _ = det.detectAndDecodeMulti(arr)
            if ok:
                lidos |= {t for t in textos if t}
        except cv2.error:
            pass
        if not lidos:
            try:
                t, _, _ = det.detectAndDecode(arr)
                if t:
                    lidos.add(t)
            except cv2.error:
                pass
    return lidos


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--ler":
        for t in sorted(ler_qr(sys.argv[2])) or ["(nenhum QR lido)"]:
            print(t)
    else:
        origem = sys.argv[1] if len(sys.argv) > 1 else "qr-feed"
        saida = sys.argv[2] if len(sys.argv) > 2 else "qr-%s.png" % origem
        url = link_destino(origem)
        qr_em_cartao(url, 600).save(saida)
        print("%s -> %s" % (url, saida))

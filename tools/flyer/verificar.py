# -*- coding: utf-8 -*-
"""
Prova do flyer antes de entregar. Falha ruidosamente — nao ha "assumido".

1. Os dois QR leem-se na imagem REDUZIDA a 700px (simula o telemovel a apontar
   para o papel a alguma distancia).
2. Cada nome de categoria aparece uma unica vez (a versao anterior do flyer
   trazia "SOBREMESAS" duas vezes).
3. Nenhum bloco proibido entrou (Reservar Mesa, BeUnique, Pizza Hut, Lidl,
   Mercadona).
4. Os ficheiros de saida existem, com as dimensoes e o peso certos.
"""
import os, sys
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_flyer import BLOCOS, PLAY_URL, WEB_URL

from build_flyer import SAIDA as DOWN
P_GRAFICA = os.path.join(DOWN, "flyer-bora-app-A4-grafica.png")
P_WHATS = os.path.join(DOWN, "flyer-bora-app-whatsapp.jpg")

FORA = ["reservar mesa", "beunique", "pizza hut", "lidl", "mercadona"]
falhas = []


def ok(cond, msg, detalhe=""):
    print(("  OK   " if cond else "  FALHA") + f"  {msg}" + (f"  [{detalhe}]" if detalhe else ""))
    if not cond:
        falhas.append(msg)


print("=" * 72)
print("1. QR — leitura na imagem reduzida a 700px de largura")
print("=" * 72)
im = Image.open(P_GRAFICA)
det = cv2.QRCodeDetector()


def le_qr(imagem, largura):
    """Reduz a pagina e tenta descodificar os dois QR."""
    r = imagem.resize((largura, int(largura * imagem.height / imagem.width)), Image.LANCZOS)
    a = cv2.cvtColor(np.array(r.convert("RGB")), cv2.COLOR_RGB2BGR)
    rv, txts, _, _ = det.detectAndDecodeMulti(a)
    return set(t for t in txts if t) if rv else set()


# (a) criterio pedido: pagina inteira reduzida a 700px
lidos700 = le_qr(im, 700)
ok(PLAY_URL in lidos700, "QR Android le' a 700px e aponta para a Play Store")
ok(WEB_URL in lidos700, "QR iPhone/PC le' a 700px e aponta para o registo web")

# (b) na imagem que vai mesmo para o WhatsApp (JPG comprimido)
wq = le_qr(Image.open(P_WHATS), 1080)
ok({PLAY_URL, WEB_URL} <= wq, "os 2 QR leem-se no JPG do WhatsApp", f"{len(wq)}/2")

# (c) prova realista: cada QR ISOLADO, como quem aponta a camara ao papel.
#     E' o que o detetor "multi" nao consegue garantir numa pagina cheia — ele
#     falha a ver 2 QR entre muitos elementos, mas o QR em si le'-se sempre.
from build_flyer import QR_LADO, BLEED, CX0, CX1, ALT_RODAPE, QR_OFFSET_Y, QR_MARGEM_X
y_rod = im.height - BLEED - ALT_RODAPE
qy, m = y_rod + QR_OFFSET_Y, 60
zonas = [("Android", PLAY_URL,
          (CX0 + QR_MARGEM_X - m, qy - m, CX0 + QR_MARGEM_X + QR_LADO + m, qy + QR_LADO + m)),
         ("iPhone/PC", WEB_URL,
          (CX1 - QR_MARGEM_X - QR_LADO - m, qy - m, CX1 - QR_MARGEM_X + m, qy + QR_LADO + m))]
for nome, url, caixa in zonas:
    rec = im.crop(caixa)
    escalas = []
    for lado in (600, 400, 300, 240, 180, 140):
        r = rec.resize((lado, int(lado * rec.height / rec.width)), Image.LANCZOS)
        a = cv2.cvtColor(np.array(r.convert("RGB")), cv2.COLOR_RGB2BGR)
        if det.detectAndDecode(a)[0] == url:
            escalas.append(lado)
    ok(len(escalas) == 6, f"QR {nome} isolado le'-se em todas as distancias",
       f"{len(escalas)}/6 (ate {min(escalas) if escalas else '-'}px)")

# (d) informativo: varredura da pagina inteira (o detetor multi e' irregular aqui)
print("  --- informativo: pagina inteira, varias reducoes ---")
for larg in (700, 760, 820, 900, 1080):
    n = len(le_qr(im, larg) & {PLAY_URL, WEB_URL})
    print(f"      {larg:>4}px: {n}/2")

mm = QR_LADO / 300 * 25.4
print(f"  --- QR impresso: {mm:.0f} mm de lado, {mm/37:.2f} mm por modulo (minimo pratico 0,4) ---")

print()
print("=" * 72)
print("2. Conteudo — 13 blocos, cada nome uma so' vez")
print("=" * 72)
nomes = [b["nome"] for b in BLOCOS]
ok(len(nomes) == 13, "sao 13 blocos", str(len(nomes)))
dups = {n for n in nomes if nomes.count(n) > 1}
ok(not dups, "nenhum nome repetido", ", ".join(dups) if dups else "todos unicos")
ok([b["n"] for b in BLOCOS] == list(range(1, 14)), "ordem 1..13 intacta")
proibidos = [n for n in nomes if any(f in n.lower() for f in FORA)]
ok(not proibidos, "nada do que ficou de fora entrou", ", ".join(proibidos) if proibidos else "limpo")

# os logos referidos existem mesmo em disco
falta = []
for b in BLOCOS:
    for lg in b.get("logos", []):
        if not os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "assets", "logos", lg + ".png")):
            falta.append(f'{b["nome"]}:{lg}')
ok(not falta, "todos os logos referidos existem em disco", ", ".join(falta) if falta else "15/15")

print()
print("=" * 72)
print("3. Ficheiros de saida")
print("=" * 72)
ok(im.size == (2480, 3508), "A4 a 300dpi", f"{im.size[0]}x{im.size[1]}")
dpi = im.info.get("dpi", (0, 0))
ok(round(dpi[0]) == 300, "metadados de 300 dpi", str(dpi))
w = Image.open(P_WHATS)
ok(w.size == (1080, 1620), "versao WhatsApp 1080x1620", f"{w.size[0]}x{w.size[1]}")
mb = os.path.getsize(P_WHATS) / 1024 / 1024
ok(mb < 2.0, "WhatsApp abaixo de 2 MB", f"{mb:.2f} MB")

# margem branca de 8mm (95px) — canto tem de estar branco
a = np.array(im.convert("RGB"))
branco = a[10:60, 10:60].mean()
ok(branco > 250, "margem branca da grafica presente", f"media {branco:.1f}")

print()
print("=" * 72)
if falhas:
    print(f"RESULTADO: {len(falhas)} FALHA(S) — {'; '.join(falhas)}")
    sys.exit(1)
print("RESULTADO: tudo verde")

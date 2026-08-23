"""Recorta e trata as imagens GERADAS que ja vinham no video da Keli.
(As 3 APIs de geracao estavam sem credito; o Danilo autorizou usar o video.)
Mesmo tratamento conservador das fotos reais: cor medida, niveis com tecto,
claros com rolloff, saturacao leve e nitidez."""
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "frames_raw")
OUT = os.path.join(BASE, "geradas")
os.makedirs(OUT, exist_ok=True)
MAX_GAIN = 0.06


def cast_correct(a):
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    neutros = (sat < 0.18) & (lum > 60) & (lum < 225)
    if neutros.sum() < 500:
        return a
    m = a[neutros].mean(axis=0)
    gain = np.clip(m.mean() / np.maximum(m, 1e-6), 1 - MAX_GAIN, 1 + MAX_GAIN)
    return np.clip(a * gain, 0, 255)


def levels(a, max_gain=1.12):
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    lo, hi = np.percentile(lum, 1.0), np.percentile(lum, 99.0)
    g = max(1.0, min(max_gain, 235.0 / max(hi - lo, 1e-6))) if hi > lo else 1.0
    a = (a - lo * 0.55) * g
    a = np.where(a > 235, 235 + (a - 235) * 0.35, a)
    return np.clip(a, 0, 255)


def treat(im, sat=1.07, sharp=95):
    a = np.asarray(im.convert("RGB"), dtype=np.float64)
    a = levels(cast_correct(a))
    o = Image.fromarray(a.astype(np.uint8))
    o = ImageEnhance.Color(o).enhance(sat)
    return o.filter(ImageFilter.UnsharpMask(radius=1.5, percent=sharp, threshold=3))


# (ficheiro, recorte esquerda/topo/direita/fundo, largura final, nome)
PECAS = [
    ("f_0156.jpg", (0, 690, 720, 1240), 1100, "bolo-cenoura"),
    ("f_0150.jpg", (140, 880, 625, 1215), 1000, "pudim"),
    ("f_0166.jpg", (55, 900, 700, 1272), 1200, "doces-mesa"),
    ("f_0110.jpg", (55, 640, 665, 1160), 1000, "salgado-partido"),
    ("f_0162.jpg", (0, 200, 720, 1080), 1000, "salgados-dourados"),
]

feitas = []
for fic, caixa, larg, nome in PECAS:
    p = os.path.join(RAW, fic)
    if not os.path.exists(p):
        print(f"  {nome}: FALTA {fic}"); continue
    im = Image.open(p).crop(caixa)
    im = treat(im)
    alt = int(larg * im.size[1] / im.size[0])
    im = im.resize((larg, alt), Image.LANCZOS)
    d = os.path.join(OUT, f"{nome}.jpg")
    im.save(d, quality=90, subsampling=0, optimize=True)
    a = np.asarray(im.convert("L"), dtype=np.float64)
    print(f"  {nome:20s} <- {fic}  {larg}x{alt}  {os.path.getsize(d)//1024} KB  "
          f"brilho={a.mean()/255:.2f} queimados={(a>250).mean():.4f}")
    feitas.append((nome, d))

# folha para eu conferir a olho
from PIL import ImageDraw
TW, TH = 300, 300
folha = Image.new("RGB", (TW * len(feitas), TH + 22), (24, 24, 26))
d = ImageDraw.Draw(folha)
for k, (nome, cam) in enumerate(feitas):
    im = Image.open(cam).convert("RGB")
    im.thumbnail((TW, TH))
    folha.paste(im, (k * TW + (TW - im.size[0]) // 2, (TH - im.size[1]) // 2))
    d.text((k * TW + 6, TH + 5), nome, fill=(255, 255, 255))
folha.save(os.path.join(BASE, "conferir_geradas.jpg"), quality=90)
print("\nconferir_geradas.jpg escrita")

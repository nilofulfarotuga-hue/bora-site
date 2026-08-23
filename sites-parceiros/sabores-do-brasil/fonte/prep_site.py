"""Prepara as imagens do site da Keli (link 1) em WebP, para media/."""
import os, base64, io, json
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(BASE, "tratadas")
G = os.path.join(BASE, "geradas")
F = os.path.join(BASE, "final")
SITE = r"C:\Users\danil\Desktop\sabores-do-brasil\media"
os.makedirs(SITE, exist_ok=True)


def guarda(origem, nome, larg, q=84):
    im = Image.open(origem).convert("RGB")
    if im.size[0] > larg:
        im = im.resize((larg, int(larg * im.size[1] / im.size[0])), Image.LANCZOS)
    p = os.path.join(SITE, nome)
    im.save(p, "WEBP", quality=q, method=6)
    print(f"  {nome:26s} {im.size[0]}x{im.size[1]}  {os.path.getsize(p)//1024} KB")


print("== fotos REAIS dela ==")
guarda(os.path.join(T, "hero-mesa-cheia.jpg"),   "real-mesa.webp", 1000)
guarda(os.path.join(T, "salgados-variados.jpg"), "real-variados.webp", 800)
guarda(os.path.join(T, "coxinhas-detalhe.jpg"),  "real-coxinhas.webp", 620)
guarda(os.path.join(T, "cento-salgados.jpg"),    "real-cento.webp", 900)

print("== imagens ilustrativas (do video dela) ==")
guarda(os.path.join(G, "bolo-cenoura.jpg"),      "ilu-bolo.webp", 950)
guarda(os.path.join(G, "pudim.jpg"),             "ilu-pudim.webp", 850)
guarda(os.path.join(G, "doces-mesa.jpg"),        "ilu-doces.webp", 1000)
guarda(os.path.join(G, "salgado-partido.jpg"),   "ilu-partido.webp", 850)
guarda(os.path.join(G, "salgados-dourados.jpg"), "ilu-dourados.webp", 700)

print("== marca ==")
guarda(os.path.join(T, "logo-fundo-creme.png"),  "logo.webp", 620, 88)

# poster do video -> webp mais leve
guarda(os.path.join(SITE, "poster.jpg"), "poster.webp", 720, 80)

print("== pequenos, em base64 (logo Bora + QR) ==")
assets = {}


def b64(origem, nome, larg, fmt="PNG"):
    im = Image.open(origem)
    if im.size[0] > larg:
        im = im.resize((larg, int(larg * im.size[1] / im.size[0])), Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "PNG":
        im.convert("RGBA").quantize(colors=128, method=Image.FASTOCTREE).save(buf, "PNG", optimize=True)
        mime = "image/png"
    else:
        im.convert("RGB").save(buf, "WEBP", quality=88, method=6)
        mime = "image/webp"
    d = buf.getvalue()
    assets[nome] = f"data:{mime};base64," + base64.b64encode(d).decode()
    print(f"  {nome:12s} {im.size[0]}x{im.size[1]}  {len(d)//1024} KB -> {len(assets[nome])//1024} KB base64")


b64(r"C:\Users\danil\Desktop\bora-site\assets\img\bora_logo.png", "boralogo", 260)
b64(os.path.join(BASE, "qr.png"), "qr", 420)

with open(os.path.join(BASE, "assets_site.json"), "w", encoding="utf-8") as fh:
    json.dump(assets, fh)

total = sum(os.path.getsize(os.path.join(SITE, f)) for f in os.listdir(SITE))
print(f"\nmedia/: {len(os.listdir(SITE))} ficheiros, {total//1024} KB")

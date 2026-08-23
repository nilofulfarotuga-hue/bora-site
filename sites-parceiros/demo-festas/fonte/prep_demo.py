"""Prepara as imagens da demo: ecras REAIS capturados da app web + o ladrilho Festas."""
import os, shutil
from PIL import Image

APP = r"C:\Users\danil\Desktop\projetosflutter\bora_app"
BASE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(BASE, "geradas")
T = os.path.join(BASE, "tratadas")
DEMO = r"C:\Users\danil\Desktop\demo-festas\img"
os.makedirs(DEMO, exist_ok=True)


def guarda(im, nome, q=86):
    p = os.path.join(DEMO, nome)
    im.convert("RGB").save(p, "WEBP", quality=q, method=6)
    print(f"  {nome:26s} {im.size[0]}x{im.size[1]}  {os.path.getsize(p)//1024} KB")
    return p


print("== ecras REAIS da app (capturados da app web em viewport de telemovel) ==")
ECRAS = [
    ("app-10-grelha-completa.png", "ecra-inicio.webp"),
    ("app-03-loja.png",            "ecra-loja-entrada.webp"),
    ("app-04-menu.png",            "ecra-loja-menu.webp"),
    ("app-05-produto.png",         "ecra-produto.webp"),
    ("app-08-carrinho-cheio.png",  "ecra-carrinho-ref.webp"),
    ("app-09-pagamento.png",       "ecra-pagamento-ref.webp"),
]
for src, dst in ECRAS:
    p = os.path.join(APP, src)
    if not os.path.exists(p):
        print(f"  FALTA {src}"); continue
    guarda(Image.open(p), dst)

print("== arte do ladrilho Festas (recorte das imagens dela) ==")
doces = Image.open(os.path.join(G, "doces-mesa.jpg"))
w, h = doces.size
lado = min(w, h)
tile = doces.crop(((w - lado) // 2, 0, (w + lado) // 2, lado)).resize((300, 300), Image.LANCZOS)
guarda(tile, "tile-festas.webp", 88)

print("== fotos dos produtos (para os cartoes da demo) ==")
for src, dst in [(os.path.join(T, "cento-salgados.jpg"), "p-cento.webp"),
                 (os.path.join(T, "salgados-variados.jpg"), "p-variados.webp"),
                 (os.path.join(G, "salgado-partido.jpg"), "p-grandes.webp"),
                 (os.path.join(G, "bolo-cenoura.jpg"), "p-bolo.webp"),
                 (os.path.join(G, "pudim.jpg"), "p-pudim.webp"),
                 (os.path.join(G, "doces-mesa.jpg"), "p-docinho.webp")]:
    im = Image.open(src)
    lado = min(im.size)
    im = im.crop(((im.size[0] - lado) // 2, (im.size[1] - lado) // 2,
                  (im.size[0] + lado) // 2, (im.size[1] + lado) // 2)).resize((260, 260), Image.LANCZOS)
    guarda(im, dst, 84)

print("== logo da loja ==")
guarda(Image.open(os.path.join(BASE, "final", "logo-quadrado.jpg")).resize((160, 160), Image.LANCZOS),
       "logo-loja.webp", 88)

total = sum(os.path.getsize(os.path.join(DEMO, f)) for f in os.listdir(DEMO))
print(f"\n{len(os.listdir(DEMO))} ficheiros, {total//1024} KB em {DEMO}")

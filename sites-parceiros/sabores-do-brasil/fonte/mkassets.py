"""Gera os assets embutidos no site (base64) + o QR com correccao M,
com PROVA de leitura em varias escalas."""
import os, io, json, base64
import numpy as np
import qrcode
import cv2
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(BASE, "tratadas")
PLAY = "https://play.google.com/store/apps/details?id=pt.boraapp.bora"
BORA_IMG = r"C:\Users\danil\Desktop\bora-site\assets\img"

assets = {}


def put(nome, im, fmt="JPEG", quality=80):
    buf = io.BytesIO()
    if fmt == "JPEG":
        im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        mime = "image/jpeg"
    else:
        im.save(buf, "PNG", optimize=True)
        mime = "image/png"
    b = buf.getvalue()
    assets[nome] = f"data:{mime};base64," + base64.b64encode(b).decode()
    print(f"  {nome:12s} {im.size[0]:4d}x{im.size[1]:<4d} {len(b)//1024:4d} KB cru -> {len(assets[nome])//1024:4d} KB base64")


def carregar(p, largura):
    im = Image.open(p)
    if im.size[0] > largura:
        im = im.resize((largura, int(largura * im.size[1] / im.size[0])), Image.LANCZOS)
    return im


print("== fotos reais da Keli (versao leve para a pagina) ==")
put("hero", carregar(os.path.join(T, "hero-mesa-cheia.jpg"), 900), quality=80)
put("variados", carregar(os.path.join(T, "salgados-variados.jpg"), 700), quality=80)
put("coxinhas", carregar(os.path.join(T, "coxinhas-detalhe.jpg"), 520), quality=80)
put("cento", carregar(os.path.join(T, "cento-salgados.jpg"), 800), quality=80)

# Placa creme com a arte original dela. O recorte transparente deixava halo
# irregular sobre o verde escuro do topo; a placa e' a arte intacta e mais limpa.
print("== logo dela (placa creme, arte original) ==")
put("logo", carregar(os.path.join(T, "logo-fundo-creme.png"), 560), quality=86)

print("== logo quadrado (avatar da loja na demo) ==")
put("logoq", Image.open(os.path.join(BASE, "final", "logo-quadrado.jpg")).resize((220, 220), Image.LANCZOS), quality=82)

print("== logo do Bora (do repo bora-site) ==")
bora = Image.open(os.path.join(BORA_IMG, "bora_logo.png")).convert("RGBA")
bora = bora.resize((260, int(260 * bora.size[1] / bora.size[0])), Image.LANCZOS)
put("boralogo", bora.quantize(colors=128, method=Image.FASTOCTREE), fmt="PNG")

print("== QR para a Play Store (correccao M, nunca H) ==")
qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                   box_size=10, border=3)
qr.add_data(PLAY)
qr.make(fit=True)
print(f"  versao={qr.version}  modulos={qr.modules_count}x{qr.modules_count}  correccao=M")
qr_im = qr.make_image(fill_color="#111111", back_color="white").convert("RGB")
qr_im.save(os.path.join(BASE, "qr.png"))
put("qr", qr_im.resize((420, 420), Image.NEAREST), fmt="PNG")

print("\n== PROVA: leitura do QR em varias escalas ==")
det = cv2.QRCodeDetector()
ok_todas = True
for px in (480, 360, 280, 220, 180, 140, 110, 90):
    teste = qr_im.resize((px, px), Image.LANCZOS)
    # moldura branca, como no site
    canvas = Image.new("RGB", (px + 40, px + 40), "white")
    canvas.paste(teste, (20, 20))
    arr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
    txt, pts, _ = det.detectAndDecode(arr)
    bate = (txt == PLAY)
    ok_todas &= bate
    print(f"  {px:3d}px -> {'LIDO OK' if bate else 'FALHOU '}  {txt[:58] if txt else '(nada)'}")

# teste com desfoque, a imitar foto tremida
print("  -- com desfoque (foto tremida) --")
for px, blur in ((280, 3), (220, 3), (180, 5)):
    teste = qr_im.resize((px, px), Image.LANCZOS)
    canvas = Image.new("RGB", (px + 40, px + 40), "white")
    canvas.paste(teste, (20, 20))
    arr = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2BGR)
    arr = cv2.GaussianBlur(arr, (blur, blur), 0)
    txt, _, _ = det.detectAndDecode(arr)
    print(f"  {px:3d}px blur{blur} -> {'LIDO OK' if txt == PLAY else 'FALHOU '}  {txt[:50] if txt else '(nada)'}")

print(f"\nQR legivel em todas as escalas testadas: {ok_todas}")

with open(os.path.join(BASE, "assets_b64.json"), "w", encoding="utf-8") as fh:
    json.dump(assets, fh)
total = sum(len(v) for v in assets.values())
print(f"assets_b64.json escrito: {len(assets)} imagens, {total//1024} KB de base64")

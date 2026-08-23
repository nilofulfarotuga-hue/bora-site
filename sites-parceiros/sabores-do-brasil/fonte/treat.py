"""Trata as fotos REAIS da Keli. v2 - conservadora.
A v1 usava gray-world cego + esticao de histograma: numa foto dominada por comida
dourada isso puxa tudo para o azul e queima os claros. Aqui a correccao e MEDIDA
(so em pixeis neutros) e com tecto, e os claros tem rolloff em vez de corte."""
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "frames_raw")
OUT = os.path.join(BASE, "tratadas")
os.makedirs(OUT, exist_ok=True)

OVERLAY_TOP, OVERLAY_BOT = 575, 925   # faixa do telefone queimado no video
MAX_GAIN = 0.06                        # tecto de correccao de cor: +-6%


def cast_correct(a):
    """Mede o desvio de cor SO nos pixeis quase-neutros (granito, aluminio).
    Se a foto nao tem dominante, nao mexe."""
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    neutros = (sat < 0.18) & (lum > 60) & (lum < 225)
    if neutros.sum() < 500:
        print("      sem pixeis neutros suficientes -> nao corrijo cor")
        return a
    m = a[neutros].mean(axis=0)
    gain = m.mean() / np.maximum(m, 1e-6)
    gain = np.clip(gain, 1 - MAX_GAIN, 1 + MAX_GAIN)
    print(f"      neutros={neutros.sum()}px  ganho R/G/B={gain[0]:.3f}/{gain[1]:.3f}/{gain[2]:.3f}")
    return np.clip(a * gain, 0, 255)


def levels(a, max_gain=1.12):
    """So levanta pretos esmagados e ganha contraste com tecto. Claros com rolloff."""
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    lo = np.percentile(lum, 1.0)
    hi = np.percentile(lum, 99.0)
    g = min(max_gain, 235.0 / max(hi - lo, 1e-6)) if hi > lo else 1.0
    g = max(g, 1.0)
    a = (a - lo * 0.55) * g
    # rolloff suave acima de 235 em vez de corte seco (evita queimar)
    a = np.where(a > 235, 235 + (a - 235) * 0.35, a)
    print(f"      preto={lo:.0f} branco={hi:.0f} ganho={g:.3f}")
    return np.clip(a, 0, 255)


def treat(im, sat=1.06, sharp_pct=90):
    a = np.asarray(im.convert("RGB"), dtype=np.float64)
    a = cast_correct(a)
    a = levels(a)
    out = Image.fromarray(a.astype(np.uint8))
    out = ImageEnhance.Color(out).enhance(sat)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.4, percent=sharp_pct, threshold=3))
    return out


def save(im, name, quality=90):
    p = os.path.join(OUT, name)
    im.save(p, quality=quality, subsampling=0, optimize=True)
    a = np.asarray(im.convert("L"), dtype=np.float64)
    print(f"  -> {name}  {im.size[0]}x{im.size[1]}  {os.path.getsize(p)//1024} KB  "
          f"brilho={a.mean()/255:.2f} queimados={(a>250).mean():.4f}")


print("== cena REAL 1: bancada de granito (f_0099, sem legenda) ==")
tray = Image.open(os.path.join(RAW, "f_0099.jpg"))
print("   hero (mesa cheia, os dois tabuleiros)")
save(treat(tray.crop((0, 360, 720, 1130))).resize((1080, 1155), Image.LANCZOS),
     "hero-mesa-cheia.jpg", 88)
print("   salgados variados (quadrado)")
save(treat(tray.crop((10, 400, 690, 1080))).resize((1000, 1000), Image.LANCZOS),
     "salgados-variados.jpg", 90)
print("   coxinhas (tabuleiro da direita)")
save(treat(tray.crop((355, 380, 720, 1060))).resize((760, 1415), Image.LANCZOS),
     "coxinhas-detalhe.jpg", 90)

print("== cena REAL 2: monte de salgados (f_0143, legenda cortada) ==")
pile = Image.open(os.path.join(RAW, "f_0143.jpg"))
save(treat(pile.crop((0, 0, 720, OVERLAY_TOP)), sat=1.05, sharp_pct=80)
     .resize((1080, 862), Image.LANCZOS), "cento-salgados.jpg", 90)

print("== PROVA: a faixa da legenda ficou fora do corte? ==")
chk = np.asarray(pile.convert("L"), dtype=np.float64)
print(f"   faixa da legenda y={OVERLAY_TOP}-{OVERLAY_BOT}: brancos(>240)="
      f"{float((chk[OVERLAY_TOP:OVERLAY_BOT] > 240).mean()):.4f}")
print(f"   faixa usada      y=0-{OVERLAY_TOP}: brancos(>240)="
      f"{float((chk[0:OVERLAY_TOP] > 240).mean()):.4f}")

# folha antes/depois para revisao a olho
pairs = [("f_0099.jpg", "hero-mesa-cheia.jpg"), ("f_0143.jpg", "cento-salgados.jpg")]
W, H = 420, 500
sheet = Image.new("RGB", (W * 2, H * len(pairs)), (20, 20, 22))
for i, (src, dst) in enumerate(pairs):
    o = Image.open(os.path.join(RAW, src)).convert("RGB")
    o.thumbnail((W, H)); sheet.paste(o, (0, i * H))
    n = Image.open(os.path.join(OUT, dst)).convert("RGB")
    n.thumbnail((W, H)); sheet.paste(n, (W, i * H))
sheet.save(os.path.join(BASE, "antes_depois.jpg"), quality=90)
print("antes_depois.jpg  (esquerda=cru  direita=tratado)")

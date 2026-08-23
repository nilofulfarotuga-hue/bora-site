"""Recorte final do logo.
Morfologia sozinha ou come o contorno dourado ou deixa fagulhas. Aqui:
  1. mascara DURA (dist>90) -> componentes -> so os grandes = semente
  2. dilata a semente = regiao de interesse (ROI)
  3. alfa SUAVE (rampa 55->85) dentro da ROI -> contorno intacto, fagulhas fora
"""
import os
from collections import deque
import numpy as np
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "tratadas")
crop = Image.open(os.path.join(OUT, "logo-fundo-creme.png")).convert("RGB")
a = np.asarray(crop, dtype=np.float64)
H, W = a.shape[:2]

creme = np.concatenate([a[:14, :14].reshape(-1, 3), a[:14, -14:].reshape(-1, 3)]).mean(axis=0)
dist = np.sqrt(((a - creme) ** 2).sum(axis=2))


def componentes(bin_):
    lab = np.zeros((H, W), dtype=np.int32)
    areas, cur = {}, 0
    for y0 in range(H):
        for x0 in range(W):
            if bin_[y0, x0] and lab[y0, x0] == 0:
                cur += 1
                n = 0
                q = deque([(y0, x0)])
                lab[y0, x0] = cur
                while q:
                    y, x = q.popleft()
                    n += 1
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < H and 0 <= xx < W and bin_[yy, xx] and lab[yy, xx] == 0:
                            lab[yy, xx] = cur
                            q.append((yy, xx))
                areas[cur] = n
    return lab, areas


# 1) semente dura
dura = dist > 90
lab, areas = componentes(dura)
grandes = {c for c, n in areas.items() if n >= 4000}
print(f"componentes na mascara dura: {len(areas)}  |  grandes(>=4000px): {len(grandes)}")
for c, n in sorted(areas.items(), key=lambda kv: -kv[1])[:4]:
    print(f"   #{c}: {n} px {'MANTIDO' if c in grandes else 'descartado'}")
semente = np.isin(lab, list(grandes))

# 2) ROI = semente dilatada
roi = Image.fromarray((semente.astype(np.uint8)) * 255)
for _ in range(4):
    roi = roi.filter(ImageFilter.MaxFilter(9))   # ~16 px de folga
roi = (np.asarray(roi) > 127)
print(f"semente={semente.mean()*100:.1f}%  ->  ROI={roi.mean()*100:.1f}% da area")

# 2b) tapar buracos internos da semente (o meio claro da coxinha central ficava
#     translucido e o verde do fundo sangrava por dentro)
fora = ~semente
lab_f, areas_f = componentes(fora)
borda = set(np.unique(np.concatenate([lab_f[0, :], lab_f[-1, :], lab_f[:, 0], lab_f[:, -1]])))
borda.discard(0)
buracos = {c for c in areas_f if c not in borda}
semente_cheia = semente | np.isin(lab_f, list(buracos))
print(f"buracos internos tapados: {len(buracos)}  "
      f"({semente.mean()*100:.1f}% -> {semente_cheia.mean()*100:.1f}%)")

# 3) alfa suave dentro da ROI, mas opaco a fundo dentro da semente cheia
LO, HI = 55.0, 85.0
soft = np.clip((dist - LO) / (HI - LO), 0, 1)
soft = np.maximum(soft, semente_cheia.astype(np.float64))
alpha = (soft * roi * 255).astype(np.uint8)
alpha_im = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.6))

rgba = crop.convert("RGBA")
rgba.putalpha(alpha_im)
bb = rgba.getbbox()
if bb:
    rgba = rgba.crop(bb)
rgba.save(os.path.join(OUT, "logo-transparente.png"))
print("logo-transparente.png", rgba.size,
      f"{os.path.getsize(os.path.join(OUT,'logo-transparente.png'))//1024} KB")

canvas = Image.new("RGB", (rgba.size[0] + 80, rgba.size[1] + 80), (22, 101, 52))
canvas.paste(rgba, (40, 40), rgba)
canvas.save(os.path.join(BASE, "prova-logo-verde.png"))
print("prova-logo-verde.png escrita")

"""Extrai fotogramas do video da Keli, pontua nitidez/exposicao, tira duplicados,
e monta contact sheets para revisao visual."""
import os, subprocess, shutil, math
import numpy as np
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
VID = r"C:\Users\danil\Downloads\WhatsApp Video 2026-08-23 at 16.16.07.mp4"
FF = r"C:\Users\danil\AppData\Local\Programs\Python\Python312\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
RAW = os.path.join(BASE, "frames_raw")

if os.path.isdir(RAW):
    shutil.rmtree(RAW)
os.makedirs(RAW)

# 3 fps -> ~173 fotogramas de 57.7s
cmd = [FF, "-hide_banner", "-loglevel", "error", "-i", VID,
       "-vf", "fps=3", "-q:v", "2", os.path.join(RAW, "f_%04d.jpg")]
subprocess.run(cmd, check=True)
files = sorted(os.listdir(RAW))
print(f"fotogramas extraidos: {len(files)}")


def sharpness(im):
    g = np.asarray(im.convert("L").resize((360, 640)), dtype=np.float64)
    # Laplaciano 3x3
    lap = (-4 * g[1:-1, 1:-1] + g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:])
    return float(lap.var())


def dhash(im, hs=8):
    g = np.asarray(im.convert("L").resize((hs + 1, hs)), dtype=np.int16)
    return (g[:, 1:] > g[:, :-1]).flatten()


def stats(im):
    a = np.asarray(im.convert("RGB").resize((180, 320)), dtype=np.float64) / 255.0
    lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    mx = a.max(axis=2); mn = a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    # % pixeis queimados / esmagados
    burnt = float((lum > 0.97).mean()); crush = float((lum < 0.03).mean())
    return float(lum.mean()), float(sat.mean()), burnt, crush, float(lum.std())


rows = []
for i, fn in enumerate(files):
    p = os.path.join(RAW, fn)
    im = Image.open(p)
    sh = sharpness(im)
    br, sat, burnt, crush, contrast = stats(im)
    rows.append(dict(fn=fn, sh=sh, br=br, sat=sat, burnt=burnt,
                     crush=crush, contrast=contrast, h=dhash(im)))

sh_all = np.array([r["sh"] for r in rows])
print(f"nitidez: min={sh_all.min():.0f} mediana={np.median(sh_all):.0f} max={sh_all.max():.0f}")

# filtro duro: fora tremidos, queimados e escuros
keep = [r for r in rows
        if r["sh"] >= np.percentile(sh_all, 45)
        and 0.22 <= r["br"] <= 0.80
        and r["burnt"] < 0.12
        and r["crush"] < 0.20
        and r["contrast"] > 0.08]
print(f"passaram o filtro de qualidade: {len(keep)}")

# dedup por hamming < 12 -> fica o mais nitido do grupo
keep.sort(key=lambda r: -r["sh"])
uniq = []
for r in keep:
    if all(int(np.count_nonzero(r["h"] != u["h"])) >= 12 for u in uniq):
        uniq.append(r)
print(f"unicos apos dedup: {len(uniq)}")

uniq.sort(key=lambda r: files.index(r["fn"]))  # ordem cronologica
OUT = os.path.join(BASE, "cand")
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
for n, r in enumerate(uniq, 1):
    shutil.copy(os.path.join(RAW, r["fn"]),
                os.path.join(OUT, f"c{n:02d}_{r['fn']}"))
    print(f"c{n:02d} <- {r['fn']} nitidez={r['sh']:.0f} brilho={r['br']:.2f} sat={r['sat']:.2f}")

# contact sheets de 12 (4x3)
cands = sorted(os.listdir(OUT))
TW, TH, COLS = 240, 427, 4
for page in range(math.ceil(len(cands) / 12)):
    chunk = cands[page * 12:(page + 1) * 12]
    rowsn = math.ceil(len(chunk) / COLS)
    sheet = Image.new("RGB", (COLS * TW, rowsn * (TH + 22)), (25, 25, 28))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for k, fn in enumerate(chunk):
        im = Image.open(os.path.join(OUT, fn)).resize((TW, TH))
        x, y = (k % COLS) * TW, (k // COLS) * (TH + 22)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + TH + 5), fn.split("_")[0], fill=(255, 255, 255))
    sheet.save(os.path.join(BASE, f"sheet_{page + 1}.jpg"), quality=88)
    print(f"sheet_{page + 1}.jpg  ({len(chunk)} fotogramas)")

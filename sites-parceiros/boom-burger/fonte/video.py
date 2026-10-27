# -*- coding: utf-8 -*-
"""Video "Na chapa" (B.4): ~11 s, mudo, so com pixeis reais do dono.

Planos (cada um <= 4 s):
  1. Boom! Duplo Smash (wa-11): aproximacao lenta (Ken Burns) ao queijo a escorrer.
  2. Boom! Portobello em CAMADAS REAIS: as 5 fatias do recorte descem e encaixam (parallax).
  3. Batata gulosa (wa-04): travelling lateral lento.
  4. Boom! Kamikaze (wa-17): aproximacao e corte final.
Saida: ../dist/assets/video/na-chapa.mp4 (H.264, 1280x720, 30 fps, sem audio, faststart)
       ../dist/assets/video/na-chapa-poster.{webp,jpg}
"""
import json, os, subprocess
from PIL import Image, ImageOps, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
WA = lambda f: os.path.join(B, 'origem', 'whatsapp', f)
OUT = os.path.join(B, 'dist', 'assets', 'video')
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1280, 720, 30
FUNDO = (18, 17, 16)


def ease(t):
    return t * t * (3 - 2 * t)


def kenburns(src, dur, z0, z1, cx0, cy0, cx1, cy1):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    iw, ih = im.size
    base = max(W / iw, H / ih)
    n = int(dur * FPS)
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        z = z0 + (z1 - z0) * t
        cx = cx0 + (cx1 - cx0) * t
        cy = cy0 + (cy1 - cy0) * t
        cw, ch = W / (base * z), H / (base * z)
        x = min(max(cx * iw - cw / 2, 0), iw - cw)
        y = min(max(cy * ih - ch / 2, 0), ih - ch)
        yield im.resize((W, H), Image.LANCZOS, box=(x, y, x + cw, y + ch))


def camadas(dur):
    pasta = os.path.join(B, 'media', 'camadas', 'portobello-v3')
    m = json.load(open(os.path.join(pasta, 'camadas.json'), encoding='utf-8'))
    esc = 0.62 * H / m['altura_px']
    lw = int(m['largura_px'] * esc)
    lh = int(m['altura_px'] * esc)
    pecas = []
    for c in m['camadas']:
        im = Image.open(os.path.join(pasta, c['ficheiro'])).convert('RGBA')
        im = im.resize((lw, max(1, int(im.height * esc))), Image.LANCZOS)
        pecas.append((im, c['top_pct'] / 100 * lh))
    # fundo: a propria foto do Portobello, desfocada e escurecida (pixeis reais)
    fundo = ImageOps.fit(Image.open(WA('wa-20.jpg')).convert('RGB'), (W, H), centering=(0.5, 0.6))
    fundo = fundo.filter(ImageFilter.GaussianBlur(28))
    fundo = Image.blend(fundo, Image.new('RGB', (W, H), FUNDO), 0.72)
    n = int(dur * FPS)
    x0 = (W - lw) // 2
    y0 = (H - lh) // 2 + 20
    k = len(pecas)
    for i in range(n):
        t = i / max(n - 1, 1)
        fr = fundo.copy().convert('RGBA')
        for j, (im, top) in enumerate(pecas):
            # cada camada entra com atraso proprio e encaixa com uma pequena mola
            d = min(max((t - j * 0.08) / 0.55, 0), 1)
            mola = 1 - (1 - d) ** 3 * (1 + 2.2 * d)  # passa um pouco e volta
            afast = (j - (k - 1) / 2) * 120
            dy = afast * (1 - mola)
            fr.alpha_composite(im, (x0, int(y0 + top + dy)))
        yield fr.convert('RGB')


planos = [kenburns(WA('wa-11.jpg'), 3.4, 1.0, 1.18, 0.55, 0.5, 0.6, 0.45),
          camadas(3.6),
          kenburns(WA('wa-04.jpg'), 2.8, 1.12, 1.12, 0.38, 0.5, 0.62, 0.5),
          kenburns(WA('wa-17.jpg'), 2.2, 1.05, 1.22, 0.5, 0.45, 0.5, 0.42)]
dst = os.path.join(OUT, 'na-chapa.mp4')
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
       '-i', '-', '-an', '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-preset', 'slow',
       '-crf', '27', '-movflags', '+faststart', dst]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n = 0
primeiro = None
for pl in planos:
    for fr in pl:
        if primeiro is None:
            primeiro = fr.copy()
        p.stdin.write(fr.tobytes())
        n += 1
p.stdin.close()
p.wait()
primeiro.save(os.path.join(OUT, 'na-chapa-poster.webp'), 'WEBP', quality=78)
primeiro.save(os.path.join(OUT, 'na-chapa-poster.jpg'), 'JPEG', quality=80)
print('frames', n, 'segundos', round(n / FPS, 1), 'MB', round(os.path.getsize(dst) / 1e6, 2))

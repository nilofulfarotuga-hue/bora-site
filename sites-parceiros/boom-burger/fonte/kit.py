# -*- coding: utf-8 -*-
"""Bloco C — kit para o cartaz e o autocolante (so preparar; nao se imprime nada).

../kit-cartaz/:
  logo/boom-logo.svg, boom-logo-fundo.svg, boom-marca.svg, boom-logo-1024.png (transparente)
  fotos/<nome>.png  — 3 fotos do dono recortadas (fundo transparente, rembg u2net); pixeis reais
  qr/qr-boomburger.svg + qr-boomburger-1200.png — https://boraguarda.com/baixar?de=qr-boomburger, correcao M
  LEIA-ME.md
Prova do QR: le-se com o OpenCV no SVG renderizado e em reducoes de 1200 ate 120 px.
"""
import io, json, os, shutil
import cv2
import numpy as np
import qrcode
import qrcode.image.svg
from PIL import Image, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
K = os.path.join(B, 'kit-cartaz')
for d in ('logo', 'fotos', 'qr'):
    os.makedirs(os.path.join(K, d), exist_ok=True)
URL_QR = 'https://boraguarda.com/baixar?de=qr-boomburger'

# logotipos
for f in ('boom-logo.svg', 'boom-logo-fundo.svg', 'boom-marca.svg', 'boom-logo-1024.png', 'boom-icone-512.png'):
    shutil.copy(os.path.join(B, 'media', 'logo', f), os.path.join(K, 'logo', f))

# fotos recortadas (so tirar fundo: o aspeto do produto nao muda)
from rembg import remove, new_session
ses = new_session('u2net')
# (provado a 27/10: o isnet abria buracos no queijo e mantinha o prato; o u2net e melhor aqui.
#  No Kamikaze o u2net deixa o prato meio transparente: corta-se alfa < 150.)
FOTOS = [('portobello', 'wa-20.jpg', (300, 600, 1380, 1790), None), ('duplo-smash', 'wa-11.jpg', None, None),
         ('kamikaze', 'wa-17.jpg', None, 150)]
for nome, f, caixa, limiar in FOTOS:
    im = ImageOps.exif_transpose(Image.open(os.path.join(B, 'origem', 'whatsapp', f))).convert('RGB')
    if caixa:
        im = im.crop(caixa)
    out = remove(im, session=ses)
    if limiar:
        out.putalpha(out.getchannel('A').point(lambda v: 0 if v < limiar else v))
    bb = out.getchannel('A').point(lambda v: 255 if v > 12 else 0).getbbox()
    out = out.crop(bb)
    out.save(os.path.join(K, 'fotos', f'{nome}.png'), optimize=True)
    print('foto', nome, out.size)

# QR com correcao M (regra 8.9 do site-premio)
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4, box_size=10)
qr.add_data(URL_QR)
qr.make(fit=True)
svg = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
svg.save(os.path.join(K, 'qr', 'qr-boomburger.svg'))
png = qr.make_image(fill_color='black', back_color='white').convert('RGB').resize((1200, 1200), Image.NEAREST)
png.save(os.path.join(K, 'qr', 'qr-boomburger-1200.png'))

det = cv2.QRCodeDetector()
leituras = {}
for lado in (1200, 600, 300, 200, 150, 120):
    a = np.array(png.resize((lado, lado), Image.LANCZOS).convert('L'))
    a = cv2.copyMakeBorder(a, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
    txt, _, _ = det.detectAndDecode(a)
    leituras[lado] = txt
# o SVG tambem: renderizado pelo MuPDF
import pymupdf
d = pymupdf.open(os.path.join(K, 'qr', 'qr-boomburger.svg'))
pix = d[0].get_pixmap(matrix=pymupdf.Matrix(3, 3))
a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
leituras['svg'] = det.detectAndDecode(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY))[0]
ok = all(v == URL_QR for v in leituras.values())
json.dump({'url': URL_QR, 'correcao': 'M', 'versao_qr': qr.version, 'leituras': leituras, 'todas_certas': ok},
          open(os.path.join(K, 'qr', 'prova-leitura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('QR versao', qr.version, 'leituras certas:', ok, {k: (v == URL_QR) for k, v in leituras.items()})

io.open(os.path.join(K, 'LEIA-ME.md'), 'w', encoding='utf-8').write(f'''# Kit do cartaz e do autocolante — Boom! Burger

Só preparação (missão boom-burger-2026-10-27, bloco C). O cartaz e o autocolante desenham-se depois
de o dono aprovar a loja; a impressão é com o Claude.ai/Danilo. Ninguém mandou imprimir nada.

- `logo/` — logótipo vetorial do dono (do PDF dele): completo transparente, com fundo carvão, só a marca
  (o hambúrguer com BOOM), PNG transparente 1024 e ícone 512. Cores: dourado #DBB545, branco, carvão #2B2A29.
- `fotos/` — 3 fotos do dono (WhatsApp 27/10) com o fundo tirado automaticamente (rembg), pixéis reais:
  Portobello (pão preto), Duplo Smash, Kamikaze. Recorte automático: o designer pode afinar as bordas
  (há restos do palito e da taça de maionese). Nunca alterar o aspeto do produto.
- `qr/` — QR para {URL_QR} (deteta iPhone/Android/computador e conta a origem "qr-boomburger"),
  correção de erro M. Na arte A4: pelo menos 500 px de lado, com margem branca à volta. Prova de leitura em
  `qr/prova-leitura.json` (lido em 1200, 600, 300, 200, 150 e 120 px e no SVG).
- Nota Google para o cartaz, se se quiser: 4,7 com 114 avaliações (lido a 27/10/2026).
''')
print('kit ok')

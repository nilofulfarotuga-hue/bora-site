#!/usr/bin/env python3
"""Autocolante da porta Boom! Burger x Bora — 10x10 cm + 3 mm de sangria, 300 dpi.
Saida: PNG (com sangria), PNG (sem sangria, para ver) e PDF 106x106 mm."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

DPI = 300
MM = DPI / 25.4
SANG = int(3 * MM)                 # 3 mm de sangria
LADO = int(100 * MM)               # 10 cm
W = H = LADO + 2 * SANG            # 1252 px

CARVAO = (11, 11, 11)
OURO = (240, 190, 88)              # mesmo dourado dos cartazes do Canva (#f0be58)
VERDE = (22, 163, 74)              # #16A34A
BRANCO = (255, 255, 255)

F = '/usr/share/fonts/opentype/inter/'
def font(name, size): return ImageFont.truetype(F + name, size)

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = '/home/claude/bora-site'
boom = Image.open(f'{SITE}/sites-parceiros/boom-burger/kit-cartaz/logo/boom-logo-1024.png').convert('RGBA')
bora = Image.open(f'{SITE}/assets/img/bora_logo.png').convert('RGBA')
qr = Image.open(f'{BASE}/qr-boom-porta-1000.png').convert('RGB')

im = Image.new('RGB', (W, H), CARVAO)
d = ImageDraw.Draw(im)

# moldura dourada fina (fica a 4 mm da borda cortada)
m = SANG + int(4 * MM)
d.rounded_rectangle([m, m, W - m, H - m], radius=int(5 * MM), outline=OURO, width=int(0.7 * MM))

# Logótipo Boom (branco+ouro) no topo, centrado
bh = int(16 * MM); bw = int(boom.width * bh / boom.height)
b = boom.resize((bw, bh), Image.LANCZOS)
im.paste(b, ((W - bw) // 2, SANG + int(7 * MM)), b)

# Título
y = SANG + int(25 * MM)
t1 = 'PEDE PELA APP'
f1 = font('InterDisplay-Black.otf', int(7.6 * MM))
w1 = d.textlength(t1, font=f1)
d.text(((W - w1) / 2, y), t1, font=f1, fill=BRANCO)
y += int(9.2 * MM)
t2 = 'Entrega em toda a Guarda'
f2 = font('Inter-SemiBold.otf', int(3.6 * MM))
w2 = d.textlength(t2, font=f2)
d.text(((W - w2) / 2, y), t2, font=f2, fill=OURO)

# QR em caixa branca (35 mm — lê-se a 1 m de distância)
qs = int(31 * MM); pad = int(2.2 * MM)
qx = (W - qs) // 2; qy = SANG + int(43.5 * MM)
d.rounded_rectangle([qx - pad, qy - pad, qx + qs + pad, qy + qs + pad], radius=int(2 * MM), fill=BRANCO)
im.paste(qr.resize((qs, qs), Image.NEAREST), (qx, qy))

# Legenda do QR
y = qy + qs + pad + int(2 * MM)
t3 = 'Aponta a câmara  ·  iPhone e Android'
f3 = font('Inter-Bold.otf', int(3.0 * MM))
w3 = d.textlength(t3, font=f3)
d.text(((W - w3) / 2, y), t3, font=f3, fill=OURO)

# Rodapé: ponto verde + endereço à esquerda, logótipo Bora num cartão branco à direita
lh = int(7.5 * MM); lw = int(bora.width * lh / bora.height)
l = bora.resize((lw, lh), Image.LANCZOS)
cpad = int(1.2 * MM)
cy = H - SANG - int(7.5 * MM) - lh - cpad      # topo do cartão
cx = W - m - int(3.5 * MM) - lw - 2 * cpad  # encostado à moldura, com respiro
d.rounded_rectangle([cx, cy - cpad, cx + lw + 2 * cpad, cy + lh + cpad], radius=int(1.8 * MM), fill=BRANCO)
im.paste(l, (cx + cpad, cy), l)
t4 = 'boraguarda.com/baixar'
f4 = font('Inter-Bold.otf', int(3.3 * MM))
dot = int(2.2 * MM)
x = m + int(5 * MM)
ym = cy + lh / 2
d.ellipse([x, ym - dot / 2, x + dot, ym + dot / 2], fill=VERDE)
x += dot + int(2 * MM)
d.text((x, ym - f4.size / 2 - int(0.3 * MM)), t4, font=f4, fill=BRANCO)

out = os.path.join(BASE, '..')
im.save(f'{out}/04-autocolante-porta-10x10-com-sangria.png', dpi=(DPI, DPI))
im.crop((SANG, SANG, SANG + LADO, SANG + LADO)).save(f'{out}/04-autocolante-porta-10x10-ver.png', dpi=(DPI, DPI))
im.save(f'{out}/04-autocolante-porta-10x10-com-sangria.pdf', 'PDF', resolution=DPI)
print('ok', im.size)

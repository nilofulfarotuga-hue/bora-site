# -*- coding: utf-8 -*-
"""Imagem de partilha 1200x630: foto real (Duplo Smash) + logotipo do dono. -> dist/assets/og-boomburger.jpg"""
import os
from PIL import Image, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
W, H = 1200, 630
foto = ImageOps.fit(Image.open(os.path.join(B, 'origem', 'whatsapp', 'wa-11.jpg')).convert('RGB'), (W, H), centering=(0.62, 0.5))
grad = Image.linear_gradient('L').rotate(90).resize((W, H))  # 255 a esquerda -> 0 a direita
grad = grad.point(lambda v: int(min(255, max(0, (v - 70) * 1.55))))
escuro = Image.new('RGB', (W, H), (18, 17, 16))
img = Image.composite(escuro, foto, grad)
logo = Image.open(os.path.join(B, 'media', 'logo', 'boom-logo-1024.png')).convert('RGBA')
logo.thumbnail((10_000, 470))
img = img.convert('RGBA')
img.alpha_composite(logo, (70, (H - logo.height) // 2))
os.makedirs(os.path.join(B, 'dist', 'assets'), exist_ok=True)
img.convert('RGB').save(os.path.join(B, 'dist', 'assets', 'og-boomburger.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)
print('og ok')

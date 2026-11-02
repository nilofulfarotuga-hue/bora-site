# -*- coding: utf-8 -*-
"""Imagens do site: AVIF + WebP em varias larguras (srcset). So redimensionar/comprimir/
recortar — o aspeto das fotos do dono nunca muda.

Saida: ../dist/assets/img/<nome>-<largura>.{avif,webp} e ../fonte/imagens.json
       {nome: {larguras:[...], w, h, origem}}
"""
import json, os, re, shutil
from PIL import Image, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
O = os.path.join(B, 'origem')
DST = os.path.join(B, 'dist', 'assets', 'img')
os.makedirs(DST, exist_ok=True)
prep = json.load(open(os.path.join(AQUI, 'menu-preparacao.json'), encoding='utf-8'))
WA = lambda f: os.path.join(O, 'whatsapp', f)
idx = {}


def gera(nome, src, larguras, origem, crop=None, q_avif=52, q_webp=76):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    if crop:  # (x0,y0,x1,y1) em fracoes
        w, h = im.size
        im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    feitas = []
    for L in larguras:
        if L > im.width * 1.02 and feitas:
            continue
        L2 = min(L, im.width)
        r = im.resize((L2, round(im.height * L2 / im.width)), Image.LANCZOS)
        r.save(os.path.join(DST, f'{nome}-{L2}.avif'), 'AVIF', quality=q_avif, speed=5)
        r.save(os.path.join(DST, f'{nome}-{L2}.webp'), 'WEBP', quality=q_webp, method=6)
        feitas.append(L2)
    idx[nome] = {'larguras': feitas, 'w': im.width, 'h': im.height, 'origem': origem}


gera('heroi', WA('wa-11.jpg'), [800, 1200, 1600, 2000], 'WhatsApp do dono 27/10 07:36 (wa-11, Boom! Duplo Smash)')
# 3.a ronda: a foto final da cena tem EXATAMENTE a caixa do recorte (wa-20 cortada em (300,600) e as
# fatias de y 380 a 1108), para o recorte passar a foto real no mesmo sitio e tamanho.
import numpy as np
_al = np.array(Image.open(os.path.join(B, 'media', 'camadas', 'recorte-u2net.png')).getchannel('A'))
_cols = np.where(_al.max(axis=0) > 12)[0]
_x0, _x1 = 300 + int(_cols.min()), 300 + int(_cols.max()) + 1
gera('fecho-portobello', WA('wa-20.jpg'), [600, 900, 1200], 'WhatsApp do dono 27/10 07:36 (wa-20, Boom! Portobello)',
     crop=(_x0 / 1500, (600 + 380) / 2000, _x1 / 1500, (600 + 1108) / 2000))
# o momento BOOM: o Duplo Smash recortado do kit (fundo tirado, pixeis reais)
_m = Image.open(os.path.join(B, 'kit-cartaz', 'fotos', 'duplo-smash.png'))
# 3.a ronda (juiz): tira o resto meio transparente do palito que flutuava por cima do pao
_m.putalpha(_m.getchannel('A').point(lambda v: 0 if v < 150 else v))
for L in (500, 900):
    _m.resize((L, round(_m.height * L / _m.width)), Image.LANCZOS).save(os.path.join(DST, f'momento-duplo-smash-{L}.webp'), 'WEBP', quality=82, method=6)
gera('casa', WA('wa-13.jpg'), [800, 1200], 'WhatsApp do dono 27/10 07:36 (wa-13, Boom! Serra da Estrela)')
# a visita leva uma foto que nao esta na galeria (juiz: repeticao)
gera('visita', WA('wa-05.jpg'), [600, 1000], 'WhatsApp do dono 27/10 07:32 (wa-05, Bolo do caco com manteiga de alho)')
GAL = [('wa-03.jpg', 'Asas de frango com molho BBQ'), ('wa-04.jpg', 'Batata gulosa'), ('wa-17.jpg', 'Boom! Kamikaze'),
       ('wa-02.jpg', 'Cogumelos frescos salteados'), ('wa-09.jpg', 'Boom! Cheddar Lovers'), ('wa-06.jpg', 'Pimentos Padrón'),
       ('wa-22.jpg', 'Tequeños — palitos de queijo'), ('wa-08.jpg', 'Boom! Burguesinha')]
for i, (f, alt) in enumerate(GAL, 1):
    gera(f'galeria-{i}', WA(f), [600, 1000], f'WhatsApp do dono 27/10 ({f})')
    idx[f'galeria-{i}']['alt'] = alt

for p in prep['produtos']:
    o = p.get('foto_origem_final')
    if not o:
        continue
    f = re.search(r'\(([^)]+)\)', o).group(1)
    src = WA(f) if o.startswith('WhatsApp') else os.path.join(O, 'glovo', 'fotos', f)
    # miniatura do menu: quadrado ao centro (so recorte)
    im = Image.open(src)
    w, h = im.size
    if w > h:
        c = ((w - h) / 2 / w, 0, 1 - (w - h) / 2 / w, 1)
    else:
        c = (0, (h - w) / 2 / h, 1, 1 - (h - w) / 2 / h)
    gera('p-' + p['id'], src, [160, 320], o, crop=c, q_avif=50, q_webp=74)
    gera('c-' + p['id'], src, [480, 800], o, q_avif=52, q_webp=76)

# camadas reais (ja fatiadas pelo tools/camadas/fatiar.py)
cam_src = os.path.join(B, 'media', 'camadas', 'portobello-v3')  # 3 camadas pelo contorno real (2.a ronda)
cam_dst = os.path.join(B, 'dist', 'assets', 'camadas')
os.makedirs(cam_dst, exist_ok=True)
for f in os.listdir(cam_src):
    shutil.copy(os.path.join(cam_src, f), cam_dst)
    if f.endswith('.webp'):  # versao de telemovel (o palco tem ~360 px)
        im = Image.open(os.path.join(cam_src, f))
        im.resize((450, max(1, round(im.height * 450 / im.width))), Image.LANCZOS).save(
            os.path.join(cam_dst, f.replace('.webp', '-450.webp')), 'WEBP', quality=84, method=6)
# logotipos
log_dst = os.path.join(B, 'dist', 'assets', 'logo')
os.makedirs(log_dst, exist_ok=True)
for f in os.listdir(os.path.join(B, 'media', 'logo')):
    shutil.copy(os.path.join(B, 'media', 'logo', f), log_dst)
json.dump(idx, open(os.path.join(AQUI, 'imagens.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tot = sum(os.path.getsize(os.path.join(DST, f)) for f in os.listdir(DST))
print('imagens', len(idx), 'ficheiros', len(os.listdir(DST)), 'MB', round(tot / 1e6, 2))

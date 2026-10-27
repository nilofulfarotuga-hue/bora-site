# -*- coding: utf-8 -*-
"""Imagens da loja na app (bloco A): so redimensionar e comprimir, nunca mudar o aspeto.

Gera ../media/app/:
  logo.png (icone 512 com fundo carvao), capa.webp (1600 px), galeria-1..4.webp,
  produtos/<product_id>.webp (1200 px no lado maior, qualidade 82)
e ../media/app/indice.json  {caminho_storage: {local, origem}}
"""
import json, os
from PIL import Image, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
O = os.path.join(B, 'origem')
M = os.path.join(B, 'media', 'app')
os.makedirs(os.path.join(M, 'produtos'), exist_ok=True)
RID = 'boom-burger-guarda'

prep = json.load(open(os.path.join(AQUI, 'menu-preparacao.json'), encoding='utf-8'))
emp = json.load(open(os.path.join(O, 'emparelhamento.json'), encoding='utf-8'))
WA_DATA = '27/10/2026'


def guarda(src, dst, lado, q=82):
    im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
    im.thumbnail((lado, lado), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=q, method=6)
    return im.size


ind = {}
# logotipo e capa
import shutil
shutil.copy(os.path.join(B, 'media', 'logo', 'boom-icone-512.png'), os.path.join(M, 'logo.png'))
ind[f'{RID}/logo.png'] = {'local': 'media/app/logo.png', 'origem': 'PDF vetorial do dono (WhatsApp 27/10 07:42), ícone gerado pelo logo_svg.py'}
CAPA = 'wa-11.jpg'   # Boom! Duplo Smash, horizontal, luz quente
print('capa', guarda(os.path.join(O, 'whatsapp', CAPA), os.path.join(M, 'capa.webp'), 1600))
ind[f'{RID}/capa.webp'] = {'local': 'media/app/capa.webp', 'origem': f'WhatsApp do dono {WA_DATA} 07:36 ({CAPA})'}
GAL = ['wa-20.jpg', 'wa-03.jpg', 'wa-04.jpg', 'wa-17.jpg']
for i, f in enumerate(GAL, 1):
    guarda(os.path.join(O, 'whatsapp', f), os.path.join(M, f'galeria-{i}.webp'), 1400)
    ind[f'{RID}/galeria-{i}.webp'] = {'local': f'media/app/galeria-{i}.webp', 'origem': f'WhatsApp do dono {WA_DATA} ({f})'}

por_gid = {str(k): v for k, v in emp.items()}
for p in prep['produtos']:
    v = por_gid.get(str(p['glovo_id']))
    if v and v.get('wa'):
        src, orig = os.path.join(O, 'whatsapp', v['wa']), f"WhatsApp do dono {WA_DATA} ({v['wa']})"
    elif p.get('foto_origem'):
        src, orig = os.path.join(O, p['foto_origem']), f"Glovo do dono, loja 539100 ({os.path.basename(p['foto_origem'])})"
    else:
        print('SEM FOTO', p['name'])
        continue
    dst = os.path.join(M, 'produtos', p['id'] + '.webp')
    guarda(src, dst, 1200)
    key = f"{RID}/produtos/{p['id']}.webp"
    ind[key] = {'local': f"media/app/produtos/{p['id']}.webp", 'origem': orig}
    p['foto_storage'] = key
    p['foto_origem_final'] = orig
json.dump(ind, open(os.path.join(M, 'indice.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(prep, open(os.path.join(AQUI, 'menu-preparacao.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
tot = sum(os.path.getsize(os.path.join(B, v['local'])) for v in ind.values())
print('ficheiros', len(ind), 'total KB', tot // 1024)

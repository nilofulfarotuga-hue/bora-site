# -*- coding: utf-8 -*-
"""F6 (adendo 3): fotos oficiais do FABRICANTE para as bebidas sem foto do dono, sem alterar o produto.
Os PNG oficiais sao transparentes: so se poe fundo branco (como as outras bebidas), redimensiona e comprime
(1200 px no lado maior, WebP 82, igual ao imagens_app.py). Gera ../media/app/indice-fabricante.json para o
subir_storage.py. Origem de cada ficheiro em origem/ORIGEM.md (seccao Fabricantes)."""
import json, os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
RID = 'boom-burger-guarda'
F = {
    'boom-cerveja-letra-a': ('cervejaletra-letra-a.png', 'https://cervejaletra.pt/product/letra-a/ (LETRA-AAA.png)'),
    'boom-cerveja-letra-b': ('cervejaletra-letra-b.png', 'https://cervejaletra.pt/product/letra-b/ (LETRA-B-SITE.png)'),
    'boom-cerveja-letra-c': ('cervejaletra-letra-c.png', 'https://cervejaletra.pt/product/letra-c/ (LETRA-C-SITE.png)'),
    'boom-cerveja-letra-d': ('cervejaletra-letra-d.png', 'https://cervejaletra.pt/product/letra-d/ (LETRA-D-SITE.png)'),
    'boom-cerveja-letra-e': ('cervejaletra-letra-e.png', 'https://cervejaletra.pt/product/letra-e/ (LETRA-E-SITE.png)'),
    'boom-cerveja-letra-f': ('cervejaletra-letra-f.png', 'https://cervejaletra.pt/product/letra-f/ (LETRA-F-SITE.png)'),
    'boom-agua-das-pedras': ('superbockgroup-pedras-salgadas-25cl.png',
                             'https://superbockgroup.com/produtos/pedras-salgadas/ (Salgadas_25cl_Bottle_spritz_SK.png)'),
}
ind = {}
for pid, (nome, url) in F.items():
    im = Image.open(os.path.join(B, 'origem', 'fabricante', nome)).convert('RGBA')
    fundo = Image.new('RGB', im.size, (255, 255, 255))
    fundo.paste(im, (0, 0), im)
    fundo.thumbnail((1200, 1200), Image.LANCZOS)
    dst = os.path.join(B, 'media', 'app', 'produtos', f'{pid}-fabricante.webp')
    fundo.save(dst, 'WEBP', quality=82, method=6)
    ind[f'{RID}/produtos/{pid}-fabricante.webp'] = {'local': f'media/app/produtos/{pid}-fabricante.webp',
                                                     'origem': f'foto oficial do fabricante, 27/10/2026: {url}'}
    print(pid, fundo.size, os.path.getsize(dst))
json.dump(ind, open(os.path.join(B, 'media', 'app', 'indice-fabricante.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

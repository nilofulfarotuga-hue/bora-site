# -*- coding: utf-8 -*-
"""Logotipo da Boom! Burger: PDF vetorial do dono -> SVG com as partes separadas + PNG.

Le os 42 desenhos do PDF (PyMuPDF get_drawings) e escreve cada um como <path>, agrupados:
  pao-cima, sementes, boom, boom-pequeno (o "hamburgueria artesanal" pequenino), pao-baixo,
  burger (a manuscrita), rodape (o "HAMBURGUERIA ARTESANAL" de baixo, que no PDF e texto
  com a fonte Now-Bold e aqui vai em curvas, para nao depender da fonte).
Cores tiradas do PDF: dourado #DBB545, branco #FFFFFF, fundo #2B2A29.

Saidas em ../media/logo/:
  boom-logo.svg            (completo, fundo transparente)
  boom-logo-fundo.svg      (completo, fundo carvao)
  boom-logo-partes.svg     (o mesmo com ids por parte, para a animacao do site)
  boom-marca.svg           (so o hamburguer: paes + sementes + BOOM; serve de icone)
  boom-logo-{1024,512,192}.png  transparentes; boom-icone-{512,192,180,32}.png; favicon.ico
"""
import os, re
import pymupdf as fitz

AQUI = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(AQUI, '..', 'origem', 'logo', 'boom-burger-logo-vetor.pdf')
OUT = os.path.join(AQUI, '..', 'media', 'logo')
os.makedirs(OUT, exist_ok=True)
DOURADO, BRANCO, FUNDO = '#DBB545', '#FFFFFF', '#2B2A29'

doc = fitz.open(PDF)
pg = doc[0]
dr = pg.get_drawings()


def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def path_d(x):
    d, cur = [], None
    for it in x['items']:
        op = it[0]
        if op == 'l':
            p1, p2 = it[1], it[2]
            if cur is None or abs(cur.x - p1.x) > 1e-3 or abs(cur.y - p1.y) > 1e-3:
                d.append('M%s %s' % (f(p1.x), f(p1.y)))
            d.append('L%s %s' % (f(p2.x), f(p2.y)))
            cur = p2
        elif op == 'c':
            p1, c1, c2, p2 = it[1], it[2], it[3], it[4]
            if cur is None or abs(cur.x - p1.x) > 1e-3 or abs(cur.y - p1.y) > 1e-3:
                d.append('M%s %s' % (f(p1.x), f(p1.y)))
            d.append('C%s %s %s %s %s %s' % (f(c1.x), f(c1.y), f(c2.x), f(c2.y), f(p2.x), f(p2.y)))
            cur = p2
        elif op == 're':
            r = it[1]
            d.append('M%s %sH%sV%sH%sZ' % (f(r.x0), f(r.y0), f(r.x1), f(r.y1), f(r.x0)))
            cur = None
        elif op == 'qu':
            q = it[1]
            d.append('M%s %sL%s %sL%s %sL%s %sZ' % tuple(f(v) for pt in (q.ul, q.ur, q.lr, q.ll) for v in (pt.x, pt.y)))
            cur = None
    if x.get('closePath'):
        d.append('Z')
    return ''.join(d)


def cor(x):
    return '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in x['fill'])


# indices medidos (ver relatorio): 0 fundo, 1 pao de baixo, 2-7 "Burger", 8-11 "BOOM",
# 12-32 letras pequenas, 33 pao de cima, 34-41 sementes
GRUPOS = [('pao-cima', [33]), ('sementes', list(range(34, 42))), ('boom', [8, 9, 10, 11]),
          ('boom-pequeno', list(range(12, 33))), ('pao-baixo', [1]), ('burger', [2, 3, 4, 5, 6, 7])]
assert len(dr) == 42 and cor(dr[0]) == FUNDO and cor(dr[33]) == DOURADO and cor(dr[1]) == DOURADO


def g_paths(ids):
    out = []
    for i in ids:
        x = dr[i]
        fr = ' fill-rule="evenodd"' if x.get('even_odd') else ''
        out.append('<path d="%s" fill="%s"%s/>' % (path_d(x), cor(x), fr))
    return '\n    '.join(out)


# rodape: o texto em curvas que o proprio MuPDF gera (defs com os glifos + <use>)
svg_txt = pg.get_svg_image(text_as_path=True)
defs = re.search(r'<defs>.*?</defs>', svg_txt, re.S)
uses = re.findall(r'<use [^>]*/>', svg_txt)
rod_defs = defs.group(0) if defs else ''
rod = '\n    '.join(uses)
# os <use> herdam o fill do grupo; o texto e branco
assert len(uses) >= 20, len(uses)


def svg(vb, corpo, fundo=False, titulo='Boom! Burger — Hamburgueria Artesanal'):
    x, y, w, h = vb
    bg = '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(x), f(y), f(w), f(h), FUNDO) if fundo else ''
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'viewBox="%s %s %s %s" role="img" aria-label="%s">\n<title>%s</title>\n%s\n%s\n%s\n</svg>\n'
            % (f(x), f(y), f(w), f(h), titulo, titulo, rod_defs, bg, corpo))


corpo_partes = '\n'.join('  <g id="%s">\n    %s\n  </g>' % (n, g_paths(ids)) for n, ids in GRUPOS)
corpo_partes += '\n  <g id="rodape" fill="%s">\n    %s\n  </g>' % (BRANCO, rod)
VB_TODO = (225, 45, 392, 510)          # conteudo: x 237-605, y 57-543, com margem
VB_MARCA = (296, 40, 262, 351)         # paes + BOOM: x 313-541, y 57-374

open(os.path.join(OUT, 'boom-logo-partes.svg'), 'w', encoding='utf-8').write(svg(VB_TODO, corpo_partes))
open(os.path.join(OUT, 'boom-logo.svg'), 'w', encoding='utf-8').write(svg(VB_TODO, corpo_partes))
open(os.path.join(OUT, 'boom-logo-fundo.svg'), 'w', encoding='utf-8').write(svg(VB_TODO, corpo_partes, fundo=True))
marca = '\n'.join('  <g id="%s">\n    %s\n  </g>' % (n, g_paths(ids)) for n, ids in GRUPOS if n in ('pao-cima', 'sementes', 'boom', 'boom-pequeno', 'pao-baixo'))
open(os.path.join(OUT, 'boom-marca.svg'), 'w', encoding='utf-8').write(svg(VB_MARCA, marca, titulo='Boom! Burger'))
# icone quadrado com fundo (favicon, app, partilha)
q = 400
cx, cy = 427, 215
VB_ICONE = (cx - q / 2, cy - q / 2, q, q)
open(os.path.join(OUT, 'boom-icone.svg'), 'w', encoding='utf-8').write(svg(VB_ICONE, marca, fundo=True, titulo='Boom! Burger'))


def png(svgfile, lado, nome):
    d = fitz.open(os.path.join(OUT, svgfile))
    p = d[0]
    z = lado / max(p.rect.width, p.rect.height)
    pix = p.get_pixmap(matrix=fitz.Matrix(z, z), alpha=True)
    pix.save(os.path.join(OUT, nome))
    return pix.width, pix.height


for lado in (1024, 512, 192):
    print('logo', lado, png('boom-logo.svg', lado, 'boom-logo-%d.png' % lado))
for lado in (512, 192, 180, 32):
    print('icone', lado, png('boom-icone.svg', lado, 'boom-icone-%d.png' % lado))
from PIL import Image
Image.open(os.path.join(OUT, 'boom-icone-192.png')).save(os.path.join(OUT, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
print('ok')

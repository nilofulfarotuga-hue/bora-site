# -*- coding: utf-8 -*-
"""Fatiar um produto recortado em CAMADAS REAIS (componente 14 do components-premio).

Recebe um PNG recortado (fundo transparente, ex.: rembg) e as fronteiras entre ingredientes,
medidas na propria foto. Escreve uma imagem por camada (WebP com alfa), em que cada pixel e o
pixel real da foto: nada e desenhado nem gerado. Os pesos de duas camadas vizinhas somam 1,
por isso as camadas encaixadas reconstroem a foto.

Cada fronteira pode ser:
  - um numero (y em pixeis do recorte): corte direito, com rampa suave de --suave px;
  - "escuro-fim:<y>"   : segue o CONTORNO REAL onde acaba uma zona escura que comeca no topo
                         (ex.: o fundo do pao de cima preto); <y> e o valor de recurso/limite;
  - "escuro-inicio:<y>": segue o contorno onde comeca a zona escura de baixo (o topo do pao de
                         baixo). Os contornos usam rampa curta (--suave-contorno), para a peca
                         sair com a forma verdadeira do pao e nao como uma fatia de foto.
  (Licao de 27/10, Boom! Burger: o juiz independente disse que os cortes direitos "parecem uma
   imagem partida"; os paes recortados pelo contorno leem-se como camadas a serio.)

Uso:
  python fatiar.py recorte.png saida/ 380:pao-cima escuro-fim:588:molho 748:bacon 872:carne escuro-inicio:1002:pao-baixo 1108
  --suave 24  --suave-contorno 8  --largura 900  --escuro 70 (luminancia que conta como "escuro")

Saida: saida/camada-<n>-<nome>.webp, saida/solida.webp e saida/camadas.json (top/altura em %).
"""
import json, os, sys
import numpy as np
from PIL import Image

args, opts, it = [], {}, iter(sys.argv[1:])
for a_ in it:
    if a_.startswith('--'):
        opts[a_] = next(it)
    else:
        args.append(a_)
SUAVE = int(opts.get('--suave', 24))
SUAVE_C = int(opts.get('--suave-contorno', 8))
LARG = int(opts.get('--largura', 900))
ESCURO = float(opts.get('--escuro', 100))
src, out = args[0], args[1]
os.makedirs(out, exist_ok=True)

im = Image.open(src).convert('RGBA')
a = np.array(im).astype(np.float32)
H0, W0 = a.shape[:2]
alfa = a[..., 3] / 255.0
lum = 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]
# mediana 2D: as sementes brancas do pao (pontos pequenos) nao podem parar o contorno
import cv2
MED = int(opts.get('--mediana', 21))
lum = cv2.medianBlur(np.clip(lum, 0, 255).astype(np.uint8), MED).astype(np.float32)
# saturacao (max-min): o pao preto e cinzento; bacon, queijo e agriao sao coloridos
sat = cv2.medianBlur(np.clip(a[..., :3].max(axis=2) - a[..., :3].min(axis=2), 0, 255).astype(np.uint8), MED).astype(np.float32)
SAT = float(opts.get('--sat', 45))
e_escuro = (lum < ESCURO) & (sat < SAT)
colunas = np.where(alfa.max(axis=0) > 0.05)[0]
x0, x1 = int(colunas.min()), int(colunas.max()) + 1


def suaviza(v, k=int(opts.get('--alisar', 31))):
    """mediana deslizante + media: tira os dentes do contorno sem o deformar."""
    p = np.pad(v, k // 2, mode='edge')
    med = np.array([np.median(p[i:i + k]) for i in range(len(v))])
    p2 = np.pad(med, k // 2, mode='edge')
    return np.convolve(p2, np.ones(k) / k, mode='valid')


def contorno(tipo, y_ref):
    """y da fronteira por coluna. escuro-fim: do 1.o pixel opaco para baixo, enquanto escuro.
    escuro-inicio: do ultimo pixel opaco para cima, enquanto escuro. Limitado a +-90 px de y_ref."""
    ys = np.full(W0, float(y_ref))
    for x in range(x0, x1):
        op = np.where(alfa[:, x] > 0.5)[0]
        if len(op) < 10:
            continue
        col = lum[:, x]
        # comeca DENTRO do pao (longe das sementes do topo e das folhas da base), procura a zona
        # escura e segue-a ate ela acabar: a fronteira e o contorno real do pao.
        if tipo == 'escuro-fim':
            y = max(op.min(), y_ref - 70)
            lim = y + 40
            while y < lim and not e_escuro[y, x]:
                y += 1
            while y < H0 - 1 and (e_escuro[y, x] or alfa[y, x] < 0.5) and y < y_ref + 90:
                y += 1
        else:
            y = min(op.max(), y_ref + 50)
            lim = y - 40
            while y > lim and not e_escuro[y, x]:
                y -= 1
            while y > 0 and (e_escuro[y, x] or alfa[y, x] < 0.5) and y > y_ref - 90:
                y -= 1
        ys[x] = min(max(y, y_ref - 90), y_ref + 90)
    ys[:x0] = ys[x0]
    ys[x1:] = ys[x1 - 1]
    return suaviza(ys)


fr = []  # (array de y por coluna, nome, largura da rampa, y medio)
for c in args[2:]:
    partes = c.split(':')
    if partes[0] in ('escuro-fim', 'escuro-inicio'):
        y_ref = int(partes[1])
        nome = partes[2] if len(partes) > 2 else ''
        ys = contorno(partes[0], y_ref)
        fr.append((ys, nome, SUAVE_C, y_ref))
    else:
        y = int(partes[0])
        nome = partes[1] if len(partes) > 1 else ''
        fr.append((np.full(W0, float(y)), nome, SUAVE, y))
nomes = [n for _, n, _, _ in fr[:-1]]
topo, fundo = int(fr[0][3]), int(fr[-1][3])
H = fundo - topo
esc = LARG / (x1 - x0)
yy = np.arange(H0, dtype=np.float32)[:, None]


def rampa(ys, larg):
    """0 acima da fronteira, 1 abaixo; suave numa faixa de 'larg' px."""
    t = np.clip((yy - (ys[None, :] - larg / 2)) / max(larg, 1), 0, 1)
    return t * t * (3 - 2 * t)


manif = {'fonte': os.path.basename(src), 'largura_px': LARG, 'altura_px': round(H * esc),
         'proporcao': round((x1 - x0) / H, 4), 'camadas': []}
for i, nome in enumerate(nomes):
    w = np.ones((H0, W0), dtype=np.float32)
    if i > 0:
        w *= rampa(fr[i][0], fr[i][2])
    if i < len(nomes) - 1:
        w *= 1 - rampa(fr[i + 1][0], fr[i + 1][2])
    camada = a.copy()
    camada[..., 3] = a[..., 3] * w
    # caixa vertical real da camada (onde ha alfa)
    linhas = np.where((camada[..., 3] > 3).any(axis=1))[0]
    c0 = max(int(linhas.min()), topo) if len(linhas) else topo
    c1 = min(int(linhas.max()) + 1, fundo) if len(linhas) else fundo
    peca = Image.fromarray(camada[c0:c1, x0:x1].astype(np.uint8), 'RGBA')
    peca = peca.resize((LARG, max(1, round((c1 - c0) * esc))), Image.LANCZOS)
    f = f'camada-{i + 1}-{nome}.webp'
    peca.save(os.path.join(out, f), 'WEBP', quality=86, method=6)
    manif['camadas'].append({'n': i + 1, 'nome': nome, 'ficheiro': f,
                             'top_pct': round((c0 - topo) / H * 100, 3), 'altura_pct': round((c1 - c0) / H * 100, 3)})
sol = Image.fromarray(a[topo:fundo, x0:x1].astype(np.uint8), 'RGBA').resize((LARG, round(H * esc)), Image.LANCZOS)
sol.save(os.path.join(out, 'solida.webp'), 'WEBP', quality=86, method=6)
manif['solida'] = 'solida.webp'
json.dump(manif, open(os.path.join(out, 'camadas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(manif, ensure_ascii=False))

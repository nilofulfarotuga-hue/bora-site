# -*- coding: utf-8 -*-
"""Liga cada foto do WhatsApp (original do dono, maior) ao produto da Glovo (mesma foto,
recortada em quadrado). Por pontos ORB + homografia: conta pontos bons por par.

Saida: ../origem/emparelhamento.json  {glovo_id: {wa, pontos, nome}}
"""
import cv2, glob, json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(AQUI, '..', 'origem')
g = json.load(open(os.path.join(O, 'glovo', 'produtos.json'), encoding='utf-8'))
orb = cv2.ORB_create(2000)


def feat(path, maxd=900):
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    s = maxd / max(im.shape)
    if s < 1:
        im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    return orb.detectAndCompute(im, None)


wa = sorted(glob.glob(os.path.join(O, 'whatsapp', 'wa-*.jpg')))
fw = {os.path.basename(p): feat(p) for p in wa}
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
res = {}
for x in g:
    if not x.get('foto_local'):
        continue
    kg, dg = feat(os.path.join(O, 'glovo', 'fotos', x['foto_local']))
    best = (0, None)
    for n, (kw, dw) in fw.items():
        if dg is None or dw is None:
            continue
        m = bf.knnMatch(dg, dw, k=2)
        good = [a for a, b in (p for p in m if len(p) == 2) if a.distance < 0.75 * b.distance]
        if len(good) < 12:
            continue
        import numpy as np
        src = np.float32([kg[a.queryIdx].pt for a in good]).reshape(-1, 1, 2)
        dst = np.float32([kw[a.trainIdx].pt for a in good]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 6.0)
        inl = int(mask.sum()) if mask is not None else 0
        if inl > best[0]:
            best = (inl, n)
    res[str(x['glovo_id'])] = {'nome': x['nome'].strip(), 'seccao': x['seccao'], 'wa': best[1] if best[0] >= 25 else None, 'pontos': best[0]}
json.dump(res, open(os.path.join(O, 'emparelhamento.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
usadas = {}
for k, v in res.items():
    print(f"{v['pontos']:4d} {str(v['wa']):10s} {v['seccao'][:10]:10s} {v['nome']}")
    if v['wa']:
        usadas.setdefault(v['wa'], []).append(v['nome'])
print('WA sem produto:', [os.path.basename(p) for p in wa if os.path.basename(p) not in usadas])
print('WA com 2+ produtos:', {k: v for k, v in usadas.items() if len(v) > 1})

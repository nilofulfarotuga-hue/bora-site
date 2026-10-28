# -*- coding: utf-8 -*-
"""Adendo 1, ponto 1: o titulo do heroi aparece INTEIRO no primeiro segundo e nunca com acentos soltos.

Grava em video (Playwright) a abertura de <url> a 1440x900, com e sem "Reduzir movimento",
e tira fotogramas aos 0,3/0,6/1,0/1,5/3/6 s contados a partir do momento em que a pagina comeca a chegar (commit).
Tambem le no DOM, a cada 100 ms ate 2 s, a opacidade do titulo e se ele foi partido em linhas.
Saida: bora-site/provas/boom-burger/titulo-<modo>-<t>s.png e titulo-folha.png + titulo.json
"""
import json, os, subprocess, sys, time
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
PROVAS = os.path.abspath(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger'))
TMP = os.path.join(PROVAS, '_video_tmp')
os.makedirs(TMP, exist_ok=True)
URL = sys.argv[1]
TEMPOS = [0.3, 0.6, 1.0, 1.5, 3.0, 6.0]
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for modo in ('normal', 'reduz'):
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, locale='pt-PT',
                            reduced_motion='reduce' if modo == 'reduz' else 'no-preference',
                            record_video_dir=TMP, record_video_size={'width': 1440, 'height': 900})
        t0 = time.time()
        pg = ctx.new_page()
        t_nav = time.time() - t0
        amostras = []
        pg.goto(URL + ('&' if '?' in URL else '?') + 'prova=' + str(int(time.time())), wait_until='commit', timeout=60000)
        t_commit = time.time() - t0
        fim = time.time() + 2.2
        while time.time() < fim:
            try:
                amostras.append(pg.evaluate("""() => { const h = document.querySelector('.heroi h1'); if (!h) return null;
                  const cs = getComputedStyle(h); return {t: performance.now()|0, op: +cs.opacity,
                  partido: !!h.querySelector('[class*=line],[class*=linha]'), fonte: document.fonts.check('40px "Bebas Neue"'),
                  texto: h.innerText.replace(/\\s+/g,' ').trim()}; }"""))
            except Exception:
                pass
            time.sleep(0.1)
        time.sleep(5)
        video = pg.video.path()
        ctx.close()
        quadros = []
        for t in TEMPOS:
            out = os.path.join(PROVAS, f'titulo-{modo}-{t:.1f}s.png')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t_commit + t:.2f}', '-i', video, '-frames:v', '1',
                            '-vf', 'crop=760:520:0:250', out], check=False)
            quadros.append(out)
        res[modo] = {'t_pagina_criada_s': round(t_nav, 2), 't_commit_s': round(t_commit, 2),
                     'amostras': [a for a in amostras if a][:22], 'quadros': [os.path.basename(q) for q in quadros]}
    b.close()
# folha: linha 1 normal, linha 2 reduzido
from PIL import Image, ImageDraw
W, H = 380, 260
folha = Image.new('RGB', (W * len(TEMPOS), (H + 22) * 2), 'white')
d = ImageDraw.Draw(folha)
for r, modo in enumerate(('normal', 'reduz')):
    for c, t in enumerate(TEMPOS):
        f = os.path.join(PROVAS, f'titulo-{modo}-{t:.1f}s.png')
        if os.path.exists(f):
            im = Image.open(f).convert('RGB').resize((W, H))
            folha.paste(im, (c * W, r * (H + 22) + 22))
        d.text((c * W + 6, r * (H + 22) + 4), f'{modo} {t:.1f}s', fill='black')
folha.save(os.path.join(PROVAS, 'titulo-folha.png'))
json.dump(res, open(os.path.join(PROVAS, 'titulo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for modo, v in res.items():
    am = v['amostras']
    vis = [a for a in am if a['op'] >= 0.99]
    print(modo, 'commit', v['t_commit_s'], 's | amostras', len(am), '| partido alguma vez:', any(a['partido'] for a in am),
          '| opacidade 1 a partir de', (vis[0]['t'] if vis else None), 'ms (relogio da pagina) | texto:', am[-1]['texto'] if am else None)

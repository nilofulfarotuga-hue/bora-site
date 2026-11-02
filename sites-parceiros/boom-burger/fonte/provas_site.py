# -*- coding: utf-8 -*-
"""Seleccao das provas (JPG leves) -> bora-site/provas/boom-burger/selecao/ + pagina index.html.
Publica-se como ramo de pre-visualizacao do projeto Pages boom-burger (provas.boom-burger-778.pages.dev),
SEPARADO do dominio do cliente e do site institucional (que tem trabalho de outras sessoes). noindex."""
import html, json, os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger'))
S = os.path.join(P, 'selecao')
os.makedirs(S, exist_ok=True)
ITENS = [
    ('Telemóvel 390 — herói (o logótipo monta-se ao abrir)', 'final-390-heroi.png'),
    ('Telemóvel 390 — cena das camadas: início', 'final-390-cena-inicio.png'),
    ('Telemóvel 390 — cena das camadas: meio', 'final-390-cena-meio.png'),
    ('Telemóvel 390 — cena das camadas: fim (foto real)', 'final-390-cena-fim.png'),
    ('Telemóvel 390 — momento BOOM (letras do logótipo + Duplo Smash real)', 'final-390-boom.png'),
    ('Telemóvel 390 — menu', 'final-390-menu.png'),
    ('Telemóvel 390 — horário e morada', 'final-390-visita.png'),
    ('Telemóvel 390 — "Reduzir movimento" ligado: herói', 'final-390-reduz-heroi.png'),
    ('Telemóvel 390 — "Reduzir movimento" ligado: cena (estática, foto inteira)', 'final-390-reduz-cena-meio.png'),
    ('Android 360 — herói', 'final-360-heroi.png'),
    ('Computador 1440 — herói', 'final-1440-heroi.png'),
    ('Computador 1440 — cena: início', 'final-1440-cena-inicio.png'),
    ('Computador 1440 — cena: meio', 'final-1440-cena-meio.png'),
    ('Computador 1440 — cena: fim (foto real no mesmo sítio)', 'final-1440-cena-fim.png'),
    ('Computador 1440 — favoritos', 'final-1440-favoritos.png'),
    ('Computador 1440 — momento BOOM', 'final-1440-boom.png'),
    ('Computador 1440 — menu', 'final-1440-menu.png'),
    ('Computador 1440 — a casa', 'final-1440-casa.png'),
    ('Computador 1440 — galeria', 'final-1440-galeria.png'),
    ('Computador 1440 — visita', 'final-1440-visita.png'),
    ('Título do herói por vídeo: 0,3 / 0,6 / 1 / 1,5 / 3 / 6 s (em cima normal, em baixo "Reduzir movimento")', 'titulo-folha.png'),
    ('Teste dos 3 segundos — computador (Glovo à esquerda, site à direita)', '3segundos/3segundos-1440.png'),
    ('Teste dos 3 segundos — telemóvel', '3segundos/3segundos-390.png'),
    ('App web como cliente: /#/loja/boom-burger-guarda com "Em breve"', 'a4-cliente-loja-390-b.png'),
    ('App web como parceiro: painel da Boom! Burger', 'a4-parceiro-painel-1280.png'),
]
cartoes = []
for i, (leg, f) in enumerate(ITENS, 1):
    src = os.path.join(P, f)
    if not os.path.exists(src):
        print('falta', f)
        continue
    im = Image.open(src).convert('RGB')
    im.thumbnail((1440, 2400))
    nome = f'{i:02d}-' + os.path.basename(f).replace('.png', '.jpg')
    im.save(os.path.join(S, nome), 'JPEG', quality=78, optimize=True, progressive=True)
    cartoes.append(f'<figure><a href="{nome}"><img src="{nome}" alt="{html.escape(leg)}" loading="lazy"></a><figcaption>{html.escape(leg)}</figcaption></figure>')
med = json.load(open(os.path.join(P, 'final-medidas.json'), encoding='utf-8')) if os.path.exists(os.path.join(P, 'final-medidas.json')) else {}
linhas = ''.join(f'<tr><td>{k}</td><td>{v.get("scroll_lateral")}</td><td>{len(v.get("alvos_pequenos", []))}</td><td>{v.get("img_sem_alt")}</td><td>{v.get("barra_altura")}</td><td>{len(v.get("erros", []))}</td></tr>' for k, v in med.items() if isinstance(v, dict) and 'erros' in v)
H = f'''<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Provas — Boom! Burger (27/10/2026)</title>
<style>body{{margin:0;background:#121110;color:#F6F0E2;font:16px/1.5 system-ui,sans-serif;padding:24px}}h1{{margin:0 0 8px}}p{{color:#BFB6A6;max-width:70ch}}
a{{color:#DBB545}}.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}figure{{margin:0;background:#1C1B1A;border-radius:12px;overflow:hidden}}
img{{width:100%;display:block}}figcaption{{padding:10px 12px;font-size:14px;color:#BFB6A6}}table{{border-collapse:collapse;margin:16px 0}}td,th{{border:1px solid #3A3836;padding:6px 10px}}</style></head>
<body><h1>Provas — site e loja Boom! Burger</h1>
<p>Missão boom-burger-2026-10-27. Site: <a href="https://boomburger.boraguarda.com/">boomburger.boraguarda.com</a> (noindex até o dono aprovar).
Capturas do site publicado (Chromium com iPhone 390, Android 360 e computador 1440; com e sem "Reduzir movimento").</p>
<table><tr><th>configuração</th><th>scroll lateral</th><th>alvos &lt;44px</th><th>img sem alt</th><th>botão fixo (px)</th><th>erros consola</th></tr>{linhas}</table>
<div class="g">{''.join(cartoes)}</div></body></html>'''
open(os.path.join(S, 'index.html'), 'w', encoding='utf-8').write(H)
open(os.path.join(S, '_headers'), 'w', encoding='utf-8', newline='\n').write('/*\n  X-Robots-Tag: noindex\n')
print('selecao', len(cartoes), 'MB', round(sum(os.path.getsize(os.path.join(S, f)) for f in os.listdir(S)) / 1e6, 2))

# -*- coding: utf-8 -*-
"""Fontes servidas pelo proprio site (Lighthouse: o CSS do Google Fonts bloqueava 1,6 s).
Bebas Neue 400 e Inter (variavel, 400-800), subconjuntos latin e latin-ext, woff2.
Saida: ../dist/assets/fonts/*.woff2 e fonte/fontes.css (as @font-face, para ir dentro do HTML).
Licenca: SIL Open Font License (as duas)."""
import os, re, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(AQUI, '..', 'dist', 'assets', 'fonts')
os.makedirs(DST, exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
URL = 'https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400..800&display=swap'
css = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': UA}), timeout=30).read().decode()
saida = []
for bloco in re.findall(r'/\* ([a-z-]+) \*/\s*(@font-face\s*{[^}]+})', css):
    subset, ff = bloco
    if subset not in ('latin', 'latin-ext'):
        continue
    fam = re.search(r"font-family: '([^']+)'", ff).group(1)
    url = re.search(r'url\((https://[^)]+\.woff2)\)', ff).group(1)
    nome = f"{fam.lower().replace(' ', '-')}-{subset}.woff2"
    urllib.request.urlretrieve(url, os.path.join(DST, nome))
    ff = ff.replace(url, f'assets/fonts/{nome}')
    saida.append(ff)
    print(nome, os.path.getsize(os.path.join(DST, nome)) // 1024, 'KB')
open(os.path.join(AQUI, 'fontes.css'), 'w', encoding='utf-8').write('\n'.join(saida))
print('faces', len(saida))

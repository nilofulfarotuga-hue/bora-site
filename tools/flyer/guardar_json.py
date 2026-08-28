# -*- coding: utf-8 -*-
"""Le' um JSON do playwright (dataURL) e grava o PNG em assets/logos/<nome>.png"""
import json, base64, io, os, sys
from PIL import Image
nome, ficheiro = sys.argv[1], sys.argv[2]
src = os.path.join(r"C:\Users\danil\Desktop\projetosflutter\bora_app", ficheiro)
d = json.load(open(src, encoding='utf-8'))
if isinstance(d, str): d = json.loads(d)
if isinstance(d, list): d = d[0]
if 'data' not in d:
    print("SEM DATA:", d); sys.exit(1)
im = Image.open(io.BytesIO(base64.b64decode(d['data'].split(',',1)[1]))).convert('RGBA')
out = f"assets/logos/{nome}.png"
im.save(out)
print(f"{nome}: natural={d.get('natural')} -> {im.size} | bbox={im.getbbox()} -> {out}")
os.remove(src)

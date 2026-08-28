# -*- coding: utf-8 -*-
"""Recorta o branco de um screenshot de overlay e grava em assets/logos/<nome>.png"""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_flyer import recortar_fundo_branco, aparar
nome, fich = sys.argv[1], sys.argv[2]
src = os.path.join(r"C:\Users\danil\Desktop\projetosflutter\bora_app", fich)
im = Image.open(src)
print("shot:", im.size)
im = aparar(recortar_fundo_branco(im))
out = f"assets/logos/{nome}.png"
im.save(out)
print(f"{nome} gravado: {im.size} -> {out}")
os.remove(src)

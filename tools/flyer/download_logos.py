# -*- coding: utf-8 -*-
"""Descarrega os logos das lojas a partir das URL reais (DB / sites oficiais)."""
import os, io, sys, requests
from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logos')
os.makedirs(OUT, exist_ok=True)
SB = "https://ojykpzwqrtusfeakzrna.supabase.co/storage/v1/object/public/restaurant-assets/"
GL = "https://glovo.dhmedia.io/image/stores-glovo/stores/"

SOURCES = {
    "mcdonalds":   SB + "logos/mcdonalds-guarda.png",
    "goola":       SB + "goola-acai-guarda/logo-marca-1787900000000.png",
    "auchan":      SB + "auchan-guarda/logo-1785605796991.jpg",
    "continente":  SB + "continente-guarda/logo.jpg?v=1779381008660",
    "intermarche": SB + "intermarche-guarda/logo-1785605561577.jpg",
    "ouroprata":   SB + "82e3162c-0560-443a-a44a-104dc71a95ef/logo-1784442556809.png",
    "saboresbrasil": SB + "sabores-brasil-guarda/logo-quadrado.jpg",
    "wells":       GL + "d7c347fe753508b380ad7bdf1773e821185708b02a4c50e7d29595c69c5a1383",
    "worten":      GL + "7fc69372aab37a0f631ec35779f95db1e8d8fbff047d420b34c3da23c76fb1a6",
    "leroymerlin": GL + "c8c423bf7caf31999581e5f3c49a10d1b3b5b6c84be3c9214f51c3c1c4186b3b",
    "kiwoko":      GL + "ab0e88201f7ccd3d3942d217d558982acab5276bc83289d34e87d6a5a90b9c2c",
    "zippy":       GL + "25bc4583943a3023f20bc118f988b1f091c773ea471202df66694c53852f1c32",
    # favicons pequenos - substituidos depois por versao grande se possivel
    "kfc":         "https://www.kfc.pt/wp-content/uploads/2025/01/cropped-favicon-180x180.png",
    "burgerking":  "https://www.google.com/s2/favicons?domain=burgerking.pt&sz=128",
    "pingodoce":   "https://www.pingodoce.pt/on/demandware.static/Sites-pingo-doce-Site/-/default/dw514eb86b/images/favicons/favicon-32x32.png",
}

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

for key, url in SOURCES.items():
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content))
        im.load()
        path = os.path.join(OUT, key + ".png")
        im.convert("RGBA").save(path)
        print(f"OK   {key:14s} {im.size[0]}x{im.size[1]}  {im.mode:5s}  {len(r.content)//1024}KB")
    except Exception as e:
        print(f"FALHA {key:14s} {type(e).__name__}: {e}")

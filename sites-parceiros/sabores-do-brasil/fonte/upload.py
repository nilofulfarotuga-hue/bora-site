"""Sobe as imagens ao bucket publico restaurant-assets/sabores-brasil-guarda/.
A service key e lida do ficheiro; nunca e impressa."""
import os
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(BASE, "final")
ENV = r"C:\Users\danil\Desktop\projetosflutter\bora_app\backend\.env"

cfg = {}
with open(ENV, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")

URL = cfg["SUPABASE_URL"].rstrip("/")
KEY = cfg["SUPABASE_SERVICE_ROLE_KEY"]
print(f"projeto: {URL}   chave: {len(KEY)} chars (nao impressa)")

BUCKET, PASTA = "restaurant-assets", "sabores-brasil-guarda"
MIME = {".png": "image/png", ".jpg": "image/jpeg"}

publicos = {}
for nome in sorted(os.listdir(F)):
    caminho = os.path.join(F, nome)
    ext = os.path.splitext(nome)[1].lower()
    with open(caminho, "rb") as fh:
        dados = fh.read()
    destino = f"{BUCKET}/{PASTA}/{nome}"
    r = requests.post(
        f"{URL}/storage/v1/object/{destino}",
        headers={"Authorization": f"Bearer {KEY}",
                 "Content-Type": MIME[ext],
                 "x-upsert": "true"},
        data=dados, timeout=120)
    pub = f"{URL}/storage/v1/object/public/{PASTA and destino}"
    print(f"  {r.status_code}  {nome:24s} {len(dados)//1024:4d} KB  {r.text[:90]}")
    if r.status_code in (200, 201):
        publicos[nome] = pub

print("\n== leitura de volta (HTTP publico, sem token) ==")
for nome, pub in publicos.items():
    g = requests.get(pub, timeout=60)
    print(f"  {g.status_code}  {len(g.content)//1024:4d} KB  {g.headers.get('content-type'):10s}  {pub}")

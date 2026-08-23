"""Sobe as imagens ilustrativas ao bucket publico. Chave lida do ficheiro, nunca impressa."""
import os
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
G = os.path.join(BASE, "geradas")
ENV = r"C:\Users\danil\Desktop\projetosflutter\bora_app\backend\.env"

cfg = {}
for line in open(ENV, encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
URL = cfg["SUPABASE_URL"].rstrip("/")
KEY = cfg["SUPABASE_SERVICE_ROLE_KEY"]
BUCKET, PASTA = "restaurant-assets", "sabores-brasil-guarda"

pub = {}
for nome in sorted(os.listdir(G)):
    if not nome.endswith(".jpg"):
        continue
    with open(os.path.join(G, nome), "rb") as fh:
        dados = fh.read()
    destino = f"{BUCKET}/{PASTA}/{nome}"
    r = requests.post(f"{URL}/storage/v1/object/{destino}",
                      headers={"Authorization": f"Bearer {KEY}",
                               "Content-Type": "image/jpeg", "x-upsert": "true"},
                      data=dados, timeout=180)
    print(f"  {r.status_code}  {nome:26s} {len(dados)//1024:4d} KB")
    if r.status_code in (200, 201):
        pub[nome] = f"{URL}/storage/v1/object/public/{destino}"

print("\n== leitura de volta (publica, sem token) ==")
for nome, u in pub.items():
    g = requests.get(u, timeout=90)
    print(f"  {g.status_code}  {len(g.content)//1024:4d} KB  {g.headers.get('content-type')}  {nome}")
print("\nURLs:")
for nome, u in pub.items():
    print(f"  {nome} -> {u}")

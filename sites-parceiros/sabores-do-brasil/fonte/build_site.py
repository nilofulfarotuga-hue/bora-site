"""Injecta o logo Bora e o QR (base64) no site da Keli e verifica o resultado."""
import os, re, json

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDA = r"C:\Users\danil\Desktop\sabores-do-brasil\index.html"
MEDIA = r"C:\Users\danil\Desktop\sabores-do-brasil\media"

html = open(os.path.join(BASE, "template_site.html"), encoding="utf-8").read()
assets = json.load(open(os.path.join(BASE, "assets_site.json"), encoding="utf-8"))

pedidos = set(re.findall(r"\{\{(\w+)\}\}", html))
faltam = pedidos - set(assets)
if faltam:
    raise SystemExit(f"FALTAM ASSETS: {faltam}")
for k, v in assets.items():
    html = html.replace("{{" + k + "}}", v)
if re.findall(r"\{\{\w+\}\}", html):
    raise SystemExit("sobraram marcadores")

open(SAIDA, "w", encoding="utf-8").write(html)
print(f"escrito: {SAIDA}  {os.path.getsize(SAIDA)//1024} KB")

print("\n== os 6 precos da base estao na fonte? ==")
for p in ["47.25", "2.10", "0.53", "12.60", "10.50", "1.05"]:
    print(f"  preco:{p}: {'SIM' if 'preco:' + p in html else 'NAO'}")

print("== conteudo obrigatorio ==")
checks = {
  "video mp4":        'media/sabores.mp4' in html,
  "video webm":       'media/sabores.webm' in html,
  "poster":           'poster="media/poster.webp"' in html,
  "muted+playsinline":'muted' in html and 'playsinline' in html,
  "48 horas":         '48 horas' in html or 'AVISO_HORAS' in html,
  "horario 9h-20h":   '9h às 20h' in html,
  "sem limite":       'Sem limite' in html,
  "pagamentos":       'MB WAY' in html,
  "Play Store":       'pt.boraapp.bora' in html,
  "registo web":      'registo-cliente' in html,
  "link para a demo": 'demo-festas.pages.dev' in html,
  "LOJA_ATIVA":       'var LOJA_ATIVA' in html[:2600],
  "Cormorant":        'Cormorant+Garamond' in html,
}
for k, v in checks.items():
    print(f"  {k:20s}: {'SIM' if v else 'NAO'}")

sem_b64 = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "«img»", html)
print("\n== varredura WhatsApp ==")
mau = re.findall(r"[^<>]*(?:encomend|pedid)[^<>]*whats[^<>]*|[^<>]*whats[^<>]*(?:encomend|pedid)[^<>]*", sem_b64, re.I)
print(f"  'encomendar' junto de 'WhatsApp': {len(mau)} {'(limpo)' if not mau else mau[:2]}")
print(f"  ocorrencias de wa.me: {sem_b64.count('wa.me')} (1 = contacto discreto no rodape)")
rodape = sem_b64[sem_b64.find("<footer"):]
print(f"  esta so no rodape: {'SIM' if sem_b64.count('wa.me')==1 and 'wa.me' in rodape else 'NAO'}")
print(f"  e discreto (contacto-discreto, 12px): {'SIM' if 'contacto-discreto' in rodape else 'NAO'}")

print("\n== media/ ==")
tot = 0
for f in sorted(os.listdir(MEDIA)):
    t = os.path.getsize(os.path.join(MEDIA, f)); tot += t
    print(f"  {f:22s} {t//1024:6d} KB")
print(f"  TOTAL {tot//1024} KB")

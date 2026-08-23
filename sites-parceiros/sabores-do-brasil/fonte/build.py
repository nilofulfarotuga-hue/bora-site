"""Injecta as imagens base64 no template e verifica o resultado."""
import os, re, json

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDA = r"C:\Users\danil\Desktop\sabores-do-brasil\index.html"

with open(os.path.join(BASE, "template.html"), encoding="utf-8") as fh:
    html = fh.read()
with open(os.path.join(BASE, "assets_b64.json"), encoding="utf-8") as fh:
    assets = json.load(fh)

pedidos = set(re.findall(r"\{\{(\w+)\}\}", html))
print("marcadores no template:", sorted(pedidos))
print("assets disponiveis     :", sorted(assets))
faltam = pedidos - set(assets)
if faltam:
    raise SystemExit(f"FALTAM ASSETS: {faltam}")

for k, v in assets.items():
    html = html.replace("{{" + k + "}}", v)

sobra = re.findall(r"\{\{\w+\}\}", html)
if sobra:
    raise SystemExit(f"SOBRARAM MARCADORES: {set(sobra)}")

os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
with open(SAIDA, "w", encoding="utf-8") as fh:
    fh.write(html)

tam = os.path.getsize(SAIDA)
print(f"\nescrito: {SAIDA}")
print(f"tamanho: {tam//1024} KB ({tam} bytes)")

# verificacoes de conteudo
# os precos sao formatados em runtime pelo JS (47.25 -> "47,25"), por isso
# aqui confirma-se o literal na fonte; o valor RENDERIZADO e' provado no browser.
precos = ["47.25", "0.53", "2.10", "1.05", "12.60", "10.50"]
print("\n== os 6 precos da base estao na fonte? ==")
for p in precos:
    print(f"  preco:{p}: {'SIM' if 'preco:' + p in html else 'NAO'}")

nomes = ["Cento de Salgados", "Salgados Grandes", "Salgados Variados",
         "Bolo de Cenoura", "Pudim de Leite", "Brigadeiro ou Beijinho"]
print("== os 6 produtos estao na pagina? ==")
for n in nomes:
    print(f"  {n:26s}: {'SIM' if n in html else 'NAO'}")

print("== outras verificacoes ==")
print(f"  ficheiro unico, sem src externos de imagem: "
      f"{'SIM' if not re.search(r'src=\"(?!data:)https?://', html) else 'NAO'}")
print(f"  WhatsApp da Keli (351937402120): {'SIM' if '351937402120' in html else 'NAO'}")
print(f"  WhatsApp do Danilo (351937501673): {'SIM' if '351937501673' in html else 'NAO'}")
print(f"  link Play Store: {'SIM' if 'pt.boraapp.bora' in html else 'NAO'}")
print(f"  verde Bora #16A34A: {'SIM' if '#16A34A' in html else 'NAO'}")
print(f"  laranja Bora #F97316: {'SIM' if '#F97316' in html else 'NAO'}")
print(f"  imagens embutidas em base64: {html.count('data:image')}")

print("\n== varredura WhatsApp (adendo 1 e 2) ==")
sem_b64 = re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "«imagem»", html)
mau = re.findall(r"[^<>]*(?:encomend|pedid)[^<>]*whats[^<>]*|[^<>]*whats[^<>]*(?:encomend|pedid)[^<>]*",
                 sem_b64, re.I)
print(f"  texto que junta 'encomendar' e 'WhatsApp': {len(mau)} {'(limpo)' if not mau else mau[:3]}")
for termo in ["Encomendar pelo WhatsApp", "wa-flutua"]:
    print(f"  '{termo}' removido: {'SIM' if termo not in sem_b64 else 'NAO'}")
print(f"  ocorrencias de wa.me: {sem_b64.count('wa.me')} "
      f"(2 = Danilo na demo + contacto discreto da Keli no rodape)")
# o unico WhatsApp da Keli tem de estar no rodape, em texto pequeno e sem CTA
rodape = sem_b64[sem_b64.find("<footer"):]
print(f"  WhatsApp da Keli SO no rodape: "
      f"{'SIM' if sem_b64.count('wa.me/351937402120') == 1 and 'wa.me/351937402120' in rodape else 'NAO'}")
print(f"  esse link e' discreto (font-size:12px, sem classe btn): "
      f"{'SIM' if 'font-size:12px' in rodape and 'btn' not in rodape.split('Falar com a Keli')[1][:220] else 'NAO'}")
print(f"  CTA 'Encomendar pelo Bora App': {sem_b64.count('Encomendar pelo Bora App')}x")
print(f"  aponta para #demo: {sem_b64.count('href=\"#demo\"')}x")

print("\n== dois destinos (adendo 2) ==")
print(f"  LOJA_ATIVA no topo do ficheiro: "
      f"{'SIM' if 'var LOJA_ATIVA' in sem_b64[:3000] else 'NAO'}")
print(f"  link web registo-cliente: {'SIM' if 'bora-app-web.pages.dev/#/registo-cliente' in sem_b64 else 'NAO'}")
print(f"  texto coming_soon: {'SIM' if 'abre em breve' in sem_b64 else 'NAO'}")
print(f"  texto loja activa: {'SIM' if 'Encomendar agora' in sem_b64 else 'NAO'}")
print(f"  caixas [data-destinos]: {sem_b64.count('data-destinos')}x (folha de pagamento + faixa)")

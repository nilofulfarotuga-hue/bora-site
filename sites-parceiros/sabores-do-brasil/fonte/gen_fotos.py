"""Gera a fotografia de comida com o Gemini (nano banana).
A chave e' lida do backend/.env; nunca e' impressa."""
import os, sys, base64, json, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "geradas")
os.makedirs(OUT, exist_ok=True)
ENV = r"C:\Users\danil\Desktop\projetosflutter\bora_app\backend\.env"

cfg = {}
with open(ENV, encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
KEY = cfg.get("GEMINI_API_KEY")
if not KEY:
    sys.exit("sem GEMINI_API_KEY")
print(f"chave carregada: {len(KEY)} chars (nao impressa)")

if "--listar" in sys.argv:
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                     headers={"x-goog-api-key": KEY}, timeout=60)
    print("HTTP", r.status_code)
    if r.status_code == 200:
        for m in r.json().get("models", []):
            n = m["name"].split("/")[-1]
            if "image" in n or "imagen" in n:
                print("  ", n, "|", ",".join(m.get("supportedGenerationMethods", []))[:60])
    else:
        print(r.text[:400])
    sys.exit(0)

ESTILO = (" Ultra-realistic editorial food photography, macro lens, soft natural window light "
          "raking from the left, warm honey and cream tones, simple uncluttered warm background, "
          "shallow depth of field, extreme texture detail, appetising. "
          "Absolutely no text, no letters, no numbers, no logo, no watermark, no hands, no people.")

FOTOS = [
    ("bolo-cenoura", "4:5",
     "A Brazilian carrot cake (bolo de cenoura) with a bright deep-orange moist crumb, covered by a "
     "thick glossy chocolate brigadeiro fudge glaze that pours over the top edge and drips slowly down "
     "the side. One thick slice is cut and pulled slightly forward so the tender orange crumb is fully "
     "visible. Rustic cream ceramic plate, loose crumbs on the plate."),
    ("pudim", "4:5",
     "A classic Brazilian pudim de leite condensado, a silky pale custard ring with a hole in the centre, "
     "unmoulded onto a white ceramic plate, dark amber caramel sauce glistening as it runs down the sides "
     "and pools around the base. Perfectly smooth glossy surface, tiny caramel droplets."),
    ("brigadeiros", "1:1",
     "Brazilian party sweets: dark chocolate brigadeiros rolled in chocolate sprinkles next to snow-white "
     "coconut beijinhos each topped with a single clove, every sweet in its own small pleated paper case, "
     "arranged in loose rows on a warm wooden surface, a few sprinkles and coconut flakes scattered around."),
    ("coxinha", "4:5",
     "A Brazilian coxinha: a golden deep-fried teardrop-shaped croquette with a crisp breadcrumb crust, "
     "broken open in the middle revealing steaming shredded chicken and creamy white catupiry cheese "
     "filling. Visible wisps of steam, crunchy golden crumbs scattered on a warm terracotta surface, "
     "one whole coxinha softly out of focus behind."),
    ("tabuleiro", "16:9",
     "A large party platter piled generously with assorted Brazilian fried savouries: golden teardrop "
     "coxinhas, oval kibbeh, half-moon risoles and round cheese balls packed close together on a rustic "
     "wooden board lined with parchment, a small bowl of dipping sauce to one side, crisp crumbs on the "
     "table. Abundant and celebratory, seen from a high three-quarter angle."),
]

MODELO = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

for nome, ar, desc in FOTOS:
    destino = os.path.join(OUT, f"{nome}.png")
    if os.path.exists(destino) and "--forcar" not in sys.argv:
        print(f"  {nome}: ja existe, salto")
        continue
    corpo = {
        "contents": [{"parts": [{"text": desc + ESTILO}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": ar}},
    }
    # A quota do plano gratis e' por MINUTO: pedidos seguidos queimam-na.
    # Ritmo lento e recuo longo, em vez de martelar.
    for tentativa in (1, 2, 3, 4, 5):
        r = requests.post(URL, headers={"x-goog-api-key": KEY,
                                        "Content-Type": "application/json"},
                          json=corpo, timeout=180)
        if r.status_code == 200:
            break
        espera = 70 if r.status_code == 429 else 10
        print(f"  {nome}: HTTP {r.status_code} (tentativa {tentativa}) "
              f"-> espero {espera}s", flush=True)
        time.sleep(espera)
    if r.status_code != 200:
        print(f"  {nome}: FALHOU"); continue
    dados = r.json()
    guardou = False
    for cand in dados.get("candidates", []):
        for p in cand.get("content", {}).get("parts", []):
            inline = p.get("inlineData") or p.get("inline_data")
            if inline and inline.get("data"):
                with open(destino, "wb") as fh:
                    fh.write(base64.b64decode(inline["data"]))
                print(f"  {nome}: OK  {os.path.getsize(destino)//1024} KB  ({ar})")
                guardou = True
    if not guardou:
        print(f"  {nome}: resposta sem imagem -> {json.dumps(dados)[:220]}")
    time.sleep(25)   # nao voltar a queimar a quota por minuto

print("\nficheiros em geradas/:", sorted(os.listdir(OUT)))

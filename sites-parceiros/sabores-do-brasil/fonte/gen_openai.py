"""Terceira via para a fotografia de comida: OpenAI (gpt-image-1).
Higgsfield ficou sem creditos e a quota diaria do Gemini esgotou.
A chave e' lida do backend/.env; nunca e' impressa."""
import os, sys, base64, time
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
KEY = cfg.get("OPENAI_API_KEY")
if not KEY:
    sys.exit("sem OPENAI_API_KEY")
print(f"chave OpenAI carregada: {len(KEY)} chars (nao impressa)")

ESTILO = (" Ultra-realistic editorial food photography, macro lens, soft natural window light "
          "raking from the left, warm honey and cream tones, simple uncluttered warm background, "
          "shallow depth of field, extreme texture detail, appetising and mouth-watering. "
          "Absolutely no text, no letters, no numbers, no logo, no watermark, no hands, no people.")

FOTOS = [
    ("bolo-cenoura", "1024x1536",
     "A Brazilian carrot cake (bolo de cenoura) with a bright deep-orange moist crumb, covered by a "
     "thick glossy chocolate brigadeiro fudge glaze that pours over the top edge and drips slowly down "
     "the side. One thick slice is cut and pulled slightly forward so the tender orange crumb is fully "
     "visible. Rustic cream ceramic plate, loose crumbs on the plate."),
    ("pudim", "1024x1536",
     "A classic Brazilian pudim de leite condensado, a silky pale custard ring with a hole in the centre, "
     "unmoulded onto a white ceramic plate, dark amber caramel sauce glistening as it runs down the sides "
     "and pools around the base. Perfectly smooth glossy surface, tiny caramel droplets."),
    ("brigadeiros", "1024x1024",
     "Brazilian party sweets: dark chocolate brigadeiros rolled in chocolate sprinkles next to snow-white "
     "coconut beijinhos each topped with a single clove, every sweet in its own small pleated paper case, "
     "arranged in loose rows on a warm wooden surface, a few sprinkles and coconut flakes scattered around."),
    ("coxinha", "1024x1536",
     "A Brazilian coxinha: a golden deep-fried teardrop-shaped croquette with a crisp breadcrumb crust, "
     "broken open in the middle revealing steaming shredded chicken and creamy white catupiry cheese "
     "filling. Visible wisps of steam, crunchy golden crumbs scattered on a warm terracotta surface, "
     "one whole coxinha softly out of focus behind."),
    ("tabuleiro", "1536x1024",
     "A large party platter piled generously with assorted Brazilian fried savouries: golden teardrop "
     "coxinhas, oval kibbeh, half-moon risoles and round cheese balls packed close together on a rustic "
     "wooden board lined with parchment, a small bowl of dipping sauce to one side, crisp crumbs on the "
     "table. Abundant and celebratory, seen from a high three-quarter angle."),
    ("cat-festas", "1024x1024",
     "A friendly 3D-rendered app category icon for a party-food section: a golden Brazilian coxinha, a "
     "small chocolate-sprinkled brigadeiro and a slice of frosted cake grouped together on a small plate, "
     "with two thin colourful paper streamers and a couple of confetti dots floating behind them. Soft "
     "rounded shapes, glossy clay-render style, bright warm orange background, cheerful and clean, "
     "centred composition with generous margins, similar to a modern mobile app tile illustration."),
]

URL = "https://api.openai.com/v1/images/generations"
for nome, tam, desc in FOTOS:
    destino = os.path.join(OUT, f"{nome}.png")
    if os.path.exists(destino) and "--forcar" not in sys.argv:
        print(f"  {nome}: ja existe, salto"); continue
    corpo = {"model": "gpt-image-1", "prompt": desc + ESTILO,
             "size": tam, "quality": "high", "n": 1}
    r = None
    for tentativa in (1, 2, 3):
        r = requests.post(URL, headers={"Authorization": f"Bearer {KEY}",
                                        "Content-Type": "application/json"},
                          json=corpo, timeout=300)
        if r.status_code == 200:
            break
        print(f"  {nome}: HTTP {r.status_code} (tent.{tentativa}) {r.text[:220]}", flush=True)
        time.sleep(12)
    if not r or r.status_code != 200:
        print(f"  {nome}: FALHOU"); continue
    d = r.json()["data"][0]
    raw = base64.b64decode(d["b64_json"]) if d.get("b64_json") else requests.get(d["url"], timeout=120).content
    with open(destino, "wb") as fh:
        fh.write(raw)
    print(f"  {nome}: OK  {len(raw)//1024} KB  ({tam})", flush=True)

print("\nficheiros gerados:", sorted(os.listdir(OUT)))

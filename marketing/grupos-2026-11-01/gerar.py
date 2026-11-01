#!/usr/bin/env python3
"""Imagens 1080x1080 para grupos de Facebook (01/11/2026): foto real do site/Boom + título Inter + logo.
Padrão dos cartões de 30/09 (docs/marketing/grupos-prontos/2026-09-30): foto grande, título branco em cima,
pastilha laranja (único laranja) com o BEMVINDO, rodapé com o endereço. Sem IA a desenhar comida."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

S = 1080
F = '/usr/share/fonts/opentype/inter/'
def font(n, s): return ImageFont.truetype(F + n, s)
SITE = '/home/claude/bora-site'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
VERDE = (22, 163, 74); VERDE_ESC = (21, 128, 61); LARANJA = (249, 115, 22); BRANCO = (255, 255, 255)

def cover(im, w, h, foco=0.5):
    """Recorta ao centro (foco horizontal 0-1) e redimensiona para cobrir w x h."""
    im = im.convert('RGB')
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = int((im.width - w) * foco); y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def gradiente(im, topo=0.62, fundo=0.80):
    """Escurece o topo e o fundo para o texto ler-se sobre a foto."""
    ov = Image.new('L', (1, S), 0)
    px = ov.load()
    for y in range(S):
        t = y / S
        a = 0
        if t < 0.52: a = int(255 * topo * (1 - t / 0.52) ** 0.8)
        if t > 0.62: a = max(a, int(255 * fundo * ((t - 0.62) / 0.38)))
        px[0, y] = a
    ov = ov.resize((S, S))
    preto = Image.new('RGB', (S, S), (8, 12, 10))
    return Image.composite(preto, im, ov)

def texto_multilinha(d, linhas, x, y, f, fill, lh):
    for l in linhas:
        d.text((x, y), l, font=f, fill=fill)
        y += lh
    return y

def logo_card(im, x, y, h=96):
    logo = Image.open(f'{SITE}/assets/img/bora_logo.png').convert('RGBA')
    w = int(logo.width * h / logo.height)
    logo = logo.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([x, y, x + w + 24, y + h + 20], radius=18, fill=BRANCO)
    im.paste(logo, (x + 12, y + 10), logo)

def pastilha(d, texto, x, y, f, fill):
    w = d.textlength(texto, font=f)
    h = f.size + 34
    d.rounded_rectangle([x, y, x + w + 56, y + h], radius=h // 2, fill=fill)
    d.text((x + 28, y + 15), texto, font=f, fill=BRANCO)
    return x + w + 56

def cartao(nome, foto, foco, titulo, sub, pastilha_txt, rodape, logo_fn=logo_card):
    im = gradiente(cover(foto, S, S, foco))
    d = ImageDraw.Draw(im)
    logo_fn(im, 56, 48)
    ft = font('InterDisplay-ExtraBold.otf', 92)
    y = texto_multilinha(d, titulo, 56, 190, ft, BRANCO, 100)
    fs = font('Inter-Medium.otf', 40)
    texto_multilinha(d, sub, 56, 850, fs, BRANCO, 48)
    if pastilha_txt:
        pastilha(d, pastilha_txt, 56, 920, font('Inter-Bold.otf', 36), LARANJA)
    fr = font('Inter-Medium.otf', 30)
    d.text((56, 1020), rodape, font=fr, fill=(220, 225, 220))
    im.save(f'{OUT}/{nome}.jpg', quality=92, subsampling=0)
    print(nome)

# 1 — mercados ao domicílio
cartao('1-mercados-guarda', Image.open(f'{SITE}/assets/cinema/c3_mercado_sacos.webp'), 0.15,
       ['As compras do', 'supermercado', 'à porta de casa'],
       ['Continente, Pingo Doce, Auchan e Intermarché.'],
       'Código BEMVINDO: 5 € no primeiro pedido',
       'Bora — Guarda · boraguarda.com/baixar')

# 2 — restaurantes / Boom em breve (foto real do dono)
boom = Image.open(f'{SITE}/sites-parceiros/boom-burger/kit-cartaz/fotos/kamikaze.png').convert('RGBA')
fundo = Image.new('RGB', (S, S), (16, 14, 12))
# halo quente atrás do hambúrguer
halo = Image.new('RGB', (S, S), (16, 14, 12)); hd = ImageDraw.Draw(halo)
hd.ellipse([140, 300, 940, 1100], fill=(92, 58, 20)); halo = halo.filter(ImageFilter.GaussianBlur(120))
fundo = Image.blend(fundo, halo, 1.0)
bw = 900; bh = int(boom.height * bw / boom.width); b = boom.resize((bw, bh), Image.LANCZOS)
fundo.paste(b, ((S - bw) // 2, 460), b)
def logo_boom(im, x, y, h=96):
    logo_card(im, x, y, h)
    lb = Image.open(f'{SITE}/sites-parceiros/boom-burger/kit-cartaz/logo/boom-logo-1024.png').convert('RGBA')
    hb = 120; wb = int(lb.width * hb / lb.height); lb = lb.resize((wb, hb), Image.LANCZOS)
    im.paste(lb, (S - 56 - wb, y - 10), lb)
cartao('2-restaurantes-boom', fundo, 0.5,
       ['Boom! Burger', 'chega à tua porta', 'esta semana'],
       ['Hambúrgueres artesanais da Guarda, pela app.'],
       'Código BEMVINDO: 5 € no primeiro pedido',
       'Bora — Guarda · boraguarda.com/baixar', logo_fn=logo_boom)

# 3 — limpeza / serviços
cartao('3-limpeza-servicos', Image.open(f'{SITE}/assets/cinema/c5_limpeza_sala.webp'), 0.55,
       ['Limpeza em casa,', 'marcada na app,', 'à hora que queres'],
       ['E lavagem do carro ou um favor, na Guarda.'],
       'Código BEMVINDO: 5 € no primeiro pedido',
       'Bora — Guarda · boraguarda.com/baixar')

# 4 — Em Dia (trabalhador independente)
def logo_emdia(im, x, y, h=96):
    d = ImageDraw.Draw(im)
    f = font('InterDisplay-Black.otf', 64)
    w = d.textlength('Em Dia', font=f)
    d.rounded_rectangle([x, y, x + w + 110, y + h + 20], radius=18, fill=BRANCO)
    # ícone: quadrado verde com visto
    d.rounded_rectangle([x + 18, y + 18, x + 18 + 80, y + 18 + 80], radius=16, fill=VERDE)
    d.line([(x + 38, y + 60), (x + 54, y + 76), (x + 82, y + 42)], fill=BRANCO, width=10, joint='curve')
    d.text((x + 112, y + 22), 'Em Dia', font=f, fill=VERDE_ESC)
im4 = gradiente(cover(Image.open(f'{SITE}/assets/cinema/c7_maos_telemovel.webp'), S, S, 0.5))
d = ImageDraw.Draw(im4)
logo_emdia(im4, 56, 48)
ft = font('InterDisplay-ExtraBold.otf', 88)
texto_multilinha(d, ['Recibos verdes', 'sem sustos:', 'o que pagar e', 'até quando'], 56, 190, ft, BRANCO, 96)
fs = font('Inter-Medium.otf', 38)
texto_multilinha(d, ['Segurança Social, IVA e IRS num só sítio. Grátis.'], 56, 860, fs, BRANCO, 46)
pastilha(d, 'Calculadora grátis do recibo verde', 56, 920, font('Inter-Bold.otf', 34), VERDE)
d.text((56, 1020), 'Em Dia · emdia.boraguarda.com', font=font('Inter-Medium.otf', 30), fill=(220, 225, 220))
im4.save(f'{OUT}/4-em-dia-recibos-verdes.jpg', quality=92, subsampling=0)
print('4-em-dia-recibos-verdes')

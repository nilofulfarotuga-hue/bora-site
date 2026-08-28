# -*- coding: utf-8 -*-
"""
Cenario de fundo do flyer Bora — cidade 3D cartoon futurista, gerada por script.

Existe porque a quota de imagem do Gemini esta a zero (confirmado 2026-08-28,
`limit: 0` nos modelos pro e flash). Ver RELATORIO_FLYER.md.

Desenha em meia resolucao e amplia: e' ~4x mais rapido e os elementos suaves
(luz, desfoque, particulas) nao perdem nada. O PC do Danilo tem 4GB.
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter

VERDE = (22, 163, 74)
LARANJA = (249, 115, 22)


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _degrade_vertical(W, H, stops):
    """Degrade com varios pontos de paragem: [(pos 0..1, (r,g,b)), ...]."""
    img = Image.new("RGB", (1, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                px[0, y] = _lerp(c0, c1, (t - p0) / (p1 - p0) if p1 > p0 else 0)
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((W, H), Image.NEAREST)


def _brilho_radial(W, H, cx, cy, rx, ry, cor, forca):
    """Mancha de luz eliptica, somada por cima (screen-like)."""
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    passos = 26
    for i in range(passos, 0, -1):
        t = i / passos
        d.ellipse([cx - rx * t, cy - ry * t, cx + rx * t, cy + ry * t],
                  fill=int(forca * (1 - t) ** 1.7))
    layer = layer.filter(ImageFilter.GaussianBlur(min(W, H) * 0.03))
    return Image.merge("RGB", [Image.new("L", (W, H), c) for c in cor]), layer


def _predio_iso(d, cx, cy, larg, prof, alt, base, luz, rng, janelas=True):
    """Prisma isometrico: topo em losango + duas faces. Cantos ao estilo cartoon."""
    hw, hp = larg / 2.0, prof / 2.0
    topo = [(cx, cy - alt - hp / 2), (cx + hw, cy - alt), (cx, cy - alt + hp / 2), (cx - hw, cy - alt)]
    esq = [(cx - hw, cy - alt), (cx, cy - alt + hp / 2), (cx, cy + hp / 2), (cx - hw, cy)]
    dir_ = [(cx + hw, cy - alt), (cx, cy - alt + hp / 2), (cx, cy + hp / 2), (cx + hw, cy)]
    c_topo = _lerp(base, (255, 255, 255), 0.30 * luz)
    c_esq = _lerp(base, (0, 0, 0), 0.34)
    c_dir = _lerp(base, (0, 0, 0), 0.14)
    d.polygon(esq, fill=c_esq)
    d.polygon(dir_, fill=c_dir)
    d.polygon(topo, fill=c_topo)
    if not janelas or alt < 26:
        return
    # janelas acesas: pequenas luzes quentes/verdes nas duas faces
    filas = max(1, int(alt / 15))
    for f in range(filas):
        yy = cy - alt + 12 + f * 15
        for k in range(2):
            if rng.random() < 0.42:
                xx = cx - hw * 0.62 + k * hw * 0.55
                cor = LARANJA if rng.random() < 0.6 else VERDE
                cor = _lerp(cor, (255, 245, 210), 0.45)
                d.rectangle([xx, yy, xx + 4.5, yy + 6], fill=cor)
        for k in range(2):
            if rng.random() < 0.42:
                xx = cx + hw * 0.12 + k * hw * 0.55
                cor = LARANJA if rng.random() < 0.5 else VERDE
                cor = _lerp(cor, (255, 245, 210), 0.35)
                d.rectangle([xx, yy, xx + 4.5, yy + 6], fill=cor)


def _faixa_cidade(W, H, y_base, escala, densidade, seed, alt_max):
    """Uma camada de skyline isometrico. Devolve RGBA para compor."""
    rng = random.Random(seed)
    cam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(cam)
    larg = 46 * escala
    prof = 26 * escala
    # varre em diagonal para pintar de tras para a frente
    cols = int(W / (larg * 0.75)) + 4
    for j in range(5):
        for i in range(-2, cols):
            if rng.random() > densidade:
                continue
            cx = i * larg * 0.80 + (j % 2) * larg * 0.40 - larg
            cy = y_base + j * prof * 0.85
            alt = rng.uniform(alt_max * 0.28, alt_max) * escala
            tons = [(26, 54, 62), (22, 46, 58), (30, 62, 60), (24, 58, 52), (34, 52, 66)]
            base = tons[rng.randrange(len(tons))]
            base = _lerp(base, (10, 20, 32), max(0.0, (4 - j) / 6.0))
            _predio_iso(d, cx, cy, larg, prof, alt, base, luz=(j + 2) / 6.0, rng=rng)
    return cam


def _rasto(d, pontos, cor, largura):
    for i in range(len(pontos) - 1):
        d.line([pontos[i], pontos[i + 1]], fill=cor, width=largura)


def gerar_fundo(W, H, seed=20260828):
    """Devolve o cenario em RGB no tamanho (W, H)."""
    rng = random.Random(seed)
    w, h = W // 2, H // 2  # desenha em meia resolucao

    # 1 — ceu de entardecer
    base = _degrade_vertical(w, h, [
        (0.00, (8, 18, 34)),
        (0.16, (11, 30, 50)),
        (0.34, (13, 44, 62)),
        (0.52, (15, 52, 68)),
        (0.66, (18, 50, 62)),
        (0.78, (14, 38, 52)),
        (0.90, (10, 25, 40)),
        (1.00, (7, 16, 30)),
    ])

    # 2 — auroras de marca (verde e laranja)
    for cx, cy, rx, ry, cor, f in [
        (w * 0.24, h * 0.20, w * 0.62, h * 0.26, VERDE, 120),
        (w * 0.82, h * 0.36, w * 0.55, h * 0.22, LARANJA, 95),
        (w * 0.50, h * 0.62, w * 0.70, h * 0.20, VERDE, 80),
        (w * 0.16, h * 0.86, w * 0.50, h * 0.18, LARANJA, 70),
    ]:
        cor_img, mask = _brilho_radial(w, h, cx, cy, rx, ry, cor, f)
        base = Image.composite(Image.blend(base, cor_img, 0.55), base, mask)

    # 3 — halo claro no topo, para o logo e o titulo assentarem
    cor_img, mask = _brilho_radial(w, h, w * 0.5, h * 0.115, w * 0.72, h * 0.15,
                                   (236, 250, 240), 210)
    base = Image.composite(cor_img, base, mask)

    base = base.convert("RGBA")

    # 4 — grelha de ruas em neon (perspetiva isometrica)
    ruas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ruas)
    for k in range(-14, 30):
        x0 = k * 92
        dr.line([(x0, h * 0.26), (x0 + h * 0.66, h * 0.99)],
                fill=VERDE + (58,), width=3)
        dr.line([(w - x0, h * 0.26), (w - x0 - h * 0.66, h * 0.99)],
                fill=LARANJA + (46,), width=3)
    ruas = ruas.filter(ImageFilter.GaussianBlur(2.2))
    base = Image.alpha_composite(base, ruas)

    # 5 — skyline: faixa distante (topo) e faixa proxima (fundo)
    longe = _faixa_cidade(w, h, y_base=int(h * 0.255), escala=0.62,
                          densidade=0.80, seed=seed + 1, alt_max=78)
    longe = longe.filter(ImageFilter.GaussianBlur(1.6))
    base = Image.alpha_composite(base, longe)

    media = _faixa_cidade(w, h, y_base=int(h * 0.865), escala=0.95,
                          densidade=0.70, seed=seed + 2, alt_max=110)
    media = media.filter(ImageFilter.GaussianBlur(0.8))
    base = Image.alpha_composite(base, media)

    perto = _faixa_cidade(w, h, y_base=int(h * 0.995), escala=1.45,
                          densidade=0.62, seed=seed + 3, alt_max=128)
    base = Image.alpha_composite(base, perto)

    # 6 — rastos de entrega (as linhas que "correm" pelas ruas) com brilho
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    # colocados nas zonas que ficam a' vista (topo e rodape); o miolo fica calmo
    # porque e' onde assentam os cartoes.
    faixas = [(0.20, 0.30), (0.22, 0.32), (0.79, 0.88), (0.82, 0.92),
              (0.86, 0.96), (0.90, 0.99)]
    for idx, (fa, fb) in enumerate(faixas):
        cor = VERDE if idx % 2 == 0 else LARANJA
        x0 = rng.uniform(-w * 0.05, w * 0.75)
        y0 = rng.uniform(h * fa, h * fb)
        comp = rng.uniform(w * 0.14, w * 0.30)
        sinal = 1 if rng.random() < 0.5 else -1
        pts = []
        for t in range(0, 26):
            u = t / 25.0
            # segue a inclinacao das ruas isometricas (~0.62)
            pts.append((x0 + comp * u, y0 + sinal * comp * u * 0.62
                        + math.sin(u * 2.4) * 4))
        _rasto(dg, pts, cor + (165,), 5)
        # o "veiculo": ponto brilhante na ponta do rasto
        px, py = pts[-1]
        dg.ellipse([px - 8, py - 8, px + 8, py + 8], fill=cor + (230,))
    glow_b = glow.filter(ImageFilter.GaussianBlur(9))
    base = Image.alpha_composite(base, glow_b)
    base = Image.alpha_composite(base, glow.filter(ImageFilter.GaussianBlur(1.4)))

    # 7 — particulas
    part = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dp = ImageDraw.Draw(part)
    for _ in range(190):
        px, py = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(1.0, 3.4)
        cor = VERDE if rng.random() < 0.5 else LARANJA
        cor = _lerp(cor, (255, 250, 235), rng.uniform(0.25, 0.75))
        dp.ellipse([px - r, py - r, px + r, py + r], fill=cor + (rng.randrange(70, 190),))
    base = Image.alpha_composite(base, part.filter(ImageFilter.GaussianBlur(1.0)))

    # 8 — vinheta
    vin = Image.new("L", (w, h), 0)
    dv = ImageDraw.Draw(vin)
    for i in range(34):
        t = i / 34.0
        m = int(w * 0.10 * t), int(h * 0.07 * t)
        dv.rectangle([m[0], m[1], w - m[0], h - m[1]], outline=int(96 * (1 - t) ** 1.5),
                     width=max(2, int(w * 0.012)))
    vin = vin.filter(ImageFilter.GaussianBlur(w * 0.035))
    base = Image.composite(Image.new("RGBA", (w, h), (6, 14, 26, 255)), base, vin)

    return base.convert("RGB").resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    im = gerar_fundo(2480, 3508)
    im.save("assets/fundo_script.png")
    print("fundo gerado:", im.size)

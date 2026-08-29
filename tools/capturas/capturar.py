#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capturas para o portfólio — imagens reais dos sites, não mockups.

Tira a fotografia do topo de cada site (1440×900, que é o que uma pessoa vê
quando abre), reduz para 1200 de largura e grava em WebP. Sai leve o
suficiente para a página do portfólio não rebentar o orçamento de LCP.

PORQUÊ O TOPO E NÃO A PÁGINA INTEIRA
Uma captura de página inteira de um site com dez secções fica com 8000 píxeis
de altura e lê-se como uma tira ilegível no cartão do portfólio. O que vende é
o primeiro ecrã — é esse que se mostra.

SITES ATRÁS DE PORTÃO
O do Guarda FC responde 401. Captura-se o ficheiro local, e na página do
portfólio mostra-se a imagem SEM link — que é o que a ordem manda.

USO
    python capturar.py                 # a lista que está aqui em baixo
    python capturar.py <url> <nome>    # um só
"""
from __future__ import annotations

import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
DESTINO = RAIZ / "assets/img/trabalhos"

LARGURA_CAPTURA = 1440
ALTURA_CAPTURA = 900
LARGURA_FINAL = 1200
QUALIDADE = 72

# nome, alvo, legenda para o alt
TRABALHOS = [
    ("guarda-fc",
     (RAIZ.parent / "projetosflutter/guarda-fc-site/index.html").as_uri(),
     "Site do Guarda Futebol Clube"),
    ("jai",
     "https://jaiagarwala.com/",
     "Site pessoal de Jai Agarwal"),
    ("ouro-e-prata",
     "https://ouroeprata.boraguarda.com/",
     "Site da Barbearia Ouro e Prata"),
    ("sabores-de-casa",
     "https://boraguarda.com/loja/sabores-de-casa-acai",
     "Pagina do Sabores de Casa Acai no Bora"),
    ("goola",
     "https://goola.boraguarda.com/",
     "Site da Goola Acai"),
    ("mr-kebab",
     "https://mrkebab.boraguarda.com/",
     "Site do Mr Kebab and Restaurant"),
    ("sabores-do-brasil",
     "https://saboresdobrasil.boraguarda.com/",
     "Site do Sabores do Brasil, de Keli Barbosa"),
]


def abrir_navegador(pw):
    """O Chrome que já está instalado primeiro. Num PC de 4 GB não se
    descarregam 150 MB de browser só para tirar fotografias."""
    for etiqueta, opcoes in [("Chrome instalado", dict(channel="chrome")),
                             ("Edge instalado", dict(channel="msedge")),
                             ("Chromium do playwright", dict())]:
        try:
            nav = pw.chromium.launch(**opcoes)
            print("browser:", etiqueta)
            return nav
        except Exception:
            continue
    sys.exit("Nenhum browser arrancou. python -m playwright install chromium")


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Falta o playwright: pip install playwright")
    from PIL import Image

    lista = TRABALHOS
    if len(sys.argv) == 3:
        lista = [(sys.argv[2], sys.argv[1], sys.argv[2])]

    DESTINO.mkdir(parents=True, exist_ok=True)
    feitos, falhados = [], []

    with sync_playwright() as pw:
        nav = abrir_navegador(pw)
        ctx = nav.new_context(
            viewport={"width": LARGURA_CAPTURA, "height": ALTURA_CAPTURA},
            device_scale_factor=1,
        )
        for nome, alvo, _alt in lista:
            bruto = DESTINO / (nome + ".png")
            final = DESTINO / (nome + ".webp")
            try:
                pag = ctx.new_page()
                pag.goto(alvo, wait_until="load", timeout=60000)
                try:
                    pag.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass
                pag.wait_for_timeout(2500)          # deixa o movimento assentar
                pag.screenshot(path=str(bruto))     # só o primeiro ecrã
                pag.close()

                with Image.open(bruto) as im:
                    im = im.convert("RGB")
                    alt = round(im.height * LARGURA_FINAL / im.width)
                    im = im.resize((LARGURA_FINAL, alt), Image.LANCZOS)
                    im.save(final, "WEBP", quality=QUALIDADE, method=6)
                bruto.unlink()

                kb = final.stat().st_size // 1024
                print("  %-20s %s  %d KB  (%dx%d)" % (nome, "OK", kb, LARGURA_FINAL, alt))
                feitos.append(nome)
            except Exception as e:
                print("  %-20s FALHOU: %s" % (nome, str(e).splitlines()[0]))
                falhados.append(nome)
        nav.close()

    print("\n%d feitas, %d falhadas." % (len(feitos), len(falhados)))
    if falhados:
        print("Falhadas:", ", ".join(falhados))
    return 1 if falhados else 0


if __name__ == "__main__":
    sys.exit(main())

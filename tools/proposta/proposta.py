#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gerador de proposta em PDF.

PORQUE E QUE ISTO EXISTE
A proposta em PDF é o que separa quem cobra quinhentos de quem cobra vários
milhares. Mandar um preço solto por mensagem baixa o valor do trabalho: o
cliente compara com o preço do primo que "também mexe em sites" e a conversa
acaba ali. Um documento com capa, o problema dele escrito, o que está e o que
não está incluído, prazo e condições, muda quem está a falar.

O QUE ISTO NAO FAZ
Não inventa o preço. O preço é decisão do Danilo e entra como campo. Se vier
vazio, sai "a combinar" e o programa avisa — nunca põe um número por si.

Também não promete resultados. Nada de "aumento de 300% nas vendas". Uma
promessa dessas afasta o cliente sério, e o cliente sério é o que paga.

USO
    python proposta.py exemplo.json
    python proposta.py cliente.json --saida ../../saida/proposta-cliente.pdf

O ficheiro de entrada é JSON. Corre `python proposta.py --modelo` para ver
um em branco com todos os campos e o que cada um quer dizer.

COMO SAI O PDF
Pelo Chrome que já está instalado, através do playwright. Isso dá controlo
tipográfico a sério (a mesma folha de estilos do site) sem instalar biblioteca
de PDF nenhuma.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import html
import json
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent

NIVEIS = {
    1: "Nível 1 · Essencial",
    2: "Nível 2 · Profissional",
    3: "Nível 3 · Prémio",
    4: "Nível 4 · Sistema",
}

MANUTENCAO_POR_OMISSAO = [
    "Alojamento e domínio a funcionar, com o certificado sempre válido",
    "Cópia de segurança e reposição se alguma coisa correr mal",
    "Alterações pequenas de texto, preço ou fotografia",
    "Actualização do que fica velho no site",
    "Resposta a avarias no próprio dia útil",
]

MODELO_VAZIO = {
    "cliente": "Nome do negócio ou da pessoa",
    "titulo": "O título da proposta, em uma linha curta",
    "resumo": "Uma frase a dizer o que se propõe. Vai na capa.",
    "problema": [
        "Um parágrafo por linha desta lista. O problema REAL que se encontrou,",
        "escrito nas palavras dele e não em jargão."
    ],
    "custo": "O que este problema custa na prática. Sem números inventados.",
    "nivel": 2,
    "proposta": [
        "Um parágrafo por linha. O que vai ser construído."
    ],
    "incluido": ["Cada coisa que está incluída, uma por linha"],
    "excluido": ["Cada coisa que NÃO está incluída, uma por linha"],
    "prazo": "3 semanas",
    "preco": "",
    "manutencao": "",
    "manutencao_inclui": [],
    "validade_dias": 30,
}


def e(t):
    return html.escape(str(t or ""), quote=True)


def paragrafos(v):
    if isinstance(v, str):
        v = [x for x in v.split("\n") if x.strip()]
    return "".join("<p>%s</p>" % e(x) for x in (v or []))


def itens(v):
    return "".join("<li>%s</li>" % e(x) for x in (v or []))


def logo_embutido():
    """O logotipo vai em base64: um PDF não vai buscar ficheiros ao disco."""
    p = RAIZ / "assets/img/bora_logo.png"
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def montar(d, hoje):
    avisos = []

    preco = (d.get("preco") or "").strip()
    if not preco:
        preco = "a combinar"
        avisos.append(
            "SEM PRECO: o campo 'preco' veio vazio e saiu 'a combinar'. "
            "O preco e decisao do Danilo — este programa nunca o inventa."
        )

    manut = (d.get("manutencao") or "").strip()
    if not manut:
        manut = "a combinar"
        avisos.append("SEM MANUTENCAO: o campo 'manutencao' veio vazio.")

    nivel = int(d.get("nivel") or 2)
    if nivel not in NIVEIS:
        avisos.append("NIVEL desconhecido (%s); usei o 2." % nivel)
        nivel = 2

    dias = int(d.get("validade_dias") or 30)
    validade = (hoje + datetime.timedelta(days=dias)).strftime("%d/%m/%Y")

    campos = {
        "CLIENTE": e(d.get("cliente", "")),
        "TITULO": e(d.get("titulo", "")),
        "RESUMO": e(d.get("resumo", "")),
        "PROBLEMA": paragrafos(d.get("problema")),
        "CUSTO": paragrafos(d.get("custo")),
        "NIVEL_ROTULO": e(NIVEIS[nivel]),
        "PROPOSTA": paragrafos(d.get("proposta")),
        "INCLUIDO": itens(d.get("incluido")),
        "EXCLUIDO": itens(d.get("excluido")),
        "PRAZO": e(d.get("prazo", "a combinar")),
        "PRECO": e(preco),
        "MANUTENCAO": e(manut),
        "MANUTENCAO_INCLUI": itens(d.get("manutencao_inclui") or MANUTENCAO_POR_OMISSAO),
        "VALIDADE": e(validade),
        "DATA": hoje.strftime("%d/%m/%Y"),
        "EMAIL": "boraappbora@gmail.com",
        "TELEFONE": "+351 937 501 673",
        "LOGO": logo_embutido(),
    }

    for obrigatorio in ("cliente", "titulo", "problema", "proposta"):
        if not d.get(obrigatorio):
            avisos.append("EM FALTA: o campo '%s' veio vazio." % obrigatorio)

    modelo = (AQUI / "modelo.html").read_text(encoding="utf-8")
    for k, v in campos.items():
        modelo = modelo.replace("{{%s}}" % k, v)

    sobrou = re.findall(r"\{\{([A-Z_]+)\}\}", modelo)
    if sobrou:
        avisos.append("Campos do modelo por preencher: " + ", ".join(sorted(set(sobrou))))

    return modelo, avisos


def escrever_pdf(html_txt, destino):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Falta o playwright: pip install playwright")

    tmp = destino.with_suffix(".tmp.html")
    tmp.write_text(html_txt, encoding="utf-8")

    with sync_playwright() as pw:
        nav = None
        for opcoes in (dict(channel="chrome"), dict(channel="msedge"), dict()):
            try:
                nav = pw.chromium.launch(**opcoes)
                break
            except Exception:
                continue
        if nav is None:
            tmp.unlink(missing_ok=True)
            sys.exit("Nenhum browser arrancou. python -m playwright install chromium")

        pag = nav.new_page()
        pag.goto(tmp.as_uri(), wait_until="load")
        pag.wait_for_timeout(900)          # deixa a fonte assentar
        pag.pdf(path=str(destino), format="A4", print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        nav.close()

    tmp.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description="Proposta em PDF, com a identidade do Danilo.")
    ap.add_argument("entrada", nargs="?", help="ficheiro JSON com os dados")
    ap.add_argument("--saida", default=None, help="caminho do PDF (por omissão saida/)")
    ap.add_argument("--modelo", action="store_true", help="escreve um JSON em branco e sai")
    args = ap.parse_args()

    if args.modelo:
        print(json.dumps(MODELO_VAZIO, ensure_ascii=False, indent=2))
        return 0
    if not args.entrada:
        ap.error("falta o ficheiro JSON (ou usa --modelo)")

    d = json.loads(pathlib.Path(args.entrada).read_text(encoding="utf-8"))
    hoje = datetime.date.today()

    html_txt, avisos = montar(d, hoje)

    if args.saida:
        destino = pathlib.Path(args.saida)
    else:
        alcunha = re.sub(r"[^a-z0-9]+", "-", str(d.get("cliente", "cliente")).lower()).strip("-")
        destino = AQUI / "saida" / ("proposta-%s-%s.pdf" % (alcunha, hoje.isoformat()))
    destino.parent.mkdir(parents=True, exist_ok=True)

    escrever_pdf(html_txt, destino)

    kb = destino.stat().st_size // 1024
    print("PDF escrito: %s  (%d KB)" % (destino, kb))
    if avisos:
        print("\nAVISOS — ler antes de enviar:")
        for a in avisos:
            print("  - " + a)
        return 2
    print("Sem avisos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

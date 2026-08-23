#!/usr/bin/env python3
"""Percorre o site publicado e testa TODOS os links, um a um.

Segue os links internos em profundidade a partir da home e reporta:
  - o estado de cada URL interno (com a cadeia de redireccionamentos)
  - os links externos, testados uma vez cada
  - qualquer 404 ou erro

Uso: python verificar_links.py [base]
"""
import collections
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://bora-site.pages.dev").rstrip("/")
UA = {"User-Agent": "Mozilla/5.0 (verificador do bora-site)"}

# Domínios que bloqueiam robôs — testam-se, mas um 403 aqui não é link partido.
TOLERANTES = ("play.google.com", "instagram.com", "facebook.com", "wa.me")


def pedir(url, metodo="GET"):
    req = urllib.request.Request(url, headers=UA, method=metodo)
    saltos = []

    class Conta(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, rq, fp, code, msg, hdrs, novo):
            saltos.append(code)
            return super().redirect_request(rq, fp, code, msg, hdrs, novo)

    op = urllib.request.build_opener(Conta)
    try:
        with op.open(req, timeout=60) as r:
            corpo = r.read() if metodo == "GET" else b""
            return r.status, corpo.decode("utf-8", "replace"), saltos, r.geturl()
    except urllib.error.HTTPError as ex:
        return ex.code, "", saltos, url
    except Exception as ex:
        return 0, str(ex), saltos, url


def links_de(html_txt, url_pagina):
    achados = set()
    for m in re.finditer(r'(?:href|src)="([^"#][^"]*)"', html_txt):
        alvo = m.group(1).strip()
        if alvo.startswith(("mailto:", "tel:", "data:", "javascript:")):
            continue
        achados.add(urllib.parse.urljoin(url_pagina, alvo))
    return achados


def main():
    por_ver = collections.deque([BASE + "/"])
    vistos, externos = {}, {}
    origem = {BASE + "/": "(raiz)"}

    while por_ver:
        url = por_ver.popleft()
        if url in vistos:
            continue
        estado, corpo, saltos, final = pedir(url)
        vistos[url] = (estado, saltos, final)
        if estado == 200 and "<html" in corpo.lower():
            for alvo in links_de(corpo, url):
                if alvo.startswith(BASE):
                    if alvo not in vistos and alvo not in por_ver:
                        origem.setdefault(alvo, url)
                        por_ver.append(alvo)
                else:
                    externos.setdefault(alvo, url)

    print("=" * 74)
    print("INTERNOS — %d URLs" % len(vistos))
    print("=" * 74)
    maus = []
    for url in sorted(vistos):
        estado, saltos, final = vistos[url]
        cauda = ""
        if saltos:
            cauda = "  (%s → %s)" % ("+".join(str(s) for s in saltos),
                                     final.replace(BASE, ""))
        marca = "OK  " if estado == 200 else "FALHA"
        if estado != 200:
            maus.append((url, estado))
        print("  %s %-52s %s%s" % (marca, url.replace(BASE, "") or "/", estado, cauda))

    print()
    print("=" * 74)
    print("EXTERNOS — %d URLs" % len(externos))
    print("=" * 74)
    for url in sorted(externos):
        estado, _, _, _ = pedir(url, "HEAD")
        if estado in (403, 405, 0):
            estado2, _, _, _ = pedir(url)
            estado = estado2 or estado
        tolerante = any(d in url for d in TOLERANTES)
        ok = estado == 200 or (tolerante and estado in (403, 429))
        if not ok:
            maus.append((url, estado))
        print("  %s %-58s %s" % ("OK  " if ok else "FALHA", url[:58], estado))

    print()
    print("=" * 74)
    if maus:
        print("%d LINK(S) COM PROBLEMA:" % len(maus))
        for url, estado in maus:
            print("  %s  <- %s" % (url, origem.get(url, "externo")))
        sys.exit(1)
    print("TODOS OS LINKS RESPONDEM. Nenhum 404.")


if __name__ == "__main__":
    main()

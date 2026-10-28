"""Prova dos botões de descarregar do bora-site em 3 aparelhos (15/10/2026).

Abre a página inicial e duas páginas de categoria no endereço dado, em iPhone 15
(WebKit), Pixel 7 (Chromium) e computador (Chromium 1366 px), carrega em CADA botão
de descarregar que se vê e regista para onde foi parar. Guarda capturas e um
resultado.json na pasta de saída. Sai 1 se algum destino estiver errado.

Certo é:
  iPhone     -> apps.apple.com/.../id6809954739
  Android    -> play.google.com/...id=pt.boraapp.bora
  computador -> página /baixar com as duas lojas à vista (ou a loja do selo, se
                o botão for o selo explícito de uma loja)

O user-agent leva "BoraProva-headless" no fim: a função registar_visita_baixar
ignora user-agents com "headless", por isso estas visitas de teste NÃO entram na
contagem de origens (link_clicks). A escolha da loja é feita pela palavra
iPhone/Android, que continua lá.

Uso:
    python provar_botoes_lojas.py https://boraguarda.com <pasta-de-saida>
"""
import json
import os
import sys

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://boraguarda.com"
SAIDA = sys.argv[2] if len(sys.argv) > 2 else "saida-provas"
os.makedirs(SAIDA, exist_ok=True)

APPSTORE = "apps.apple.com/pt/app/bora-entregas-e-servicos/id6809954739"
PLAY = "play.google.com/store/apps/details?id=pt.boraapp.bora"

PAGINAS = [("inicio", "/"), ("entregas", "/entregas"), ("viagens", "/viagens")]

# Os botões de descarregar: o que manda para /baixar e os selos explícitos das lojas.
SELETOR = ('a[href*="/baixar"], a[href*="play.google.com"], a[href*="apps.apple.com"]')


def aparelhos(p):
    return [
        ("iphone15", p.webkit, dict(p.devices["iPhone 15"]), "ios"),
        ("pixel7", p.chromium, dict(p.devices["Pixel 7"]), "android"),
        ("computador", p.chromium, dict(p.devices["Desktop Chrome"],
                                         viewport={"width": 1366, "height": 800}), "outro"),
    ]


def esperado(plat, href):
    """Para onde este botão TEM de levar, neste aparelho."""
    if "apps.apple.com" in href:
        return "appstore"
    if "play.google.com" in href:
        return "play"
    return {"ios": "appstore", "android": "play", "outro": "pagina-baixar"}[plat]


def classificar(url):
    if APPSTORE in url:
        return "appstore"
    if PLAY in url:
        return "play"
    if "/baixar" in url:
        return "pagina-baixar"
    return "outro: " + url[:80]


def botoes_visiveis(page):
    out = []
    loc = page.locator(SELETOR)
    for i in range(loc.count()):
        a = loc.nth(i)
        try:
            if not a.is_visible():
                continue
            box = a.bounding_box()
            if not box or box["width"] < 4 or box["height"] < 4:
                continue
            # fora do ecrã na horizontal = gaveta do menu fechada: não se vê
            largura = page.viewport_size["width"]
            if box["x"] >= largura or box["x"] + box["width"] <= 0:
                continue
        except Exception:
            continue
        txt = " ".join((a.inner_text() or a.get_attribute("aria-label") or "").split())
        if not txt:
            txt = a.get_attribute("aria-label") or "(imagem)"
        out.append({"i": i, "href": a.get_attribute("href"), "texto": txt[:60]})
    return out


def clicar(ctx, base_url, i, nome_img):
    """Abre a página de novo, carrega no i-ésimo botão e devolve o destino.

    O destino lê-se da CADEIA de navegação (todas as abas): no iPhone o WebKit
    chega a apps.apple.com e passa logo para itms-appss:// (abrir a app App Store),
    que um navegador de teste não tem — a aba volta para trás, mas o destino foi
    a App Store, e é isso que conta."""
    page = ctx.new_page()
    page.goto(base_url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(800)
    cadeia = []

    def ouvir(r):
        try:
            if r.is_navigation_request():
                cadeia.append(r.url)
        except Exception:
            pass

    ctx.on("request", ouvir)
    a = page.locator(SELETOR).nth(i)
    a.scroll_into_view_if_needed(timeout=8000)
    # As cenas de cinema (computador) estão empilhadas e só a activa está à frente:
    # desce-se como uma pessoa até o botão ser mesmo o que está por cima no ecrã.
    for _ in range(60):
        box = a.bounding_box()
        if box and page.evaluate(
                "([x, y, el]) => { const e = document.elementFromPoint(x, y);"
                " return !!e && el.contains(e); }",
                [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, a.element_handle()]):
            break
        page.evaluate("window.scrollBy(0, 250)")
        page.wait_for_timeout(200)
    alvo = page
    try:
        with ctx.expect_page(timeout=5000) as nova:
            a.click(timeout=8000)
        alvo = nova.value
    except PWTimeout:
        pass
    # espera a cadeia chegar a uma loja ou a página /baixar acabar de carregar
    for _ in range(60):
        if any(APPSTORE in u or PLAY in u for u in cadeia):
            break
        if "/baixar" in alvo.url and "?" in alvo.url:
            break
        alvo.wait_for_timeout(250)
    try:
        alvo.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception:
        pass
    alvo.wait_for_timeout(1500)
    ctx.remove_listener("request", ouvir)
    lojas = [u for u in cadeia if APPSTORE in u or PLAY in u]
    final = lojas[0] if lojas else alvo.url
    extra = {"aba_final": alvo.url}
    if "/baixar" in final:
        # computador: as duas lojas têm de estar à vista na página /baixar
        extra["appstore_visivel"] = alvo.locator('a[href*="apps.apple.com"]').first.is_visible()
        extra["play_visivel"] = alvo.locator('a[href*="play.google.com"]').first.is_visible()
    try:
        alvo.screenshot(path=os.path.join(SAIDA, nome_img), timeout=20000)
    except Exception as e:
        extra["erro_captura"] = str(e)[:80]
    for pg in ctx.pages:
        pg.close()
    return final, cadeia, extra


def main():
    resultado = {"base": BASE, "aparelhos": {}}
    falhas = 0
    with sync_playwright() as p:
        so = os.environ.get("APARELHOS")
        for nome, motor, dev, plat in aparelhos(p):
            if so and nome not in so.split(","):
                continue
            dev["user_agent"] = dev["user_agent"] + " BoraProva-headless"
            browser = motor.launch()
            ctx = browser.new_context(**dev, locale="pt-PT")
            r_ap = resultado["aparelhos"][nome] = {"plataforma": plat, "paginas": {}}
            for pnome, caminho in PAGINAS:
                url = BASE + caminho
                page = ctx.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(1200)
                r_pg = r_ap["paginas"][pnome] = {"url": url, "cliques": []}
                page.screenshot(path=os.path.join(SAIDA, f"{nome}-{pnome}-topo.png"))
                if pnome == "inicio":
                    r_pg["data_aparelho"] = page.evaluate(
                        "document.documentElement.getAttribute('data-aparelho')")
                    sec = page.locator("#download")
                    sec.scroll_into_view_if_needed()
                    page.wait_for_timeout(1500)
                    sec.screenshot(path=os.path.join(SAIDA, f"{nome}-inicio-descarrega.png"))
                    selos = []
                    for cls in ("selo-ios", "selo-android"):
                        b = page.locator(f"#download a.{cls} img").bounding_box()
                        selos.append({"selo": cls, "x": round(b["x"]), "y": round(b["y"]),
                                      "altura": round(b["height"]), "largura": round(b["width"])})
                    r_pg["selos"] = selos
                    r_pg["qr_src"] = page.locator("#download img[src*='qr-']").get_attribute("src")
                    r_pg["texto_brevemente"] = page.content().count("brevemente")
                botoes = botoes_visiveis(page)
                page.close()
                for k, b in enumerate(botoes):
                    esp = esperado(plat, b["href"] or "")
                    # nos telemóveis, o selo da OUTRA loja é explícito: não se testa
                    if plat != "outro" and esp != {"ios": "appstore", "android": "play"}[plat]:
                        r_pg["cliques"].append(dict(b, esperado=esp, nota="selo da outra loja — não testado"))
                        continue
                    img = f"{nome}-{pnome}-clique{k + 1}.png"
                    try:
                        final, cadeia, extra = clicar(ctx, url, b["i"], img)
                    except Exception as e:
                        final, cadeia, extra = "ERRO: " + str(e)[:120], [], {}
                    obtido = classificar(final)
                    ok = obtido == esp
                    if esp == "pagina-baixar":
                        ok = ok and extra.get("appstore_visivel") and extra.get("play_visivel")
                    if not ok:
                        falhas += 1
                    r_pg["cliques"].append(dict(b, esperado=esp, obtido=obtido, ok=bool(ok),
                                                destino=final, cadeia=cadeia[:6], captura=img,
                                                **extra))
                    print(f"{nome:10s} {pnome:9s} {b['texto'][:34]:34s} -> {obtido:14s} "
                          f"{'OK' if ok else 'FALHOU'}")
            browser.close()
    resultado["falhas"] = falhas
    with open(os.path.join(SAIDA, "resultado.json"), "w", encoding="utf-8") as fh:
        json.dump(resultado, fh, ensure_ascii=False, indent=1)
    print("falhas:", falhas)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()

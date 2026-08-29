#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fiscal visual — o crítico que mede em vez de opinar.

Porta para os sites o que o Bora Studio já provou na animação.

A REGRA QUE VEIO DE UM ERRO REAL E NÃO SE DISCUTE
-------------------------------------------------
O crítico compara CAPTURA contra CAPTURA da referência. Nunca captura contra
uma descrição escrita. Um crítico a quem se dá a ficha escrita recita a ficha e
aprova lixo — no meta-juiz do estúdio deu 2 em 12.

Por isso este programa NÃO julga estética. Faz duas coisas separadas:

  PARTE 1 — GEOMETRIA (determinística, aqui dentro)
      Enquadramento e espaçamento verificam-se por medida, não por modelo de
      visão. Isso já foi provado com precisão de 3 pontos percentuais.
      Sai uma lista de defeitos concretos, cada um COM A MEDIDA.

  PARTE 2 — A FOLHA DE COMPARAÇÃO (para o olho, humano ou modelo)
      Gera saida/<nome>/comparar.html com a captura do trabalho ao lado da
      captura da referência, à mesma largura. É ISTO que se dá a um crítico.
      Sem referências em referencias/, diz que não comparou — não finge.

USO
    python fiscal.py <url-ou-ficheiro> [--nome alcunha] [--ref pasta]
    python fiscal.py https://boraguarda.com/ --nome montra
    python fiscal.py ../../index.html --nome montra-local

SAÍDA
    tools/fiscal-visual/saida/<nome>/
        360.png 768.png 1440.png     capturas do trabalho
        relatorio.md                  defeitos com medida
        relatorio.json                o mesmo, para máquina
        comparar.html                 trabalho vs referência, lado a lado

Depende só de playwright (já instalado nesta máquina).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import urllib.parse

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI / "saida"

# As três larguras obrigatórias. 360 e não 375: é o Android barato, que é o
# que a maioria da Guarda tem na mão.
LARGURAS = [
    (360, 800, "telemovel"),
    (768, 1024, "tablet"),
    (1440, 900, "computador"),
]

# ---------------------------------------------------------------------------
# O que se mede dentro da página. Corre no browser, devolve números.
# Cada medida existe porque um defeito real já passou por não ser medido.
# ---------------------------------------------------------------------------
MEDIR_JS = r"""
() => {
  const vw = window.innerWidth;
  const out = {
    vw, vh: window.innerHeight,
    scrollWidth: document.documentElement.scrollWidth,
    transbordo: [], alvos: [], letraPequena: [], semDimensao: [],
    esticadas: [], semAlt: [], contraste: [], espacos: {}, paleta: {},
    tipos: {}, h1: 0, titulo: '', metas: {}, ancoras: 0, ancorasVazias: 0,
  };

  out.h1 = document.querySelectorAll('h1').length;
  out.titulo = (document.title || '').trim();
  const m = n => { const e = document.querySelector(n); return e ? (e.content || e.href || '') : ''; };
  out.metas = {
    descricao: m('meta[name="description"]'),
    ogTitulo:  m('meta[property="og:title"]'),
    ogImagem:  m('meta[property="og:image"]'),
    canonico:  m('link[rel="canonical"]'),
    icone:     m('link[rel="icon"]') || m('link[rel="shortcut icon"]'),
    viewport:  m('meta[name="viewport"]'),
  };

  const visivel = el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity || '1') > 0.05;
  };
  const nome = el => {
    let t = el.tagName.toLowerCase();
    if (el.id) t += '#' + el.id;
    else if (el.className && typeof el.className === 'string') {
      const c = el.className.trim().split(/\s+/).slice(0, 2).join('.');
      if (c) t += '.' + c;
    }
    return t;
  };

  const todos = Array.from(document.body.querySelectorAll('*'));

  // ---- 1. transbordo horizontal: o defeito nº1 do telemóvel ----
  for (const el of todos) {
    if (!visivel(el)) continue;
    const r = el.getBoundingClientRect();
    // ignora quem está dentro de um contentor que rola de propósito
    let p = el.parentElement, dentroDeRolo = false;
    while (p && p !== document.body) {
      const s = getComputedStyle(p);
      if (s.overflowX === 'auto' || s.overflowX === 'scroll') { dentroDeRolo = true; break; }
      p = p.parentElement;
    }
    if (dentroDeRolo) continue;
    // Painel fora do ecra DE PROPOSITO (gaveta fechada): position:fixed com
    // transform a empurra-lo para fora, ou aria-hidden. Nao e defeito.
    let q = el, forade = false;
    while (q && q !== document.body) {
      const s = getComputedStyle(q);
      if ((s.position === 'fixed' || s.position === 'absolute') &&
          s.transform && s.transform !== 'none' &&
          /matrix\(1, 0, 0, 1, (-?\d{3,})/.test(s.transform)) { forade = true; break; }
      if (q.getAttribute && q.getAttribute('aria-hidden') === 'true') { forade = true; break; }
      q = q.parentElement;
    }
    if (forade) continue;
    const excesso = Math.round(r.right - vw);
    if (excesso > 2) out.transbordo.push({ el: nome(el), excesso, largura: Math.round(r.width) });
  }
  out.transbordo.sort((a, b) => b.excesso - a.excesso);
  out.transbordo = out.transbordo.slice(0, 12);

  // ---- 2. alvos de toque pequenos (só faz sentido no telemóvel) ----
  if (vw < 768) {
    for (const el of document.querySelectorAll('a,button,input,select,textarea,[role="button"]')) {
      if (!visivel(el)) continue;
      const r = el.getBoundingClientRect();
      // links dentro de um parágrafo não são alvos isolados
      const dentroDeTexto = el.tagName === 'A' && el.closest('p,li');
      if (dentroDeTexto) continue;
      if (r.width < 44 || r.height < 44) {
        out.alvos.push({ el: nome(el), l: Math.round(r.width), a: Math.round(r.height) });
      }
    }
    out.alvos = out.alvos.slice(0, 12);
  }

  // ---- 3. letra pequena de mais no telemóvel ----
  if (vw < 768) {
    for (const el of todos) {
      if (!visivel(el)) continue;
      const texto = Array.from(el.childNodes)
        .filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('');
      if (texto.length < 12) continue;
      const px = parseFloat(getComputedStyle(el).fontSize);
      if (px && px < 13) out.letraPequena.push({ el: nome(el), px: +px.toFixed(1) });
    }
    out.letraPequena = out.letraPequena.slice(0, 10);
  }

  // ---- 4/5. imagens: sem dimensão declarada (salta ao carregar) e esticadas ----
  for (const im of document.querySelectorAll('img')) {
    if (!visivel(im)) continue;
    const temDim = im.hasAttribute('width') && im.hasAttribute('height');
    const aspecto = getComputedStyle(im).aspectRatio;
    if (!temDim && (!aspecto || aspecto === 'auto')) {
      out.semDimensao.push({ src: (im.currentSrc || im.src || '').slice(-60) });
    }
    if (im.naturalWidth && im.naturalHeight) {
      const r = im.getBoundingClientRect();
      if (r.width > 8 && r.height > 8) {
        const fit = getComputedStyle(im).objectFit;
        if (fit === 'fill' || fit === 'none' || (!fit || fit === 'initial')) {
          const nat = im.naturalWidth / im.naturalHeight;
          const des = r.width / r.height;
          const desvio = Math.abs(des - nat) / nat;
          if (desvio > 0.05) {
            out.esticadas.push({
              src: (im.currentSrc || im.src || '').slice(-60),
              natural: +nat.toFixed(3), desenhado: +des.toFixed(3),
              desvioPct: +(desvio * 100).toFixed(1),
            });
          }
        }
      }
    }
    if (!im.hasAttribute('alt')) out.semAlt.push({ src: (im.currentSrc || im.src || '').slice(-60) });
  }
  out.semDimensao = out.semDimensao.slice(0, 10);
  out.esticadas   = out.esticadas.slice(0, 10);
  out.semAlt      = out.semAlt.slice(0, 10);

  // ---- 6. contraste do texto (WCAG AA: 4.5 normal, 3.0 grande) ----
  const lum = c => {
    const v = c.map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); });
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  };
  const rgb = s => { const m = (s || '').match(/\d+/g); return m ? m.slice(0, 3).map(Number) : null; };
  const fundoDe = el => {
    let p = el;
    while (p && p !== document.documentElement) {
      const s = getComputedStyle(p).backgroundColor;
      const c = rgb(s);
      const alfa = (s.match(/[\d.]+\)$/) || ['1'])[0];
      if (c && parseFloat(alfa) > 0.7) return c;
      p = p.parentElement;
    }
    return [0, 0, 0];
  };
  const vistos = new Set();
  for (const el of todos) {
    if (!visivel(el)) continue;
    const texto = Array.from(el.childNodes).filter(n => n.nodeType === 3)
      .map(n => n.textContent.trim()).join('');
    if (texto.length < 8) continue;
    // texto de recurso dentro de <video>/<audio>/<noscript> nunca chega a ver-se
    if (el.closest('video,audio,noscript')) continue;
    const s = getComputedStyle(el);
    const f = rgb(s.color); if (!f) continue;
    const b = fundoDe(el);
    const chave = f.join(',') + '|' + b.join(',');
    if (vistos.has(chave)) continue; vistos.add(chave);
    const L1 = lum(f), L2 = lum(b);
    const razao = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const px = parseFloat(s.fontSize), peso = parseInt(s.fontWeight, 10) || 400;
    const grande = px >= 24 || (px >= 18.66 && peso >= 700);
    const minimo = grande ? 3.0 : 4.5;
    if (razao < minimo) {
      out.contraste.push({
        el: nome(el), razao: +razao.toFixed(2), minimo,
        texto: texto.slice(0, 40), cor: s.color, fundo: 'rgb(' + b.join(',') + ')',
      });
    }
  }
  out.contraste = out.contraste.slice(0, 10);

  // ---- 7. régua de espaçamentos: quantos valores distintos há mesmo? ----
  const conta = {};
  for (const el of todos) {
    if (!visivel(el)) continue;
    const s = getComputedStyle(el);
    for (const p of ['paddingTop', 'paddingBottom', 'marginTop', 'marginBottom']) {
      const v = Math.round(parseFloat(s[p]) || 0);
      if (v > 0) conta[v] = (conta[v] || 0) + 1;
    }
  }
  out.espacos = Object.entries(conta).filter(([, n]) => n >= 2)
    .sort((a, b) => b[1] - a[1]).slice(0, 20)
    .reduce((o, [k, v]) => (o[k] = v, o), {});

  // ---- 8. paleta e tipografia: uma regra, ou o acaso? ----
  const cores = {}, tam = {};
  for (const el of todos) {
    if (!visivel(el)) continue;
    const s = getComputedStyle(el);
    const t = (el.textContent || '').trim();
    if (t.length > 3) {
      cores[s.color] = (cores[s.color] || 0) + 1;
      const px = Math.round(parseFloat(s.fontSize) || 0);
      if (px) tam[px] = (tam[px] || 0) + 1;
    }
  }
  out.paleta = Object.entries(cores).sort((a, b) => b[1] - a[1]).slice(0, 14)
    .reduce((o, [k, v]) => (o[k] = v, o), {});
  out.tipos = Object.entries(tam).sort((a, b) => b[1] - a[1]).slice(0, 16)
    .reduce((o, [k, v]) => (o[k] = v, o), {});

  // ---- 9. becos sem saída: links que não levam a lado nenhum ----
  for (const a of document.querySelectorAll('a')) {
    if (!visivel(a)) continue;
    out.ancoras++;
    const h = (a.getAttribute('href') || '').trim();
    if (!h || h === '#') out.ancorasVazias++;
  }

  return out;
}
"""


# ---------------------------------------------------------------------------
def medir(pagina, largura):
    """Corre o medidor e junta as métricas de desempenho do próprio browser."""
    dados = pagina.evaluate(MEDIR_JS)
    try:
        dados["desempenho"] = pagina.evaluate(
            """() => {
              const n = performance.getEntriesByType('navigation')[0] || {};
              const p = performance.getEntriesByType('paint') || [];
              const fcp = p.find(x => x.name === 'first-contentful-paint');
              return {
                fcp: fcp ? Math.round(fcp.startTime) : null,
                lcp: window.__lcp ? Math.round(window.__lcp) : null,
                cls: window.__cls != null ? +window.__cls.toFixed(4) : null,
                dom: n.domContentLoadedEventEnd ? Math.round(n.domContentLoadedEventEnd) : null,
              };
            }"""
        )
    except Exception:
        dados["desempenho"] = {}
    dados["largura"] = largura
    return dados


def abrir_navegador(pw):
    """Arranca um Chromium, pelo caminho que estiver disponível.

    Ordem de propósito: primeiro o Chrome que já está instalado na máquina
    (custa zero e não descarrega nada), depois o Chromium do playwright.
    Num PC de 4 GB não se puxam 150 MB de browser só para tirar três fotos.
    """
    tentativas = [
        ("Chrome instalado", dict(channel="chrome")),
        ("Edge instalado",   dict(channel="msedge")),
        ("Chromium do playwright", dict()),
    ]
    erros = []
    for etiqueta, opcoes in tentativas:
        try:
            nav = pw.chromium.launch(**opcoes)
            print(f"  browser: {etiqueta}")
            return nav
        except Exception as e:
            erros.append(f"{etiqueta}: {str(e).splitlines()[0]}")
    sys.exit("Nenhum browser arrancou.\n  " + "\n  ".join(erros) +
             "\n\nResolve com:  python -m playwright install chromium")


ESPIA_JS = """
window.__cls = 0;
try {
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp = e.startTime; })
    .observe({ type: 'largest-contentful-paint', buffered: true });
  new PerformanceObserver(l => {
    for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value;
  }).observe({ type: 'layout-shift', buffered: true });
} catch (e) {}
"""


# ---------------------------------------------------------------------------
def defeitos(m, rotulo):
    """Traduz medidas em defeitos concretos. Cada um leva a medida."""
    d = []
    L = m["largura"]

    if m["scrollWidth"] > m["vw"] + 2:
        d.append(("GRAVE", f"[{rotulo} {L}px] A página rola para o lado: "
                           f"{m['scrollWidth']}px de conteúdo para {m['vw']}px de ecrã "
                           f"({m['scrollWidth'] - m['vw']}px a mais)."))
    rola = m["scrollWidth"] > m["vw"] + 2
    for t in m["transbordo"][:5]:
        if rola:
            d.append(("GRAVE", f"[{rotulo} {L}px] {t['el']} sai {t['excesso']}px para fora "
                               f"do ecrã e faz a página rolar (mede {t['largura']}px)."))
        else:
            d.append(("MEDIO", f"[{rotulo} {L}px] {t['el']} passa {t['excesso']}px para fora "
                               f"do ecrã (mede {t['largura']}px). A página não rola, mas o "
                               f"conteúdo está cortado — confirma se é sangria de propósito."))
    for a in m["alvos"][:5]:
        d.append(("MEDIO", f"[{rotulo} {L}px] Alvo de toque pequeno: {a['el']} "
                           f"tem {a['l']}×{a['a']}px, o mínimo é 44×44."))
    for t in m["letraPequena"][:4]:
        d.append(("MEDIO", f"[{rotulo} {L}px] Letra a {t['px']}px em {t['el']} — "
                           f"abaixo de 13px não se lê no telemóvel."))
    for i in m["esticadas"][:4]:
        d.append(("GRAVE", f"[{rotulo} {L}px] Imagem esticada {i['desvioPct']}% fora de "
                           f"proporção (…{i['src']}). Falta object-fit: cover."))
    if m["semDimensao"]:
        d.append(("MEDIO", f"[{rotulo} {L}px] {len(m['semDimensao'])} imagens sem width/height "
                           f"declarados — a página salta ao carregar."))
    if m["semAlt"]:
        d.append(("MEDIO", f"[{rotulo} {L}px] {len(m['semAlt'])} imagens sem atributo alt."))
    for c in m["contraste"][:4]:
        d.append(("MEDIO", f"[{rotulo} {L}px] Contraste {c['razao']}:1 (mínimo {c['minimo']}) "
                           f"em {c['el']} — “{c['texto']}”, {c['cor']} sobre {c['fundo']}."))

    if len(m["espacos"]) > 10:
        d.append(("LEVE", f"[{rotulo} {L}px] {len(m['espacos'])} valores de espaçamento "
                          f"distintos. Uma régua tem 6 a 8 — acima disso é acaso."))
    if len(m["paleta"]) > 8:
        d.append(("LEVE", f"[{rotulo} {L}px] {len(m['paleta'])} cores de texto distintas. "
                          f"Uma paleta com regra tem 4 a 6."))
    if len(m["tipos"]) > 9:
        d.append(("LEVE", f"[{rotulo} {L}px] {len(m['tipos'])} tamanhos de letra distintos. "
                          f"Uma escala tipográfica tem 5 a 7."))

    if L == LARGURAS[-1][0]:   # coisas de página, medem-se uma vez só
        if m["h1"] == 0:
            d.append(("GRAVE", "Não há <h1> nenhum na página."))
        elif m["h1"] > 1:
            d.append(("MEDIO", f"Há {m['h1']} elementos <h1>. Deve haver um só."))
        mt = m["metas"]
        if not m["titulo"]:      d.append(("GRAVE", "Falta o <title>."))
        if not mt["descricao"]:  d.append(("MEDIO", "Falta a meta description."))
        if not mt["ogImagem"]:   d.append(("MEDIO", "Falta a og:image — é o que aparece no WhatsApp."))
        if not mt["canonico"]:   d.append(("LEVE",  "Falta o link canonical."))
        if not mt["icone"]:      d.append(("MEDIO", "Falta o favicon."))
        if not mt["viewport"]:   d.append(("GRAVE", "Falta a meta viewport — o site não é responsivo."))
        if m["ancorasVazias"]:
            d.append(("MEDIO", f"{m['ancorasVazias']} de {m['ancoras']} links não levam a lado "
                               f"nenhum (href vazio ou #). São becos sem saída."))
        p = m.get("desempenho") or {}
        if p.get("lcp") and p["lcp"] > 2500:
            d.append(("GRAVE", f"LCP a {p['lcp']}ms. O tecto é 2500ms."))
        if p.get("cls") is not None and p["cls"] > 0.1:
            d.append(("MEDIO", f"CLS de {p['cls']}. O tecto é 0.1 — a página salta ao carregar."))
    return d


# ---------------------------------------------------------------------------
def folha_comparacao(nome, refs, destino):
    """A folha que se dá ao crítico: captura CONTRA captura, nunca contra texto."""
    linhas = []
    for larg, _, rot in LARGURAS:
        par = [f'<figure><figcaption>Trabalho · {rot} · {larg}px</figcaption>'
               f'<img src="{larg}.png" alt="Captura do trabalho a {larg} pixéis"></figure>']
        for r in refs:
            rel = os.path.relpath(r, destino).replace("\\", "/")
            par.append(f'<figure><figcaption>Referência · {r.name}</figcaption>'
                       f'<img src="{rel}" alt="Captura da referência {r.name}"></figure>')
        linhas.append(f'<section><h2>{rot} — {larg}px</h2><div class="par">{"".join(par)}</div></section>')

    aviso = ("" if refs else
             '<p class="alerta"><b>Não há referências.</b> A pasta <code>referencias/</code> '
             'está vazia, por isso esta folha mostra só o trabalho. '
             '<b>Sem referência não houve comparação</b> — e um crítico a quem se dá a ficha '
             'escrita em vez da imagem recita a ficha e aprova lixo. Guarda 2 a 4 capturas '
             'da referência antes de pedir juízo.</p>')

    return f"""<!DOCTYPE html>
<html lang="pt-PT"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fiscal visual — {nome}</title>
<style>
 body{{background:#0B0F0D;color:#F4F7F5;font-family:Inter,system-ui,sans-serif;
      margin:0;padding:28px;line-height:1.6}}
 h1{{font-size:1.6rem;font-weight:900;letter-spacing:-.03em}}
 .nota{{color:#A9B5AE;max-width:70ch;margin:12px 0 26px}}
 .alerta{{background:rgba(249,115,22,.12);border:1px solid rgba(249,115,22,.4);
         border-radius:12px;padding:16px 18px;color:#f4d9c2;max-width:70ch}}
 section{{margin:40px 0;border-top:1px solid rgba(255,255,255,.1);padding-top:22px}}
 h2{{font-size:1.05rem;font-weight:800;color:#22C55E;margin-bottom:16px}}
 .par{{display:flex;gap:18px;overflow-x:auto;align-items:flex-start}}
 figure{{margin:0;flex:0 0 auto;max-width:46vw}}
 figcaption{{font-size:.8rem;color:#A9B5AE;margin-bottom:8px}}
 img{{max-width:100%;display:block;border:1px solid rgba(255,255,255,.14);border-radius:10px}}
 code{{background:#171F1B;border-radius:5px;padding:1px 5px}}
</style></head><body>
<h1>Fiscal visual — {nome}</h1>
<p class="nota">Captura contra captura. Compara-se o que se vê com o que se vê —
nunca com uma descrição escrita. As medidas exactas estão no
<code>relatorio.md</code>, ao lado deste ficheiro.</p>
{aviso}
{''.join(linhas)}
</body></html>
"""


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Fiscal visual — mede, não opina.")
    ap.add_argument("alvo", help="URL (https://…) ou caminho de um ficheiro .html")
    ap.add_argument("--nome", default=None, help="alcunha da pasta de saída")
    ap.add_argument("--ref", default=None, help="pasta com as capturas de referência")
    ap.add_argument("--espera", type=int, default=1800, help="ms de espera depois de carregar")
    args = ap.parse_args()

    alvo = args.alvo
    if not re.match(r"^https?://", alvo):
        p = pathlib.Path(alvo).resolve()
        if not p.exists():
            sys.exit(f"Não existe: {p}")
        alvo = p.as_uri()

    nome = args.nome or re.sub(r"[^a-z0-9]+", "-",
                               urllib.parse.urlparse(alvo).netloc.lower() or "local").strip("-") or "site"
    destino = SAIDA / nome
    destino.mkdir(parents=True, exist_ok=True)

    pasta_ref = pathlib.Path(args.ref) if args.ref else (AQUI.parent.parent / "referencias")
    refs = []
    if pasta_ref.exists():
        refs = sorted(x for x in pasta_ref.iterdir()
                      if x.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Falta o playwright:  pip install playwright && python -m playwright install chromium")

    todos, todos_defeitos = [], []
    with sync_playwright() as pw:
        nav = abrir_navegador(pw)
        for larg, alt, rot in LARGURAS:
            ctx = nav.new_context(viewport={"width": larg, "height": alt},
                                  device_scale_factor=1,
                                  is_mobile=(larg < 768), has_touch=(larg < 768))
            ctx.add_init_script(ESPIA_JS)
            pag = ctx.new_page()
            print(f"  {rot} {larg}px …", flush=True)
            pag.goto(alvo, wait_until="load", timeout=60000)
            try:
                pag.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            pag.wait_for_timeout(args.espera)
            m = medir(pag, larg)
            m["rotulo"] = rot
            todos.append(m)
            todos_defeitos += defeitos(m, rot)
            pag.screenshot(path=str(destino / f"{larg}.png"), full_page=True)
            ctx.close()
        nav.close()

    ordem = {"GRAVE": 0, "MEDIO": 1, "LEVE": 2}
    todos_defeitos.sort(key=lambda x: ordem[x[0]])

    (destino / "relatorio.json").write_text(json.dumps(
        {"alvo": alvo, "medidas": todos,
         "defeitos": [{"nivel": n, "texto": t} for n, t in todos_defeitos],
         "referencias": [r.name for r in refs]},
        ensure_ascii=False, indent=1), encoding="utf-8")

    graves = sum(1 for n, _ in todos_defeitos if n == "GRAVE")
    medios = sum(1 for n, _ in todos_defeitos if n == "MEDIO")
    leves = len(todos_defeitos) - graves - medios

    linhas = [f"# Fiscal visual — {nome}", "",
              f"Alvo: {alvo}", "",
              f"{graves} graves, {medios} médios, {leves} leves.", ""]
    if not todos_defeitos:
        linhas.append("Nenhum defeito de geometria encontrado nas três larguras.")
    for nivel in ("GRAVE", "MEDIO", "LEVE"):
        ns = [t for n, t in todos_defeitos if n == nivel]
        if ns:
            linhas += [f"## {nivel}", ""] + [f"- {t}" for t in ns] + [""]

    linhas += ["## O que isto NÃO julgou", "",
               "Geometria e medidas, só. Estética, hierarquia e se o site parece caro",
               "julgam-se na folha `comparar.html`, captura contra captura."]
    if not refs:
        linhas += ["", "**Não havia referências em `referencias/`, por isso não houve comparação",
                   "nenhuma.** Isto está dito de propósito: um relatório que cale este facto",
                   "faria passar por juízo aquilo que foi só medição."]
    else:
        linhas += ["", f"Referências usadas: {', '.join(r.name for r in refs)}."]

    (destino / "relatorio.md").write_text("\n".join(linhas), encoding="utf-8")
    (destino / "comparar.html").write_text(folha_comparacao(nome, refs, destino), encoding="utf-8")

    print()
    print("\n".join(linhas[:6]))
    print(f"\nSaída em {destino}")
    print(f"Folha de comparação: {destino / 'comparar.html'}")
    return 1 if graves else 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Le a ficha publica da Boom! Burger no Google Maps (sem conta, so leitura).

Tira: nota, numero de avaliacoes, horario por dia, telefone, morada, links
(site/redes) e o URL da ficha. Grava ../origem/google/ficha.json + captura.
"""
import json, os, re, sys, time
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'origem', 'google')
os.makedirs(SAIDA, exist_ok=True)
Q = 'Boom! Burger Hamburgueria Artesanal, R. Jardim dos Castelos Velhos, 6300-397 Guarda'

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(locale='pt-PT', viewport={'width': 1280, 'height': 900},
                        geolocation={'latitude': 40.5414484, 'longitude': -7.261693}, permissions=['geolocation'])
    pg = ctx.new_page()
    pg.goto('https://www.google.com/maps/search/' + Q.replace(' ', '+') + '?hl=pt-PT', timeout=60000)
    time.sleep(3)
    # consentimento europeu
    for txt in ['Rejeitar tudo', 'Reject all', 'Recusar tudo']:
        try:
            pg.get_by_role('button', name=txt).first.click(timeout=3000)
            break
        except Exception:
            pass
    time.sleep(6)
    # se caiu numa lista, abre o primeiro resultado
    if '/maps/place/' not in pg.url:
        try:
            pg.locator('a[href*="/maps/place/"]').first.click(timeout=8000)
            time.sleep(6)
        except Exception as e:
            print('sem resultado clicavel', e)
    # abrir a tabela do horario
    for sel in ['[aria-label*="Horário"]', '[aria-label*="horário"]', '[data-item-id="oh"]', 'button[aria-label*="Mostrar horário"]']:
        try:
            pg.locator(sel).first.click(timeout=3000)
            time.sleep(2)
            break
        except Exception:
            pass
    txt = pg.locator('[role="main"]').first.inner_text(timeout=15000)
    horas = []
    for row in pg.locator('table tr').all():
        try:
            horas.append(row.inner_text().replace('\n', ' | ').strip())
        except Exception:
            pass
    links = pg.eval_on_selector_all('a[href]', 'els => els.map(e => [e.getAttribute("aria-label")||e.innerText, e.href]).filter(x => /instagram|facebook|http/.test(x[1]) && !/google\\./.test(x[1]))')
    aria = pg.eval_on_selector_all('[aria-label]', 'els => els.map(e => e.getAttribute("aria-label")).filter(t => /estrela|avalia|Telefone|Morada|Endereço|Horário|segunda|domingo/i.test(t)).slice(0,60)')
    pg.screenshot(path=os.path.join(SAIDA, 'ficha-google.png'), full_page=False)
    ficha = {'url': pg.url, 'lido_em': time.strftime('%Y-%m-%d %H:%M'), 'texto_painel': txt[:3000],
             'horario_tabela': horas, 'links': links[:40], 'aria': aria}
    json.dump(ficha, open(os.path.join(SAIDA, 'ficha.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(pg.url)
    print('HORAS', horas)
    print('ARIA', [a for a in aria if re.search(r'estrela|avalia', a, re.I)][:6])
    print('LINKS', [l for l in links if re.search('instagram|facebook', l[1])][:6])
    print(txt[:1200])
    b.close()

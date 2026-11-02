# -*- coding: utf-8 -*-
"""2.a leitura do Google Maps: horario da semana inteira e numero de avaliacoes."""
import json, os, re, time
from playwright.sync_api import sync_playwright
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, '..', 'origem', 'google')
URL = json.load(open(os.path.join(SAIDA, 'ficha.json'), encoding='utf-8'))['url']
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(locale='pt-PT', viewport={'width': 1280, 'height': 900},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    pg = ctx.new_page()
    pg.goto(URL, timeout=60000); time.sleep(3)
    for txt in ['Rejeitar tudo', 'Reject all']:
        try: pg.get_by_role('button', name=txt).first.click(timeout=3000); break
        except Exception: pass
    time.sleep(6)
    try:
        pg.locator('[aria-label="Mostrar horário de funcionamento da semana"]').first.click(timeout=5000); time.sleep(2)
    except Exception as e: print('sem botao semana', str(e)[:80])
    rows = [r.inner_text().replace('\n', ' ').replace('\t', ' ') for r in pg.locator('table tr').all()]
    aria = pg.eval_on_selector_all('[aria-label]', 'els => els.map(e => e.getAttribute("aria-label")).filter(t => /avalia|crítica|review|feira|sábado|domingo/i.test(t))')
    html = pg.content()
    cont = re.findall(r'\((\d{2,4})\)', pg.locator('[role="main"]').first.inner_text())
    m = re.findall(r'(\d{2,4}) (?:críticas|avaliações|comentários)', html)
    out = {'rows': rows, 'aria': aria[:40], 'parenteses': cont[:10], 'n_criticas': m[:10]}
    json.dump(out, open(os.path.join(SAIDA, 'ficha-semana.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    pg.screenshot(path=os.path.join(SAIDA, 'ficha-google-semana.png'))
    b.close()
print(json.dumps(out, ensure_ascii=True)[:2500])

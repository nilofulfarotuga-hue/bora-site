# -*- coding: utf-8 -*-
"""Capturas das referencias (B.1) a 1440 e 390 px -> bora-site/referencias/boom-burger/.

So leitura de paginas publicas. Para cada uma: primeiro ecra + pagina inteira (limitada),
mais o texto dos botoes de pedir, para o prompt longo.
"""
import json, os, time
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..', '..'))
SAIDA = os.path.join(RAIZ, 'referencias', 'boom-burger')
os.makedirs(SAIDA, exist_ok=True)

REFS = [
    ('glovo-boomburger', 'https://glovoapp.com/pt/pt/guarda/stores/boom-burger-hamburgueria-artesanal-grd'),
    ('deleito', 'https://quierodeleito.com/'),
    ('thegoodburger-dgrees', 'https://dgrees.studio/works/the-good-burger/'),
    ('stack-contra', 'https://contra.com/p/sgF6BMkM-stack-burger-joint-website'),
    ('crav', 'https://cravburgers.shop/'),
]
VP = {'1440': {'width': 1440, 'height': 900}, '390': {'width': 390, 'height': 844}}
UA_M = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
notas = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for nome, url in REFS:
        for k, vp in VP.items():
            kw = dict(viewport=vp, locale='pt-PT')
            if k == '390':
                kw.update(user_agent=UA_M, is_mobile=True, has_touch=True, device_scale_factor=2)
            ctx = b.new_context(**kw)
            pg = ctx.new_page()
            try:
                pg.goto(url, timeout=60000, wait_until='domcontentloaded')
                time.sleep(7)
                for txt in ['Aceitar', 'Accept', 'Aceptar', 'Rejeitar tudo', 'Accept all', 'Aceptar todo', 'OK']:
                    try:
                        pg.get_by_role('button', name=txt).first.click(timeout=1200)
                        time.sleep(1)
                        break
                    except Exception:
                        pass
                pg.screenshot(path=os.path.join(SAIDA, f'{nome}-{k}-heroi.png'))
                # descer devagar para disparar animacoes e lazy-load, depois pagina inteira
                h = pg.evaluate('document.documentElement.scrollHeight')
                y = 0
                while y < min(h, 9000):
                    y += vp['height'] // 2
                    pg.evaluate(f'window.scrollTo(0,{y})')
                    time.sleep(0.5)
                pg.screenshot(path=os.path.join(SAIDA, f'{nome}-{k}-meio.png'))
                pg.evaluate('window.scrollTo(0,0)')
                time.sleep(1)
                pg.screenshot(path=os.path.join(SAIDA, f'{nome}-{k}-inteira.png'), full_page=True, timeout=30000)
                if k == '1440':
                    botoes = pg.eval_on_selector_all('a,button', 'els=>els.map(e=>(e.innerText||"").trim()).filter(t=>t&&t.length<40)')
                    notas[nome] = {'url': url, 'altura': h, 'botoes': sorted(set(botoes))[:80],
                                   'fontes': pg.evaluate('[...new Set([...document.querySelectorAll("h1,h2,h3,p,a,button")].slice(0,80).map(e=>getComputedStyle(e).fontFamily))]'),
                                   'titulo': pg.title()}
                print('ok', nome, k, h)
            except Exception as e:
                print('falhou', nome, k, str(e)[:150])
            ctx.close()
    b.close()
json.dump(notas, open(os.path.join(SAIDA, 'notas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

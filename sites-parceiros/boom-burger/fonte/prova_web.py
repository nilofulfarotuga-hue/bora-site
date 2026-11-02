# -*- coding: utf-8 -*-
"""A.4 — prova pela WEB (app.boraguarda.com), sem escrever nada no banco.

cliente  : /#/loja/boom-burger-guarda num telemovel (390x844) -> captura + texto da arvore
           de acessibilidade (tem de dizer "Em breve" e "Boom! Burger").
parceiro : entra com um link de acesso gerado pela Admin API (generate_link, nao envia
           email) e abre o painel -> captura + texto.
Capturas em bora-site/provas/boom-burger/ (publica, noindex) e textos em .json ao lado.
Uso: python prova_web.py [cliente|parceiro|ambos] [sufixo]
"""
import json, os, sys, time, urllib.request
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, '..', '..', '..'))
PROVAS = os.path.join(RAIZ, 'provas', 'boom-burger')
os.makedirs(PROVAS, exist_ok=True)
APP = 'https://app.boraguarda.com'
QUAL = sys.argv[1] if len(sys.argv) > 1 else 'ambos'
SUF = sys.argv[2] if len(sys.argv) > 2 else 'a4'
UA_M = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'


def semantica(pg):
    try:
        pg.evaluate("() => { const p = document.querySelector('flt-semantics-placeholder'); if (p) p.click(); }")
    except Exception:
        pass
    time.sleep(2)
    try:
        return pg.evaluate("() => [...document.querySelectorAll('flt-semantics, [aria-label], [role]')].map(e => (e.getAttribute('aria-label') || e.innerText || '').trim()).filter(t => t && t.length < 200)")
    except Exception as e:
        return ['erro: ' + str(e)[:100]]


def espera_flutter(pg, s=25):
    t0 = time.time()
    while time.time() - t0 < s:
        try:
            if pg.evaluate("() => !!document.querySelector('flt-glass-pane, flutter-view')"):
                break
        except Exception:
            pass
        time.sleep(1)
    time.sleep(8)


def cliente(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True,
                        has_touch=True, user_agent=UA_M, locale='pt-PT', service_workers='block')
    pg = ctx.new_page()
    pg.goto(f'{APP}/#/loja/boom-burger-guarda', timeout=90000)
    espera_flutter(pg, 40)
    pg.screenshot(path=os.path.join(PROVAS, f'{SUF}-cliente-loja-390.png'))
    txt = semantica(pg)
    pg.screenshot(path=os.path.join(PROVAS, f'{SUF}-cliente-loja-390-b.png'))
    ctx.close()
    return txt


def parceiro(b):
    env = dict(l.strip().split('=', 1) for l in open(r'C:\BoraLocal\projetosflutter\bora_app\backend\.env', encoding='utf-8') if '=' in l)
    url, sr = env['SUPABASE_URL'].rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
    req = urllib.request.Request(f'{url}/auth/v1/admin/generate_link', method='POST',
                                 data=json.dumps({'type': 'magiclink', 'email': 'boomburger@bora.app',
                                                  'redirect_to': APP + '/'}).encode(),
                                 headers={'apikey': sr, 'Authorization': f'Bearer {sr}', 'Content-Type': 'application/json'})
    link = json.loads(urllib.request.urlopen(req, timeout=60).read())
    acao = link.get('action_link') or link.get('properties', {}).get('action_link')
    ctx = b.new_context(viewport={'width': 1280, 'height': 860}, locale='pt-PT', service_workers='block')
    pg = ctx.new_page()
    pg.goto(acao, timeout=90000)
    espera_flutter(pg, 45)
    destino = pg.url.split('#')[0]
    pg.screenshot(path=os.path.join(PROVAS, f'{SUF}-parceiro-entrada-1280.png'))
    txt = semantica(pg)
    pg.screenshot(path=os.path.join(PROVAS, f'{SUF}-parceiro-entrada-1280-b.png'))
    # se pedir escolha de perfil, escolhe o de parceiro
    for nome in ['Sou Parceiro', 'Parceiro', 'Entrar como parceiro', 'Loja', 'Painel do parceiro']:
        try:
            pg.get_by_role('button', name=nome).first.click(timeout=2500)
            time.sleep(8)
            break
        except Exception:
            pass
    pg.screenshot(path=os.path.join(PROVAS, f'{SUF}-parceiro-painel-1280.png'))
    txt2 = semantica(pg)
    ctx.close()
    return {'url_depois_do_link': destino, 'texto_entrada': txt, 'texto_painel': txt2}


out = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    if QUAL in ('cliente', 'ambos'):
        out['cliente'] = cliente(b)
    if QUAL in ('parceiro', 'ambos'):
        out['parceiro'] = parceiro(b)
    b.close()
json.dump(out, open(os.path.join(PROVAS, f'{SUF}-texto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
c = out.get('cliente', [])
print('CLIENTE: em breve =', any('Em breve' in t for t in c), '| nome =', any('Boom' in t for t in c), '|', [t for t in c if t][:25])
if 'parceiro' in out:
    print('PARCEIRO url:', out['parceiro']['url_depois_do_link'])
    print('PARCEIRO entrada:', [t for t in out['parceiro']['texto_entrada'] if t][:25])
    print('PARCEIRO painel:', [t for t in out['parceiro']['texto_painel'] if t][:40])

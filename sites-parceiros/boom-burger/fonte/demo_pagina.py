# -*- coding: utf-8 -*-
"""Prova da pagina /demo/ (o "telemovel 1") num telemovel de 390x844:
  sem sessao -> mostra a entrada; com a sessao do Cliente Demonstracao (link de acesso da Admin API, posta no
  armazenamento do supabase-js como depois de um login) -> menu com precos da app -> Fazer o pedido ->
  segue o estado. Uso: python demo_pagina.py [url-base]   (por omissao a pre-visualizacao 'provas')
Capturas em bora-site/provas/boom-burger/demo-pagina-*.png. Imprime o pedido criado."""
import json, os, sys, time, urllib.request
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://provas.boom-burger-778.pages.dev'
AQUI = os.path.dirname(os.path.abspath(__file__))
PROVAS = os.path.abspath(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger'))
env = dict(l.strip().split('=', 1) for l in open(r'C:\BoraLocal\projetosflutter\bora_app\backend\.env', encoding='utf-8') if '=' in l)
URL, SR = env['SUPABASE_URL'].strip().rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
ANON = json.load(open(r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines', encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
UA_M = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'


def http(metodo, caminho, corpo=None, chave=ANON):
    req = urllib.request.Request(URL + caminho, method=metodo, headers={'apikey': chave, 'Authorization': f'Bearer {chave}',
                                 'Content-Type': 'application/json'}, data=json.dumps(corpo).encode() if corpo is not None else None)
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


l = http('POST', '/auth/v1/admin/generate_link', {'type': 'magiclink', 'email': 'demo.cliente.boomburger@bora.app'}, chave=SR)
sess = http('POST', '/auth/v1/verify', {'type': 'magiclink', 'token_hash': l.get('hashed_token') or l['properties']['hashed_token']})
sess.setdefault('expires_at', int(time.time()) + int(sess.get('expires_in', 3600)))
chave_ls = 'sb-' + URL.split('//')[1].split('.')[0] + '-auth-token'

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True,
                        user_agent=UA_M, locale='pt-PT')
    pg = ctx.new_page()
    erros = []
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)
    pg.goto(BASE + '/demo/', timeout=60000)
    pg.wait_for_selector('#bEntrar', timeout=30000)
    time.sleep(2)
    pg.screenshot(path=os.path.join(PROVAS, 'demo-pagina-1-entrada.png'), full_page=True)
    robots = pg.evaluate("() => document.querySelector('meta[name=robots]').content")
    print('entrada ok | robots:', robots, '| entrar visivel:', pg.is_visible('#entrar'))
    pg.evaluate("([k, v]) => localStorage.setItem(k, v)", [chave_ls, json.dumps(sess)])
    pg.reload()
    pg.wait_for_selector('#menu:not([hidden]) .item', timeout=30000)
    time.sleep(2)
    pg.screenshot(path=os.path.join(PROVAS, 'demo-pagina-2-menu.png'), full_page=True)
    itens = pg.eval_on_selector_all('#lista .item', "els => els.map(e => e.innerText.replace(/\\s+/g, ' ').trim())")
    print('menu:', itens, '| total:', pg.inner_text('#total'))
    pg.tap('#bPedir')
    pg.wait_for_function("() => !document.querySelector('#seguir').hidden || document.querySelector('#ePedir').innerText.trim()", timeout=30000)
    time.sleep(6)
    fechada = bool(pg.inner_text('#ePedir').strip())
    pg.screenshot(path=os.path.join(PROVAS, 'demo-pagina-3-' + ('fora-da-janela' if fechada else 'seguir') + '.png'), full_page=True)
    print('pedido:', pg.inner_text('#numero'), '| pin:', pg.inner_text('#pin'),
          '| passos feitos:', pg.eval_on_selector_all('.passo.feito', 'els => els.map(e => e.innerText)'), '| erro:', pg.inner_text('#ePedir'))
    print('consola (erros):', erros[:5])
    b.close()

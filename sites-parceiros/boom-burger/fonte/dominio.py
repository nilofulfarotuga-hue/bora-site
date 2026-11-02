# -*- coding: utf-8 -*-
"""Liga boomburger.boraguarda.com ao projeto Pages boom-burger (as duas metades, ver DOMINIOS.md):
custom domain no Pages (token Pages) + CNAME com proxy na zona boraguarda.com (token DNS).
Os tokens leem-se de bora-site/.env e nunca se imprimem. Idempotente: se ja existir, diz e segue."""
import json, os, urllib.request

ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '.env')
env = {}
for l in open(ENV, encoding='utf-8'):
    if '=' in l and not l.startswith('#'):
        k, v = l.strip().split('=', 1)
        env[k] = v.strip().strip('"')
ACC = '2cd0212b0f5e5c8284aa227f629c050a'
PROJ, NOME, ALVO = 'boom-burger', 'boomburger.boraguarda.com', 'boom-burger-778.pages.dev'


def api(metodo, caminho, token, corpo=None):
    req = urllib.request.Request('https://api.cloudflare.com/client/v4' + caminho, method=metodo,
                                 data=json.dumps(corpo).encode() if corpo else None,
                                 headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b'{}')


r = api('GET', f'/accounts/{ACC}/pages/projects/{PROJ}/domains', env['CLOUDFLARE_API_TOKEN'])
ja = [d for d in r.get('result') or [] if d.get('name') == NOME]
if not ja:
    r = api('POST', f'/accounts/{ACC}/pages/projects/{PROJ}/domains', env['CLOUDFLARE_API_TOKEN'], {'name': NOME})
    print('pages dominio:', r.get('success'), r.get('errors'), (r.get('result') or {}).get('status'))
else:
    print('pages dominio ja existia:', ja[0].get('status'))

z = api('GET', '/zones?name=boraguarda.com', env['CLOUDFLARE_DNS_TOKEN'])
zona = z['result'][0]['id']
rec = api('GET', f'/zones/{zona}/dns_records?name={NOME}', env['CLOUDFLARE_DNS_TOKEN'])
if rec.get('result'):
    x = rec['result'][0]
    print('dns ja existia:', x['type'], x['content'], 'proxy', x['proxied'])
else:
    r = api('POST', f'/zones/{zona}/dns_records', env['CLOUDFLARE_DNS_TOKEN'],
            {'type': 'CNAME', 'name': 'boomburger', 'content': ALVO, 'proxied': True,
             'comment': 'Site Boom! Burger (missao boom-burger-2026-10-27)'})
    x = r.get('result') or {}
    print('dns criado:', r.get('success'), r.get('errors'), x.get('name'), x.get('content'), x.get('proxied'))
r = api('GET', f'/accounts/{ACC}/pages/projects/{PROJ}/domains', env['CLOUDFLARE_API_TOKEN'])
print('estado agora:', [(d['name'], d['status'], (d.get('validation_data') or {}).get('status')) for d in r.get('result') or []])

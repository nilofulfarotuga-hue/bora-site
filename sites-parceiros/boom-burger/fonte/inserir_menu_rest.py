# -*- coding: utf-8 -*-
"""A.5 — insere o menu da Boom! Burger com os precos do dono (regra 5), pela API REST com a chave de servico.

Mesma regra do inserir_menu.py (que gera SQL), mas sem passar 50 KB de SQL pela conversa:
  partner_shelf_price = loja; price = round(loja / (1 - vis) * (1 + oculto), 2) com vis/oculto LIDOS de
  platform_settings; se partner_store_share(price) != loja ao centimo, tenta price -0,01 / +0,01.
  Opcoes: price_add com a mesma formula. Glovo so em product_price_sources (modo 'referencia').
Arredondamento igual ao Postgres numeric (metade para longe de zero). A PROVA final e o SQL verificar_menu.
Uso: python inserir_menu_rest.py [--ensaio]   (--ensaio calcula e mostra, nao escreve)
"""
import json, os, sys, urllib.request
from decimal import Decimal, ROUND_HALF_UP

AQUI = os.path.dirname(os.path.abspath(__file__))
ENSAIO = '--ensaio' in sys.argv
env = dict(l.strip().split('=', 1) for l in open(r'C:\BoraLocal\projetosflutter\bora_app\backend\.env', encoding='utf-8') if '=' in l)
URL, SR = env['SUPABASE_URL'].strip().rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
H = {'apikey': SR, 'Authorization': 'Bearer ' + SR, 'Content-Type': 'application/json'}
RID = 'boom-burger-guarda'
ST = URL + '/storage/v1/object/public/restaurant-assets/'
GLOVO = 'https://glovoapp.com/pt/pt/guarda/stores/boom-burger-hamburgueria-artesanal-grd'


def rest(metodo, caminho, corpo=None, extra=None):
    h = dict(H, **(extra or {}))
    req = urllib.request.Request(URL + '/rest/v1/' + caminho, method=metodo, headers=h,
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        r = urllib.request.urlopen(req, timeout=60)
        t = r.read()
        return r.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')[:400]


st, ps = rest('GET', 'platform_settings?key=in.(partner_visible_commission_pct,partner_hidden_markup_pct)&select=key,value')
cfg = {x['key']: Decimal(str(x['value'])) for x in ps}
VIS, OCU = cfg['partner_visible_commission_pct'], cfg['partner_hidden_markup_pct']
C = Decimal('0.01')
r2 = lambda x: x.quantize(C, rounding=ROUND_HALF_UP)
share = lambda p: r2(p * (1 - VIS) / (1 + OCU))   # igual a public.partner_store_share(p)


def preco_app(loja):
    loja = r2(Decimal(str(loja)))
    b = r2(loja / (1 - VIS) * (1 + OCU))
    for c in (b, b - C, b + C):
        if share(c) == loja:
            return float(c)
    raise SystemExit(f'sem preco exato para loja {loja}')


prep = json.load(open(os.path.join(AQUI, 'menu-preparacao.json'), encoding='utf-8'))
dono = json.load(open(os.path.join(AQUI, 'precos-dono.json'), encoding='utf-8'))
prods, grupos, itens, fontes = [], [], [], []
for p in prep['produtos']:
    loja = dono['produtos'][p['id']]
    foto = ST + p['foto_storage'] if p.get('foto_storage') else None
    prods.append({'id': p['id'], 'restaurant_id': RID, 'name': p['name'], 'description': p['description'] or None,
                  'category': p['category'], 'partner_shelf_price': loja, 'price': preco_app(loja), 'sort_order': p['sort_order'],
                  'is_popular': p['is_popular'], 'age_restricted': p['age_restricted'], 'photo_url': foto,
                  'image_source': p.get('foto_origem_final'), 'needs_photo': foto is None, 'is_available': True,
                  'source': 'dono_whatsapp_2026_10_27'})
    if p.get('preco_glovo_ref') is not None:
        fontes.append({'product_id': p['id'], 'restaurant_id': RID, 'fonte': 'glovo', 'preco': p['preco_glovo_ref'], 'url': GLOVO,
                       'modo': 'referencia', 'nome_na_fonte': p['name'], 'confianca': 1, 'duvidoso': False,
                       'apanhado_em': '2026-10-27T08:50:00+00:00'})
    for g in p['option_groups']:
        grupos.append({'id': g['id'], 'product_id': p['id'], 'name': g['name'], 'is_required': g['is_required'],
                       'min_choices': g['min_choices'], 'max_choices': g['max_choices'], 'sort_order': g['sort_order']})
        for it in g['items']:
            itens.append({'id': it['id'], 'group_id': g['id'], 'name': it['name'], 'price_add': preco_app(dono['opcoes'][it['name']]),
                          'is_available': True, 'sort_order': it['sort_order']})

ex = next(x for x in prods if x['id'] == 'boom-classico')
print(f'vis={VIS} oculto={OCU} | produtos {len(prods)} grupos {len(grupos)} opcoes {len(itens)} refs glovo {len(fontes)} '
      f'| exemplo Classico loja {ex["partner_shelf_price"]:.2f} -> app {ex["price"]:.2f}')
if ENSAIO:
    sys.exit(0)
for tab, linhas in (('products', prods), ('product_option_groups', grupos), ('product_option_items', itens),
                    ('product_price_sources', fontes)):
    st, r = rest('POST', tab, linhas, {'Prefer': 'return=minimal'})
    print(tab, st, '' if st in (200, 201, 204) else r)
    if st not in (200, 201, 204):
        raise SystemExit(1)

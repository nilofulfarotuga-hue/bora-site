# -*- coding: utf-8 -*-
"""Menu do site (B.7): nomes, textos e fotos do menu de preparacao + PRECOS DA APP.

Le os produtos da Boom! Burger na base com a chave PUBLICA (o mesmo que o site faz no
browser). Se houver produtos, o preco mostrado e products.price — o mesmo que o cliente ve
na app. Se ainda nao houver (precos do dono por chegar), preco = null e o site escreve
"Preco na app". Nunca se usa o preco da Glovo.

Saida: fonte/menu.json
"""
import json, os, urllib.request, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
DEF = r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines'
d = json.load(open(DEF, encoding='utf-8-sig'))
URL, ANON = d['SUPABASE_URL'], d['SUPABASE_ANON_KEY']
RID = 'boom-burger-guarda'

prep = json.load(open(os.path.join(AQUI, 'menu-preparacao.json'), encoding='utf-8'))
req = urllib.request.Request(
    f'{URL}/rest/v1/products?restaurant_id=eq.{RID}&select=id,name,description,price,is_available,category,sort_order',
    headers={'apikey': ANON, 'Authorization': f'Bearer {ANON}'})
vivos = {p['id']: p for p in json.loads(urllib.request.urlopen(req, timeout=30).read())}
print('produtos na base:', len(vivos))

cats, ordem = {}, []
for p in prep['produtos']:
    v = vivos.get(p['id'])
    if vivos and (v is None or v.get('is_available') is False):
        continue  # com a loja carregada, o site mostra so o que a app mostra
    c = p['category']
    if c not in cats:
        cats[c] = []
        ordem.append(c)
    cats[c].append({
        'id': p['id'],
        'nome': (v or {}).get('name') or p['name'],
        'desc': (v or {}).get('description') or p['description'],
        'preco': float(v['price']) if v and v.get('price') is not None else None,
        'popular': p['is_popular'],
        'alcool': p['age_restricted'],
        'foto': p['id'] if p.get('foto_storage') else None,
    })
IDS = {'Hambúrgueres': 'hamburgueres', 'Entradas': 'entradas', 'Menu Traquinas': 'traquinas',
       'Sobremesas': 'sobremesas', 'Bebidas e cervejas': 'bebidas', 'Acompanhamentos e molhos': 'acompanhamentos'}
menu = {
    'gerado_em': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    'com_precos': any(x['preco'] is not None for c in cats.values() for x in c),
    'categorias': [{'id': IDS.get(c, c.lower()), 'nome': c, 'produtos': cats[c]} for c in ordem],
}
json.dump(menu, open(os.path.join(AQUI, 'menu.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('categorias', [(c['nome'], len(c['produtos'])) for c in menu['categorias']], 'com_precos', menu['com_precos'])

# -*- coding: utf-8 -*-
"""Adendo 2 (27/10 15:30): lista de precos do dono (WhatsApp 14:47) -> menu-preparacao.json v2 + precos-dono.json.

Decisoes do adendo: nomes do dono em PT-PT corrigidos; "Smash" = Duplo Smash (nome "Boom! Smash", foto do
Duplo Smash, POR CONFIRMAR com o dono); Refrigerantes e sumos 2,30 = um produto por bebida; ficam FORA ate o
dono responder: Terra e Mar, The King Elvis, Heineken Zero, Super Bock Stout. Produtos novos sem foto (nao ha
nas 40 imagens do dono): 4 sobremesas, Agua das Pedras, Cerveja Letra A-F.
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(AQUI, 'menu-preparacao.json')
prep = json.load(open(P, encoding='utf-8'))
por_id = {p['id']: p for p in prep['produtos']}

# --- preco da LOJA por produto (o que o dono quer receber) ---
LOJA = {
    'boom-classico': 10.90, 'boom-bombastico': 12.90, 'boom-cheddar-lovers': 14.10, 'boom-brie-fan': 13.50,
    'boom-camone': 12.80, 'boom-chicken-breast': 12.50, 'boom-crispy-chicken': 14.00, 'boom-serra-da-estrela': 13.00,
    'boom-burguesinha': 15.00, 'boom-portobello': 15.20, 'boom-duplo-smash': 15.90, 'boom-kamikaze': 17.90,
    'boom-veggie-beyond': 13.50, 'boom-nuggets-de-frango': 10.00,
    'boom-bolo-do-caco-com-manteiga-de-alho': 3.80, 'boom-bolinhas-alheira-de-mirandela': 4.40,
    'boom-asas-de-frango-com-molho-bbq': 8.60, 'boom-batata-gulosa': 6.50, 'boom-cogumelos-frescos-salteados': 5.50,
    'boom-pimentos-padron-frescos': 5.30, 'boom-tequenhos-palitos-de-queijo': 5.30, 'boom-bites-crocantes-peito-de-frango': 6.00,
    'boom-dose-batata-artesanal': 2.75, 'boom-dose-batata-doce': 3.85, 'boom-molho-cheddar': 3.20,
    'boom-maionese-caseira-extra': 1.10, 'boom-maionese-caseira-malagueta-picante': 1.40,
    'boom-crumble-maca-c-caramelo-caseiro': 6.60, 'boom-cheesecake-frutos-vermelhos': 6.10,
    'boom-agua-alardo-0-33': 1.40, 'boom-franziskaner': 4.40, 'boom-desperados': 3.85, 'boom-super-bock-0-33': 2.10,
    'boom-bandida-pomar-maca-sidra': 2.90, 'boom-bandida-pomar-frutos-vermelhos-sidra': 2.90,
}
for rid in ('boom-coca-cola', 'boom-coca-cola-zero', 'boom-sprite', 'boom-fanta-laranja', 'boom-fanta-guarana',
            'boom-ice-tea-limao', 'boom-ice-tea-pessego', 'boom-ice-tea-manga', 'boom-compal-laranja', 'boom-compal-maca'):
    LOJA[rid] = 2.30
FORA = {'boom-terra-e-mar-hamburguer-mes-outubro': 'não veio na lista do dono (perguntado às 15:30)',
        'boom-the-king-elvis': 'não veio na lista do dono (perguntado às 15:30)',
        'boom-heineken-zero-alcool': 'não veio na lista do dono', 'boom-super-bock-stout': 'não veio na lista do dono'}

# --- nomes do dono / correcoes PT-PT ---
NOMES = {
    'boom-duplo-smash': 'Boom! Smash',
    'boom-bolinhas-alheira-de-mirandela': 'Bolinhas de alheira de Mirandela',
    'boom-asas-de-frango-com-molho-bbq': 'Asas de frango com molho BBQ',
    'boom-cogumelos-frescos-salteados': 'Cogumelos frescos salteados',
    'boom-pimentos-padron-frescos': 'Pimentos Padrón salteados',
    'boom-tequenhos-palitos-de-queijo': 'Palitos de queijo',
    'boom-bites-crocantes-peito-de-frango': 'Bites crocantes de peito de frango',
    'boom-crumble-maca-c-caramelo-caseiro': 'Tarte crumble de maçã e gelado',
    'boom-cheesecake-frutos-vermelhos': 'Cheesecake de frutos vermelhos',
    'boom-agua-alardo-0-33': 'Água 0,33 L',
    'boom-nuggets-de-frango': 'Nuggets de frango',
}
DESCR = {
    'boom-cheesecake-frutos-vermelhos': 'Cheesecake caseiro de frutos vermelhos.',
    'boom-crumble-maca-c-caramelo-caseiro': 'Tarte crumble de maçã, servida com gelado.',
    'boom-tequenhos-palitos-de-queijo': 'Palitos de queijo (tequeños) com massa mãe.',
    'boom-pimentos-padron-frescos': 'Pimentos Padrón salteados em brandy e especiarias.',
    'boom-agua-alardo-0-33': 'Água Alardo 0,33 L.',
}
NOVOS = [  # (id, nome, categoria, loja, idade, descricao)
    ('boom-bolo-chocolate-pistacho-gelado', 'Bolo de chocolate com creme de pistáchio e gelado', 'Sobremesas', 6.60, False, ''),
    ('boom-brownie-chocolate-nozes-gelado', 'Brownie de chocolate com nozes e gelado', 'Sobremesas', 6.60, False, ''),
    ('boom-cheesecake-caramelo-salgado', 'Cheesecake de caramelo salgado', 'Sobremesas', 6.10, False, ''),
    ('boom-palitos-de-nutella', 'Palitos de Nutella', 'Sobremesas', 6.60, False, ''),
    ('boom-agua-das-pedras', 'Água das Pedras', 'Bebidas e cervejas', 1.70, False, ''),
] + [(f'boom-cerveja-letra-{l.lower()}', f'Cerveja Letra {l}', 'Bebidas e cervejas', v, True, 'Cerveja artesanal Letra.')
     for l, v in (('A', 3.65), ('B', 3.85), ('C', 3.95), ('D', 3.95), ('E', 3.95), ('F', 3.95))]

# --- opcoes: preco da loja pelo nome; e as duas opcoes novas da lista ---
OPC = {'Ingrediente extra': 1.40, 'Trocar a batata por batata doce': 2.20, 'Pão brioche': 2.10, 'Bolo do caco': 2.10,
       'Pão sem glúten': 2.20, 'Veggie Beyond (proteína de ervilha)': 3.15, 'Peito de frango grelhado': 1.40,
       'Mais peito de frango grelhado': 2.75, 'Carne de novilho (160 g)': 3.40, 'Mais 160 g de carne de novilho': 5.30,
       'Maionese caseira extra': 1.10, 'Maionese de malagueta picante': 1.40}

produtos = []
for p in prep['produtos']:
    if p['id'] in FORA:
        continue
    p = dict(p)
    if p['id'] in NOMES:
        p['name'] = NOMES[p['id']]
    if p['id'] in DESCR:
        p['description'] = DESCR[p['id']]
    p['description'] = p['description'].replace('Cheescake', 'Cheesecake')
    if p['id'] == 'boom-duplo-smash':
        p['nota'] = 'POR CONFIRMAR: "Smash" da lista do dono = Duplo Smash da Glovo (perguntado às 15:30)'
    # opcoes novas nos hamburgueres
    for g in p['option_groups']:
        base = g['id']
        nomes = [i['name'] for i in g['items']]
        if g['name'] == 'Extras' and 'Mais peito de frango grelhado' not in nomes:
            g['items'].append({'id': f'{base}-mais-peito-de-frango-grelhado', 'name': 'Mais peito de frango grelhado',
                               'preco_loja': None, 'preco_glovo_ref': None, 'sort_order': len(g['items']) + 1})
        if g['name'] == 'Trocar a carne':
            d = p['description'].lower()
            base_novilho = 'novilho' in d.split('.')[0] and 'beyond' not in d and 'frango' not in d.split('.')[0]
            if not base_novilho and 'Carne de novilho (160 g)' not in nomes:
                g['items'].insert(0, {'id': f'{base}-carne-de-novilho-160-g', 'name': 'Carne de novilho (160 g)',
                                      'preco_loja': None, 'preco_glovo_ref': None, 'sort_order': 0})
            for k, it in enumerate(g['items'], 1):
                it['sort_order'] = k
    produtos.append(p)
ordem = max(p['sort_order'] for p in produtos)
for nid, nome, cat, loja, idade, desc in NOVOS:
    ordem += 1
    produtos.append({'id': nid, 'name': nome, 'description': desc, 'category': cat, 'sort_order': ordem, 'is_popular': False,
                     'age_restricted': idade, 'allergens': None, 'preco_loja': None, 'preco_glovo_ref': None, 'glovo_id': None,
                     'foto_origem': None, 'foto_nota': 'sem foto: não há nas 40 imagens do dono', 'option_groups': []})
    LOJA[nid] = loja
# ordem do menu por categoria (os novos ao pe dos irmaos)
CATS = ['Hambúrgueres', 'Entradas', 'Menu Traquinas', 'Sobremesas', 'Bebidas e cervejas', 'Acompanhamentos e molhos']
produtos.sort(key=lambda p: (CATS.index(p['category']), p['sort_order']))
for k, p in enumerate(produtos, 1):
    p['sort_order'] = k
    p['preco_loja'] = LOJA.get(p['id'])
prep['produtos'] = produtos
prep['estado'] = 'PRECOS DO DONO RECEBIDOS (WhatsApp 27/10 14:47, adendo 2)'
prep['excluidos'] = prep.get('excluidos', []) + [{'nome': por_id[k]['name'], 'motivo': v} for k, v in FORA.items()]
json.dump(prep, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

faltam = [p['name'] for p in produtos if p['preco_loja'] is None]
opc_falta = sorted({i['name'] for p in produtos for g in p['option_groups'] for i in g['items'] if i['name'] not in OPC})
dono = {'produtos': {p['id']: p['preco_loja'] for p in produtos}, 'opcoes': OPC, 'fora': []}
json.dump(dono, open(os.path.join(AQUI, 'precos-dono.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('produtos', len(produtos), '| sem preco:', faltam, '| opcoes sem preco:', opc_falta)
print('sem foto:', [p['name'] for p in produtos if not p.get('foto_storage')])
for c in CATS:
    print(' ', c, sum(1 for p in produtos if p['category'] == c))

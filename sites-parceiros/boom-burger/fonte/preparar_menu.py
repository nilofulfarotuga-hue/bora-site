# -*- coding: utf-8 -*-
"""Menu de PREPARACAO da Boom! Burger (bloco A.2), a partir do catalogo publico da Glovo.

Regra 5 da missao: os produtos SO entram na base com o preco do dono. Ate la vivem
aqui, em fonte/menu-preparacao.json, com preco_loja = null. O preco da Glovo fica so
como referencia (vai para product_price_sources com fonte 'glovo' quando o produto
existir) e NUNCA para products.price nem para o site.

Quando chegar a lista do dono: preencher preco_loja de cada produto e de cada opcao
(o preco que ele quer RECEBER) e correr fonte/inserir_menu.py.
"""
import json, os, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
GLOVO = os.path.join(AQUI, '..', 'origem', 'glovo', 'produtos.json')
SAIDA = os.path.join(AQUI, 'menu-preparacao.json')
RID = 'boom-burger-guarda'


def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'boom!?', '', t)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def limpa(t):
    return re.sub(r'\s+', ' ', (t or '')).strip()


g = json.load(open(GLOVO, encoding='utf-8'))
por_nome = {limpa(x['nome']): x for x in g}

# Categorias da app (ordem = ordem no menu). Os nomes da Glovo sao do proprio dono.
CAT = [
    ('Hambúrgueres', ['Mais vendidos', 'Hambúrgueres Artesanais']),
    ('Entradas', ['Entradas']),
    ('Menu Traquinas', ['Traquinas']),
    ('Sobremesas', ['Sobremesas']),
    ('Bebidas e cervejas', ['Bebidas']),
    ('Acompanhamentos e molhos', ['Extras']),
]
# Os "Com ..." e o "160gr carne" e o "Ingrediente extra" da Glovo sao modificadores de
# hamburguer: viram grupos de opcoes, nao produtos soltos.
MODIFICADORES = {
    'Com pão brioche': ('pao', 'Pão brioche'),
    'Com pão sem glúten': ('pao', 'Pão sem glúten'),
    'Com bolo do caco': ('pao', 'Bolo do caco'),
    'Com Peito Frango': ('carne', 'Peito de frango grelhado'),
    'Com Veggie Beyond': ('carne', 'Veggie Beyond (proteína de ervilha)'),
    '160gr carne novilho': ('extra', 'Mais 160 g de carne de novilho'),
    'Ingrediente extra': ('extra', 'Ingrediente extra'),
    'Maionese caseira extra': ('extra', 'Maionese caseira extra'),
    'Maionese caseira malagueta picante': ('extra', 'Maionese de malagueta picante'),
    'Com batata doce': ('batata', 'Trocar a batata por batata doce'),
}
# Continuam a existir tambem como produto solto (a Glovo vende-os assim): doses e molhos.
SOLTOS_TAMBEM = {'Maionese caseira extra', 'Maionese caseira malagueta picante'}
EXCLUIDOS = {
    'Embalagem de Utilização Única': 'taxa de embalagem da Glovo; no Bora o saco do restaurante ja e cobrado a parte (0,30 EUR fixo)',
    'Saco': 'idem: saco e regra do Bora, nao produto',
}
ALCOOL = {'Franziskaner', 'Desperados', 'Bandida Pomar Maçã Sidra', 'Bandida Pomar Frutos Vermelhos Sidra',
          'Super Bock Stout', 'Super Bock 0,33'}
FOTO_NAO_E_DELE = {'Ingrediente extra': 'parece foto de banco de imagens (legumes sobre tabua branca) - nao usar',
                   'Embalagem de Utilização Única': 'foto generica de embalagem - nao usar'}
NOMES = {  # so arrumacao de espacos/maiusculas; o texto e o do dono
    'Boom! Terra e Mar, Hamburguer mês Outubro': 'Boom! Terra e Mar',
    'Tequenhos Palitos de queijo': 'Tequeños — palitos de queijo',
    'Crumble Maçã c/ Caramelo caseiro': 'Crumble de maçã com caramelo caseiro',
    'Coca cola': 'Coca-Cola', 'Coca cola Zero': 'Coca-Cola Zero',
    'Dose batata artesanal': 'Dose de batata frita artesanal', 'Dose batata doce': 'Dose de batata doce',
    'Molho cheddar': 'Molho cheddar (300 g)', 'Maionese caseira extra': 'Maionese caseira',
    'Maionese caseira malagueta picante': 'Maionese de malagueta picante',
    'Super Bock 0,33': 'Super Bock 0,33 L', 'Água Alardo 0,33': 'Água Alardo 0,33 L',
}
DESCR = {
    'Boom! Terra e Mar, Hamburguer mês Outubro': 'Hambúrguer do mês (outubro). ',
}


def opcoes_para(burger):
    d = limpa(burger['descricao']).lower()
    grupos = []
    paes = [k for k, v in MODIFICADORES.items() if v[0] == 'pao']
    itens = []
    for k in paes:
        nome = MODIFICADORES[k][1]
        if nome.lower().split()[-1] in d and 'brioche' in nome.lower() and 'brioche' in d:
            continue  # ja vem em brioche
        itens.append(k)
    grupos.append(('Trocar o pão', 0, 1, itens))
    carnes = [k for k, v in MODIFICADORES.items() if v[0] == 'carne']
    if 'beyond' in d:
        carnes = [k for k in carnes if 'Veggie' not in k]
    if 'frango' in d.split('.')[0]:
        carnes = [k for k in carnes if 'Frango' not in k]
    grupos.append(('Trocar a carne', 0, 1, carnes))
    grupos.append(('Extras', 0, 4, [k for k, v in MODIFICADORES.items() if v[0] == 'extra']))
    if 'batata' in d:
        grupos.append(('Batata', 0, 1, ['Com batata doce']))
    out = []
    for gi, (nome, mn, mx, itens) in enumerate(grupos, 1):
        if not itens:
            continue
        gid = f"boom-{slug(burger['nome'])}-{slug(nome)}"
        out.append({
            'id': gid, 'name': nome, 'is_required': mn > 0, 'min_choices': mn, 'max_choices': mx,
            'sort_order': gi,
            'items': [{
                'id': f"{gid}-{slug(MODIFICADORES[k][1])}", 'name': MODIFICADORES[k][1],
                'preco_loja': None, 'preco_glovo_ref': por_nome[k]['preco_glovo'], 'sort_order': ii,
            } for ii, k in enumerate(itens, 1)],
        })
    return out


produtos, excluidos = [], []
ordem = 0
for cat, secs in CAT:
    for x in g:
        nome = limpa(x['nome'])
        if x['seccao'] is None or limpa(x['seccao']) not in secs:
            continue
        if nome in EXCLUIDOS:
            excluidos.append({'nome': nome, 'motivo': EXCLUIDOS[nome]})
            continue
        if nome in MODIFICADORES and nome not in SOLTOS_TAMBEM:
            continue
        ordem += 1
        e_burger = cat == 'Hambúrgueres'
        produtos.append({
            'id': f"boom-{slug(nome)}",
            'name': NOMES.get(nome, nome),
            'description': DESCR.get(nome, '') + limpa(x['descricao']),
            'category': cat,
            'sort_order': ordem,
            'is_popular': x['seccao'] == 'Mais vendidos',
            'age_restricted': nome in ALCOOL,
            'allergens': None,  # a Glovo nao os publica; pedir ao dono, nunca adivinhar
            'preco_loja': None,
            'preco_glovo_ref': x['preco_glovo'],
            'glovo_id': x['glovo_id'],
            'foto_origem': None if nome in FOTO_NAO_E_DELE else ('glovo/fotos/' + x['foto_local'] if x.get('foto_local') else None),
            'foto_nota': FOTO_NAO_E_DELE.get(nome),
            'option_groups': opcoes_para(x) if e_burger else [],
        })
for x in g:
    if limpa(x['nome']) in EXCLUIDOS:
        excluidos.append({'nome': limpa(x['nome']), 'motivo': EXCLUIDOS[limpa(x['nome'])]})
for k in MODIFICADORES:
    if k in FOTO_NAO_E_DELE:
        excluidos.append({'nome': k, 'motivo': 'vira opcao; ' + FOTO_NAO_E_DELE[k]})

doc = {
    'restaurant_id': RID,
    'fonte': 'Glovo Guarda, loja 539100 (catalogo publico lido a 2026-10-27); textos e fotos do proprio dono',
    'regra_preco': 'preco_loja = o que o dono quer RECEBER (products.partner_shelf_price). '
                   'products.price = round(preco_loja / (1 - partner_visible_commission_pct) * (1 + partner_hidden_markup_pct), 2) '
                   '-> hoje 0,10 e 0,05 (x1,1667). price_add das opcoes com a mesma formula.',
    'estado': 'A ESPERA DOS PRECOS DO DONO - nada disto esta na base',
    'produtos': produtos,
    'excluidos': excluidos,
}
json.dump(doc, open(SAIDA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('produtos', len(produtos), 'com opcoes', sum(1 for p in produtos if p['option_groups']),
      'itens de opcao', sum(len(gq['items']) for p in produtos for gq in p['option_groups']), 'excluidos', len(excluidos))
for c, _ in CAT:
    print(' ', c, sum(1 for p in produtos if p['category'] == c))

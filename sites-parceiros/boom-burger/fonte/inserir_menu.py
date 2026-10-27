# -*- coding: utf-8 -*-
"""A.5 — gera o SQL que poe o menu da Boom! Burger na base, com os PRECOS DO DONO (regra 5).

Entrada: fonte/precos-dono.json, escrito a partir do adendo com a lista dele:
  {"produtos": {"boom-bombastico": 12.50, ...},          # preco da LOJA (o que ele quer receber)
   "opcoes":   {"Pão brioche": 1.80, "Peito de frango grelhado": 2.20, ...},  # pelo nome da opcao
   "fora":     ["boom-terra-e-mar"]}                       # produtos que ele disse que nao quer
Saida: fonte/inserir_menu.sql (uma transacao) e fonte/verificar_menu.sql.

Regra 5: products.partner_shelf_price = loja; products.price = round(loja / (1 - vis) * (1 + oculto), 2)
com vis/oculto lidos de platform_settings (hoje 0,10 e 0,05). Se partner_store_share(price) nao der
a loja ao centimo, escolhe-se price -0,01 ou +0,01 (o que der; nunca outro valor). Opcoes (price_add)
com a mesma formula. Preco da Glovo so em product_price_sources (fonte 'glovo', modo 'referencia').
Nada disto tira o "Em breve": a loja continua coming_soon = true.
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
prep = json.load(open(os.path.join(AQUI, 'menu-preparacao.json'), encoding='utf-8'))
import sys
# ensaio: python inserir_menu.py <precos.json> <n_produtos> <pasta_saida>  (nada no repo)
PRECOS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, 'precos-dono.json')
SAIDA = sys.argv[3] if len(sys.argv) > 3 else AQUI
dono = json.load(open(PRECOS, encoding='utf-8'))
if len(sys.argv) > 2:
    prep['produtos'] = prep['produtos'][:int(sys.argv[2])]
RID = prep['restaurant_id']
URL_ST = 'https://ojykpzwqrtusfeakzrna.supabase.co/storage/v1/object/public/restaurant-assets/'
GLOVO = 'https://glovoapp.com/pt/pt/guarda/stores/boom-burger-hamburgueria-artesanal-grd'
q = lambda t: "'" + str(t).replace("'", "''") + "'" if t is not None else 'null'

faltam, linhas_p, linhas_g, linhas_i, linhas_s = [], [], [], [], []
fora = set(dono.get('fora', []))
for p in prep['produtos']:
    if p['id'] in fora:
        continue
    loja = dono['produtos'].get(p['id'])
    if loja is None:
        faltam.append(p['name'])
        continue
    foto = URL_ST + p['foto_storage'] if p.get('foto_storage') else None
    linhas_p.append(f"({q(p['id'])},{q(p['name'])},{q(p['description'])},{q(p['category'])},{loja:.2f},{p['sort_order']},"
                    f"{str(p['is_popular']).lower()},{str(p['age_restricted']).lower()},{q(foto)},{q(p.get('foto_origem_final'))})")
    if p.get('preco_glovo_ref') is not None:
        linhas_s.append(f"({q(p['id'])},{p['preco_glovo_ref']:.2f},{q(p['name'])})")
    for g in p['option_groups']:
        itens = [(it, dono['opcoes'].get(it['name'])) for it in g['items']]
        for it, v in itens:
            if v is None:
                faltam.append(f"opção {it['name']}")
        itens = [(it, v) for it, v in itens if v is not None]
        if not itens:
            continue
        linhas_g.append(f"({q(g['id'])},{q(p['id'])},{q(g['name'])},{str(g['is_required']).lower()},{g['min_choices']},{g['max_choices']},{g['sort_order']})")
        for it, v in itens:
            linhas_i.append(f"({q(it['id'])},{q(g['id'])},{q(it['name'])},{v:.2f},{it['sort_order']})")

FORMULA = ("round({x} / (1 - (select (value::text)::numeric from public.platform_settings where key='partner_visible_commission_pct'))"
           " * (1 + (select (value::text)::numeric from public.platform_settings where key='partner_hidden_markup_pct')), 2)")
AJUSTA = ("(select c from (values ({b}), ({b} - 0.01), ({b} + 0.01)) t(c) where public.partner_store_share(c) = {x} "
          "order by abs(c - {b}) limit 1)")


def preco_app(x):
    b = FORMULA.format(x=x)
    return f"coalesce({AJUSTA.format(b=b, x=x)}, {b})"


sql = ["-- Menu Boom! Burger com os precos do dono (regra 5). Gerado por fonte/inserir_menu.py.", "begin;"]
sql.append("with v(id, name, description, category, loja, sort_order, is_popular, age_restricted, photo_url, image_source) as (values\n  "
           + ",\n  ".join(linhas_p) + ")\n"
           "insert into public.products (id, restaurant_id, name, description, category, partner_shelf_price, price, sort_order, is_popular,\n"
           "  age_restricted, photo_url, image_source, needs_photo, is_available, source, updated_at)\n"
           f"select v.id, {q(RID)}, v.name, v.description, v.category, v.loja, {preco_app('v.loja')}, v.sort_order, v.is_popular,\n"
           "  v.age_restricted, v.photo_url, v.image_source, v.photo_url is null, true, 'dono_whatsapp_2026_10_27', now() from v;")
if linhas_g:
    sql.append("insert into public.product_option_groups (id, product_id, name, is_required, min_choices, max_choices, sort_order) values\n  "
               + ",\n  ".join(linhas_g) + ";")
    sql.append("with v(id, group_id, name, loja, sort_order) as (values\n  " + ",\n  ".join(linhas_i) + ")\n"
               f"insert into public.product_option_items (id, group_id, name, price_add, is_available, sort_order)\n"
               f"select v.id, v.group_id, v.name, {preco_app('v.loja')}, true, v.sort_order from v;")
if linhas_s:
    sql.append("with v(product_id, preco, nome) as (values\n  " + ",\n  ".join(linhas_s) + ")\n"
               "insert into public.product_price_sources (product_id, restaurant_id, fonte, preco, url, modo, nome_na_fonte, confianca, duvidoso, apanhado_em)\n"
               f"select v.product_id, {q(RID)}, 'glovo', v.preco, {q(GLOVO)}, 'referencia', v.nome, 1, false, '2026-10-27 08:50+00' from v\n"
               "where exists (select 1 from public.products p where p.id = v.product_id);")
sql.append("commit;")
open(os.path.join(SAIDA, 'inserir_menu.sql'), 'w', encoding='utf-8').write('\n'.join(sql) + '\n')

ver = f"""-- Prova A.5: partner_store_share(price) = preco da loja, AO CENTIMO, em todos (produtos e opcoes)
select 'produtos' o, count(*) total, count(*) filter (where public.partner_store_share(price) = partner_shelf_price) certos,
       count(*) filter (where photo_url is null or needs_photo) sem_foto
  from public.products where restaurant_id = {q(RID)}
union all
select 'opcoes', count(*), count(*) filter (where public.partner_store_share(i.price_add) = v.loja), null
  from public.product_option_items i join public.product_option_groups g on g.id = i.group_id
  join public.products p on p.id = g.product_id
  join (values {", ".join(f"({q(n)},{v:.2f})" for n, v in dono['opcoes'].items()) or "('',0)"}) v(nome, loja) on v.nome = i.name
 where p.restaurant_id = {q(RID)}
union all
select 'loja_em_breve', count(*), count(*) filter (where coming_soon), null from public.restaurants where id = {q(RID)};
"""
open(os.path.join(SAIDA, 'verificar_menu.sql'), 'w', encoding='utf-8').write(ver)
print('produtos', len(linhas_p), 'grupos', len(linhas_g), 'itens', len(linhas_i), 'refs glovo', len(linhas_s))
print('SEM PRECO DO DONO:', faltam if faltam else 'nenhum')

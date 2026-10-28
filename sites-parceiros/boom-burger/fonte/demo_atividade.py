# -*- coding: utf-8 -*-
"""D1b — o Estafeta Demonstracao envia o "comprovativo de atividade" pela via normal (sessao propria):
um PDF que diz claramente que e uma conta de demonstracao, sem atividade real, e o NIF generico de
consumidor final (999999990), que nao pertence a ninguem. A aprovacao (admin) faz-se a seguir em SQL,
com a mesma nota. Palavra-passe temporaria so para este passo (descartada)."""
import json, os, secrets, string, urllib.request
import pymupdf

AQUI = os.path.dirname(os.path.abspath(__file__))
env = dict(l.strip().split('=', 1) for l in open(r'C:\BoraLocal\projetosflutter\bora_app\backend\.env', encoding='utf-8') if '=' in l)
URL, SR = env['SUPABASE_URL'].strip().rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
ANON = json.load(open(r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines', encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
uids = json.load(open(os.path.join(AQUI, 'demo_uids.json'), encoding='utf-8'))
EMAIL = 'demo.estafeta.boomburger@bora.app'
UID = uids[EMAIL]


def http(metodo, caminho, dados=None, chave=SR, token=None, tipo='application/json'):
    h = {'apikey': chave, 'Authorization': f'Bearer {token or chave}', 'Content-Type': tipo}
    if isinstance(dados, (dict, list)):
        dados = json.dumps(dados).encode()
    req = urllib.request.Request(URL + caminho, method=metodo, headers=h, data=dados)
    try:
        r = urllib.request.urlopen(req, timeout=60)
        t = r.read()
        return r.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')[:300]


doc = pymupdf.open()
pg = doc.new_page()
pg.insert_text((60, 90), 'Bora - conta de DEMONSTRACAO', fontsize=18)
for i, l in enumerate(['Estafeta Demonstracao (demo.estafeta.boomburger@bora.app)',
                       'Nao e um prestador real nem tem atividade aberta nas Financas.',
                       'Criada a 27/10/2026 para a demonstracao da loja Boom! Burger (Guarda) a 28/10/2026.',
                       'So recebe pedidos de demonstracao dessa loja (modo_demo_loja). NIF generico 999999990.']):
    pg.insert_text((60, 140 + 22 * i), l, fontsize=11)
pdf = doc.tobytes()

pw = 'Demo' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)) + '!7'
http('PUT', f'/auth/v1/admin/users/{UID}', {'password': pw})
st, s = http('POST', '/auth/v1/token?grant_type=password', {'email': EMAIL, 'password': pw}, chave=ANON)
assert st == 200, (st, s)
tok = s['access_token']
st, r = http('POST', '/rest/v1/rpc/provider_atividade_get', {}, chave=ANON, token=tok)  # como a app ao abrir o ecra
print('provider_atividade_get', st, str(r)[:160])
caminho = f'{UID}/comprovativo-demonstracao.pdf'
st, r = http('POST', f'/storage/v1/object/provider-atividade/{caminho}', pdf, chave=ANON, token=tok, tipo='application/pdf')
print('upload', st, r if st not in (200, 201) else 'ok')
st, r = http('POST', '/rest/v1/rpc/provider_atividade_enviar', {'p_nif': '999999990', 'p_documento_path': caminho}, chave=ANON, token=tok)
print('provider_atividade_enviar', st, r)
del pw, tok

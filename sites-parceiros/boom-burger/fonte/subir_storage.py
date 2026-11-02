# -*- coding: utf-8 -*-
"""Sobe para o Storage (balde publico restaurant-assets) os ficheiros de um indice JSON.

Uso: python subir_storage.py ../media/app/indice.json
A chave de servico le-se de bora_app/backend/.env e NUNCA se imprime.
Prova: depois de subir, faz GET ao URL publico e compara o tamanho em bytes.
"""
import json, mimetypes, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(AQUI, '..')
ENV = r'C:\BoraLocal\projetosflutter\bora_app\backend\.env'
env = {}
for linha in open(ENV, encoding='utf-8'):
    if '=' in linha and not linha.strip().startswith('#'):
        k, v = linha.strip().split('=', 1)
        env[k] = v.strip().strip('"')
URL, KEY = env['SUPABASE_URL'].rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY']
BALDE = 'restaurant-assets'
ind = json.load(open(sys.argv[1], encoding='utf-8'))
ok = falha = 0
for key, v in ind.items():
    loc = os.path.join(B, v['local'])
    dados = open(loc, 'rb').read()
    tipo = mimetypes.guess_type(loc)[0] or ('image/webp' if loc.endswith('.webp') else 'application/octet-stream')
    req = urllib.request.Request(f'{URL}/storage/v1/object/{BALDE}/{key}', data=dados, method='POST',
                                 headers={'Authorization': f'Bearer {KEY}', 'apikey': KEY, 'Content-Type': tipo,
                                          'x-upsert': 'true', 'cache-control': 'max-age=3600'})
    try:
        urllib.request.urlopen(req, timeout=60).read()
        pub = f'{URL}/storage/v1/object/public/{BALDE}/{key}'
        n = len(urllib.request.urlopen(pub, timeout=60).read())
        if n == len(dados):
            v['url'] = pub
            ok += 1
        else:
            print('TAMANHO DIFERENTE', key, n, len(dados))
            falha += 1
    except Exception as e:
        print('FALHOU', key, str(e)[:160])
        falha += 1
json.dump(ind, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('subidos e lidos de volta:', ok, 'falhas:', falha)

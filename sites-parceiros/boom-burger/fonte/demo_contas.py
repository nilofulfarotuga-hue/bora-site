# -*- coding: utf-8 -*-
"""D1 — contas de demonstracao da Boom! Burger (cliente e estafeta), pelas vias normais.

  criar   : cria os 2 utilizadores (Admin API) com palavra-passe aleatoria descartada; o estafeta
            regista-se com a PROPRIA sessao (driver_register_or_update, como na app). Imprime os uid.
            (A aprovacao do estafeta e feita a seguir pelo admin_approve_driver, em SQL.)
  entregar: troca as palavras-passe por novas e manda-as SO ao Danilo pelo Telegram (API do bot,
            texto por stdin do ssh, sem log), com a explicacao de como se usa cada conta.
Nada de palavras-passe impressas, em ficheiro, repositorio, Cortex ou e2e_log.
"""
import json, os, secrets, string, subprocess, sys, urllib.request

ENV = r'C:\BoraLocal\projetosflutter\bora_app\backend\.env'
env = dict(l.strip().split('=', 1) for l in open(ENV, encoding='utf-8') if '=' in l and not l.startswith('#'))
URL = env['SUPABASE_URL'].strip().rstrip('/')
SR = env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
ANON = json.load(open(r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines', encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
CLIENTE = ('demo.cliente.boomburger@bora.app', 'Cliente Demonstração', 'client')
ESTAFETA = ('demo.estafeta.boomburger@bora.app', 'Estafeta Demonstração', 'driver')


def http(metodo, caminho, corpo=None, chave=SR, token=None):
    h = {'apikey': chave, 'Authorization': f'Bearer {token or chave}', 'Content-Type': 'application/json'}
    req = urllib.request.Request(URL + caminho, method=metodo, headers=h,
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        r = urllib.request.urlopen(req, timeout=60)
        t = r.read()
        return r.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')[:300]


def senha():
    a = string.ascii_letters + string.digits
    return 'Demo' + ''.join(secrets.choice(a) for _ in range(10)) + '!' + str(secrets.randbelow(90) + 10)


UIDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'demo_uids.json')  # uid nao e segredo


def uid_de(email):
    # (a lista /auth/v1/admin/users devolve 500 "Database error finding users" a 27/10: reportado)
    try:
        return json.load(open(UIDS, encoding='utf-8')).get(email)
    except FileNotFoundError:
        return None


def guarda_uid(email, uid):
    try:
        d = json.load(open(UIDS, encoding='utf-8'))
    except FileNotFoundError:
        d = {}
    d[email] = uid
    json.dump(d, open(UIDS, 'w', encoding='utf-8'), indent=1)


if sys.argv[1] == 'criar':
    for email, nome, papel in (CLIENTE, ESTAFETA):
        uid = uid_de(email)
        if not uid:
            st, u = http('POST', '/auth/v1/admin/users', {'email': email, 'password': senha(), 'email_confirm': True,
                                                         'user_metadata': {'name': nome, 'role': papel, 'bora_role': papel,
                                                                           'email_verified': True}})
            if st not in (200, 201):
                raise SystemExit(f'criar {email} falhou {st} {u}')
            uid = u['id']
            guarda_uid(email, uid)
        print(papel, uid)
    # o estafeta regista-se como na app: sessao propria (palavra-passe temporaria so para este passo)
    uid_e = uid_de(ESTAFETA[0])
    pw = senha()
    http('PUT', f'/auth/v1/admin/users/{uid_e}', {'password': pw})
    st, s = http('POST', '/auth/v1/token?grant_type=password', {'email': ESTAFETA[0], 'password': pw}, chave=ANON)
    if st != 200:
        raise SystemExit(f'login estafeta falhou {st} {s}')
    st, r = http('POST', '/rest/v1/rpc/driver_register_or_update', {
        'p_name': ESTAFETA[1], 'p_phone': '+351900000001', 'p_vehicle_type': 'motorcycle',
        'p_address': 'Conta de demonstração da Boom! Burger (Guarda) — não é um estafeta real'},
        chave=ANON, token=s['access_token'])
    print('driver_register_or_update', st, json.dumps(r)[:200] if not isinstance(r, str) else r[:200])
    del pw

elif sys.argv[1] == 'entregar':
    senhas = {}
    for email, nome, papel in (CLIENTE, ESTAFETA):
        uid = uid_de(email)
        pw = senha()
        st, _ = http('PUT', f'/auth/v1/admin/users/{uid}', {'password': pw})
        st2, s = http('POST', '/auth/v1/token?grant_type=password', {'email': email, 'password': pw}, chave=ANON)
        print(papel, 'nova palavra-passe', st, '| login', st2)
        senhas[papel] = pw
    msg = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'telegram_demo.txt'), encoding='utf-8').read()
    msg = msg.replace('{SENHA_CLIENTE}', senhas['client']).replace('{SENHA_ESTAFETA}', senhas['driver'])
    remoto = ("set -a; . /opt/data/social/.aviso.conf; set +a; "
              "curl -sS --max-time 25 -o /tmp/.r.json -w '%{http_code}' -X POST "
              "\"https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage\" "
              "--data-urlencode \"chat_id=$TELEGRAM_HOME_CHANNEL\" --data-urlencode text@- -d disable_web_page_preview=true; "
              "echo; grep -o '\"ok\":[a-z]*' /tmp/.r.json; rm -f /tmp/.r.json")
    r = subprocess.run(['ssh', '-i', os.path.expanduser('~/.ssh/id_ed25519_vps'), '-o', 'BatchMode=yes',
                        'root@srv1786862.hstgr.cloud', remoto], input=msg.encode('utf-8'), capture_output=True, timeout=90)
    print('telegram:', r.stdout.decode(errors='replace').strip().replace('\n', ' '))
    senhas.clear()

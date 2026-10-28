# -*- coding: utf-8 -*-
"""A.3 — conta de parceiro boomburger@bora.app (como a sabores.brasil@bora.app).

Passos:  criar  -> cria o utilizador (Admin API) com palavra-passe aleatoria, confirma o login
                   com a chave publica e manda a palavra-passe SO ao Danilo pelo Telegram,
                   direto pela API (o texto vai por stdin do ssh; nao fica em log nenhum).
         provar -> nao faz nada aqui (a prova do painel e por SQL + web).
A palavra-passe nunca e impressa, nunca vai para ficheiro, repo, Cortex nem e2e_log.
"""
import base64, json, os, secrets, string, subprocess, sys, urllib.request

ENV = r'C:\BoraLocal\projetosflutter\bora_app\backend\.env'
DEF = r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines'
env = dict(l.strip().split('=', 1) for l in open(ENV, encoding='utf-8') if '=' in l and not l.startswith('#'))
URL = env['SUPABASE_URL'].strip().rstrip('/')
SR = env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
ANON = json.load(open(DEF, encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
EMAIL = 'boomburger@bora.app'


def http(metodo, caminho, corpo=None, chave=SR):
    req = urllib.request.Request(URL + caminho, method=metodo,
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={'apikey': chave, 'Authorization': f'Bearer {chave}', 'Content-Type': 'application/json'})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


alfa = string.ascii_letters + string.digits
pw = 'Boom' + ''.join(secrets.choice(alfa) for _ in range(10)) + '!' + str(secrets.randbelow(90) + 10)
st, u = http('POST', '/auth/v1/admin/users', {
    'email': EMAIL, 'password': pw, 'email_confirm': True,
    'user_metadata': {'name': 'Boom! Burger', 'role': 'partner', 'bora_role': 'partner', 'email_verified': True}})
if st not in (200, 201):
    print('criar falhou', st, json.dumps(u)[:300])
    sys.exit(1)
uid = u['id']
print('utilizador criado', uid)

# login a serio com a chave publica (o que a app faz)
st, s = http('POST', '/auth/v1/token?grant_type=password', {'email': EMAIL, 'password': pw}, chave=ANON)
if st != 200 or 'access_token' not in s:
    print('LOGIN FALHOU', st, json.dumps(s)[:200])
    sys.exit(2)
carga = s['access_token'].split('.')[1]
claims = json.loads(base64.urlsafe_b64decode(carga + '=' * (-len(carga) % 4)))
print('login 200; sub =', claims.get('sub') == uid, '; role jwt =', claims.get('role'),
      '; user_role =', claims.get('user_role') or claims.get('app_metadata', {}).get('role'))

msg = ('Conta de parceiro da Boom! Burger (para entregar ao dono quando ele aprovar a loja).\n'
       f'Email: {EMAIL}\nPalavra-passe: {pw}\n'
       'Entra em app.boraguarda.com, no acesso de parceiro. É temporária: quando ele der o email verdadeiro, '
       'troca-se, como na Goola. Esta mensagem é só para ti; não fica guardada em lado nenhum.')
remoto = ("set -a; . /opt/data/social/.aviso.conf; set +a; "
          "curl -sS --max-time 25 -o /tmp/.r.json -w '%{http_code}' -X POST "
          "\"https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage\" "
          "--data-urlencode \"chat_id=$TELEGRAM_HOME_CHANNEL\" --data-urlencode text@-; "
          "echo; grep -o '\"ok\":[a-z]*' /tmp/.r.json; rm -f /tmp/.r.json")
r = subprocess.run(['ssh', '-i', os.path.expanduser('~/.ssh/id_ed25519_vps'), '-o', 'BatchMode=yes',
                    'root@srv1786862.hstgr.cloud', remoto], input=msg.encode('utf-8'), capture_output=True, timeout=90)
print('telegram:', r.stdout.decode(errors='replace').strip().replace('\n', ' '), r.stderr.decode(errors='replace')[:200])
del pw

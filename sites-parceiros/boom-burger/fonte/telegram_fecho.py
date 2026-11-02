# -*- coding: utf-8 -*-
"""Fecho da missao: 3 capturas + texto ao Danilo pelo Telegram (album com legenda).
As imagens vao por scp para /tmp da VPS e seguem pela API do bot (token lido la, nunca aqui)."""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
S = os.path.abspath(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger', 'selecao'))
FOTOS = ['01-final-390-heroi.jpg', '06-final-390-menu.jpg', '13-final-1440-cena-meio.jpg']
CHAVE = os.path.expanduser('~/.ssh/id_ed25519_vps')
HOST = 'root@srv1786862.hstgr.cloud'
TEXTO = open(os.path.join(AQUI, 'telegram_fecho.txt'), encoding='utf-8').read().strip()

for f in FOTOS:
    assert os.path.exists(os.path.join(S, f)), f
r = subprocess.run(['scp', '-i', CHAVE, '-o', 'BatchMode=yes'] + [os.path.join(S, f) for f in FOTOS] + [HOST + ':/tmp/'],
                   capture_output=True, timeout=120)
print('scp', r.returncode, r.stderr.decode(errors='replace')[:200])
media = '[' + ','.join('{"type":"photo","media":"attach://f%d"}' % i for i in range(len(FOTOS))) + ']'
forms = ' '.join(f"-F f{i}=@/tmp/{f}" for i, f in enumerate(FOTOS))
remoto = ("set -a; . /opt/data/social/.aviso.conf; set +a; "
          f"curl -sS --max-time 60 -o /tmp/.r1.json -w '%{{http_code}} ' -X POST \"https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMediaGroup\" "
          f"-F chat_id=\"$TELEGRAM_HOME_CHANNEL\" -F media='{media}' {forms}; grep -o '\"ok\":[a-z]*' /tmp/.r1.json | head -1; "
          "curl -sS --max-time 30 -o /tmp/.r2.json -w '%{http_code} ' -X POST \"https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage\" "
          "--data-urlencode \"chat_id=$TELEGRAM_HOME_CHANNEL\" --data-urlencode text@- -d disable_web_page_preview=true; "
          "grep -o '\"ok\":[a-z]*' /tmp/.r2.json | head -1; rm -f /tmp/.r1.json /tmp/.r2.json " + ' '.join('/tmp/' + f for f in FOTOS))
r = subprocess.run(['ssh', '-i', CHAVE, '-o', 'BatchMode=yes', HOST, remoto], input=TEXTO.encode('utf-8'), capture_output=True, timeout=180)
print('telegram:', r.stdout.decode(errors='replace').strip().replace('\n', ' '), r.stderr.decode(errors='replace')[:200])

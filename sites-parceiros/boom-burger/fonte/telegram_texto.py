# -*- coding: utf-8 -*-
"""Manda um texto ao Danilo pelo Telegram (API do bot na VPS; o token e lido la, o texto vai por stdin, sem log).
Uso: python telegram_texto.py <ficheiro.txt>"""
import os, subprocess, sys

texto = open(sys.argv[1], encoding='utf-8').read().strip()
remoto = ("set -a; . /opt/data/social/.aviso.conf; set +a; "
          "curl -sS --max-time 25 -o /tmp/.r.json -w '%{http_code}' -X POST "
          "\"https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage\" "
          "--data-urlencode \"chat_id=$TELEGRAM_HOME_CHANNEL\" --data-urlencode text@- -d disable_web_page_preview=true; "
          "echo; grep -o '\"ok\":[a-z]*' /tmp/.r.json; rm -f /tmp/.r.json")
r = subprocess.run(['ssh', '-i', os.path.expanduser('~/.ssh/id_ed25519_vps'), '-o', 'BatchMode=yes', 'root@srv1786862.hstgr.cloud', remoto],
                   input=texto.encode('utf-8'), capture_output=True, timeout=90)
print('telegram:', r.stdout.decode(errors='replace').strip().replace('\n', ' '), r.stderr.decode(errors='replace')[:200])

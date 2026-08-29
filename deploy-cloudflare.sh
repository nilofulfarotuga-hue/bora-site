#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Deploy do bora-site para Cloudflare Pages (projeto: bora-site).
#
# O projeto Pages "bora-site" é de UPLOAD DIRETO (wrangler) — NÃO está ligado
# ao GitHub — por isso `git push` NÃO publica. É preciso correr este deploy.
#
# Requer um Cloudflare API Token com permissão "Account > Cloudflare Pages: Edit"
# (conta Nilofulfarotuga@gmail.com). NUNCA committar o valor do token.
# Formas de o fornecer (escolhe UMA):
#   1) export CLOUDFLARE_API_TOKEN=xxxxxxxx        # nesta shell, antes de correr
#   2) criar um ficheiro .env (ja no .gitignore) com a linha:
#        CLOUDFLARE_API_TOKEN=xxxxxxxx
#
# SEGURANCA: publica a partir de uma COPIA FILTRADA (so os ficheiros publicos
# do site), para NUNCA expor o .env/token, relatorios, backups nem os PNG
# originais em assets/cinema/src.
#
# Uso:  bash deploy-cloudflare.sh
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"

# Carrega .env local se existir (o .env esta no .gitignore — nunca vai para o git).
if [ -f .env ]; then set -a; . ./.env; set +a; fi

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  echo "ERRO: falta CLOUDFLARE_API_TOKEN. Ve as instrucoes no topo deste ficheiro." >&2
  exit 1
fi

# ---- copia filtrada (whitelist do que e publico) ----
STAGE_ROOT="$(mktemp -d)"
STAGE="$STAGE_ROOT/site"
mkdir -p "$STAGE"

for f in index.html app.html estafetas.html faq.html parceiros.html privacidade.html termos.html \
         viagens.html entregas.html beleza.html festas.html mais.html ser-parceiro.html \
         trabalhos.html orcamento.html 404.html \
         manifest.json robots.txt sitemap.xml; do
  [ -f "$f" ] && cp "$f" "$STAGE"/
done
# Uma pagina por parceiro (geradas por gerar_paginas.py) + o JSON de origem.
[ -d loja ]  && cp -r loja  "$STAGE"/loja
[ -d dados ] && cp -r dados "$STAGE"/dados
# assets/ vai INTEIRO: e onde vivem os videos (assets/video/*.mp4) e os
# posters. Video nunca em base64, e nunca fora desta copia — se ficar
# de fora nao e publicado e ninguem da por isso. (site-premio 2026-08-29)
cp -r assets "$STAGE"/assets
rm -rf "$STAGE"/assets/cinema/src   # PNG originais nao sao servidos (~7MB)

# rede de seguranca: garante que nenhum segredo/relatorio entrou na copia
rm -f "$STAGE"/.env "$STAGE"/*.md 2>/dev/null || true

echo "A publicar a partir de: $STAGE"
if npx --yes wrangler@latest pages deploy "$STAGE" \
     --project-name=bora-site --branch=main --commit-dirty=true; then
  rc=0
else
  rc=$?
fi

rm -rf "$STAGE_ROOT"
exit $rc

#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Deploy do bora-site para Cloudflare Pages (projeto: bora-site).
#
# O projeto Pages "bora-site" é de UPLOAD DIRETO (wrangler) — NÃO está ligado
# ao GitHub — por isso `git push` NÃO publica. É preciso correr este deploy.
#
# Requer um Cloudflare API Token com permissão "Cloudflare Pages: Edit"
# (conta Nilofulfarotuga@gmail.com). NUNCA committar o valor do token.
# Formas de o fornecer (escolhe UMA):
#   1) export CLOUDFLARE_API_TOKEN=xxxxxxxx        # nesta shell, antes de correr
#   2) criar um ficheiro .env (já no .gitignore) com a linha:
#        CLOUDFLARE_API_TOKEN=xxxxxxxx
#
# Uso:  bash deploy-cloudflare.sh
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"

# Carrega .env local se existir (o .env está no .gitignore — nunca vai para o git).
if [ -f .env ]; then set -a; . ./.env; set +a; fi

if [ -z "${CLOUDFLARE_API_TOKEN:-}" ]; then
  echo "ERRO: falta CLOUDFLARE_API_TOKEN. Vê as instruções no topo deste ficheiro." >&2
  exit 1
fi

exec npx --yes wrangler@latest pages deploy . \
  --project-name=bora-site \
  --branch=main \
  --commit-dirty=true

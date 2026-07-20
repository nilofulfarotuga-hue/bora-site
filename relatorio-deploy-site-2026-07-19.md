# Relatório — Deploy da homepage cinematográfica

**Data:** 2026-07-19 → execução na madrugada de 2026-07-20
**Repo:** `nilofulfarotuga-hue/bora-site` (branch `main`, HEAD `62b46ab`)
**Objetivo:** publicar no ar o redesenho cinematográfico que já está no GitHub.

---

## ✅ RESOLVIDO — SITE NO AR (2026-07-20)

O deploy **foi concluído com sucesso** com um API Token válido fornecido pelo Danilo.
- **Deployment:** https://b17a933b.bora-site.pages.dev · **Produção:** https://bora-site.pages.dev
- **Verificado por fetch** (produção, com e sem cache): `assets/cinema` ✅, `ScrollTrigger` ✅,
  `cine-scene`/`cine-title`/`cine-kicker` ✅, headline "…cidade inteira." ✅, imagens
  `assets/cinema/*.webp` → **HTTP 200** ✅, `google-site-verification` intacta ✅.
- **Segurança:** publicado a partir de **cópia filtrada** → `bora-site.pages.dev/.env` **NÃO**
  expõe o token (confirmado). O `.env` fica só local (gitignored).
- **1ª tentativa falhou** porque o valor dado era o **Account ID** (`2cd0…`), não um token
  (erro `6111`). Resolvido com token real. *(Histórico do diagnóstico abaixo, para referência.)*

---

## TL;DR (histórico do diagnóstico)

- ✅ O código está **correto e no GitHub** (`62b46ab`): `index.html` + `/assets/cinema/` (9 WebP) + GSAP/ScrollTrigger.
- ⚠️ O deploy exigiu **autenticação**: não havia `CLOUDFLARE_API_TOKEN` na máquina (env, `.env`, User/Machine, nem OAuth do wrangler). Resolvido quando o Danilo forneceu um token válido.
- ✅ **Site no ar atualizado** para a versão cinematográfica (confirmado por fetch).
- 💡 **Recomendação futura (Opção B):** ligar o Pages ao GitHub para os pushes publicarem sozinhos.

---

## 1. Estado do repositório (PASSO 1) — OK

```
git checkout main + git pull origin main  →  Already up to date
HEAD = 62b46ab  (feat(site): homepage cinematográfica scroll-driven)
raiz: index.html ✅   assets/cinema/*.webp ✅ (9 ficheiros)
```

## 2. Comando de deploy tentado (PASSO 2)

```bash
npx wrangler@latest pages deploy . --project-name=bora-site --branch=main --commit-dirty=true
```

## 3. Resultado — FALHA POR AUTENTICAÇÃO (PASSO 3)

Diagnóstico prévio (nada impresso além de SET/UNSET):

| Fonte do token | Estado |
|---|---|
| `CLOUDFLARE_API_TOKEN` (env do processo) | UNSET |
| `CLOUDFLARE_API_TOKEN` (User / Machine no Windows) | UNSET |
| `.env` / `.dev.vars` no repo | não existem |
| `wrangler whoami` (OAuth) | **You are not authenticated** |

**Erro exato do wrangler:**

> X [ERROR] In a non-interactive environment, it's necessary to set a
> `CLOUDFLARE_API_TOKEN` environment variable for wrangler to work.
> (https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)

Não se insistiu às cegas. Não há token na máquina e não é possível criar um novo
token nem fazer `wrangler login` (OAuth por browser) de forma autónoma/headless —
ambos exigem o Danilo no dashboard da Cloudflare.

### Deployment URL
Nenhum — nenhum deployment foi criado.

## 4. Verificação do site no ar (PASSO 4) — ainda ANTIGO

`curl https://bora-site.pages.dev/` (21 691 bytes):

| Marcador (novo) | No ar? |
|---|---|
| `assets/cinema` | ❌ ausente |
| `ScrollTrigger` | ❌ ausente |
| `cine-scene` | ❌ ausente |
| `cidade inteira` (headline nova) | ❌ ausente |
| `google-site-verification` | ✅ presente (já existia na versão antiga) |

→ Confirma que o Pages **não** está ligado ao Git e que o push não publicou.

---

## 5. O que o Danilo precisa de decidir (uma destas resolve)

### Opção A — Fornecer um Cloudflare API Token (rápido)
1. Cloudflare Dashboard → **My Profile → API Tokens → Create Token** →
   template **"Edit Cloudflare Workers"** ou permissão mínima **Account › Cloudflare Pages › Edit**
   (conta Nilofulfarotuga@gmail.com). *(Assumir que o token antigo foi revogado — criar novo.)*
2. Guardar na máquina, **sem o committar**, de UMA destas formas:
   - `export CLOUDFLARE_API_TOKEN=xxxx` na shell, **ou**
   - criar `bora-site/.env` (já está no `.gitignore`) com `CLOUDFLARE_API_TOKEN=xxxx`.
3. Correr: **`bash deploy-cloudflare.sh`** (script criado nesta sessão, na raiz do repo)
   — faz exatamente o deploy acima. Fim.

### Opção B — Ligar o Pages ao GitHub (melhor a longo prazo) ✅ recomendado
Cloudflare Dashboard → **Workers & Pages → bora-site → Settings →
Builds & deployments → Connect to Git** → escolher o repo `nilofulfarotuga-hue/bora-site`,
branch de produção `main`, **sem build command** e **output directory = `/`** (site estático).
A partir daí, **todos os `git push` publicam sozinhos** e este problema nunca mais acontece.

---

## 6. Segurança
- Nenhuma API key foi impressa nem committada. `.mcp.json`, `.env` e `*.key` estão no `.gitignore`.
- Nenhum ficheiro temporário com token foi criado.
- Criado `deploy-cloudflare.sh` (lê o token do ambiente/`.env` em runtime; **não** contém segredos).

---

## 7. Anexos
- Redesign e testes: ver `relatorio-site-cinematografico-2026-07-19.md` + `docs/preview/`.
- Backup pré-redesign: `backup-2026-07-19/`.

---

**FASE 5 fechada em 2026-07-20 07:16 — site liga ao web app.**
"Pedir pelo site" na navbar (sempre visível, também a 390px) e no herói do
capítulo 01, além do botão do fundo que já existia; "Portal do Parceiro —
Entrar" em `parceiros.html`. Todos apontam a https://bora-app-web.pages.dev.
Commit `dd7807b`, publicado e verificado por fetch.

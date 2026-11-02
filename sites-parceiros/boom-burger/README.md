# Boom! Burger — loja parceira no Bora + site de presente

- **Site:** https://boomburger.boraguarda.com/ (projeto Cloudflare Pages `boom-burger`, também em
  `boom-burger-778.pages.dev`). **noindex** até o dono aprovar (meta robots + `X-Robots-Tag` no `_headers`).
- **Provas:** https://provas.boom-burger-778.pages.dev/ (ramo de pré-visualização do mesmo projeto, noindex).
- **Loja na app:** `restaurants.id = 'boom-burger-guarda'`, **coming_soon = true** ("Em breve").
  Ligação direta: https://app.boraguarda.com/#/loja/boom-burger-guarda
- **Conta de parceiro:** `boomburger@bora.app` (palavra-passe só no Telegram do Danilo).
- Missão `boom-burger-2026-10-27`; relatório em `../../.claude/.ai/reports/BOOM-BURGER-2026-10-27.md`.

## Pastas

| Pasta | O que é |
|---|---|
| `origem/` | Material do PRÓPRIO cliente, com a origem por ficheiro em `ORIGEM.md` (WhatsApp, Glovo, logótipo PDF). O zip/manifest do WhatsApp e a ficha do Google ficam fora do git (dados pessoais; repo público). |
| `fonte/` | Todos os guiões (ver abaixo) + `menu-preparacao.json` (menu à espera dos preços) e `PROMPT.md` na raiz. |
| `media/` | Logótipo em SVG por partes e PNG (`media/logo/`), imagens da loja na app (`media/app/`, já no Storage), recorte e camadas (`media/camadas/portobello-v3/` é a versão em uso). |
| `dist/` | O site pronto a publicar. |
| `kit-cartaz/` | Kit para o cartaz e o autocolante (logótipo, 3 recortes, QR testado). Também no Storage em `restaurant-assets/boom-burger-guarda/kit/`. |

## Refazer o site

```bash
cd fonte
python gerar_menu.py      # preços da app (products.price) pela chave pública; sem preços -> "Preço na app"
python imagens_site.py    # só quando mudam fotos (AVIF/WebP; camadas; foto final alinhada ao recorte)
python video.py           # só quando muda o vídeo (12 s, só pixéis do dono)
python og.py              # imagem de partilha
python fontes.py          # só uma vez (Bebas Neue + Inter servidas pelo site)
python build_site.py      # index.html, 404, robots, sitemap, _headers, manifest, vendor GSAP
python shot.py <url> <prefixo>        # provas a 390/360/1440, com e sem "Reduzir movimento"
python prova_titulo.py <url>          # o título aparece inteiro antes de 1 s (adendo 1)
```

## Publicar (caminho ABSOLUTO, sempre)

```bash
cd ../../..            # bora-site
set -a && . ./.env && set +a && export CLOUDFLARE_ACCOUNT_ID=2cd0212b0f5e5c8284aa227f629c050a
npx wrangler@4 pages deploy "C:/BoraLocal/projetosflutter/bora-site/sites-parceiros/boom-burger/dist" \
  --project-name boom-burger --branch main --commit-dirty=true
```
Auditar uns segundos depois e olhar o CONTEÚDO (o Pages dá 200 a tudo). O domínio foi ligado por
`fonte/dominio.py` (custom domain no Pages + CNAME com proxy); é idempotente.

## Quando chegarem os preços do dono

1. Escrever `fonte/precos-dono.json` (formato no topo de `fonte/inserir_menu.py`): o preço da LOJA de
   cada produto e de cada opção; os que ele não quer vão em `"fora"`.
2. `python inserir_menu.py` → `inserir_menu.sql` + `verificar_menu.sql`; correr os dois pelo MCP do
   Supabase. A prova é `partner_store_share(price) = partner_shelf_price` em TODOS (produtos e opções).
3. `python gerar_menu.py && python build_site.py` e publicar: o site passa a mostrar os preços da app.
4. A loja continua "Em breve" — quem a tira é o Claude.ai/Danilo, depois de o dono aprovar.

## Quando o dono aprovar

- Tirar o `noindex`: em `fonte/build_site.py` a linha `<meta name="robots" ...>` e o `X-Robots-Tag` do
  `_headers`; reconstruir e publicar.
- Antes de tirar o "Em breve": recolher os dados legais (NIF, IBAN, nome legal, data de nascimento,
  autocertificação DSA) — o portão de conformidade só atua quando `approval_status` muda, e esta loja
  já nasceu aprovada.
- Pedir-lhe os alergénios (a Glovo não os publica) e confirmar o horário (o VisitGuarda diz outro).

# Relatório Final — Site Oficial Bora App

**Data:** 2026-07-05
**Repositório:** https://github.com/nilofulfarotuga-hue/bora-site
**Hosting:** Cloudflare Pages (projeto `bora-site`, conta `nilofulfarotuga@gmail.com`)

## 1. URL do site (no ar)

**Produção:** https://bora-site.pages.dev/

Verificado com `curl`:
- `/` → 200
- `/faq.html` → 308 → `/faq` → 200 (Cloudflare Pages faz clean-URL redirect automático, normal)
- `/parceiros.html`, `/termos.html` → mesmo comportamento (308 → 200)
- `/sitemap.xml` → 200
- `/robots.txt` → 200

Páginas: `index.html`, `parceiros.html`, `estafetas.html`, `faq.html`, `privacidade.html`, `termos.html`.

## 2. Assets em falta (gerar no Gemini / fornecer)

- ~~Screenshot/mockup da Home do app~~ — **resolvido em 2026-07-05**, ver secção "Fix 2026-07-05" abaixo.
- Badge oficial da Play Store em **PT-PT** não está disponível publicamente na CDN da Google (só devolve 404); foi usado o badge oficial em inglês ("GET IT ON Google Play"), que é o mesmo usado por várias apps portuguesas. Se quiseres o badge PT-PT, tem de vir de um export manual do Google Play Console.

## 3. Placeholders a preencher

**Dados legais RGPD** (`privacidade.html`, `termos.html`):
- `[NOME LEGAL DA EMPRESA]`
- `[NIF]`
- `[MORADA]`
- `[NOME DO DPO]`

**Emails de contacto** — ~~usados por convenção~~ **corrigido em 2026-07-05**: todos apontam agora para `boraappbora@gmail.com` (o email real do Bora), com subject pré-preenchido consoante a página (ver secção "Fix 2026-07-05").

**Redes sociais** — footer do `index.html` tem `href="#"` em Facebook/Instagram com comentário `<!-- TODO Danilo -->`; falta os links reais.

**Link Play Store** usado: `https://play.google.com/store/apps/details?id=pt.boraapp.bora` (conforme fornecido na missão — confirmar que o `id` da app é este quando publicada).

## 4. Como atualizar o site no futuro

```bash
cd bora-site
# editar ficheiros
git add -A && git commit -m "..." && git push
CLOUDFLARE_API_TOKEN=<token> wrangler pages deploy . --project-name=bora-site
```

## Fix 2026-07-05 — emails reais + screenshot Home no hero

**1. Emails corrigidos.** Os emails `@boraapp.pt` usados na v1 não existiam (domínio morto). Substituídos em todo o site por `boraappbora@gmail.com` (email real do Bora), com `subject` pré-preenchido para triagem na inbox:
- Footer (contacto geral, todas as páginas): `?subject=Contacto%20Site%20Bora`
- `parceiros.html` (2 CTAs): `?subject=Quero%20ser%20Parceiro%20Bora`
- `estafetas.html` (2 CTAs): `?subject=Quero%20ser%20Estafeta%20Bora`
- `privacidade.html` (RGPD/DPO, 2 ocorrências): `?subject=Privacidade%20RGPD`
- Verificado com `grep -r "boraapp.pt" *.html` → zero resultados.

**2. Screenshot real da Home no hero.** O mockup de design já existia — encontrado em `C:\Users\danil\Downloads\BORA Design System.zip` → ficheiro `Client Home.html` (design system completo do Bora, com todos os ecrãs de cliente/parceiro/estafeta, exportado em 28/05/2026). Não foi gerada nenhuma imagem por IA.

Processo: extraído o zip para um diretório temporário (mantendo `assets/` para os ícones que o mockup referencia), servido localmente via `python -m http.server`, renderizado com Playwright em viewport 390×844, e capturado um screenshot do elemento do telemóvel (excluindo o rótulo da página e a scrollbar do preview). Aplicada uma máscara de cantos arredondados via `sharp` para remover um pequeno "sliver" branco nos 4 cantos da captura. Resultado final: `bora-site/assets/img/screenshot-home.png` (390×844, ~74KB).

O hero do `index.html` foi atualizado — removida a moldura CSS de telemóvel (placeholder) e colocada a imagem real diretamente (`drop-shadow-2xl`), já que o mockup capturado já inclui a moldura do telemóvel desenhada.

Ficheiros temporários gerados durante o processo (no repo `bora_app`, fora do `bora-site`) foram todos apagados — `git status` no `bora_app` confirmado limpo, zero alterações a esse repo.

**Pendente:** nenhum. As duas tarefas desta missão foram concluídas sem bloqueios.

## 5. Notas técnicas

- Stack: HTML + Tailwind CSS (CDN, sem build) + JS vanilla + Lucide icons (CDN) + Google Fonts Inter.
- Zero alterações ao repo `bora-app-cloud`, ao Flutter, ao Supabase ou ao Stripe — site 100% isolado.
- Nenhuma comissão, split ou regra de negócio interna foi exposta no site público.
- Categorias do site mapeadas 1:1 às categorias reais do `client_home_screen.dart` (10 categorias, incluindo Beleza e Bora Motorista/TVDE).
- Imagens comprimidas com `sharp` (logo 1MB→230KB); QR code gerado com `npx qrcode` a apontar para a Play Store.

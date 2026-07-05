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

- **Screenshot/mockup da Home do app** para a secção Hero do `index.html` — não existe nenhum screenshot real no repo do app (`bora_app/`). Atualmente o hero mostra um placeholder textual dentro do contorno de telemóvel. Sugestão de prompt: "screenshot realista da home de uma app de entregas estilo Uber Eats/Glovo, tema verde, categorias em grid".
- Badge oficial da Play Store em **PT-PT** não está disponível publicamente na CDN da Google (só devolve 404); foi usado o badge oficial em inglês ("GET IT ON Google Play"), que é o mesmo usado por várias apps portuguesas. Se quiseres o badge PT-PT, tem de vir de um export manual do Google Play Console.

## 3. Placeholders a preencher

**Dados legais RGPD** (`privacidade.html`, `termos.html`):
- `[NOME LEGAL DA EMPRESA]`
- `[NIF]`
- `[MORADA]`
- `[NOME DO DPO]`

**Emails de contacto** (usados por convenção, confirmar ou substituir):
- `ola@boraapp.pt` (geral/footer)
- `parceiros@boraapp.pt` (página Parceiros)
- `estafetas@boraapp.pt` (página Estafetas)
- `privacidade@boraapp.pt` (RGPD/DPO)

**Redes sociais** — footer do `index.html` tem `href="#"` em Facebook/Instagram com comentário `<!-- TODO Danilo -->`; falta os links reais.

**Link Play Store** usado: `https://play.google.com/store/apps/details?id=pt.boraapp.bora` (conforme fornecido na missão — confirmar que o `id` da app é este quando publicada).

## 4. Como atualizar o site no futuro

```bash
cd bora-site
# editar ficheiros
git add -A && git commit -m "..." && git push
CLOUDFLARE_API_TOKEN=<token> wrangler pages deploy . --project-name=bora-site
```

## 5. Notas técnicas

- Stack: HTML + Tailwind CSS (CDN, sem build) + JS vanilla + Lucide icons (CDN) + Google Fonts Inter.
- Zero alterações ao repo `bora-app-cloud`, ao Flutter, ao Supabase ou ao Stripe — site 100% isolado.
- Nenhuma comissão, split ou regra de negócio interna foi exposta no site público.
- Categorias do site mapeadas 1:1 às categorias reais do `client_home_screen.dart` (10 categorias, incluindo Beleza e Bora Motorista/TVDE).
- Imagens comprimidas com `sharp` (logo 1MB→230KB); QR code gerado com `npx qrcode` a apontar para a Play Store.

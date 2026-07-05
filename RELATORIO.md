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

## SEO 2026-07-05 — schema local + reforço "Guarda" + performance

Objetivo: quem pesquisar "bora app guarda", "bora app", "entregas guarda", "delivery guarda" ou "reservar mesa guarda" encontra o site. "Bora" sozinho é uma palavra muito disputada (BORA blockchain, Bora Bora), por isso todo o trabalho ancorou em "Guarda, Portugal" + nomes de serviço.

**1. Schema.org (JSON-LD) — 9 blocos, todos validados com `JSON.parse` (zero erros):**
- `index.html`: mantidos `MobileApplication` e `Organization`, adicionado **`LocalBusiness`** (nome, descrição, área servida = cidade da Guarda, endereço só com `addressLocality`/`addressRegion`/`addressCountry` — **sem inventar `streetAddress`**, `priceRange`, imagem).
- `faq.html`: adicionado **`FAQPage`** com as 11 perguntas/respostas reais da página (texto das respostas com HTML removido, só texto simples, como o Schema.org recomenda).
- `parceiros.html`, `estafetas.html`, `faq.html`, `privacidade.html`, `termos.html`: adicionado **`BreadcrumbList`** (Início → página).
- Verificado em produção via `curl -sL` (importante: `curl -s` sem `-L` só apanha o redirect 308 do clean-URL do Cloudflare Pages, não o HTML real — usar sempre `-L` para validar conteúdo de páginas que não sejam a home).

**2. Reforço local nos textos:**
- Titles atualizados: `parceiros.html` → "Torna-te Parceiro Bora \| Vende para toda a Guarda"; `estafetas.html` → "Ganha Dinheiro como Estafeta Bora na Guarda"; `faq.html` → "Perguntas Frequentes \| Bora App Guarda". `index.html` mantido (já tinha "Guarda" no title).
- Meta descriptions reescritas (150–160 car.) mencionando Guarda + o serviço de cada página.
- H2 da secção de categorias no `index.html`: "O que podes fazer com o Bora" → **"O que podes fazer com o Bora em Guarda"**.
- Frase de rodapé nova em **todas as 6 páginas**: "Bora App — serviço de entregas, viagens e reservas na cidade da Guarda, Portugal."
- `alt` de 5 categorias no hero (Restaurantes, Supermercados, Farmácia, Enviar Encomenda, Viagens/TVDE) passaram a incluir "na Guarda" — as restantes 5 categorias mantiveram `alt` descritivo simples, para não parecer keyword-stuffing aos olhos do Google.

**3. Ficheiros técnicos:**
- `sitemap.xml`: `<lastmod>2026-07-05</lastmod>` + `<changefreq>` (weekly na home, monthly nas páginas de conversão, yearly nas legais) em todas as 6 URLs.
- `robots.txt`: confirmado `Allow: /` + `Sitemap:` (já estava correto).
- `canonical`: já existia em todas as páginas (confirmado, nenhuma em falta).
- Open Graph + Twitter Cards: **`privacidade.html` e `termos.html` não tinham OG** — adicionado (estavam em falta desde a v1, agora as 6 páginas têm og:type/title/description/image/url/locale=pt_PT).
- `manifest.json` criado (nome "Bora App", `theme_color` #16A34A, ícones) e linkado (`<link rel="manifest">` + `<meta name="theme-color">`) nas 6 páginas.

**4. Performance:**
- Todas as imagens de conteúdo têm `loading="lazy"`, exceto o screenshot do hero (`loading="eager"`, correto por estar acima da dobra) e os logos do header (também eager de propósito — estão sempre visíveis no primeiro ecrã, lazy-load neles seria contraproducente). Adicionado `loading="lazy"` aos logos do rodapé (estavam sem atributo).
- **Decisão consciente: NÃO foi adicionado `defer`/`async` ao script do Tailwind CDN.** O Tailwind Play CDN escreve estilos dinamicamente a partir do DOM logo no carregamento — adiar a sua execução causaria um "flash" visível de HTML sem estilo (pior para UX/performance percebida do que o pequeno custo de bloqueio atual). Se no futuro quiseres eliminar isto de vez, a solução correta é compilar Tailwind localmente (build step), não adiar o CDN.
- Tamanhos de imagem confirmados <300KB: maior ficheiro é `bora_logo.png` (230KB), `og-image.png` 92KB, `screenshot-home.png` 74KB — todos dentro do limite.

**Pendente:** nenhum bloqueio técnico. Os passos que faltam são só os que precisam de conta Google do Danilo — ver checklist abaixo.

### ✅ CHECKLIST MANUAL DANILO (contas Google — só tu podes fazer isto)

```
1. Google Search Console → search.google.com/search-console
   - Adicionar propriedade: https://bora-site.pages.dev
   - Verificar (método: prefixo de URL, verificação por meta tag ou DNS)
   - Submeter sitemap: sitemap.xml
   - "Inspecionar URL" da home → "Pedir indexação"

2. Google Business Profile → business.google.com
   - Criar perfil "Bora - Entregas Guarda"
   - Categoria: serviço de entrega / delivery
   - Área servida: Guarda
   - Adicionar site, email, logo
   (Isto é o que faz aparecer no topo com mapa em buscas locais)

3. Repetir "Pedir indexação" para as páginas principais no Search Console
   (index, parceiros, estafetas, faq).
```

## 5. Notas técnicas

- Stack: HTML + Tailwind CSS (CDN, sem build) + JS vanilla + Lucide icons (CDN) + Google Fonts Inter.
- Zero alterações ao repo `bora-app-cloud`, ao Flutter, ao Supabase ou ao Stripe — site 100% isolado.
- Nenhuma comissão, split ou regra de negócio interna foi exposta no site público.
- Categorias do site mapeadas 1:1 às categorias reais do `client_home_screen.dart` (10 categorias, incluindo Beleza e Bora Motorista/TVDE).
- Imagens comprimidas com `sharp` (logo 1MB→230KB); QR code gerado com `npx qrcode` a apontar para a Play Store.

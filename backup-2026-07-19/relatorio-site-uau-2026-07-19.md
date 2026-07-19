# Relatório — Homepage "uau" (2026-07-19)

**Repo:** `nilofulfarotuga-hue/bora-site` · branch `main` · **Deploy:** Cloudflare Pages (auto a cada push)
**Escopo:** só `index.html` + `assets/css/custom.css` + novo `assets/js/animations.js`. HTML/CSS/JS vanilla, sem framework novo, sem build step (mantém Tailwind Play CDN).

## O que mudou, secção a secção

1. **Hero (`#inicio`)**
   - Headline mais forte: *"Tudo o que a Guarda te dá, agora num só toque."*
   - Mockup de telemóvel: o `screenshot-home.png` real (já existente) agora fica dentro de uma moldura CSS (`.bora-phone-frame` — notch, cantos arredondados, sombra), com animação de flutuação suave (`@keyframes bora-float`) e parallax leve no scroll via GSAP/ScrollTrigger (`gsap.to('.bora-phone-frame', {y:-40, scrub:true})`).
   - Duas manchas (`bora-blob`) desfocadas no fundo do hero, com o próprio parallax (scrub) em velocidade diferente para dar profundidade.
   - Botões "Baixar a App" / "Aponta a câmara" mantidos como estavam.
   - `prefers-reduced-motion: reduce` desativa a flutuação e as animações GSAP (acessibilidade).

2. **Contadores animados (count-up)** — novos, na base do hero:
   - **11** categorias num só app — contagem real dos 11 cartões já existentes na secção Categorias (Restaurantes, Supermercados, Farmácia, Viagens, Encomenda, Compras, Reservar Mesa, Favores, Lojas, Beleza, Limpeza).
   - **1** cidade servida — a Guarda (facto já presente no schema.org `areaServed` e em todo o copy).
   - **2** formas de pagamento seguras (MB Way e cartão — já mencionado na secção "Porquê o Bora").
   - Todos os 3 números são **factos verificáveis na própria página**, não inventados. Não incluí métricas de "clientes"/"pedidos entregues"/"parceiros" porque não existe nenhum número real dessas na base de código nem no site — **TODO_DANILO_CONFIRMAR** se quiseres esse tipo de contador, preciso do valor real (ou de uma fonte tipo Supabase) para não inventar.
   - Implementado via GSAP (`gsap.to` a animar um valor numérico) + `ScrollTrigger` (`once:true`, dispara ao entrar em viewport).

3. **Categorias (`#categorias`)**
   - Grid mantido (11 cartões, inalterado no conteúdo/imagens).
   - Hover reforçado: além do lift já existente, o ícone agora dá um `scale(1.08)` suave (`.bora-card:hover img`).
   - Entrada em scroll: fade/slide-in com stagger (`data-reveal-stagger` no grid, `data-reveal` no título) via GSAP ScrollTrigger.

4. **Porquê o Bora + Como Funciona**
   - Mesmo conteúdo, agora com fade/slide-in em scroll (título + grid com stagger). Nada de texto ou imagem alterado.

5. **Nova secção "Não tens Android?"** (`#web-em-breve`), inserida entre "Como Funciona" e "Download"
   - Cartão em gradiente verde, badge "Em breve", texto anunciando que no futuro será possível pedir pelo site.
   - **Sem funcionalidade real** — o botão "Disponível brevemente" está desativado (`cursor-not-allowed`, sem `href`), conforme pedido (a loja funcional é ordem futura separada).

6. **Mantido sem regressão**
   - QR code Play Store (secção Download) — inalterado.
   - Botão/link `mailto:boraappbora@gmail.com` no rodapé — inalterado.
   - Screenshot real da Home no hero — mesma imagem, agora dentro da moldura de telemóvel.
   - Design tokens: verde `#16A34A`, laranja `#F97316`, fonte Inter — todos mantidos (nada novo introduzido).
   - Copy 100% PT-PT (revisto o texto novo).

## Ficheiros tocados
- `index.html` — hero, contadores, atributos `data-reveal`/`data-reveal-stagger`, nova secção, scripts GSAP (cdnjs) + `animations.js`.
- `assets/css/custom.css` — moldura de telemóvel, manchas de fundo, hover de ícone, keyframe de flutuação, guarda `prefers-reduced-motion`.
- `assets/js/animations.js` (novo) — toda a lógica de scroll-reveal, parallax e count-up. Fica "silencioso" (`if (!window.gsap...) return`) se o GSAP não carregar, para nunca partir a página.

## Verificação feita
- **Sintaxe:** balanceamento de tags do `index.html` validado com um script Node ad-hoc (0 erros — script depois apagado); `node --check` correu limpo em `assets/js/animations.js` e `assets/js/main.js`.
- **Revisão manual** dos ficheiros alterados (sem build step, por isso a verificação é visual/manual em vez de linter automático).
- Não corri um browser real neste ambiente (headless, sem GUI) — recomendo o Danilo dar uma vista de olhos rápida em `https://bora-site.pages.dev/` depois do deploy, sobretudo o hero em mobile.

## Deploy Cloudflare Pages
- **Commit feito localmente** (`979a429`, branch `main`), mas o **`git push` FALHOU** neste ambiente headless:
  - HTTPS: `wincredman` (Git Credential Manager) devolve `fatal: Unable to persist credentials with the 'wincredman' credential store` — o gestor de credenciais do Windows não funciona em sessão não-interativa headless.
  - SSH: a deploy key existente (`id_ed25519_bora_deploy`, usada para `bora-app-cloud`) tem acesso de **leitura** a este repo (`bora-site`) mas GitHub recusa a escrita: `ERROR: Permission to nilofulfarotuga-hue/bora-site.git denied to deploy key`.
  - **⚠️ TODO_DANILO_CONFIRMAR / AÇÃO NECESSÁRIA:** por favor corre `git pull` e depois `git push origin main` a partir da tua sessão normal (já autenticada nesta máquina, como mostram os commits anteriores `22c3724`/`87de103`), ou configura uma deploy key com permissão de escrita para este repo se quiseres que o executor autónomo publique sozinho no futuro.
- Segundo o `RELATORIO_SITE_UPDATE.md` anterior (2026-07-06), o projeto Pages `bora-site` era **Direct Upload** (não ligado ao Git) — ou seja, mesmo depois do `git push` manual, pode ser preciso `wrangler pages deploy` (conta `nilofulfarotuga@gmail.com`, já autenticada na máquina segundo o relatório anterior) para publicar de facto.
- **TODO_DANILO_CONFIRMAR:** verificar se o projeto Pages entretanto passou a estar ligado ao GitHub (deploy automático por push) ou se continua Direct Upload — se continuar Direct Upload, correr:
  `npx wrangler pages deploy . --project-name=bora-site --branch=main` (excluindo os `.md` da pasta, como da última vez, ou aceitando que ficam publicados — são só documentação, sem segredos).

## TODOs pendentes (não resolvidos nesta tarefa, fora do pedido)
- `TODO_DANILO_CONFIRMAR`: números reais de clientes/parceiros/pedidos, se quiseres contadores desse tipo.
- `TODO_DANILO_CONFIRMAR`: confirmar mecanismo de deploy atual (Git-linked vs Direct Upload) do projeto Cloudflare Pages.
- Pendências já registadas no relatório anterior (placeholders RGPD em `termos.html`/`privacidade.html`, links Facebook/Instagram no rodapé) — não tocados, fora do escopo desta tarefa.

# Relatório — Homepage cinematográfica scroll-driven

**Data:** 2026-07-19
**Repo:** `nilofulfarotuga-hue/bora-site` (branch `main`)
**Site:** https://bora-site.pages.dev
**Executado por:** Claude Code (Opus) — MODO PROTECÇÃO TOTAL, ponta-a-ponta, sem intervenção humana.

---

## 1. Objetivo

Transformar a homepage numa experiência **cinematográfica nível "site premiado"** (estilo
Apple/Framer): o scroll controla a história visualmente, mantendo o site rápido, leve,
SEO-são e perfeito no mobile. Custo ~0€, só recursos gratuitos.

---

## 2. Plano usado — **PLANO A** (imagens cinematográficas via nano-banana / Gemini)

| Plano | Estado | Porquê |
|---|---|---|
| **A — imagens IA (nano-banana)** | ✅ **USADO** | MCP `nano-banana` já configurado (chave global). Modelo `pro` (gemini-3-pro-image-preview), 16:9. Resultados fotorrealistas de altíssima qualidade. |
| B — vídeo IA (Veo/Gemini) | ⏭️ **Ignorado** | A geração de vídeo (Veo) na API Gemini é **paga/faturada** — não free tier. Regra dura "se custar dinheiro → ignorar plano B sem insistir". Não se gastou uma chamada paga a testar. |
| C — visuais por código (CSS/SVG) | ➖ Não necessário | O Plano A correu na perfeição. (O código já degrada em pilha estática elegante quando não há JS / há `reduced-motion` — parte da robustez, não substituição de imagem.) |

### Cenas geradas (9 imagens finais, 10 gerações)

| # | Ficheiro | Cena | Uso |
|---|---|---|---|
| C1 | `c1_guarda_dawn.webp` | Cidade de granito na serra ao amanhecer (torre gótica, névoa) | Capítulo 1 + preload |
| C2 | `c2_estafeta_rua.webp` | Estafeta de mota, baú verde, rua de pedra | Capítulo 2 |
| C3 | `c3_mercado_sacos.webp` | Sacos de mercado com produtos frescos | Capítulo 3 |
| C4 | `c4_tvde_noite.webp` | Carro à noite, asfalto molhado, reflexos verde/laranja | Capítulo 4 *(regenerado 1× para remover emblema de marca)* |
| C5 | `c5_limpeza_sala.webp` | Sala impecável, luz de janela | Capítulo 5 |
| C6 | `c6_reserva_mesa.webp` | Mesa de restaurante posta, velas | Capítulo 6 |
| C7 | `c7_maos_telemovel.webp` | Mãos com telemóvel (ecrã escuro), cidade ao fundo | Capítulo 7 + CTA |
| C8 | `c8_granito_verde.webp` | Textura granito com fenda de luz verde | Divisória parallax "Feito na Guarda" |
| C9 | `c9_cidade_noite.webp` | Vista aérea da cidade à noite | Fundo do app-showcase |

- **Originais** (PNG) em `assets/cinema/src/` (6,9 MB); **WebP q72** (máx. 1920px) em `assets/cinema/` (**664 KB no total**), convertidos com **ffmpeg/libwebp**.
- **Regras respeitadas:** sem texto, sem logótipos, sem marcas reais, sem rostos reconhecíveis; paleta com acentos verde `#16A34A` e laranja `#F97316` como luz/detalhe.

### Custo real
- **10 gerações** de imagem no modelo Gemini `pro`. Uso de free-tier / valor de cêntimos no projeto `boraapp-d2bea`. **Sem custo material.** (Confirmar no billing se se pretender rigor contabilístico.)
- **Higgsfield: NÃO usado** (proibido — pago).

---

## 3. O que mudou, secção a secção

- **HERO → CINEMA (7 capítulos):** o antigo hero (gradiente + mockup) deu lugar a um
  **palco fixo (sticky)** com as cenas C1→C7 em crossfade controlado pelo scroll
  (GSAP ScrollTrigger, scrub). Câmara virtual: **Ken Burns** (zoom 1.05→1.16 por cena),
  crossfade, **legendas que entram palavra a palavra** (stagger), **dots de capítulo**
  (desktop) e sugestão "Desliza".
  - Copy: "A Guarda tem tudo perto." → "Entregas em minutos." → "O mercado até à tua
    porta." → "Viagens com motoristas da cidade." → "A tua casa impecável." → "Reserva
    mesa. Marca o teu corte." → **"Bora. Uma app, a cidade inteira."** + botões Play Store.
- **APP SHOWCASE (novo):** banda com o **ecrã REAL da app** (`screenshot-home.png`,
  preservado) em mockup de telemóvel + os 3 contadores animados (11 categorias / 1 cidade /
  2 pagamentos), sobre fundo cinematográfico (C9). *(Decisão: em vez de sobrepor o
  screenshot ao telemóvel inclinado da foto C7 — o que ficaria torto —, o ecrã real
  aparece num mockup nítido nesta banda. Nunca se gerou UI falsa.)*
- **DIVISÓRIA "Feito na Guarda":** banda com textura de granito+luz verde (C8) em
  **parallax** leve.
- **CATEGORIAS:** mantidas as 11 (incl. **Limpeza** — pendência antiga já resolvida).
- **PORQUÊ O BORA:** mantida (4 pontos reais, ilustrações 3D existentes).
- **COMO FUNCIONA / WEB EM BREVE / DOWNLOAD (QR + badge) / CTA duplo / FOOTER:** mantidos.
  Ícones sociais Facebook/Instagram passaram a **SVG inline** (os do lucide foram
  descontinuados e davam warning + ícone vazio).

### Preservado sem exceção (rule 3)
- ✅ Meta `google-site-verification` **byte-a-byte intacta** (confirmado no DOM).
- ✅ QR Play Store · ✅ badge Google Play · ✅ `mailto:boraappbora@gmail.com`
- ✅ Screenshot real da Home · ✅ `sitemap.xml`, `robots.txt`
- ✅ Schema `MobileApplication` + `Organization` + `LocalBusiness` (intactos)
- ✅ Copy 100% PT-PT · tokens verde/laranja · fonte Inter

---

## 4. Performance / Mobile / Acessibilidade

- **Peso do 1º load ≈ 1,3 MB** (alvo < 3,5 MB) — **✅ com folga**.
  - Cinema WebP: só **~64 KB** carregam no topo (C1); C2–C7 são backgrounds fora-de-ecrã
    que só carregam ao aproximar (lazy natural). Preload dedicado só do C1 (`fetchpriority=high`).
  - O maior peso (~1,17 MB) são os **ícones PNG de categoria** (legado). Ver TODO abaixo.
- **`prefers-reduced-motion`:** desliga o palco cinematográfico → **pilha estática elegante**
  (todas as cenas empilhadas, legíveis). Validado.
- **Mobile (390px):** capítulos mais curtos (640vh), dots ocultos, **sem scroll horizontal**,
  título a 36px legível. Validado.
- **A11y:** `<h1>` (sr-only) na página, `alt` nas imagens de conteúdo, overlay para contraste
  AA do texto sobre imagem, **foco visível** nos botões, `scroll-padding-top` para as âncoras
  não ficarem escondidas sob o header.

---

## 5. Teste real em navegador (Chrome via Playwright)

| Verificação | Resultado |
|---|---|
| Consola | **0 erros**, 1 warning (aviso do Tailwind Play CDN — inofensivo/esperado) |
| Cenas carregam | ✅ C1–C7 (crossfade 1-a-1 confirmado por opacidades) |
| Scrub nos 2 sentidos | ✅ (ScrollTrigger scrub, estados verificados em vários pontos) |
| Capítulo final + CTA | ✅ visível e clicável |
| Secções abaixo | ✅ showcase (ecrã real), 11 categorias, QR, contadores 11/1/2 |
| Âncoras | ✅ `#categorias` aterra a 72px (header 64px — sem sobreposição) |
| Mobile 390px | ✅ sem overflow horizontal |
| Reduced-motion / no-JS | ✅ fallback estático (7 cenas visíveis, empilhadas) |

Provas visuais em **`docs/preview/`** (01 hero desktop, 02 viagens C4, 03 categorias, 04 hero mobile).

---

## 6. Stack técnica (sem build step)

HTML/CSS/JS vanilla + **Tailwind Play CDN** + **GSAP core + ScrollTrigger** (cdnjs) + Lucide + Inter.
Novo: `assets/js/cinema.js` (motor do palco), CSS do cinema em `assets/css/custom.css`.
**Sem Lenis** (decisão: scrub nativo bem afinado é mais leve e robusto no touch/mobile do que
Lenis + ScrollTrigger).

---

## 7. Estado do deploy

- Commits por fase (backup → imagens → build → perf/a11y → relatório) e **`git push origin main`**.
- **Cloudflare Pages** faz deploy automático no push.
- ⚠️ **Se o deploy não aparecer:** verificar o `CLOUDFLARE_API_TOKEN` / ligação do projeto
  `bora-site` na conta Nilofulfarotuga. O push fica feito de qualquer forma.

---

## 8. TODOs

- `TODO_DANILO_CONFIRMAR` — links reais das redes sociais (Facebook/Instagram) no footer.
- `TODO_DANILO_CONFIRMAR` — email de contacto oficial (atual: `boraappbora@gmail.com`).
- **(Opcional, perf)** converter os 11 ícones PNG de categoria + `screenshot-home.png` para
  WebP — reduziria o 1º load de ~1,3 MB para bem abaixo de 700 KB. (Fora do âmbito desta
  missão; o alvo de peso já está cumprido com folga.)
- **(Opcional)** migrar o Tailwind Play CDN para CLI/PostCSS em produção (remove o warning de
  consola). Mantido CDN por exigência de "sem build step".

---

*Backup completo do site pré-redesign em `backup-2026-07-19/`.*

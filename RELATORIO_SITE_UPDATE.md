# Relatório — Atualização do Site Bora (Limpeza + "Porquê o Bora")

**Data:** 2026-07-06
**Repo:** `nilofulfarotuga-hue/bora-site` · **Deploy alvo:** Cloudflare Pages · projeto `bora-site` · conta `Nilofulfarotuga@gmail.com` (`2cd0212b0f5e5c8284aa227f629c050a`)

---

## 1. Imagens geradas (Nano-Banana / Gemini `pro`)

Todas em estilo 3D "clay" fofo, coerentes com a família de ilustrações do site (verde #16A34A + laranja #F97316). Geradas em 1:1, redimensionadas a 512×512 e convertidas para **WebP** otimizado. Guardadas em `assets/img/`.

| Ficheiro | Uso | Descrição | Peso |
|---|---|---|---|
| `cat_limpeza.webp` | Categoria Limpeza | Spray sorridente + esponja + balde + brilhos, num "squircle" verde (mesma família do cartão Beleza/Motorista) | 15.3 KB |
| `why_app_unico.webp` | Porquê — Tudo num só app | Telemóvel com bolhas de serviços a convergir (comida, carro, spray, reserva) | 15.2 KB |
| `why_suporte.webp` | Porquê — Suporte humano | Pessoa com headset + balão de conversa com coração | 10.4 KB |
| `why_viagens.webp` | Porquê — Menos espera | Carro fofo + relógio + relâmpago | 13.5 KB |
| `why_guarda.webp` | Porquê — Feito na Guarda | Colina/serra verde com pin de localização laranja | 6.6 KB |

**Total: ~61 KB** para as 5 imagens (carregamento leve). Usei ícones existentes (`cat_beleza`, `cat_restaurantes`, `cat_supermercados`) como `reference_images` para o ícone da Limpeza casar com a família visual.

## 2. Alterações no `index.html`

1. **Nova categoria "Limpeza"** — 11.º cartão na grelha de categorias, mesmo padrão/estilo/hover dos outros. Texto: *"Profissionais de confiança para limpeza doméstica, em tua casa."*
2. **Nova secção "Porquê escolher o Bora?"** — inserida **logo a seguir às categorias** (no meio da inicial), banda verde-claro (`bg-[#F0FDF4]`), 4 cartões brancos com as ilustrações 3D:
   - **Tudo num só app** (super-app: comida, mercado, farmácia, viagens, limpeza, reservas, favores — em vez de Uber + Glovo + apps à parte).
   - **Suporte humano e local** (pessoa real da Guarda, rápido, sem robôs — cliente/parceiro/estafeta).
   - **Viagens com menos espera** (motoristas da cidade → carro chega mais depressa).
   - **Feito na Guarda, para a Guarda** (projeto local).
   - Abaixo: 2 selos de confiança reais (*Apoia o comércio local* · *Pagamentos seguros — MB Way e cartão*), recuperados da secção antiga.
3. **Removida a secção "Porquê o Bora?" antiga** (era simples, 4 ícones, ficava depois do download) — para não duplicar o título. O conteúdo real dela foi preservado nos selos acima.
4. **Reforço do super-app** — subtítulo do hero passou a *"…limpeza, reservas e favores na Guarda — tudo num só app."* + subtítulo da nova secção descreve o super-app local.
5. **SEO / Schema** — adicionado "limpeza doméstica" à `meta description`, `og:description` e à `description` do Schema.org `LocalBusiness` (sem quebrar validação). Adicionada "Limpeza" à lista de categorias do rodapé.

**Não tocado (conforme instruções):** meta de verificação do Google Search Console (linha 5), sitemap.xml, robots.txt, restantes páginas, emails de contacto.

## 3. Validação visual

Renderizado localmente (servidor estático + Playwright):
- **Desktop (1280px):** grelha com 11 categorias (Limpeza integra-se perfeitamente); secção "Porquê" com as 4 ilustrações + selos. 0 erros de consola.
- **Mobile (390px):** grelha 2 colunas; cartões "Porquê" empilhados 1 por linha, ilustrações a renderizar, tudo legível e bonito. ✅

## 4. Deploy — ⏳ PENDENTE (falta credencial)

O deploy **não pôde ser executado autonomamente**: o `wrangler` não está autenticado e não existe `CLOUDFLARE_API_TOKEN` no ambiente. Não é possível inventar/expor o segredo.

**Para publicar (corre TU, num terminal teu — NÃO com `!` aqui, para o token não voltar a ficar exposto no chat):**

```powershell
$env:CLOUDFLARE_API_TOKEN="<TOKEN_NOVO_DA_CONTA_NILO>"
npx --yes wrangler pages deploy "C:\Users\danil\Desktop\bora-site" --project-name=bora-site --branch=main
```

Usa um **token novo** (custom "Editar Cloudflare Workers" na conta Nilo) — isto também trata do item de segurança abaixo (rotação do token antigo exposto).

Depois do deploy, confirmar em: **https://bora-site.pages.dev/**

## 5. Pendentes registados

| Item | Estado |
|---|---|
| Rodar/apagar o token `cfut_` exposto em chat antigo | ⏳ Só no dashboard Cloudflare (Danilo). Recomendado: gerar token novo para o deploy acima → o antigo deixa de servir. Nada exposto no repo. |
| Placeholders RGPD `[NOME LEGAL DA EMPRESA]` · `[NIF]` · `[MORADA]` | ⏳ Em `termos.html` (L93, L123) e `privacidade.html` (L93). Faltam os dados legais reais. (Sem `[DPO]` no site.) |
| Links Facebook/Instagram no rodapé | ⏳ Continuam `href="#"` (TODO). Só preencher quando existirem URLs reais. |

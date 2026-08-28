# Sabores do Brasil — Keli Barbosa

**São duas coisas separadas, dois links. Não voltar a juntar.**

| | Link | O que é |
|---|---|---|
| 1 | https://saboresdobrasil.boraguarda.com/ | O site dela. Montra. Sem demo lá dentro. |
| 2 | https://festas.boraguarda.com/ | A demo da categoria Festas dentro da app. |

- **Loja na base:** `restaurants.id = 'sabores-brasil-guarda'` (`coming_soon = true`)
- **Projectos Cloudflare Pages:** `sabores-do-brasil` e `demo-festas` — upload directo por
  wrangler, sem ligação ao git.
- Fonte da demo em `../demo-festas/`.

## Ligar a loja quando a Keli disser sim

Uma linha, no topo de **cada** um dos dois `index.html` (e do `fonte/template_site.html`):

```js
var LOJA_ATIVA = false;   // -> true
```

`false` → o site diz "Cria conta e fica a par" e a demo trava no pagamento.
`true` → o site diz "Encomendar agora" e a demo deixa passar. Recompilar e republicar.

## Refazer o site

```bash
python fonte/prep_site.py    # imagens -> media/*.webp + assets_site.json
python fonte/build_site.py   # injecta o QR e o logo Bora -> index.html + verificações
```

## Publicar

```bash
npx wrangler pages deploy "C:/Users/danil/Desktop/sabores-do-brasil" --project-name sabores-do-brasil --branch main
npx wrangler pages deploy "C:/Users/danil/Desktop/demo-festas"      --project-name demo-festas      --branch main
```

**Caminho absoluto, sempre.** Com `.` publica-se a pasta onde a shell estiver — foi assim que
a pasta de rascunho foi ao ar durante uns minutos a 23/08/2026. E depois de publicar, confirmar
o **conteúdo** de caminhos que não deviam existir: o Cloudflare Pages devolve 200 com o
`index.html` em rotas inexistentes, por isso o código HTTP sozinho não prova nada.

## O vídeo

`media/sabores.mp4` (5,2 MB, H.264, 720×1280, 58 s) é a versão comprimida do vídeo que a Keli
mandou. O original está em `C:\Users\danil\Downloads`. O `sabores.webm` **não** está no git
(é regenerável); se for preciso:

```bash
ffmpeg -i original.mp4 -c:v libvpx-vp9 -crf 40 -b:v 0 -row-mt 1 -cpu-used 5 \
       -vf scale=720:-2 -c:a libopus -b:a 56k media/sabores.webm
```

## As imagens

**Fotos reais dela** (`fonte/tratadas/`) — a bancada de granito e o monte de salgados, tirados
do vídeo. No site levam etiqueta amarela "foto real".

**Ilustrativas** (`fonte/geradas/`) — bolo com calda, pudim, mesa de doces, salgado partido e
salgados dourados. Vieram das partes **geradas por IA do próprio vídeo dela**, recortadas e
tratadas. No site levam etiqueta "ilustrativa".

Porquê do vídeo e não geradas de novo: as três APIs de geração estavam sem crédito no dia
(Higgsfield sem créditos, Gemini com a quota diária do plano grátis esgotada, OpenAI sem
créditos). Se algum dia houver crédito, o `fonte/gen_fotos.py` (Gemini) e o `fonte/gen_openai.py`
já têm os prompts escritos e prontos a correr.

## A demo (link 2)

O **ecrã inicial é uma captura real** da app web em viewport de telemóvel — a categoria Festas
está composta por cima, no 12.º lugar vazio da grelha. Os restantes ecrãs estão desenhados com o
mesmo sistema visual, a partir das capturas em `../demo-festas/fonte/ecras-reais/`.

Não foi possível capturar com `adb`: no dia não havia telemóvel ligado por USB (o Windows também
não via nenhum dispositivo Android). O plano B — app web em viewport de telemóvel — está previsto
no próprio pedido.

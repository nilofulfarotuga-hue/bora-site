# Sabores do Brasil — Keli Barbosa

Site-presente + demonstração da categoria **Festas**, feito para a Keli entrar na Bora.

- **No ar:** https://sabores-do-brasil.pages.dev/
- **Projeto Cloudflare Pages:** `sabores-do-brasil` (upload directo por wrangler, sem ligação ao git)
- **Loja na base:** `restaurants.id = 'sabores-brasil-guarda'` (`coming_soon = true`)

## Porque é que isto vive aqui

O `beunique.html` e o `sabores-de-casa.html` já desapareceram do PC uma vez cada,
e travaram publicações durante semanas. As pastas soltas `Desktop\mr-kebab` e
`Desktop\ouro-e-prata` continuam fora do git — esta não fica.

`sites-parceiros/` **não** entra no deploy do bora-site: o `deploy-cloudflare.sh`
monta a pasta a publicar por lista de permissões (só `loja/`, `dados/`, `assets/`
e alguns ficheiros da raiz). Fica versionado sem ir para o ar.

## Ligar a loja quando a Keli disser sim

Uma linha só, no topo do `index.html` (e do `fonte/template.html`):

```js
var LOJA_ATIVA = false;   // -> true
```

`false` mostra "Criar conta e ficar a par — a Sabores do Brasil abre em breve".
`true` passa a "Encomendar agora". Depois é recompilar e voltar a publicar.

## Refazer a página

O `index.html` é auto-contido (imagens em base64, um ficheiro só).

```bash
python fonte/mkassets.py   # trata imagens + QR (correcao M) -> assets_b64.json
python fonte/build.py      # injecta no template -> index.html
```

O `fonte/extract.py` volta a tirar fotogramas do vídeo original da Keli
(`WhatsApp Video 2026-08-23 at 16.16.07.mp4`) e o `fonte/treat.py` trata-os.
As imagens já tratadas estão em `fonte/tratadas/`, por isso os dois primeiros
passos só são precisos se houver material novo.

## Publicar

```bash
npx wrangler pages deploy "C:/Users/danil/Desktop/sabores-do-brasil" --project-name sabores-do-brasil --branch main
```

**Caminho absoluto, sempre.** Com `.` publica-se a pasta onde a shell estiver —
foi assim que os ficheiros de trabalho foram parar ao ar durante uns minutos
a 23/08/2026. A pasta a publicar só pode ter o `index.html` lá dentro.

## As fotos

Só material real dela. O vídeo que ela mandou é, na maior parte, publicidade
gerada por IA (pessoas de camisola do Brasil, bolo com calda impossível, e o
logótipo na caixa sai ilegível). Nada disso foi usado.

As únicas cenas verdadeiras são a bancada de granito com os tabuleiros e o monte
de salgados — desse segundo teve de se cortar a faixa onde o telefone dela está
queimado por cima. Por isso só 2 dos 6 produtos têm foto na base; os outros
ficam com `needs_photo = true` até ela mandar fotografias.

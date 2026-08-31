# Design system — turismo rural / boutique de serra
> Extraído a 2026-08-31 das capturas reais em `referencias/`:
> `turismo-casasaolourenco-1` (Casa de São Lourenço, Burel Panorama Hotel,
> Manteigas — o topo da própria Serra da Estrela), `turismo-barrocal-2`
> (São Lourenço do Barrocal, Alentejo, Design Hotels) e
> `turismo-babylonstoren-3` (Babylonstoren, África do Sul — a quinta-hotel
> mais famosa do mundo). Tokens medidos por computed style + paleta por
> quantização das capturas (ficheiros `*-tokens.json`).

## 1. Cores (4–6, com papel)

Dois caminhos provados; escolher UM por site:

**Caminho escuro imersivo (Casa de São Lourenço)**
- `--noite: #1C1C1C` — fundo base
- `--carvao-azulado: #182D39` — fundo secundário / cartões
- `--nevoa: #CACECD` — texto sobre escuro
- `--branco: #FFFFFF` — títulos sobre foto
- acento discreto tirado do material do cliente (madeira, burel, granito)

**Caminho claro de quinta (Barrocal + Babylonstoren)**
- `--osso: #F5F4F3` — fundo base
- `--tinta: #212123` — texto principal
- `--cinza-quente: #707070` — texto secundário
- `--salva: #8B8A68` — acento vegetal (barras, painéis, hovers)
- `--azeitona: #3B3A05` — títulos/acentos profundos
- `--ocre: #83652C` — detalhe raro (selos, filetes)

## 2. Tipografia

- **Display serifada leve**: 57–80px no herói, peso 300–400, tracking
  ligeiramente positivo (0.5–0.8px). Medidas reais: Domaine Display 72px/400
  (CSL), Chronicle Display 80px/300 (Barrocal), Cormorant Garamond (Babylonstoren).
  Equivalentes Google Fonts: **Cormorant Garamond** ou **Playfair Display** leve.
- **Corpo sans discreto**: 16–17px, cor rebaixada (#707070 sobre claro,
  #CACECD sobre escuro), line-height ~1.7. Equivalente: **Inter** 400.
- **Utilitária caps**: 11–13px, MAIÚSCULAS, letter-spacing 1.5–2px, para nav,
  etiquetas e botões. Medido: `tt:uppercase ls:2px` no Barrocal.
- Itálico serifado só para frases curtas de voz humana (anúncio do Babylonstoren).

## 3. Escala de espaçamentos

Régua 8/16/24/40/64/96/140. Secções respiram 96–140px vertical. O herói é
100vh ou quase. Nada encostado: mínimo 24px entre blocos relacionados.

## 4. Raio de cantos

**0px. Sempre.** Nos três sites de topo não há um único canto arredondado.
Pílulas e cartões redondos leem-se como template barato neste nicho.

## 5. Sombras

Quase nenhumas. Profundidade vem da fotografia e de painéis de cor cheia
(sage panels do Babylonstoren). Se precisar: `0 20px 60px -30px rgba(0,0,0,.35)`
numa única peça flutuante, nunca em cartões repetidos.

## 6. Botões

Contornados, quadrados, caps espaçadas: `border:1px solid`, fundo transparente,
`letter-spacing:.18em`, padding 14px 28px. Hover: fundo enche devagar (300ms)
com a cor do texto a inverter. UM botão cheio no máximo por ecrã (o RESERVAR).
Reserva SEMPRE presente: botão fixo no topo (CSL), aba vertical BOOK na borda
direita (Barrocal), ou painel MAKE A BOOKING (Babylonstoren).

## 7. Grelha

Conteúdo de texto a max-width 680–760px centrado; galerias e fotos a sangrar
até à borda (full-bleed). 12 colunas implícitas; quebra única a ~768px.
Nav: logótipo central com links dos dois lados (Barrocal) ou lockup central
sobre o herói (CSL). EN|PT minúsculo no canto superior.

## 8. Estilo das fotos

Fotografia É o site. Full-bleed, sem moldura, sem raio. Herói = vídeo
cinematográfico ou foto aérea/paisagem com gradiente escuro subtil por cima
para segurar o texto branco. Interiores com luz natural. Pessoas só de longe
ou de costas. Nada de banco de imagens: a textura local (granito, burel,
pomar) é a identidade.

## 9. Tipo de movimento

Contido e caro: crossfade lento no herói (6–8s), revelação ao scroll suave
(600ms, uma vez), zoom lentíssimo em fotos (scale 1→1.06 em 12s). Nenhum
elemento salta. O movimento nunca esconde informação — público inclui
hóspede mais velho.

## Blocos que estes três têm e a maquete tem de ter

herói fotográfico total → frase de identidade → quartos/casas com fotos
grandes → a experiência (mesa, animais, rio) → prova social real → mapa e
como chegar → reserva direta sempre à mão → rodapé completo com selos legais.

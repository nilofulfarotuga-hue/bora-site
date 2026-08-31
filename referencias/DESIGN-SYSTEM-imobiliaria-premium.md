# Design system — imobiliária de alto padrão (comprador estrangeiro)
> Extraído a 2026-08-31 das capturas reais em `referencias/`:
> `imobiliaria-portadafrente-1` (Porta da Frente Christie's, Lisboa),
> `imobiliaria-fineandcountry-2` (Fine & Country Portugal) e
> `imobiliaria-engelvoelkers-3` (Engel & Völkers). Tokens medidos por
> computed style + paleta por quantização das capturas (`*-tokens.json`).

## 1. Cores (4–6, com papel)

- `--branco: #FFFFFF` — fundo dominante; o luxo aqui é espaço em branco
- `--grafite: #111418` — texto principal (Porta da Frente mede rgb(17,24,28))
- `--pedra: #6B6E73` — texto secundário
- `--acento-profundo`: UMA cor de marca funda usada com avareza —
  bordeaux Christie's (#7A1F2B) ou champanhe F&C (#9E8C72). Para o
  Imoaugusto: derivar da cor do logótipo dele, nunca inventar.
- `--areia: #D7C7B1` — superfícies suaves de apoio (F&C)
- `--linha: #E6E4E0` — filetes e separadores

## 2. Tipografia

- **Display serifada de alto contraste**: 48–64px, peso 300–400. Medido:
  Aleo 57px/300 (PdF), Didot (F&C). Equivalente Google Fonts:
  **Playfair Display** 400 ou **Cormorant** 500.
- **Corpo sans geométrico**: **Montserrat** 15–16px (medido nos dois),
  line-height 1.65; pesos 400/500, títulos de secção 600.
- **Utilitária caps**: 11–12px, MAIÚSCULAS, ls 1.5–2px — nav, etiquetas de
  cartão, botões.
- Números (preços, contagens) na serifada — dá peso institucional.

## 3. Escala de espaçamentos

8/16/24/32/48/72/120. Nav alta (~100px) e arejada. Herói com muito ar:
headline isolada 120px acima/abaixo. Cartões de imóvel com gutters 24–32px.

## 4. Raio de cantos

**0px em tudo** (medido: radius 0 nos dois). Inputs e botões quadrados.
É a assinatura do segmento alto — arredondar é descer de prateleira.

## 5. Sombras

Nenhuma decorativa. Cartões separam-se por espaço e filete `--linha`.
Única exceção: a barra de pesquisa flutuante sobre o herói pode ter
`0 12px 40px -20px rgba(0,0,0,.25)`.

## 6. Botões

Dois tipos, os dois quadrados e caps espaçadas:
- **Cheio no acento** (COMPRAR/ARRENDAR da F&C em champanhe; tabs bordeaux
  da PdF) — só para a ação principal.
- **Contornado fino** ("Vender Imóvel" da PdF, "AVALIE A MINHA PROPRIEDADE"
  da F&C) — para a segunda ação. Hover: enche com o acento.

## 7. Grelha

Nav branca fixa que ganha sombra ténue ao descer. Herói full-bleed com foto
aérea/lifestyle OU headline em branco puro (F&C). **A pesquisa é o herói:**
barra larga central com separadores Comprar|Arrendar (+ Investir), select de
zona, campo de texto e botão no acento. Cartões de imóvel: 3 colunas a 1440,
foto 3:2 em cima, dados por baixo, quebra para 1 coluna no telemóvel.

## 8. Estilo das fotos

Aéreas e de lifestyle no herói (Cascais da PdF, praia dourada da F&C) —
vendem o SÍTIO antes da casa. Fichas: fotos grandes 3:2, luz natural,
sem molduras nem raio. Retratos da equipa: fundo neutro consistente,
enquadramento igual para todos (os do site do cliente).

## 9. Tipo de movimento

Mínimo e sóbrio: fade suave ao scroll, hover que aproxima a foto do cartão
(scale 1.04) ou troca para a segunda foto, sublinhados que deslizam na nav.
Zero parallax agressivo, zero contadores saltitantes — "o movimento é o
inimigo da credibilidade" vale aqui como nos advogados.

## Blocos que estes três têm e a maquete tem de ter

nav com telefone e idiomas → herói com pesquisa/promessa → imóveis em
destaque (cartões grandes) → o argumento do vendedor ("avalie a sua casa",
contornado, sempre visível) → prova social com números → equipa com cara e
nome → serviços → contactos diretos (telefone, WhatsApp, morada com mapa)
→ rodapé completo com AMI e livro de reclamações.

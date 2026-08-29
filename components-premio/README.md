# Componentes prémio — a caixa de ferramentas

> Escrito a 2026-08-29 na missão `site-premio-montra-bora`.
> Peça irmã da skill `site-premio` (o manual) e do `tools/fiscal-visual/` (o crítico).

Treze componentes isolados. Cada um num ficheiro, cada um com demo própria, cada um com um
comentário no topo a dizer **para que serve, quando não usar, e que erro real o originou**.

**Sem frameworks.** HTML, CSS e JavaScript puro. Um componente que obrigue a instalar
qualquer coisa não serve para o que isto é: copiar e colar num site de um cliente.

**Esta pasta não é publicada.** Não está na lista branca do `deploy-cloudflare.sh` — é
ferramenta interna, como o `tools/`.

---

## Os treze

| # | Ficheiro | O que faz |
|---|---|---|
| 1 | `01-cena-em-scroll.html` | A secção fixa-se e um elemento monta-se por camadas ao descer. **Elemento assinatura** — um por site. |
| 2 | `02-revelacao-ao-scroll.html` | Opacidade e deslocamento ao entrar no ecrã, com atraso escalonado entre irmãos. |
| 3 | `03-cabecalho-que-muda.html` | Transparente em cima, sólido e mais fino a partir do primeiro scroll. |
| 4 | `04-carrossel-infinito.html` | Fita sem fim que pára no hover e no foco de teclado. CSS puro. |
| 5 | `05-card-troca-imagem.html` | Duas fotos do mesmo produto, troca no hover com aproximação. Ao toque no telemóvel. |
| 6 | `06-contador-no-ecra.html` | Números que sobem quando a secção aparece. **Só números verdadeiros.** |
| 7 | `07-galeria-lightbox.html` | Grelha que abre em grande, navegável por setas do teclado. Usa `<dialog>` nativo. |
| 8 | `08-antes-depois.html` | Duas imagens com puxador. Clínicas, oficinas, estética — e site velho vs site novo. |
| 9 | `09-formulario-whatsapp.html` | **A peça que transforma um site em máquina de orçamentos.** Abre o WhatsApp já escrito. |
| 10 | `10-cta-duplo-fixo.html` | Duas acções coladas ao fundo no telemóvel, do **mesmo tamanho**. |
| 11 | `11-heroi-video.html` | Vídeo real em fundo, sem som, com poster real e queda para imagem fixa. |
| 12 | `12-parallax-camadas.html` | Fundo, meio e frente a velocidades diferentes. `translate3d`, nunca `background-attachment`. |
| 13 | `13-previsualizacao-protegida.html` | Marca de água em canvas + o caminho de servidor que protege a sério. **Base do Nível 4.** |

Ver todos de uma vez: abre `index.html` desta pasta.

---

## As regras que valem para os treze

### 1. `prefers-reduced-motion: reduce` respeitado
Quem tem essa preferência ligada **vê tudo, sem movimento**. Não vê menos conteúdo — vê o
mesmo conteúdo parado. Em todos os treze isto é a primeira linha do script.

### 2. Foco de teclado visível
`:focus-visible` com contorno laranja de 3px e afastamento. Nenhum componente usa `<div>`
com `onclick`: onde há acção, há `<button>` ou `<a>`.

### 3. Nada de animação que ESCONDA informação
**O estado por omissão é visível. A animação é que esconde e revela.**

Na prática: o script começa por acrescentar uma classe (`js-revelar`, `js-cena`, `cta-espera`)
e só a partir daí é que o CSS esconde. Se o JavaScript falhar, não correr, ou for bloqueado,
a pessoa vê o conteúdo todo. É a diferença entre um site degradado e um site em branco.

Verifica-se assim: desliga o JavaScript e recarrega. Se desaparecer conteúdo, está errado.

### 4. Orçamento de desempenho
- **LCP abaixo de 2,5s** em 4G simulado.
- Imagens em **WebP** com `width` e `height` declarados (senão a página salta ao carregar).
- `loading="lazy"` em tudo o que não é o herói. O herói nunca leva lazy.
- Nenhum ouvinte de `scroll` faz trabalho directo: tudo passa por `requestAnimationFrame`,
  e o ouvinte só existe enquanto a secção está no ecrã (`IntersectionObserver`).
- `will-change` posto e **tirado**. Deixá-lo ligado sempre come memória — num PC de 4 GB
  nota-se.

### 5. Mobile primeiro, testado a 360px
Não é 375. É **360**, que é o Android barato e é o que a maioria da Guarda tem na mão.
O `tools/fiscal-visual/` tira captura a 360, 768 e 1440 — os três são obrigatórios.

---

## Como se leva um componente para um site

1. Abre o ficheiro e lê o comentário do topo. Diz quando **não** usar.
2. Copia o `<style>`, o HTML e o `<script>`.
3. Acerta as variáveis de cor ao design system daquele site (§Passo 2 da skill `site-premio`).
   Nenhum componente traz cores próprias que não sejam variáveis.
4. Troca as imagens de demonstração (SVG embutidos) por **fotografias reais**.
5. Corre o fiscal visual às três larguras.

O único componente com configuração que se mexe sempre é o **9**: o número de WhatsApp está
numa constante no topo do script, e é o único sítio a mudar.

# Fiscal visual — o crítico que mede em vez de opinar

> Missão `site-premio-montra-bora`, 2026-08-29. Bloco F.
> Porta para os sites o que o Bora Studio já provou na animação.

## A regra que veio de um erro real e não se discute

**O crítico compara CAPTURA contra CAPTURA da referência. Nunca captura contra uma
descrição escrita.**

Um crítico a quem se dá a ficha escrita **recita a ficha e aprova lixo** — no meta-juiz do
estúdio deu 2 em 12. Quando o modelo tem o texto do que devia estar lá, ele confirma o
texto em vez de olhar para a imagem.

Por isso este programa faz **duas coisas separadas** e nunca as mistura.

### Parte 1 — geometria, determinística

Enquadramento e espaçamento verificam-se **por medida**, não por modelo de visão. Isso já
foi provado com precisão de 3 pontos percentuais. Sai uma lista de defeitos concretos,
**cada um com a medida**:

- a página rola para o lado (o defeito número um do telemóvel)
- elementos que passam para fora do ecrã, com os píxeis de excesso
- alvos de toque abaixo de 44×44
- letra abaixo de 13px no telemóvel
- imagens esticadas fora de proporção, com a percentagem de desvio
- imagens sem `width`/`height` (é o que faz a página saltar ao carregar)
- imagens sem `alt`
- contraste abaixo de 4.5:1 (3.0 para texto grande), com a razão exacta
- quantos valores de espaçamento, cores e tamanhos de letra distintos existem
- `<h1>`, `<title>`, description, `og:image`, canonical, favicon, viewport
- links que não levam a lado nenhum (becos sem saída)
- LCP e CLS medidos pelo próprio browser

### Parte 2 — a folha de comparação, para o olho

Gera `saida/<nome>/comparar.html` com a captura do trabalho **ao lado** da captura da
referência, à mesma largura. **É isto que se dá a um crítico** — humano ou modelo.

Sem ficheiros em `referencias/`, a folha di-lo em letra grande e o relatório também.
Um relatório que calasse esse facto faria passar por juízo aquilo que foi só medição.

## Como se usa

```bash
python fiscal.py https://boraguarda.com/ --nome montra
```

Também aceita um ficheiro local:

```bash
python fiscal.py ../../index.html --nome montra-local
```

Para páginas com caminhos absolutos (`/assets/...`), levanta primeiro um servidor local,
senão o CSS não carrega e o fiscal mede uma página sem estilos:

```bash
python -m http.server 8899 --bind 127.0.0.1
```

## O que sai

```
tools/fiscal-visual/saida/<nome>/
    360.png 768.png 1440.png    capturas de página inteira
    relatorio.md                 defeitos com a medida, por gravidade
    relatorio.json               o mesmo, para máquina
    comparar.html                trabalho vs referência, lado a lado
```

Código de saída **1** se houver algum defeito GRAVE — dá para usar num portão automático.

## As três larguras

**360**, 768 e 1440. É 360 e não 375: 360 é o Android barato, e é o que a maioria da
Guarda tem na mão.

## Falsos positivos já corrigidos

Um fiscal que grita ao lobo passa a ser ignorado, e aí deixa de servir para nada. Três
avisos falsos foram corrigidos no próprio dia em que o programa nasceu:

1. **Gaveta fora do ecrã de propósito.** Um menu fechado vive fora do ecrã com um
   `transform`. Era contado como transbordo. Agora é ignorado, tal como o que está dentro
   de um contentor que rola de propósito ou marcado `aria-hidden`.
2. **Texto de recurso dentro de `<video>`.** O "o teu navegador não consegue mostrar este
   vídeo" nunca chega a ver-se, mas entrava na conta do contraste. Agora salta-se.
3. **Transbordo sem a página rolar.** Uma imagem que sangra 36px para fora com a página a
   não rolar é quase sempre desenho de propósito. Deixou de ser GRAVE e passou a MÉDIO,
   com a frase a dizer que pode ser sangria intencional.

## O browser

Usa o **Chrome que já está instalado** na máquina, e só cai para o Chromium do playwright
se não encontrar nenhum. Num PC de 4 GB não se puxam 150 MB de browser para tirar três
fotografias.

## O que este programa NÃO julga

Estética, hierarquia, se o site parece caro, se o texto convence. Nada disso se mede em
píxeis. Isso julga-se na folha `comparar.html`, olhando — e sempre com a referência ao lado.

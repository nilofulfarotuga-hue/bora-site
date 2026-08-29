# Gerador de proposta em PDF

> Missão `site-premio-montra-bora`, 2026-08-29. Peça G1.

## Porque é que isto existe

**A proposta em PDF é o que separa quem cobra quinhentos de quem cobra vários milhares.**

Mandar um preço solto por mensagem baixa o valor do trabalho: o cliente compara aquele
número com o do primo que "também mexe em sites" e a conversa acaba ali. Um documento com
capa, o problema dele escrito por palavras dele, o que está e o que não está incluído,
prazo e condições de pagamento, muda quem é que está a falar.

## Como se usa

```bash
python proposta.py exemplo.json
```

Sai em `saida/proposta-<cliente>-<data>.pdf`.

Para começar um novo:

```bash
python proposta.py --modelo > cliente.json
```

Depois abre o `cliente.json`, preenche, e corre `python proposta.py cliente.json`.

O `exemplo.json` está preenchido de ponta a ponta com um negócio inventado de propósito
(**Barbearia da Sé**) — copia-o e muda os campos, é mais rápido do que partir do vazio.

## Os campos

| Campo | O que é |
|---|---|
| `cliente` | Nome do negócio ou da pessoa. Vai na capa e no rodapé de todas as páginas. |
| `titulo` | Uma linha curta. É o que a pessoa lê primeiro. |
| `resumo` | Uma frase na capa a dizer o que se propõe. |
| `problema` | Lista de parágrafos. **O problema real que encontraste**, nas palavras dele. |
| `custo` | O que esse problema custa na prática. Sem números inventados. |
| `nivel` | 1 a 4 (ver a skill `site-premio`). Aparece como chapéu na página 2. |
| `proposta` | Lista de parágrafos. O que vai ser construído. |
| `incluido` | Lista. Uma coisa por linha. |
| `excluido` | Lista. **Escreve-se sempre** — é o que evita "mas eu pensei que também vinha". |
| `prazo` | Texto livre. |
| `preco` | Texto livre (ex.: `"1 200 €"`). **Decisão do Danilo.** |
| `manutencao` | Mensalidade, texto livre. |
| `manutencao_inclui` | Lista. Vazia usa a lista por omissão, que já está escrita. |
| `validade_dias` | Dias até a proposta expirar. Por omissão 30. |

## O que este programa NÃO faz

**Não inventa o preço.** Se o campo `preco` vier vazio, sai "a combinar" e o programa
avisa no fim, com código de saída 2. O preço é decisão do Danilo — nenhuma ferramenta o
escolhe por ele.

**Não promete resultados.** Não há nem haverá campo para "aumento de 300% nas vendas".
Uma promessa dessas afasta o cliente sério, e o cliente sério é o que paga.

**Não usa emoji.** É um documento comercial.

## Como sai o PDF

Pelo Chrome que já está instalado, através do playwright (`page.pdf`). Isso dá controlo
tipográfico a sério — a mesma folha de estilos que o site — sem instalar biblioteca de PDF
nenhuma. O logótipo vai embutido em base64, porque um PDF não vai buscar ficheiros ao disco.

## As condições que estão escritas no modelo

Metade no início, metade na entrega. A manutenção mensal é opcional, começa depois da
entrega, e cancela-se quando se quiser. Se alguma vez estas condições mudarem, mudam-se no
`modelo.html` e não a mão em cada proposta.

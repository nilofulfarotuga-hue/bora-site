# Flyer oficial do Bora App

Gera o flyer A4 (300 dpi) que o Danilo imprime e entrega em mão na Guarda, mais
a versão para WhatsApp.

## Refazer o flyer

```bash
python build_flyer.py     # escreve os dois ficheiros em Downloads/
python verificar.py       # prova: QR lêem-se, 13 blocos, nada repetido
```

Saídas, em `C:\Users\danil\Downloads\`:

| ficheiro | para quê |
|---|---|
| `flyer-bora-app-A4-grafica.png` | 2480×3508, 300 dpi, margem branca de 8 mm — é o que vai para a gráfica |
| `flyer-bora-app-whatsapp.jpg` | 1080×1620, abaixo de 2 MB — é o que se manda nos grupos |

**Não entregar sem `verificar.py` a dizer "tudo verde".**

## Porque é montado por script e não gerado por IA de imagem

Três tentativas com o Gemini falharam sempre pelo mesmo motivo: o modelo
**redesenha** os logos e escreve os nomes errados — "gaola" em vez de Goola,
CONTINENTE torto, KIWOKO deformado, SOBREMESAS repetido duas vezes, blocos
trocados de sítio.

Aqui os logos são os ficheiros verdadeiros das marcas e os textos são
desenhados com a fonte Inter. Nada é "imaginado". À IA de imagem cabia só o
cenário de fundo — e como a quota do Gemini está a zero (confirmado 2026-08-28,
`limit: 0` nos modelos pro e flash), o fundo é gerado por `fundo.py`.

## Quando entra uma loja nova

1. Põe o logo em `assets/logos/<nome>.png` (ver "Onde arranjar um logo" abaixo).
2. Acrescenta o nome à lista `logos=[...]` do bloco certo em `build_flyer.py`
   (constante `BLOCOS`).
3. `python build_flyer.py && python verificar.py`.

Para mudar a altura relativa dos blocos, mexe nos pesos de `LINHAS`.
Para saber quanta altura útil sobra em cada bloco antes de mexer, corre o
espia que está descrito no relatório — é a forma de medir em vez de adivinhar.

## Onde arranjar um logo

`download_logos.py` puxa o que está em `restaurants.photo_url` /
`service_providers.photo_url`. **Atenção:** para as lojas vindas do Glovo esse
campo costuma ser uma **foto da montra**, não o logo — foi o caso do Wells,
Worten, Leroy Merlin, Kiwoko e Zippy, e num flyer isso não serve.

Nesses casos vai-se ao site oficial da marca com o Playwright:

- **Logo em SVG por URL** (Kiwoko, Worten, Zippy, Pingo Doce): buscar o SVG e
  desenhá-lo num `<canvas>` grande, devolvendo o dataURL. `guardar_json.py`
  grava o PNG.
- **SVG inline que não serializa** (Leroy Merlin, Wells): clonar o elemento para
  um overlay `position:fixed` com `transform: scale(N)` e tirar screenshot desse
  overlay. `guardar_shot.py` recorta o branco e grava.

Um logo só publicado em versão branca (Worten) leva pastilha com a cor da marca
— ver `FUNDO_PASTILHA` em `build_flyer.py`.

## Ficheiros

| ficheiro | o que faz |
|---|---|
| `build_flyer.py` | monta o flyer; é aqui que vivem os 13 blocos e o layout |
| `fundo.py` | cenário de fundo (cidade 3D cartoon isométrica, néon verde/laranja) |
| `verificar.py` | prova antes de entregar; sai com código 1 se algo falhar |
| `download_logos.py` | descarrega logos a partir dos URL da base de dados |
| `guardar_json.py` / `guardar_shot.py` | auxiliares da recolha por browser |
| `assets/icons/` | os `cat_*.png` — os mesmos ladrilhos que o cliente vê na app |
| `assets/logos/` | logos das lojas, já aparados |
| `assets/brand/` | `bora_logo.png` e o ícone da aplicação |
| `assets/fonts/` | Inter (variável), a fonte do design system |

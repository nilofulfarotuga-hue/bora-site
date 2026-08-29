# Motor de imagem e vídeo a custo zero

> Escrito a 2026-08-29 na missão `site-premio-montra-bora`.
> É o Passo 5 do funil da skill `site-premio`: **imagens reais, nunca emoji nem ícone a
> fazer de imagem**.
>
> **Regra que manda sobre tudo o resto:** custo zero. Nada aqui usa serviço pago.
> A conta Higgsfield está confirmada a **zero créditos, plano free** — não se tenta usar.

---

## A ordem, e não se salta

1. **Fotos do próprio cliente.** Primeiro sítio a procurar, sempre.
2. **Logótipo do site oficial da marca.** Sempre. Sem excepção.
3. **Só o que falta é que se gera** — cenários e fundos, nunca pessoas.
4. **Vídeo do estúdio `bora-anuncios`**, que corre na cloud a custo zero.

Quem inverte esta ordem acaba com um site de banco de imagens, e um site de banco de
imagens não convence dono nenhum de que se estudou o negócio dele.

---

## 1. Fotos do cliente — a recolha

**Onde se procura, por esta ordem:**

- **Site oficial da marca** — é onde está o logótipo em condições e, muitas vezes, as fotos
  de melhor qualidade.
- **Instagram público** — o perfil da loja. É onde estão as fotos verdadeiras do produto,
  tiradas por quem sabe como é que aquilo deve aparecer.
- **Facebook público** — para negócios com dono mais velho é frequentemente o único sítio
  com fotos, e costuma ter as do interior do espaço.

**Nunca banco de imagens genérico.** Uma fotografia de sorriso comprada lê-se de longe e
diz ao cliente que ninguém foi ver o negócio dele.

### A cicatriz do logótipo, que vale a pena conhecer

> **28/08 — Wells, Worten, Leroy Merlin, Kiwoko, Zippy, Burger King, KFC, Pingo Doce:**
> o `photo_url` que entrou pelo scraping do Glovo era a **foto de montra da loja**, não o
> logótipo — em duas delas nem sequer tinha o nome da marca escrito. As três puxadas do
> site oficial tinham ficado com o **favicon**, um quadrado de 32 a 128 píxeis.

**Regra que saiu daí:** o logótipo vem do **site oficial da marca**, em vector ou alta
resolução. Um agregador (Glovo, Uber Eats) só serve para nome, categoria e, na falta de
melhor, uma foto de posição — **nunca para logótipo**.

Como se apanha o logótipo bom, por ordem de qualidade:
1. SVG no HTML do site oficial (procurar `<svg`, `logo.svg`, `.svg` no CSS)
2. PNG grande na pasta de temas ou no `og:image`
3. `apple-touch-icon` (180 px) — já dá para muita coisa
4. `favicon` de 32 px — **último recurso, e nunca esticado**

### Onde a foto tem de aparecer (a regra dos gémeos)

> **Cicatriz de 27–28/08, Goola:** o site ficou lindo e **a loja dentro da app ficou sem
> logo, sem capa e sem foto nenhuma.**

As imagens de um parceiro vivem em **três** sítios e escrevem-se nos três:
1. o Storage do Supabase (balde `restaurant-assets`)
2. as colunas da base que apontam para elas
3. o mini-site

E regista-se a **origem** de cada foto — site oficial, Instagram do cliente, fotografia
tirada — para daqui a seis meses ninguém ter de adivinhar de onde veio.

### O que nunca se faz

- **Retrato fotorrealista por inteligência artificial de pessoa identificável.** Nunca. Nem
  do cliente, nem da equipa dele, nem de figura pública.
- **Pessoa cortada de fora do enquadramento.** Lê-se como descuido.
- **Duplicados.** Comparar por hash percetual antes de publicar a galeria.

---

## 2. Cenários e fundos em falta — Gemini / Nano Banana

Para o que falta e **não é pessoa**: o granito ao amanhecer, a serra ao fundo, uma textura,
um cenário de montra vazio, um ladrilho de categoria.

**A ferramenta:** o servidor MCP `nano-banana` (`@ycse/nanobanana-mcp`), que fala com o
Gemini. A chave vive em `GOOGLE_AI_API_KEY` na configuração do MCP.

**Âncora de imagem, sempre.** Nunca se pede "uma foto de uma barbearia". Dá-se uma
fotografia real do sítio como âncora e pede-se a variação — outra luz, outro ângulo, o fundo
limpo. Sem âncora sai o genérico, e o genérico está proibido pela regra anti-genérico da
skill.

### Se a chave estiver bloqueada, NÃO se pára a produção

Uma chave do AI Studio é grátis e faz-se em dois minutos. O caminho:

1. Entrar no Google AI Studio com a conta do Danilo (`boraappbora@gmail.com`).
2. Criar uma chave de API nova.
3. Trocar o valor de `GOOGLE_AI_API_KEY` na configuração do MCP e reiniciar a sessão.

**Isto faz-se sozinho, pelo navegador com a sessão já autenticada** — o Danilo não mexe em
painéis web. Ficar à espera de uma quota é que não é opção.

> **Estado a 2026-08-29:** nesta sessão o servidor `nano-banana` **não chegou a ligar**
> (`CONNECT_TIMEOUT`, 30 segundos). Não é falta de configuração — a configuração está lá,
> com chave. Num PC de 4 GB o arranque do `npx` a frio passa facilmente dos 30 segundos.
> Quando isto acontece: repetir; e se voltar a falhar, a causa é o arranque, não a conta.

### E há a queda que quase sempre chega

Um fundo pode ser **CSS**. Um gradiente radial, um `clip-path` de serra, uma textura de
granito em SVG — como no componente 12 (`components-premio/12-parallax-camadas.html`), que
não tem uma única imagem e mesmo assim tem profundidade. Custa zero, pesa zero, e não
depende de quota nenhuma.

---

## 3. Vídeo — o estúdio `bora-anuncios`

**Onde vive:** `C:\Users\danil\Desktop\bora-anuncios`, repositório público
`nilofulfarotuga-hue/bora-anuncios`.

**O que faz:** dá-se-lhe o **URL de um site que já está no ar** e devolve **dois vídeos**
com narração em português de Portugal e música:

- `saida/<cliente>-16x9.mp4` — 1920×1080, para a página
- `saida/<cliente>-9x16.mp4` — 1080×1920, para Instagram, TikTok e anúncios

**O material é o site do cliente.** Não gera vídeo por inteligência artificial, não gera
caras, não gera pessoas.

### Porque é que é grátis, peça a peça

| Peça | O que faz | Grátis porquê |
|---|---|---|
| Playwright + Chromium | grava o site | Apache-2.0, no PyPI |
| edge-tts | narração pt-PT neural | LGPLv3; usa o endpoint público de leitura em voz alta da Microsoft, **sem conta nem chave** |
| FFmpeg | montagem e prova | instalado no runner |
| GitHub Actions | onde tudo corre | o repositório é **público** → minutos ilimitados |
| Música | fundo | 3 faixas CC0 1.0 já commitadas |
| Inter | tipo de letra | SIL Open Font License 1.1 |

As vozes disponíveis em português de Portugal são `pt-PT-DuarteNeural` (masculina) e
`pt-PT-RaquelNeural` (feminina).

### Como se corre

1. Escrever `roteiros/<cliente>.yaml` à mão (o formato está no `README.md` do estúdio; já lá
   estão quatro exemplos reais, entre eles `ouro-e-prata.yaml` e `bora-app.yaml`).
2. No GitHub, Actions → workflow `anuncio` → correr com o nome do cliente.
3. Verde: descarregar o artefacto `anuncio-<cliente>` — traz os dois MP4 e o `prova.txt`.
   Vermelho: a prova falhou, e a razão está no log.

### O workflow irmão: `fotos`

O mesmo estúdio tem um segundo workflow, `fotos`, que fotografa e **mede** uma lista de
páginas (`paginas.txt`) em computador e telemóvel 390×844. É o caminho da cloud para as
capturas do portfólio e do fiscal visual — útil quando o PC de 4 GB não aguenta abrir um
Chromium local.

### Se o cliente não tiver vídeo nenhum

Monta-se a partir das **fotografias reais dele**, com movimento suave — aproximação lenta e
deslocamento, corte a cada dois ou três segundos. Com legendas que digam a mensagem, porque
**um vídeo mudo e parado lê-se de relance como uma fotografia**.

### Regras de vídeo que já custaram caro

**Nunca em base64.** O vídeo fica em `assets/` com caminho relativo e **tem de passar a lista
branca do `deploy-cloudflare.sh`**. Se não estiver na lista, não é publicado e ninguém dá
por isso.

**Poster de imagem real, sempre.** Sem poster, o primeiro segundo é um rectângulo preto — o
oposto do efeito que se quer.

> **Cicatriz de 28/08, Goola:** o mp4 rebentou a meio da codificação por falta de memória
> (dois `ffmpeg` ao mesmo tempo num PC de 4 GB) e **subiu para produção um ficheiro de 57 KB
> com dois quadros**. O webm estava bom e o mp4 era lixo.
>
> Daí a guarda que o gerador tem hoje: **abaixo de um megabyte rebenta em vez de deixar
> passar**. E daí a regra maior: **render de vídeo não se faz no PC do Danilo.** Corre na
> cloud, onde há memória.

---

## 4. O que está proibido

- **Pedir fotos ao Danilo à mão.** Ele decide e aprova; a recolha é dos agentes.
- **Serviços pagos.** A Higgsfield está a **zero créditos, plano free** — não se tenta usar,
  nem se sugere comprar créditos.
- **Banco de imagens genérico** onde devia estar uma foto do cliente.
- **Render de vídeo no PC local.** Já rebentou uma vez e subiu lixo para produção.

---

## 5. Lista de verificação antes de publicar

- [ ] O logótipo veio do site oficial, em vector ou alta resolução (não é o favicon esticado)
- [ ] Nenhuma imagem é de banco genérico onde devia ser do cliente
- [ ] Nenhuma pessoa identificável foi gerada
- [ ] Ninguém aparece cortado de fora do enquadramento
- [ ] Sem duplicados (hash percetual)
- [ ] As fotos do parceiro entraram nos **três** sítios: Storage, colunas da base, mini-site
- [ ] A origem de cada foto está registada
- [ ] O vídeo está em `assets/`, **não** em base64, e passa a lista branca do deploy
- [ ] O vídeo tem poster de imagem real
- [ ] O ficheiro de vídeo tem mais de um megabyte (abaixo disso é lixo de codificação)
- [ ] Imagens em WebP, com `width` e `height` declarados
- [ ] `loading="lazy"` em tudo o que não é o herói

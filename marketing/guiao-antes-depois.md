# Guião — vídeo curto "antes e depois", 15 a 20 segundos

> Missão `site-premio-montra-bora`, 2026-08-29. Peça G3.
> **Sem cara e sem voz.** Sai do estúdio `bora-anuncios` a custo zero.
> **TikTok primeiro, Instagram depois.**

---

## Porque é que é este o vídeo, e não outro

O argumento mais forte que existe numa proposta de site é ver o site velho e o site novo
lado a lado. Não é preciso explicar nada: a diferença explica-se sozinha em dois segundos.

É por isso que o componente 8 da caixa de ferramentas
(`components-premio/08-antes-depois.html`) tem o puxador que se arrasta — e é por isso que
este vídeo é literalmente esse componente a ser arrastado.

**Sem cara e sem voz** por três razões práticas: o Danilo não tem de aparecer nem de gravar
áudio, o vídeo funciona com o som desligado (que é como a maioria das pessoas vê), e
produz-se inteiro na cloud sem tocar no PC de 4 GB.

---

## Formato

- **9:16**, 1080×1920. Vertical, ecrã cheio.
- **15 a 20 segundos.** Abaixo de 15 não dá para ler; acima de 20 perde-se a pessoa.
- **Sem áudio falado.** Música de fundo CC0, das que já estão no estúdio.
- **Legendas grandes**, porque a maioria vê sem som. Um vídeo mudo e parado lê-se de
  relance como uma fotografia — as legendas e o movimento é que dizem que é vídeo.

---

## O guião, plano a plano

### Plano 1 — 0s a 3s · O gancho

Ecrã dividido ao meio na vertical. À esquerda o site velho, à direita o novo, ambos
parados. O puxador está exactamente ao meio.

**Texto por cima, grande, em cima:**
> Este é o mesmo negócio.

Nada mais. Três segundos parados a deixar a pessoa perceber que são dois sites do mesmo
sítio. É a pergunta que a faz ficar.

### Plano 2 — 3s a 9s · O arrasto

O puxador anda devagar da esquerda para a direita, revelando o site novo por inteiro.
Movimento constante, sem solavancos. Seis segundos.

**Texto por baixo, mais pequeno, a aparecer aos 4s:**
> À esquerda, o que estava no ar.
> À direita, o que ficou.

### Plano 3 — 9s a 14s · A prova de telemóvel

Corte. O site novo, a rolar sozinho num telemóvel, de cima até ao botão de acção. Rolagem
lenta e contínua.

**Texto em cima:**
> Feito primeiro para o telemóvel.

Este plano existe porque é aí que a diferença se sente. Um dono de negócio abre o site dele
no telemóvel enquanto vê o vídeo — e é nesse gesto que a proposta se fecha.

### Plano 4 — 14s a 18s · O fecho

Fundo escuro. Logótipo do Bora em cima. Uma linha grande ao centro e o endereço em baixo.

**Texto:**
> Sites para negócios da Guarda.
>
> boraguarda.com/trabalhos

Sem preço. Sem "a partir de". Sem promessa de resultados. O preço vive na proposta em PDF,
depois de haver conversa.

---

## As frases, para escolher uma

Uma frase por vídeo, nunca duas. Estas estão escritas para caberem numa linha a 1080px:

1. Este é o mesmo negócio.
2. O teu site é a primeira coisa que a pessoa vê. Ou não vê.
3. Site velho à esquerda. O que ficou, à direita.
4. Quinze segundos a mostrar a diferença.

**A número 1 é a melhor** e é a que vai no primeiro vídeo: é uma afirmação estranha que
obriga a pessoa a olhar para as duas metades para perceber.

---

## O que NÃO entra neste vídeo

- **Nome do cliente**, sem ele autorizar por escrito. Um antes-e-depois identifica o
  negócio que tinha o site mau, e isso é dele decidir.
- **Números.** Nada de "aumentou 300% as visitas". Não temos esse número e inventá-lo é a
  forma mais rápida de perder o cliente sério.
- **Preços.** Nunca em vídeo de canal.
- **Voz e cara.** É a regra deste formato.
- **Música com direitos.** Só as faixas CC0 que já estão no estúdio.

---

## Como se produz, a custo zero

O estúdio é o repositório público `nilofulfarotuga-hue/bora-anuncios`
(`C:\Users\danil\Desktop\bora-anuncios`). Corre em GitHub Actions, e como o repositório é
público os minutos são ilimitados.

1. Escrever `roteiros/antes-depois-<cliente>.yaml`. O formato está no `README.md` do
   estúdio e já lá estão quatro exemplos reais.
2. No GitHub, Actions → workflow **anuncio** → correr com o nome do roteiro.
3. Verde: descarregar o artefacto, que traz o 16:9, o 9:16 e o `prova.txt`.
   Vermelho: a prova falhou e a razão está no log.

**A captura das duas metades** faz-se com `tools/capturas/capturar.py` deste repositório,
que já fotografa qualquer site em 1200×750 e grava em WebP.

**Nunca no PC.** A 28/08 dois `ffmpeg` ao mesmo tempo num PC de 4 GB rebentaram a meio e
subiu para produção um mp4 de 57 KB com dois quadros. O render corre na cloud, onde há
memória.

---

## Onde vai, e por que ordem

**TikTok primeiro.** É onde um vídeo sem seguidores ainda chega a gente nova, e o público
de dono de negócio pequeno está lá mais do que parece.

**Instagram depois**, como Reel, com o mesmo ficheiro. Não se republica no mesmo dia: dá-se
dois ou três dias de intervalo.

**Nunca se publica sozinho.** A publicação passa pelo agente `social-media`, e esse nunca
publica sem aprovação explícita do Danilo.

---

## Lista de verificação antes de publicar

- [ ] Tem menos de 20 segundos
- [ ] Lê-se com o som desligado
- [ ] Uma só frase, não duas
- [ ] O nome do cliente não aparece (ou há autorização escrita)
- [ ] Nenhum número inventado
- [ ] Nenhum preço
- [ ] O endereço no fim está certo e responde
- [ ] O ficheiro tem mais de um megabyte (abaixo disso é lixo de codificação)
- [ ] O Danilo aprovou

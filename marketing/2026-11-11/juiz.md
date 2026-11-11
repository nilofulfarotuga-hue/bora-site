# Juiz com visão — Casa e Manutenção (11/11/2026)

Juiz: agente de contexto limpo, a tentar reprovar; regra: nota >= 9 em cada peça. Detalhe no e2e_log
(fluxo propaganda-casa-amigo-2026-11-11, passo bloco1-juiz).

Como foram feitas: fotos de cinema no Gemini Plus (Chrome da Bora), pedidas sem texto nem marcas;
título, preços, logótipo Bora real e QR real postos por código (Inter). Nada de cartaz plano.

| Peça | Ronda 1 | Ronda 2 | Ronda 3 | Ronda 4 | Final |
|---|---|---|---|---|---|
| casa-c1-feed.jpg | 8 | 9,2 | — | — | 9,2 |
| casa-c1-story.jpg | 8 | 9,0 | — | — | 9,0 |
| casa-c2-feed.jpg | 8 | 8,6 | 8,6 | 9,0 | 9,0 |
| casa-grupo.jpg | 8,5 | 9,1 | — | — | 9,1 |

O que se corrigiu entre rondas:
- R1 → R2: a chave de fendas estava mal posta e o roupeiro não se reconhecia → foto do roupeiro refeita
  (porta aberta, varão, cabides e prateleiras à vista); letras pequenas do rodapé subidas para 31-34 px;
  Story com o rodapé a 300 px do fundo; cartão do post de grupo reorganizado.
- R2 → R4 (só a C2): emblema redondo no caixilho da TV (parecia logótipo de marca) apagado por clonagem
  do próprio caixilho; canto de baixo à esquerda escurecido (tampa da caixa de ferramentas); linha
  pequena do rodapé mais escura e maior.

Verificado por máquina: o QR da casa-grupo.jpg lê `https://boraguarda.com/baixar?de=qr-grupo-casa`.

Avisos que ficam (não reprovaram): na Story há uma etiqueta preta minúscula num saco de plástico em
baixo à esquerda (zona tapada pela interface); o QR do post de grupo não se lê se a imagem for reduzida
a 400 px (no telemóvel, em ecrã inteiro, lê-se).

---

# Juiz com visão — Amigo Bora (11/11/2026)

Juiz: um agente NOVO de contexto limpo em cada ronda, a tentar reprovar, comparando lado a lado com o anúncio
da Boom (marketing/boom-2026-11-02). Regra: nota >= 9 em cada peça.

Como foram feitas: fundo de cinema no Gemini Plus (Chrome da Bora): Sé da Guarda ao anoitecer e uma mão com
telemóvel de ecrã verde, sem texto nem marcas. Por código (montar_amigo.py): a captura REAL do Amigo
("quero açaí" -> Goola Bowl, 12,48 € com entrega, "Encher o carrinho") colada só onde o ecrã era verde (os
dedos ficam por cima); os ladrilhos REAIS das categorias recortados da captura da home; título condensado,
faixa de pincel, caixa "FALA COM ELE!" com o logo Bora real, Cartão / MB Way / Dinheiro e o QR real.

| Peça | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | Final |
|---|---|---|---|---|---|---|---|---|---|
| amigo-a1-feed.jpg | 7,8 | 8,3 | 8,6 | 8,6 | 8,6 | 9,1 | — | — | 9,1 |
| amigo-a1-story.jpg | 7,3 | 7,6 | 8,8 | 8,3 | 8,2 | 8,7 | 8,6 | 8,8 | 9,0 |
| amigo-grupo.jpg | 7,6 | 7,7 | 8,3 | 8,7 | 8,4 | 9,0 | — | — | 9,0 |

O que se corrigiu entre rondas: o título do ecrã escondido pelo entalhe (folga em cima, sem cortar os lados);
ícones a tapar a mão (passaram a 5, numa coroa mais larga: restaurantes, supermercados, casa, limpeza,
favores); a faixa a cortar o "Total 12,48 €" e o botão verde do microfone a espreitar (captura cortada na
linha do total); a Sé mais visível; candeeiros desfocados entre ícones apagados; a linha de categorias com
os mesmos nomes dos ícones; MB Way só uma vez; Story recomposta para a vertical com as zonas seguras
(conteúdo entre y 266 e 1662) e o fundo de baixo com as luzes da cidade; QR do grupo num cartão de 284 px.

Verificado por máquina: o QR de amigo-grupo.jpg lê `https://boraguarda.com/baixar?de=qr-grupo-amigo`
no original e reduzido a 540 e 400 px de largura (cv2).

Avisos que ficam (não reprovaram): na Story o topo é céu desfocado (não faixa lisa); no grupo a coluna da
direita é apertada e não tem a onda verde e laranja; a captura mostra o nome do parceiro Goola Açaí (parceiro
da Bora, como a Boom no anúncio dela). Ao "preciso de montar um roupeiro" o Amigo ainda não dá o preço da Casa
(erro do bloco 0), por isso estas peças não prometem isso.

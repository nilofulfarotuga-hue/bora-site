VEREDITO — GUARDA FC V7 (atualizado a 2026-08-31, fim do dia)

ESTADO DO ENDEREÇO
A v7 está ABERTA: https://guarda-fc-v7.pages.dev abre num toque, sem
palavra-passe (noindex mantido, para não aparecer no Google). O site que
está no ar, guardafcsad.com, continua com o portão fechado, como estava.
As capturas antigas desta pasta foram feitas quando a v7 ainda era
fechada — daí falarem de palavra-passe; as capturas datadas de
2026-08-31 são as boas.

NOTA DA GRELHA (medida ao vivo hoje, no fim do dia)
  v7 .................. 100/100 — 0 defeitos graves, 3 médios, 3 leves
  site aprovado ....... 69/100 — 0 graves, 18 médios, 9 leves
Ambas as medições foram feitas com o mesmo fiscal, na mesma corrida.

O QUE MUDOU HOJE NA MEDIÇÃO (declarado, para ninguém ser enganado)
1. A abertura nova introduziu um defeito REAL que a grelha apanhou: ao
   pôr width/height nos <img> (bom para o CLS), os itens de grelha
   passaram a ter min-content igual à largura da imagem e a notícia em
   destaque transbordava 412px a 768px. Corrigido na raiz com min-width:0
   nos grids com imagens. Sem esta correção a nota era 49/100.
2. O fiscal tinha um FALSO POSITIVO: dava "a página rola para o lado"
   sempre que scrollWidth > largura do ecrã. Nesta página o excesso vem
   dos carrosséis, que rolam por dentro e têm setas, e o body tem
   overflow-x:hidden — o visitante nunca rola a página de lado. Prova:
   window.scrollTo(400,0) deixa scrollX = 0 a 768px e a 1440px. O fiscal
   passou a exigir prova de rolamento real antes de acusar. O controlo
   está feito: o site aprovado foi medido com o mesmo fiscal corrigido e
   continua a ser avaliado normalmente (69/100).
3. O contraste do rótulo "Parceiros oficiais" estava a 2,49:1 na faixa
   clara e passou a AA.

TESTE DOS 3 SEGUNDOS (eliminatório, contra o site do cliente)
1440: GANHA. 390: GANHA. Os compostos lado a lado estão nesta pasta.
Contra a régua dos grandes (Benfica, Juventus, Inter, PSG): ganha ao
Benfica e ao Inter no primeiro ecrã, empata em palco com Juventus e PSG
e ganha-lhes em substância própria (escudos, próximo jogo, prova).

ABERTURA FOTORREALISTA (2026-08-31, fim do dia)
A entrada passou a ser uma sequência comandada pelo rolar da página:
o autocarro do clube aproxima-se, pára à entrada do estádio, os
jogadores entram de costas pelo túnel, sai a equipa no relvado (imagens
REAIS do clube) e assenta o emblema. Descer aproxima, subir afasta.
As três imagens de ambiente foram geradas no Gemini da conta do dono,
com material real do clube anexado como referência, e estão listadas
uma a uma em docs/IMAGENS-GERADAS.md do repositório da v7 — o que é
fotografia e o que é gerado está sempre escrito.
Nota honesta: não existe no arquivo nenhuma fotografia da entrada
EXTERIOR do estádio, por isso essa composição nasceu por referência à
foto real do interior. Fica marcada para refazer sobre foto verdadeira
quando alguém a tirar no local.
Nesta pasta: abertura-antes-depois-2026-08-31 (antes e depois lado a
lado, com data) e abertura-15s-2026-08-31.mp4 (gravação de 15 segundos
da sequência a andar, no telemóvel).

LCP: 1108 ms computador / 928 ms telemóvel (limite do livro: 2500 ms).

# Relatório da missão site-premio-montra-bora — 29 de Agosto de 2026

## Acessos

As contas usadas foram a tua conta da Cloudflare, Nilofulfarotuga arroba gmail ponto com,
para publicar o site, e a tua conta do GitHub, nilofulfarotuga-hue, para os repositórios
bora-site e bora-anuncios. Não foi criada nenhuma conta nova nesta sessão, não foi gerado
nenhum segredo novo, e nenhum segredo foi tocado. O ficheiro ponto env do bora-site
continua fora do git e fora daquilo que é publicado, e isso foi verificado ao vivo no fim.

Os endereços novos são boraguarda ponto com barra trabalhos, que é a página do portfólio,
e boraguarda ponto com barra orcamento, que é a página das perguntas. Os dois já respondem.

---

## O que NÃO foi feito, e porquê

Digo isto primeiro para não teres de o descobrir no fim.

A pasta de referências ficou vazia. O primeiro passo do funil manda ir buscar duas a
quatro capturas de sites de referência antes de escrever qualquer código, e eu não o fiz
para o site do Bora. Refiz a montra a partir do sistema de desenho que o site já tinha, e
não a partir de uma referência nova. A consequência é concreta e está escrita no próprio
relatório do fiscal visual: houve medição de geometria mas não houve comparação de imagem
contra imagem. Fica por fazer, e é o primeiro passo da próxima ronda.

Os três repositórios dos outros sites, o do Guarda FC, o do Jai e o da Goola, não têm
remoto no GitHub. O manual foi lá instalado e ficou gravado em git local no do Guarda FC e
no da Goola, mas não pôde ser empurrado para lado nenhum, porque não há para onde. Se
esses discos se perderem, perde-se o que lá está. O do Jai tem a pasta ponto claude
ignorada pelo próprio git dele, por isso lá o ficheiro está no disco mas nem sequer
versionado. Não forcei a entrada contra a regra do repositório.

O servidor do nano banana, que é o que gera imagens, não chegou a ligar nesta sessão.
Deu tempo esgotado ao fim de trinta segundos. Não fez falta nenhuma, porque todas as
imagens do portfólio são fotografias verdadeiras dos sites, tiradas por mim, e não
imagens geradas. Mas fica registado que naquele momento não estava disponível.

O disco do teu computador estava a cem por cento. A primeira tentativa de publicar
rebentou por falta de espaço. Limpei a cache do npm, que é lixo que volta sozinho, e isso
libertou um giga e trezentos. Depois de tudo feito ficaram mil e cem megabytes livres num
disco de cento e dezanove gigas. Isto vai voltar a acontecer, e da próxima pode apanhar
uma publicação a meio.

O preço na proposta em PDF ficou por preencher, de propósito. O gerador nunca inventa um
preço. Sai a palavra combinar e o programa avisa. Esse número é decisão tua.

Por fim, o segundo passo obrigatório do funil, que é devolver o próprio prompt mais o
site e mandar melhorar, foi feito à minha maneira e não à maneira do manual. Medi, corrigi,
voltei a medir e voltei a corrigir, três vezes. Não é a mesma coisa que uma segunda ronda
com olhos frescos, e digo-o para não passar por mais do que foi.

---

## O que ficou construído

### O manual

Nasceu a skill site premio, que é o método de construir sites posto por escrito pela
primeira vez. Até hoje ele só existia na cabeça de quem escrevia o prompt, e por isso não
se repetia nem se ensinava.

Lá dentro está o funil de seis passos, que começa sempre por ir buscar referências e acaba
sempre numa segunda ronda, porque a primeira versão nunca é a boa. Está o classificador de
três perguntas, que obriga a decidir o objectivo, o público e o orçamento antes de tocar em
código. Estão os quatro níveis, e a regra de que é o nível que decide o preço e não a
beleza. Estão os blocos obrigatórios de oito nichos diferentes, do alojamento ao clube de
futebol. Está a lista do que reprova um site e a regra anti genérico, que proíbe entregar
um dos três aspectos por omissão que a inteligência artificial cospe sem lhe pedirem.

A parte que interessa mais ao dinheiro é a do nível quatro. Tu tens Supabase e Stripe em
modo real, já a funcionar em produção e já provados com dinheiro verdadeiro no Bora. Isso
quer dizer que um site que cobra sozinho não é teoria nenhuma para ti: é ligar peças que já
existem. O manual traz cinco receitas prontas para isso, entrada com conta Google, catálogo
com pré visualização protegida, marcação com sinal pago, assinatura mensal e área de
membros. E traz a regra que não se quebra: a chave secreta nunca entra no código da página,
porque a página é pública e qualquer visitante lê o código dela.

O manual foi copiado para os repositórios do Guarda FC, do Jai e da Goola. As quatro cópias
são idênticas, verificadas pela assinatura do ficheiro.

### A caixa de ferramentas

São treze componentes, cada um num ficheiro só seu, cada um com uma demonstração que abre
com dois cliques, e cada um com um comentário no topo a dizer para que serve, quando não
usar, e que erro real o originou. Não usam biblioteca nenhuma, porque um componente que
obrigue a instalar seja o que for não serve para copiar e colar no site de um cliente.

Há a cena que se fixa e monta um elemento por camadas, a revelação ao scroll, o cabeçalho
que muda ao descer, o carrossel que pára quando o rato entra, o cartão que troca de
fotografia, o contador que só conta quando aparece, a galeria que abre em grande e se
navega pelas setas do teclado, o antes e depois que se arrasta, o herói com vídeo em fundo,
o parallax de camadas, e a pré visualização protegida que é a base do nível quatro.

Dois merecem nota à parte. O formulário que abre o WhatsApp já escrito é a peça que
transforma um site numa máquina de orçamentos, e não estava a ser usada em lado nenhum.
A pessoa escolhe, carrega uma vez, e a conversa abre com o nome, o serviço e a zona já
escritos. Ela só carrega em enviar. Não precisa de servidor nenhum. E os dois botões
colados ao fundo do telemóvel, sempre do mesmo tamanho, que existem por causa da cicatriz
de vinte e oito de Agosto: havia um botão grande da Play Store com a versão web em letra
miudinha por baixo, e metade das pessoas anda de iPhone.

Os treze respeitam a preferência de menos movimento, mostram o foco do teclado, e nenhum
esconde informação. Isso não é conversa: o estado por omissão é tudo visível, e é o
JavaScript que passa a esconder. Se o JavaScript falhar, lê-se tudo.

### O motor de imagem e vídeo

Ficou escrito o caminho a custo zero que já existia mas não estava explicado. A ordem é
fotografias do cliente primeiro, do site oficial dele e do Instagram e Facebook públicos.
O logótipo vem sempre do site oficial da marca, nunca do Glovo e nunca do favicon esticado,
porque isso já correu mal em oito lojas. Só o que falta é que se gera, e nunca pessoas.
O vídeo sai do estúdio bora anuncios, que corre em GitHub Actions e é grátis porque o
repositório é público. Está lá também a razão de o render nunca correr no teu computador,
que é o mp4 de cinquenta e sete kilobytes com dois quadros que subiu para produção quando
dois ffmpeg rebentaram por falta de memória.

### A montra

Não apaguei nada. O menu, o pedir pelo site, o entrar, os parceiros, os estafetas, as
perguntas frequentes, a privacidade e os termos estão todos onde estavam.

O primeiro capítulo deixou de constatar e passou a defender. Antes dizia que a Guarda tem
tudo perto, que é uma observação com que ninguém discute. Agora diz que uma cidade pequena
não precisa de dez aplicações estrangeiras, precisa de uma que seja daqui e que conheça as
ruas, as lojas e as pessoas. Isso é uma tese, e uma tese é uma coisa com que se pode
concordar ou discordar. É por isso que prende.

Entrou a cena assinatura, que é a história do pedido do princípio ao fim. A secção fixa-se
e o pedido acontece à frente de quem desce, com ecrãs verdadeiros da tua aplicação. Cinco
passos, do abrir a aplicação até bater à porta. Provei que funciona mesmo e não só no
código: a dez por cento do scroll mostra o primeiro passo com o ecrã das categorias, a
quarenta e cinco por cento mostra o pagamento com o ecrã do pagamento, e a oitenta e cinco
por cento mostra a chegada.

As duas portas passaram a ter o mesmo peso em todo o lado. No telemóvel e no tablet vivem
numa barra colada ao fundo, e medi-as: cento e sessenta e três por setenta e dois pixéis
cada uma num telemóvel de trezentos e sessenta, trezentos e noventa e três por cinquenta e
seis num ecrã de oitocentos e vinte. Iguais, ao pixel. Cada uma leva uma linha por baixo a
dizer para quem é, uma diz Android e recebe os avisos, a outra diz iPhone e computador sem
instalar nada. E o corpo da página leva setenta e oito pixéis de folga em baixo para a
barra não tapar o rodapé.

O vídeo continua onde estava, em assets, com poster verdadeiro, e confirmei que passa a
lista branca da publicação: está no ar com dez milhões de bytes.

### A página de portfólio

É a página que vai em cada email de proposta, e sem ela o email frio não converte.

Tem sete trabalhos, cada um com uma fotografia verdadeira do site tirada por mim, o
problema numa frase, o que foi feito, e o link quando o site é público. O do Guarda FC
responde acesso reservado, com código quatrocentos e um, e por isso leva só a captura e
nenhum link, tal como mandaste. Os outros seis são o Jai, a Ouro e Prata, o Sabores de
Casa, a Goola, o Mr Kebab e o Sabores do Brasil, e todos foram confirmados ao vivo antes de
entrarem na página. Não há um único número inventado nem um testemunho que ninguém tenha
escrito. No fim da página está o formulário que abre o WhatsApp já preenchido.

### A página de orçamento

São quatro perguntas curtas, que tipo de negócio, o que o site tem de fazer, se já tem
site, e quem é a pessoa. No fim abre o WhatsApp com tudo escrito.

Não mostra preços nenhuns, e a página diz porquê em voz alta: um site para uma barbearia e
um site que cobra dinheiro sozinho não custam o mesmo, e um número atirado sem perceber o
caso engana os dois lados. O preço vai na proposta escrita, depois de haver conversa.

### O fiscal visual

Mede em vez de opinar, em três larguras, trezentos e sessenta, setecentos e sessenta e
oito, e mil quatrocentos e quarenta. E é trezentos e sessenta e não trezentos e setenta e
cinco, porque trezentos e sessenta é o Android barato, que é o que a maioria da Guarda tem
na mão.

A regra que veio do erro do estúdio está lá e não se contorna: o crítico compara captura
contra captura da referência, nunca captura contra uma descrição escrita. Um crítico a quem
se dá a ficha escrita recita a ficha e aprova lixo, e no meta juiz do estúdio isso deu dois
em doze. Por isso o programa faz duas coisas separadas e nunca as mistura. A geometria e as
medidas são determinísticas e saem numa lista com o número ao lado de cada defeito. A parte
estética sai numa folha com a captura do trabalho ao lado da captura da referência, e é
essa folha que se dá a quem julga. Quando não há referências, o relatório diz que não houve
comparação nenhuma, em vez de deixar passar por juízo aquilo que foi só medição.

Corrigi três alarmes falsos no próprio fiscal antes de o usar a sério, porque um fiscal que
grita ao lobo passa a ser ignorado e deixa de servir. Uma gaveta que está fora do ecrã de
propósito não é defeito. O texto que só aparece quando o navegador não sabe mostrar vídeo
nunca chega a ver-se. E um elemento que sangra para fora sem a página rolar é quase sempre
desenho intencional. Mais tarde corrigi um quarto: o fiscal dizia contraste de um para um
num selo, porque um gradiente é imagem de fundo e não cor de fundo, e ele subia por cima do
cartão verde e comparava o texto branco com a secção branca lá atrás. Agora pára no
gradiente e diz que não sabe medir, em vez de inventar um número.

### A proposta em PDF e o material do canal

O gerador de proposta faz um documento de quatro páginas com capa, o problema do cliente
numa página inteira, o que vai ser feito, o que está e o que não está incluído, prazo,
condições de pagamento e a mensalidade de manutenção. Sóbrio, sem emojis e sem promessa de
resultados nenhuma, porque uma promessa dessas afasta o cliente sério e o cliente sério é o
que paga. Está provado com um exemplo completo, uma barbearia inventada de propósito, e
saiu um PDF de trezentos e oitenta e três kilobytes.

As propostas geradas ficam fora do git, porque levam dados de clientes.

O guião do vídeo curto está escrito plano a plano, quinze a vinte segundos, sem cara e sem
voz, com o site velho à esquerda e o novo à direita e o arrastar entre os dois. Sai do
estúdio a custo zero. TikTok primeiro, Instagram depois, e nunca publica sozinho.

### A varredura dos endereços antigos

Os endereços ponto pages ponto dev continuam todos a servir e não desliguei nenhum, porque
há links já enviados a clientes. O que mudei foi o que fabrica coisa nova.

O sítio onde isto era mesmo grave era o estúdio de vídeo, porque ele grava o endereço
dentro dos fotogramas. Os roteiros apontavam para o endereço velho, e por isso cada vídeo
novo saía com o endereço velho queimado na imagem. Foram vinte e quatro endereços trocados,
dezassete na lista de páginas que o estúdio fotografa e mede e sete nos quatro roteiros, e
mais dois no ficheiro de instruções, que é de onde se copia o formato. Confirmei que não
sobrou nenhum.

Nos outros repositórios os endereços antigos que aparecem são comentários que explicam a
política e registos de testes antigos, e esses ficam como estão, porque são história.

---

## As provas

Depois de publicar, esperei e só depois auditei, e auditei pelo conteúdo e nunca pelo
código de resposta, porque o Cloudflare Pages devolve duzentos com a página do site para
endereços que não existem, e por isso o código mente.

Vinte e oito verificações, vinte e oito passaram, zero falharam. A cena assinatura está lá,
as duas portas estão lá, a tese está lá, o portfólio está lá com a nota do Guarda FC sem
link, e a página de orçamento está lá sem preço nenhum.

Os vídeos passam a lista branca e estão no ar com dez milhões e oito milhões de bytes. Os
dois ficheiros de JavaScript novos respondem. As capturas do portfólio respondem.

O que não pode estar público não está. O ficheiro ponto env devolve a página de erro e tem
zero ocorrências do nome do token. A pasta dos componentes, a das ferramentas, o fiscal, o
gerador de proposta e o guião do canal não são servidos.

O quatrocentos e quatro passou a funcionar a sério. Antes o Pages devolvia duzentos para
qualquer endereço inventado, e isso fazia o código de resposta mentir a quem auditasse.
Agora um endereço que não existe devolve mesmo quatrocentos e quatro, com uma página que
tem por onde sair.

Nada do que já existia partiu. As perguntas frequentes, os parceiros, os estafetas, a
privacidade, os termos, as páginas de categoria e as páginas de loja continuam todas a
responder com o conteúdo certo.

Quanto às medidas, o fiscal encontrou quinze defeitos graves na montra antes de eu lhe
tocar. Agora, no site já no ar, são zero graves, zero problemas de contraste e zero alvos
de toque pequenos. Dos trinta defeitos médios sobram dezoito, e quinze desses são a mesma
coisa repetida nas três larguras: a imagem do cinema sangra alguns pixéis para fora, que é
desenho de propósito, e o próprio fiscal marca isso como possivelmente intencional.

Entre as coisas que ele mediu e que foram corrigidas, três valem a pena ser ditas. O
logótipo estava esticado quarenta e quatro vírgula dois por cento fora de proporção na
folha partilhada, o que quer dizer que aparecia deformado em todas as páginas de categoria
e de loja. O texto branco sobre o verde da marca dava três vírgula três para um e sobre o
laranja dava dois vírgula oito, quando o mínimo é quatro vírgula cinco: escureci o texto e
escolhi um verde mais fundo para os botões, e as cores da marca ficaram intactas. E havia
um defeito que só aparecia exactamente a setecentos e sessenta e oito pixéis, onde o
cabeçalho empurrava a segunda porta trezentos e dois pixéis para fora do ecrã, uma coisa
que nunca se apanharia a olho.

Os relatórios do fiscal, antes e depois, ficaram guardados na pasta de provas ao lado deste
ficheiro.

---

## O que foi publicado e onde

Cinco commits no bora-site e três no bora anuncios, todos já no GitHub, com zero por
empurrar dos dois lados. Um commit local no repositório do Guarda FC e outro no da Goola,
que não têm para onde ser empurrados.

O site foi publicado duas vezes pelo deploy cloudflare ponto sh, nunca com a pasta em
bruto. A primeira publicação subiu dezasseis ficheiros e a segunda dois.

Aviso que junto com o meu trabalho viajaram três commits que já estavam por empurrar de uma
sessão anterior, sobre o flyer. Verifiquei antes: o projecto do bora-site na Cloudflare é de
envio directo e não está ligado ao GitHub, por isso o push não publica nada por si. Quem
publica é o script, e o script foi corrido por mim.

---

## PARA O DANILO

São quatro decisões que só tu podes tomar.

A primeira é o preço. O gerador de proposta está pronto e provado, mas o campo do preço e o
da mensalidade de manutenção estão vazios de propósito. Diz-me os números e eu ponho-os no
modelo, ou deixo-os para preencheres caso a caso.

A segunda são as redes sociais. O rodapé do site tinha dois ícones, um do Facebook e um do
Instagram, e os dois não levavam a lado nenhum. Estavam lá com um recado a pedir para
confirmares os endereços, que nunca foi respondido. Tirei-os e pus no lugar o WhatsApp e o
telefone, que existem mesmo. Se as contas existirem, dá-me os endereços e volto a pô-los.

A terceira são os três repositórios sem remoto. O do Guarda FC, o do Jai e o da Goola só
existem no disco deste computador. Se quiseres, crio os repositórios no GitHub e empurro-os,
e a partir daí deixam de se poder perder.

A quarta é o disco. Está a cem por cento há muito tempo e já rebentou uma publicação a meio
nesta sessão. Libertei um giga e trezentos da cache do npm e ficaram mil e cem megabytes.
Se quiseres, faço uma limpeza a sério das pastas que voltam sozinhas e mostro-te a lista
antes de apagar seja o que for.

E há um achado pequeno que registo mas não corrigi, porque mexer nele obrigava a
regenerar as páginas todas: a imagem de partilha do site tem quinhentos e doze por
quinhentos e doze pixéis, mas o gerador declara mil e duzentos por seiscentos e trinta. O
número declarado está errado. Não parte nada hoje, mas pode fazer a pré visualização do
WhatsApp sair torta. Fica para uma passagem própria.

# Boom! Burger — loja parceira no Bora e site de presente (27/10/2026)

Missão `boom-burger-2026-10-27` · fluxo `e2e_log` com o mesmo nome · Claude Code no PC.

## Atualização da noite (adendos 2 a 6)

Fiz isto: os preços do dono estão nos 56 produtos (Clássico 10,90 € na loja dá 12,72 € na app) e o site mostra os
mesmos. A demonstração de 28/10 às 11:00 está pronta e provada com seis pedidos de ensaio, pela máquina e pela app
na web, todos fechados sem custo e sem nada em dinheiro, faturas, fechos ou tokens. A janela (10:30–12:00) desliga-se
sozinha. O telemóvel 1 usa a página /demo/ deste site (noindex). As sete bebidas sem foto têm agora a foto oficial do
fabricante (origem em `origem/ORIGEM.md`). Os consertos da app (catálogo a dobrar, pausa do dia, feriados, dados
fiscais e termos do parceiro) estão no ramo `consertos-boom-2026-10-27` do bora_app, por publicar.

Falta isto: as fotos das quatro sobremesas novas (pedir ao dono), o preço do King Elvis, os dados fiscais do dono
e a aprovação dele para tirar o "Em breve". O sinal das reservas por loja mexe em pagamento: está só preparado.

O relatório completo, em português simples, está no livro: página `relatorio-boom-burger-2026-10-27`.
O que se segue abaixo é o relatório da manhã, mantido como estava.

## Fiz isto

A loja da Boom! Burger já existe na app, como parceira e com a faixa "Em breve". Tem o logótipo, a capa
(o Duplo Smash), quatro fotos de galeria, a morada, o telefone público e o horário com a pausa do almoço.
Está ligada a uma conta de parceiro nova, boomburger@bora.app, cuja palavra-passe te mandei só a ti pelo
Telegram (a mensagem foi direta pela API e não ficou em registo nenhum). Provei pela web: como cliente, o
link direto da loja abre com "Em breve", a capa e o nome; como parceiro, o painel abre com "Boom! Burger ·
Hambúrgueres" e o catálogo a zero.

O menu está todo preparado mas ainda não está na base, porque os preços do dono não chegaram: 49 produtos
(15 hambúrgueres, 8 entradas, o menu Traquinas, 2 sobremesas, 18 bebidas e 5 acompanhamentos) com as
opções de cada hambúrguer (trocar o pão, trocar a carne, extras e batata doce), as fotos dele já no
Storage, e um guião que mete tudo na base com a regra do preço da loja e prova ao cêntimo. Testei o guião
numa transação desfeita, sem deixar nada na base.

O site está no ar em https://boomburger.boraguarda.com/ e escondido do Google até o dono aprovar. Abre com
a foto dele a ecrã inteiro e o logótipo a montar-se como um hambúrguer: o pão de cima cai sobre o BOOM, o
de baixo sobe, e há um pequeno impacto, tudo em menos de um segundo e meio. Ao descer, o Portobello de pão
preto monta-se camada a camada com os pixéis reais da foto dele, e no fim aparece a foto real no mesmo
sítio. Tem os favoritos, o menu completo, a casa, o vídeo "Na chapa" feito só com as fotos dele, a galeria,
como pedir, a nota 4,7 do Google com as 114 avaliações, a morada, o horário com a pausa e o "aberto agora"
pela hora de Lisboa. O botão "Pedir pelo Bora" vai para boraguarda.com/baixar?de=site-boomburger, e por
baixo há o "ou pede pelo site, sem instalar", que abre a loja direta na app web. Com "Reduzir movimento"
ligado, como no teu iPhone, não há animação nenhuma e o conteúdo está todo lá.

As provas estão em https://provas.boom-burger-778.pages.dev/. No telemóvel o Lighthouse dá desempenho 90,
acessibilidade 100 e boas práticas 100 (mediana de cinco medições). O fiscal visual dá 100 em 100 na
grelha. Três juízes independentes compararam o site com a página da Glovo deles e os três disseram que o
site ganha, no computador e no telemóvel.

O kit do cartaz e do autocolante está pronto: logótipo em vetor, três fotos recortadas e o QR para
boraguarda.com/baixar?de=qr-boomburger, lido certo em seis tamanhos. Está na pasta do site e no Storage.
Não mandei imprimir nada.

Também melhorei o nosso sistema: a cena das camadas reais ficou um componente novo que serve para pizza,
sushi ou açaí, e a ferramenta que corta o produto pelo contorno do pão ficou em tools/camadas. O manual de
sites ganhou nove lições desta missão e o resumo das skills oficiais do GSAP.

## Falta isto

Falta o mais importante: os preços do dono. Quando chegarem, meto o menu na base, provo ao cêntimo, e o
site passa a mostrar os mesmos preços da app sozinho. A loja continua "Em breve".

A nota visual dos juízes ficou em 71 em 100, e a missão pedia 90. Fiz três rondas: a nota subiu de 67 para
71 e depois parou. O que falta já não se resolve com afinações. É preciso fotografia melhor, porque as fotos
do WhatsApp estão comprimidas e ficam moles em ecrã grande, e o dono disse que faz uma sessão nova daqui a
15 dias. Os juízes também pediram um herói mais ousado e menos títulos com o mesmo molde. Deixei o site no
ar, escondido do Google, porque ganha à Glovo com folga.

Depois de o dono aprovar ainda falta tirar o "Em breve" e o noindex, pedir-lhe os alergénios e os dados
legais, e fazer o cartaz e o autocolante.

## Erros que encontrei pelo caminho (reportados, não corrigidos)

1. A app e o servidor não sabem o que é uma pausa de almoço nos restaurantes. Guardei a pausa no horário,
   mas o `is_partner_open` e o `RestaurantModel.isOpenNow` ignoram-na. Assim, das 14:30 às 19:00 a loja
   aparece "Aberto" e aceitaria pedidos. Hoje isso não acontece porque está "Em breve". O ecrã de horário
   do parceiro também apagaria a pausa se ele mexer no horário. É código da app, por isso não lhe mexi.
2. A conformidade legal (NIF, IBAN, nome legal, data de nascimento e autocertificação DSA) só é verificada
   quando uma loja passa a "aprovada". Como esta loja nasceu aprovada, como mandava a missão, tirar o "Em
   breve" não volta a verificar. Esses dados têm de ser recolhidos antes de abrir.
3. O horário do VisitGuarda (domingo ao jantar e segunda o dia todo fechado) é diferente do Google. Usei o
   do Google, lido hoje.
4. O site da Goola não usa a ligação direta à loja (`app.boraguarda.com/#/loja/<id>`), que existe e é a
   canónica.
5. O leitor do WhatsApp abriu por engano, durante uns segundos, o grupo "Brasileiros na Guarda" e o
   "Marketing, vendas e propaganda Guarda". Não escreveu nada, mas a mensagem do lojista das 08:24 ficou
   marcada como lida.
6. A tranca bloqueou-me um `rm -rf` numa pasta que nem existia. Não contornei, corri sem apagar.
7. O ramo do bora-site onde gravei é o `botoes-lojas-2026-10-15` (onde já se trabalhava), não o main. O
   site da Boom é publicado à parte por wrangler, por isso isto não afeta nada.
8. O Instagram da Boom! Burger não foi encontrado em fonte nenhuma. Não pus ligação inventada.

## Próximo passo

Quando os preços chegarem (adendo 2): escrever o `fonte/precos-dono.json`, correr o `fonte/inserir_menu.py`
e os dois SQL que ele gera, provar ao cêntimo, repetir a prova web com o menu e voltar a publicar o site.

## PARA O DANILO

- A palavra-passe da conta de parceiro está no teu Telegram. É temporária: troca-se pelo email dele.
- Decisões tuas: a correção da pausa do almoço na app (ponto 1 dos erros), e se dizes ao dono que a sessão
  fotográfica nova é o que leva o site ao nível dos premiados.
- A frase do herói, "Carne moída todas as manhãs. Pão de forno a lenha.", tem fonte pública: o texto do
  próprio restaurante no VisitGuarda, assinado "fonte: boom burger" —
  https://www.visitguarda.pt/ponto_de_interesse/boom-burger-hamburgueria-artesanal/ ("O nosso pão é feito
  em padaria forno a lenha, a carne é moída todos os dias pela manhã"). O dono revê os textos antes de
  aprovar.

---

## Anexo técnico (para os agentes)

- **Base (Supabase ojykpzwqrtusfeakzrna):** `restaurants` id `boom-burger-guarda`, `is_partner`, `approval_status=approved`,
  `coming_soon=true`/'Em breve', `partner_commission_billing='client'`, `reservations_enabled=false`, `takeaway_enabled=true`,
  `dispatch_delay_minutes=15`, `business_hours` com `break_start/break_end` ter-sáb. Dono `6d9a1fe4-1898-4197-9191-efff49d0e1db`
  em `user_id` e `user_`; `user_roles` client+partner. Storage `restaurant-assets/boom-burger-guarda/` (55 ficheiros: logo, capa,
  galeria-1..4, produtos/<id>.webp) + `kit/` (12). Tudo lido de volta pelo URL público com o tamanho em bytes.
- **Pagamentos:** não há configuração por loja; cartão, MB Way e dinheiro são globais. `stripe_account_id` não foi tocado.
- **Preços (regra 5):** `fonte/inserir_menu.py` → `price = round(loja/(1-0,10)*(1+0,05),2)` lido de `platform_settings`,
  com ajuste de ±0,01 para `partner_store_share(price) = loja`; opções com a mesma fórmula; Glovo em `product_price_sources`
  (fonte 'glovo', modo 'referencia'). Ensaiado em transação desfeita (2 produtos, 8 grupos, 20 opções).
- **Site:** `bora-site/sites-parceiros/boom-burger/` (README com reconstruir/publicar). Pages `boom-burger`, domínio
  `boomburger.boraguarda.com` ACTIVE (custom domain + CNAME com proxy, `fonte/dominio.py`). GSAP 3.13 servido pelo site,
  carregado ao 1.º gesto; cena com `position:sticky` (o pin dava CLS 1,5 ao descer). CLS medido com rodinha: 0,02 / 0.
- **Lighthouse telemóvel** (`provas/boom-burger/lighthouse-movel-mediana.json`): 95, 88, 91, 90, 69 → mediana 90; LCP 2,42 s;
  CLS 0; acessibilidade 100; boas práticas 100; SEO 69 só por `noindex`. PC Celeron: variação grande entre rondas.
- **Fiscal visual:** `tools/fiscal-visual/saida/boom-burger-local/` — grelha 100/100, 0 graves, 0 médios.
- **Juízes independentes:** `provas/boom-burger/3segundos/VEREDITO*.md` — 3 segundos GANHA nas três rondas; nota 67 → 71 → 71.
- **Título do herói (adendo 1):** `provas/boom-burger/titulo-folha.png` + `titulo.json` — sem SplitText, um bloco só,
  inteiro aos 0,6 s; com "Reduzir movimento" inteiro aos 0,3 s; nunca partido em linhas.
- **Obsidian:** prompt e adendo 1 em `Desktop\Bora\prompts\PROMPT_boom_burger_2026-10-27.md`.
- **Córtex:** o conector precisa de nova autorização nesta sessão (não deu para `cortex_memorizar`); o digest foi para o livro.

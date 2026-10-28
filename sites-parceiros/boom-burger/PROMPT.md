# PROMPT LONGO — site da Boom! Burger (boomburger.boraguarda.com)

> Missão `boom-burger-2026-10-27`. Passo 3 do método `site-premio`. A 2.ª ronda (passo 6)
> volta a este ficheiro com o site construído na mão.

## Classificador (§2 do site-premio)

```
NÍVEL: 3 (prémio) — presente do Bora para fechar a parceria
BLOCOS OBRIGATÓRIOS (restaurante): menu com preços verdadeiros (os da app), fotos do prato real,
  horário com a pausa, alergénios (por telefone até o dono os mandar), botão de pedir pelo Bora
FICA DE FORA: reservas de mesa (reservations_enabled=false até o dono dizer se tem mesas),
  carrinho no site (o pedido é na app), inglês (só PT-PT nesta versão), milkshakes (o VisitGuarda
  fala neles mas não estão no menu de lado nenhum), Instagram (não encontrado), textos de
  avaliações, "desde 20XX", prémios, pessoas nas fotos, preços da Glovo
ELEMENTO ASSINATURA: o hambúrguer que se monta — o logótipo monta-se ao abrir (pão de cima cai
  sobre o BOOM, pão de baixo fecha, impacto) e, ao descer, o Portobello real monta-se camada a
  camada. Tudo o resto é disciplinado.
```

## Quem é o cliente

Boom! Burger — Hamburgueria Artesanal. R. Jardim dos Castelos Velhos, 6300-397 Guarda.
Telefone público 923 177 918. Google 4,7 com 114 avaliações (lido a 27/10/2026).
Horário (Google, 27/10/2026): segunda 19:00–22:30; terça a sábado 12:00–14:30 e 19:00–22:30;
domingo fechado. Está na Glovo; não tem site. As palavras deles (VisitGuarda, "fonte: boom
burger"): "Somos uma hamburgueria artesanal onde prezamos pela qualidade e frescura dos alimentos
que utilizamos. O nosso pão é feito em padaria forno a lenha, a carne é moída todos os dias pela
manhã e os legumes e frutas são frescos diariamente."

**Objetivo comercial numa frase:** quem chega ao site carrega em "Pedir pelo Bora".

**Público:** gente nova e adulta da Guarda, estudantes do Politécnico, turistas. Digital, mas o
botão de pedir tem de ser óbvio em qualquer ecrã e a qualquer altura do scroll.

**Adversário verdadeiro (teste dos 3 segundos):** a página da Glovo deles. Referências de nível:
Deleito Burger (Pide Ahora em todo o lado), The Good Burger (produto reage ao cursor), STÄCK
(escuro, cinematográfico, hambúrguer em camadas), Crav (letra condensada gigante, rodapé animado).
Capturas em `bora-site/referencias/boom-burger/` (o dgrees.studio bloqueou o robô e a página do
STÄCK na Contra já dá 404 — fica a ideia descrita no briefing).

## Design system (tirado do logótipo vetorial do dono)

1. **Cores**
   - `--noite #121110` — fundo da página (mais fundo que o do logótipo, para o dourado brilhar)
   - `--carvao #2B2A29` — o fundo exato do logótipo; superfícies e cartões
   - `--carvao-2 #1C1B1A` — cartões sobre a noite
   - `--linha #3A3836` — filetes e contornos
   - `--ouro #DBB545` — o dourado exato do PDF; pão do logótipo, títulos pequenos, estrelas
   - `--creme #F6F0E2` — texto principal (branco quente)
   - `--creme-2 #BFB6A6` — texto secundário (9:1 sobre a noite)
   - `--brasa #F97316` — SÓ o botão de pedir (é o laranja do Bora; texto escuro por cima, 6,6:1)
2. **Tipografia** — display Bebas Neue 400 (a condensada mais parecida com o "BOOM"), em
   maiúsculas, `letter-spacing:.01em`, `line-height:.9`; corpo Inter 400/500 a 17px, 1.6;
   utilitária Inter 700 a .78rem, `letter-spacing:.18em`, maiúsculas, em dourado. A manuscrita
   "Burger" só existe no SVG do logótipo, nunca como fonte.
3. **Espaçamentos** — 4/8/12/16/24/32/48/64/96/128. Secções: 96 (computador) / 64 (telemóvel).
   Margem lateral 16 px no telemóvel.
4. **Cantos** — 8 (etiquetas), 20 (cartões e fotos), 999 (botões). Só estes três.
5. **Sombras** — uma: `0 30px 60px -30px rgba(0,0,0,.75)`; mais um brilho dourado só no
   hambúrguer recortado.
6. **Botões** — pílula cheia brasa com texto noite, Inter 800, mínimo 52 px de altura; hover
   sobe 2 px e clareia; foco: contorno dourado de 3 px. Secundário: contorno creme fino.
7. **Grelha** — 12 colunas, máximo 1240 px, quebra a 900 e 600.
8. **Fotos** — as do dono, luz quente de madeira; cantos 20; herói a sangrar; grão subtil
   (ruído SVG a 6%) por cima da página inteira.
9. **Movimento** — o logótipo monta-se (<1,5 s, sem esperar pelo scroll); a cena das camadas
   (pin + scrub); revelações curtas ao descer; o logótipo do rodapé volta a montar-se. Com
   "Reduzir movimento": nada disto, tudo visível e a foto inteira.

## Secções, por ordem, com o conteúdo real

1. **Herói** — foto inteira do Boom! Duplo Smash (wa-11) a sangrar, escurecida à esquerda e em
   baixo. Por cima: o logótipo SVG que se monta; frase "Carne moída todas as manhãs. Pão de forno
   a lenha."; "Pedir pelo Bora" (brasa) + "ou pede pelo site, sem instalar"; selo "4,7 no Google ·
   114 avaliações". Cabeçalho fixo com o logótipo pequeno e "Pedir pelo Bora". No telemóvel,
   barra fixa em baixo com o botão (56 px).
1b. **Cena das camadas** — "O Portobello, por dentro" / "Monta-se camada a camada.": as 5 fatias
   REAIS do recorte do Portobello (pão de feijão preto; cogumelo portobello, cebola grelhada e
   molho de trufa negra; bacon e provolone fumado; 160 g de novilho e agrião; pão) descem e
   encaixam com mola; no fecho: a foto real inteira, o logótipo e "Pedir pelo Bora".
2. **Favoritos da casa** — Duplo Smash, Bombástico, Brie Fan (os mais vendidos na Glovo),
   Kamikaze, Portobello, Serra da Estrela; foto, ingredientes, preço da app e "Pedir".
3. **Menu completo** — Hambúrgueres (15), Entradas (8), Menu Traquinas (1), Sobremesas (2),
   Bebidas e cervejas (18), Acompanhamentos e molhos (5); "Personaliza" com as trocas de pão e
   carne; alergénios: "liga 923 177 918". Preços = os da app (`menu.json` gerado da base e
   refrescado no browser); enquanto não houver, "Preço na app".
4. **A casa** — as palavras deles + 3 factos (forno a lenha, carne moída todas as manhãs, frescos
   todos os dias) + Wi-Fi grátis; foto do Serra da Estrela.
5. **Na chapa** — vídeo de 11 s feito com as fotos e o recorte reais, mudo, em loop, só carrega
   ao entrar no ecrã.
6. **Galeria** — 8 fotos de produto do dono, sem pessoas.
7. **Como pedir** — 1 Abre o Bora · 2 Escolhe na Boom! Burger · 3 Recebe em casa ou levanta.
8. **Google** — 4,7, 114 avaliações, ligação para a ficha no Google Maps (sem copiar textos).
9. **Visita-nos** — morada com ligação ao Google Maps, horário com a pausa, "aberto agora"
   calculado na hora de Lisboa, telefone.
10. **Rodapé** — logótipo completo (que se monta outra vez), Facebook, "Site oferecido pelo Bora".

## Ligações

- Pedir (único): `https://boraguarda.com/baixar?de=site-boomburger`
- Sem instalar: `https://app.boraguarda.com/#/loja/boom-burger-guarda` (ligação canónica da app)
- Google Maps: `https://maps.google.com/?cid=12467143797523261163`
- Facebook: `https://www.facebook.com/people/Boom-Burger-Hamburgueria-Artesanal/61571813637975/`

## Técnica

HTML + CSS + JS sem framework; GSAP 3.13 + ScrollTrigger + SplitText servidos do próprio site
(`assets/vendor`). `gsap.matchMedia()` com `(prefers-reduced-motion: no-preference)`; sem JS ou
com movimento reduzido, a página é estática e completa. AVIF/WebP com srcset; herói com
`fetchpriority=high`; LCP < 2,5 s; CLS < 0,05; nada a rolar para o lado a 360 px; alvos ≥ 44 px;
foco visível; alt em tudo. JSON-LD Restaurant; OG; favicon; sitemap; robots; 404; `noindex` até
o dono aprovar.

## Proibido neste site

Banco de imagens; fotos de outras lojas; pessoas; IA a inventar comida; preços da Glovo; o nome
do Danilo; prometer reservas, entregas grátis, prazos ou prémios; "desde"; textos copiados de
avaliações; mais de um elemento assinatura.

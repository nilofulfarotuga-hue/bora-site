# Domínios do Bora — quem aponta para onde

> Última alteração: 2026-08-27. Domínio próprio ligado nesta data.

## O que está no ar

| Endereço | Serve | Projecto Cloudflare Pages |
|---|---|---|
| `boraguarda.com` | Site institucional do Bora | `bora-site` |
| `www.boraguarda.com` | O mesmo | `bora-site` |
| `goola.boraguarda.com` | Mini-site da Goola Açaí | `goola-guarda` |
| `ouroeprata.boraguarda.com` | Mini-site da Barbearia Ouro e Prata | `ouro-e-prata` |
| `saboresdobrasil.boraguarda.com` | Mini-site do Sabores do Brasil (Keli) | `sabores-do-brasil` |
| `app.boraguarda.com` | A app no browser | `bora-app-web` |
| `mrkebab.boraguarda.com` | Mini-site do Mr Kebab | `mr-kebab` |
| `festas.boraguarda.com` | Demo da categoria Festas | `demo-festas` |

**Os `.pages.dev` continuam todos a servir e não devem ser desligados** — há
links já enviados a clientes. Cada projecto responde nos dois endereços.

Endereços antigos, todos vivos: `bora-site.pages.dev`, `goola-guarda.pages.dev`,
`ouro-e-prata.pages.dev`, `sabores-do-brasil.pages.dev`,
`bora-app-web.pages.dev` (a app no browser, sem domínio próprio),
`mr-kebab.pages.dev`, `demo-festas.pages.dev`.

Outros domínios da mesma conta, sem relação com o Bora:
`guardafcsad.com` (`guarda-fc`) e `jaiagarwala.com` (`jai-agarwal`).

## Como está montado

O domínio foi comprado dentro da própria Cloudflare, por isso **não há
servidores de nomes para mudar**. A zona `boraguarda.com` está activa na conta
`Nilofulfarotuga@gmail.com's Account`, com os servidores `dante.ns.cloudflare.com`
e `elaine.ns.cloudflare.com`.

Cada endereço é um **CNAME com proxy ligado** (nuvem laranja) a apontar para o
`.pages.dev` do projecto, mais o **custom domain** registado do lado do Pages.
São as duas metades: sem o CNAME o Pages fica eternamente em `pending`; sem o
custom domain o Pages não sabe que aquele endereço é dele.

Na raiz (`boraguarda.com`) o CNAME funciona porque a Cloudflare faz
*CNAME flattening* sozinha.

Certificados emitidos pela Google Trust Services, renovação automática.

## Os DOIS tokens (são precisos os dois)

O ficheiro `.env` desta pasta — que **está no `.gitignore` e nunca entrou em
git** — tem duas variáveis, e não se substituem uma à outra:

- `CLOUDFLARE_API_TOKEN` — **só Pages**. Cria projectos, publica sites e regista
  custom domains. Não vê zonas nem mexe em DNS.
- `CLOUDFLARE_DNS_TOKEN` — **só DNS**, limitado à zona `boraguarda.com`. É este
  que cria os CNAME.

Se um dia os custom domains ficarem presos em `pending`, é quase sempre porque
faltou o registo de DNS — ou seja, faltou usar o segundo token.

## ⚠️ Publicar SEMPRE pelo `deploy-cloudflare.sh`, nunca a pasta inteira

A 2026-08-27 publicou-se esta pasta em bruto, com `wrangler pages deploy` a
apontar para a raiz. Resultado: o `.env` — com os dois tokens lá dentro — ficou
a ser servido em `boraguarda.com/.env`, público, durante horas.

O `deploy-cloudflare.sh` existe exactamente para isso não acontecer: monta uma
cópia com a lista branca do que é público e publica dessa cópia. **Usa-o sempre.**

Ao verificar se um ficheiro está exposto, **olha para o conteúdo, não para o
código de resposta**: o Cloudflare Pages devolve `200` com a página do site para
endereços que não existem, por isso `200` não prova que o ficheiro lá está.

Purgar cache precisa de um token com `Zone > Cache Purge`. Nenhum dos dois
tokens actuais o tem — ou se acrescenta a permissão, ou é o botão
"Purge Everything" no painel.

## Acrescentar um mini-site novo

1. Publicar o site: `wrangler pages deploy <pasta absoluta> --project-name <proj>`
2. Registar o custom domain no projecto (token de Pages):
   `POST /accounts/{acc}/pages/projects/{proj}/domains` com `{"name":"loja.boraguarda.com"}`
3. Criar o CNAME (token de DNS):
   `POST /zones/{zone}/dns_records` com
   `{"type":"CNAME","name":"loja.boraguarda.com","content":"<proj>.pages.dev","proxied":true,"ttl":1}`
4. Esperar. O certificado leva alguns minutos; só depois auditar — auditar cedo
   demais dá falso negativo.
5. Actualizar no site o `canonical`, o `og:url` e o `sitemap.xml`.

**Só se cria subdomínio para lojas que já confirmaram.** Não inventar.

## Detalhe que engana

Depois de criar os registos, o resolver do fornecedor de internet pode continuar
a dizer que o subdomínio não existe durante até **30 minutos** — é o tempo que
ele guarda a resposta negativa anterior (o `default TTL` do SOA da zona).

Nesse intervalo o site já está bom: prova-se forçando o IP, sem depender do
resolver local —

```bash
curl -sS -o /dev/null -w "%{http_code} ssl_verify=%{ssl_verify_result}\n" \
  --resolve "goola.boraguarda.com:443:104.21.74.105" https://goola.boraguarda.com/
```

`200` com `ssl_verify=0` quer dizer que serve e que o certificado é válido.

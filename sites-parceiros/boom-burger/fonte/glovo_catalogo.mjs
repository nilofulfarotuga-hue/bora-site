// Catalogo publico da Boom! Burger na Glovo Guarda (store 539100, address 873866).
// So LEITURA da API publica (mesmos cabecalhos do glovo_walk.js do bora_app).
// Saida: ../origem/glovo/catalogo.json (bruto) e ../origem/glovo/produtos.json (limpo)
// e as fotos dos produtos em ../origem/glovo/fotos/<id>.<ext>.
// Os PRECOS da Glovo sao so referencia (product_price_sources fonte 'glovo'),
// nunca vao para products.price nem para o site.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const SAIDA = path.join(AQUI, '..', 'origem', 'glovo');
fs.mkdirSync(path.join(SAIDA, 'fotos'), { recursive: true });

const STORE = '539100', ADDR = '873866';
const H = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36',
  'Accept': 'application/json',
  'glovo-api-version': '14',
  'glovo-app-platform': 'web',
  'glovo-app-type': 'customer',
  'glovo-location-country-code': 'PT',
  'glovo-location-city-code': 'GRD',
  'glovo-location-latitude': '40.5414484',
  'glovo-location-longitude': '-7.261693',
  'glovo-language-code': 'pt',
  'Origin': 'https://glovoapp.com',
  'Referer': 'https://glovoapp.com/pt/pt/guarda/stores/boom-burger-hamburgueria-artesanal-grd',
};

async function get(url) {
  const r = await fetch(url, { headers: H });
  const t = await r.text();
  if (!r.ok) throw new Error(`${r.status} ${url} ${t.slice(0, 200)}`);
  return JSON.parse(t);
}

const main = await get(`https://api.glovoapp.com/v4/stores/${STORE}/addresses/${ADDR}/content/main`);
fs.writeFileSync(path.join(SAIDA, 'catalogo-main.json'), JSON.stringify(main, null, 1));

// Percorre a arvore e apanha todos os PRODUCT_ROW/PRODUCT_TILE, com a seccao onde estao.
const produtos = [];
const visto = new Set();
const links = new Set();
function walk(n, seccao) {
  if (!n || typeof n !== 'object') return;
  if (Array.isArray(n)) { n.forEach((x) => walk(x, seccao)); return; }
  let sec = seccao;
  if ((n.type === 'LIST' || n.type === 'GRID' || n.type === 'CAROUSEL') && n.data && n.data.title) sec = n.data.title;
  if (n.data && n.data.action && n.data.action.data && n.data.action.data.path) links.add(n.data.action.data.path);
  if (n.type && /PRODUCT/.test(n.type) && n.data && n.data.id != null) {
    const d = n.data;
    if (!visto.has(d.id)) {
      visto.add(d.id);
      produtos.push({
        glovo_id: d.id,
        external_id: d.externalId || null,
        nome: d.name,
        descricao: d.description || '',
        seccao: sec || null,
        preco_glovo: d.price ?? null,
        foto: d.imageUrl || (d.images && d.images[0] && d.images[0].imageUrl) || null,
        atributos: d.attributeGroups || [],
        tags: d.tags || [],
        promocao: d.promotion || d.promotions || null,
        bruto_chaves: Object.keys(d),
      });
    }
  }
  for (const k of Object.keys(n)) if (k !== 'data' || !(n.type && /PRODUCT/.test(n.type))) walk(n[k], sec);
}
walk(main, null);
console.log('main: produtos', produtos.length, 'links', links.size);

// Se o main so trouxer as categorias, segue cada link de categoria.
for (const l of links) {
  try {
    const sub = await get(`https://api.glovoapp.com/v4/stores/${STORE}/addresses/${ADDR}/content?nodeType=DEEP_LINK&link=${encodeURIComponent(l)}`);
    const antes = produtos.length;
    walk(sub, null);
    console.log('link', l, '+', produtos.length - antes);
  } catch (e) {
    console.log('link falhou', l, e.message.slice(0, 120));
  }
}

fs.writeFileSync(path.join(SAIDA, 'produtos.json'), JSON.stringify(produtos, null, 1));
console.log('TOTAL produtos', produtos.length);

// Fotos (originais da Glovo = fotos do proprio cliente, segundo o dono).
let n = 0;
for (const p of produtos) {
  if (!p.foto) continue;
  const url = p.foto.replace(/\/image\/upload\/[^/]*\//, '/image/upload/');
  try {
    const r = await fetch(url, { headers: { 'User-Agent': H['User-Agent'] } });
    if (!r.ok) { console.log('foto', r.status, p.nome); continue; }
    const b = Buffer.from(await r.arrayBuffer());
    let ext = 'jpg';
    if (b[0] === 0x89) ext = 'png'; else if (b.slice(8, 12).toString() === 'WEBP') ext = 'webp'; else if (b.slice(4, 12).toString().includes('ftypavif')) ext = 'avif';
    const f = path.join(SAIDA, 'fotos', `${p.glovo_id}.${ext}`);
    fs.writeFileSync(f, b);
    p.foto_local = path.basename(f);
    p.foto_bytes = b.length;
    n++;
  } catch (e) { console.log('foto erro', p.nome, e.message); }
}
fs.writeFileSync(path.join(SAIDA, 'produtos.json'), JSON.stringify(produtos, null, 1));
console.log('fotos', n);

// Puxa os quatro sites pelo ENDERECO PUBLICO e fotografa o bloco das duas
// portas, no computador e no telemovel. Nada de ficheiros locais: o que conta
// e o que o visitante recebe.
const path = require('path');
const SCRAPER = 'C:/Users/danil/Desktop/projetosflutter/bora_app/scripts/scraper/node_modules';
module.paths.push(SCRAPER);
const { chromium } = require(path.join(SCRAPER, 'playwright'));

const SITES = [
  ['bora',    'https://boraguarda.com/',                 'Descarregar a app'],
  ['goola',   'https://goola.boraguarda.com/',           'Descarregar a app'],
  ['ouro',    'https://ouroeprata.boraguarda.com/',      'Descarregar a app'],
  ['sabores', 'https://saboresdobrasil.boraguarda.com/', 'Descarregar a app'],
];
const ECRAS = [['desk', 1440, 900], ['tel', 390, 844]];

(async () => {
  const b = await chromium.launch({ channel: 'chrome' });
  for (const [nome, url, texto] of SITES) {
    for (const [ecra, w, h] of ECRAS) {
      const p = await b.newPage({ viewport: { width: w, height: h } });
      await p.goto(url + '?prova=' + Date.now(), { waitUntil: 'networkidle', timeout: 90000 });
      await p.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 400) {
          window.scrollTo(0, y); await new Promise(r => setTimeout(r, 50));
        }
      });
      await p.waitForTimeout(1200);

      const alvo = p.locator(`text=${texto}`).first();
      let achou = false;
      try {
        await alvo.scrollIntoViewIfNeeded({ timeout: 8000 });
        await p.waitForTimeout(700);
        achou = true;
      } catch (e) { /* fica a foto da pagina toda */ }

      const f = `${__dirname}/${nome}_${ecra}.png`;
      await p.screenshot({ path: f });

      // conta os dois botoes e confirma para onde apontam
      const links = await p.evaluate(() => {
        const a = [...document.querySelectorAll('a')];
        const play = a.filter(x => (x.href || '').includes('play.google.com')).length;
        const web = a.filter(x => (x.href || '').includes('app.boraguarda.com')).length;
        return { play, web };
      });
      console.log(`  ${nome.padEnd(8)} ${ecra}  bloco visivel=${achou}  play=${links.play} site=${links.web}`);
      await p.close();
    }
  }
  await b.close();
})();

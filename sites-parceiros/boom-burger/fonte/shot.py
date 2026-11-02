# -*- coding: utf-8 -*-
"""Provas do site (B.10): capturas + medidas, com e sem "Reduzir movimento".

Uso: python shot.py <url> <prefixo>   (ex.: http://127.0.0.1:8765/ local)
Gera bora-site/provas/boom-burger/<prefixo>-*.png e <prefixo>-medidas.json:
  erros de consola, scroll lateral a 360, alvos de toque < 44 px, imagens sem alt,
  LCP e CLS (PerformanceObserver), altura do botao fixo, estado da cena das camadas.
"""
import json, os, sys, time
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
PROVAS = os.path.abspath(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger'))
os.makedirs(PROVAS, exist_ok=True)
URL, PRE = sys.argv[1], sys.argv[2]
UA_I = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
UA_A = 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
OBS = """() => { window.__lcp=0; window.__cls=0;
 new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});
 new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value}).observe({type:'layout-shift',buffered:true}); }"""
MEDE = """() => {
 const de=document.documentElement, r={};
 r.scroll_lateral = de.scrollWidth - de.clientWidth;
 r.largos = [...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect();return b.right>de.clientWidth+1 && getComputedStyle(e).position!=='fixed' && !e.closest('.fav-lista,.menu-abas')}).slice(0,5).map(e=>e.className||e.tagName);
 r.alvos_pequenos = [...document.querySelectorAll('a,button')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&(b.height<44||b.width<44)&&getComputedStyle(e).visibility!=='hidden'}).map(e=>(e.innerText||e.getAttribute('aria-label')||e.className).trim().slice(0,30)).slice(0,12);
 r.img_sem_alt = [...document.querySelectorAll('img')].filter(i=>!i.hasAttribute('alt')).length;
 const b=document.querySelector('.barra-pedir .btn'); r.barra_altura = b ? Math.round(b.getBoundingClientRect().height) : null;
 r.barra_visivel = b ? getComputedStyle(document.querySelector('.barra-pedir')).display!=='none' : false;
 r.anima = de.classList.contains('anima');
 r.h1 = document.querySelector('h1').innerText.slice(0,80);
 const mk = document.querySelector('.heroi h1 [class*=mask]'); r.mascara = mk ? mk.className + ' pt=' + getComputedStyle(mk).paddingTop : null;
 r.precos_sem = document.querySelectorAll('.preco.sem').length; r.precos = document.querySelectorAll('.preco').length;
 r.lcp = Math.round(window.__lcp||0); r.cls = Math.round((window.__cls||0)*1000)/1000;
 return r; }"""


def corre(b, nome, vp, mobile, ua, reduz):
    ctx = b.new_context(viewport=vp, device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile,
                        user_agent=ua, locale='pt-PT', reduced_motion='reduce' if reduz else 'no-preference')
    pg = ctx.new_page()
    erros = []
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.add_init_script(OBS.replace('() => {', '', 1).rsplit('}', 1)[0])
    pg.goto(URL, wait_until='load', timeout=90000)
    time.sleep(2.5)
    pg.screenshot(path=os.path.join(PROVAS, f'{PRE}-{nome}-heroi.png'))
    m = pg.evaluate(MEDE)
    # cena das camadas: meio e fim
    # o GSAP so carrega ao primeiro gesto: simular um, esperar, e so depois medir o pin
    pg.mouse.wheel(0, 1)
    time.sleep(2.5)
    pg.evaluate('window.scrollTo(0,0)')
    time.sleep(0.8)
    # inicio real do pin (o offsetTop da secao fixada e relativo ao pin-spacer)
    y0 = pg.evaluate("(()=>{const st=window.ScrollTrigger&&ScrollTrigger.getAll().find(t=>t.trigger&&t.trigger.id==='camadas');"
                     "return st?st.start:document.querySelector('#camadas').getBoundingClientRect().top+scrollY})()")
    alturas = {}
    for k, frac in (('cena-inicio', 0.05), ('cena-meio', 0.9), ('cena-fim', 2.3)):
        pg.evaluate(f'window.scrollTo(0,{y0} + window.innerHeight*{frac})')
        time.sleep(1.6)
        pg.screenshot(path=os.path.join(PROVAS, f'{PRE}-{nome}-{k}.png'))
    for sec in ('favoritos', 'boom', 'menu', 'casa', 'na-chapa', 'galeria', 'visita'):
        pg.evaluate(f"document.getElementById('{sec}').scrollIntoView({{block:'start'}})")
        time.sleep(1.4)
        pg.screenshot(path=os.path.join(PROVAS, f'{PRE}-{nome}-{sec}.png'))
    pg.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(1.5)
    pg.screenshot(path=os.path.join(PROVAS, f'{PRE}-{nome}-rodape.png'))
    m2 = pg.evaluate(MEDE)
    m['cls_fim'] = m2['cls']
    m['video'] = pg.evaluate("(()=>{const v=document.querySelector('video');return {carregado:!!v.dataset.carregado,pausa:v.paused,src:v.currentSrc.split('/').pop(),rs:v.readyState}})()")
    m['estado_agora'] = pg.evaluate("document.querySelector('.estado-agora').innerText")
    m['erros'] = erros[:10]
    ctx.close()
    return m


res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for nome, vp, mob, ua in (('390', {'width': 390, 'height': 844}, True, UA_I), ('360', {'width': 360, 'height': 780}, True, UA_A),
                              ('1440', {'width': 1440, 'height': 900}, False, None)):
        for reduz in (False, True):
            k = nome + ('-reduz' if reduz else '')
            try:
                res[k] = corre(b, k, vp, mob, ua, reduz)
            except Exception as e:
                res[k] = {'falhou': str(e)[:300]}
            print(k, json.dumps(res[k], ensure_ascii=False)[:700])
    b.close()
json.dump(res, open(os.path.join(PROVAS, f'{PRE}-medidas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

/* Boom! Burger — comportamento do site.
   Regra de ouro: sem JS, ou com "Reduzir movimento" ligado, a pagina e estatica e completa.
   So se esconde/anima depois de confirmar que o GSAP carregou E que o movimento e permitido. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var reduz = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- cabecalho que muda ao descer ---------- */
  var cab = document.querySelector('.cab');
  function cabecalho() { if (cab) cab.classList.toggle('cheio', window.scrollY > 40); }
  cabecalho();
  window.addEventListener('scroll', cabecalho, { passive: true });

  /* barra fixa do telemovel: so quando o botao do heroi saiu do ecra (2.a ronda: dois botoes iguais empilhados) */
  var barra = document.querySelector('.barra-pedir');
  var btnHeroi = document.querySelector('.heroi .btn-pedir');
  if (barra && btnHeroi && 'IntersectionObserver' in window) {
    /* um botao de pedir de cada vez: a barra esconde-se enquanto houver outro a vista
       (o do heroi, o da cena) e enquanto ainda nao se passou o heroi */
    barra.classList.add('escondida');
    var visiveis = new Set();
    var outros = [].slice.call(document.querySelectorAll('main .btn-pedir'));
    var decide = function () {
      var acimaDoHeroi = btnHeroi.getBoundingClientRect().top > window.innerHeight;
      barra.classList.toggle('escondida', visiveis.size > 0 || acimaDoHeroi);
    };
    var io2 = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) { if (e.isIntersecting) visiveis.add(e.target); else visiveis.delete(e.target); });
      decide();
    });
    outros.forEach(function (b) { io2.observe(b); });
  }

  /* Tudo o que nao e preciso para o primeiro ecra corre quando o browser estiver livre
     (Lighthouse: o arranque do site.js era uma tarefa longa que atrasava o desenho do heroi). */
  function quandoLivre(fn) {
    var corre = function () { if ('requestIdleCallback' in window) window.requestIdleCallback(fn, { timeout: 2500 }); else setTimeout(fn, 300); };
    if (document.readyState === 'complete') corre(); else window.addEventListener('load', corre);
  }
  /* cada tarefa num pedaco proprio: nenhuma passa dos 50 ms de uma vez */
  [precosVivos, abertoAgora, abasMenu, videoPreguicoso].forEach(quandoLivre);
  function precosVivos() {
  /* ---------- precos vivos (os mesmos da app) ---------- */
  var SB = window.BOOM_SB;
  var eur = new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' });
  if (SB && window.fetch) {
    fetch(SB.url + '/rest/v1/products?restaurant_id=eq.' + SB.loja + '&select=id,price,is_available', {
      headers: { apikey: SB.chave, Authorization: 'Bearer ' + SB.chave }
    }).then(function (r) { return r.ok ? r.json() : []; }).then(function (lista) {
      if (!lista || !lista.length) return;
      var m = {};
      lista.forEach(function (p) { m[p.id] = p; });
      document.querySelectorAll('.preco[data-id]').forEach(function (el) {
        var p = m[el.getAttribute('data-id')];
        if (p && p.price != null) { el.textContent = eur.format(Number(p.price)); el.classList.remove('sem'); }
      });
      var aviso = document.querySelector('.aviso-precos');
      if (aviso) aviso.textContent = 'Preços iguais aos da app Bora, atualizados agora.';
    }).catch(function () { /* fica o que veio no build */ });
  }

  }
  function abertoAgora() {
  /* ---------- aberto agora (hora de Lisboa) ---------- */
  var HORAS = { 0: [], 1: [[1140, 1350]], 2: [[720, 870], [1140, 1350]], 3: [[720, 870], [1140, 1350]],
    4: [[720, 870], [1140, 1350]], 5: [[720, 870], [1140, 1350]], 6: [[720, 870], [1140, 1350]] };
  function hm(m) { return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); }
  try {
    var partes = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Lisbon', weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date());
    var p = {}; partes.forEach(function (x) { p[x.type] = x.value; });
    var dia = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[p.weekday];
    var agora = parseInt(p.hour, 10) * 60 + parseInt(p.minute, 10);
    var linha = document.querySelector('.horario tr[data-dia="' + dia + '"]');
    if (linha) linha.classList.add('hoje');
    var est = document.querySelector('.estado-agora');
    if (est) {
      var aberto = null, prox = null;
      (HORAS[dia] || []).forEach(function (j) { if (agora >= j[0] && agora < j[1]) aberto = j; if (agora < j[0] && prox === null) prox = j; });
      if (aberto) { est.textContent = 'Aberto agora · fecha às ' + hm(aberto[1]); est.classList.add('aberto'); }
      else if (prox) { est.textContent = 'Fechado agora · abre hoje às ' + hm(prox[0]); }
      else {
        for (var k = 1; k <= 7; k++) { var d = (dia + k) % 7; if (HORAS[d].length) { est.textContent = 'Fechado agora · abre ' + (k === 1 ? 'amanhã' : ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'][d]) + ' às ' + hm(HORAS[d][0][0]); break; } }
      }
    }
  } catch (e) { /* sem Intl: fica o horario escrito */ }

  }
  function abasMenu() {
  /* ---------- abas do menu ---------- */
  var abas = document.querySelectorAll('.menu-abas a');
  if ('IntersectionObserver' in window && abas.length) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) {
        if (!e.isIntersecting) return;
        abas.forEach(function (a) {
          var on = a.getAttribute('href') === '#' + e.target.id;
          a.classList.toggle('ativa', on);
          if (on && a.scrollIntoView && a.parentNode.scrollWidth > a.parentNode.clientWidth) {
            a.parentNode.scrollTo({ left: a.offsetLeft - 16, behavior: reduz ? 'auto' : 'smooth' });
          }
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    document.querySelectorAll('.menu-cat').forEach(function (s) { io.observe(s); });
  }

  }
  function videoPreguicoso() {
  /* ---------- video: so carrega ao chegar perto; nunca no heroi ---------- */
  var v = document.querySelector('.chapa-video video');
  if (v) {
    if (reduz) { v.removeAttribute('autoplay'); v.controls = true; }
    var carregar = function () {
      if (v.dataset.carregado) return;
      v.querySelectorAll('source[data-src]').forEach(function (s) { s.src = s.getAttribute('data-src'); });
      v.load(); v.dataset.carregado = '1';
    };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (ents) {
        ents.forEach(function (e) {
          if (e.isIntersecting) { carregar(); if (!reduz) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); } }
          else if (!v.paused) v.pause();
        });
      }, { rootMargin: '250px 0px' }).observe(v);
    } else { carregar(); }
  }
  } /* fim das tarefas de fundo */

  /* ---------- animacao: so com GSAP e movimento permitido ---------- */
  if (reduz) return;

  /* o logotipo do heroi monta-se em CSS (site.css). Aqui: reage ao cursor, so com rato */
  var logo = document.querySelector('.heroi .logo-monta');
  if (logo && window.matchMedia('(pointer:fine)').matches) {
    var pendente = false, ex = 0, ey = 0;
    window.addEventListener('pointermove', function (e) {
      ex = e.clientX; ey = e.clientY;
      if (pendente) return;
      pendente = true;
      requestAnimationFrame(function () {
        pendente = false;
        logo.style.transform = 'perspective(700px) rotateY(' + ((ex / window.innerWidth - 0.5) * 16).toFixed(2) +
          'deg) rotateX(' + ((ey / window.innerHeight - 0.5) * -12).toFixed(2) + 'deg)';
      });
    }, { passive: true });
  }
  /* o logotipo do rodape volta a montar-se quando aparece */
  var rod = document.querySelector('.rodape .logo-monta');
  if (rod && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (ents, ob) {
      ents.forEach(function (e) { if (e.isIntersecting) { rod.classList.add('visto'); ob.disconnect(); } });
    }, { rootMargin: '0px 0px -8% 0px' }).observe(rod);
  } else if (rod) { rod.classList.add('visto'); }

  /* GSAP so depois de a pagina estar pronta: nao atrasa o primeiro ecra (Lighthouse) */
  function script(src) {
    return new Promise(function (ok, ko) {
      var s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = ko; document.head.appendChild(s);
    });
  }
  function arranca() {
    script('assets/vendor/gsap.min.js').then(function () { return script('assets/vendor/ScrollTrigger.min.js'); })
      .then(iniciaGsap).catch(function () { /* sem GSAP: fica a versao estatica, completa */ });
  }
  /* so quando a pessoa mexe na pagina (descer, tocar, tecla): a cena esta abaixo do primeiro ecra,
     e quem nao desce nao paga o custo. Ate la, a versao estatica esta completa. */
  var EVENTOS = ['scroll', 'wheel', 'touchstart', 'pointerdown', 'keydown'];
  var iniciado = false;
  function primeiroGesto(ev) {
    if (iniciado) return;
    /* um "scroll" sem a pagina ter descido (redimensionar, capturas do Lighthouse) nao conta */
    if (ev && ev.type === 'scroll' && window.scrollY < 40) return;
    iniciado = true;
    EVENTOS.forEach(function (ev) { window.removeEventListener(ev, primeiroGesto, true); });
    arranca();
  }
  EVENTOS.forEach(function (ev) { window.addEventListener(ev, primeiroGesto, { capture: true, passive: true }); });
  if (window.scrollY > 40) primeiroGesto();

  function iniciaGsap() {
  var gsap = window.gsap;
  if (!gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(window.ScrollTrigger);
  doc.classList.add('anima');
  var mm = gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)', function () {
    /* CENA: o Portobello real monta-se camada a camada */
    var cena = document.querySelector('.cena');
    var camadas = gsap.utils.toArray('.cena-palco .camada');
    var legendas = gsap.utils.toArray('.cena-legendas li');
    if (cena && camadas.length) {
      var palco = document.querySelector('.cena-palco');
      var fecho = document.querySelector('.cena-fecho');
      var solida = document.querySelector('.cena-palco .solida');
      var n = camadas.length;
      var rot = [-7, 5, -4, 6, -5, 4];
      /* no telemovel o palco fica por cima do texto: afastar menos para nao passar por cima do titulo */
      /* o recheio (camadas do meio) entra primeiro; os paes chegam juntos, como no logotipo */
      var meio = function (i) { return i > 0 && i < n - 1; };
      var afasta = function () { return window.innerWidth < 900 ? 0.34 : 0.5; };
      var marcaLegenda = function (i) { legendas.forEach(function (li, k) { li.classList.toggle('ativa', k === i); }); };
      marcaLegenda(0);
      var tl = gsap.timeline({
        defaults: { ease: 'back.out(1.5)' },
        scrollTrigger: {
          trigger: cena, start: 'top top', end: 'bottom bottom', scrub: 0.8, invalidateOnRefresh: true,
          onUpdate: function (st) { marcaLegenda(Math.min(legendas.length - 1, Math.floor(st.progress * 1.25 * legendas.length))); }
        }
      });
      camadas.forEach(function (c, i) {
        tl.fromTo(c,
          { y: function () { return (i - (n - 1) / 2) * palco.offsetHeight * afasta(); },
            x: meio(i) ? 0 : (i % 2 ? 1 : -1) * 14, rotation: meio(i) ? 0 : rot[i % rot.length],
            scale: meio(i) ? 0.9 : 1, autoAlpha: meio(i) ? 0.2 : 0.35 },
          { y: 0, x: 0, rotation: 0, scale: 1, autoAlpha: 1, duration: 1 }, meio(i) ? 0 : 0.45 + (i === 0 ? 0 : 0.05));
      });
      tl.to(solida, { autoAlpha: 1, duration: 0.25, ease: 'none' }, '>-0.05')
        .to(palco, { scale: 1.04, duration: 0.3, ease: 'power2.out' }, '<')
        .to(palco, { autoAlpha: 0, scale: 0.92, duration: 0.45, ease: 'power2.in' }, '>+0.25')
        .fromTo(fecho, { autoAlpha: 0, y: 30 }, { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power2.out' }, '<0.15');
    }

    /* revelacoes curtas ao descer — so o que ainda esta abaixo do ecra (nada pisca) */
    var abaixo = gsap.utils.toArray('.revela').filter(function (el) { return el.getBoundingClientRect().top > window.innerHeight; });
    gsap.set(abaixo, { autoAlpha: 0, y: 28 });
    if (abaixo.length) {
      window.ScrollTrigger.batch(abaixo, {
        start: 'top 88%', once: true,
        onEnter: function (b) { gsap.to(b, { autoAlpha: 1, y: 0, duration: 0.7, stagger: 0.08, ease: 'power3.out', overwrite: true }); }
      });
    }
    return function () { doc.classList.remove('anima'); };
  });
  /* fontes e imagens mudam alturas: recalcular */
  window.ScrollTrigger.refresh();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { window.ScrollTrigger.refresh(); });
  }
})();

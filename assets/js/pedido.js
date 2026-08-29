/* =========================================================================
   A história do pedido — cena assinatura da montra.
   Missão site-premio-montra-bora, 2026-08-29.

   Duas peças, ambas com a mesma regra: o estado por omissão é VISÍVEL.
   É este ficheiro que passa a esconder, e só depois de confirmar que pode.
   Se o JavaScript não correr, a história lê-se em lista e as duas portas
   ficam à vista. Nada de informação desaparece.

     1. A cena que se fixa e monta o pedido passo a passo.
     2. As duas portas coladas ao fundo, no telemóvel.
   ========================================================================= */
(function () {
  'use strict';

  var menosMovimento = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------------------------------------------------------------- 1 */
  (function cena() {
    var sec = document.getElementById('historia-do-pedido');
    if (!sec || !('IntersectionObserver' in window)) return;

    var passos = Array.prototype.slice.call(sec.querySelectorAll('[data-passo]'));
    var fotos = Array.prototype.slice.call(sec.querySelectorAll('[data-foto]'));
    var barra = document.getElementById('pedido-progresso');
    if (!passos.length || passos.length !== fotos.length) return;

    // Só a partir daqui é que o CSS passa a fixar e a esconder.
    document.body.classList.add('js-pedido');

    // Com movimento reduzido a classe fica (o CSS trata de a neutralizar),
    // mas não se liga ouvinte de scroll nenhum.
    if (menosMovimento.matches) {
      passos.forEach(function (p) { p.classList.add('activo'); });
      fotos.forEach(function (f) { f.classList.add('activa'); });
      return;
    }

    var actual = -1, pedido = null, ligado = false;

    function mostrar(i) {
      if (i === actual) return;
      actual = i;
      passos.forEach(function (p, n) { p.classList.toggle('activo', n === i); });
      fotos.forEach(function (f, n) { f.classList.toggle('activa', n === i); });
    }

    function desenhar() {
      pedido = null;
      var r = sec.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      if (total <= 0) { mostrar(0); return; }

      var andado = Math.min(Math.max(-r.top / total, 0), 1);
      if (barra) barra.style.width = (andado * 100).toFixed(1) + '%';

      // Uma margem no fim para o último passo não passar a correr.
      var i = Math.floor(andado * passos.length * 0.98);
      mostrar(Math.min(i, passos.length - 1));
    }

    function pedir() { if (pedido === null) pedido = requestAnimationFrame(desenhar); }

    // O ouvinte de scroll só existe enquanto a cena está no ecrã.
    new IntersectionObserver(function (ents) {
      ents.forEach(function (e) {
        if (e.isIntersecting && !ligado) {
          window.addEventListener('scroll', pedir, { passive: true });
          window.addEventListener('resize', pedir);
          ligado = true;
          pedir();
        } else if (!e.isIntersecting && ligado) {
          window.removeEventListener('scroll', pedir);
          window.removeEventListener('resize', pedir);
          ligado = false;
        }
      });
    }, { rootMargin: '250px' }).observe(sec);

    mostrar(0);

    // Se a pessoa mudar a preferência a meio, devolve-se tudo ao visível.
    menosMovimento.addEventListener('change', function (ev) {
      if (!ev.matches) return;
      if (ligado) { window.removeEventListener('scroll', pedir); ligado = false; }
      passos.forEach(function (p) { p.classList.add('activo'); });
      fotos.forEach(function (f) { f.classList.add('activa'); });
    });
  })();

  /* ----------------------------------------------------------------- 2
     As duas portas coladas ao fundo nao precisam de JavaScript nenhum: sao
     CSS puro e estao la desde o primeiro segundo. Tinham um atraso ate a
     pessoa descer meio ecra, e isso deixava o heroi do telemovel sem elas —
     logo no sitio onde a accao principal tem de estar a vista. (2026-08-29) */
})();

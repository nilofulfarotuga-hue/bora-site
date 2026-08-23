/* Animação das páginas geradas do bora-site.
 *
 * Sem bibliotecas, sem build, sem WebGL. Tudo o que se mexe aqui é
 * transform/opacity — o que o compositor faz de graça e o que o Chromium
 * headless do estúdio consegue mesmo filmar (fundos WebGL saem pretos).
 *
 * Regras que este ficheiro cumpre:
 *   - quem tem "menos movimento" ligado no telemóvel vê o site QUIETO e
 *     COMPLETO: nem sequer marcamos nada para revelar;
 *   - sem JS, o site também aparece completo — o CSS só esconde o que vai
 *     revelar depois de a classe `anim` existir no <html>;
 *   - cada coisa revela UMA vez e o observador larga-a.
 */
(function () {
  var mq = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  if (mq && mq.matches) return;

  var raiz = document.documentElement;
  raiz.classList.add('anim');

  var alvos = document.querySelectorAll('.bloco, .capa-in, .cat-topo .wrap');
  var numeros = document.querySelectorAll('.numeros b');

  function revelarTudo() {
    for (var i = 0; i < alvos.length; i++) alvos[i].classList.add('on');
    for (var j = 0; j < numeros.length; j++) numeros[j].classList.add('on');
  }

  if (!('IntersectionObserver' in window)) { revelarTudo(); return; }

  for (var i = 0; i < alvos.length; i++) alvos[i].classList.add('rev');

  var obs = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('on');
      obs.unobserve(e.target);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -5% 0px' });

  for (var k = 0; k < alvos.length; k++) obs.observe(alvos[k]);

  /* Números a contar. Só arranca quando o número entra no ecrã — senão
     ficava um "0" pendurado numa secção que ninguém chegou a ver. */
  function contar(el) {
    var m = el.textContent.trim().match(/^(\d+)(.*)$/);
    if (!m) return;
    var fim = parseInt(m[1], 10), sufixo = m[2] || '';
    if (!fim) return;                 // "0€" não tem contagem nenhuma para fazer
    var t0 = null, dur = 900;
    el.textContent = '0' + sufixo;
    requestAnimationFrame(function passo(agora) {
      if (t0 === null) t0 = agora;
      var p = Math.min(1, (agora - t0) / dur);
      el.textContent = Math.round(fim * (1 - Math.pow(1 - p, 3))) + sufixo;
      if (p < 1) requestAnimationFrame(passo);
    });
  }

  var obsNum = new IntersectionObserver(function (entradas) {
    entradas.forEach(function (e) {
      if (!e.isIntersecting) return;
      contar(e.target);
      obsNum.unobserve(e.target);
    });
  }, { threshold: 0.6 });

  for (var n = 0; n < numeros.length; n++) obsNum.observe(numeros[n]);
})();

/* ============================================================
   Bora — Cinema scroll-driven (GSAP ScrollTrigger)
   Palco fixo (sticky) + crossfade + Ken Burns + legendas por palavra.
   Degrada em pilha estática sem GSAP ou com prefers-reduced-motion.
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasGsap = !!(window.gsap && window.ScrollTrigger);

  if (hasGsap) gsap.registerPlugin(ScrollTrigger);

  /* ---------- CINEMA ---------- */
  var cinema = document.querySelector('.cinema');
  if (cinema) {
    var scenes = Array.prototype.slice.call(cinema.querySelectorAll('.cine-scene'));
    var dotsWrap = cinema.querySelector('.cine-dots');
    var hint = cinema.querySelector('.cine-hint');

    // Construir os dots de capítulo
    if (dotsWrap) {
      scenes.forEach(function (_, i) {
        var d = document.createElement('span');
        d.className = 'cine-dot' + (i === 0 ? ' active' : '');
        dotsWrap.appendChild(d);
      });
    }
    var dots = dotsWrap ? Array.prototype.slice.call(dotsWrap.querySelectorAll('.cine-dot')) : [];

    if (hasGsap && !reduceMotion) {
      cinema.classList.add('is-live');

      var imgs = scenes.map(function (s) { return s.querySelector('.cine-img'); });
      var wordsByScene = scenes.map(function (s) {
        return Array.prototype.slice.call(s.querySelectorAll('.cine-word'));
      });

      scenes.forEach(function (s, i) { gsap.set(s, { opacity: i === 0 ? 1 : 0 }); });
      imgs.forEach(function (im) { if (im) gsap.set(im, { scale: 1.05 }); });
      wordsByScene.forEach(function (words, i) {
        if (i === 0) return; // primeiro capítulo já visível no topo
        gsap.set(words, { opacity: 0, y: '0.7em' });
      });

      var HOLD = 0.85; // permanência de cada cena
      var TR = 0.55;   // duração do crossfade

      var tl = gsap.timeline({
        scrollTrigger: {
          trigger: cinema,
          start: 'top top',
          end: 'bottom bottom',
          scrub: 1,
          onUpdate: function (self) {
            var idx = Math.min(scenes.length - 1, Math.round(self.progress * (scenes.length - 1)));
            for (var k = 0; k < dots.length; k++) dots[k].classList.toggle('active', k === idx);
            if (hint) hint.style.opacity = self.progress > 0.04 ? '0' : '1';
          }
        }
      });

      if (imgs[0]) tl.fromTo(imgs[0], { scale: 1.05 }, { scale: 1.16, ease: 'none', duration: HOLD + TR }, 0);
      var pos = HOLD;

      for (var i = 1; i < scenes.length; i++) {
        tl.to(scenes[i - 1], { opacity: 0, ease: 'power1.inOut', duration: TR }, pos);
        tl.fromTo(scenes[i], { opacity: 0 }, { opacity: 1, ease: 'power1.inOut', duration: TR }, pos);
        if (imgs[i]) tl.fromTo(imgs[i], { scale: 1.05 }, { scale: 1.16, ease: 'none', duration: HOLD + TR }, pos);
        if (wordsByScene[i].length) {
          tl.fromTo(
            wordsByScene[i],
            { opacity: 0, y: '0.7em' },
            { opacity: 1, y: '0em', ease: 'power2.out', duration: TR * 0.9, stagger: 0.05 },
            pos + TR * 0.45
          );
        }
        pos += TR + HOLD;
      }

      window.addEventListener('load', function () { ScrollTrigger.refresh(); });
    }
  }

  /* ---------- Parallax leve (divisórias) ---------- */
  if (hasGsap && !reduceMotion) {
    gsap.utils.toArray('[data-parallax]').forEach(function (el) {
      gsap.fromTo(
        el,
        { yPercent: -10 },
        {
          yPercent: 10,
          ease: 'none',
          scrollTrigger: { trigger: el.parentElement, start: 'top bottom', end: 'bottom top', scrub: true }
        }
      );
    });
  }
});

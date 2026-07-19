document.addEventListener('DOMContentLoaded', function () {
  if (!window.gsap || !window.ScrollTrigger) return;

  gsap.registerPlugin(ScrollTrigger);

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!reduceMotion) {
    document.querySelectorAll('[data-reveal]').forEach(function (el) {
      gsap.from(el, {
        opacity: 0,
        y: 30,
        duration: 0.7,
        ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 85%' }
      });
    });

    document.querySelectorAll('[data-reveal-stagger]').forEach(function (group) {
      gsap.from(group.children, {
        opacity: 0,
        y: 24,
        duration: 0.6,
        ease: 'power2.out',
        stagger: 0.06,
        scrollTrigger: { trigger: group, start: 'top 85%' }
      });
    });

  }

  document.querySelectorAll('.bora-counter').forEach(function (el) {
    var target = parseInt(el.getAttribute('data-target'), 10) || 0;
    ScrollTrigger.create({
      trigger: el,
      start: 'top 90%',
      once: true,
      onEnter: function () {
        var counter = { value: 0 };
        gsap.to(counter, {
          value: target,
          duration: 1.2,
          ease: 'power1.out',
          onUpdate: function () {
            el.textContent = Math.round(counter.value);
          }
        });
      }
    });
  });
});

/* =========================================================================
   Formulário que abre o WhatsApp já preenchido.
   Componente 9 da caixa de ferramentas (components-premio/).
   Missão site-premio-montra-bora, 2026-08-29.

   É a peça que transforma um site numa máquina de orçamentos: a pessoa
   escolhe, carrega uma vez, e a conversa abre com tudo escrito. Ela só tem
   de carregar em enviar. Não precisa de servidor nenhum.

   COMO SE USA
     - qualquer campo com [data-msg] entra na mensagem
     - o texto de data-msg é o rótulo que aparece no WhatsApp
     - a ordem da mensagem é a ordem em que os campos aparecem no HTML
     - #resumo-txt (se existir) mostra a mensagem antes de a pessoa carregar
     - o formulário pode declarar data-abertura="..." para trocar a 1ª linha

   DETALHES QUE JÁ CUSTARAM CARO
     - encodeURIComponent em tudo: um "&" no nome partia o link inteiro
     - api.whatsapp.com/send funciona em computador E telemóvel; o wa.me
       às vezes salta para uma página intermédia no desktop
     - rel/noopener na janela nova, senão o site fica preso quando a app abre
     - se o browser bloquear a janela, segue-se na mesma aba em vez de falhar
       em silêncio
   ========================================================================= */
(function () {
  'use strict';

  var NUMERO = '351937501673';   // internacional, sem + e sem espaços
  var ABERTURA_POR_OMISSAO = 'Olá! Vi o site e queria falar sobre um site para o meu negócio.';

  document.querySelectorAll('form[id="fwa"], form[data-whatsapp]').forEach(function (form) {
    var saida = form.querySelector('#resumo-txt') ||
                (form.parentElement && form.parentElement.querySelector('#resumo-txt'));
    var abertura = form.getAttribute('data-abertura') || ABERTURA_POR_OMISSAO;

    function valorDe(el) {
      if (el.type === 'radio' || el.type === 'checkbox') {
        if (el.type === 'checkbox') {
          var marcados = form.querySelectorAll('[name="' + el.name + '"]:checked');
          return Array.prototype.map.call(marcados, function (c) { return c.value; }).join(', ');
        }
        var m = form.querySelector('[name="' + el.name + '"]:checked');
        return m ? m.value : '';
      }
      return (el.value || '').trim();
    }

    function linhas() {
      var vistos = {}, out = [];
      form.querySelectorAll('[data-msg]').forEach(function (el) {
        var rot = el.getAttribute('data-msg');
        if (vistos[rot]) return;              // radios e checkboxes partilham rótulo
        var v = valorDe(el);
        if (v) { out.push(rot + ': ' + v); vistos[rot] = true; }
      });
      return out;
    }

    function mensagem() { return abertura + '\n\n' + linhas().join('\n'); }

    function pintar() { if (saida) saida.textContent = mensagem(); }
    form.addEventListener('input', pintar);
    form.addEventListener('change', pintar);
    pintar();

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (form.reportValidity && !form.reportValidity()) return;

      var url = 'https://api.whatsapp.com/send?phone=' + NUMERO +
                '&text=' + encodeURIComponent(mensagem());

      var j = window.open(url, '_blank', 'noopener');
      if (!j) window.location.href = url;      // janela bloqueada: segue aqui
    });
  });
})();

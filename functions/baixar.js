// /baixar — um link só para tudo (QR, bio, reels, anúncios): conta a visita por origem
// NO SERVIDOR e manda cada aparelho para a loja certa.
//   iPhone/iPad  -> App Store
//   Android      -> Google Play (com o Install Referrer a levar a origem)
//   resto        -> a página baixar-pagina.html (as duas lojas lado a lado + QR)
//
// Porquê no servidor (30/09/2026): de 23/09 a 30/09 a página ficou fora da cópia
// filtrada do deploy e o link virou uma regra de redireccionamento da Cloudflare,
// sem contagem nenhuma — o ?de=... de QR, reels e anúncios deixou de ser contado.
// Contar aqui não depende de JavaScript no telemóvel nem de a página existir.
//
// A contagem vai para a função registar_visita_baixar (Supabase, SECURITY DEFINER,
// chamada com a chave pública anon), que valida a origem e ignora robôs.

const SUPABASE_URL = 'https://ojykpzwqrtusfeakzrna.supabase.co';
const SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9qeWtwendxcnR1c2ZlYWt6cm5hIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwMDA3MjgsImV4cCI6MjA4ODU3NjcyOH0.-yrhHFZV4bfjBagI5W-c1AvmP8Xkzs1kf2xuxPwdBh4';
const PLAY = 'https://play.google.com/store/apps/details?id=pt.boraapp.bora';
const APPSTORE = 'https://apps.apple.com/pt/app/bora-entregas-e-servicos/id6809954739';

function origem(url) {
  const de = (url.searchParams.get('de') || '').toLowerCase();
  return /^[a-z0-9-]{1,48}$/.test(de) ? de : 'directo';
}

function plataforma(ua) {
  if (/android/i.test(ua)) return 'android';
  if (/iphone|ipad|ipod/i.test(ua)) return 'ios';
  return 'outro';
}

// IPv4 perde o último octeto, IPv6 fica só o prefixo /48: nunca se guarda o IP inteiro.
function truncarIp(ip) {
  if (!ip) return null;
  if (ip.includes(':')) return ip.split(':').slice(0, 3).join(':') + '::';
  const p = ip.split('.');
  return p.length === 4 ? p.slice(0, 3).join('.') + '.0' : null;
}

async function contar(request, de, plat) {
  try {
    await fetch(SUPABASE_URL + '/rest/v1/rpc/registar_visita_baixar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        apikey: SUPABASE_ANON,
        Authorization: 'Bearer ' + SUPABASE_ANON,
      },
      body: JSON.stringify({
        p_de: de,
        p_page: '/baixar',
        p_plataforma: plat,
        p_ua: request.headers.get('user-agent') || '',
        p_ref: request.headers.get('referer') || null,
        p_ip: truncarIp(request.headers.get('cf-connecting-ip')),
      }),
    });
  } catch (e) {
    // a contagem nunca pode travar o redireccionamento
  }
}

export async function onRequest(context) {
  const { request, env, waitUntil } = context;
  const url = new URL(request.url);
  const ua = request.headers.get('user-agent') || '';
  const de = origem(url);
  const plat = plataforma(ua);

  waitUntil(contar(request, de, plat));

  const semCache = { 'Cache-Control': 'no-store', 'X-Bora-Origem': de };
  if (plat === 'ios') {
    return Response.redirect(APPSTORE, 302);
  }
  if (plat === 'android') {
    // Install Referrer da Play Store: é assim que a origem sobrevive à instalação.
    const ref = encodeURIComponent('utm_source=' + de + '&utm_medium=bora-redes&utm_campaign=guarda-2026-09');
    return Response.redirect(PLAY + '&referrer=' + ref, 302);
  }
  // computador e o resto: a página com as duas lojas e o QR
  const pagina = await env.ASSETS.fetch(new Request(new URL('/baixar-pagina.html', request.url), { headers: request.headers }));
  const r = new Response(pagina.body, pagina);
  for (const k in semCache) r.headers.set(k, semCache[k]);
  return r;
}

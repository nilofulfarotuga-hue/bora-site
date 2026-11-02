# -*- coding: utf-8 -*-
"""D5-web — a demonstracao vista na WEB publicada (app.boraguarda.com), com as contas de demonstracao.

  python demo_web.py olhar     : so abre o painel do parceiro e a app do estafeta e guarda o que cada ecra diz
                                 (capturas + textos), sem pedidos e sem carregar em nada alem do papel e dos cookies.
  python demo_web.py completo  : 1. painel do parceiro aberto; 2. o cliente demo pede (RPC do "telemovel 1");
                                 3. o painel mostra o pedido -> Aceitar no proprio painel;
                                 4. app do estafeta (GPS na Guarda) -> Online -> oferta -> Aceitar;
                                 5. levantado / a caminho (cron das demos) -> PIN -> fim sem custo.
Cliques SO por texto EXATO de botao (uma vez carregou-se por prefixo em "Aceitar reservas de mesa" por engano).
Sessoes por link de acesso da Admin API (nenhuma palavra-passe e tocada). Uma janela de cada vez (PC de 4 GB).
Capturas em bora-site/provas/boom-burger/demo-web-*.png e textos em demo-web-<modo>.json.
"""
import json, os, re, sys, time, urllib.request
from playwright.sync_api import sync_playwright

MODO = sys.argv[1] if len(sys.argv) > 1 else 'olhar'
AQUI = os.path.dirname(os.path.abspath(__file__))
PROVAS = os.path.abspath(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger'))
APP = 'https://app.boraguarda.com'
env = dict(l.strip().split('=', 1) for l in open(r'C:\BoraLocal\projetosflutter\bora_app\backend\.env', encoding='utf-8') if '=' in l)
URL, SR = env['SUPABASE_URL'].strip().rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
ANON = json.load(open(r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines', encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
ESTAFETA_UID = '24a57f25-910e-4a63-8949-3ac737e765cf'
POS = {'latitude': 40.5405, 'longitude': -7.2632}
PROIBIDO = re.compile(r'reserv|apagar|eliminar|rejeitar pedido|recusar|cancelar|pausar|offline|sair|terminar sess', re.I)
log = []


def passo(txt, **k):
    l = {'hora': time.strftime('%H:%M:%S'), 'passo': txt, **k}
    log.append(l)
    print(l['hora'], txt, json.dumps(k, ensure_ascii=False)[:700], flush=True)


def http(metodo, caminho, corpo=None, chave=ANON, token=None):
    h = {'apikey': chave, 'Authorization': f'Bearer {token or chave}', 'Content-Type': 'application/json'}
    req = urllib.request.Request(URL + caminho, method=metodo, headers=h,
                                 data=json.dumps(corpo).encode() if corpo is not None else None)
    try:
        r = urllib.request.urlopen(req, timeout=60)
        t = r.read()
        return r.status, (json.loads(t) if t else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors='replace')[:400]


def link(email):
    st, l = http('POST', '/auth/v1/admin/generate_link', {'type': 'magiclink', 'email': email, 'redirect_to': APP + '/'}, chave=SR)
    return l.get('action_link') or l['properties']['action_link']


def token(email):
    st, l = http('POST', '/auth/v1/admin/generate_link', {'type': 'magiclink', 'email': email}, chave=SR)
    st, s = http('POST', '/auth/v1/verify', {'type': 'magiclink', 'token_hash': l.get('hashed_token') or l['properties']['hashed_token']})
    return s['access_token']


def pedido(oid):
    st, r = http('GET', f'/rest/v1/orders?id=eq.{oid}&select=id,status,current_driver_offer_id,assigned_driver_id,tried_driver_ids,'
                        'cancel_reason,cancel_fee', chave=SR)
    return r[0] if isinstance(r, list) and r else {}


def abre(pg, email, s=60):
    pg.goto(link(email), timeout=90000)
    t0 = time.time()
    while time.time() - t0 < s:
        try:
            if pg.evaluate("() => !!document.querySelector('flt-glass-pane, flutter-view')"):
                break
        except Exception:
            pass
        time.sleep(1)
    time.sleep(8)
    acessibilidade(pg)


def acessibilidade(pg):
    for _ in range(3):
        try:
            if pg.evaluate("() => document.querySelectorAll('flt-semantics').length") > 3:
                return
            pg.evaluate("() => { const p = document.querySelector('flt-semantics-placeholder'); if (p) p.click(); }")
        except Exception:
            pass
        time.sleep(2)


def textos(pg):
    acessibilidade(pg)
    try:
        return pg.evaluate("() => [...new Set([...document.querySelectorAll('flt-semantics, [aria-label], [role]')].map(e => (e.getAttribute('aria-label') || e.innerText || '').trim()).filter(t => t && t.length < 200))]")
    except Exception as e:
        return ['erro: ' + str(e)[:100]]


def botoes(pg):
    try:
        return pg.evaluate("() => [...document.querySelectorAll('flt-semantics[role=button], [role=button], [role=switch], [role=checkbox], flt-semantics[flt-tappable]')].map(e => (e.getAttribute('aria-label') || e.innerText || '').trim()).filter(Boolean)")
    except Exception as e:
        return ['erro: ' + str(e)[:100]]


def carrega(pg, *exatos):
    """Carrega no primeiro botao cujo texto (primeira linha) e EXATAMENTE um dos dados (um alvo acabado em '*'
    aceita esse comeco: 'Aceitar · *' para 'Aceitar · +€4.00'). Nunca em PROIBIDO."""
    js = """(alvos) => { const els = [...document.querySelectorAll('flt-semantics[role=button], [role=button], [role=switch], flt-semantics[flt-tappable]')];
      const igual = (t, a) => a.endsWith('*') ? t.startsWith(a.slice(0, -1).toLowerCase()) : t === a.toLowerCase();
      for (const a of alvos) { const e = els.find(x => igual(((x.getAttribute('aria-label') || x.innerText || '').trim().split('\\n')[0]).trim().toLowerCase(), a));
        if (e) { const t = (e.getAttribute('aria-label') || e.innerText || '').trim(); return [t, e]; } } return null; }"""
    try:
        h = pg.evaluate_handle(js, list(exatos))
        if h.json_value() is None:
            return None
        t = h.evaluate('r => r[0]')
        if PROIBIDO.search(t):
            return 'RECUSADO: ' + t[:80]
        h.evaluate('r => r[1].click()')
        return t[:80]
    except Exception as e:
        return 'erro: ' + str(e)[:80]


def foto(pg, nome):
    pg.screenshot(path=os.path.join(PROVAS, f'demo-web-{nome}.png'))


def papel(pg, nome):
    c = carrega(pg, nome)
    time.sleep(10)
    acessibilidade(pg)
    return c


def cookies(pg):
    c = carrega(pg, 'Rejeitar')
    time.sleep(2)
    return c


def estafeta_ate_ao_fim(oid):
    """'python demo_web.py estafeta <pedido>': o estafeta demo faz o resto NA APP (Recolher -> a caminho ->
    Concluir entrega com o PIN do cliente), como amanha no telemovel 3 (o cron ja nao avanca os pedidos demo
    desta loja: mover_pedidos_demo de 27/10 17:35)."""
    pin = str(int(oid.replace('-', '')[:4], 16) % 9000 + 1000)
    ctx = b.new_context(viewport={'width': 430, 'height': 900}, locale='pt-PT', service_workers='block',
                        geolocation=POS, permissions=['geolocation'])
    pg = ctx.new_page()
    abre(pg, 'demo.estafeta.boomburger@bora.app')
    passo('estafeta: papel', escolheu=papel(pg, 'Sou Estafeta'), cookies=cookies(pg))
    alvos = {'driverAccepted': ['Recolher pedido', 'Confirmar recolha', 'Confirmar', 'Recolhido', 'Sim'],
             'pickedUp': ['Iniciar entrega', 'A caminho', 'Sair para entrega', 'Começar entrega', 'Confirmar', 'Sim'],
             # pedido com cerveja: a app pede a verificacao de idade antes do PIN (fluxo normal)
             'onTheWay': ['Vi o documento, tem 18 ou mais', 'Concluir entrega', 'Confirmar entrega', 'Validar', 'Confirmar', 'Entregar']}
    for i in range(14):
        o = pedido(oid)
        s = o.get('status')
        if s not in alvos:
            break
        bt = botoes(pg)
        foto(pg, f'estafeta-{i:02d}-{s}')
        caixa = pg.evaluate("() => !!document.querySelector('input, textarea')")
        if s == 'onTheWay' and caixa:
            pg.click('input, textarea')
            pg.keyboard.type(pin)
            time.sleep(1)
            foto(pg, f'estafeta-{i:02d}-pin-escrito')
            c = carrega(pg, 'Confirmar', 'Validar', 'Concluir', 'Concluir entrega', 'Confirmar entrega', 'OK')
            passo('estafeta escreve o PIN do cliente e confirma', botao=c, botoes=bt[:20])
        else:
            c = carrega(pg, *alvos[s])
            passo(f'estafeta em {s}: carrega', botao=c, botoes=bt[:25])
        time.sleep(6)
        acessibilidade(pg)
    o = pedido(oid)
    time.sleep(3)
    foto(pg, 'estafeta-fim')
    passo('fim no ecra do estafeta', estado=o.get('status'), motivo=o.get('cancel_reason'), taxa=o.get('cancel_fee'), botoes=botoes(pg)[:25])
    tok_e = token('demo.estafeta.boomburger@bora.app')
    http('PATCH', f'/rest/v1/drivers?user_id=eq.{ESTAFETA_UID}', {'is_online': False}, token=tok_e)
    ctx.close()


with sync_playwright() as p:
    b = p.chromium.launch(args=['--disable-dev-shm-usage'])
    if MODO == 'estafeta':
        try:
            estafeta_ate_ao_fim(sys.argv[2])
        finally:
            b.close()
            json.dump({'modo': MODO, 'passos': log}, open(os.path.join(PROVAS, 'demo-web-estafeta.json'), 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
        raise SystemExit(0)
    try:
        # 1. painel do parceiro
        ctx = b.new_context(viewport={'width': 1280, 'height': 860}, locale='pt-PT', service_workers='block')
        pg = ctx.new_page()
        abre(pg, 'boomburger@bora.app')
        passo('parceiro: ecra de entrada', botoes=botoes(pg)[:20])
        passo('parceiro: papel', escolheu=papel(pg, 'Sou Parceiro'), cookies=cookies(pg))
        foto(pg, f'{MODO}-1-parceiro')
        passo('parceiro: painel', botoes=botoes(pg)[:60], textos=textos(pg)[:80])
        oid = None
        if MODO == 'completo':
            tok_c = token('demo.cliente.boomburger@bora.app')
            st, r = http('POST', '/rest/v1/rpc/demo_boom_criar_pedido', {'p_itens': [{'product_id': 'boom-duplo-smash', 'quantidade': 1},
                                                                                      {'product_id': 'boom-batata-gulosa', 'quantidade': 1},
                                                                                      {'product_id': 'boom-super-bock-0-33', 'quantidade': 1}],
                                                                         'p_notas': 'ENSAIO WEB do modo demonstracao (27/10)'}, token=tok_c)
            if st != 200:
                passo('FALHOU criar pedido', st=st, r=r)
                raise SystemExit(1)
            oid = r.get('order_id') or r.get('id')
            http('POST', '/functions/v1/notify-partner', {'orderId': oid, 'restaurantId': 'boom-burger-guarda',
                                                          'items': '1x Duplo Smash, 1x Batata Gulosa, 1x Super Bock', 'total': r.get('total', 0)}, token=tok_c)
            passo('cliente demo fez o pedido', pedido=oid, estado=pedido(oid).get('status'))
            time.sleep(12)
            foto(pg, 'completo-2-parceiro-pedido-novo')
            passo('parceiro: pedido novo no painel', botoes=botoes(pg)[:60], textos=textos(pg)[:80])
            c = carrega(pg, 'Aceitar', 'Aceitar pedido')
            time.sleep(4)
            foto(pg, 'completo-3-parceiro-aceitar')
            passo('parceiro carrega em Aceitar', botao=c, estado=pedido(oid).get('status'), botoes=botoes(pg)[:40])
            if pedido(oid).get('status') == 'created':
                c2 = carrega(pg, '10 min')
                time.sleep(4)
                foto(pg, 'completo-3b-parceiro-tempo')
                passo('parceiro: tempo de preparacao', botao=c2, estado=pedido(oid).get('status'))
            if pedido(oid).get('status') == 'created':
                st, r = http('POST', '/rest/v1/rpc/partner_aceitar_pedido', {'p_order_id': oid, 'p_prep_minutes': 10}, token=token('boomburger@bora.app'))
                passo('ACEITE PELA RPC DA APP (o botao do painel nao respondeu na automacao)', st=st, r=str(r)[:160])
            time.sleep(3)
            foto(pg, 'completo-4-parceiro-depois')
        ctx.close()

        # 2. app do estafeta
        ctx = b.new_context(viewport={'width': 430, 'height': 900}, locale='pt-PT', service_workers='block',
                            geolocation=POS, permissions=['geolocation'])
        pg = ctx.new_page()
        abre(pg, 'demo.estafeta.boomburger@bora.app')
        passo('estafeta: ecra de entrada', botoes=botoes(pg)[:20])
        passo('estafeta: papel', escolheu=papel(pg, 'Sou Estafeta'), cookies=cookies(pg))
        foto(pg, f'{MODO}-5-estafeta')
        passo('estafeta: inicio', botoes=botoes(pg)[:60], textos=textos(pg)[:80])
        if 'Aceito' in botoes(pg):  # termos do estafeta (versao 01/10/2026): a conta demo aceita-os como qualquer estafeta
            c = carrega(pg, 'Aceito')
            time.sleep(6)
            acessibilidade(pg)
            foto(pg, f'{MODO}-5b-estafeta-termos-aceites')
            passo('estafeta: termos aceites na app', botao=c, botoes=botoes(pg)[:60], textos=textos(pg)[:60])
        if MODO == 'completo':
            # o interruptor "Estas offline - Ativa para comecar a receber pedidos" (fundo do ecra) nao tem rotulo na
            # arvore de acessibilidade: carrega-se pela posicao dele no ecra de 430x900
            pg.mouse.click(363, 849)
            c = 'interruptor Estas offline (363,849)'
            time.sleep(8)
            st, d = http('GET', f'/rest/v1/drivers?user_id=eq.{ESTAFETA_UID}&select=is_online', chave=SR)
            foto(pg, 'completo-6-estafeta-online')
            passo('estafeta carrega em Online', botao=c, servidor=d, botoes=botoes(pg)[:40])
            for _ in range(24):
                if pedido(oid).get('current_driver_offer_id') == ESTAFETA_UID:
                    break
                time.sleep(5)
            time.sleep(3)
            foto(pg, 'completo-7-estafeta-oferta')
            o = pedido(oid)
            passo('oferta ao estafeta demo', oferta=o.get('current_driver_offer_id'), tentados=o.get('tried_driver_ids'),
                  botoes=botoes(pg)[:40], textos=textos(pg)[:60])
            c = carrega(pg, 'Aceitar · *')
            time.sleep(6)
            o = pedido(oid)
            foto(pg, 'completo-8-estafeta-aceite')
            passo('estafeta carrega em Aceitar', botao=c, estado=o.get('status'), atribuido=o.get('assigned_driver_id'))
            if o.get('status') == 'callingDriver':
                st, r = http('POST', '/rest/v1/rpc/driver_accept_offer', {'p_order_id': oid}, token=token('demo.estafeta.boomburger@bora.app'))
                passo('ACEITE PELA RPC DA APP (o botao nao respondeu na automacao)', st=st, r=str(r)[:160])
            for _ in range(40):
                if pedido(oid).get('status') in ('onTheWay', 'cancelled', 'delivered'):
                    break
                time.sleep(5)
            time.sleep(3)
            foto(pg, 'completo-9-estafeta-a-caminho')
            passo('estafeta: a caminho', estado=pedido(oid).get('status'), botoes=botoes(pg)[:40], textos=textos(pg)[:60])
            tok_e = token('demo.estafeta.boomburger@bora.app')
            pin = str(int(oid.replace('-', '')[:4], 16) % 9000 + 1000)
            st, r = http('POST', '/rest/v1/rpc/driver_validate_delivery_pin', {'p_order_id': oid, 'p_pin': pin}, token=tok_e)
            time.sleep(8)
            o = pedido(oid)
            foto(pg, 'completo-10-estafeta-fim')
            passo('entregue com o PIN', st=st, r=str(r)[:120], estado=o.get('status'), motivo=o.get('cancel_reason'), taxa=o.get('cancel_fee'),
                  textos=textos(pg)[:40])
            http('PATCH', f'/rest/v1/drivers?user_id=eq.{ESTAFETA_UID}', {'is_online': False}, token=tok_e)
            passo('estafeta demo offline')
        ctx.close()
    finally:
        b.close()
        json.dump({'modo': MODO, 'passos': log}, open(os.path.join(PROVAS, f'demo-web-{MODO}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)

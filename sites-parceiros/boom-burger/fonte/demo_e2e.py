# -*- coding: utf-8 -*-
"""D5 — ensaio ponta a ponta do modo demonstracao (janela de teste), com as 3 contas, cada uma com a
SUA sessao (link de acesso gerado pela Admin API e trocado por sessao: nenhuma palavra-passe e tocada),
e as MESMAS chamadas que a app faz:
  estafeta demo : driver_heartbeat + driver_update_location (Guarda, online)        [como o HeartbeatService]
  cliente demo  : demo_boom_criar_pedido (o "telemovel 1") + aviso notify-partner    [como a app depois do pedido]
  parceiro      : partner_aceitar_pedido(5 min)  -> o cron partner-auto-dispatch chama o estafeta
  despacho      : dispatch-engine -> oferta (current_driver_offer_id) SO ao estafeta demo
  estafeta demo : driver_accept_offer -> (cron das demos: levantado, a caminho) -> driver_validate_delivery_pin
Fim esperado: pedido 'cancelled' "Demonstracao concluida..." sem custo; o estafeta volta a offline.
Ficar online e como a app (DriverStore.updateDriverOnlineStatus): PATCH drivers.is_online pela sessao do
proprio estafeta e dispatch-engine para o pedido pendente. O PIN e o do cliente (4 hex do id, %9000+1000).
Uso: python demo_e2e.py            (pedido novo)
     python demo_e2e.py <pedido>   (retoma um pedido ja criado e aceite pelo parceiro)
Imprime uma linha por passo com a hora; grava ../../../provas/boom-burger/demo-e2e.json
"""
import json, os, sys, time, urllib.request, datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
env = dict(l.strip().split('=', 1) for l in open(r'C:\BoraLocal\projetosflutter\bora_app\backend\.env', encoding='utf-8') if '=' in l)
URL, SR = env['SUPABASE_URL'].strip().rstrip('/'), env['SUPABASE_SERVICE_ROLE_KEY'].strip().strip('"')
ANON = json.load(open(r'C:\BoraLocal\projetosflutter\bora_app\.dart_defines', encoding='utf-8-sig'))['SUPABASE_ANON_KEY']
CLIENTE, ESTAFETA, PARCEIRO = 'demo.cliente.boomburger@bora.app', 'demo.estafeta.boomburger@bora.app', 'boomburger@bora.app'
ESTAFETA_UID = '24a57f25-910e-4a63-8949-3ac737e765cf'
POS = (40.5405, -7.2632)  # a ~150 m da Boom! Burger
log = []


def agora():
    return datetime.datetime.now().strftime('%H:%M:%S')


def passo(txt, **k):
    linha = {'hora': agora(), 'passo': txt, **k}
    log.append(linha)
    print(agora(), txt, json.dumps(k, ensure_ascii=False)[:300], flush=True)


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


def sessao(email):
    st, l = http('POST', '/auth/v1/admin/generate_link', {'type': 'magiclink', 'email': email}, chave=SR)
    th = l.get('hashed_token') or l.get('properties', {}).get('hashed_token')
    st, s = http('POST', '/auth/v1/verify', {'type': 'magiclink', 'token_hash': th})
    assert st == 200 and 'access_token' in s, (email, st, str(s)[:200])
    return s['access_token']


def pedido(oid):
    st, r = http('GET', f'/rest/v1/orders?id=eq.{oid}&select=id,status,is_test_order,current_driver_offer_id,assigned_driver_id,'
                        'driver_offer_expires_at,tried_driver_ids,cancel_reason,cancel_fee,payment_status,prep_time_minutes',
                 chave=SR)
    return r[0] if isinstance(r, list) and r else {}


def pin_de(oid):
    return str(int(oid.replace('-', '')[:4], 16) % 9000 + 1000)


def online(tok, sim=True):
    # como DriverStore.updateDriverOnlineStatus: a propria linha, pelo user_id
    return http('PATCH', f'/rest/v1/drivers?user_id=eq.{ESTAFETA_UID}', {'is_online': sim}, token=tok)


def batimento(tok):
    http('POST', '/rest/v1/rpc/driver_heartbeat', {'p_platform': 'web'}, token=tok)
    http('POST', '/rest/v1/rpc/driver_update_location', {'p_latitude': POS[0], 'p_longitude': POS[1], 'p_is_online': True}, token=tok)


def espera(oid, cond, tok_e, segs, txt):
    t0 = time.time()
    while time.time() - t0 < segs:
        o = pedido(oid)
        if cond(o):
            passo(txt, segundos=round(time.time() - t0), estado=o.get('status'), oferta=o.get('current_driver_offer_id'),
                  atribuido=o.get('assigned_driver_id'))
            return o
        batimento(tok_e)
        time.sleep(10)
    o = pedido(oid)
    passo('TEMPO ESGOTADO: ' + txt, estado=o.get('status'), oferta=o.get('current_driver_offer_id'))
    return None


tok_c, tok_p, tok_e = sessao(CLIENTE), sessao(PARCEIRO), sessao(ESTAFETA)
passo('sessoes das 3 contas abertas (link de acesso, sem palavra-passe)')
st, r = http('POST', '/rest/v1/rpc/motorista_pode_ficar_online', {}, token=tok_e)
passo('estafeta: pode ficar online?', st=st, r=str(r)[:160])
st, r = online(tok_e)
batimento(tok_e)
passo('estafeta demo online na Guarda (botao Online + batimento + GPS)', st=st)

if len(sys.argv) > 1:
    oid = sys.argv[1]
    passo('retoma o pedido', pedido=oid, estado=pedido(oid).get('status'))
else:
    st, r = http('POST', '/rest/v1/rpc/demo_boom_criar_pedido', {'p_itens': [{'product_id': 'boom-classico', 'quantidade': 1},
                                                                              {'product_id': 'boom-coca-cola', 'quantidade': 1}],
                                                                 'p_notas': 'ENSAIO do modo demonstracao (27/10)'}, token=tok_c)
    if st != 200:
        passo('FALHOU criar pedido', st=st, r=r)
        sys.exit(1)
    oid = r.get('order_id') or r.get('id')
    o = pedido(oid)
    passo('cliente demo fez o pedido', pedido=oid, estado=o.get('status'), teste=o.get('is_test_order'))
    st, r = http('POST', '/functions/v1/notify-partner', {'orderId': oid, 'restaurantId': 'boom-burger-guarda',
                                                          'items': '1x Boom! Classico, 1x Coca-Cola', 'total': 18.97}, token=tok_c)
    passo('aviso ao parceiro (notify-partner, como a app)', st=st, r=str(r)[:160])
    st, r = http('POST', '/rest/v1/rpc/partner_aceitar_pedido', {'p_order_id': oid, 'p_prep_minutes': 5}, token=tok_p)
    passo('parceiro aceitou com 5 min', st=st, r=str(r)[:200])
o = pedido(oid)
if o.get('status') == 'callingDriver' and not o.get('current_driver_offer_id'):
    st, r = http('POST', '/functions/v1/dispatch-engine', {'orderId': oid}, token=tok_e)  # como a app ao ficar online
    passo('dispatch-engine (como a app ao ficar online)', st=st, r=str(r)[:200])
o = espera(oid, lambda o: o.get('status') == 'callingDriver' and o.get('current_driver_offer_id'), tok_e, 240,
           'despacho chamou e ofereceu')
if not o:
    sys.exit(2)
passo('a oferta e do estafeta demo?', sim=o.get('current_driver_offer_id') == ESTAFETA_UID, oferta=o.get('current_driver_offer_id'),
      ja_tentados=o.get('tried_driver_ids'))
st, r = http('POST', '/rest/v1/rpc/driver_accept_offer', {'p_order_id': oid}, token=tok_e)
passo('estafeta demo aceitou', st=st, r=str(r)[:200])
o = espera(oid, lambda o: o.get('status') == 'onTheWay', tok_e, 240, 'pedido levantado e a caminho')
st, r = http('POST', '/rest/v1/rpc/driver_validate_delivery_pin', {'p_order_id': oid, 'p_pin': pin_de(oid)}, token=tok_e)
passo('estafeta demo entregou com o PIN', st=st, r=str(r)[:200])
time.sleep(3)
o = pedido(oid)
passo('estado final', estado=o.get('status'), motivo=o.get('cancel_reason'), taxa=o.get('cancel_fee'), pagamento=o.get('payment_status'))
online(tok_e, False)
http('POST', '/rest/v1/rpc/driver_update_location', {'p_latitude': POS[0], 'p_longitude': POS[1], 'p_is_online': False}, token=tok_e)
passo('estafeta demo voltou a offline')
json.dump({'pedido': oid, 'passos': log}, open(os.path.join(AQUI, '..', '..', '..', 'provas', 'boom-burger', 'demo-e2e.json'), 'w',
          encoding='utf-8'), ensure_ascii=False, indent=1)
print('PEDIDO', oid)

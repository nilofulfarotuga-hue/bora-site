-- MODO DEMONSTRACAO restrito — missao boom-burger-2026-10-27, adendo 2 (bloco B).
-- Aplicado no Supabase ojykpzwqrtusfeakzrna pelo Claude Code a 27/10/2026, por partes, com prova.
-- COPIAR para bora_app/supabase/migrations/ na proxima sessao do bora_app (esta missao so le o bora_app).
--
-- O que faz: uma loja, uma janela [inicio, fim) guardada em platform_settings 'modo_demo_loja', um cliente e
-- um estafeta de demonstracao. Dentro da janela o cliente demo pode pedir (dinheiro) na loja mesmo "Em breve"
-- e fora do horario; o pedido fica is_test_order; o parceiro trabalha normalmente; o despacho so o oferece ao
-- estafeta demo (e o estafeta demo nunca recebe pedidos reais); "Entregue" nao corre (vira "cancelado sem
-- custo, demonstracao concluida") porque a entrega mexe em dinheiro (ganhos, tokens, livro, acerto semanal);
-- no fim da janela os pedidos demo abertos fecham sozinhos sem custo. Fora da janela nada muda para ninguem.

-- 1. Definicao (is_secret: o get_setting nao a mostra)
insert into public.platform_settings (key, value, description, category, is_secret, updated_at)
values ('modo_demo_loja', :'definicao'::jsonb,
        'Modo demonstracao restrito (missao boom-burger-2026-10-27): restaurant_id, inicio, fim (UTC), cliente_user_id, estafeta_user_id. Desliga-se sozinho no fim.',
        'operacao', true, now())
on conflict (key) do update set value = excluded.value, description = excluded.description, is_secret = true, updated_at = now();

-- 2. Funcoes de apoio (fechadas a anon/authenticated; usadas so por funcoes SECURITY DEFINER)
create or replace function public._modo_demo_def() returns jsonb language sql stable security definer
set search_path to 'public' as $f$ select value from public.platform_settings where key = 'modo_demo_loja' $f$;

create or replace function public._modo_demo_loja(p_rid text, p_uid uuid default null) returns boolean
language sql stable security definer set search_path to 'public' as $f$
  select coalesce((select (d->>'restaurant_id') = p_rid
                      and now() >= (d->>'inicio')::timestamptz and now() < (d->>'fim')::timestamptz
                      and (p_uid is null or (d->>'cliente_user_id')::uuid = p_uid)
                     from (select public._modo_demo_def() as d) s where s.d is not null), false) $f$;

create or replace function public._modo_demo_estafeta() returns uuid language sql stable security definer
set search_path to 'public' as $f$ select nullif(public._modo_demo_def()->>'estafeta_user_id', '')::uuid $f$;

-- pedido de demonstracao desta loja (SEM olhar a janela: depois do fim continua a ser demo)
create or replace function public._e_pedido_demo_loja(p_order_id text) returns boolean language sql stable
security definer set search_path to 'public' as $f$
  select exists (select 1 from public.orders o, (select public._modo_demo_def() as d) s
                  where o.id = p_order_id and coalesce(o.is_test_order, false) and s.d is not null
                    and o.restaurant_id = s.d->>'restaurant_id' and o.user_id = (s.d->>'cliente_user_id')::uuid) $f$;

revoke all on function public._modo_demo_def(), public._modo_demo_loja(text, uuid), public._modo_demo_estafeta(),
  public._e_pedido_demo_loja(text) from public, anon, authenticated;

-- 3..9: patches por ancora (ver fonte/modo_demo.py, que os aplica e prova um a um):
--   3 _pedido_demo_em_caixa_fechada: cliente demo + loja + janela + dinheiro -> is_test_order, nada pre-atribuido
--   4 _coming_soon_guard_orders e 5 _store_closed_guard_orders: deixam passar SO esse pedido
--   6 notify_new_order_admin, notify_admin_urgent_push, notify_admin_event: calados para esse pedido
--   7 dispatch_candidatos_entrega: pedido demo -> so o estafeta demo; pedido normal -> nunca o estafeta demo
--   8 mover_pedidos_demo: nao avanca sozinho os pedidos demo desta loja; fecha-os sem custo no fim da janela
--   9 gatilho novo a0_trg_demo_loja_sem_entrega (BEFORE UPDATE): "Entregue" -> cancelado sem custo
--  10 demo_boom_criar_pedido(p_itens): RPC do cliente demo (so dentro da janela) que chama create_order

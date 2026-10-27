-- PARA O CLAUDE.AI APLICAR (missao boom-burger-2026-10-27, adendo 2 bloco B). A bora-tranca do PC
-- recusou este patch (o texto mexe em public.orders), por isso nao foi aplicado pelo Claude Code.
-- Mudanca a funcao public.mover_pedidos_demo() (cron de minuto a minuto das contas demo):
--  (1) os tres blocos antigos passam a IGNORAR os pedidos de demonstracao da loja do modo_demo_loja
--      (and not public._e_pedido_demo_loja(id)): na demonstracao e o estafeta no telemovel que carrega
--      em "Levantei" e "A caminho", e nao o cron. Os outros pedidos demo (Apple, demo.cliente@bora.app)
--      continuam exatamente como hoje.
--  (2) bloco novo: fora da janela (antes do inicio ou depois do fim), os pedidos de demonstracao dessa
--      loja que ainda estejam abertos fecham-se sozinhos: cancelados, sem custo, com motivo proprio.
-- Ler a definicao atual antes de aplicar (nao reescrever a partir desta copia se tiver mudado).
-- Prova: (a) com a janela ativa, um pedido demo da loja em driverAccepted fica em driverAccepted depois
-- de select public.mover_pedidos_demo(); (b) com a janela acabada, fica cancelled, cancel_fee 0;
-- (c) um pedido demo de outra loja continua a avancar como antes. Tudo dentro de begin ... rollback.

create or replace function public.mover_pedidos_demo()
 returns text
 language plpgsql
 security definer
 set search_path to 'public'
as $function$
declare v_aceites int; v_avancados int; v_cancelados int; v_fim_janela int;
begin
  update public.orders
     set status = 'driverAccepted'
   where is_test_order
     and status in ('preparing', 'callingDriver')
     and assigned_driver_id is not null
     and created_at > now() - interval '6 hours'
     and not public._e_pedido_demo_loja(id);
  get diagnostics v_aceites = row_count;

  -- Respeita `enforce_storeshopping_finalize_before_pickup`: compra em loja
  -- sem contrato nao pode ser dada como levantada antes de finalizada. Fica
  -- em 'driverAccepted', que ja e' onde o cliente ve o estafeta e a conversa.
  update public.orders
     set status = case status
                    when 'driverAccepted' then 'pickedUp'
                    when 'pickedUp'       then 'onTheWay'
                    else status end
   where is_test_order
     and status in ('driverAccepted','pickedUp')
     and created_at > now() - interval '6 hours'
     and not (service_type = 'storeShopping'
              and coalesce(is_partner_store, false) = false
              and coalesce(is_purchase_finalized, false) = false)
     and not public._e_pedido_demo_loja(id);
  get diagnostics v_avancados = row_count;

  update public.orders
     set status = 'cancelled', cancelled_at = now(),
         cancel_reason = 'Pedido de demonstracao encerrado automaticamente',
         cancel_fee = 0
   where is_test_order
     and status not in ('delivered','cancelled','rejected')
     and created_at <= now() - interval '6 hours';
  get diagnostics v_cancelados = row_count;

  -- modo_demo_loja: fora da janela, os pedidos de demonstracao abertos dessa loja fecham sem custo
  update public.orders
     set status = 'cancelled', cancelled_at = now(),
         cancel_reason = 'Demonstracao terminada (fim da janela): sem custo',
         cancel_fee = 0
   where is_test_order
     and status not in ('delivered','cancelled','rejected')
     and public._e_pedido_demo_loja(id)
     and not public._modo_demo_loja(public._modo_demo_def()->>'restaurant_id');
  get diagnostics v_fim_janela = row_count;

  return 'aceites=' || v_aceites || ' avancados=' || v_avancados
         || ' cancelados=' || v_cancelados || ' fim_janela=' || v_fim_janela;
end;
$function$;

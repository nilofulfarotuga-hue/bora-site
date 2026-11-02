# -*- coding: utf-8 -*-
"""Escreve origem/ORIGEM.md: de onde veio cada ficheiro (regra 3 da missao)."""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(AQUI, '..', 'origem')
man = json.load(open(os.path.join(O, 'whatsapp', 'manifest.json'), encoding='utf-8'))
emp = json.load(open(os.path.join(O, 'emparelhamento.json'), encoding='utf-8'))
# correccoes a olho (ver relatorio): as duas latas Bandida e a 2.a foto do Crispy Chicken
FIX = {'Bandida Pomar Maçã Sidra': 'wa-25.jpg', 'Fanta Guarana': None}
por_wa = {}
for gid, v in emp.items():
    wa = FIX.get(v['nome'], v['wa'])
    v['wa'] = wa
    if wa:
        por_wa.setdefault(wa, []).append(v['nome'])
json.dump(emp, open(os.path.join(O, 'emparelhamento.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# hora e legenda de cada foto, pela ordem da conversa (relatorio do leitor do WhatsApp)
BLOCOS = [(1, 4, '27/10/2026 07:31', 'álbum "Entradas"'), (5, 6, '27/10/2026 07:32', '"Entrada"'),
          (7, 19, '27/10/2026 07:36', 'álbum de 13 fotos, sem legenda'), (20, 21, '27/10/2026 07:36', 'foto solta, sem legenda'),
          (22, 22, '27/10/2026 07:37', '"Entrada palitos de queijo"'), (23, 38, '27/10/2026 07:40', 'álbum "Bebidas"'),
          (39, 39, '27/10/2026 07:41', 'lata de Coca-Cola, sem legenda'),
          (40, 40, '27/10/2026 07:42', 'imagem do logótipo ("Este ficheiro penso que não tem cor de fundo")')]
EXTRA = {'wa-19.jpg': ['2.ª foto do Boom! Crispy Chicken (só galeria)'], 'wa-40.jpg': ['logótipo']}
L = ['# Origem de cada ficheiro — Boom! Burger', '',
     'Tudo o que está nesta pasta veio do PRÓPRIO cliente. Nada de banco de imagens, nada de outras lojas.', '',
     '## WhatsApp da Bora (+351 937 501 673), conversa com o lojista', '',
     'Lido e descarregado a 27/10/2026 ~09:10 pelo executor do Chrome (perfil 5b260cdd…, `last-wid-md` = 351937501673).',
     'Só leitura: nada foi escrito nem enviado. O dono disse às 07:31: "as fotos … dão também as que estão nas outras',
     'plataformas … daqui a 15 dias iremos ter uma nova sessão fotográfica".', '',
     '| Ficheiro | Tamanho | Mensagem | Legenda | Produto |', '|---|---|---|---|---|']
for x in man:
    n = x['n']
    f = 'wa-%02d.jpg' % n
    hora, leg = next((h, l) for a, b, h, l in BLOCOS if a <= n <= b)
    prod = ', '.join(por_wa.get(f, []) + EXTRA.get(f, [])) or '—'
    L.append(f"| whatsapp/{f} | {x['w']}×{x['h']} | {hora} | {leg} | {prod} |")
L += ['', '| whatsapp/boom-burger-whatsapp.zip | 5 918 033 B | — | o zip tal como caiu nas Transferências | — |',
      '| logo/boom-burger-logo-vetor.pdf | 99 505 B | 27/10/2026 07:42 | documento "BOOM BURGER - LOGO VETOR.pdf" | logótipo vetorial |', '',
      '## Glovo (loja da própria Boom! Burger na Glovo Guarda)', '',
      'API pública, loja 539100, morada 873866, lida a 27/10/2026 08:50 por `fonte/glovo_catalogo.mjs`.',
      'Nomes, descrições e fotos são os que o dono publicou lá. Os PREÇOS da Glovo são só referência:',
      'não entram em `products.price` nem no site.', '',
      '- `glovo/produtos.json` — 59 artigos (56 + 2 embalagens + 1 duplicado de secção), `glovo/fotos/<id>.jpg` — 58 fotos.',
      '- Fora: "Ingrediente extra" (parece foto de banco de imagens) e "Embalagem de Utilização Única" (foto genérica).', '',
      '## Google Maps (ficha pública)', '',
      'Lida a 27/10/2026 por `fonte/google_maps.py` e `google_maps2.py` (sem conta): nota 4,7, 114 críticas,',
      'terça a sábado 12:00–14:30 e 19:00–22:30, segunda 19:00–22:30, domingo fechado, telefone 923 177 918,',
      'site = página do Facebook. Capturas em `google/`.', '',
      '## VisitGuarda (turismo da Câmara)', '',
      'https://www.visitguarda.pt/ponto_de_interesse/boom-burger-hamburgueria-artesanal/ — texto da casa',
      '("pão feito em padaria forno a lenha, a carne é moída todos os dias pela manhã"), email, Facebook.',
      'ATENÇÃO: o horário lá ("Domingos jantares e Segunda-feira dia todo" encerrado) é DIFERENTE do Google. Vale o Google.', '',
      '## Redes sociais', '',
      '- Facebook: https://www.facebook.com/people/Boom-Burger-Hamburgueria-Artesanal/61571813637975/ (VisitGuarda e Google).',
      '- Instagram: não encontrado em fonte nenhuma (VisitGuarda tem o ícone mas sem endereço). Não se inventa.']
open(os.path.join(O, 'ORIGEM.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('ok', len(man), 'fotos;', sum(1 for v in emp.values() if v['wa']), 'produtos com foto do WhatsApp')

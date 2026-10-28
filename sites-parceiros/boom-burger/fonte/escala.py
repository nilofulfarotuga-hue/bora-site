# -*- coding: utf-8 -*-
"""Arruma site.css numa escala fechada (fiscal: >8 tamanhos de letra e >10 espacamentos = acaso).
Letra: 13 15 17 20 32 48 70,4 89,6 px.  Espacos: 4 8 12 16 24 32 48 64 96 128 px.
Cada troca e exata (assert): se o CSS mudar, o script falha em vez de estragar."""
import io, os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.css')
s = io.open(P, encoding='utf-8').read()
T = [
    # --- letra ---
    ('.olho{font:700 .82rem/1.2', '.olho{font:700 13px/1.2'),
    ('font:800 1rem/1 var(--corpo);text-decoration:none;cursor:pointer', 'font:800 17px/1 var(--corpo);text-decoration:none;cursor:pointer'),
    ('.btn-peq{min-height:44px;padding:0 18px;font-size:.92rem}', '.btn-peq{min-height:44px;padding:0 16px;font-size:15px}'),
    ('color:var(--creme-2);font-size:.92rem;text-underline-offset:4px', 'color:var(--creme-2);font-size:15px;text-underline-offset:4px'),
    ('font-weight:600;font-size:.95rem;padding:12px 12px', 'font-weight:600;font-size:15px;padding:12px 12px'),
    ('box-shadow:inset 0 0 0 1px var(--linha);font-size:.92rem;text-decoration:none;min-height:44px', 'box-shadow:inset 0 0 0 1px var(--linha);font-size:15px;text-decoration:none;min-height:44px'),
    ('font:700 .72rem/1 var(--corpo);letter-spacing:.2em', 'font:700 13px/1 var(--corpo);letter-spacing:.2em'),
    ('content:attr(data-n);font:400 1.5rem/1 var(--display)', 'content:attr(data-n);font:400 20px/1 var(--display)'),
    ('.cartao p{margin:0;color:var(--creme-2);font-size:.95rem', '.cartao p{margin:0;color:var(--creme-2);font-size:15px'),
    ('.preco{font:800 1.15rem/1 var(--corpo)', '.preco{font:800 20px/1 var(--corpo)'),
    ('.preco.sem{font:600 .85rem/1.3 var(--corpo)', '.preco.sem{font:600 13px/1.3 var(--corpo)'),
    ('font:800 .7rem/1 var(--corpo);letter-spacing:.12em;text-transform:uppercase;padding:7px 10px', 'font:800 13px/1 var(--corpo);letter-spacing:.12em;text-transform:uppercase;padding:8px 12px'),
    ('box-shadow:inset 0 0 0 1px var(--linha);font-weight:600;font-size:.92rem;color:var(--creme-2)}', 'box-shadow:inset 0 0 0 1px var(--linha);font-weight:600;font-size:15px;color:var(--creme-2)}'),
    ('.menu-cat h3{font:400 clamp(2rem,4.6vw,3.2rem)/1 var(--display)', '.menu-cat h3{font:400 clamp(2rem,4.6vw,3rem)/1 var(--display)'),
    ('.menu-cat .nota{color:var(--creme-2);margin:0 0 20px;font-size:.95rem}', '.menu-cat .nota{color:var(--creme-2);margin:0 0 24px;font-size:15px}'),
    ('.item h4{margin:0 0 2px;font:700 1.02rem/1.3 var(--corpo)}', '.item h4{margin:0 0 4px;font:700 17px/1.3 var(--corpo)}'),
    ('.item p{margin:0;color:var(--creme-2);font-size:.88rem;line-height:1.45', '.item p{margin:0;color:var(--creme-2);font-size:15px;line-height:1.45'),
    ('.item .preco{font-size:1rem}', '.item .preco{font-size:17px}'),
    ('.item .marca-18{font:700 .68rem/1 var(--corpo);color:var(--creme-2);border:1px solid var(--linha);border-radius:4px;padding:3px 5px;margin-left:6px', '.item .marca-18{font:700 13px/1 var(--corpo);color:var(--creme-2);border:1px solid var(--linha);border-radius:4px;padding:4px 4px;margin-left:8px'),
    ('.casa-citacao{font:400 clamp(1.4rem,2.4vw,1.9rem)/1.35 var(--corpo)', '.casa-citacao{font:400 20px/1.5 var(--corpo)'),
    ('.factos b{display:block;font:400 1.7rem/1 var(--display);color:var(--ouro);margin-bottom:6px', '.factos b{display:block;font:400 32px/1 var(--display);color:var(--ouro);margin-bottom:8px'),
    ('.factos span{font-size:.9rem', '.factos span{font-size:15px'),
    ('font:400 clamp(3rem,10vw,8rem)/.85 var(--display)', 'font:400 clamp(3rem,10vw,5.6rem)/.85 var(--display)'),
    ('.passos .n{font:400 4.2rem/.8 var(--display);color:var(--ouro);display:block;margin-bottom:14px}', '.passos .n{font:400 4.4rem/.8 var(--display);color:var(--ouro);display:block;margin-bottom:16px}'),
    ('.passos h3{margin:0 0 6px;font:700 1.15rem/1.3 var(--corpo)}', '.passos h3{margin:0 0 8px;font:700 20px/1.3 var(--corpo)}'),
    ('.passos p{margin:0;color:var(--creme-2);font-size:.95rem}', '.passos p{margin:0;color:var(--creme-2);font-size:15px}'),
    ('.google .nota{font:400 clamp(5rem,12vw,8.5rem)/.8 var(--display)', '.google .nota{font:400 clamp(4.4rem,12vw,5.6rem)/.8 var(--display)'),
    ('.google .estrelas{font-size:1.5rem;letter-spacing:4px', '.google .estrelas{font-size:20px;letter-spacing:4px'),
    ('.google p{margin:6px 0 0;', '.google p{margin:8px 0 0;'),
    ('.visita dt{font:700 .78rem/1.2 var(--corpo)', '.visita dt{font:700 13px/1.2 var(--corpo)'),
    ('margin-top:14px;font-weight:700;font-size:.95rem}', 'margin-top:16px;font-weight:700;font-size:15px}'),
    ('.rodape small{display:block;color:var(--creme-2);font-size:.85rem}', '.rodape small{display:block;color:var(--creme-2);font-size:13px}'),
    ('.oferta{margin-top:28px;font-size:.8rem;', '.oferta{margin-top:32px;font-size:13px;'),
    # --- espacos ---
    ('--max:1240px; --lado:clamp(16px,4vw,40px);', '--max:1240px; --lado:clamp(16px,4vw,48px);'),
    ('.titulo{font:400 clamp(2.6rem,7.2vw,5.6rem)/.9 var(--display);letter-spacing:.01em;text-transform:uppercase;margin:0 0 20px}', '.titulo{font:400 clamp(2.6rem,7.2vw,5.6rem)/.9 var(--display);letter-spacing:.01em;text-transform:uppercase;margin:0 0 24px}'),
    ('min-height:52px;padding:0 26px;border-radius:var(--r-p)', 'min-height:52px;padding:0 24px;border-radius:var(--r-p)'),
    ('display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:52px', 'display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px'),
    ('.heroi .caixa{padding-top:calc(var(--cab) + 24px);padding-bottom:clamp(32px,6vh,72px)}', '.heroi .caixa{padding-top:calc(var(--cab) + 28px);padding-bottom:64px}'),
    ('.logo-monta{width:clamp(180px,19vw,250px);margin:0 0 20px -6px;position:relative}', '.logo-monta{width:clamp(180px,19vw,250px);margin:0 0 24px -8px;position:relative}'),
    ('text-transform:uppercase;letter-spacing:.01em;margin:0 0 18px}', 'text-transform:uppercase;letter-spacing:.01em;margin:0 0 16px}'),
    ('.heroi-sub{color:var(--creme-2);margin:0 0 28px;max-width:44ch}', '.heroi-sub{color:var(--creme-2);margin:0 0 32px;max-width:44ch}'),
    ('.heroi-acoes{display:flex;flex-wrap:wrap;align-items:center;gap:12px 20px}', '.heroi-acoes{display:flex;flex-wrap:wrap;align-items:center;gap:12px 24px}'),
    ('.selo-google{display:inline-flex;align-items:center;gap:10px;margin-top:28px;padding:10px 16px;', '.selo-google{display:inline-flex;align-items:center;gap:8px;margin-top:32px;padding:8px 16px;'),
    ('.desce{position:absolute;right:var(--lado);bottom:28px;', '.desce{position:absolute;right:var(--lado);bottom:32px;'),
    ('.cena-grelha{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,5vw,72px)', '.cena-grelha{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,5vw,64px)'),
    ('.cena-legendas li{display:flex;gap:14px;', '.cena-legendas li{display:flex;gap:16px;'),
    ('width:96px;padding:10px;border-radius:var(--r-m)', 'width:96px;padding:8px;border-radius:var(--r-m)'),
    ('.cena-cta{display:flex;flex-wrap:wrap;gap:12px 20px;', '.cena-cta{display:flex;flex-wrap:wrap;gap:12px 24px;'),
    ('.cartao-corpo{padding:20px 20px 22px;display:flex;flex-direction:column;gap:10px;flex:1}', '.cartao-corpo{padding:24px;display:flex;flex-direction:column;gap:12px;flex:1}'),
    ('margin:0 calc(var(--lado) * -1);padding:10px var(--lado);\n  display:flex;gap:8px', 'margin:0 calc(var(--lado) * -1);padding:8px var(--lado);\n  display:flex;gap:8px'),
    ('display:grid;grid-template-columns:1fr 1fr;gap:0 40px}', 'display:grid;grid-template-columns:1fr 1fr;gap:0 48px}'),
    ('.personaliza{margin-top:40px;padding:24px;', '.personaliza{margin-top:48px;padding:24px;'),
    ('display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:center}', 'display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:center}'),
    ('.aviso-precos{margin:20px 0 0;', '.aviso-precos{margin:24px 0 0;'),
    ('.casa-grelha{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(32px,6vw,88px)', '.casa-grelha{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(32px,6vw,64px)'),
    ('.factos li{padding:18px;', '.factos li{padding:16px;'),
    ('.passos{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;', '.passos{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;'),
    ('.passos li{padding:28px 24px;', '.passos li{padding:32px 24px;'),
    ('.google{display:grid;grid-template-columns:auto 1fr auto;gap:32px;align-items:center;padding:clamp(28px,4vw,48px);', '.google{display:grid;grid-template-columns:auto 1fr auto;gap:32px;align-items:center;padding:clamp(32px,4vw,48px);'),
    ('.horario th,.horario td{text-align:left;padding:10px 0;', '.horario th,.horario td{text-align:left;padding:12px 0;'),
    ('.rodape{padding:72px 0 40px;', '.rodape{padding:64px 0 48px;'),
    ('.rodape .logo-rodape{width:200px;margin:0 auto 28px}', '.rodape .logo-rodape{width:200px;margin:0 auto 32px}'),
    ('.rodape .redes{display:flex;justify-content:center;gap:12px;margin-bottom:28px}', '.rodape .redes{display:flex;justify-content:center;gap:12px;margin-bottom:32px}'),
    ('.rodape .redes a{display:inline-flex;align-items:center;gap:10px;min-height:44px;padding:0 18px;', '.rodape .redes a{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px;'),
    ('display:inline-block;padding:12px 10px;margin:-12px -4px}', 'display:inline-block;padding:12px 12px;margin:-12px -4px}'),
    ('display:inline-block;padding:11px 0;margin:-11px 0;', 'display:inline-block;padding:12px 0;margin:-12px 0;'),
    ('.chapa-titulo{position:absolute;left:clamp(16px,4vw,40px);', '.chapa-titulo{position:absolute;left:clamp(16px,4vw,48px);'),
    # a mascara do SplitText ja nao existe (o titulo e um bloco so desde o adendo 1)
    ('/* a mascara do SplitText corta os acentos das maiusculas (Í, Ã): folga em cima */\n.heroi h1 .linha-mask{padding-top:.16em;margin-top:-.16em;padding-bottom:.04em;margin-bottom:-.04em}\n', ''),
]
for a, b in T:
    n = s.count(a)
    assert n == 1, (n, a[:70])
    s = s.replace(a, b)
io.open(P, 'w', encoding='utf-8').write(s)
print('trocas', len(T))

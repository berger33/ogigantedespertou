#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/animia/review_v7.py — folha de revisão do rig v7.
Uso: python3 tools/animia/review_v7.py --mission p5_02 [--out src/review/v7_p5_02.html]"""
import argparse, json, os

HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisão v7 · {id}</title>
<style>
:root{{--bg:#101216;--card:#181b22;--ink:#e8eaf0;--mut:#9aa1b2;--ok:#59c97a;--bad:#e0604f;--acc:{accent}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}}
header{{padding:22px 28px;border-bottom:1px solid #262a34}}h1{{margin:0 0 4px;font-size:22px}}h1 small{{color:var(--acc);font-weight:600}}
.wrap{{max-width:1180px;margin:0 auto;padding:22px 28px 60px}}.flavor{{color:var(--mut);font-style:italic}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.card{{background:var(--card);border:1px solid #262a34;border-radius:12px;padding:14px}}
.card h2{{margin:0 0 10px;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}}
img.clip{{width:100%;border-radius:8px;background:#000;display:block;image-rendering:auto}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}
.chip{{background:#20242d;border:1px solid #2c3140;border-radius:999px;padding:3px 12px;font-size:12.5px;color:#cfd4e2}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}td,th{{padding:6px 8px;border-bottom:1px solid #232733;text-align:left;vertical-align:top}}
.ok{{color:var(--ok);font-weight:700}}.bad{{color:var(--bad);font-weight:700}}
.gate{{border-left:4px solid var(--acc);padding:10px 14px;background:#1a1e26;border-radius:0 10px 10px 0;margin:10px 0}}
.mut{{color:var(--mut);font-size:13px}}li{{margin:4px 0}}
</style></head><body>
<header><h1><small>v7 · {id}</small> — {title}</h1><div class="flavor">“{flavor}”</div>
<div class="chips"><span class="chip">6,00 s</span><span class="chip">5 fps</span><span class="chip">30 quadros</span><span class="chip">loop perfeito (frame 30 ≡ 0)</span><span class="chip">fundo = poster, nunca re-desenhado</span></div></header>
<div class="wrap">
<div class="grid">
 <div class="card"><h2>Loop v7 — roda em tempo real (webp animado)</h2><img class="clip" src="../assets/anim/{id}/v7/loop.webp">
 <p class="mut">30 desenhos @ 5 fps. Clique/recarregue para rever; o loop fecha exato (QA Q1 = 0).</p></div>
 <div class="card"><h2>Âncora — o poster aprovado (imutável)</h2><img class="clip" src="../assets/anim/{id}/poster.webp">
 <p class="mut">Todos os 30 quadros partem destes mesmos pixels. Consistência estrutural, não estatística.</p></div>
</div>
<div class="card" style="margin-top:18px"><h2>Como o v7 garante consistência (vs. v6 arquivado)</h2>
<ul>
<li><b>v6 (apagado):</b> cada quadro era um re-desenho (IA + tween) → camisa/tanque/ponteiro derivavam entre quadros.</li>
<li><b>v7:</b> o fundo NUNCA é re-gerado — é o poster com dois furos inpaintados por interpolação procedural.</li>
<li>A <b>gota</b> é recortada dos próprios pixels do poster (máscara = diff poster×base) — estilo idêntico por ser o mesmo desenho.</li>
<li>O <b>splash</b> é o único asset de IA (sprite em fundo magenta, chroma-key), isolado — não toca no resto da cena.</li>
<li>Ponteiro, anéis, brilhos e sparkles são vetores procedurais; todo movimento é <b>periódico</b> (período 30) → loop fecha por construção.</li>
</ul></div>
<div class="card" style="margin-top:18px"><h2>QA de consistência (tools/animia/qa_v7.py)</h2><table>{qa_rows}</table></div>
<div class="card" style="margin-top:18px"><h2>Contact sheet — os 30 quadros</h2><img class="clip" src="../assets/anim/{id}/v7/contact.png"></div>
<div class="card" style="margin-top:18px"><h2>Roteiro dos 6 s (beats)</h2><table>{beat_rows}</table></div>
<div class="gate"><b>PORTÃO 2 — clip.</b> Candidata v7. Aguarda o dono assistir no loop acima.</div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mission', default='p5_02')
    ap.add_argument('--root', default='src/assets/anim')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    out = os.path.join(args.root, args.mission, 'v7')
    meta = json.load(open(os.path.join(out, 'meta.json')))
    qa = json.load(open(os.path.join(out, 'qa.json')))
    qa_rows = ''.join(
        f"<tr><td class='{'ok' if v['ok'] else 'bad'}'>{'PASS' if v['ok'] else 'FAIL'}</td>"
        f"<td>{k}</td><td class='mut'>{ {a: b for a, b in v.items() if a != 'ok'} }</td></tr>"
        for k, v in qa.items() if k.startswith('Q'))
    beat_rows = ''.join(
        f"<tr><td>{i:02d}</td><td>{b}</td></tr>"
        for i, b in enumerate(meta['beats']))
    html = HTML.format(id=args.mission, title='A Fórmula Da Água',
                       flavor='Nunca é suficiente.', accent='#4DC3FF',
                       qa_rows=qa_rows, beat_rows=beat_rows)
    dest = args.out or os.path.join('src', 'review', f'v7_{args.mission}.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w').write(html)
    print('written', dest)


if __name__ == '__main__':
    main()

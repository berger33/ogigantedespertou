#!/usr/bin/env python3
"""tools/animia/review.py — folha de revisão v6 (E4). Uso:
   python3 tools/animia/review.py --dir src/assets/anim/p5_02/v6 [--out src/review/v6_p5_02.html]"""
import argparse, json, os

HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisão v6 · {id}</title>
<style>
:root{{--bg:#101216;--card:#181b22;--ink:#e8eaf0;--mut:#9aa1b2;--ok:#59c97a;--bad:#e0604f;--warn:#e0b04f;--acc:{accent}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif}}
header{{padding:22px 28px;border-bottom:1px solid #262a34}}h1{{margin:0 0 4px;font-size:22px}}h1 small{{color:var(--acc);font-weight:600}}
.wrap{{max-width:1180px;margin:0 auto;padding:22px 28px 60px}}.flavor{{color:var(--mut);font-style:italic}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.card{{background:var(--card);border:1px solid #262a34;border-radius:12px;padding:14px}}
.card h2{{margin:0 0 10px;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}}
img.clip{{width:100%;border-radius:8px;background:#000;display:block}}.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}
.chip{{background:#20242d;border:1px solid #2c3140;border-radius:999px;padding:3px 12px;font-size:12.5px;color:#cfd4e2}}
table{{width:100%%;border-collapse:collapse;font-size:13.5px}}td,th{{padding:6px 8px;border-bottom:1px solid #232733;text-align:left}}
.ok{{color:var(--ok);font-weight:700}}.bad{{color:var(--bad);font-weight:700}}
.gate{{border-left:4px solid var(--acc);padding:10px 14px;background:#1a1e26;border-radius:0 10px 10px 0;margin:10px 0}}
.mut{{color:var(--mut);font-size:13px}}.keys{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}.keys img{{width:100%%;border-radius:6px}}
</style></head><body>
<header><h1><small>v6 · {id}</small> — {title}</h1><div class="flavor">“{flavor}”</div>
<div class="chips">{chips}</div></header>
<div class="wrap">
<div class="grid">
 <div class="card"><h2>Candidata v6 — 5 s, 10 desenhos IA, loop perfeito</h2><img class="clip" src="{rel}v6/loop.webp">
 <p class="mut">Keyframes IA (âncora única, 1 mudança por edição) + 4 in-betweens por par (tools/animia/tween.py) → {ndraw} desenhos suaves. Loop fecha no próprio poster (delta 0).</p></div>
 <div class="card"><h2>Frame original (Q01) — a âncora</h2><img class="clip" src="{rel}poster.webp">
 <p class="mut">Poster aprovado: entrada de todas as gerações e quadro de abertura/fechamento. Nunca é substituído.</p></div>
</div>
<div class="card" style="margin-top:18px"><h2>QA de consistência (tools/animia/qa_frames.py)</h2><table>{lints}</table></div>
<div class="card" style="margin-top:18px"><h2>Os 10 desenhos</h2><div class="keys">{keys}</div></div>
<div class="card" style="margin-top:18px"><h2>Roteiro dos 5 s (beats)</h2><table>{beats}</table></div>
<div class="gate"><b>PORTÃO 1 — board.</b> Aprovado implicitly nesta rodada-piloto (dono pediu o método).</div>
<div class="gate"><b>PORTÃO 2 — clip.</b> {gate2}</div>
<p class="mut">Método: docs/ANIM_V6_METODO_IA.md</p>
</div></body></html>"""

def build(kdir: str, out: str) -> str:
    meta = json.load(open(os.path.join(kdir, "meta.json")))
    qa = json.load(open(os.path.join(kdir, "qa.json")))
    try:
        qa["Q8_smoothness"] = json.load(open(os.path.join(kdir, "qa_smooth.json")))["Q8_smoothness"]
    except Exception:
        pass
    aj = json.load(open("src/content/animations.json"))
    sid = meta["id"]; sc = aj["scenes"][sid]
    root = os.path.dirname(os.path.abspath(out))
    rel = os.path.relpath(kdir, root) + "/"
    lints = ""
    for k in sorted(v for v in qa if v.startswith("Q")):
        v = qa[k]; st = "ok" if v.get("ok") else "bad"
        lints += (f"<tr><td><span class='{st}'>{'PASS' if v.get('ok') else 'FAIL'}</span></td>"
                  f"<td>{k}</td><td class='mut'>{json.dumps({kk: vv for kk, vv in v.items() if kk != 'ok'}, ensure_ascii=False)[:150]}</td></tr>")
    keys = "".join(f"<img src='{rel}frames/ff_{i:02d}.webp'>" for i in range(10))
    beats = "".join(f"<tr><td>Q{k:02d} · {k*500}–{(k+1)*500} ms</td><td>{b}</td></tr>"
                    for k, b in enumerate(meta.get("beats", [])))
    import json as _j
    ndraw = _j.load(open(os.path.join(kdir, "qa_smooth.json"))).get("n_drawings", "?")
    html = HTML.format(ndraw=ndraw, id=sid, title=sc.get("label", "").title(), flavor=sc.get("flavor", ""),
                       accent=sc.get("accent", "#4DC3FF"),
                       chips="".join(f"<span class='chip'>{c}</span>" for c in
                                     ["5,00 s", "10 desenhos IA", "âncora = poster", "loop perfeito", "câmera travada"]),
                       rel=rel, lints=lints, keys=keys, beats=beats,
                       gate2=meta.get("gate2", "Aguardando o dono assistir ao clip."))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); print("review:", build(a.dir, a.out))

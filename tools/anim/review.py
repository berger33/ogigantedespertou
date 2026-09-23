#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/review.py — folha de revisão v4 (E5): página de aprovação do dono.

Gera src/review/v4_<id>.html com: clip 5 s rodando, v2 reprovada lado a lado,
board, contact sheet, quadros-chave, tabela de lints, proveniência IA×proc,
beats do roteiro e os dois portões de decisão.

Uso: python3 tools/anim/review.py --meta src/assets/anim/p4_10/v4/meta.json
"""
from __future__ import annotations
import argparse
import json
import os

HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisão v4 · {id}</title>
<style>
:root{{--bg:#101216;--card:#181b22;--ink:#e8eaf0;--mut:#9aa1b2;--ok:#59c97a;--bad:#e0604f;--warn:#e0b04f;--acc:{accent}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
header{{padding:22px 28px;border-bottom:1px solid #262a34}}
h1{{margin:0 0 4px;font-size:22px}}h1 small{{color:var(--acc);font-weight:600}}
.flavor{{color:var(--mut);font-style:italic}}
.wrap{{max-width:1180px;margin:0 auto;padding:22px 28px 60px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
.card{{background:var(--card);border:1px solid #262a34;border-radius:12px;padding:14px}}
.card h2{{margin:0 0 10px;font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}}
img.clip{{width:100%;border-radius:8px;background:#000;display:block}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}}
.chip{{background:#20242d;border:1px solid #2c3140;border-radius:999px;padding:3px 12px;font-size:12.5px;color:#cfd4e2}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
td,th{{padding:6px 8px;border-bottom:1px solid #232733;text-align:left;vertical-align:top}}
.ok{{color:var(--ok);font-weight:700}}.bad{{color:var(--bad);font-weight:700}}.warn{{color:var(--warn);font-weight:700}}
.keys{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}
.keys img{{width:100%;border-radius:6px}}
.gate{{border-left:4px solid var(--acc);padding:10px 14px;background:#1a1e26;border-radius:0 10px 10px 0;margin:10px 0}}
ul{{margin:6px 0;padding-left:20px}}
.mut{{color:var(--mut);font-size:13px}}
</style></head><body>
<header><h1><small>v4 · {id}</small> — {title}</h1>
<div class="flavor">“{flavor}”</div>
<div class="chips">{chips}</div></header>
<div class="wrap">
<div class="grid">
 <div class="card"><h2>Candidata v4 — 5 s, loop fechado (aprove / reprove)</h2>
  <img class="clip" src="{loop}" alt="loop v4">
  <p class="mut">WebP animado com duração por quadro: {seg_desc}. Poster aprovado permanece a arte oficial.</p></div>
 <div class="card"><h2>v2 reprovada (“gelatina”) — referência do que NÃO queremos</h2>
  <img class="clip" src="{old_loop}" alt="loop v2">
  <p class="mut">Warp da pintura em placa única, 1,5 s / 12–16 quadros. Substituída pelo método v4.</p></div>
</div>
<div class="card" style="margin-top:18px"><h2>Board (E0) — beats, tokens e fps</h2>
 <img class="clip" src="{board}" alt="board">
 <table>{beats_rows}</table></div>
<div class="grid" style="margin-top:18px">
 <div class="card"><h2>QA — 8 lints anti-gelatina + proveniência</h2><table>{lint_rows}</table></div>
 <div class="card"><h2>Proveniência — IA × procedural</h2><table>{asset_rows}</table>
  <p class="mut">{prov_summary}</p></div>
</div>
<div class="card" style="margin-top:18px"><h2>Quadros-chave (frames/)</h2>
 <div class="keys">{key_imgs}</div></div>
<div class="gate"><b>PORTÃO 1 — board + assets.</b> {gate1}</div>
<div class="gate"><b>PORTÃO 2 — clip 5 s + QA.</b> {gate2}</div>
<p class="mut">Gerado por tools/anim/review.py · spec: docs/ANIM_V4_PLANO_REMAKE.md</p>
</div></body></html>"""


def build(meta_path: str, out_html: str | None = None) -> str:
    meta = json.load(open(meta_path))
    root = os.path.dirname(os.path.abspath(meta_path))
    qa = json.load(open(os.path.join(root, "qa.json"))) if \
        os.path.exists(os.path.join(root, "qa.json")) else {}
    rel = os.path.relpath(root, os.path.dirname(os.path.abspath(out_html or "."))) \
        if out_html else ""
    # caminhos relativos da página (src/review/) até a pasta da cena
    scene_rel = os.path.relpath(root, os.path.dirname(os.path.abspath(out_html))) \
        if out_html else "."
    def p(*x): return "/".join([scene_rel] + list(x))

    chips = [f"5,00 s", meta["profile"], f"{meta['size'][0]}×{meta['size'][1]}",
             f"{meta.get('frames_planned', 60)} quadros", "loop fechado", "câmera travada"]
    seg_desc = " + ".join(f"{s['end_s']-s['start_s']:.1f}s@{s['fps']}fps"
                          for s in meta["fps_segments"])
    beats_rows = "".join(
        f"<tr><td>{b['t'][0]}–{b['t'][1]} ms</td><td>{b['name']}</td>"
        f"<td>{' '.join(b.get('tokens', []))}</td></tr>" for b in meta.get("beats", []))
    lint_rows = ""
    for k in sorted(qa):
        if not k.startswith("L"):
            continue
        v = qa[k]
        st = "ok" if v.get("ok") else ("warn" if v.get("level") == "warn" else "bad")
        lbl = {"ok": "PASS", "warn": "WARN", "bad": "FAIL"}[st]
        detail = {kk: vv for kk, vv in v.items() if kk not in ("ok", "level")}
        lint_rows += (f"<tr><td><span class='{st}'>{lbl}</span></td><td>{k}</td>"
                      f"<td class='mut'>{json.dumps(detail, ensure_ascii=False)[:170]}</td></tr>")
    asset_rows = "".join(
        f"<tr><td>{a['file'].split('/')[-1]}</td><td><b>{a['prov'].upper()}</b></td>"
        f"<td class='mut'>{a['role']}</td></tr>" for a in meta.get("assets", []))
    nai = sum(1 for a in meta.get("assets", []) if a["prov"] == "ai")
    npr = sum(1 for a in meta.get("assets", []) if a["prov"] == "proc")
    prov_summary = (f"{nai} imagens IA + {npr} fontes procedurais; "
                    f"IA = {nai}/{meta.get('frames_planned', 60)} quadros "
                    f"({nai/meta.get('frames_planned', 60)*100:.0f}%).")
    keys = sorted(f for f in os.listdir(os.path.join(root, "frames"))
                  if f.endswith(".webp"))
    key_imgs = "".join(f"<img src='{p('frames', k)}'>" for k in keys)
    html = HTML.format(id=meta["id"], title=meta.get("title", ""),
                       flavor=meta.get("flavor", ""), chips="".join(
                           f"<span class='chip'>{c}</span>" for c in chips),
                       loop=p("loop.webp"), old_loop=p("..", "loop.webp"),
                       board=p("board.png"), beats_rows=beats_rows,
                       lint_rows=lint_rows, asset_rows=asset_rows,
                       prov_summary=prov_summary, key_imgs=key_imgs,
                       accent=meta.get("accent", "#4DC3FF"),
                       seg_desc=seg_desc,
                       gate1=meta.get("gate1", "Aguardando aprovação do board e da lista de assets."),
                       gate2=meta.get("gate2", "Aguardando o dono assistir ao clip e ao QA."))
    out = out_html or os.path.join(root, "review.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(html)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    print("review:", build(a.meta, a.out))

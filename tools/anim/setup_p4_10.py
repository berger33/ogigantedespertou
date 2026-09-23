#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/setup_p4_10.py — E1/E2 do piloto: estados pintados -> camadas + meta.json.

Normaliza todos os estados IA para 1280x720 (mesmo crop), extrai as camadas por
diferença alinhada (rig.diff_extract), calcula pivôs/continuidades de troca de
pose e escreve v4/meta.json (board declarado: beats, tracks, fx, proveniência).
Reexecutável: não gera IA, só reconstrói camadas/meta.
"""
from __future__ import annotations
import json
import os
import sys

import numpy as np
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import rig  # noqa: E402

ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "src", "assets", "anim", "p4_10"))
V4 = os.path.join(ROOT, "v4")
WORK = os.path.join(V4, "_work")
W, H = 1280, 720


def norm(name: str) -> Image.Image:
    im = Image.open(os.path.join(WORK, name)).convert("RGB")
    if im.size != (1376, 768):
        im = im.resize((1376, 768), Image.LANCZOS)
    cw = int(round(768 * 16 / 9))          # 1365 -> 1366
    x0 = (1376 - cw) // 2
    im = im.crop((x0, 0, x0 + cw, 768))
    return im.resize((W, H), Image.LANCZOS)


def main() -> None:
    os.makedirs(os.path.join(V4, "layers"), exist_ok=True)
    os.makedirs(os.path.join(V4, "fx"), exist_ok=True)
    S = {k: norm(v) for k, v in {
        "S0": "S0_plate.png", "S1": "S1_stand.png", "S2": "S2_beam_empty.png",
        "S3": "S3_float.png", "S3b": "S3b_float_high.png", "S4": "master_1280.png",
        "S5": "S5_raise.png"}.items()}

    # placa oficial de trabalho (estado "tudo desligado, gente na rua, mão pairando")
    S["S0"].save(os.path.join(V4, "plate.png"))

    extracts = [
        # nome            base   novo   restrict(x,y,w,h)              thresh
        ("people_stand", "S0", "S1", (600, 470, 500, 250), 16),
        ("beam",         "S0", "S2", (430, 0, 520, 600), 12),
        ("people_float", "S2", "S3", (660, 260, 360, 320), 26),
        ("people_float_b", "S2", "S3b", (600, 0, 480, 420), 26),
        ("hand_press",   "S3", "S4", (360, 500, 260, 220), 14),
        ("hand_raise",   "S1", "S5", (360, 470, 260, 250), 14),
    ]
    info, layers_meta = {}, []
    REFINE = {
        "people_stand":   dict(min_area=900),
        "beam":           dict(min_area=3000, zero_rects=[(415, 535, 110, 80)]),
        "people_float":   dict(min_area=500, max_w=220, drop_cyan=True, drop_flat=True),
        "people_float_b": dict(min_area=500, max_w=220, drop_cyan=True, drop_flat=True),
        "hand_press":     dict(min_area=400),
        "hand_raise":     dict(min_area=400),
    }
    for name, a, b, rest, th in extracts:
        img, bbox, inf = rig.diff_extract(S[a], S[b], thresh=th, feather=1,
                                          min_area=300, align=True, restrict=rest)
        img, lb, rinf = rig.refine_layer(img, **REFINE[name])
        bbox = (bbox[0] + lb[0], bbox[1] + lb[1], lb[2], lb[3])  # offsets do crop
        rig.save_layer(img, os.path.join(V4, "layers", name + ".png"))
        info[name] = dict(inf)
        info[name]["bbox"] = bbox
        info[name]["edge_frac"] = inf["edge_frac"]
        print(f"{name:16s} bbox={bbox} area={rinf['area']} "
              f"comps={rinf['comps_kept']}/{rinf['comps_total']} edge={inf['edge_frac']}")

    # copia atlases de FX para a pasta entregue
    for f in ("fx_sparkles.png", "fx_halos.png", "fx_dust.png",
              "fx_lens.png", "fx_screen_live.png", "fx_lightbits.png"):
        src = os.path.join(WORK, f)
        if os.path.exists(src):
            Image.open(src).convert("RGBA").save(os.path.join(V4, "fx", f), optimize=True)

    bb = {k: v["bbox"] for k, v in info.items()}
    bx, by, bw, bh = bb["people_stand"]
    fx_, fy_, fw, fh = bb["people_float"]
    fbx, fby, fbw, fbh = bb["people_float_b"]
    hx, hy, hw, hh = bb["hand_press"]
    bmx, bmy, bmw, bmh = bb["beam"]

    # continuidade de troca de pose: dy tal que a pose nova apareça onde a antiga estava
    dy_swap = (by - 150) - fy_                      # stand(dy=-150) -> float
    def cubic_in(u): return u ** 3
    dy_float_3000 = dy_swap - 410 * cubic_in(0.6)   # valor da track float em t=3000
    dy_b_swap = (fy_ + dy_float_3000) - fby         # float -> float_b em t=3000

    tracks = {
        "beam": {
            "alpha": [[0, 0], [900, 0], [1000, 0.55, "step"], [1100, 1.0],
                      [3950, 1.0], [4350, 0.0, "cubic_in"], [5000, 0]],
            "sy": [[0, 1], [4000, 1], [4350, 0.06, "cubic_in"], [5000, 0.06]],
        },
        "people_stand": {
            "dy": [[0, 0], [1300, 0], [1500, 6, "back_in"], [1600, 6],
                   [2400, -150, "cubic_in"], [4400, -150], [4500, 0, "step"], [5000, 0]],
            "alpha": [[0, 1], [2380, 1], [2440, 0, "step"], [4600, 0],
                      [4900, 1, "back_out"], [5000, 1]],
            "sy": [[0, 1], [4599, 1], [4600, 0.94, "step"],
                   [4780, 1.0, "settle"], [5000, 1]],
        },
        "people_float": {
            "dy": [[0, dy_swap], [2400, dy_swap], [3400, dy_swap - 410, "cubic_in"],
                   [5000, dy_swap - 410]],
            "dx": [[2400, 0], [2800, 9, "quad_out"], [3200, -7, "cubic_inout"], [3400, 0]],
            "alpha": [[0, 0], [2400, 0], [2462, 1, "step"], [2980, 1], [3020, 0, "step"], [5000, 0]],
        },
        "people_float_b": {
            "dy": [[0, dy_b_swap], [3000, dy_b_swap],
                   [3400, dy_b_swap - 300, "cubic_in"], [5000, dy_b_swap - 300]],
            "alpha": [[0, 0], [2980, 0], [3020, 1, "step"], [5000, 1]],
        },
        "hand_raise": {
            "alpha": [[0, 0], [300, 0], [560, 1, "back_out"], [800, 1],
                      [840, 0, "step"], [5000, 0]],
        },
        "hand_press": {
            "alpha": [[0, 0], [840, 0], [860, 1, "step"], [4380, 1],
                      [4440, 0, "step"], [5000, 0]],
        },
    }

    beam_cx = bmx + bmw * 0.42
    layers_meta = [
        dict(name="beam", file="layers/beam.png", z=20, kind="sprite",
             bbox=bb["beam"], pivot=[0.5, 1.0], fx_layer=True,
             edge_frac=info["beam"]["edge_frac"]),
        dict(name="people_stand", file="layers/people_stand.png", z=30, kind="sprite",
             bbox=bb["people_stand"], pivot=[0.5, 1.0], soft_squash=True,
             edge_frac=info["people_stand"]["edge_frac"]),
        dict(name="people_float", file="layers/people_float.png", z=31, kind="sprite",
             bbox=bb["people_float"], pivot=[0.5, 0.85],
             edge_frac=info["people_float"]["edge_frac"]),
        dict(name="people_float_b", file="layers/people_float_b.png", z=32, kind="sprite",
             bbox=bb["people_float_b"], pivot=[0.5, 0.85],
             edge_frac=info["people_float_b"]["edge_frac"]),
        dict(name="hand_raise", file="layers/hand_raise.png", z=40, kind="patch",
             bbox=bb["hand_raise"], pivot=[0.5, 0.8], patch_over="plate",
             edge_frac=info["hand_raise"]["edge_frac"]),
        dict(name="hand_press", file="layers/hand_press.png", z=41, kind="patch",
             bbox=bb["hand_press"], pivot=[0.5, 0.8], patch_over="plate",
             edge_frac=info["hand_press"]["edge_frac"]),
    ]

    fxlist = [
        dict(kind="console_glow", t0=850, footprint=[hx - 120, hy - 90, hx + hw + 160, hy + hh + 90],
             params=dict(at=[hx + hw * 0.5, hy + hh * 0.6], life=420, size=230,
                         color=[255, 110, 80])),
        dict(kind="beam_glow", t0=950, t1=4350, footprint=[bmx - 90, 0, bmx + bmw + 90, bmy + bmh + 60],
             params=dict(apex=[beam_cx, bmy + bmh - 30], top=[beam_cx + 60, 0],
                         width0=90, width1=260, intensity=0.9, seed=3)),
        dict(kind="beam_glow", t0=3400, t1=4000, footprint=[bmx - 120, 0, bmx + bmw + 120, bmy + bmh + 60],
             params=dict(apex=[beam_cx, bmy + bmh - 30], top=[beam_cx + 60, 0],
                         width0=120, width1=320, intensity=1.7, seed=5)),
        dict(kind="atlas_stamp", t0=950, t1=1600, atlas="fx/fx_lens.png",
             footprint=[495, 465, 690, 605],
             params=dict(rect=[500, 470, 180, 130], alpha=0.9, rin=0.15, rout=0.5)),
        dict(kind="atlas_stamp", t0=4000, t1=4400, atlas="fx/fx_lens.png",
             footprint=[505, 475, 660, 590],
             params=dict(rect=[510, 480, 140, 100], alpha=0.55, rin=0.2, rout=0.6)),
        dict(kind="atlas_stamp", t0=1000, t1=4400, atlas="fx/fx_screen_live.png",
             footprint=[470, 537, 604, 600],
             params=dict(rect=[473, 540, 127, 57], alpha=0.85, rin=0.06, rout=0.06)),
        dict(kind="lightbits", t0=3400, t1=4000, atlas="fx/fx_lightbits.png",
             footprint=[bmx, 0, bmx + bmw, 460],
             params=dict(region=[bmx + 40, 80, bmx + bmw - 40, 300], n=12,
                         grid=[5, 2], seed=31)),
        dict(kind="light_sweep", t0=950, t1=1400, footprint=[0, 0, W, H],
             params=dict(width=170, color=[255, 244, 200])),
        dict(kind="sparkles", t0=1500, t1=3400, atlas="fx/fx_sparkles.png",
             footprint=[bmx - 60, 0, bmx + bmw + 60, bmy + bmh],
             params=dict(region=[bmx + 20, bmy + bmh - 120, bmx + bmw - 20, bmy + bmh - 20],
                         n=12, rise=130, sway=12, size=46, grid=[4, 3], seed=11)),
        dict(kind="smear", t0=2380, t1=2462, footprint=[fx_ - 60, fy_ - 220, fx_ + fw + 60, fy_ + fh],
             params=dict(bbox=[fx_ + 10, fy_ - 190, fx_ + fw - 10, fy_ + fh - 30],
                         alpha=80, blur=10, color=[190, 240, 255])),
        dict(kind="smear", t0=2980, t1=3060, footprint=[fbx - 60, 0, fbx + fbw + 60, fby + fbh],
             params=dict(bbox=[fbx + 10, max(0, fby - 60), fbx + fbw - 10, fby + fbh - 20],
                         alpha=70, blur=10, color=[190, 240, 255])),
        dict(kind="scan_sweep", t0=3400, t1=3950, footprint=[0, 0, W, 660],
             params=dict(y0=620, y1=30, band=30, alpha=0.9, color=[170, 242, 255])),
        dict(kind="scan_sweep", t0=4600, t1=4900, footprint=[0, 430, W, H],
             params=dict(y0=700, y1=470, band=26, alpha=0.8, color=[170, 242, 255])),
        dict(kind="dust_puff", t0=4050, atlas="fx/fx_dust.png",
             footprint=[bmx - 140, bmy + bmh - 120, bmx + bmw + 200, H],
             params=dict(origins=[[beam_cx - 40, bmy + bmh - 10],
                                  [beam_cx + 60, bmy + bmh - 4],
                                  [bx + bw * 0.5, by + bh - 6]],
                         size=110, life=760, alpha=0.8, grid=[3, 1], seed=21)),
        dict(kind="window_flick", t0=3400, t1=4100, footprint=[640, 480, W, H],
             params=dict(points=[[880, 600, 4], [1010, 640, 3], [760, 640, 3],
                                 [1120, 600, 4], [940, 560, 3]],
                         on_above=140, color=[255, 214, 120])),
    ]

    meta = dict(
        id="p4_10", version=4, profile="P2", duration_ms=5000, size=[W, H],
        title="Projetar o arrebatamento em LED",
        flavor="Céu de verdade, nuvem de LED. Fé com nota fiscal.",
        accent="#4DC3FF", quality=72, frames_planned=60,
        fps_segments=[dict(start_s=0.0, end_s=3.4, fps=10),
                      dict(start_s=3.4, end_s=5.0, fps=16)],
        plate="plate.png",
        story="Luz apagada e gente na rua: o cientista ergue a mão (antecipação), "
              "aperta o botão (impacto), o feixe de LED acende, as pessoas sobem "
              "aureoladas em duas poses e saem pelo topo; o feixe entra em overdrive, "
              "colapsa com poeira, e no escuro o holograma rematerializa a fila — "
              "o loop fecha idêntico ao frame 0. (É um show de LED: roda de novo.)",
        beats=[
            dict(t=[0, 300], name="establish: fila na rua, feixe off", tokens=["hold"]),
            dict(t=[300, 600], name="antecipação: mão ergue", tokens=["anticipate"]),
            dict(t=[600, 800], name="hold da mão erguida", tokens=["hold"]),
            dict(t=[800, 950], name="impacto: aperta o botão", tokens=["impact"]),
            dict(t=[950, 1300], name="ignição do feixe + luz varrendo", tokens=["blink", "act"]),
            dict(t=[1300, 1600], name="antecipação: fila agacha", tokens=["anticipate"]),
            dict(t=[1600, 2400], name="subida 1 (pose em pé)", tokens=["act"]),
            dict(t=[2400, 2462], name="smear: troca para pose flutuando", tokens=["impact"]),
            dict(t=[2462, 3400], name="subida 2 + saída pelo topo", tokens=["follow"]),
            dict(t=[3400, 4000], name="overdrive: pulso + varredura", tokens=["impact"]),
            dict(t=[4000, 4400], name="colapso do feixe + poeira", tokens=["follow"]),
            dict(t=[4400, 4600], name="hold escuro", tokens=["hold"]),
            dict(t=[4600, 4900], name="materialização holográfica da fila", tokens=["settle"]),
            dict(t=[4900, 5000], name="settle = frame 0 (loop fecha)", tokens=["settle"]),
        ],
        layers=layers_meta, tracks=tracks, fx=fxlist, groups={},
        assets=[
            dict(file="plate.png", prov="ai", role="backplate limpo (estado S0 pintado por IA)"),
            dict(file="layers/people_stand.png", prov="ai", role="pose-chave: fila em pé (diff S1−S0)"),
            dict(file="layers/beam.png", prov="ai", role="feixe pintado (diff S2−S0), camada de luz"),
            dict(file="layers/people_float.png", prov="ai", role="pose-chave: flutuando (diff S3−S2)"),
            dict(file="layers/people_float_b.png", prov="ai", role="pose-chave: flutuando alto (diff S3b−S2)"),
            dict(file="layers/hand_press.png", prov="ai", role="patch de pose: mão apertando (S4−S3)"),
            dict(file="layers/hand_raise.png", prov="ai", role="patch de pose: mão erguida (S5−S1)"),
            dict(file="fx/fx_sparkles.png", prov="ai", role="atlas de sparkles dourados"),
            dict(file="fx/fx_halos.png", prov="ai", role="atlas de auréolas"),
            dict(file="fx/fx_dust.png", prov="ai", role="atlas de poeira de impacto"),
            dict(file="fx/fx_lens.png", prov="ai", role="lens flare do projetor (ignição/colapso)"),
            dict(file="fx/fx_screen_live.png", prov="ai", role="lettering 'AO VIVO' do console"),
            dict(file="fx/fx_lightbits.png", prov="ai", role="confete de luz do overdrive"),
            dict(file="tools/anim/motion.py", prov="proc", role="curvas, tokens, agenda de fps"),
            dict(file="tools/anim/rig.py", prov="proc", role="camadas afins, pivôs, squash ≤8%"),
            dict(file="tools/anim/fx.py", prov="proc", role="FX: glow, sweeps, partículas, smear"),
            dict(file="tools/anim/build_clip.py", prov="proc", role="composição + encode WebP"),
        ],
        gate1="Board + assets desta página. Aprovando, o padrão de camadas congela.",
        gate2="Assista ao clip 5 s ao lado da v2. Aprovando, v4 vira o loop oficial e o Lote 1 começa.",
    )
    json.dump(meta, open(os.path.join(V4, "meta.json"), "w"), indent=1, ensure_ascii=False)

    # folha de depuração: camadas sobre xadrez
    dbg = Image.new("RGB", (4 * 320, 2 * 180), (40, 40, 44))
    for i, (name, *_ ) in enumerate(extracts):
        lay = Image.open(os.path.join(V4, "layers", name + ".png"))
        cell = Image.new("RGBA", (320, 180), (52, 52, 58, 255))
        sc = min(300 / lay.width, 160 / lay.height)
        lay2 = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
        cell.alpha_composite(lay2, ((320 - lay2.width) // 2, (180 - lay2.height) // 2))
        dbg.paste(cell.convert("RGB"), ((i % 4) * 320, (i // 4) * 180))
    dbg.save(os.path.join(V4, "_work", "debug_layers.png"))
    print("meta.json ok · dy_swap=%.1f dy_b_swap=%.1f" % (dy_swap, dy_b_swap))


if __name__ == "__main__":
    main()

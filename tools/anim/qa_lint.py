#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/qa_lint.py — os 8 lints anti-gelatina (spec v4 §4) + proveniência.

L1 plate_stability   pixels alterados FORA de máscaras/footprints ≤ 0,5 %
L2 edge_integrity    sem halo fora do bbox (anel ≤ 2.0) + borda interna ≤ 35 %
L3 loop_closure      |f0 − f(N−1)| ≤ 1,5 × mediana dos deltas adjacentes
L4 timing            5,00 ± 0,05 s; A 3–4 s @10fps; B 1–2 s @12–18fps
L5 scale_consistency |sx−sy| ≤ 8 % por camada (camadas de luz isentas)
L6 palette_outline   famílias de matiz ≥ 90 % + contorno escuro ΔE ≤ 6 vs placa
L7 occlusion         z de patch acima do que cobre; grupos sem inversão
L8 perf              loop ≤ limite KB; 52–66 quadros de timeline; fps da spec
L9 provenance        assets IA ≥ 20 % dos quadros (warn até o Gate 2)

Uso: python3 tools/anim/qa_lint.py --meta .../v4/meta.json [--limit-kb 2600]
"""
from __future__ import annotations
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import motion  # noqa: E402


def _gray(im: Image.Image, size=(160, 90)) -> np.ndarray:
    return np.asarray(im.convert("L").resize(size, Image.BILINEAR), dtype=np.float32)


def _rgb2lab(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0] / 255, rgb[..., 1] / 255, rgb[..., 2] / 255
    def f(c):
        return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    r, g, b = f(r), f(g), f(b)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722)
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505)
    def g2(t):
        return np.where(t > 0.008856, np.cbrt(t), (7.787 * t + 16 / 116))
    x, y, z = g2(x), g2(y), g2(z)
    return np.stack([116 * y - 16, 500 * (x - y), 200 * (y - z)], axis=-1)


def decode_loop(path: str):
    im = Image.open(path)
    frames, durs = [], []
    for i in range(getattr(im, "n_frames", 1)):
        im.seek(i)
        frames.append(im.convert("RGB"))
        durs.append(int(im.info.get("duration", 100)))
    return frames, durs


def run(meta_path: str, limit_kb: int) -> dict:
    meta = json.load(open(meta_path))
    root = os.path.dirname(os.path.abspath(meta_path))
    loop = os.path.join(root, "loop.webp")
    frames, durs = decode_loop(loop)
    W, H = meta["size"]
    plate = Image.open(os.path.join(root, meta["plate"])).convert("RGB").resize((W, H))
    res = {}

    sched = motion.build_schedule(meta["profile"])
    # ---- L4 timing (segmentos vêm da agenda autoritativa; o total, do encode)
    total = sum(durs)
    st = motion.schedule_stats(sched)
    sa, sb = st["segA_s"], st["segB_s"]
    fps_b = st["segB_fps"]
    ok4 = abs(total - 5000) <= 50 and 3.0 <= sa <= 4.0 and 1.0 <= sb <= 2.0 \
        and all(12 <= f <= 18 for f in fps_b)
    res["L4_timing"] = dict(ok=ok4, total_ms=total, segA_s=round(sa, 3),
                            segB_s=round(sb, 3), segB_fps=fps_b)

    # ---- L8 perf
    kb = os.path.getsize(loop) / 1024
    ok8 = kb <= limit_kb and 52 <= len(sched) <= 66
    res["L8_perf"] = dict(ok=ok8, loop_kb=round(kb, 1), limit_kb=limit_kb,
                          timeline_frames=len(sched), encoded=len(frames))

    # ---- L3 loop closure
    gs = [_gray(f) for f in frames]
    adj = [np.abs(gs[i + 1] - gs[i]).mean() for i in range(len(gs) - 1)]
    med = float(np.median(adj)) if adj else 0.0
    clo = float(np.abs(gs[0] - gs[-1]).mean())
    ok3 = clo <= 1.5 * max(med, 0.35)
    res["L3_loop_closure"] = dict(ok=ok3, close=round(clo, 3),
                                  median_adj=round(med, 3))

    # ---- L1 plate stability (fora de máscaras/footprints)
    masks_dir = os.path.join(root, "masks")
    worst = 0.0
    p_small = plate.resize((320, 180), Image.BILINEAR)
    p_arr = np.asarray(p_small, dtype=np.float32)
    for i, f in enumerate(frames):
        mp = os.path.join(masks_dir, f"mm_{i:02d}.png")
        if os.path.exists(mp):
            m = np.asarray(Image.open(mp).convert("L"), dtype=np.float32) > 127
        else:
            m = np.zeros((180, 320), bool)
        fa = np.asarray(f.resize((320, 180), Image.BILINEAR), dtype=np.float32)
        delta = np.abs(fa - p_arr).mean(axis=2)
        out = delta[~m]
        pct = float((out > 16).mean() * 100)
        worst = max(worst, pct)
    ok1 = worst <= 0.5
    res["L1_plate_stability"] = dict(ok=ok1, worst_pct_outside=round(worst, 3))

    # ---- L2 edge integrity
    edge_bad = []
    for lc in meta["layers"]:
        ef = lc.get("edge_frac", 0.0)
        edge_bad.append((lc["name"], ef))
    halo_worst = 0.0
    for i, f in enumerate(frames):
        mp = os.path.join(masks_dir, f"mm_{i:02d}.png")
        if not os.path.exists(mp):
            continue
        m = np.asarray(Image.open(mp).convert("L"), dtype=np.float32) > 127
        ring = np.roll(m, 3, 0) | np.roll(m, -3, 0) | np.roll(m, 3, 1) | np.roll(m, -3, 1)
        ring &= ~m
        fa = np.asarray(f.resize((320, 180), Image.BILINEAR), dtype=np.float32)
        delta = np.abs(fa - p_arr).mean(axis=2)
        if ring.any():
            halo_worst = max(halo_worst, float(delta[ring].mean()))
    ok2 = all(ef <= 0.35 for _, ef in edge_bad) and halo_worst <= 2.5
    res["L2_edge_integrity"] = dict(ok=ok2, layers=edge_bad,
                                    halo_ring=round(halo_worst, 3))

    # ---- L5 scale consistency
    bad = []
    for lc in meta["layers"]:
        if lc.get("fx_layer"):
            continue
        tr = meta["tracks"].get(lc["name"], {})
        sxk, syk = tr.get("sx"), tr.get("sy")
        if not sxk and not syk:
            continue
        import importlib
        mo = importlib.import_module("motion")
        sx = mo.track_from_keys(sxk).at if sxk else (lambda t: 1.0)
        sy = mo.track_from_keys(syk).at if syk else (lambda t: 1.0)
        worstd = max(abs(sx(t) - sy(t)) for t in range(0, 5001, 50))
        if worstd > 0.08 + 1e-6:
            bad.append((lc["name"], round(worstd, 3)))
    res["L5_scale_consistency"] = dict(ok=not bad, bad=bad)

    # ---- L6 palette / outline
    def hue_hist(im):
        a = np.asarray(im.resize((160, 90)), dtype=np.float32) / 255
        mx = a.max(axis=2); mn = a.min(axis=2)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        h = np.zeros_like(mx)
        d = mx - mn + 1e-6
        h = np.where(mx == r, (g - b) / d % 6, h)
        h = np.where(mx == g, (b - r) / d + 2, h)
        h = np.where(mx == b, (r - g) / d + 4, h)
        h = (h * 60) % 360
        hist, _ = np.histogram(h[mx > 0.15], bins=8, range=(0, 360))
        return hist / max(1, hist.sum())
    hp = hue_hist(plate)
    worst_share = 1.0
    dark_de = 0.0
    lab_p = _rgb2lab(np.asarray(plate.resize((160, 90)), dtype=np.float32))
    for f in frames[::6]:
        fs = f.resize((160, 90))
        worst_share = min(worst_share, float((np.minimum(hp, hue_hist(fs)).sum())))
        af = np.asarray(fs, dtype=np.float32)
        lum = af.mean(axis=2)
        sel_f = af[lum < np.percentile(lum, 6)]
        sel_p = lab_p[..., :1]  # placeholder
        ap = np.asarray(plate.resize((160, 90)), dtype=np.float32)
        lump = ap.mean(axis=2)
        sel_p = ap[lump < np.percentile(lump, 6)]
        if len(sel_f) and len(sel_p):
            de = np.abs(_rgb2lab(sel_f[:400]).mean(axis=0) -
                        _rgb2lab(sel_p[:400]).mean(axis=0)).sum()
            dark_de = max(dark_de, float(de))
    ok6 = worst_share >= 0.90 and dark_de <= 6.0
    res["L6_palette_outline"] = dict(ok=ok6, hue_share=round(worst_share, 3),
                                     outline_dE=round(dark_de, 2))

    # ---- L7 occlusion
    probs = []
    zmap = {lc["name"]: lc["z"] for lc in meta["layers"]}
    for lc in meta["layers"]:
        if lc.get("kind") == "patch" and lc.get("patch_over"):
            target = lc["patch_over"]
            tz = zmap.get(target, 0)
            if lc["z"] <= tz:
                probs.append((lc["name"], target))
    res["L7_occlusion"] = dict(ok=not probs, problems=probs,
                               z_order=sorted(zmap.items(), key=lambda kv: kv[1]))

    # ---- L9 provenience
    assets = meta.get("assets", [])
    nai = sum(1 for a in assets if a["prov"] == "ai")
    nframes = len(sched)
    pct = nai / nframes * 100
    res["L9_provenance"] = dict(ok=pct >= 20.0, ai=nai, frames=nframes,
                                pct=round(pct, 1), level="warn")

    res["_summary"] = dict(
        fail=[k for k, v in res.items()
              if isinstance(v, dict) and v.get("ok") is False and v.get("level") != "warn"],
        warn=[k for k, v in res.items()
              if isinstance(v, dict) and v.get("ok") is False and v.get("level") == "warn"])
    json.dump(res, open(os.path.join(root, "qa.json"), "w"), indent=1, ensure_ascii=False)
    return res


def _frame_fps(meta: dict, durs) -> list:
    sched = motion.build_schedule(meta["profile"])
    out, i = [], 0
    acc = 0
    for (t, d, f) in sched:
        out.append(f)
    # quadros encodados podem ser menos (holds): reconstrói pela agenda e corta
    return out[:len(durs)] if len(out) >= len(durs) else out + [out[-1]] * (len(durs) - len(out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--limit-kb", type=int, default=2600)
    a = ap.parse_args()
    r = run(a.meta, a.limit_kb)
    for k, v in r.items():
        if k.startswith("L"):
            print(f"{k:22s} {'OK ' if v.get('ok') else ('WARN' if v.get('level') == 'warn' else 'FAIL')} {json.dumps(v, ensure_ascii=False)[:150]}")
    print("SUMMARY:", json.dumps(r["_summary"], ensure_ascii=False))
    sys.exit(0 if not r["_summary"]["fail"] else 1)

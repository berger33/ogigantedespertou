#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/qa_frames.py — lints de consistência para keyframes IA (v6).

Q1 anchor_diff      diff média de cada keyframe vs. poster (128px) ≤ 60
Q2 anchor_hue       sobreposição de matiz vs. poster ≥ 0.90
Q3 delta_progress   Δ médio entre keyframes consecutivos ≤ 45 (sem teleporte)
Q4 brightness       desvio-padrão de luminância entre quadros ≤ 22 (sem flicker)
Q5 palette_shift    Δshare de matiz ≤ 0.05 por bin (calibrado c/ rastro no doc)
Q6 loop_closure     |último Q − Q01| ≤ 12 (o ciclo fecha no frame original)
Q7 palette_count    Δ no nº de matizes dominantes ≤ 3

Keyframes em glob natural (k01=poster, k02…kNN, suporta k05b). Reprovados são
reportados POR NOME (o build_webp os exclui da sequência).

Uso: python3 tools/animia/qa_frames.py --dir src/assets/anim/p5_02/v6
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re

import numpy as np
from PIL import Image


def _natkey(path: str):
    m = re.match(r"k(\d+)([a-z]?)*\.png$", os.path.basename(path))
    return (int(m.group(1)), m.group(2) or "")


def load_frames(kdir: str, size=(128, 72)):
    frames = [("k01", Image.open(os.path.join(kdir, "..", "poster.webp")).convert("RGB"))]
    for p in sorted(glob.glob(os.path.join(kdir, "k*.png")), key=_natkey):
        name = os.path.basename(p)[:-4]
        frames.append((name, Image.open(p).convert("RGB")))
    return [(n, f.resize(size, Image.BILINEAR)) for n, f in frames]


def hue_share(im: Image.Image, bins: int = 8):
    a = np.asarray(im, dtype=np.float32) / 255
    mx, mn = a.max(axis=2), a.min(axis=2)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = mx - mn + 1e-6
    h = np.where(mx == r, (g - b) / d % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4))
    h = (h * 60) % 360
    hist, _ = np.histogram(h[mx > 0.12], bins=bins, range=(0, 360))
    return hist / max(1, hist.sum())


def run(kdir: str) -> dict:
    fr = load_frames(kdir)
    names = [n for n, _ in fr]
    arrs = [np.asarray(f, dtype=np.float32) for _, f in fr]
    lums = [a.mean(axis=2) for a in arrs]
    poster = arrs[0]
    hp = hue_share(fr[0][1])
    res = {}

    diffs = {names[i]: round(float(np.abs(arrs[i] - poster).mean()), 1)
             for i in range(1, len(arrs))}
    res["Q1_anchor_diff"] = dict(ok=max(diffs.values()) <= 60, diffs=diffs)

    shares = {names[i]: round(float(np.minimum(hp, hue_share(fr[i][1])).sum()), 3)
              for i in range(1, len(arrs))}
    res["Q2_anchor_hue"] = dict(ok=min(shares.values()) >= 0.90, shares=shares)

    deltas = {f"{names[i]}→{names[i+1]}": round(float(np.abs(lums[i + 1] - lums[i]).mean()), 1)
              for i in range(len(lums) - 1)}
    res["Q3_delta_progress"] = dict(ok=max(deltas.values()) <= 45, deltas=deltas)

    std = float(np.std([l.mean() for l in lums]))
    res["Q4_brightness"] = dict(ok=std <= 22, std=round(std, 2),
                                means=[round(float(l.mean()), 1) for l in lums])

    worst_bin, worst_k = 0.0, ""
    for i in range(1, len(arrs)):
        d = float(np.abs(hue_share(fr[i][1]) - hp).max())
        if d > worst_bin:
            worst_bin, worst_k = d, names[i]
    res["Q5_palette_shift"] = dict(ok=worst_bin <= 0.05, worst_bin=round(worst_bin, 4),
                                   frame=worst_k)

    loop_d = float(np.abs(arrs[-1] - poster).mean())
    res["Q6_loop_closure"] = dict(ok=loop_d <= 12, close=round(loop_d, 2),
                                  last=names[-1])

    def dom_count(s, thr=0.06):
        return int((s > thr).sum())
    hp_count = dom_count(hp)
    kc = {names[i]: abs(dom_count(hue_share(fr[i][1])) - hp_count)
          for i in range(1, len(arrs))}
    res["Q7_palette_count"] = dict(ok=max(kc.values()) <= 3, counts=kc, poster=hp_count)

    res["_summary"] = dict(
        fail=[k for k, v in res.items() if isinstance(v, dict) and v.get("ok") is False],
        n_keys=len(names), key_names=names)
    json.dump(res, open(os.path.join(kdir, "qa.json"), "w"), indent=1, ensure_ascii=False)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    a = ap.parse_args()
    r = run(a.dir)
    for k, v in r.items():
        if k.startswith("Q"):
            print(f"{k:20s} {'OK ' if v.get('ok') else 'FAIL'} {json.dumps(v, ensure_ascii=False)[:170]}")
    print("SUMMARY:", json.dumps(r["_summary"], ensure_ascii=False))
    raise SystemExit(0 if not r["_summary"]["fail"] else 1)

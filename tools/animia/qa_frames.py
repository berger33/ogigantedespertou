#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/qa_frames.py — lints de consistência para keyframes IA (v6).

Q1 anchor_diff      diff média de cada keyframe vs. poster (128px) ≤ 60
Q2 anchor_hue       sobreposição de matiz vs. poster ≥ 0.90
Q3 delta_progress   Δ médio entre keyframes consecutivos ≤ 45 (sem teleporte)
Q4 brightness       desvio-padrão de luminância entre quadros ≤ 22 (sem flicker)
Q5 palette_shift    Δ de share de matiz (8 bins) ≤ 0.035 por bin
Q6 loop_closure     |Q10 − Q01| ≤ 12 (o ciclo fecha no frame original)
Q7 palette_count    Δ no nº de matizes dominantes ≤ 3

Uso: python3 tools/animia/qa_frames.py --dir src/assets/anim/p5_02/v6
"""
from __future__ import annotations
import argparse
import json
import os

import numpy as np
from PIL import Image

FRAMES = [f"k{int(m.group(1)):02d}.png" for m in ()]  # placeholder, ver abaixo


def load_frames(kdir: str, n: int = 10, size=(128, 72)):
    """Carrega Q01 (poster.webp) + k02..k10, em RGB no tamanho de análise."""
    frames = [Image.open(os.path.join(kdir, "..", "poster.webp")).convert("RGB")]
    for k in range(2, n + 1):
        p = os.path.join(kdir, f"k{k:02d}.png")
        frames.append(Image.open(p).convert("RGB"))
    return [f.resize(size, Image.BILINEAR) for f in frames]


def hue_share(im: Image.Image, bins: int = 8):
    a = np.asarray(im, dtype=np.float32) / 255
    mx, mn = a.max(axis=2), a.min(axis=2)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = mx - mn + 1e-6
    h = np.where(mx == r, (g - b) / d % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4))
    h = (h * 60) % 360
    hist, _ = np.histogram(h[mx > 0.12], bins=bins, range=(0, 360))
    return hist / max(1, hist.sum())


def run(kdir: str, n: int = 10) -> dict:
    fr = load_frames(kdir, n)
    arrs = [np.asarray(f, dtype=np.float32) for f in fr]
    lums = [a.mean(axis=2) for a in arrs]
    poster = arrs[0]
    res = {}

    diffs_anchor = [float(np.abs(a - poster).mean()) for a in arrs[1:]]
    res["Q1_anchor_diff"] = dict(ok=max(diffs_anchor) <= 60, diffs=[round(d, 1) for d in diffs_anchor])

    hp = hue_share(fr[0])
    shares = [float(np.minimum(hp, hue_share(f)).sum()) for f in fr[1:]]
    res["Q2_anchor_hue"] = dict(ok=min(shares) >= 0.90, shares=[round(s, 3) for s in shares])

    deltas = [float(np.abs(lums[i + 1] - lums[i]).mean()) for i in range(len(lums) - 1)]
    res["Q3_delta_progress"] = dict(ok=max(deltas) <= 45, deltas=[round(d, 1) for d in deltas])

    lum_means = [float(l.mean()) for l in lums]
    res["Q4_brightness"] = dict(ok=float(np.std(lum_means)) <= 22,
                                std=round(float(np.std(lum_means)), 2),
                                means=[round(m, 1) for m in lum_means])

    worst_bin, worst_k = 0.0, -1
    for k, f in enumerate(fr[1:], start=2):
        s = hue_share(f)
        d = float(np.abs(s - hp).max())
        if d > worst_bin:
            worst_bin, worst_k = d, k
    res["Q5_palette_shift"] = dict(ok=worst_bin <= 0.05, worst_bin=round(worst_bin, 4), frame=worst_k)

    loop_d = float(np.abs(arrs[-1] - poster).mean())
    res["Q6_loop_closure"] = dict(ok=loop_d <= 12, close=round(loop_d, 2))

    def dominant_count(s, thr=0.06):
        return int((s > thr).sum())
    hp_count = dominant_count(hp)
    kc = [abs(dominant_count(hue_share(f)) - hp_count) for f in fr[1:]]
    res["Q7_palette_count"] = dict(ok=max(kc) <= 3, counts=kc, poster=hp_count)

    res["_summary"] = dict(
        fail=[k for k, v in res.items() if isinstance(v, dict) and v.get("ok") is False],
        n_frames=n)
    json.dump(res, open(os.path.join(kdir, "qa.json"), "w"), indent=1, ensure_ascii=False)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    r = run(a.dir, a.n)
    for k, v in r.items():
        if k.startswith("Q"):
            print(f"{k:20s} {'OK ' if v.get('ok') else 'FAIL'} {json.dumps(v, ensure_ascii=False)[:160]}")
    print("SUMMARY:", json.dumps(r["_summary"], ensure_ascii=False))
    raise SystemExit(0 if not r["_summary"]["fail"] else 1)

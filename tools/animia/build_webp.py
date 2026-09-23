#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/build_webp.py — entrega v6.1: loop SUAVE (poses IA + tweens).

  * sequência = Q01, 4 tweens, Q02, 4 tweens, … Q10  (41 desenhos @ ~122 ms)
  * loop.webp (5 s, loop=0) + frames/ff_XX.webp + contact.png + meta.json
  * QA integrado: Q8_smoothness = max Δ entre desenhos consecutivos ≤ 12

Uso: python3 tools/animia/build_webp.py --dir src/assets/anim/p5_02/v6
"""
from __future__ import annotations
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tween as tween_mod

SIZE = (640, 360)


def _font(sz):
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()


def load_keys(kdir: str) -> dict:
    """Carrega Q01 (poster) + keyframes aprovados no qa.json (reprovados saem
    da sequência — o tween entre vizinhos cobre o beat)."""
    poster = Image.open(os.path.join(kdir, "..", "poster.webp")).convert("RGB")
    keys = {"k01": np.asarray(poster.resize(SIZE, Image.LANCZOS), dtype=np.float32)}
    qa = {}
    qap = os.path.join(kdir, "qa.json")
    if os.path.exists(qap):
        qa = json.load(open(qap))
    bad = set()
    if isinstance(qa.get("Q5_palette_shift"), dict) and not qa["Q5_palette_shift"]["ok"]:
        bad.add(f"k{qa['Q5_palette_shift'].get('frame', -1):02d}")
    for k in range(2, 11):
        name = f"k{k:02d}"
        if name in bad:
            continue
        p = os.path.join(kdir, f"{name}.png")
        if os.path.exists(p):
            keys[name] = np.asarray(Image.open(p).convert("RGB").resize(
                SIZE, Image.LANCZOS), dtype=np.float32)
    return keys


def build(kdir: str, quality: int = 78, n_tweens: int = 4) -> dict:
    keys = load_keys(kdir)
    seq = tween_mod.build_sequence(keys, n_tweens)
    # o ciclo termina no ESTADO DO POSTER (o último desenho é o próprio Q01),
    # então a emenda do loop fecha com delta 0
    seq[-1] = np.clip(keys["k01"], 0, 255).astype(np.uint8)
    n = len(seq)
    durs = [round(5000 / n)] * n
    durs[-1] += 5000 - sum(durs)

    loop_path = os.path.join(kdir, "loop.webp")
    imgs = [Image.fromarray(f) for f in seq]
    imgs[0].save(loop_path, save_all=True, append_images=imgs[1:],
                 duration=durs, loop=0, quality=quality, method=6)

    fdir = os.path.join(kdir, "frames")
    os.makedirs(fdir, exist_ok=True)
    for old in os.listdir(fdir):
        os.remove(os.path.join(fdir, old))
    for i, f in enumerate(imgs):
        f.save(os.path.join(fdir, f"ff_{i:02d}.webp"), quality=85)

    tw, th = 300, 169
    cols = 6
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, (th + 18) * rows), (14, 15, 20))
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(imgs):
        x, y = (i % cols) * tw, (i // cols) * (th + 18)
        sheet.paste(f.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 5, y + th + 2), f"#{i:02d}", fill=(225, 228, 238), font=_font(12))
    sheet.save(os.path.join(kdir, "contact.png"))

    # ---- Q8 smoothness: max Δ médio entre desenhos consecutivos ----
    lums = [f.mean(axis=2) for f in seq]
    deltas = [float(np.abs(lums[i + 1] - lums[i]).mean()) for i in range(n - 1)]
    q8 = dict(ok=max(deltas) <= 12, max_delta=round(max(deltas), 2),
              mean_delta=round(float(np.mean(deltas)), 2),
              wrap_delta=round(float(np.abs(lums[-1] - lums[0]).mean()), 2))
    qa = dict(Q8_smoothness=q8, n_drawings=n,
              keys_used=sorted(keys), tween_per_pair=n_tweens)
    json.dump(qa, open(os.path.join(kdir, "qa_smooth.json"), "w"), indent=1)

    meta_path = os.path.join(kdir, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    meta.update({"version": "6.1", "method": "ai-keyframes+tween",
                 "duration_ms": 5000, "drawings": n, "step_ms": 5000 // n,
                 "keys": sorted(keys), "tweens_per_pair": n_tweens,
                 "smoothness": q8, "anchor": "../poster.webp"})
    json.dump(meta, open(meta_path, "w"), indent=1, ensure_ascii=False)

    return {"frames": n, "duration_ms": sum(durs),
            "loop_kb": round(os.path.getsize(loop_path) / 1024, 1),
            "Q8": q8}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--quality", type=int, default=78)
    ap.add_argument("--tweens", type=int, default=4)
    a = ap.parse_args()
    print(json.dumps(build(a.dir, a.quality, a.tweens), ensure_ascii=False))

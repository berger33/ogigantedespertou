#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/build_webp.py — entrega v6: loop.webp + frames/ + contact.png.

  * loop.webp: Q01..Q10 a 10 fps (100 ms/quadro), loop=0, q configurável
  * frames/ff_00..ff_09.webp (10 desenhos da receita)
  * contact.png (folha de contato 5x2)
  * meta.json (registro de proveniência e parâmetros)

Uso: python3 tools/animia/build_webp.py --dir src/assets/anim/p5_02/v6
"""
from __future__ import annotations
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

DUR_MS = 100  # 10 desenhos × 100 ms = 1000 ms por volta... não: 10 fps ⇒ 5000 ms
# Cada desenho fica 500 ms em tela (cadência do jogo); o contêiner carrega
# a duração real por quadro → 10 quadros × 500 ms = 5000 ms.


def _font(sz):
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()


def build(kdir: str, quality: int = 80) -> dict:
    poster = Image.open(os.path.join(kdir, "..", "poster.webp")).convert("RGB")
    frames = [poster] + [Image.open(os.path.join(kdir, f"k{k:02d}.png")).convert("RGB")
                         for k in range(2, 11)]
    W, H = 640, 360
    frames = [f.resize((W, H), Image.LANCZOS) for f in frames]
    durs = [500] * 10

    loop_path = os.path.join(kdir, "loop.webp")
    frames[0].save(loop_path, save_all=True, append_images=frames[1:],
                   duration=durs, loop=0, quality=quality, method=6)

    fdir = os.path.join(kdir, "frames")
    os.makedirs(fdir, exist_ok=True)
    for i, f in enumerate(frames):
        f.save(os.path.join(fdir, f"ff_{i:02d}.webp"), quality=85)

    tw, th = 300, 169
    sheet = Image.new("RGB", (tw * 5, (th + 20) * 2), (14, 15, 20))
    d = ImageDraw.Draw(sheet)
    labels = ["Q01 poster"] + [f"Q{k:02d}" for k in range(2, 11)]
    for i, f in enumerate(frames):
        x, y = (i % 5) * tw, (i // 5) * (th + 20)
        sheet.paste(f.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 6, y + th + 3), labels[i], fill=(225, 228, 238), font=_font(13))
    sheet.save(os.path.join(kdir, "contact.png"))

    meta = {
        "id": os.path.basename(os.path.dirname(kdir)),
        "version": 6, "method": "ai-keyframes",
        "duration_ms": 5000, "frames": 10, "drawing_ms": 500,
        "size": [W, H], "loop": "perfect (Q10 = Q01)",
        "anchor": "../poster.webp",
        "keyframes": [f"k{k:02d}.png" for k in range(2, 11)],
        "qa": "qa.json",
    }
    json.dump(meta, open(os.path.join(kdir, "meta.json"), "w"), indent=1, ensure_ascii=False)
    rep = {"loop_kb": round(os.path.getsize(loop_path) / 1024, 1),
           "frames": len(frames), "duration_ms": sum(durs)}
    json.dump(rep, open(os.path.join(kdir, "build_report.json"), "w"), indent=1)
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--quality", type=int, default=80)
    a = ap.parse_args()
    print(json.dumps(build(a.dir, a.quality), ensure_ascii=False))

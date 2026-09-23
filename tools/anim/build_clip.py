#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/build_clip.py — compositor + encoder WebP de duração por quadro (E3/E4).

Lê o meta.json da missão (board declarado), compõe os quadros pela agenda de
fps variável, deduplica holds (1 quadro encodado carrega o tempo do hold),
encoda o loop.webp e emite frames-chave, contact sheet, máscaras de movimento
(para o lint L1) e o build_report.json.

Uso:
  python3 tools/anim/build_clip.py --meta src/assets/anim/p4_10/v4/meta.json
"""
from __future__ import annotations
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import motion  # noqa: E402
import rig     # noqa: E402
import fx      # noqa: E402

TRACK_PROPS = ("dx", "dy", "rot", "sx", "sy", "alpha")


def _font(sz):
    try:
        return ImageFont.load_default(size=sz)
    except TypeError:
        return ImageFont.load_default()


def compose_frame(meta: dict, plate: Image.Image, layers: dict,
                  atlases: dict, t_ms: float, W: int, H: int,
                  mask_img: Image.Image | None = None) -> Image.Image:
    canvas = plate.copy().convert("RGBA")
    mdraw = ImageDraw.Draw(mask_img) if mask_img is not None else None
    ms = (mask_img.width / W, mask_img.height / H) if mask_img is not None else (1, 1)

    for lc in sorted(meta["layers"], key=lambda l: l["z"]):
        tr = {p: meta["tracks"].get(lc["name"], {}).get(p) for p in TRACK_PROPS}
        vals = {}
        for p, keys in tr.items():
            if keys is None:
                vals[p] = 1.0 if p in ("sx", "sy", "alpha") else 0.0
            else:
                vals[p] = motion.track_from_keys(keys).at(t_ms)
        if vals["alpha"] <= 0.004:
            continue
        L = layers[lc["name"]]
        rig.affine_paste(canvas, L["img"], tuple(lc["bbox"]), tuple(lc["pivot"]),
                         vals["dx"], vals["dy"], vals["rot"], vals["sx"], vals["sy"],
                         vals["alpha"], kind=lc.get("kind", "sprite"),
                         soft_squash=lc.get("soft_squash", False))
        if mdraw is not None:
            x, y, w, h = lc["bbox"]
            pad = 26 + abs(vals["dx"]) + abs(vals["dy"])
            mdraw.rectangle([(x - pad) * ms[0], (y - pad) * ms[1],
                             (x + w + pad) * ms[0], (y + h + pad) * ms[1]], fill=255)

    group_off = {}
    for gname, g in meta.get("groups", {}).items():
        keys = meta["tracks"].get(g, {}).get("dy")
        group_off[gname] = (0.0, motion.track_from_keys(keys).at(t_ms) if keys else 0.0)

    for f in meta.get("fx", []):
        p = dict(f["params"]); p["t0"] = f.get("t0", p.get("t0", 0)); p["t1"] = f.get("t1", p.get("t1", 10 ** 9))
        fol = f.get("follow")
        if fol and fol in group_off:
            dx, dy = group_off[fol]
            if "positions" in p:
                p["positions"] = [[x + dx, y + dy, s] for (x, y, s) in p["positions"]]
            if "region" in p:
                x0, y0, x1, y1 = p["region"]
                p["region"] = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
        kind = f["kind"]
        if kind in fx.ATLAS_KINDS:
            fx.ATLAS_KINDS[kind](canvas, t_ms, p, atlases[f["atlas"]])
        elif kind in fx.KINDS:
            fx.KINDS[kind](canvas, t_ms, p)
        if mdraw is not None and f.get("footprint"):
            x0, y0, x1, y1 = f["footprint"]
            mdraw.rectangle([x0 * ms[0], y0 * ms[1], x1 * ms[0], y1 * ms[1]], fill=255)
    return canvas.convert("RGB")


def build(meta_path: str, quality: int | None = None) -> dict:
    meta = json.load(open(meta_path))
    root = os.path.dirname(os.path.abspath(meta_path))
    W, H = meta["size"]
    plate = Image.open(os.path.join(root, meta["plate"])).convert("RGBA")
    if plate.size != (W, H):
        plate = plate.resize((W, H), Image.LANCZOS)

    layers = {}
    for lc in meta["layers"]:
        img = Image.open(os.path.join(root, lc["file"])).convert("RGBA")
        layers[lc["name"]] = {"img": img}
    atlases = {}
    for f in meta.get("fx", []):
        a = f.get("atlas")
        if a and a not in atlases:
            atlases[a] = Image.open(os.path.join(root, a)).convert("RGBA")

    sched = motion.build_schedule(meta["profile"])
    frames, durs, masks = [], [], []
    prev_arr = None
    for (t, dur, fps) in sched:
        mimg = Image.new("L", (320, 180), 0)
        img = compose_frame(meta, plate, layers, atlases, t, W, H, mimg)
        arr = np.asarray(img, dtype=np.uint8)
        if prev_arr is not None and np.array_equal(arr, prev_arr):
            durs[-1] += dur           # hold deduplicado (§2 / L8)
            continue
        frames.append(img); durs.append(dur); masks.append(mimg)
        prev_arr = arr

    # loop-tail dedup: se o último quadro é idêntico ao primeiro, funde no f0
    if len(frames) > 2 and np.array_equal(np.asarray(frames[-1]), np.asarray(frames[0])):
        durs[0] += durs.pop(-1)
        frames.pop(-1); masks.pop(-1)

    out = os.path.join(root)
    os.makedirs(os.path.join(out, "frames"), exist_ok=True)
    os.makedirs(os.path.join(out, "masks"), exist_ok=True)
    loop_path = os.path.join(out, "loop.webp")
    q = quality or meta.get("quality", 72)
    frames[0].save(loop_path, save_all=True, append_images=frames[1:],
                   duration=durs, loop=0, quality=q, method=6)

    for i, m in enumerate(masks):
        m.save(os.path.join(out, "masks", f"mm_{i:02d}.png"))
    n = len(frames)
    keys = sorted({0, n // 8, n // 4, 3 * n // 8, n // 2, 5 * n // 8, 3 * n // 4, n - 1})
    for j, ki in enumerate(keys):
        frames[ki].save(os.path.join(out, "frames", f"ff_{j:02d}.webp"), quality=85)
    # contact sheet
    tw, th = 320, 180
    sheet = Image.new("RGB", (tw * 4, th * 2), (18, 18, 22))
    for j, ki in enumerate(keys):
        sheet.paste(frames[ki].resize((tw, th), Image.LANCZOS),
                    ((j % 4) * tw, (j // 4) * th))
    sheet.save(os.path.join(out, "contact.png"))

    make_board(meta, frames, keys, os.path.join(out, "board.png"))
    report = {"frames_encoded": n, "frames_timeline": len(sched),
              "durations": durs, "quality": q,
              "loop_bytes": os.path.getsize(loop_path),
              "stats": motion.schedule_stats(sched)}
    json.dump(report, open(os.path.join(out, "build_report.json"), "w"), indent=1)
    return report


def make_board(meta: dict, frames, keys, path: str) -> None:
    W = 1280
    bh = 86
    th_h = 200
    img = Image.new("RGB", (W, bh + th_h + 46), (16, 17, 22))
    d = ImageDraw.Draw(img)
    f_small, f_big = _font(13), _font(17)
    d.text((10, 6), f"{meta['id']} — board v4 · {meta['profile']} · "
                    f"{meta['duration_ms']}ms · {meta['size'][0]}x{meta['size'][1]}",
           fill=(235, 235, 235), font=f_big)
    y0 = 34
    for seg in meta.get("fps_segments", []):
        x0 = seg["start_s"] / 5.0 * W; x1 = seg["end_s"] / 5.0 * W
        col = (70, 130, 200) if seg["fps"] == 10 else (215, 130, 40)
        d.rectangle([x0, y0, x1 - 1, y0 + 16], fill=col)
        d.text((x0 + 6, y0 + 1), f"{seg['fps']} fps", fill=(255, 255, 255), font=f_small)
    y1 = y0 + 20
    for b in meta.get("beats", []):
        t0, t1 = b["t"]
        x0 = t0 / 5000 * W; x1 = t1 / 5000 * W
        d.rectangle([x0, y1, x1 - 1, y1 + 30], outline=(120, 124, 140), fill=(30, 32, 40))
        d.text((x0 + 4, y1 + 2), b["name"], fill=(220, 224, 235), font=f_small)
        d.text((x0 + 4, y1 + 16), " ".join(b.get("tokens", [])), fill=(150, 200, 160), font=f_small)
    yy = bh + 6
    tw, th = 300, 169
    for j, ki in enumerate(keys):
        x = 10 + j * (tw + 12)
        img.paste(frames[ki].resize((tw, th), Image.LANCZOS), (x, yy))
        d.text((x, yy + th + 2), f"f{ki}", fill=(190, 190, 200), font=f_small)
    img.save(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--quality", type=int, default=None)
    a = ap.parse_args()
    rep = build(a.meta, a.quality)
    print(json.dumps(rep["stats"], ensure_ascii=False),
          f"encoded={rep['frames_encoded']} bytes={rep['loop_bytes']}")
